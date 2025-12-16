# Análisis de Código - .

**Fecha de generación:** 2025-12-16 10:54:53

**Directorio analizado:** `.`

**Total de archivos procesados:** 37

---

### main.py

**Ruta:** `main.py`

```py
0001 | # infrastructure/llm/response_parser.py
0002 | """
0003 | 🔧 LLM Response Parser - Limpieza, validación y parsing de respuestas JSON
0004 | 
0005 | Features:
0006 | - ✅ Limpieza avanzada con markdown wrappers
0007 | - ✅ Extracción inteligente con stack balancing
0008 | - ✅ Validación pre-parsing
0009 | - ✅ Parsing a modelos Pydantic
0010 | - ✅ Corrección de escapes inválidos
0011 | """
0012 | 
0013 | import json
0014 | import re
0015 | import logging
0016 | import time
0017 | from typing import Dict, Any, Optional, List
0018 | 
0019 | from core.models import (
0020 |     TriageResult, 
0021 |     RemediationPlan, 
0022 |     TriageDecision, 
0023 |     AnalysisStatus, 
0024 |     RemediationStep, 
0025 |     VulnerabilityType
0026 | )
0027 | from core.exceptions import LLMError
0028 | 
0029 | logger = logging.getLogger(__name__)
0030 | 
0031 | 
0032 | class LLMResponseParser:
0033 |     """
0034 |     Parser especializado para respuestas de LLM
0035 |     
0036 |     Responsabilidades:
0037 |     - Limpieza de JSON con markdown/noise
0038 |     - Validación de estructura JSON
0039 |     - Extracción inteligente de JSON
0040 |     - Parsing a modelos de dominio (TriageResult, RemediationPlan)
0041 |     """
0042 |     
0043 |     def __init__(self, debug_enabled: bool = False):
0044 |         self.debug_enabled = debug_enabled
0045 |     
0046 |     
0047 |     # ============================================================================
0048 |     # PUBLIC API - PARSING METHODS
0049 |     # ============================================================================
0050 |     
0051 |     def parse_triage_response(self, llm_response: str, original_data: str = None) -> TriageResult:
0052 |         """
0053 |         Parsear respuesta LLM a TriageResult
0054 |         
0055 |         Args:
0056 |             llm_response: Respuesta cruda del LLM
0057 |             original_ Datos originales (para contexto en errores)
0058 |             
0059 |         Returns:
0060 |             TriageResult validado
0061 |             
0062 |         Raises:
0063 |             LLMError: Si el parsing falla después de intentos de recuperación
0064 |         """
0065 |         
0066 |         logger.info(f"📥 Parsing triage response ({len(llm_response):,} chars)...")
0067 |         
0068 |         try:
0069 |             # Paso 1: Limpiar respuesta
0070 |             cleaned = self.clean_json_response(llm_response)
0071 |             
0072 |             # Paso 2: Validar estructura
0073 |             validation = self.validate_json_structure(cleaned)
0074 |             
0075 |             if not validation['is_valid']:
0076 |                 logger.error(f"❌ JSON structure validation failed:")
0077 |                 for error in validation['errors']:
0078 |                     logger.error(f"   • {error}")
0079 |                 
0080 |                 # Intentar recuperación
0081 |                 logger.info("🔧 Attempting recovery...")
0082 |                 extracted = self.extract_json(
0083 |                     cleaned, 
0084 |                     required_fields=['decisions', 'analysis_summary']
0085 |                 )
0086 |                 
0087 |                 if extracted:
0088 |                     cleaned = extracted
0089 |                     logger.info("✅ Recovery successful")
0090 |                 else:
0091 |                     raise LLMError(f"JSON structure invalid: {validation['errors']}")
0092 |             
0093 |             # Paso 3: Parsear JSON
0094 |             try:
0095 |                 response_data = json.loads(cleaned)
0096 |                 logger.info(f"✅ JSON parsed successfully")
0097 |             except json.JSONDecodeError as e:
0098 |                 logger.error(f"❌ JSON parsing failed: {e}")
0099 |                 
0100 |                 # Último intento de recuperación
0101 |                 extracted = self.extract_json(
0102 |                     llm_response,
0103 |                     required_fields=['decisions', 'analysis_summary']
0104 |                 )
0105 |                 
0106 |                 if extracted:
0107 |                     try:
0108 |                         response_data = json.loads(extracted)
0109 |                         logger.info("✅ Recovery parse successful")
0110 |                     except Exception:
0111 |                         raise LLMError(f"Failed to parse triage response: {e}")
0112 |                 else:
0113 |                     raise LLMError(f"Failed to parse triage response: {e}")
0114 |             
0115 |             # Paso 4: Validar campos requeridos
0116 |             self._validate_required_fields(
0117 |                 response_data,
0118 |                 required_fields=['decisions'],
0119 |                 response_type='triage'
0120 |             )
0121 |             
0122 |             # Paso 5: Crear TriageResult (Pydantic validará)
0123 |             triage_result = TriageResult(**response_data)
0124 |             
0125 |             # Paso 6: Log resultados
0126 |             logger.info(f"✅ TriageResult created successfully")
0127 |             logger.info(f"   Total analyzed: {triage_result.total_analyzed}")
0128 |             logger.info(f"   Confirmed: {triage_result.confirmed_count}")
0129 |             logger.info(f"   False positives: {triage_result.false_positive_count}")
0130 |             logger.info(f"   Needs review: {triage_result.needs_review_count}")
0131 |             
0132 |             return triage_result
0133 |             
0134 |         except Exception as e:
0135 |             logger.error(f"❌ Triage parsing failed: {e}")
0136 |             logger.exception("Full traceback:")
0137 |             raise LLMError(f"Failed to parse triage response: {e}")
0138 |     
0139 |     
0140 |     def parse_remediation_response(self, 
0141 |                                    llm_response: str, 
0142 |                                    vuln_type: str = None, 
0143 |                                    language: str = None) -> RemediationPlan:
0144 |         """
0145 |         Parsear respuesta LLM a RemediationPlan
0146 |         
0147 |         Args:
0148 |             llm_response: Respuesta cruda del LLM
0149 |             vuln_type: Tipo de vulnerabilidad (para logging)
0150 |             language: Lenguaje (para normalización)
0151 |             
0152 |         Returns:
0153 |             RemediationPlan validado
0154 |             
0155 |         Raises:
0156 |             LLMError: Si el parsing falla
0157 |         """
0158 |         
0159 |         logger.info(f"📥 Parsing remediation response ({len(llm_response):,} chars)...")
0160 |         
0161 |         try:
0162 |             # Paso 1: Limpiar respuesta
0163 |             cleaned = self.clean_json_response(llm_response)
0164 |             
0165 |             # Paso 2: Validar estructura
0166 |             validation = self.validate_json_structure(cleaned)
0167 |             
0168 |             if not validation['is_valid']:
0169 |                 logger.error(f"❌ JSON structure validation failed:")
0170 |                 for error in validation['errors']:
0171 |                     logger.error(f"   • {error}")
0172 |                 
0173 |                 # Intentar recuperación
0174 |                 extracted = self.extract_json(
0175 |                     cleaned,
0176 |                     required_fields=['vulnerability_type', 'priority_level', 'steps']
0177 |                 )
0178 |                 
0179 |                 if extracted:
0180 |                     cleaned = extracted
0181 |                     logger.info("✅ Recovery successful")
0182 |                 else:
0183 |                     raise LLMError(f"JSON structure invalid: {validation['errors']}")
0184 |             
0185 |             # Paso 3: Parsear JSON
0186 |             try:
0187 |                 response_data = json.loads(cleaned)
0188 |                 logger.info(f"✅ JSON parsed successfully")
0189 |             except json.JSONDecodeError as e:
0190 |                 logger.error(f"❌ JSON parsing failed: {e}")
0191 |                 
0192 |                 # Último intento
0193 |                 extracted = self.extract_json(
0194 |                     llm_response,
0195 |                     required_fields=['vulnerability_type', 'priority_level', 'steps']
0196 |                 )
0197 |                 
0198 |                 if extracted:
0199 |                     try:
0200 |                         response_data = json.loads(extracted)
0201 |                         logger.info("✅ Recovery parse successful")
0202 |                     except Exception:
0203 |                         raise LLMError(f"Failed to parse remediation response: {e}")
0204 |                 else:
0205 |                     raise LLMError(f"Failed to parse remediation response: {e}")
0206 |             
0207 |             # Paso 4: Validar campos requeridos
0208 |             self._validate_required_fields(
0209 |                 response_data,
0210 |                 required_fields=['vulnerability_type', 'priority_level', 'steps'],
0211 |                 response_type='remediation'
0212 |             )
0213 |             
0214 |             # Paso 5: Normalizar datos
0215 |             response_data = self._normalize_remediation_data(response_data, vuln_type)
0216 |             
0217 |             # Paso 6: Crear RemediationPlan
0218 |             remediation_plan = RemediationPlan(**response_data)
0219 |             
0220 |             # Paso 7: Validar calidad
0221 |             self._validate_remediation_quality(remediation_plan)
0222 |             
0223 |             # Paso 8: Log resultados
0224 |             logger.info(f"✅ RemediationPlan created successfully")
0225 |             logger.info(f"   Type: {remediation_plan.vulnerability_type.value}")
0226 |             logger.info(f"   Priority: {remediation_plan.priority_level}")
0227 |             logger.info(f"   Steps: {len(remediation_plan.steps)}")
0228 |             
0229 |             return remediation_plan
0230 |             
0231 |         except Exception as e:
0232 |             logger.error(f"❌ Remediation parsing failed: {e}")
0233 |             logger.exception("Full traceback:")
0234 |             raise LLMError(f"Failed to parse remediation response: {e}")
0235 |     
0236 |     
0237 |     # ============================================================================
0238 |     # JSON CLEANING & EXTRACTION
0239 |     # ============================================================================
0240 |     
0241 |     def clean_json_response(self, response: str) -> str:
0242 |         """
0243 |         Limpiar respuesta eliminando markdown, prefijos y ruido
0244 |         
0245 |         Maneja:
0246 |         - Markdown wrappers: ```json ... ```
0247 |         - Prefijos anómalos: L3##, etc
0248 |         - Líneas no-JSON al inicio/final
0249 |         - Caracteres de escape inválidos
0250 |         
0251 |         Args:
0252 |             response: Respuesta cruda del LLM
0253 |             
0254 |         Returns:
0255 |             JSON limpio y válido
0256 |         """
0257 |         
0258 |         original_length = len(response)
0259 |         cleaned = response.strip()
0260 |         
0261 |         if self.debug_enabled:
0262 |             logger.debug(f"🧹 Starting JSON cleaning (original: {original_length} chars)")
0263 |         
0264 |         # Paso 1: Remover wrapper markdown completo
0265 |         markdown_pattern = r'^```(?:json)?\s*\n(.*?)\n\s*```$'
0266 |         markdown_match = re.match(markdown_pattern, cleaned, re.DOTALL)
0267 |         
0268 |         if markdown_match:
0269 |             cleaned = markdown_match.group(1).strip()
0270 |             if self.debug_enabled:
0271 |                 logger.debug("✅ Removed markdown wrapper (```json ...```)")
0272 |         
0273 |         # Paso 2: Remover prefijos anómalos
0274 |         anomalous_prefixes = [
0275 |             'L3##```json\n', 'L3##json', 'L3##\n', 'L3##',
0276 |             '```json\n', '```json', '```\n', '```', 'json\n'
0277 |         ]
0278 |         
0279 |         for prefix in anomalous_prefixes:
0280 |             if cleaned.startswith(prefix):
0281 |                 cleaned = cleaned[len(prefix):].lstrip()
0282 |                 if self.debug_enabled:
0283 |                     logger.debug(f"✅ Removed prefix: '{prefix[:15]}'")
0284 |                 break
0285 |         
0286 |         # Paso 3: Remover sufijos
0287 |         anomalous_suffixes = ['\n```', '```', '`']
0288 |         
0289 |         for suffix in anomalous_suffixes:
0290 |             if cleaned.endswith(suffix):
0291 |                 cleaned = cleaned[:-len(suffix)].rstrip()
0292 |                 if self.debug_enabled:
0293 |                     logger.debug(f"✅ Removed suffix: '{suffix}'")
0294 |                 break
0295 |         
0296 |         # Paso 4: Limpiar líneas no-JSON al inicio
0297 |         lines = cleaned.split('\n')
0298 |         json_start_index = 0
0299 |         
0300 |         for i, line in enumerate(lines):
0301 |             stripped = line.strip()
0302 |             if stripped.startswith(('{', '[')):
0303 |                 json_start_index = i
0304 |                 break
0305 |         
0306 |         if json_start_index > 0:
0307 |             cleaned = '\n'.join(lines[json_start_index:])
0308 |             if self.debug_enabled:
0309 |                 logger.debug(f"✅ Skipped {json_start_index} non-JSON lines at start")
0310 |         
0311 |         # Paso 5: Limpiar líneas no-JSON al final
0312 |         lines = cleaned.split('\n')
0313 |         json_end_index = len(lines)
0314 |         
0315 |         for i in range(len(lines) - 1, -1, -1):
0316 |             stripped = lines[i].strip()
0317 |             if stripped.endswith(('}', ']')):
0318 |                 json_end_index = i + 1
0319 |                 break
0320 |         
0321 |         if json_end_index < len(lines):
0322 |             skipped = len(lines) - json_end_index
0323 |             cleaned = '\n'.join(lines[:json_end_index])
0324 |             if self.debug_enabled:
0325 |                 logger.debug(f"✅ Skipped {skipped} non-JSON lines at end")
0326 |         
0327 |         # Paso 6: Validar que no esté vacío
0328 |         cleaned = cleaned.strip()
0329 |         if not cleaned:
0330 |             raise ValueError("Response is empty after cleaning")
0331 |         
0332 |         # Paso 7: Corregir escapes inválidos
0333 |         cleaned = self._fix_escape_sequences(cleaned)
0334 |         
0335 |         # Log final
0336 |         final_length = len(cleaned)
0337 |         bytes_removed = original_length - final_length
0338 |         if self.debug_enabled:
0339 |             logger.debug(f"✅ Cleaning complete: {bytes_removed} bytes removed ({original_length} → {final_length})")
0340 |         
0341 |         return cleaned
0342 |     
0343 |     
0344 |     def validate_json_structure(self, text: str) -> Dict[str, Any]:
0345 |         """
0346 |         Validar estructura JSON antes de parsear
0347 |         
0348 |         Args:
0349 |             text: Texto que debería ser JSON
0350 |             
0351 |         Returns:
0352 |             Dict con información de validación:
0353 |             {
0354 |                 'is_valid': bool,
0355 |                 'errors': List[str],
0356 |                 'warnings': List[str]
0357 |             }
0358 |         """
0359 |         
0360 |         validation = {
0361 |             'is_valid': True,
0362 |             'errors': [],
0363 |             'warnings': []
0364 |         }
0365 |         
0366 |         # Verificar delimitadores balanceados
0367 |         open_braces = text.count('{')
0368 |         close_braces = text.count('}')
0369 |         open_brackets = text.count('[')
0370 |         close_brackets = text.count(']')
0371 |         
0372 |         if open_braces != close_braces:
0373 |             validation['is_valid'] = False
0374 |             validation['errors'].append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
0375 |         
0376 |         if open_brackets != close_brackets:
0377 |             validation['is_valid'] = False
0378 |             validation['errors'].append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
0379 |         
0380 |         # Verificar que empiece con { o [
0381 |         if not text.startswith(('{', '[')):
0382 |             validation['warnings'].append(f"JSON doesn't start with {{ or [")
0383 |         
0384 |         # Verificar que termine con } o ]
0385 |         if not text.endswith(('}', ']')):
0386 |             validation['warnings'].append(f"JSON doesn't end with }} or ]")
0387 |         
0388 |         return validation
0389 |     
0390 |     
0391 |     def extract_json(self, text: str, required_fields: List[str] = None) -> Optional[str]:
0392 |         """
0393 |         Extraer JSON de texto con ruido usando múltiples estrategias
0394 |         
0395 |         Estrategias (en orden de prioridad):
0396 |         1. Stack-based balancing con validación de estructura
0397 |         2. Regex pattern matching
0398 |         3. Simple first/last delimiter
0399 |         
0400 |         Args:
0401 |             text: Texto con JSON mezclado con ruido
0402 |             required_fields: Campos requeridos para considerar JSON válido
0403 |             
0404 |         Returns:
0405 |             JSON extraído o None si falla
0406 |         """
0407 |         
0408 |         logger.info("🔧 Attempting aggressive JSON extraction...")
0409 |         if required_fields:
0410 |             logger.debug(f"   Required fields: {required_fields}")
0411 |         
0412 |         # === MÉTODO 1: Stack-based balancing ===
0413 |         try:
0414 |             possible_jsons = []
0415 |             
0416 |             i = 0
0417 |             while i < len(text):
0418 |                 if text[i] == '{':
0419 |                     stack = ['{']
0420 |                     start_pos = i
0421 |                     j = i + 1
0422 |                     
0423 |                     while j < len(text) and stack:
0424 |                         if text[j] == '{':
0425 |                             stack.append('{')
0426 |                         elif text[j] == '}':
0427 |                             stack.pop()
0428 |                             if not stack:  # JSON completo encontrado
0429 |                                 end_pos = j + 1
0430 |                                 candidate = text[start_pos:end_pos]
0431 |                                 
0432 |                                 # Intentar parsear y validar
0433 |                                 try:
0434 |                                     parsed = json.loads(candidate)
0435 |                                     has_required = self._has_required_fields(parsed, required_fields)
0436 |                                     
0437 |                                     possible_jsons.append({
0438 |                                         'json': candidate,
0439 |                                         'parsed': parsed,
0440 |                                         'length': len(candidate),
0441 |                                         'start': start_pos,
0442 |                                         'has_required_fields': has_required,
0443 |                                         'available_fields': list(parsed.keys()) if isinstance(parsed, dict) else []
0444 |                                     })
0445 |                                 except json.JSONDecodeError:
0446 |                                     pass
0447 |                                 
0448 |                                 break
0449 |                         j += 1
0450 |                 i += 1
0451 |             
0452 |             if possible_jsons:
0453 |                 logger.info(f"   Found {len(possible_jsons)} valid JSON objects")
0454 |                 
0455 |                 # Priorizar por: campos requeridos > tamaño
0456 |                 possible_jsons.sort(key=lambda x: (
0457 |                     x['has_required_fields'],
0458 |                     x['length']
0459 |                 ), reverse=True)
0460 |                 
0461 |                 best_candidate = possible_jsons[0]
0462 |                 
0463 |                 if best_candidate['has_required_fields']:
0464 |                     logger.info(f"✅ Stack extraction successful ({best_candidate['length']} chars)")
0465 |                     logger.debug(f"   Fields found: {best_candidate['available_fields']}")
0466 |                     return best_candidate['json']
0467 |                 else:
0468 |                     logger.warning(f"⚠️ Best candidate missing required fields")
0469 |                     logger.warning(f"   Required: {required_fields}")
0470 |                     logger.warning(f"   Available: {best_candidate['available_fields']}")
0471 |                     logger.info(f"   Using largest JSON anyway ({best_candidate['length']} chars)")
0472 |                     return best_candidate['json']
0473 |             
0474 |             logger.debug("   Stack method found no valid JSON")
0475 |         
0476 |         except Exception as e:
0477 |             logger.debug(f"   Stack extraction failed: {e}")
0478 |         
0479 |         # === MÉTODO 2: Regex pattern matching ===
0480 |         logger.info("🔧 Trying regex extraction...")
0481 |         
0482 |         try:
0483 |             # Buscar patrón {...} con contenido
0484 |             pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
0485 |             matches = re.findall(pattern, text, re.DOTALL)
0486 |             
0487 |             if matches:
0488 |                 logger.info(f"   Found {len(matches)} potential JSON objects via regex")
0489 |                 
0490 |                 valid_matches = []
0491 |                 for match in matches:
0492 |                     try:
0493 |                         parsed = json.loads(match)
0494 |                         has_required = self._has_required_fields(parsed, required_fields)
0495 |                         
0496 |                         valid_matches.append({
0497 |                             'json': match,
0498 |                             'parsed': parsed,
0499 |                             'length': len(match),
0500 |                             'has_required_fields': has_required,
0501 |                             'available_fields': list(parsed.keys()) if isinstance(parsed, dict) else []
0502 |                         })
0503 |                     except json.JSONDecodeError:
0504 |                         continue
0505 |                 
0506 |                 if valid_matches:
0507 |                     # Ordenar por campos requeridos + tamaño
0508 |                     valid_matches.sort(key=lambda x: (
0509 |                         x['has_required_fields'],
0510 |                         x['length']
0511 |                     ), reverse=True)
0512 |                     
0513 |                     best = valid_matches[0]
0514 |                     
0515 |                     if best['has_required_fields']:
0516 |                         logger.info(f"✅ Regex extracted valid JSON ({best['length']} chars)")
0517 |                         return best['json']
0518 |                     else:
0519 |                         logger.warning(f"⚠️ Using largest regex match without required fields")
0520 |                         return best['json']
0521 |         
0522 |         except Exception as e:
0523 |             logger.debug(f"   Regex extraction failed: {e}")
0524 |         
0525 |         # === MÉTODO 3: Simple first/last delimiter ===
0526 |         logger.info("🔧 Trying simple first/last delimiter...")
0527 |         
0528 |         try:
0529 |             first_brace = text.find('{')
0530 |             last_brace = text.rfind('}')
0531 |             
0532 |             if first_brace >= 0 and last_brace > first_brace:
0533 |                 extracted = text[first_brace:last_brace + 1]
0534 |                 try:
0535 |                     parsed = json.loads(extracted)
0536 |                     has_required = self._has_required_fields(parsed, required_fields)
0537 |                     
0538 |                     if has_required or not required_fields:
0539 |                         logger.info(f"✅ Simple extraction successful ({len(extracted)} chars)")
0540 |                         return extracted
0541 |                     else:
0542 |                         logger.warning(f"⚠️ Simple extraction missing required fields")
0543 |                         return extracted
0544 |                 
0545 |                 except json.JSONDecodeError as e:
0546 |                     logger.debug(f"   Simple extraction not valid JSON: {e}")
0547 |         
0548 |         except Exception as e:
0549 |             logger.debug(f"   Simple extraction failed: {e}")
0550 |         
0551 |         # Todos los métodos fallaron
0552 |         logger.error("❌ All extraction methods failed")
0553 |         return None
0554 |     
0555 |     
0556 |     # ============================================================================
0557 |     # HELPER METHODS - PRIVATE
0558 |     # ============================================================================
0559 |     
0560 |     def _fix_escape_sequences(self, text: str) -> str:
0561 |         """
0562 |         Corregir secuencias de escape inválidas en JSON
0563 |         
0564 |         JSON válido solo acepta: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
0565 |         
0566 |         Args:
0567 |             text: Texto con posibles escapes inválidos
0568 |             
0569 |         Returns:
0570 |             Texto con escapes corregidos
0571 |         """
0572 |         
0573 |         result = []
0574 |         i = 0
0575 |         
0576 |         while i < len(text):
0577 |             if text[i] == '\\' and i + 1 < len(text):
0578 |                 next_char = text[i + 1]
0579 |                 
0580 |                 # Escapes válidos simples
0581 |                 if next_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']:
0582 |                     result.append(text[i:i+2])
0583 |                     i += 2
0584 |                     continue
0585 |                 
0586 |                 # Escape unicode: \uXXXX
0587 |                 elif next_char == 'u' and i + 5 < len(text):
0588 |                     hex_part = text[i+2:i+6]
0589 |                     if re.match(r'^[0-9a-fA-F]{4}$', hex_part):
0590 |                         result.append(text[i:i+6])
0591 |                         i += 6
0592 |                         continue
0593 |                 
0594 |                 # Escape inválido - escapar el backslash
0595 |                 if self.debug_enabled:
0596 |                     logger.debug(f"🔧 Fixed invalid escape: \\{next_char}")
0597 |                 result.append('\\\\' + next_char)
0598 |                 i += 2
0599 |             else:
0600 |                 result.append(text[i])
0601 |                 i += 1
0602 |         
0603 |         return ''.join(result)
0604 |     
0605 |     
0606 |     def _has_required_fields(self, parsed: Any, required_fields: Optional[List[str]]) -> bool:
0607 |         """
0608 |         Verificar si un objeto parseado tiene los campos requeridos
0609 |         
0610 |         Args:
0611 |             parsed: Objeto parseado (dict, list, etc)
0612 |             required_fields: Lista de campos requeridos
0613 |             
0614 |         Returns:
0615 |             True si tiene todos los campos requeridos (o si no hay campos requeridos)
0616 |         """
0617 |         
0618 |         if not required_fields:
0619 |             return True
0620 |         
0621 |         if not isinstance(parsed, dict):
0622 |             return False
0623 |         
0624 |         return all(field in parsed for field in required_fields)
0625 |     
0626 |     
0627 |     def _validate_required_fields(self, 
0628 |                                    response_ Dict[str, Any], 
0629 |                                    required_fields: List[str],
0630 |                                    response_type: str) -> None:
0631 |         """
0632 |         Validar que un dict tenga los campos requeridos
0633 |         
0634 |         Args:
0635 |             response_ Dict con la respuesta parseada
0636 |             required_fields: Campos que deben estar presentes
0637 |             response_type: Tipo de respuesta (para mensajes de error)
0638 |             
0639 |         Raises:
0640 |             LLMError: Si faltan campos requeridos
0641 |         """
0642 |         
0643 |         if not isinstance(response_data, dict):
0644 |             raise LLMError(f"{response_type} response is not a dict: {type(response_data)}")
0645 |         
0646 |         missing = [f for f in required_fields if f not in response_data]
0647 |         
0648 |         if missing:
0649 |             available = list(response_data.keys())
0650 |             raise LLMError(
0651 |                 f"{response_type} response missing required fields: {missing}. "
0652 |                 f"Available: {available}"
0653 |             )
0654 |         
0655 |         logger.debug(f"✅ All required fields present: {required_fields}")
0656 |     
0657 |     
0658 |     def _normalize_remediation_data(self, 
0659 |                                      response_ Dict[str, Any], 
0660 |                                      vuln_type: str = None) -> Dict[str, Any]:
0661 |         """
0662 |         Normalizar datos de remediación para asegurar compatibilidad con RemediationPlan
0663 |         
0664 |         Args:
0665 |             response_ Datos parseados del LLM
0666 |             vuln_type: Tipo de vulnerabilidad (fallback)
0667 |             
0668 |         Returns:
0669 |             Datos normalizados
0670 |         """
0671 |         
0672 |         # Asegurar que vulnerability_id existe
0673 |         if 'vulnerability_id' not in response_
0674 |             response_data['vulnerability_id'] = f"{vuln_type or 'unknown'}-remediation-{int(time.time())}"
0675 |             logger.warning(f"⚠️ Added missing vulnerability_id: {response_data['vulnerability_id']}")
0676 |         
0677 |         # Asegurar que llm_model_used existe
0678 |         if 'llm_model_used' not in response_
0679 |             response_data['llm_model_used'] = 'meta-llama/llama-3-3-70b-instruct'
0680 |             logger.debug("   Added default llm_model_used")
0681 |         
0682 |         # Validar que steps tenga contenido
0683 |         if not response_data.get('steps') or len(response_data['steps']) < 1:
0684 |             raise LLMError("Response has no remediation steps")
0685 |         
0686 |         return response_data
0687 |     
0688 |     
0689 |     def _validate_remediation_quality(self, plan: RemediationPlan) -> None:
0690 |         """
0691 |         Validar calidad de los steps del plan de remediación
0692 |         
0693 |         Args:
0694 |             plan: Plan de remediación a validar
0695 |             
0696 |         Warnings:
0697 |             Genera warnings si los steps tienen calidad baja
0698 |         """
0699 |         
0700 |         for i, step in enumerate(plan.steps, 1):
0701 |             desc_length = len(step.description)
0702 |             if desc_length < 50:
0703 |                 logger.warning(f"⚠️ Step {i} has short description ({desc_length} chars)")
0704 |             
0705 |             if not step.title or len(step.title) < 10:
0706 |                 logger.warning(f"⚠️ Step {i} has very short title")
0707 | 
0708 | 
0709 | # ============================================================================
0710 | # FACTORY FUNCTION
0711 | # ============================================================================
0712 | 
0713 | def create_response_parser(debug_enabled: bool = False) -> LLMResponseParser:
0714 |     """
0715 |     Factory function para crear parser
0716 |     
0717 |     Args:
0718 |         debug_enabled: Habilitar logging debug detallado
0719 |         
0720 |     Returns:
0721 |         LLMResponseParser configurado
0722 |     """
0723 |     return LLMResponseParser(debug_enabled=debug_enabled)
```

---

### security_report.html

**Ruta:** `security_report.html`

```html
0001 |  <!-- adapters/output/templates/report.html -->
0002 | <!DOCTYPE html>
0003 | <html lang="es">
0004 | <head>
0005 |     <meta charset="UTF-8">
0006 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0007 |     <title>🛡️ Security Analysis Platform v3.0 - Report</title>
0008 | <!-- adapters/output/templates/styles.html -->
0009 | <style>
0010 | /* === RESET & BASE === */
0011 | * {
0012 |     margin: 0;
0013 |     padding: 0;
0014 |     box-sizing: border-box;
0015 | }
0016 | 
0017 | body {
0018 |     font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
0019 |     line-height: 1.6;
0020 |     color: #1f2937;
0021 |     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
0022 |     min-height: 100vh;
0023 | }
0024 | 
0025 | /* === LAYOUT === */
0026 | .container {
0027 |     max-width: 1200px;
0028 |     margin: 20px auto;
0029 |     background: white;
0030 |     border-radius: 16px;
0031 |     box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
0032 |     overflow: hidden;
0033 | }
0034 | 
0035 | /* === HEADER === */
0036 | .header {
0037 |     background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
0038 |     color: white;
0039 |     padding: 2rem;
0040 |     position: relative;
0041 | }
0042 | 
0043 | .header::before {
0044 |     content: '';
0045 |     position: absolute;
0046 |     top: 0;
0047 |     left: 0;
0048 |     right: 0;
0049 |     bottom: 0;
0050 |     background: url('image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
0051 |     opacity: 0.3;
0052 | }
0053 | 
0054 | .header-content {
0055 |     position: relative;
0056 |     z-index: 1;
0057 |     text-align: center;
0058 | }
0059 | 
0060 | .header h1 {
0061 |     font-size: 2.5rem;
0062 |     font-weight: 700;
0063 |     margin-bottom: 1rem;
0064 |     text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
0065 | }
0066 | 
0067 | .header-grid {
0068 |     display: grid;
0069 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0070 |     gap: 1rem;
0071 |     margin-top: 1.5rem;
0072 | }
0073 | 
0074 | .header-item {
0075 |     background: rgba(255, 255, 255, 0.15);
0076 |     padding: 1rem;
0077 |     border-radius: 12px;
0078 |     backdrop-filter: blur(10px);
0079 |     border: 1px solid rgba(255, 255, 255, 0.2);
0080 | }
0081 | 
0082 | .header-label {
0083 |     font-size: 0.875rem;
0084 |     opacity: 0.9;
0085 |     margin-bottom: 0.25rem;
0086 | }
0087 | 
0088 | .header-value {
0089 |     font-size: 1.25rem;
0090 |     font-weight: 600;
0091 | }
0092 | 
0093 | /* === CONTENT === */
0094 | .content {
0095 |     padding: 2rem;
0096 | }
0097 | 
0098 | .section {
0099 |     margin-bottom: 3rem;
0100 | }
0101 | 
0102 | .section-title {
0103 |     font-size: 1.875rem;
0104 |     font-weight: 700;
0105 |     color: #1f2937;
0106 |     margin-bottom: 1.5rem;
0107 |     padding-bottom: 0.75rem;
0108 |     border-bottom: 3px solid #4f46e5;
0109 |     position: relative;
0110 | }
0111 | 
0112 | .section-title::after {
0113 |     content: '';
0114 |     position: absolute;
0115 |     bottom: -3px;
0116 |     left: 0;
0117 |     width: 60px;
0118 |     height: 3px;
0119 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0120 | }
0121 | 
0122 | /* === METRICS === */
0123 | .metrics-grid {
0124 |     display: grid;
0125 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0126 |     gap: 1.5rem;
0127 |     margin-bottom: 2rem;
0128 | }
0129 | 
0130 | .metric-card {
0131 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0132 |     border-radius: 16px;
0133 |     padding: 1.5rem;
0134 |     text-align: center;
0135 |     transition: transform 0.3s ease, box-shadow 0.3s ease;
0136 |     position: relative;
0137 |     overflow: hidden;
0138 | }
0139 | 
0140 | .metric-card::before {
0141 |     content: '';
0142 |     position: absolute;
0143 |     top: 0;
0144 |     left: 0;
0145 |     right: 0;
0146 |     height: 4px;
0147 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0148 | }
0149 | 
0150 | .metric-card:hover {
0151 |     transform: translateY(-4px);
0152 |     box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
0153 | }
0154 | 
0155 | .metric-icon {
0156 |     font-size: 2rem;
0157 |     margin-bottom: 0.5rem;
0158 | }
0159 | 
0160 | .metric-value {
0161 |     font-size: 2.5rem;
0162 |     font-weight: 700;
0163 |     margin-bottom: 0.5rem;
0164 |     background: linear-gradient(135deg, #4f46e5, #7c3aed);
0165 |     -webkit-background-clip: text;
0166 |     -webkit-text-fill-color: transparent;
0167 |     background-clip: text;
0168 | }
0169 | 
0170 | .metric-label {
0171 |     color: #64748b;
0172 |     font-size: 0.875rem;
0173 |     font-weight: 500;
0174 |     text-transform: uppercase;
0175 |     letter-spacing: 0.05em;
0176 | }
0177 | 
0178 | /* === VULNERABILITIES === */
0179 | .vulnerabilities-list {
0180 |     display: grid;
0181 |     gap: 1.5rem;
0182 | }
0183 | 
0184 | .vulnerability-card {
0185 |     background: white;
0186 |     border: 1px solid #e5e7eb;
0187 |     border-radius: 16px;
0188 |     overflow: hidden;
0189 |     transition: all 0.3s ease;
0190 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0191 | }
0192 | 
0193 | .vulnerability-card:hover {
0194 |     box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
0195 |     transform: translateY(-2px);
0196 | }
0197 | 
0198 | .vulnerability-card.critical {
0199 |     border-left: 6px solid #dc2626;
0200 | }
0201 | 
0202 | .vulnerability-card.high {
0203 |     border-left: 6px solid #ea580c;
0204 | }
0205 | 
0206 | .vulnerability-card.medium {
0207 |     border-left: 6px solid #d97706;
0208 | }
0209 | 
0210 | .vulnerability-card.low {
0211 |     border-left: 6px solid #16a34a;
0212 | }
0213 | 
0214 | .vulnerability-card.info {
0215 |     border-left: 6px solid #0ea5e9;
0216 | }
0217 | 
0218 | .vuln-header {
0219 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0220 |     padding: 1.5rem;
0221 |     border-bottom: 1px solid #e5e7eb;
0222 |     display: flex;
0223 |     justify-content: space-between;
0224 |     align-items: flex-start;
0225 |     gap: 1rem;
0226 | }
0227 | 
0228 | .vuln-title {
0229 |     font-size: 1.25rem;
0230 |     font-weight: 600;
0231 |     color: #1f2937;
0232 |     flex: 1;
0233 | }
0234 | 
0235 | .vuln-badges {
0236 |     display: flex;
0237 |     gap: 0.5rem;
0238 |     flex-shrink: 0;
0239 | }
0240 | 
0241 | .badge {
0242 |     padding: 0.25rem 0.75rem;
0243 |     border-radius: 12px;
0244 |     font-size: 0.75rem;
0245 |     font-weight: 600;
0246 |     text-transform: uppercase;
0247 |     letter-spacing: 0.05em;
0248 | }
0249 | 
0250 | .badge.severity-critical {
0251 |     background: #dc2626;
0252 |     color: white;
0253 | }
0254 | 
0255 | .badge.severity-high {
0256 |     background: #ea580c;
0257 |     color: white;
0258 | }
0259 | 
0260 | .badge.severity-medium {
0261 |     background: #d97706;
0262 |     color: white;
0263 | }
0264 | 
0265 | .badge.severity-low {
0266 |     background: #16a34a;
0267 |     color: white;
0268 | }
0269 | 
0270 | .badge.severity-info {
0271 |     background: #0ea5e9;
0272 |     color: white;
0273 | }
0274 | 
0275 | .badge.type-badge {
0276 |     background: #6b7280;
0277 |     color: white;
0278 | }
0279 | 
0280 | .vuln-body {
0281 |     padding: 1.5rem;
0282 | }
0283 | 
0284 | .vuln-meta {
0285 |     display: grid;
0286 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0287 |     gap: 1rem;
0288 |     margin-bottom: 1.5rem;
0289 | }
0290 | 
0291 | .meta-item {
0292 |     background: #f8fafc;
0293 |     padding: 0.75rem;
0294 |     border-radius: 8px;
0295 |     border: 1px solid #e5e7eb;
0296 | }
0297 | 
0298 | .meta-label {
0299 |     font-size: 0.75rem;
0300 |     font-weight: 600;
0301 |     color: #6b7280;
0302 |     text-transform: uppercase;
0303 |     letter-spacing: 0.05em;
0304 |     margin-bottom: 0.25rem;
0305 | }
0306 | 
0307 | .meta-value {
0308 |     font-weight: 500;
0309 |     color: #1f2937;
0310 | }
0311 | 
0312 | .meta-value a {
0313 |     color: #4f46e5;
0314 |     text-decoration: none;
0315 | }
0316 | 
0317 | .meta-value a:hover {
0318 |     text-decoration: underline;
0319 | }
0320 | 
0321 | .vuln-description,
0322 | .vuln-code,
0323 | .vuln-remediation {
0324 |     margin-bottom: 1.5rem;
0325 | }
0326 | 
0327 | .vuln-description h4,
0328 | .vuln-code h4,
0329 | .vuln-remediation h4 {
0330 |     font-size: 1rem;
0331 |     font-weight: 600;
0332 |     color: #374151;
0333 |     margin-bottom: 0.75rem;
0334 |     display: flex;
0335 |     align-items: center;
0336 |     gap: 0.5rem;
0337 | }
0338 | 
0339 | .code-block {
0340 |     background: #0f172a;
0341 |     color: #e2e8f0;
0342 |     padding: 1rem;
0343 |     border-radius: 8px;
0344 |     font-family: 'JetBrains Mono', 'Fira Code', Monaco, monospace;
0345 |     font-size: 0.875rem;
0346 |     overflow-x: auto;
0347 |     line-height: 1.5;
0348 |     border: 1px solid #334155;
0349 | }
0350 | 
0351 | .advice-content {
0352 |     background: #dbeafe;
0353 |     padding: 1rem;
0354 |     border-radius: 8px;
0355 |     border-left: 4px solid #3b82f6;
0356 |     color: #1e40af;
0357 | }
0358 | 
0359 | /* === NO VULNERABILITIES === */
0360 | .no-vulnerabilities {
0361 |     text-align: center;
0362 |     padding: 4rem 2rem;
0363 |     background: linear-gradient(135deg, #22c55e, #16a34a);
0364 |     color: white;
0365 |     border-radius: 16px;
0366 | }
0367 | 
0368 | .no-vulns-icon {
0369 |     font-size: 4rem;
0370 |     margin-bottom: 1rem;
0371 | }
0372 | 
0373 | .no-vulnerabilities h2 {
0374 |     font-size: 2rem;
0375 |     margin-bottom: 1rem;
0376 | }
0377 | 
0378 | /* === REMEDIATION === */
0379 | .remediation-summary {
0380 |     background: #f0f9ff;
0381 |     padding: 1rem;
0382 |     border-radius: 8px;
0383 |     border-left: 4px solid #0ea5e9;
0384 |     margin-bottom: 2rem;
0385 | }
0386 | 
0387 | .remediation-plans {
0388 |     display: grid;
0389 |     gap: 2rem;
0390 | }
0391 | 
0392 | .remediation-card {
0393 |     background: white;
0394 |     border: 1px solid #e5e7eb;
0395 |     border-radius: 12px;
0396 |     padding: 1.5rem;
0397 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0398 | }
0399 | 
0400 | .plan-header {
0401 |     display: flex;
0402 |     justify-content: space-between;
0403 |     align-items: center;
0404 |     margin-bottom: 1rem;
0405 | }
0406 | 
0407 | .plan-header h3 {
0408 |     font-size: 1.25rem;
0409 |     font-weight: 600;
0410 |     color: #1f2937;
0411 | }
0412 | 
0413 | .priority-badge {
0414 |     padding: 0.25rem 0.75rem;
0415 |     border-radius: 20px;
0416 |     font-size: 0.75rem;
0417 |     font-weight: 600;
0418 |     text-transform: uppercase;
0419 | }
0420 | 
0421 | .priority-badge.priority-immediate {
0422 |     background: #dc2626;
0423 |     color: white;
0424 | }
0425 | 
0426 | .priority-badge.priority-high {
0427 |     background: #ea580c;
0428 |     color: white;
0429 | }
0430 | 
0431 | .priority-badge.priority-medium {
0432 |     background: #d97706;
0433 |     color: white;
0434 | }
0435 | 
0436 | .priority-badge.priority-low {
0437 |     background: #16a34a;
0438 |     color: white;
0439 | }
0440 | 
0441 | .plan-meta {
0442 |     display: flex;
0443 |     gap: 1rem;
0444 |     margin-bottom: 1.5rem;
0445 |     flex-wrap: wrap;
0446 | }
0447 | 
0448 | .plan-stat {
0449 |     background: #f3f4f6;
0450 |     padding: 0.5rem 1rem;
0451 |     border-radius: 6px;
0452 |     font-size: 0.875rem;
0453 |     font-weight: 500;
0454 | }
0455 | 
0456 | .plan-steps {
0457 |     margin-bottom: 1.5rem;
0458 | }
0459 | 
0460 | .plan-steps h4 {
0461 |     font-size: 1rem;
0462 |     font-weight: 600;
0463 |     margin-bottom: 1rem;
0464 |     color: #374151;
0465 | }
0466 | 
0467 | .plan-steps ol {
0468 |     list-style: none;
0469 |     counter-reset: step-counter;
0470 | }
0471 | 
0472 | .remediation-step {
0473 |     counter-increment: step-counter;
0474 |     margin-bottom: 1rem;
0475 |     padding: 1rem;
0476 |     background: #f8fafc;
0477 |     border-radius: 8px;
0478 |     border-left: 4px solid #4f46e5;
0479 |     position: relative;
0480 |     padding-left: 3rem;
0481 | }
0482 | 
0483 | .remediation-step::before {
0484 |     content: counter(step-counter);
0485 |     position: absolute;
0486 |     left: 1rem;
0487 |     top: 1rem;
0488 |     background: #4f46e5;
0489 |     color: white;
0490 |     width: 1.5rem;
0491 |     height: 1.5rem;
0492 |     border-radius: 50%;
0493 |     display: flex;
0494 |     align-items: center;
0495 |     justify-content: center;
0496 |     font-weight: 600;
0497 |     font-size: 0.875rem;
0498 | }
0499 | 
0500 | .step-header {
0501 |     display: flex;
0502 |     justify-content: space-between;
0503 |     align-items: flex-start;
0504 |     margin-bottom: 0.5rem;
0505 | }
0506 | 
0507 | .step-meta {
0508 |     font-size: 0.75rem;
0509 |     color: #6b7280;
0510 |     background: #e5e7eb;
0511 |     padding: 0.25rem 0.5rem;
0512 |     border-radius: 4px;
0513 | }
0514 | 
0515 | .step-description {
0516 |     color: #4b5563;
0517 |     margin-bottom: 0.75rem;
0518 | }
0519 | 
0520 | .step-code {
0521 |     background: #f3f4f6;
0522 |     color: #374151;
0523 |     padding: 0.75rem;
0524 |     border-radius: 6px;
0525 |     font-family: 'JetBrains Mono', monospace;
0526 |     font-size: 0.8rem;
0527 |     border: 1px solid #d1d5db;
0528 | }
0529 | 
0530 | .risk-warning {
0531 |     background: #fef2f2;
0532 |     padding: 1rem;
0533 |     border-radius: 8px;
0534 |     border-left: 4px solid #ef4444;
0535 |     color: #991b1b;
0536 | }
0537 | 
0538 | .risk-warning h5 {
0539 |     font-weight: 600;
0540 |     margin-bottom: 0.5rem;
0541 | }
0542 | 
0543 | /* === TECHNICAL DETAILS === */
0544 | .technical-details {
0545 |     background: #f8fafc;
0546 |     border: 1px solid #e5e7eb;
0547 |     border-radius: 12px;
0548 |     overflow: hidden;
0549 | }
0550 | 
0551 | .details-toggle {
0552 |     background: #f1f5f9;
0553 |     padding: 1rem 1.5rem;
0554 |     cursor: pointer;
0555 |     font-weight: 600;
0556 |     color: #374151;
0557 |     display: flex;
0558 |     align-items: center;
0559 |     gap: 0.5rem;
0560 |     border: none;
0561 |     width: 100%;
0562 |     text-align: left;
0563 |     transition: background 0.2s;
0564 | }
0565 | 
0566 | .details-toggle:hover {
0567 |     background: #e2e8f0;
0568 | }
0569 | 
0570 | .details-toggle::after {
0571 |     content: '▶';
0572 |     margin-left: auto;
0573 |     transition: transform 0.3s;
0574 | }
0575 | 
0576 | .technical-details[open] .details-toggle::after {
0577 |     transform: rotate(90deg);
0578 | }
0579 | 
0580 | .details-content {
0581 |     padding: 1.5rem;
0582 | }
0583 | 
0584 | .tech-grid {
0585 |     display: grid;
0586 |     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
0587 |     gap: 1.5rem;
0588 |     margin-bottom: 1.5rem;
0589 | }
0590 | 
0591 | .tech-item h4 {
0592 |     font-weight: 600;
0593 |     color: #374151;
0594 |     margin-bottom: 0.75rem;
0595 | }
0596 | 
0597 | .tech-item ul {
0598 |     list-style: none;
0599 |     padding-left: 0;
0600 | }
0601 | 
0602 | .tech-item li {
0603 |     padding: 0.25rem 0;
0604 |     color: #6b7280;
0605 | }
0606 | 
0607 | .analysis-summary {
0608 |     background: white;
0609 |     padding: 1rem;
0610 |     border-radius: 8px;
0611 |     border: 1px solid #e5e7eb;
0612 | }
0613 | 
0614 | .analysis-summary h4 {
0615 |     font-weight: 600;
0616 |     color: #374151;
0617 |     margin-bottom: 0.75rem;
0618 | }
0619 | 
0620 | .analysis-summary pre {
0621 |     background: #f8fafc;
0622 |     padding: 1rem;
0623 |     border-radius: 6px;
0624 |     font-size: 0.875rem;
0625 |     color: #4b5563;
0626 |     white-space: pre-wrap;
0627 |     word-wrap: break-word;
0628 | }
0629 | 
0630 | /* === FOOTER === */
0631 | .footer {
0632 |     background: #1f2937;
0633 |     color: white;
0634 |     padding: 2rem;
0635 |     text-align: center;
0636 | }
0637 | 
0638 | .footer-content p {
0639 |     margin-bottom: 0.5rem;
0640 | }
0641 | 
0642 | /* === RESPONSIVE DESIGN === */
0643 | @media (max-width: 768px) {
0644 |     .container {
0645 |         margin: 10px;
0646 |         border-radius: 8px;
0647 |     }
0648 |     
0649 |     .header {
0650 |         padding: 1.5rem;
0651 |     }
0652 |     
0653 |     .header h1 {
0654 |         font-size: 2rem;
0655 |     }
0656 |     
0657 |     .header-grid {
0658 |         grid-template-columns: 1fr;
0659 |     }
0660 |     
0661 |     .content {
0662 |         padding: 1.5rem;
0663 |     }
0664 |     
0665 |     .metrics-grid {
0666 |         grid-template-columns: 1fr;
0667 |     }
0668 |     
0669 |     .vuln-header {
0670 |         flex-direction: column;
0671 |         align-items: flex-start;
0672 |     }
0673 |     
0674 |     .vuln-meta {
0675 |         grid-template-columns: 1fr;
0676 |     }
0677 |     
0678 |     .plan-header {
0679 |         flex-direction: column;
0680 |         align-items: flex-start;
0681 |         gap: 0.5rem;
0682 |     }
0683 |     
0684 |     .plan-meta {
0685 |         flex-direction: column;
0686 |     }
0687 |     
0688 |     .step-header {
0689 |         flex-direction: column;
0690 |         align-items: flex-start;
0691 |     }
0692 | }
0693 | 
0694 | /* === ANIMATIONS === */
0695 | @keyframes fadeIn {
0696 |     from {
0697 |         opacity: 0;
0698 |         transform: translateY(20px);
0699 |     }
0700 |     to {
0701 |         opacity: 1;
0702 |         transform: translateY(0);
0703 |     }
0704 | }
0705 | 
0706 | .section {
0707 |     animation: fadeIn 0.6s ease-out;
0708 | }
0709 | 
0710 | /* === PRINT STYLES === */
0711 | @media print {
0712 |     body {
0713 |         background: white;
0714 |     }
0715 |     
0716 |     .container {
0717 |         box-shadow: none;
0718 |         margin: 0;
0719 |     }
0720 |     
0721 |     .header {
0722 |         background: #4f46e5 !important;
0723 |         -webkit-print-color-adjust: exact;
0724 |         color-adjust: exact;
0725 |     }
0726 |     
0727 |     .technical-details {
0728 |         border: 1px solid #ccc;
0729 |     }
0730 |     
0731 |     .details-content {
0732 |         display: block !important;
0733 |     }
0734 |     
0735 |     .details-toggle {
0736 |         display: none;
0737 |     }
0738 |     
0739 |     .vulnerability-card {
0740 |         break-inside: avoid;
0741 |         page-break-inside: avoid;
0742 |         margin-bottom: 1rem;
0743 |     }
0744 | }
0745 | </style></head>
0746 | <body>
0747 |     <div class="container">
0748 |         <!-- Header -->
0749 |         <header class="header">
0750 |             <div class="header-content">
0751 |                 <h1>🛡️ Security Analysis Report</h1>
0752 |                 <div class="header-grid">
0753 |                     <div class="header-item">
0754 |                         <div class="header-label">📁 File</div>
0755 |                         <div class="header-value">abap_sample.json</div>
0756 |                     </div>
0757 |                     <div class="header-item">
0758 |                         <div class="header-label">📊 Total Vulnerabilities</div>
0759 |                         <div class="header-value">2</div>
0760 |                     </div>
0761 |                     <div class="header-item">
0762 |                         <div class="header-label">⚡ High Priority</div>
0763 |                         <div class="header-value">2</div>
0764 |                     </div>
0765 |                     <div class="header-item">
0766 |                         <div class="header-label">🎯 Risk Score</div>
0767 |                         <div class="header-value">7.0/10</div>
0768 |                     </div>
0769 |                 </div>
0770 |             </div>
0771 |         </header>
0772 | 
0773 |         <main class="content">
0774 |             <!-- Executive Summary -->
0775 |             <section class="section">
0776 |                 <h2 class="section-title">📈 Executive Summary</h2>
0777 |                 
0778 |                 <div class="metrics-grid">
0779 |                     <div class="metric-card high">
0780 |                         <div class="metric-icon">⚡</div>
0781 |                         <div class="metric-value">2</div>
0782 |                         <div class="metric-label">ALTA</div>
0783 |                     </div>
0784 |                 </div>
0785 | 
0786 |                 <div class="summary-info">
0787 |                     <p><strong>Analysis completed in 36.09s</strong></p>
0788 |                     <p>🤖 AI-powered triage analyzed 2 vulnerabilities</p>
0789 |                 </div>
0790 |             </section>
0791 | 
0792 |             <!-- Vulnerabilities -->
0793 |             <section class="section">
0794 |                 <h2 class="section-title">🚨 Security Vulnerabilities</h2>
0795 |                 
0796 |                 <div class="vulnerabilities-list">
0797 |                     <div class="vulnerability-card high">
0798 |                         <div class="vuln-header">
0799 |                             <h3 class="vuln-title">
0800 |                                 📄 1. Directory Traversal
0801 |                             </h3>
0802 |                             <div class="vuln-badges">
0803 |                                 <span class="badge severity-high">
0804 |                                     ALTA
0805 |                                 </span>
0806 |                                 <span class="badge type-badge">Directory Traversal</span>
0807 |                             </div>
0808 |                         </div>
0809 |                         
0810 |                         <div class="vuln-body">
0811 |                             <div class="vuln-meta">
0812 |                                 <div class="meta-item">
0813 |                                     <span class="meta-label">📍 Location</span>
0814 |                                     <span class="meta-value">test-code\YAL0029.TXT:679</span>
0815 |                                 </div>
0816 |                                 <div class="meta-item">
0817 |                                     <span class="meta-label">🆔 ID</span>
0818 |                                     <span class="meta-value">abap-directory-traversal-001</span>
0819 |                                 </div>
0820 |                                 <div class="meta-item">
0821 |                                     <span class="meta-label">🔗 CWE</span>
0822 |                                     <span class="meta-value">
0823 |                                         <a href="https://cwe.mitre.org/data/definitions/22.html" target="_blank">
0824 |                                             CWE-22
0825 |                                         </a>
0826 |                                     </span>
0827 |                                 </div>
0828 |                             </div>
0829 |                             
0830 |                             <div class="vuln-description">
0831 |                                 <h4>📝 Description</h4>
0832 |                                 <p>File operation with unvalidated path may allow directory traversal</p>
0833 |                             </div>
0834 |                             
0835 |                             <div class="vuln-code">
0836 |                                 <h4>💻 Code Context</h4>
0837 |                                 <pre class="code-block">  1 |    
0838 |   2 |      ELSEIF rb_ser EQ abap_true.
0839 |   3 |        CONCATENATE p_path p_nfich INTO ld_path SEPARATED BY &#39;/&#39;.
0840 |   4 | &gt;&gt;     OPEN DATASET ld_path FOR OUTPUT IN TEXT MODE ENCODING UTF-8.
0841 |   5 |        IF sy-subrc EQ 0.
0842 |   6 |          lf_fich_open = abap_true.
0843 |   7 |        ELSE.</pre>
0844 |                             </div>
0845 |                             
0846 |                             <div class="vuln-remediation">
0847 |                                 <h4>💡 Remediation Advice</h4>
0848 |                                 <div class="advice-content">
0849 |     Prevent directory traversal:
0850 |     - Validate file paths using FILE_VALIDATE_NAME
0851 |     - Use absolute paths with proper validation
0852 |     - Implement allowlist for accessible directories
0853 |     - Check sy-subrc after FILE_VALIDATE_NAME call
0854 |     
0855 |     Example:
0856 |     CALL FUNCTION &#39;FILE_VALIDATE_NAME&#39;
0857 |       EXPORTING logical_filename = file_path
0858 |       EXCEPTIONS OTHERS = 1.
0859 |     IF sy-subrc = 0.
0860 |       &#34; Safe to use file_path
0861 |     ENDIF.
0862 |     </div>
0863 |                             </div>
0864 |                         </div>
0865 |                     </div>
0866 |                     <div class="vulnerability-card high">
0867 |                         <div class="vuln-header">
0868 |                             <h3 class="vuln-title">
0869 |                                 📄 2. Directory Traversal
0870 |                             </h3>
0871 |                             <div class="vuln-badges">
0872 |                                 <span class="badge severity-high">
0873 |                                     ALTA
0874 |                                 </span>
0875 |                                 <span class="badge type-badge">Directory Traversal</span>
0876 |                             </div>
0877 |                         </div>
0878 |                         
0879 |                         <div class="vuln-body">
0880 |                             <div class="vuln-meta">
0881 |                                 <div class="meta-item">
0882 |                                     <span class="meta-label">📍 Location</span>
0883 |                                     <span class="meta-value">test-code\YAL0029.TXT:780</span>
0884 |                                 </div>
0885 |                                 <div class="meta-item">
0886 |                                     <span class="meta-label">🆔 ID</span>
0887 |                                     <span class="meta-value">abap-directory-traversal-001</span>
0888 |                                 </div>
0889 |                                 <div class="meta-item">
0890 |                                     <span class="meta-label">🔗 CWE</span>
0891 |                                     <span class="meta-value">
0892 |                                         <a href="https://cwe.mitre.org/data/definitions/22.html" target="_blank">
0893 |                                             CWE-22
0894 |                                         </a>
0895 |                                     </span>
0896 |                                 </div>
0897 |                             </div>
0898 |                             
0899 |                             <div class="vuln-description">
0900 |                                 <h4>📝 Description</h4>
0901 |                                 <p>File operation with unvalidated path may allow directory traversal</p>
0902 |                             </div>
0903 |                             
0904 |                             <div class="vuln-code">
0905 |                                 <h4>💻 Code Context</h4>
0906 |                                 <pre class="code-block">  1 |    
0907 |   2 |          IF sy-subrc EQ 0.
0908 |   3 |    *       Si la compresion ha ido bien, se borra el fichero original
0909 |   4 | &gt;&gt;         DELETE DATASET ld_path.
0910 |   5 |          ENDIF.
0911 |   6 |        ENDIF.
0912 |   7 |      ENDIF.</pre>
0913 |                             </div>
0914 |                             
0915 |                             <div class="vuln-remediation">
0916 |                                 <h4>💡 Remediation Advice</h4>
0917 |                                 <div class="advice-content">
0918 |     Prevent directory traversal:
0919 |     - Validate file paths using FILE_VALIDATE_NAME
0920 |     - Use absolute paths with proper validation
0921 |     - Implement allowlist for accessible directories
0922 |     - Check sy-subrc after FILE_VALIDATE_NAME call
0923 |     
0924 |     Example:
0925 |     CALL FUNCTION &#39;FILE_VALIDATE_NAME&#39;
0926 |       EXPORTING logical_filename = file_path
0927 |       EXCEPTIONS OTHERS = 1.
0928 |     IF sy-subrc = 0.
0929 |       &#34; Safe to use file_path
0930 |     ENDIF.
0931 |     </div>
0932 |                             </div>
0933 |                         </div>
0934 |                     </div>
0935 |                 </div>
0936 |             </section>
0937 | 
0938 |             <!-- Remediation Plans -->
0939 |             <section class="section">
0940 |                 <h2 class="section-title">🛠️ Remediation Plans</h2>
0941 |                 
0942 |                 <div class="remediation-summary">
0943 |                     <p>2 actionable remediation plans generated, prioritized by risk and complexity.</p>
0944 |                 </div>
0945 |                 
0946 |                 <div class="remediation-plans">
0947 |                     <div class="remediation-card">
0948 |                         <div class="plan-header">
0949 |                             <h3>🔧 Directory Traversal</h3>
0950 |                             <span class="priority-badge priority-high">
0951 |                                 HIGH
0952 |                             </span>
0953 |                         </div>
0954 |                         
0955 |                         <div class="plan-meta">
0956 |                             <span class="plan-stat">⏱️ h</span>
0957 |                             <span class="plan-stat">📊 Complexity: 5.0/10</span>
0958 |                             <span class="plan-stat">📋 4 steps</span>
0959 |                         </div>
0960 |                         
0961 |                         <div class="plan-steps">
0962 |                             <h4>Implementation Steps:</h4>
0963 |                             <ol>
0964 |                                 <li class="remediation-step">
0965 |                                     <div class="step-header">
0966 |                                         <strong>Manual Security Review</strong>
0967 |                                         <span class="step-meta">30min • medium</span>
0968 |                                     </div>
0969 |                                     <div class="step-description">Manually review Directory Traversal vulnerability in test-code\YAL0029.TXT</div>
0970 |                                 </li>
0971 |                                 <li class="remediation-step">
0972 |                                     <div class="step-header">
0973 |                                         <strong>Research Best Practices</strong>
0974 |                                         <span class="step-meta">15min • easy</span>
0975 |                                     </div>
0976 |                                     <div class="step-description">Research security best practices for Directory Traversal</div>
0977 |                                 </li>
0978 |                                 <li class="remediation-step">
0979 |                                     <div class="step-header">
0980 |                                         <strong>Implement Fix</strong>
0981 |                                         <span class="step-meta">120min • hard</span>
0982 |                                     </div>
0983 |                                     <div class="step-description">Apply appropriate security fix based on research</div>
0984 |                                 </li>
0985 |                                 <li class="remediation-step">
0986 |                                     <div class="step-header">
0987 |                                         <strong>Validate Fix</strong>
0988 |                                         <span class="step-meta">30min • medium</span>
0989 |                                     </div>
0990 |                                     <div class="step-description">Test that vulnerability has been properly addressed</div>
0991 |                                 </li>
0992 |                             </ol>
0993 |                         </div>
0994 |                         
0995 |                         <div class="risk-warning">
0996 |                             <h5>⚠️ Risk if not addressed:</h5>
0997 |                             <p>Security risk associated with Directory Traversal</p>
0998 |                         </div>
0999 |                     </div>
1000 |                     <div class="remediation-card">
1001 |                         <div class="plan-header">
1002 |                             <h3>🔧 Directory Traversal</h3>
1003 |                             <span class="priority-badge priority-high">
1004 |                                 HIGH
1005 |                             </span>
1006 |                         </div>
1007 |                         
1008 |                         <div class="plan-meta">
1009 |                             <span class="plan-stat">⏱️ h</span>
1010 |                             <span class="plan-stat">📊 Complexity: 5.0/10</span>
1011 |                             <span class="plan-stat">📋 4 steps</span>
1012 |                         </div>
1013 |                         
1014 |                         <div class="plan-steps">
1015 |                             <h4>Implementation Steps:</h4>
1016 |                             <ol>
1017 |                                 <li class="remediation-step">
1018 |                                     <div class="step-header">
1019 |                                         <strong>Manual Security Review</strong>
1020 |                                         <span class="step-meta">30min • medium</span>
1021 |                                     </div>
1022 |                                     <div class="step-description">Manually review Directory Traversal vulnerability in test-code\YAL0029.TXT</div>
1023 |                                 </li>
1024 |                                 <li class="remediation-step">
1025 |                                     <div class="step-header">
1026 |                                         <strong>Research Best Practices</strong>
1027 |                                         <span class="step-meta">15min • easy</span>
1028 |                                     </div>
1029 |                                     <div class="step-description">Research security best practices for Directory Traversal</div>
1030 |                                 </li>
1031 |                                 <li class="remediation-step">
1032 |                                     <div class="step-header">
1033 |                                         <strong>Implement Fix</strong>
1034 |                                         <span class="step-meta">120min • hard</span>
1035 |                                     </div>
1036 |                                     <div class="step-description">Apply appropriate security fix based on research</div>
1037 |                                 </li>
1038 |                                 <li class="remediation-step">
1039 |                                     <div class="step-header">
1040 |                                         <strong>Validate Fix</strong>
1041 |                                         <span class="step-meta">30min • medium</span>
1042 |                                     </div>
1043 |                                     <div class="step-description">Test that vulnerability has been properly addressed</div>
1044 |                                 </li>
1045 |                             </ol>
1046 |                         </div>
1047 |                         
1048 |                         <div class="risk-warning">
1049 |                             <h5>⚠️ Risk if not addressed:</h5>
1050 |                             <p>Security risk associated with Directory Traversal</p>
1051 |                         </div>
1052 |                     </div>
1053 |                 </div>
1054 |             </section>
1055 | 
1056 |             <!-- Technical Details -->
1057 |             <section class="section">
1058 |                 <details class="technical-details">
1059 |                     <summary class="details-toggle">🔍 Technical Analysis Details</summary>
1060 |                     <div class="details-content">
1061 |                         <div class="tech-grid">
1062 |                             <div class="tech-item">
1063 |                                 <h4>📊 Analysis Statistics</h4>
1064 |                                 <ul>
1065 |                                     <li>Processing time: 36.09s</li>
1066 |                                     <li>File size: 3.67 KB</li>
1067 |                                     <li>Language: Auto-detected</li>
1068 |                                     <li>Chunking: Disabled</li>
1069 |                                 </ul>
1070 |                             </div>
1071 |                             
1072 |                             <div class="tech-item">
1073 |                                 <h4>🤖 LLM Triage Results</h4>
1074 |                                 <ul>
1075 |                                     <li>Confirmed vulnerabilities: 2</li>
1076 |                                     <li>False positives: 0</li>
1077 |                                     <li>Need manual review: 0</li>
1078 |                                     <li>Analysis time: 2.10s</li>
1079 |                                 </ul>
1080 |                             </div>
1081 |                         </div>
1082 |                         
1083 |                         <div class="analysis-summary">
1084 |                             <h4>📋 Analysis Summary</h4>
1085 |                             <pre>Se han detectado dos vulnerabilidades de Directory Traversal con gravedad alta en el código proporcionado. Ambas vulnerabilidades podrían permitir la travesía de directorios y el acceso no autorizado a archivos y directorios, lo que representa un riesgo significativo para la seguridad del sistema.</pre>
1086 |                         </div>
1087 |                     </div>
1088 |                 </details>
1089 |             </section>
1090 |         </main>
1091 | 
1092 |         <!-- Footer -->
1093 |         <footer class="footer">
1094 |             <div class="footer-content">
1095 |                 <p>Generated by <strong>Security Analysis Platform v3.0</strong> on 2025-12-16 at 10:53:39</p>
1096 |                 <p>For questions about this report, contact your security team.</p>
1097 |             </div>
1098 |         </footer>
1099 |     </div>
1100 | 
1101 | <!-- adapters/output/templates/scripts.html -->
1102 | <script>
1103 | document.addEventListener('DOMContentLoaded', function() {
1104 |     console.log('🛡️ Security Analysis Report v3.0 loaded');
1105 |     
1106 |     // Enhanced interactivity
1107 |     initializeAnimations();
1108 |     setupCopyFunctionality();
1109 |     setupSearchFunctionality();
1110 |     setupKeyboardNavigation();
1111 |     
1112 |     // Report statistics
1113 |     logReportStatistics();
1114 | });
1115 | 
1116 | function initializeAnimations() {
1117 |     // Intersection Observer for scroll animations
1118 |     const observerOptions = {
1119 |         threshold: 0.1,
1120 |         rootMargin: '0px 0px -50px 0px'
1121 |     };
1122 | 
1123 |     const observer = new IntersectionObserver(function(entries) {
1124 |         entries.forEach(function(entry) {
1125 |             if (entry.isIntersecting) {
1126 |                 entry.target.style.opacity = '1';
1127 |                 entry.target.style.transform = 'translateY(0)';
1128 |             }
1129 |         });
1130 |     }, observerOptions);
1131 | 
1132 |     // Apply to vulnerability cards
1133 |     document.querySelectorAll('.vulnerability-card, .remediation-card').forEach(function(el) {
1134 |         el.style.opacity = '0';
1135 |         el.style.transform = 'translateY(20px)';
1136 |         el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
1137 |         observer.observe(el);
1138 |     });
1139 | }
1140 | 
1141 | function setupCopyFunctionality() {
1142 |     // Add copy buttons to vulnerability IDs and CWE links
1143 |     document.querySelectorAll('.meta-value').forEach(function(element) {
1144 |         const text = element.textContent.trim();
1145 |         
1146 |         if (text.match(/^(VULN-|ABAP-|CWE-)/)) {
1147 |             element.style.cursor = 'pointer';
1148 |             element.title = 'Click to copy ' + text;
1149 |             
1150 |             element.addEventListener('click', function() {
1151 |                 copyToClipboard(text);
1152 |                 showToast('✅ Copied: ' + text);
1153 |             });
1154 |         }
1155 |     });
1156 | }
1157 | 
1158 | function setupSearchFunctionality() {
1159 |     // Create search box
1160 |     const searchBox = document.createElement('div');
1161 |     searchBox.innerHTML = `
1162 |         <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
1163 |             <input type="text" id="vulnerabilitySearch" placeholder="🔍 Search vulnerabilities..." 
1164 |                    style="border: 1px solid #ddd; padding: 8px; border-radius: 4px; width: 250px;">
1165 |         </div>
1166 |     `;
1167 |     document.body.appendChild(searchBox);
1168 |     
1169 |     const searchInput = document.getElementById('vulnerabilitySearch');
1170 |     searchInput.addEventListener('input', function(e) {
1171 |         const query = e.target.value.toLowerCase();
1172 |         filterVulnerabilities(query);
1173 |     });
1174 | }
1175 | 
1176 | function setupKeyboardNavigation() {
1177 |     document.addEventListener('keydown', function(e) {
1178 |         // Ctrl+F or Cmd+F to focus search
1179 |         if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
1180 |             e.preventDefault();
1181 |             const searchInput = document.getElementById('vulnerabilitySearch');
1182 |             if (searchInput) {
1183 |                 searchInput.focus();
1184 |             }
1185 |         }
1186 |         
1187 |         // Escape to clear search
1188 |         if (e.key === 'Escape') {
1189 |             const searchInput = document.getElementById('vulnerabilitySearch');
1190 |             if (searchInput && searchInput === document.activeElement) {
1191 |                 searchInput.value = '';
1192 |                 filterVulnerabilities('');
1193 |                 searchInput.blur();
1194 |             }
1195 |         }
1196 |     });
1197 | }
1198 | 
1199 | function filterVulnerabilities(query) {
1200 |     const cards = document.querySelectorAll('.vulnerability-card');
1201 |     let visibleCount = 0;
1202 |     
1203 |     cards.forEach(function(card) {
1204 |         const text = card.textContent.toLowerCase();
1205 |         const isVisible = query === '' || text.includes(query);
1206 |         
1207 |         card.style.display = isVisible ? 'block' : 'none';
1208 |         if (isVisible) visibleCount++;
1209 |     });
1210 |     
1211 |     // Update search results indicator
1212 |     updateSearchResults(visibleCount, cards.length, query);
1213 | }
1214 | 
1215 | function updateSearchResults(visible, total, query) {
1216 |     let indicator = document.getElementById('searchResults');
1217 |     
1218 |     if (!indicator) {
1219 |         indicator = document.createElement('div');
1220 |         indicator.id = 'searchResults';
1221 |         indicator.style.cssText = `
1222 |             position: fixed;
1223 |             bottom: 20px;
1224 |             right: 20px;
1225 |             background: #4f46e5;
1226 |             color: white;
1227 |             padding: 8px 12px;
1228 |             border-radius: 6px;
1229 |             font-size: 0.875rem;
1230 |             z-index: 1000;
1231 |             transition: opacity 0.3s;
1232 |         `;
1233 |         document.body.appendChild(indicator);
1234 |     }
1235 |     
1236 |     if (query) {
1237 |         indicator.textContent = `Found ${visible} of ${total} vulnerabilities`;
1238 |         indicator.style.opacity = '1';
1239 |     } else {
1240 |         indicator.style.opacity = '0';
1241 |     }
1242 | }
1243 | 
1244 | function copyToClipboard(text) {
1245 |     if (navigator.clipboard) {
1246 |         navigator.clipboard.writeText(text).catch(function() {
1247 |             fallbackCopy(text);
1248 |         });
1249 |     } else {
1250 |         fallbackCopy(text);
1251 |     }
1252 | }
1253 | 
1254 | function fallbackCopy(text) {
1255 |     const textArea = document.createElement('textarea');
1256 |     textArea.value = text;
1257 |     textArea.style.position = 'fixed';
1258 |     textArea.style.left = '-9999px';
1259 |     document.body.appendChild(textArea);
1260 |     textArea.focus();
1261 |     textArea.select();
1262 |     
1263 |     try {
1264 |         document.execCommand('copy');
1265 |     } catch (err) {
1266 |         console.warn('Copy failed:', err);
1267 |     }
1268 |     
1269 |     document.body.removeChild(textArea);
1270 | }
1271 | 
1272 | function showToast(message) {
1273 |     const toast = document.createElement('div');
1274 |     toast.textContent = message;
1275 |     toast.style.cssText = `
1276 |         position: fixed;
1277 |         top: 20px;
1278 |         left: 50%;
1279 |         transform: translateX(-50%);
1280 |         background: #10b981;
1281 |         color: white;
1282 |         padding: 12px 20px;
1283 |         border-radius: 8px;
1284 |         z-index: 9999;
1285 |         animation: slideInDown 0.3s ease-out;
1286 |         font-weight: 500;
1287 |     `;
1288 |     
1289 |     document.body.appendChild(toast);
1290 |     
1291 |     setTimeout(function() {
1292 |         toast.style.animation = 'slideOutUp 0.3s ease-out';
1293 |         setTimeout(function() {
1294 |             document.body.removeChild(toast);
1295 |         }, 300);
1296 |     }, 2000);
1297 | }
1298 | 
1299 | function logReportStatistics() {
1300 |     const stats = {
1301 |         totalVulnerabilities: 2,
1302 |         highPriority: 2,
1303 |         riskScore: 7.0,
1304 |         processingTime: '36.09s',
1305 |         chunking: false,
1306 |         llmAnalysis: true,
1307 |         reportVersion: '3.0'
1308 |     };
1309 |     
1310 |     console.log('📊 Report Statistics:', stats);
1311 |     
1312 |     // Performance metrics
1313 |     console.log('⚡ Performance Metrics:');
1314 |     console.log('  • DOM Ready:', performance.now().toFixed(2) + 'ms');
1315 |     console.log('  • Interactive elements:', document.querySelectorAll('[onclick], [data-action]').length);
1316 |     console.log('  • Vulnerability cards:', document.querySelectorAll('.vulnerability-card').length);
1317 | }
1318 | 
1319 | // CSS animations for toasts
1320 | const additionalStyles = `
1321 | @keyframes slideInDown {
1322 |     from {
1323 |         opacity: 0;
1324 |         transform: translate(-50%, -100%);
1325 |     }
1326 |     to {
1327 |         opacity: 1;
1328 |         transform: translate(-50%, 0);
1329 |     }
1330 | }
1331 | 
1332 | @keyframes slideOutUp {
1333 |     from {
1334 |         opacity: 1;
1335 |         transform: translate(-50%, 0);
1336 |     }
1337 |     to {
1338 |         opacity: 0;
1339 |         transform: translate(-50%, -100%);
1340 |     }
1341 | }
1342 | `;
1343 | 
1344 | const styleSheet = document.createElement('style');
1345 | styleSheet.textContent = additionalStyles;
1346 | document.head.appendChild(styleSheet);
1347 | </script></body>
1348 | </html>```

---

### setup.py

**Ruta:** `setup.py`

```py
0001 | # setup.py
0002 | from setuptools import setup, find_packages
0003 | from pathlib import Path
0004 | 
0005 | readme_path = Path(__file__).parent / "README.md"
0006 | long_description = ""
0007 | if readme_path.exists():
0008 |     try:
0009 |         long_description = readme_path.read_text(encoding="utf-8")
0010 |     except Exception:
0011 |         long_description = "LLM-Powered Vulnerability Triage"
0012 | 
0013 | setup(
0014 |     name="llm-triage",
0015 |     version="3.0.0",
0016 |     description="LLM-Powered Vulnerability Triage with CVSS Filtering and Deduplication",
0017 |     long_description=long_description,
0018 |     long_description_content_type="text/markdown",
0019 |     author="Security Team",
0020 |     author_email="security@research.com",
0021 |     url="https://github.com/your-org/llm-vuln-triage",
0022 |     packages=find_packages(),
0023 |     include_package_data=True,
0024 |     install_requires=[
0025 |         "pydantic>=2.0.0",
0026 |         "click>=8.0.0",
0027 |         "jinja2>=3.0.0",
0028 |         "requests>=2.31.0",
0029 |     ],
0030 |     extras_require={
0031 |         "dev": [
0032 |             "pytest>=7.0.0",
0033 |             "pytest-asyncio>=0.21.0",
0034 |             "black>=23.0.0",
0035 |         ],
0036 |         "openai": ["openai>=1.0.0"],
0037 |     },
0038 |     entry_points={
0039 |         "console_scripts": [
0040 |             "llm-triage=application.cli:cli",
0041 |             "vuln-triage=application.cli:cli",
0042 |         ],
0043 |     },
0044 |     python_requires=">=3.8",
0045 |     package_data={
0046 |         "adapters.output": ["templates/*.html"],
0047 |     },
0048 | )
```

---

### adapters\__init__.py

**Ruta:** `adapters\__init__.py`

```py
```

---

### adapters\output\html_generator.py

**Ruta:** `adapters\output\html_generator.py`

```py
0001 | # adapters/output/html_generator.py
0002 | import logging
0003 | from pathlib import Path
0004 | from datetime import datetime
0005 | from typing import Dict, Any, Optional
0006 | from jinja2 import Environment, FileSystemLoader, select_autoescape
0007 | 
0008 | from core.models import AnalysisReport, Vulnerability
0009 | from shared.metrics import MetricsCollector
0010 | 
0011 | logger = logging.getLogger(__name__)
0012 | 
0013 | class OptimizedHTMLGenerator:
0014 |     """Generador HTML optimizado y simplificado"""
0015 |     
0016 |     def __init__(self, template_dir: Optional[Path] = None, metrics: Optional[MetricsCollector] = None):
0017 |         self.template_dir = template_dir or Path(__file__).parent / "templates"
0018 |         self.metrics = metrics
0019 |         
0020 |         # Configure Jinja2 environment
0021 |         self.env = Environment(
0022 |             loader=FileSystemLoader(str(self.template_dir)),
0023 |             autoescape=select_autoescape(['html', 'xml']),
0024 |             trim_blocks=True,
0025 |             lstrip_blocks=True
0026 |         )
0027 |         
0028 |         # Register optimized filters
0029 |         self._register_filters()
0030 |         
0031 |         logger.info(f"HTML Generator initialized")
0032 |     
0033 |     def generate_report(self, analysis_report: AnalysisReport, output_file: str) -> bool:
0034 |         """Generate optimized HTML report"""
0035 |         
0036 |         try:
0037 |             logger.info(f"Generating HTML report: {output_file}")
0038 |             
0039 |             # Prepare template context
0040 |             context = self._prepare_context(analysis_report)
0041 |             
0042 |             # Render main template
0043 |             template = self.env.get_template('report.html')
0044 |             html_content = template.render(**context)
0045 |             
0046 |             # Write file
0047 |             output_path = Path(output_file)
0048 |             output_path.parent.mkdir(parents=True, exist_ok=True)
0049 |             
0050 |             with open(output_path, 'w', encoding='utf-8') as f:
0051 |                 f.write(html_content)
0052 |             
0053 |             # Record metrics
0054 |             file_size = output_path.stat().st_size
0055 |             if self.metrics:
0056 |                 self.metrics.record_report_generation(
0057 |                     "html", file_size, len(analysis_report.scan_result.vulnerabilities), True
0058 |                 )
0059 |             
0060 |             logger.info(f"HTML report generated: {output_file} ({file_size:,} bytes)")
0061 |             return True
0062 |             
0063 |         except Exception as e:
0064 |             logger.error(f"HTML generation failed: {e}")
0065 |             if self.metrics:
0066 |                 self.metrics.record_report_generation("html", success=False, error=str(e))
0067 |             
0068 |             # Try fallback generation
0069 |             return self._generate_fallback_report(analysis_report, output_file)
0070 |     
0071 |     def _prepare_context(self, analysis_report: AnalysisReport) -> Dict[str, Any]:
0072 |         """Prepare optimized template context"""
0073 |         
0074 |         scan_result = analysis_report.scan_result
0075 |         vulnerabilities = scan_result.vulnerabilities
0076 |         
0077 |         # Calculate derived metrics
0078 |         severity_stats = self._calculate_severity_stats(vulnerabilities)
0079 |         risk_score = self._calculate_risk_score(vulnerabilities)
0080 |         
0081 |         return {
0082 |             # Main data
0083 |             'report': analysis_report,
0084 |             'scan_result': scan_result,
0085 |             'triage_result': analysis_report.triage_result,
0086 |             'remediation_plans': analysis_report.remediation_plans,
0087 |             
0088 |             # Calculated metrics
0089 |             'total_vulnerabilities': len(vulnerabilities),
0090 |             'high_priority_count': len([v for v in vulnerabilities if v.is_high_priority]),
0091 |             'severity_stats': severity_stats,
0092 |             'risk_score': risk_score,
0093 |             
0094 |             # Report metadata
0095 |             'generation_timestamp': datetime.now(),
0096 |             'report_version': '3.0',
0097 |             'platform_name': 'Security Analysis Platform v3.0',
0098 |             
0099 |             # Configuration
0100 |             'show_code_snippets': True,
0101 |             'enable_interactive_features': True
0102 |         }
0103 |     
0104 |     def _calculate_severity_stats(self, vulnerabilities: list[Vulnerability]) -> Dict[str, int]:
0105 |         """Calculate severity distribution"""
0106 |         from collections import Counter
0107 |         return dict(Counter(v.severity.value for v in vulnerabilities))
0108 |     
0109 |     def _calculate_risk_score(self, vulnerabilities: list[Vulnerability]) -> float:
0110 |         """Calculate overall risk score (0-10)"""
0111 |         if not vulnerabilities:
0112 |             return 0.0
0113 |         
0114 |         severity_weights = {
0115 |             'CRÍTICA': 10.0, 'ALTA': 7.0, 'MEDIA': 4.0, 'BAJA': 2.0, 'INFO': 0.5
0116 |         }
0117 |         
0118 |         total_score = sum(severity_weights.get(v.severity.value, 0) for v in vulnerabilities)
0119 |         max_possible = len(vulnerabilities) * 10.0
0120 |         
0121 |         normalized = (total_score / max_possible) * 10.0 if max_possible > 0 else 0.0
0122 |         return round(min(normalized, 10.0), 1)
0123 |     
0124 |     def _generate_fallback_report(self, analysis_report: AnalysisReport, output_file: str) -> bool:
0125 |         """Generate minimal fallback report"""
0126 |         
0127 |         try:
0128 |             logger.warning("Generating minimal fallback report")
0129 |             
0130 |             scan_result = analysis_report.scan_result
0131 |             vuln_count = len(scan_result.vulnerabilities)
0132 |             
0133 |             fallback_html = f"""<!DOCTYPE html>
0134 | <html lang="es">
0135 | <head>
0136 |     <meta charset="UTF-8">
0137 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0138 |     <title>🛡️ Security Analysis Report</title>
0139 |     <style>
0140 |         body {{ font-family: system-ui, sans-serif; margin: 20px; line-height: 1.6; }}
0141 |         .header {{ background: #4f46e5; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
0142 |         .summary {{ background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #4f46e5; }}
0143 |         .vuln {{ background: #fef2f2; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ef4444; }}
0144 |         .no-vulns {{ background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #22c55e; text-align: center; }}
0145 |     </style>
0146 | </head>
0147 | <body>
0148 |     <div class="header">
0149 |         <h1>🛡️ Security Analysis Report</h1>
0150 |         <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
0151 |     </div>
0152 |     
0153 |     <div class="summary">
0154 |         <h2>📊 Summary</h2>
0155 |         <p><strong>File:</strong> {scan_result.file_info.get('filename', 'Unknown')}</p>
0156 |         <p><strong>Total Vulnerabilities:</strong> {vuln_count}</p>
0157 |         <p><strong>Analysis Time:</strong> {analysis_report.total_processing_time_seconds:.2f}s</p>
0158 |     </div>
0159 | """
0160 |             
0161 |             if vuln_count > 0:
0162 |                 fallback_html += '<div class="summary"><h2>🚨 Vulnerabilities Found</h2>'
0163 |                 
0164 |                 # Mostrar primeras 10 vulnerabilidades
0165 |                 for i, vuln in enumerate(scan_result.vulnerabilities[:10], 1):
0166 |                     fallback_html += f'''
0167 |     <div class="vuln">
0168 |         <h3>{i}. {vuln.title}</h3>
0169 |         <p><strong>Severity:</strong> {vuln.severity.value}</p>
0170 |         <p><strong>File:</strong> {vuln.file_path}:{vuln.line_number}</p>
0171 |         <p><strong>Description:</strong> {vuln.description[:200]}...</p>
0172 |     </div>'''
0173 |                 
0174 |                 if vuln_count > 10:
0175 |                     fallback_html += f'<p><em>... and {vuln_count - 10} more vulnerabilities</em></p>'
0176 |                 
0177 |                 fallback_html += '</div>'
0178 |             else:
0179 |                 fallback_html += '''
0180 |     <div class="no-vulns">
0181 |         <h2>✅ No Vulnerabilities Found</h2>
0182 |         <p>Great! No security vulnerabilities were detected.</p>
0183 |     </div>'''
0184 |             
0185 |             fallback_html += '''
0186 |     <div class="summary">
0187 |         <h2>ℹ️ Simplified Report</h2>
0188 |         <p>This is a simplified report due to template rendering issues.</p>
0189 |         <p>Generated by Security Analysis Platform v3.0 - Fallback Mode</p>
0190 |     </div>
0191 | </body>
0192 | </html>'''
0193 |             
0194 |             with open(output_file, 'w', encoding='utf-8') as f:
0195 |                 f.write(fallback_html)
0196 |             
0197 |             logger.info(f"Fallback report generated: {output_file}")
0198 |             return True
0199 |             
0200 |         except Exception as e:
0201 |             logger.error(f"Even fallback generation failed: {e}")
0202 |             return False
0203 |     
0204 |     def _register_filters(self):
0205 |         """Register optimized Jinja2 filters - CORREGIDO"""
0206 |         
0207 |         def format_bytes(value):
0208 |             """Format bytes in human readable format"""
0209 |             if not value:
0210 |                 return "0 bytes"
0211 |             try:
0212 |                 value = int(value)
0213 |                 if value >= 1024 * 1024:
0214 |                     return f"{value / (1024 * 1024):.2f} MB"
0215 |                 elif value >= 1024:
0216 |                     return f"{value / 1024:.2f} KB"
0217 |                 return f"{value} bytes"
0218 |             except (ValueError, TypeError):
0219 |                 return str(value)
0220 |         
0221 |         def format_duration(seconds):
0222 |             """Format duration in human readable format"""
0223 |             if not seconds:
0224 |                 return "0s"
0225 |             try:
0226 |                 seconds = float(seconds)
0227 |                 if seconds >= 60:
0228 |                     minutes = int(seconds // 60)
0229 |                     remaining = seconds % 60
0230 |                     return f"{minutes}m {remaining:.1f}s"
0231 |                 return f"{seconds:.2f}s"
0232 |             except (ValueError, TypeError):
0233 |                 return str(seconds)
0234 |         
0235 |         def severity_icon(severity):
0236 |             """Get icon for severity level"""
0237 |             if not severity:
0238 |                 return '📄'
0239 |             icons = {
0240 |                 'CRÍTICA': '🔥', 'ALTA': '⚡', 'MEDIA': '⚠️', 
0241 |                 'BAJA': '📝', 'INFO': 'ℹ️'
0242 |             }
0243 |             return icons.get(str(severity).upper(), '📄')
0244 |         
0245 |         def severity_class(severity):
0246 |             """Get CSS class for severity"""
0247 |             if not severity:
0248 |                 return 'default'
0249 |             classes = {
0250 |                 'CRÍTICA': 'critical', 'ALTA': 'high', 'MEDIA': 'medium',
0251 |                 'BAJA': 'low', 'INFO': 'info'
0252 |             }
0253 |             return classes.get(str(severity).upper(), 'default')
0254 |         
0255 |         def truncate_smart(text, length=300):
0256 |             """Smart truncation preserving word boundaries"""
0257 |             if not text:
0258 |                 return ""
0259 |             text = str(text)
0260 |             if len(text) <= length:
0261 |                 return text
0262 |             return text[:length].rsplit(' ', 1)[0] + "..."
0263 |         
0264 |         # CORREGIR: Usar self.env.filters en lugar de @self.env.filter
0265 |         self.env.filters['format_bytes'] = format_bytes
0266 |         self.env.filters['format_duration'] = format_duration
0267 |         self.env.filters['severity_icon'] = severity_icon
0268 |         self.env.filters['severity_class'] = severity_class
0269 |         self.env.filters['truncate_smart'] = truncate_smart
0270 | 
0271 |                 ```

---

### adapters\output\__init__.py

**Ruta:** `adapters\output\__init__.py`

```py
```

---

### adapters\output\templates\report.html

**Ruta:** `adapters\output\templates\report.html`

```html
0001 |  <!-- adapters/output/templates/report.html -->
0002 | <!DOCTYPE html>
0003 | <html lang="es">
0004 | <head>
0005 |     <meta charset="UTF-8">
0006 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0007 |     <title>🛡️ {{ platform_name }} - Report</title>
0008 |     {% include 'styles.html' %}
0009 | </head>
0010 | <body>
0011 |     <div class="container">
0012 |         <!-- Header -->
0013 |         <header class="header">
0014 |             <div class="header-content">
0015 |                 <h1>🛡️ Security Analysis Report</h1>
0016 |                 <div class="header-grid">
0017 |                     <div class="header-item">
0018 |                         <div class="header-label">📁 File</div>
0019 |                         <div class="header-value">{{ scan_result.file_info.filename }}</div>
0020 |                     </div>
0021 |                     <div class="header-item">
0022 |                         <div class="header-label">📊 Total Vulnerabilities</div>
0023 |                         <div class="header-value">{{ total_vulnerabilities }}</div>
0024 |                     </div>
0025 |                     <div class="header-item">
0026 |                         <div class="header-label">⚡ High Priority</div>
0027 |                         <div class="header-value">{{ high_priority_count }}</div>
0028 |                     </div>
0029 |                     <div class="header-item">
0030 |                         <div class="header-label">🎯 Risk Score</div>
0031 |                         <div class="header-value">{{ risk_score }}/10</div>
0032 |                     </div>
0033 |                 </div>
0034 |             </div>
0035 |         </header>
0036 | 
0037 |         <main class="content">
0038 |             <!-- Executive Summary -->
0039 |             <section class="section">
0040 |                 <h2 class="section-title">📈 Executive Summary</h2>
0041 |                 
0042 |                 <div class="metrics-grid">
0043 |                     {% for severity, count in severity_stats.items() %}
0044 |                     {% if count > 0 %}
0045 |                     <div class="metric-card {{ severity | severity_class }}">
0046 |                         <div class="metric-icon">{{ severity | severity_icon }}</div>
0047 |                         <div class="metric-value">{{ count }}</div>
0048 |                         <div class="metric-label">{{ severity }}</div>
0049 |                     </div>
0050 |                     {% endif %}
0051 |                     {% endfor %}
0052 |                 </div>
0053 | 
0054 |                 <div class="summary-info">
0055 |                     <p><strong>Analysis completed in {{ report.total_processing_time_seconds | format_duration }}</strong></p>
0056 |                     {% if report.chunking_enabled %}
0057 |                     <p>🧩 Advanced chunking was used for optimal analysis</p>
0058 |                     {% endif %}
0059 |                     {% if triage_result %}
0060 |                     <p>🤖 AI-powered triage analyzed {{ triage_result.total_analyzed }} vulnerabilities</p>
0061 |                     {% endif %}
0062 |                 </div>
0063 |             </section>
0064 | 
0065 |             <!-- Vulnerabilities -->
0066 |             {% if scan_result.vulnerabilities %}
0067 |             <section class="section">
0068 |                 <h2 class="section-title">🚨 Security Vulnerabilities</h2>
0069 |                 
0070 |                 <div class="vulnerabilities-list">
0071 |                     {% for vuln in scan_result.vulnerabilities %}
0072 |                     <div class="vulnerability-card {{ vuln.severity.value | severity_class }}">
0073 |                         <div class="vuln-header">
0074 |                             <h3 class="vuln-title">
0075 |                                 {{ vuln.severity | severity_icon }} {{ loop.index }}. {{ vuln.title }}
0076 |                             </h3>
0077 |                             <div class="vuln-badges">
0078 |                                 <span class="badge severity-{{ vuln.severity.value | severity_class }}">
0079 |                                     {{ vuln.severity.value }}
0080 |                                 </span>
0081 |                                 <span class="badge type-badge">{{ vuln.type.value }}</span>
0082 |                             </div>
0083 |                         </div>
0084 |                         
0085 |                         <div class="vuln-body">
0086 |                             <div class="vuln-meta">
0087 |                                 <div class="meta-item">
0088 |                                     <span class="meta-label">📍 Location</span>
0089 |                                     <span class="meta-value">{{ vuln.file_path }}:{{ vuln.line_number }}</span>
0090 |                                 </div>
0091 |                                 <div class="meta-item">
0092 |                                     <span class="meta-label">🆔 ID</span>
0093 |                                     <span class="meta-value">{{ vuln.id }}</span>
0094 |                                 </div>
0095 |                                 {% if vuln.cwe_id %}
0096 |                                 <div class="meta-item">
0097 |                                     <span class="meta-label">🔗 CWE</span>
0098 |                                     <span class="meta-value">
0099 |                                         <a href="https://cwe.mitre.org/data/definitions/{{ vuln.cwe_id.replace('CWE-', '') }}.html" target="_blank">
0100 |                                             {{ vuln.cwe_id }}
0101 |                                         </a>
0102 |                                     </span>
0103 |                                 </div>
0104 |                                 {% endif %}
0105 |                             </div>
0106 |                             
0107 |                             <div class="vuln-description">
0108 |                                 <h4>📝 Description</h4>
0109 |                                 <p>{{ vuln.description }}</p>
0110 |                             </div>
0111 |                             
0112 |                             {% if vuln.code_snippet %}
0113 |                             <div class="vuln-code">
0114 |                                 <h4>💻 Code Context</h4>
0115 |                                 <pre class="code-block">{{ vuln.code_snippet | truncate_smart(500) }}</pre>
0116 |                             </div>
0117 |                             {% endif %}
0118 |                             
0119 |                             {% if vuln.remediation_advice %}
0120 |                             <div class="vuln-remediation">
0121 |                                 <h4>💡 Remediation Advice</h4>
0122 |                                 <div class="advice-content">{{ vuln.remediation_advice }}</div>
0123 |                             </div>
0124 |                             {% endif %}
0125 |                         </div>
0126 |                     </div>
0127 |                     {% endfor %}
0128 |                 </div>
0129 |             </section>
0130 |             {% else %}
0131 |             <section class="section">
0132 |                 <div class="no-vulnerabilities">
0133 |                     <div class="no-vulns-icon">✅</div>
0134 |                     <h2>No Vulnerabilities Found</h2>
0135 |                     <p>Excellent! No security vulnerabilities were detected in the analyzed code.</p>
0136 |                 </div>
0137 |             </section>
0138 |             {% endif %}
0139 | 
0140 |             <!-- Remediation Plans -->
0141 |             {% if remediation_plans %}
0142 |             <section class="section">
0143 |                 <h2 class="section-title">🛠️ Remediation Plans</h2>
0144 |                 
0145 |                 <div class="remediation-summary">
0146 |                     <p>{{ remediation_plans | length }} actionable remediation plans generated, prioritized by risk and complexity.</p>
0147 |                 </div>
0148 |                 
0149 |                 <div class="remediation-plans">
0150 |                     {% for plan in remediation_plans %}
0151 |                     <div class="remediation-card">
0152 |                         <div class="plan-header">
0153 |                             <h3>🔧 {{ plan.vulnerability_type.value }}</h3>
0154 |                             <span class="priority-badge priority-{{ plan.priority_level }}">
0155 |                                 {{ plan.priority_level.upper() }}
0156 |                             </span>
0157 |                         </div>
0158 |                         
0159 |                         <div class="plan-meta">
0160 |                             <span class="plan-stat">⏱️ {{ plan.total_estimated_hours }}h</span>
0161 |                             <span class="plan-stat">📊 Complexity: {{ plan.complexity_score }}/10</span>
0162 |                             <span class="plan-stat">📋 {{ plan.steps | length }} steps</span>
0163 |                         </div>
0164 |                         
0165 |                         <div class="plan-steps">
0166 |                             <h4>Implementation Steps:</h4>
0167 |                             <ol>
0168 |                                 {% for step in plan.steps %}
0169 |                                 <li class="remediation-step">
0170 |                                     <div class="step-header">
0171 |                                         <strong>{{ step.title }}</strong>
0172 |                                         <span class="step-meta">{{ step.estimated_minutes }}min • {{ step.difficulty }}</span>
0173 |                                     </div>
0174 |                                     <div class="step-description">{{ step.description }}</div>
0175 |                                     {% if step.code_example %}
0176 |                                     <pre class="step-code">{{ step.code_example | truncate_smart(200) }}</pre>
0177 |                                     {% endif %}
0178 |                                 </li>
0179 |                                 {% endfor %}
0180 |                             </ol>
0181 |                         </div>
0182 |                         
0183 |                         {% if plan.risk_if_not_fixed %}
0184 |                         <div class="risk-warning">
0185 |                             <h5>⚠️ Risk if not addressed:</h5>
0186 |                             <p>{{ plan.risk_if_not_fixed }}</p>
0187 |                         </div>
0188 |                         {% endif %}
0189 |                     </div>
0190 |                     {% endfor %}
0191 |                 </div>
0192 |             </section>
0193 |             {% endif %}
0194 | 
0195 |             <!-- Technical Details -->
0196 |             <section class="section">
0197 |                 <details class="technical-details">
0198 |                     <summary class="details-toggle">🔍 Technical Analysis Details</summary>
0199 |                     <div class="details-content">
0200 |                         <div class="tech-grid">
0201 |                             <div class="tech-item">
0202 |                                 <h4>📊 Analysis Statistics</h4>
0203 |                                 <ul>
0204 |                                     <li>Processing time: {{ report.total_processing_time_seconds | format_duration }}</li>
0205 |                                     <li>File size: {{ scan_result.file_info.size_bytes | format_bytes }}</li>
0206 |                                     <li>Language: {{ scan_result.language_detected or 'Auto-detected' }}</li>
0207 |                                     <li>Chunking: {{ 'Enabled' if report.chunking_enabled else 'Disabled' }}</li>
0208 |                                 </ul>
0209 |                             </div>
0210 |                             
0211 |                             {% if triage_result %}
0212 |                             <div class="tech-item">
0213 |                                 <h4>🤖 LLM Triage Results</h4>
0214 |                                 <ul>
0215 |                                     <li>Confirmed vulnerabilities: {{ triage_result.confirmed_count }}</li>
0216 |                                     <li>False positives: {{ triage_result.false_positive_count }}</li>
0217 |                                     <li>Need manual review: {{ triage_result.needs_review_count }}</li>
0218 |                                     <li>Analysis time: {{ triage_result.llm_analysis_time_seconds | format_duration }}</li>
0219 |                                 </ul>
0220 |                             </div>
0221 |                             {% endif %}
0222 |                         </div>
0223 |                         
0224 |                         {% if triage_result and triage_result.analysis_summary %}
0225 |                         <div class="analysis-summary">
0226 |                             <h4>📋 Analysis Summary</h4>
0227 |                             <pre>{{ triage_result.analysis_summary }}</pre>
0228 |                         </div>
0229 |                         {% endif %}
0230 |                     </div>
0231 |                 </details>
0232 |             </section>
0233 |         </main>
0234 | 
0235 |         <!-- Footer -->
0236 |         <footer class="footer">
0237 |             <div class="footer-content">
0238 |                 <p>Generated by <strong>{{ platform_name }}</strong> on {{ generation_timestamp.strftime('%Y-%m-%d at %H:%M:%S') }}</p>
0239 |                 <p>For questions about this report, contact your security team.</p>
0240 |             </div>
0241 |         </footer>
0242 |     </div>
0243 | 
0244 |     {% include 'scripts.html' %}
0245 | </body>
0246 | </html>
```

---

### adapters\output\templates\scripts.html

**Ruta:** `adapters\output\templates\scripts.html`

```html
0001 | <!-- adapters/output/templates/scripts.html -->
0002 | <script>
0003 | document.addEventListener('DOMContentLoaded', function() {
0004 |     console.log('🛡️ Security Analysis Report v3.0 loaded');
0005 |     
0006 |     // Enhanced interactivity
0007 |     initializeAnimations();
0008 |     setupCopyFunctionality();
0009 |     setupSearchFunctionality();
0010 |     setupKeyboardNavigation();
0011 |     
0012 |     // Report statistics
0013 |     logReportStatistics();
0014 | });
0015 | 
0016 | function initializeAnimations() {
0017 |     // Intersection Observer for scroll animations
0018 |     const observerOptions = {
0019 |         threshold: 0.1,
0020 |         rootMargin: '0px 0px -50px 0px'
0021 |     };
0022 | 
0023 |     const observer = new IntersectionObserver(function(entries) {
0024 |         entries.forEach(function(entry) {
0025 |             if (entry.isIntersecting) {
0026 |                 entry.target.style.opacity = '1';
0027 |                 entry.target.style.transform = 'translateY(0)';
0028 |             }
0029 |         });
0030 |     }, observerOptions);
0031 | 
0032 |     // Apply to vulnerability cards
0033 |     document.querySelectorAll('.vulnerability-card, .remediation-card').forEach(function(el) {
0034 |         el.style.opacity = '0';
0035 |         el.style.transform = 'translateY(20px)';
0036 |         el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
0037 |         observer.observe(el);
0038 |     });
0039 | }
0040 | 
0041 | function setupCopyFunctionality() {
0042 |     // Add copy buttons to vulnerability IDs and CWE links
0043 |     document.querySelectorAll('.meta-value').forEach(function(element) {
0044 |         const text = element.textContent.trim();
0045 |         
0046 |         if (text.match(/^(VULN-|ABAP-|CWE-)/)) {
0047 |             element.style.cursor = 'pointer';
0048 |             element.title = 'Click to copy ' + text;
0049 |             
0050 |             element.addEventListener('click', function() {
0051 |                 copyToClipboard(text);
0052 |                 showToast('✅ Copied: ' + text);
0053 |             });
0054 |         }
0055 |     });
0056 | }
0057 | 
0058 | function setupSearchFunctionality() {
0059 |     // Create search box
0060 |     const searchBox = document.createElement('div');
0061 |     searchBox.innerHTML = `
0062 |         <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
0063 |             <input type="text" id="vulnerabilitySearch" placeholder="🔍 Search vulnerabilities..." 
0064 |                    style="border: 1px solid #ddd; padding: 8px; border-radius: 4px; width: 250px;">
0065 |         </div>
0066 |     `;
0067 |     document.body.appendChild(searchBox);
0068 |     
0069 |     const searchInput = document.getElementById('vulnerabilitySearch');
0070 |     searchInput.addEventListener('input', function(e) {
0071 |         const query = e.target.value.toLowerCase();
0072 |         filterVulnerabilities(query);
0073 |     });
0074 | }
0075 | 
0076 | function setupKeyboardNavigation() {
0077 |     document.addEventListener('keydown', function(e) {
0078 |         // Ctrl+F or Cmd+F to focus search
0079 |         if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
0080 |             e.preventDefault();
0081 |             const searchInput = document.getElementById('vulnerabilitySearch');
0082 |             if (searchInput) {
0083 |                 searchInput.focus();
0084 |             }
0085 |         }
0086 |         
0087 |         // Escape to clear search
0088 |         if (e.key === 'Escape') {
0089 |             const searchInput = document.getElementById('vulnerabilitySearch');
0090 |             if (searchInput && searchInput === document.activeElement) {
0091 |                 searchInput.value = '';
0092 |                 filterVulnerabilities('');
0093 |                 searchInput.blur();
0094 |             }
0095 |         }
0096 |     });
0097 | }
0098 | 
0099 | function filterVulnerabilities(query) {
0100 |     const cards = document.querySelectorAll('.vulnerability-card');
0101 |     let visibleCount = 0;
0102 |     
0103 |     cards.forEach(function(card) {
0104 |         const text = card.textContent.toLowerCase();
0105 |         const isVisible = query === '' || text.includes(query);
0106 |         
0107 |         card.style.display = isVisible ? 'block' : 'none';
0108 |         if (isVisible) visibleCount++;
0109 |     });
0110 |     
0111 |     // Update search results indicator
0112 |     updateSearchResults(visibleCount, cards.length, query);
0113 | }
0114 | 
0115 | function updateSearchResults(visible, total, query) {
0116 |     let indicator = document.getElementById('searchResults');
0117 |     
0118 |     if (!indicator) {
0119 |         indicator = document.createElement('div');
0120 |         indicator.id = 'searchResults';
0121 |         indicator.style.cssText = `
0122 |             position: fixed;
0123 |             bottom: 20px;
0124 |             right: 20px;
0125 |             background: #4f46e5;
0126 |             color: white;
0127 |             padding: 8px 12px;
0128 |             border-radius: 6px;
0129 |             font-size: 0.875rem;
0130 |             z-index: 1000;
0131 |             transition: opacity 0.3s;
0132 |         `;
0133 |         document.body.appendChild(indicator);
0134 |     }
0135 |     
0136 |     if (query) {
0137 |         indicator.textContent = `Found ${visible} of ${total} vulnerabilities`;
0138 |         indicator.style.opacity = '1';
0139 |     } else {
0140 |         indicator.style.opacity = '0';
0141 |     }
0142 | }
0143 | 
0144 | function copyToClipboard(text) {
0145 |     if (navigator.clipboard) {
0146 |         navigator.clipboard.writeText(text).catch(function() {
0147 |             fallbackCopy(text);
0148 |         });
0149 |     } else {
0150 |         fallbackCopy(text);
0151 |     }
0152 | }
0153 | 
0154 | function fallbackCopy(text) {
0155 |     const textArea = document.createElement('textarea');
0156 |     textArea.value = text;
0157 |     textArea.style.position = 'fixed';
0158 |     textArea.style.left = '-9999px';
0159 |     document.body.appendChild(textArea);
0160 |     textArea.focus();
0161 |     textArea.select();
0162 |     
0163 |     try {
0164 |         document.execCommand('copy');
0165 |     } catch (err) {
0166 |         console.warn('Copy failed:', err);
0167 |     }
0168 |     
0169 |     document.body.removeChild(textArea);
0170 | }
0171 | 
0172 | function showToast(message) {
0173 |     const toast = document.createElement('div');
0174 |     toast.textContent = message;
0175 |     toast.style.cssText = `
0176 |         position: fixed;
0177 |         top: 20px;
0178 |         left: 50%;
0179 |         transform: translateX(-50%);
0180 |         background: #10b981;
0181 |         color: white;
0182 |         padding: 12px 20px;
0183 |         border-radius: 8px;
0184 |         z-index: 9999;
0185 |         animation: slideInDown 0.3s ease-out;
0186 |         font-weight: 500;
0187 |     `;
0188 |     
0189 |     document.body.appendChild(toast);
0190 |     
0191 |     setTimeout(function() {
0192 |         toast.style.animation = 'slideOutUp 0.3s ease-out';
0193 |         setTimeout(function() {
0194 |             document.body.removeChild(toast);
0195 |         }, 300);
0196 |     }, 2000);
0197 | }
0198 | 
0199 | function logReportStatistics() {
0200 |     const stats = {
0201 |         totalVulnerabilities: {{ total_vulnerabilities }},
0202 |         highPriority: {{ high_priority_count }},
0203 |         riskScore: {{ risk_score }},
0204 |         processingTime: '{{ report.total_processing_time_seconds | format_duration }}',
0205 |         chunking: {{ 'true' if report.chunking_enabled else 'false' }},
0206 |         llmAnalysis: {{ 'true' if triage_result else 'false' }},
0207 |         reportVersion: '{{ report_version }}'
0208 |     };
0209 |     
0210 |     console.log('📊 Report Statistics:', stats);
0211 |     
0212 |     // Performance metrics
0213 |     console.log('⚡ Performance Metrics:');
0214 |     console.log('  • DOM Ready:', performance.now().toFixed(2) + 'ms');
0215 |     console.log('  • Interactive elements:', document.querySelectorAll('[onclick], [data-action]').length);
0216 |     console.log('  • Vulnerability cards:', document.querySelectorAll('.vulnerability-card').length);
0217 | }
0218 | 
0219 | // CSS animations for toasts
0220 | const additionalStyles = `
0221 | @keyframes slideInDown {
0222 |     from {
0223 |         opacity: 0;
0224 |         transform: translate(-50%, -100%);
0225 |     }
0226 |     to {
0227 |         opacity: 1;
0228 |         transform: translate(-50%, 0);
0229 |     }
0230 | }
0231 | 
0232 | @keyframes slideOutUp {
0233 |     from {
0234 |         opacity: 1;
0235 |         transform: translate(-50%, 0);
0236 |     }
0237 |     to {
0238 |         opacity: 0;
0239 |         transform: translate(-50%, -100%);
0240 |     }
0241 | }
0242 | `;
0243 | 
0244 | const styleSheet = document.createElement('style');
0245 | styleSheet.textContent = additionalStyles;
0246 | document.head.appendChild(styleSheet);
0247 | </script>
```

---

### adapters\output\templates\styles.html

**Ruta:** `adapters\output\templates\styles.html`

```html
0001 | <!-- adapters/output/templates/styles.html -->
0002 | <style>
0003 | /* === RESET & BASE === */
0004 | * {
0005 |     margin: 0;
0006 |     padding: 0;
0007 |     box-sizing: border-box;
0008 | }
0009 | 
0010 | body {
0011 |     font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
0012 |     line-height: 1.6;
0013 |     color: #1f2937;
0014 |     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
0015 |     min-height: 100vh;
0016 | }
0017 | 
0018 | /* === LAYOUT === */
0019 | .container {
0020 |     max-width: 1200px;
0021 |     margin: 20px auto;
0022 |     background: white;
0023 |     border-radius: 16px;
0024 |     box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
0025 |     overflow: hidden;
0026 | }
0027 | 
0028 | /* === HEADER === */
0029 | .header {
0030 |     background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
0031 |     color: white;
0032 |     padding: 2rem;
0033 |     position: relative;
0034 | }
0035 | 
0036 | .header::before {
0037 |     content: '';
0038 |     position: absolute;
0039 |     top: 0;
0040 |     left: 0;
0041 |     right: 0;
0042 |     bottom: 0;
0043 |     background: url('image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
0044 |     opacity: 0.3;
0045 | }
0046 | 
0047 | .header-content {
0048 |     position: relative;
0049 |     z-index: 1;
0050 |     text-align: center;
0051 | }
0052 | 
0053 | .header h1 {
0054 |     font-size: 2.5rem;
0055 |     font-weight: 700;
0056 |     margin-bottom: 1rem;
0057 |     text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
0058 | }
0059 | 
0060 | .header-grid {
0061 |     display: grid;
0062 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0063 |     gap: 1rem;
0064 |     margin-top: 1.5rem;
0065 | }
0066 | 
0067 | .header-item {
0068 |     background: rgba(255, 255, 255, 0.15);
0069 |     padding: 1rem;
0070 |     border-radius: 12px;
0071 |     backdrop-filter: blur(10px);
0072 |     border: 1px solid rgba(255, 255, 255, 0.2);
0073 | }
0074 | 
0075 | .header-label {
0076 |     font-size: 0.875rem;
0077 |     opacity: 0.9;
0078 |     margin-bottom: 0.25rem;
0079 | }
0080 | 
0081 | .header-value {
0082 |     font-size: 1.25rem;
0083 |     font-weight: 600;
0084 | }
0085 | 
0086 | /* === CONTENT === */
0087 | .content {
0088 |     padding: 2rem;
0089 | }
0090 | 
0091 | .section {
0092 |     margin-bottom: 3rem;
0093 | }
0094 | 
0095 | .section-title {
0096 |     font-size: 1.875rem;
0097 |     font-weight: 700;
0098 |     color: #1f2937;
0099 |     margin-bottom: 1.5rem;
0100 |     padding-bottom: 0.75rem;
0101 |     border-bottom: 3px solid #4f46e5;
0102 |     position: relative;
0103 | }
0104 | 
0105 | .section-title::after {
0106 |     content: '';
0107 |     position: absolute;
0108 |     bottom: -3px;
0109 |     left: 0;
0110 |     width: 60px;
0111 |     height: 3px;
0112 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0113 | }
0114 | 
0115 | /* === METRICS === */
0116 | .metrics-grid {
0117 |     display: grid;
0118 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0119 |     gap: 1.5rem;
0120 |     margin-bottom: 2rem;
0121 | }
0122 | 
0123 | .metric-card {
0124 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0125 |     border-radius: 16px;
0126 |     padding: 1.5rem;
0127 |     text-align: center;
0128 |     transition: transform 0.3s ease, box-shadow 0.3s ease;
0129 |     position: relative;
0130 |     overflow: hidden;
0131 | }
0132 | 
0133 | .metric-card::before {
0134 |     content: '';
0135 |     position: absolute;
0136 |     top: 0;
0137 |     left: 0;
0138 |     right: 0;
0139 |     height: 4px;
0140 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0141 | }
0142 | 
0143 | .metric-card:hover {
0144 |     transform: translateY(-4px);
0145 |     box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
0146 | }
0147 | 
0148 | .metric-icon {
0149 |     font-size: 2rem;
0150 |     margin-bottom: 0.5rem;
0151 | }
0152 | 
0153 | .metric-value {
0154 |     font-size: 2.5rem;
0155 |     font-weight: 700;
0156 |     margin-bottom: 0.5rem;
0157 |     background: linear-gradient(135deg, #4f46e5, #7c3aed);
0158 |     -webkit-background-clip: text;
0159 |     -webkit-text-fill-color: transparent;
0160 |     background-clip: text;
0161 | }
0162 | 
0163 | .metric-label {
0164 |     color: #64748b;
0165 |     font-size: 0.875rem;
0166 |     font-weight: 500;
0167 |     text-transform: uppercase;
0168 |     letter-spacing: 0.05em;
0169 | }
0170 | 
0171 | /* === VULNERABILITIES === */
0172 | .vulnerabilities-list {
0173 |     display: grid;
0174 |     gap: 1.5rem;
0175 | }
0176 | 
0177 | .vulnerability-card {
0178 |     background: white;
0179 |     border: 1px solid #e5e7eb;
0180 |     border-radius: 16px;
0181 |     overflow: hidden;
0182 |     transition: all 0.3s ease;
0183 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0184 | }
0185 | 
0186 | .vulnerability-card:hover {
0187 |     box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
0188 |     transform: translateY(-2px);
0189 | }
0190 | 
0191 | .vulnerability-card.critical {
0192 |     border-left: 6px solid #dc2626;
0193 | }
0194 | 
0195 | .vulnerability-card.high {
0196 |     border-left: 6px solid #ea580c;
0197 | }
0198 | 
0199 | .vulnerability-card.medium {
0200 |     border-left: 6px solid #d97706;
0201 | }
0202 | 
0203 | .vulnerability-card.low {
0204 |     border-left: 6px solid #16a34a;
0205 | }
0206 | 
0207 | .vulnerability-card.info {
0208 |     border-left: 6px solid #0ea5e9;
0209 | }
0210 | 
0211 | .vuln-header {
0212 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0213 |     padding: 1.5rem;
0214 |     border-bottom: 1px solid #e5e7eb;
0215 |     display: flex;
0216 |     justify-content: space-between;
0217 |     align-items: flex-start;
0218 |     gap: 1rem;
0219 | }
0220 | 
0221 | .vuln-title {
0222 |     font-size: 1.25rem;
0223 |     font-weight: 600;
0224 |     color: #1f2937;
0225 |     flex: 1;
0226 | }
0227 | 
0228 | .vuln-badges {
0229 |     display: flex;
0230 |     gap: 0.5rem;
0231 |     flex-shrink: 0;
0232 | }
0233 | 
0234 | .badge {
0235 |     padding: 0.25rem 0.75rem;
0236 |     border-radius: 12px;
0237 |     font-size: 0.75rem;
0238 |     font-weight: 600;
0239 |     text-transform: uppercase;
0240 |     letter-spacing: 0.05em;
0241 | }
0242 | 
0243 | .badge.severity-critical {
0244 |     background: #dc2626;
0245 |     color: white;
0246 | }
0247 | 
0248 | .badge.severity-high {
0249 |     background: #ea580c;
0250 |     color: white;
0251 | }
0252 | 
0253 | .badge.severity-medium {
0254 |     background: #d97706;
0255 |     color: white;
0256 | }
0257 | 
0258 | .badge.severity-low {
0259 |     background: #16a34a;
0260 |     color: white;
0261 | }
0262 | 
0263 | .badge.severity-info {
0264 |     background: #0ea5e9;
0265 |     color: white;
0266 | }
0267 | 
0268 | .badge.type-badge {
0269 |     background: #6b7280;
0270 |     color: white;
0271 | }
0272 | 
0273 | .vuln-body {
0274 |     padding: 1.5rem;
0275 | }
0276 | 
0277 | .vuln-meta {
0278 |     display: grid;
0279 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0280 |     gap: 1rem;
0281 |     margin-bottom: 1.5rem;
0282 | }
0283 | 
0284 | .meta-item {
0285 |     background: #f8fafc;
0286 |     padding: 0.75rem;
0287 |     border-radius: 8px;
0288 |     border: 1px solid #e5e7eb;
0289 | }
0290 | 
0291 | .meta-label {
0292 |     font-size: 0.75rem;
0293 |     font-weight: 600;
0294 |     color: #6b7280;
0295 |     text-transform: uppercase;
0296 |     letter-spacing: 0.05em;
0297 |     margin-bottom: 0.25rem;
0298 | }
0299 | 
0300 | .meta-value {
0301 |     font-weight: 500;
0302 |     color: #1f2937;
0303 | }
0304 | 
0305 | .meta-value a {
0306 |     color: #4f46e5;
0307 |     text-decoration: none;
0308 | }
0309 | 
0310 | .meta-value a:hover {
0311 |     text-decoration: underline;
0312 | }
0313 | 
0314 | .vuln-description,
0315 | .vuln-code,
0316 | .vuln-remediation {
0317 |     margin-bottom: 1.5rem;
0318 | }
0319 | 
0320 | .vuln-description h4,
0321 | .vuln-code h4,
0322 | .vuln-remediation h4 {
0323 |     font-size: 1rem;
0324 |     font-weight: 600;
0325 |     color: #374151;
0326 |     margin-bottom: 0.75rem;
0327 |     display: flex;
0328 |     align-items: center;
0329 |     gap: 0.5rem;
0330 | }
0331 | 
0332 | .code-block {
0333 |     background: #0f172a;
0334 |     color: #e2e8f0;
0335 |     padding: 1rem;
0336 |     border-radius: 8px;
0337 |     font-family: 'JetBrains Mono', 'Fira Code', Monaco, monospace;
0338 |     font-size: 0.875rem;
0339 |     overflow-x: auto;
0340 |     line-height: 1.5;
0341 |     border: 1px solid #334155;
0342 | }
0343 | 
0344 | .advice-content {
0345 |     background: #dbeafe;
0346 |     padding: 1rem;
0347 |     border-radius: 8px;
0348 |     border-left: 4px solid #3b82f6;
0349 |     color: #1e40af;
0350 | }
0351 | 
0352 | /* === NO VULNERABILITIES === */
0353 | .no-vulnerabilities {
0354 |     text-align: center;
0355 |     padding: 4rem 2rem;
0356 |     background: linear-gradient(135deg, #22c55e, #16a34a);
0357 |     color: white;
0358 |     border-radius: 16px;
0359 | }
0360 | 
0361 | .no-vulns-icon {
0362 |     font-size: 4rem;
0363 |     margin-bottom: 1rem;
0364 | }
0365 | 
0366 | .no-vulnerabilities h2 {
0367 |     font-size: 2rem;
0368 |     margin-bottom: 1rem;
0369 | }
0370 | 
0371 | /* === REMEDIATION === */
0372 | .remediation-summary {
0373 |     background: #f0f9ff;
0374 |     padding: 1rem;
0375 |     border-radius: 8px;
0376 |     border-left: 4px solid #0ea5e9;
0377 |     margin-bottom: 2rem;
0378 | }
0379 | 
0380 | .remediation-plans {
0381 |     display: grid;
0382 |     gap: 2rem;
0383 | }
0384 | 
0385 | .remediation-card {
0386 |     background: white;
0387 |     border: 1px solid #e5e7eb;
0388 |     border-radius: 12px;
0389 |     padding: 1.5rem;
0390 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0391 | }
0392 | 
0393 | .plan-header {
0394 |     display: flex;
0395 |     justify-content: space-between;
0396 |     align-items: center;
0397 |     margin-bottom: 1rem;
0398 | }
0399 | 
0400 | .plan-header h3 {
0401 |     font-size: 1.25rem;
0402 |     font-weight: 600;
0403 |     color: #1f2937;
0404 | }
0405 | 
0406 | .priority-badge {
0407 |     padding: 0.25rem 0.75rem;
0408 |     border-radius: 20px;
0409 |     font-size: 0.75rem;
0410 |     font-weight: 600;
0411 |     text-transform: uppercase;
0412 | }
0413 | 
0414 | .priority-badge.priority-immediate {
0415 |     background: #dc2626;
0416 |     color: white;
0417 | }
0418 | 
0419 | .priority-badge.priority-high {
0420 |     background: #ea580c;
0421 |     color: white;
0422 | }
0423 | 
0424 | .priority-badge.priority-medium {
0425 |     background: #d97706;
0426 |     color: white;
0427 | }
0428 | 
0429 | .priority-badge.priority-low {
0430 |     background: #16a34a;
0431 |     color: white;
0432 | }
0433 | 
0434 | .plan-meta {
0435 |     display: flex;
0436 |     gap: 1rem;
0437 |     margin-bottom: 1.5rem;
0438 |     flex-wrap: wrap;
0439 | }
0440 | 
0441 | .plan-stat {
0442 |     background: #f3f4f6;
0443 |     padding: 0.5rem 1rem;
0444 |     border-radius: 6px;
0445 |     font-size: 0.875rem;
0446 |     font-weight: 500;
0447 | }
0448 | 
0449 | .plan-steps {
0450 |     margin-bottom: 1.5rem;
0451 | }
0452 | 
0453 | .plan-steps h4 {
0454 |     font-size: 1rem;
0455 |     font-weight: 600;
0456 |     margin-bottom: 1rem;
0457 |     color: #374151;
0458 | }
0459 | 
0460 | .plan-steps ol {
0461 |     list-style: none;
0462 |     counter-reset: step-counter;
0463 | }
0464 | 
0465 | .remediation-step {
0466 |     counter-increment: step-counter;
0467 |     margin-bottom: 1rem;
0468 |     padding: 1rem;
0469 |     background: #f8fafc;
0470 |     border-radius: 8px;
0471 |     border-left: 4px solid #4f46e5;
0472 |     position: relative;
0473 |     padding-left: 3rem;
0474 | }
0475 | 
0476 | .remediation-step::before {
0477 |     content: counter(step-counter);
0478 |     position: absolute;
0479 |     left: 1rem;
0480 |     top: 1rem;
0481 |     background: #4f46e5;
0482 |     color: white;
0483 |     width: 1.5rem;
0484 |     height: 1.5rem;
0485 |     border-radius: 50%;
0486 |     display: flex;
0487 |     align-items: center;
0488 |     justify-content: center;
0489 |     font-weight: 600;
0490 |     font-size: 0.875rem;
0491 | }
0492 | 
0493 | .step-header {
0494 |     display: flex;
0495 |     justify-content: space-between;
0496 |     align-items: flex-start;
0497 |     margin-bottom: 0.5rem;
0498 | }
0499 | 
0500 | .step-meta {
0501 |     font-size: 0.75rem;
0502 |     color: #6b7280;
0503 |     background: #e5e7eb;
0504 |     padding: 0.25rem 0.5rem;
0505 |     border-radius: 4px;
0506 | }
0507 | 
0508 | .step-description {
0509 |     color: #4b5563;
0510 |     margin-bottom: 0.75rem;
0511 | }
0512 | 
0513 | .step-code {
0514 |     background: #f3f4f6;
0515 |     color: #374151;
0516 |     padding: 0.75rem;
0517 |     border-radius: 6px;
0518 |     font-family: 'JetBrains Mono', monospace;
0519 |     font-size: 0.8rem;
0520 |     border: 1px solid #d1d5db;
0521 | }
0522 | 
0523 | .risk-warning {
0524 |     background: #fef2f2;
0525 |     padding: 1rem;
0526 |     border-radius: 8px;
0527 |     border-left: 4px solid #ef4444;
0528 |     color: #991b1b;
0529 | }
0530 | 
0531 | .risk-warning h5 {
0532 |     font-weight: 600;
0533 |     margin-bottom: 0.5rem;
0534 | }
0535 | 
0536 | /* === TECHNICAL DETAILS === */
0537 | .technical-details {
0538 |     background: #f8fafc;
0539 |     border: 1px solid #e5e7eb;
0540 |     border-radius: 12px;
0541 |     overflow: hidden;
0542 | }
0543 | 
0544 | .details-toggle {
0545 |     background: #f1f5f9;
0546 |     padding: 1rem 1.5rem;
0547 |     cursor: pointer;
0548 |     font-weight: 600;
0549 |     color: #374151;
0550 |     display: flex;
0551 |     align-items: center;
0552 |     gap: 0.5rem;
0553 |     border: none;
0554 |     width: 100%;
0555 |     text-align: left;
0556 |     transition: background 0.2s;
0557 | }
0558 | 
0559 | .details-toggle:hover {
0560 |     background: #e2e8f0;
0561 | }
0562 | 
0563 | .details-toggle::after {
0564 |     content: '▶';
0565 |     margin-left: auto;
0566 |     transition: transform 0.3s;
0567 | }
0568 | 
0569 | .technical-details[open] .details-toggle::after {
0570 |     transform: rotate(90deg);
0571 | }
0572 | 
0573 | .details-content {
0574 |     padding: 1.5rem;
0575 | }
0576 | 
0577 | .tech-grid {
0578 |     display: grid;
0579 |     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
0580 |     gap: 1.5rem;
0581 |     margin-bottom: 1.5rem;
0582 | }
0583 | 
0584 | .tech-item h4 {
0585 |     font-weight: 600;
0586 |     color: #374151;
0587 |     margin-bottom: 0.75rem;
0588 | }
0589 | 
0590 | .tech-item ul {
0591 |     list-style: none;
0592 |     padding-left: 0;
0593 | }
0594 | 
0595 | .tech-item li {
0596 |     padding: 0.25rem 0;
0597 |     color: #6b7280;
0598 | }
0599 | 
0600 | .analysis-summary {
0601 |     background: white;
0602 |     padding: 1rem;
0603 |     border-radius: 8px;
0604 |     border: 1px solid #e5e7eb;
0605 | }
0606 | 
0607 | .analysis-summary h4 {
0608 |     font-weight: 600;
0609 |     color: #374151;
0610 |     margin-bottom: 0.75rem;
0611 | }
0612 | 
0613 | .analysis-summary pre {
0614 |     background: #f8fafc;
0615 |     padding: 1rem;
0616 |     border-radius: 6px;
0617 |     font-size: 0.875rem;
0618 |     color: #4b5563;
0619 |     white-space: pre-wrap;
0620 |     word-wrap: break-word;
0621 | }
0622 | 
0623 | /* === FOOTER === */
0624 | .footer {
0625 |     background: #1f2937;
0626 |     color: white;
0627 |     padding: 2rem;
0628 |     text-align: center;
0629 | }
0630 | 
0631 | .footer-content p {
0632 |     margin-bottom: 0.5rem;
0633 | }
0634 | 
0635 | /* === RESPONSIVE DESIGN === */
0636 | @media (max-width: 768px) {
0637 |     .container {
0638 |         margin: 10px;
0639 |         border-radius: 8px;
0640 |     }
0641 |     
0642 |     .header {
0643 |         padding: 1.5rem;
0644 |     }
0645 |     
0646 |     .header h1 {
0647 |         font-size: 2rem;
0648 |     }
0649 |     
0650 |     .header-grid {
0651 |         grid-template-columns: 1fr;
0652 |     }
0653 |     
0654 |     .content {
0655 |         padding: 1.5rem;
0656 |     }
0657 |     
0658 |     .metrics-grid {
0659 |         grid-template-columns: 1fr;
0660 |     }
0661 |     
0662 |     .vuln-header {
0663 |         flex-direction: column;
0664 |         align-items: flex-start;
0665 |     }
0666 |     
0667 |     .vuln-meta {
0668 |         grid-template-columns: 1fr;
0669 |     }
0670 |     
0671 |     .plan-header {
0672 |         flex-direction: column;
0673 |         align-items: flex-start;
0674 |         gap: 0.5rem;
0675 |     }
0676 |     
0677 |     .plan-meta {
0678 |         flex-direction: column;
0679 |     }
0680 |     
0681 |     .step-header {
0682 |         flex-direction: column;
0683 |         align-items: flex-start;
0684 |     }
0685 | }
0686 | 
0687 | /* === ANIMATIONS === */
0688 | @keyframes fadeIn {
0689 |     from {
0690 |         opacity: 0;
0691 |         transform: translateY(20px);
0692 |     }
0693 |     to {
0694 |         opacity: 1;
0695 |         transform: translateY(0);
0696 |     }
0697 | }
0698 | 
0699 | .section {
0700 |     animation: fadeIn 0.6s ease-out;
0701 | }
0702 | 
0703 | /* === PRINT STYLES === */
0704 | @media print {
0705 |     body {
0706 |         background: white;
0707 |     }
0708 |     
0709 |     .container {
0710 |         box-shadow: none;
0711 |         margin: 0;
0712 |     }
0713 |     
0714 |     .header {
0715 |         background: #4f46e5 !important;
0716 |         -webkit-print-color-adjust: exact;
0717 |         color-adjust: exact;
0718 |     }
0719 |     
0720 |     .technical-details {
0721 |         border: 1px solid #ccc;
0722 |     }
0723 |     
0724 |     .details-content {
0725 |         display: block !important;
0726 |     }
0727 |     
0728 |     .details-toggle {
0729 |         display: none;
0730 |     }
0731 |     
0732 |     .vulnerability-card {
0733 |         break-inside: avoid;
0734 |         page-break-inside: avoid;
0735 |         margin-bottom: 1rem;
0736 |     }
0737 | }
0738 | </style>
```

---

### adapters\output\templates\__init__.py

**Ruta:** `adapters\output\templates\__init__.py`

```py
```

---

### adapters\processing\chunker.py

**Ruta:** `adapters\processing\chunker.py`

```py
0001 | # adapters/processing/chunker.py
0002 | import logging
0003 | import math
0004 | from typing import List, Dict, Any, Optional
0005 | from dataclasses import dataclass
0006 | 
0007 | from core.models import ScanResult, Vulnerability, ChunkingStrategy
0008 | from core.exceptions import ChunkingError
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | @dataclass
0013 | class ChunkMetadata:
0014 |     """Metadatos optimizados de chunk"""
0015 |     id: int
0016 |     strategy: str
0017 |     total_chunks: int
0018 |     vulnerability_count: int
0019 |     estimated_size_bytes: int
0020 |     has_overlap: bool = False
0021 | 
0022 | @dataclass
0023 | class VulnerabilityChunk:
0024 |     """Chunk optimizado de vulnerabilidades"""
0025 |     id: int
0026 |     vulnerabilities: List[Vulnerability]
0027 |     metadata: ChunkMetadata
0028 |     
0029 |     @property
0030 |     def size_estimate(self) -> int:
0031 |         """Estimación rápida de tamaño"""
0032 |         return sum(len(v.title) + len(v.description) + len(v.code_snippet or "") 
0033 |                   for v in self.vulnerabilities)
0034 | 
0035 | class OptimizedChunker:
0036 |     """Chunker optimizado con estrategias inteligentes"""
0037 |     
0038 |     def __init__(self, config: Dict[str, Any]):
0039 |         self.max_vulns_per_chunk = config.get("max_vulnerabilities_per_chunk", 5)
0040 |         self.max_size_bytes = config.get("max_size_bytes", 8000)
0041 |         self.overlap_vulns = config.get("overlap_vulnerabilities", 1)
0042 |         self.min_chunk_size = config.get("min_chunk_size", 3)
0043 |     
0044 |     def should_chunk(self, scan_result: ScanResult) -> bool:
0045 |         """Determinar si se necesita chunking con heurísticas optimizadas"""
0046 |         
0047 |         vuln_count = len(scan_result.vulnerabilities)
0048 |         
0049 |         # Chunking por cantidad
0050 |         if vuln_count > self.max_vulns_per_chunk:
0051 |             logger.info(f"Chunking needed: {vuln_count} vulnerabilities > {self.max_vulns_per_chunk}")
0052 |             return True
0053 |         
0054 |         # Chunking por tamaño estimado
0055 |         estimated_size = self._estimate_total_size(scan_result.vulnerabilities)
0056 |         if estimated_size > self.max_size_bytes:
0057 |             logger.info(f"Chunking needed: {estimated_size} bytes > {self.max_size_bytes}")
0058 |             return True
0059 |         
0060 |         return False
0061 |     
0062 |     def create_chunks(self, scan_result: ScanResult) -> List[VulnerabilityChunk]:
0063 |         """Crear chunks usando estrategia óptima"""
0064 |         
0065 |         vulnerabilities = scan_result.vulnerabilities
0066 |         
0067 |         if not vulnerabilities:
0068 |             return []
0069 |         
0070 |         if not self.should_chunk(scan_result):
0071 |             # Chunk único
0072 |             return [VulnerabilityChunk(
0073 |                 id=1,
0074 |                 vulnerabilities=vulnerabilities,
0075 |                 metadata=ChunkMetadata(
0076 |                     id=1, strategy="no_chunking", total_chunks=1,
0077 |                     vulnerability_count=len(vulnerabilities),
0078 |                     estimated_size_bytes=self._estimate_total_size(vulnerabilities)
0079 |                 )
0080 |             )]
0081 |         
0082 |         # Seleccionar estrategia óptima
0083 |         strategy = self._select_strategy(vulnerabilities)
0084 |         
0085 |         try:
0086 |             if strategy == "by_count":
0087 |                 return self._chunk_by_count(vulnerabilities)
0088 |             else:  # by_size
0089 |                 return self._chunk_by_size(vulnerabilities)
0090 |         
0091 |         except Exception as e:
0092 |             logger.error(f"Chunking failed: {e}")
0093 |             return self._emergency_chunking(vulnerabilities)
0094 |     
0095 |     def _select_strategy(self, vulnerabilities: List[Vulnerability]) -> str:
0096 |         """Seleccionar estrategia óptima basada en características"""
0097 |         
0098 |         avg_desc_length = sum(len(v.description) for v in vulnerabilities) / len(vulnerabilities)
0099 |         
0100 |         # Si las descripciones son muy largas, usar estrategia por tamaño
0101 |         if avg_desc_length > 300:
0102 |             return "by_size"
0103 |         
0104 |         return "by_count"
0105 |     
0106 |     def _chunk_by_count(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
0107 |         """Chunking optimizado por cantidad"""
0108 |         
0109 |         chunks = []
0110 |         chunk_size = self.max_vulns_per_chunk
0111 |         
0112 |         for i in range(0, len(vulnerabilities), chunk_size - self.overlap_vulns):
0113 |             chunk_vulns = vulnerabilities[i:i + chunk_size]
0114 |             
0115 |             # Evitar chunks muy pequeños al final
0116 |             if i > 0 and len(chunk_vulns) < self.min_chunk_size:
0117 |                 if chunks:
0118 |                     chunks[-1].vulnerabilities.extend(chunk_vulns)
0119 |                     chunks[-1].metadata.vulnerability_count += len(chunk_vulns)
0120 |                 break
0121 |             
0122 |             chunk = VulnerabilityChunk(
0123 |                 id=len(chunks) + 1,
0124 |                 vulnerabilities=chunk_vulns,
0125 |                 metadata=ChunkMetadata(
0126 |                     id=len(chunks) + 1,
0127 |                     strategy="by_count",
0128 |                     total_chunks=math.ceil(len(vulnerabilities) / chunk_size),
0129 |                     vulnerability_count=len(chunk_vulns),
0130 |                     estimated_size_bytes=self._estimate_total_size(chunk_vulns),
0131 |                     has_overlap=i > 0 and self.overlap_vulns > 0
0132 |                 )
0133 |             )
0134 |             chunks.append(chunk)
0135 |         
0136 |         # Actualizar total_chunks
0137 |         for chunk in chunks:
0138 |             chunk.metadata.total_chunks = len(chunks)
0139 |         
0140 |         logger.info(f"Created {len(chunks)} chunks by count strategy")
0141 |         return chunks
0142 |     
0143 |     def _chunk_by_size(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
0144 |         """Chunking optimizado por tamaño"""
0145 |         
0146 |         chunks = []
0147 |         current_vulns = []
0148 |         current_size = 0
0149 |         
0150 |         for vuln in vulnerabilities:
0151 |             vuln_size = self._estimate_vuln_size(vuln)
0152 |             
0153 |             if current_size + vuln_size > self.max_size_bytes and current_vulns:
0154 |                 # Crear chunk actual
0155 |                 chunk = VulnerabilityChunk(
0156 |                     id=len(chunks) + 1,
0157 |                     vulnerabilities=current_vulns.copy(),
0158 |                     metadata=ChunkMetadata(
0159 |                         id=len(chunks) + 1,
0160 |                         strategy="by_size",
0161 |                         total_chunks=0,  # Se actualizará después
0162 |                         vulnerability_count=len(current_vulns),
0163 |                         estimated_size_bytes=current_size
0164 |                     )
0165 |                 )
0166 |                 chunks.append(chunk)
0167 |                 
0168 |                 # Nuevo chunk con overlap
0169 |                 overlap_vulns = current_vulns[-self.overlap_vulns:] if self.overlap_vulns > 0 else []
0170 |                 current_vulns = overlap_vulns + [vuln]
0171 |                 current_size = sum(self._estimate_vuln_size(v) for v in current_vulns)
0172 |             else:
0173 |                 current_vulns.append(vuln)
0174 |                 current_size += vuln_size
0175 |         
0176 |         # Último chunk
0177 |         if current_vulns:
0178 |             chunk = VulnerabilityChunk(
0179 |                 id=len(chunks) + 1,
0180 |                 vulnerabilities=current_vulns,
0181 |                 metadata=ChunkMetadata(
0182 |                     id=len(chunks) + 1,
0183 |                     strategy="by_size",
0184 |                     total_chunks=0,
0185 |                     vulnerability_count=len(current_vulns),
0186 |                     estimated_size_bytes=current_size
0187 |                 )
0188 |             )
0189 |             chunks.append(chunk)
0190 |         
0191 |         # Actualizar total_chunks
0192 |         for chunk in chunks:
0193 |             chunk.metadata.total_chunks = len(chunks)
0194 |         
0195 |         logger.info(f"Created {len(chunks)} chunks by size strategy")
0196 |         return chunks
0197 |     
0198 |     def _emergency_chunking(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
0199 |         """Chunking de emergencia ultra-conservador"""
0200 |         
0201 |         logger.warning("Using emergency chunking with very small chunks")
0202 |         
0203 |         emergency_size = 3  # Chunks muy pequeños
0204 |         chunks = []
0205 |         
0206 |         for i in range(0, len(vulnerabilities), emergency_size):
0207 |             chunk_vulns = vulnerabilities[i:i + emergency_size]
0208 |             
0209 |             chunk = VulnerabilityChunk(
0210 |                 id=len(chunks) + 1,
0211 |                 vulnerabilities=chunk_vulns,
0212 |                 metadata=ChunkMetadata(
0213 |                     id=len(chunks) + 1,
0214 |                     strategy="emergency",
0215 |                     total_chunks=math.ceil(len(vulnerabilities) / emergency_size),
0216 |                     vulnerability_count=len(chunk_vulns),
0217 |                     estimated_size_bytes=self._estimate_total_size(chunk_vulns)
0218 |                 )
0219 |             )
0220 |             chunks.append(chunk)
0221 |         
0222 |         return chunks
0223 |     
0224 |     def _estimate_total_size(self, vulnerabilities: List[Vulnerability]) -> int:
0225 |         """Estimación rápida de tamaño total"""
0226 |         return sum(self._estimate_vuln_size(v) for v in vulnerabilities)
0227 |     
0228 |     def _estimate_vuln_size(self, vulnerability: Vulnerability) -> int:
0229 |         """Estimación optimizada de tamaño de vulnerabilidad"""
0230 |         base_size = len(vulnerability.title) + len(vulnerability.description)
0231 |         code_size = len(vulnerability.code_snippet or "")
0232 |         
0233 |         # Factor de multiplicación para metadatos JSON (reducido)
0234 |         return int((base_size + code_size) * 1.3)
0235 | 
0236 |         
0237 |         ```

---

### adapters\processing\__init__.py

**Ruta:** `adapters\processing\__init__.py`

```py
```

---

### application\cli.py

**Ruta:** `application\cli.py`

```py
0001 | # application/cli.py
0002 | #!/usr/bin/env python3
0003 | """
0004 | 🛡️ Security Analysis Platform v3.0 - CLI
0005 | Complete command-line interface with filtering support
0006 | """
0007 | 
0008 | import asyncio
0009 | import sys
0010 | import os
0011 | from pathlib import Path
0012 | from typing import Optional
0013 | import click
0014 | 
0015 | # Add project root to path
0016 | sys.path.insert(0, str(Path(__file__).parent.parent))
0017 | 
0018 | from application.factory import create_factory
0019 | from application.use_cases import AnalysisUseCase, CLIUseCase
0020 | from infrastructure.config import settings
0021 | 
0022 | 
0023 | # ============================================================================
0024 | # CLI GROUP
0025 | # ============================================================================
0026 | 
0027 | @click.group()
0028 | @click.version_option("1.0", prog_name="LLM Vulnerability Triage")
0029 | def cli():
0030 |     """🛡️ LLM Vulnerability Triage v1.0 - Advanced Security Analysis"""
0031 |     pass
0032 | 
0033 | 
0034 | # ============================================================================
0035 | # ANALYZE COMMAND - MAIN FUNCTIONALITY
0036 | # ============================================================================
0037 | 
0038 | @cli.command()
0039 | @click.argument('input_file', type=click.Path(exists=True))
0040 | @click.option('-o', '--output', default='security_report.html', help='Output file')
0041 | @click.option('-v', '--verbose', is_flag=True, help='Verbose logging')
0042 | @click.option('--no-dedup', is_flag=True, help='Disable duplicate removal')
0043 | def analyze(input_file, output, verbose, no_dedup):
0044 |     """Analyze security vulnerabilities from SAST results"""
0045 |     
0046 |     click.echo("🛡️  LLM Vulnerability Triage v1.0\n")
0047 |     click.echo(f"📁 {Path(input_file).name} → {output}")
0048 |     
0049 |     if no_dedup:
0050 |         click.echo("🔄 Deduplication: Disabled")
0051 |     
0052 |     try:
0053 |         success = asyncio.run(_run_analysis(
0054 |             input_file=input_file,
0055 |             output=output,
0056 |             verbose=verbose,
0057 |             dedup_enabled=not no_dedup
0058 |         ))
0059 |         
0060 |         sys.exit(0 if success else 1)
0061 |         
0062 |     except KeyboardInterrupt:
0063 |         click.echo("\n🛑 Interrupted")
0064 |         sys.exit(1)
0065 | 
0066 | 
0067 | 
0068 | async def _run_analysis(input_file, output, verbose, min_cvss=0.0, 
0069 |                        dedup_enabled=True, dedup_mode='moderate'):
0070 |     """Execute analysis"""
0071 |     
0072 |     try:
0073 |         factory = create_factory()
0074 |         factory.enable_dedup = dedup_enabled
0075 |         factory.dedup_strategy = dedup_mode
0076 |         
0077 |         if not settings.has_llm_provider:
0078 |             click.echo("⚠️  No LLM - using basic mode")
0079 |         
0080 |         analysis = AnalysisUseCase(
0081 |             scanner_service=factory.create_scanner_service(),
0082 |             triage_service=factory.create_triage_service(),
0083 |             remediation_service=factory.create_remediation_service(),
0084 |             reporter_service=factory.create_reporter_service(),
0085 |             chunker=factory.create_chunker(),
0086 |             metrics=factory.get_metrics()
0087 |         )
0088 |         
0089 |         cli_case = CLIUseCase(analysis)
0090 |         return await cli_case.execute_cli_analysis(input_file, output, None, verbose)
0091 |         
0092 |     except Exception as e:
0093 |         click.echo(f"❌ {e}")
0094 |         if verbose:
0095 |             import traceback
0096 |             traceback.print_exc()
0097 |         return False
0098 | 
0099 | 
0100 | # ============================================================================
0101 | # VALIDATE COMMAND
0102 | # ============================================================================
0103 | 
0104 | @cli.command()
0105 | @click.argument('input_file', type=click.Path(exists=True))
0106 | def validate(input_file):
0107 |     """Validate input file format and structure"""
0108 |     click.echo(f"🔍 Validating: {input_file}")
0109 |     
0110 |     try:
0111 |         from core.services.scanner import ScannerService
0112 |         
0113 |         scanner = ScannerService()
0114 |         
0115 |         # Basic validation
0116 |         scanner._validate_file(input_file)
0117 |         click.echo("✅ File validation: PASSED")
0118 |         
0119 |         # Load and analyze structure
0120 |         raw_data = scanner._load_file(input_file)
0121 |         click.echo("✅ JSON format: VALID")
0122 |         
0123 |         # Analyze structure
0124 |         if isinstance(raw_data, list):
0125 |             click.echo(f"📊 Format: List with {len(raw_data)} items")
0126 |         elif isinstance(raw_data, dict):
0127 |             keys = list(raw_data.keys())[:5]
0128 |             click.echo(f"📊 Format: Object with keys: {keys}")
0129 |             
0130 |             # Look for vulnerability containers
0131 |             for container_key in ['findings', 'vulnerabilities', 'issues', 'results']:
0132 |                 if container_key in raw_data and isinstance(raw_data[container_key], list):
0133 |                     count = len(raw_data[container_key])
0134 |                     click.echo(f"🎯 Found {count} items in '{container_key}'")
0135 |                     
0136 |                     # Sample first item
0137 |                     if count > 0:
0138 |                         sample = raw_data[container_key][0]
0139 |                         if isinstance(sample, dict):
0140 |                             sample_keys = list(sample.keys())[:3]
0141 |                             click.echo(f"📋 Sample item keys: {sample_keys}")
0142 |                             
0143 |                             # Check for CVSS
0144 |                             if any(k in sample for k in ['cvss_score', 'cvss', 'score']):
0145 |                                 click.echo(f"✅ CVSS scores detected")
0146 |                     break
0147 |         
0148 |         # Test parsing
0149 |         parser = scanner.parser
0150 |         vulnerabilities = parser.parse(raw_data)
0151 |         click.echo(f"✅ Parsing test: Found {len(vulnerabilities)} vulnerabilities")
0152 |         
0153 |         if vulnerabilities:
0154 |             severity_dist = {}
0155 |             for vuln in vulnerabilities:
0156 |                 sev = vuln.severity.value
0157 |                 severity_dist[sev] = severity_dist.get(sev, 0) + 1
0158 |             
0159 |             click.echo("\n📈 Severity distribution:")
0160 |             for severity, count in severity_dist.items():
0161 |                 click.echo(f"  • {severity}: {count}")
0162 |             
0163 |             # Check CVSS scores
0164 |             cvss_scores = [v.meta.get('cvss_score') for v in vulnerabilities 
0165 |                           if v.meta.get('cvss_score') is not None]
0166 |             
0167 |             if cvss_scores:
0168 |                 click.echo(f"\n📊 CVSS Statistics ({len(cvss_scores)} vulnerabilities with scores):")
0169 |                 click.echo(f"  • Min: {min(cvss_scores):.1f}")
0170 |                 click.echo(f"  • Max: {max(cvss_scores):.1f}")
0171 |                 click.echo(f"  • Average: {sum(cvss_scores)/len(cvss_scores):.1f}")
0172 |                 high_cvss = sum(1 for s in cvss_scores if s >= 7.0)
0173 |                 click.echo(f"  • High severity (>= 7.0): {high_cvss}")
0174 |             else:
0175 |                 click.echo(f"\n⚠️  No CVSS scores found in vulnerabilities")
0176 |     
0177 |     except Exception as e:
0178 |         click.echo(f"❌ Validation failed: {e}")
0179 | 
0180 | 
0181 | # ============================================================================
0182 | # EXAMPLES COMMAND
0183 | # ============================================================================
0184 | 
0185 | @cli.command()
0186 | def examples():
0187 |     """Show usage examples and help"""
0188 |     click.echo("""
0189 | 🎓 Security Analysis Platform v3.0 - Usage Examples
0190 | 
0191 | 📝 BASIC USAGE:
0192 |    security-analyzer analyze vulnerabilities.json
0193 | 
0194 | 🎯 ADVANCED OPTIONS:
0195 |    # Custom output file
0196 |    security-analyzer analyze scan.json -o my_report.html
0197 | 
0198 |    # Specify programming language
0199 |    security-analyzer analyze abap_scan.json -l abap
0200 | 
0201 |    # Verbose output for debugging
0202 |    security-analyzer analyze results.json --verbose
0203 | 
0204 |    # Basic mode (no LLM analysis)
0205 |    security-analyzer analyze scan.json --basic-mode
0206 | 
0207 | 🆕 FILTERING OPTIONS:
0208 |    # Filter by minimum CVSS score (only analyze HIGH/CRITICAL)
0209 |    security-analyzer analyze scan.json --min-cvss 7.0
0210 |    
0211 |    # Disable duplicate removal (keep all duplicates)
0212 |    security-analyzer analyze scan.json --no-remove-duplicates
0213 |  
0214 |    
0215 |    # Combined: CVSS + Deduplication
0216 |    security-analyzer analyze scan.json --min-cvss 6.5 --dedup-strategy loose
0217 | 
0218 | 🧩 CHUNKING OPTIONS:
0219 |    # Force or disable chunking
0220 |    security-analyzer analyze small_scan.json --disable-chunking
0221 | 
0222 | 
0223 | 🔧 SYSTEM COMMANDS:
0224 |    security-analyzer setup              # Test configuration
0225 |    security-analyzer validate file.json # Validate input format
0226 |    security-analyzer examples           # Show this help
0227 |    security-analyzer metrics            # View performance metrics
0228 | 
0229 | 📁 EXPECTED INPUT FORMAT:
0230 |    {
0231 |      "findings": [
0232 |        {
0233 |          "rule_id": "abap-sql-injection-001",
0234 |          "title": "SQL Injection Vulnerability",
0235 |          "message": "User input directly concatenated into SQL query",
0236 |          "severity": "HIGH",
0237 |          "cvss_score": 8.5,  // 🆕 Optional CVSS score (0.0-10.0)
0238 |          "location": {
0239 |            "file": "src/login.abap",
0240 |            "line": 42,
0241 |            "context": ["SELECT * FROM users", "WHERE name = '" + input + "'"]
0242 |          },
0243 |          "cwe": "CWE-89"
0244 |        }
0245 |      ]
0246 |    }
0247 | 
0248 | 🔑 ENVIRONMENT VARIABLES:
0249 |    OPENAI_API_KEY          # OpenAI GPT API key
0250 |    RESEARCH_API_KEY        # IBM WatsonX API key
0251 |    LOG_LEVEL               # Logging level (DEBUG, INFO, WARNING, ERROR)
0252 |    CHUNKING_MAX_VULNS      # Max vulnerabilities per chunk (default: 5)
0253 |    CACHE_ENABLED           # Enable result caching (default: true)
0254 | 
0255 | 💡 PRACTICAL EXAMPLES:
0256 | 
0257 |    # Focus on critical issues only
0258 |    security-analyzer analyze scan.json --min-cvss 9.0
0259 | 
0260 |    # Analyze with strict deduplication (most conservative)
0261 |    security-analyzer analyze scan.json --dedup-strategy strict
0262 | 
0263 |    # Quick scan without deduplication (see all findings)
0264 |    security-analyzer analyze scan.json --no-remove-duplicates --basic-mode
0265 | 
0266 |    # Production-ready analysis
0267 |    security-analyzer analyze production_scan.json \\
0268 |        --min-cvss 7.0 \\
0269 |        --dedup-strategy moderate \\
0270 |        -l java \\
0271 |        --open-browser
0272 | 
0273 |    # Debug mode with all details
0274 |    security-analyzer analyze scan.json --verbose --no-remove-duplicates
0275 | 
0276 | 📊 CVSS SCORE RANGES:
0277 |    • 0.0-3.9:  LOW     (informational issues)
0278 |    • 4.0-6.9:  MEDIUM  (moderate risk)
0279 |    • 7.0-8.9:  HIGH    (serious vulnerabilities)
0280 |    • 9.0-10.0: CRITICAL (critical security flaws)
0281 | 
0282 | 🔄 DEDUPLICATION IMPACT:
0283 |    Without dedup: 100% of findings (includes duplicates)
0284 |    Strict mode:   ~75-85% kept (very safe, minimal false removals)
0285 |    Moderate mode: ~65-75% kept (balanced, recommended)
0286 |    Loose mode:    ~50-65% kept (aggressive, may over-deduplicate)
0287 | 
0288 | 📈 TYPICAL WORKFLOW:
0289 | 
0290 |    1. Validate your input file first:
0291 |       security-analyzer validate scan.json
0292 | 
0293 |    2. Run analysis with appropriate filters:
0294 |       security-analyzer analyze scan.json --min-cvss 7.0
0295 | 
0296 |    3. Review the HTML report in your browser
0297 | 
0298 |    4. Re-run with different settings if needed:
0299 |       security-analyzer analyze scan.json --dedup-strategy loose
0300 | 
0301 | 💡 TIPS:
0302 |    • Use --verbose for detailed logs and debugging
0303 |    • The system auto-detects input format and language
0304 |    • LLM analysis significantly improves accuracy
0305 |    • Use --min-cvss to focus on critical vulnerabilities
0306 |    • Deduplication is enabled by default to reduce noise
0307 |    • Reports are interactive with search functionality
0308 |    • Cache speeds up repeated analysis of same files
0309 | 
0310 | 📚 For more information: https://github.com/your-org/security-analyzer
0311 | """)
0312 | 
0313 | 
0314 | # ============================================================================
0315 | # METRICS COMMAND
0316 | # ============================================================================
0317 | 
0318 | @cli.command()
0319 | def metrics():
0320 |     """Display performance metrics from last session"""
0321 |     click.echo("📊 Performance Metrics")
0322 |     click.echo("=" * 50)
0323 |     
0324 |     # Check if metrics file exists
0325 |     metrics_file = Path(".security_cache/metrics.json")
0326 |     
0327 |     if metrics_file.exists():
0328 |         try:
0329 |             import json
0330 |             with open(metrics_file, 'r') as f:
0331 |                 data = json.load(f)
0332 |             
0333 |             click.echo(f"\n📈 Session Summary:")
0334 |             click.echo(f"  • Total analyses: {data.get('total_analyses', 0)}")
0335 |             click.echo(f"  • Success rate: {data.get('success_rate', 0):.1%}")
0336 |             click.echo(f"  • Average time: {data.get('avg_time', 0):.2f}s")
0337 |             click.echo(f"  • Vulnerabilities analyzed: {data.get('total_vulns', 0)}")
0338 |             click.echo(f"  • Duplicates removed: {data.get('duplicates_removed', 0)}")
0339 |             
0340 |         except Exception as e:
0341 |             click.echo(f"❌ Could not load metrics: {e}")
0342 |     else:
0343 |         click.echo("\n⚠️  No metrics file found")
0344 |         click.echo("Metrics are collected during analysis.")
0345 |         click.echo("Run an analysis first, then check metrics again.")
0346 | 
0347 | 
0348 | # ============================================================================
0349 | # MAIN ENTRY POINT
0350 | # ============================================================================
0351 | 
0352 | if __name__ == '__main__':
0353 |     cli()
```

---

### application\factory.py

**Ruta:** `application\factory.py`

```py
0001 | # application/factory.py - ACTUALIZADO CON CONTROL DE DEBUG
0002 | import logging
0003 | from typing import Optional
0004 | 
0005 | from core.services.scanner import ScannerService
0006 | from core.services.triage import TriageService
0007 | from core.services.remediation import RemediationService
0008 | from core.services.reporter import ReporterService
0009 | from infrastructure.llm.client import LLMClient
0010 | from infrastructure.cache import AnalysisCache
0011 | from infrastructure.config import settings
0012 | from adapters.processing.chunker import OptimizedChunker
0013 | from shared.metrics import MetricsCollector
0014 | from shared.logger import setup_logging
0015 | 
0016 | logger = logging.getLogger(__name__)
0017 | 
0018 | class ServiceFactory:
0019 |     """Factory optimizado con control de debug automático"""
0020 |     
0021 |     def __init__(self, enable_cache: bool = True, log_level: str = "INFO"):
0022 |         # Setup logging
0023 |         setup_logging(log_level)
0024 |         
0025 |         # Initialize shared components
0026 |         self.settings = settings
0027 |         self.metrics = MetricsCollector() if settings.metrics_enabled else None
0028 |         self.cache = AnalysisCache(settings.cache_directory, settings.cache_ttl_hours) if enable_cache else None
0029 |         
0030 |         # Control de debug
0031 |         self.debug_mode = False
0032 |         
0033 |         # Validate configuration
0034 |         self._validate_configuration()
0035 |         
0036 |         logger.info(f"ServiceFactory initialized with {settings.get_available_llm_provider()}")
0037 |     
0038 |     def enable_debug_mode(self):
0039 |         """Habilitar modo debug - será llamado desde el debugger"""
0040 |         self.debug_mode = True
0041 |         logger.info("🔍 Debug mode enabled in ServiceFactory")
0042 |     
0043 |     def disable_debug_mode(self):
0044 |         """Deshabilitar modo debug"""
0045 |         self.debug_mode = False
0046 |         logger.info("🔍 Debug mode disabled in ServiceFactory")
0047 |     
0048 |     def _validate_configuration(self) -> None:
0049 |         """Validate system configuration"""
0050 |         if not self.settings.has_llm_provider:
0051 |             logger.warning("No LLM providers configured - system will run in basic mode")
0052 |         else:
0053 |             logger.info(f"LLM provider available: {self.settings.get_available_llm_provider()}")
0054 |     
0055 |     def create_scanner_service(self) -> ScannerService:
0056 |         return ScannerService(
0057 |             cache=self.cache,
0058 |             enable_deduplication=getattr(self, 'enable_dedup', True),
0059 |             dedup_strategy=getattr(self, 'dedup_strategy', 'moderate')
0060 |         )
0061 |     
0062 |     def create_llm_client(self) -> Optional[LLMClient]:
0063 |         """Create LLM client with debug control"""
0064 |         if not self.settings.has_llm_provider:
0065 |             return None
0066 |         
0067 |         try:
0068 |             provider = self.settings.get_available_llm_provider()
0069 |             # Pasar el estado de debug al cliente
0070 |             client = LLMClient(primary_provider=provider, enable_debug=self.debug_mode)
0071 |             
0072 |             # Si el debug está habilitado, registrar el cliente automáticamente
0073 |             if self.debug_mode:
0074 |                 try:
0075 |                     from debug.llm_debugger import register_llm_client_for_debug
0076 |                     register_llm_client_for_debug(client)
0077 |                 except ImportError:
0078 |                     logger.warning("Debug module not available")
0079 |             
0080 |             return client
0081 |         except Exception as e:
0082 |             logger.error(f"Failed to create LLM client: {e}")
0083 |             return None
0084 |    
0085 |     def create_triage_service(self) -> Optional[TriageService]:
0086 |         """Create triage service with LLM client"""
0087 |         llm_client = self.create_llm_client()
0088 |         if not llm_client:
0089 |             return None
0090 |         
0091 |         return TriageService(llm_client=llm_client, metrics=self.metrics)
0092 |     
0093 |     def create_remediation_service(self) -> Optional[RemediationService]:
0094 |         """Create remediation service with LLM client"""
0095 |         llm_client = self.create_llm_client()
0096 |         if not llm_client:
0097 |             return None
0098 |         
0099 |         return RemediationService(llm_client=llm_client, metrics=self.metrics)
0100 |     
0101 |     def create_reporter_service(self) -> ReporterService:
0102 |         """Create reporter service"""
0103 |         return ReporterService(metrics=self.metrics)
0104 |     
0105 |     def create_chunker(self) -> OptimizedChunker:
0106 |         """Create optimized chunker"""
0107 |         return OptimizedChunker(self.settings.chunking_config)
0108 |     
0109 |     def get_metrics(self) -> Optional[MetricsCollector]:
0110 |         """Get metrics collector"""
0111 |         return self.metrics
0112 | 
0113 | # Convenience function
0114 | def create_factory() -> ServiceFactory:
0115 |     """Create factory with default configuration"""
0116 |     return ServiceFactory(
0117 |         enable_cache=settings.cache_enabled,
0118 |         log_level=settings.log_level
0119 |     )
0120 | 
0121 | # Factory con debug habilitado - para uso desde debugger
0122 | def create_debug_factory() -> ServiceFactory:
0123 |     """Create factory with debug enabled"""
0124 |     factory = create_factory()
0125 |     factory.enable_debug_mode()
0126 |     return factory
```

---

### application\use_cases.py

**Ruta:** `application\use_cases.py`

```py
0001 | # application/use_cases.py
0002 | import asyncio
0003 | import logging
0004 | from pathlib import Path
0005 | from typing import Optional, List
0006 | from datetime import datetime
0007 | 
0008 | from core.models import AnalysisReport, ScanResult, Vulnerability
0009 | from core.services.scanner import ScannerService
0010 | from core.services.triage import TriageService
0011 | from core.services.remediation import RemediationService
0012 | from core.services.reporter import ReporterService
0013 | from adapters.processing.chunker import OptimizedChunker
0014 | from shared.metrics import MetricsCollector
0015 | 
0016 | logger = logging.getLogger(__name__)
0017 | 
0018 | class AnalysisUseCase:
0019 |     """Caso de uso principal consolidado - sin duplicación"""
0020 |     
0021 |     def __init__(self,
0022 |                  scanner_service: ScannerService,
0023 |                  triage_service: Optional[TriageService] = None,
0024 |                  remediation_service: Optional[RemediationService] = None,
0025 |                  reporter_service: Optional[ReporterService] = None,
0026 |                  chunker: Optional[OptimizedChunker] = None,
0027 |                  metrics: Optional[MetricsCollector] = None):
0028 |         
0029 |         self.scanner_service = scanner_service
0030 |         self.triage_service = triage_service
0031 |         self.remediation_service = remediation_service
0032 |         self.reporter_service = reporter_service
0033 |         self.chunker = chunker
0034 |         self.metrics = metrics
0035 |     
0036 |     async def execute_full_analysis(self,
0037 |                                   file_path: str,
0038 |                                   output_file: Optional[str] = None,
0039 |                                   language: Optional[str] = None,
0040 |                                   tool_hint: Optional[str] = None,
0041 |                                   force_chunking: bool = False,
0042 |                                   disable_chunking: bool = False) -> AnalysisReport:
0043 |         """Execute complete security analysis pipeline"""
0044 |         
0045 |         start_time = asyncio.get_event_loop().time()
0046 |         
0047 |         try:
0048 |             logger.info(f"Starting complete analysis: {file_path}")
0049 |             
0050 |             # Phase 1: Scan and normalize vulnerabilities
0051 |             scan_result = await self.scanner_service.scan_file(
0052 |                 file_path=file_path,
0053 |                 language=language,
0054 |                 tool_hint=tool_hint
0055 |             )
0056 |             
0057 |             if not scan_result.vulnerabilities:
0058 |                 logger.info("No vulnerabilities found")
0059 |                 return self._create_clean_report(scan_result, start_time)
0060 |             
0061 |             # Phase 2: LLM Triage (if available)
0062 |             triage_result = None
0063 |             if self.triage_service:
0064 |                 triage_result = await self._perform_triage_analysis(
0065 |                     scan_result, language, force_chunking, disable_chunking
0066 |                 )
0067 |             
0068 |             # Phase 3: Generate remediation plans (if available)
0069 |             remediation_plans = []
0070 |             if self.remediation_service and triage_result:
0071 |                 confirmed_vulns = self._extract_confirmed_vulnerabilities(
0072 |                     scan_result.vulnerabilities, triage_result
0073 |                 )
0074 |                 if confirmed_vulns:
0075 |                     remediation_plans = await self.remediation_service.generate_remediation_plans(
0076 |                         confirmed_vulns, language
0077 |                     )
0078 |             
0079 |             # Phase 4: Create analysis report
0080 |             total_time = asyncio.get_event_loop().time() - start_time
0081 |             analysis_report = self._create_analysis_report(
0082 |                 scan_result, triage_result, remediation_plans, total_time,
0083 |                 force_chunking, disable_chunking, language, tool_hint
0084 |             )
0085 |             
0086 |             # Phase 5: Generate HTML report (if requested)
0087 |             if output_file and self.reporter_service:
0088 |                 await self.reporter_service.generate_html_report(analysis_report, output_file)
0089 |             
0090 |             # Record metrics
0091 |             if self.metrics:
0092 |                 self.metrics.record_complete_analysis(
0093 |                     file_path=file_path,
0094 |                     vulnerability_count=len(scan_result.vulnerabilities),
0095 |                     confirmed_count=len(remediation_plans),
0096 |                     total_time=total_time,
0097 |                     chunking_used=self._was_chunking_used(scan_result, force_chunking, disable_chunking),
0098 |                     language=language,
0099 |                     success=True
0100 |                 )
0101 |             
0102 |             logger.info(f"Analysis completed successfully in {total_time:.2f}s")
0103 |             return analysis_report
0104 |             
0105 |         except Exception as e:
0106 |             total_time = asyncio.get_event_loop().time() - start_time
0107 |             if self.metrics:
0108 |                 self.metrics.record_complete_analysis(
0109 |                     file_path=file_path,
0110 |                     total_time=total_time,
0111 |                     success=False,
0112 |                     error=str(e)
0113 |                 )
0114 |             logger.error(f"Analysis failed: {e}")
0115 |             raise
0116 |     
0117 |     async def execute_basic_analysis(self, file_path: str, output_file: Optional[str] = None,
0118 |                                    tool_hint: Optional[str] = None) -> AnalysisReport:
0119 |         """Execute basic analysis without LLM services"""
0120 |         
0121 |         start_time = asyncio.get_event_loop().time()
0122 |         
0123 |         logger.info(f"Starting basic analysis: {file_path}")
0124 |         
0125 |         # Only scan and normalize
0126 |         scan_result = await self.scanner_service.scan_file(
0127 |             file_path=file_path,
0128 |             tool_hint=tool_hint
0129 |         )
0130 |         
0131 |         total_time = asyncio.get_event_loop().time() - start_time
0132 |         
0133 |         # Create basic report
0134 |         analysis_report = AnalysisReport(
0135 |             scan_result=scan_result,
0136 |             triage_result=None,
0137 |             remediation_plans=[],
0138 |             analysis_config={"mode": "basic", "tool_hint": tool_hint},
0139 |             total_processing_time_seconds=total_time,
0140 |             chunking_enabled=False
0141 |         )
0142 |         
0143 |         # Generate HTML if requested
0144 |         if output_file and self.reporter_service:
0145 |             await self.reporter_service.generate_html_report(analysis_report, output_file)
0146 |         
0147 |         logger.info(f"Basic analysis completed in {total_time:.2f}s")
0148 |         return analysis_report
0149 |     
0150 |     async def _perform_triage_analysis(self, scan_result: ScanResult, language: Optional[str],
0151 |                                      force_chunking: bool, disable_chunking: bool):
0152 |         """Perform triage analysis with optional chunking"""
0153 |         
0154 |         should_chunk = (
0155 |             (self.chunker and self.chunker.should_chunk(scan_result) and not disable_chunking) 
0156 |             or force_chunking
0157 |         )
0158 |         
0159 |         if should_chunk and self.chunker:
0160 |             logger.info("Using chunked triage analysis")
0161 |             return await self._analyze_with_chunking(scan_result, language)
0162 |         else:
0163 |             logger.info("Using direct triage analysis")
0164 |             return await self.triage_service.analyze_vulnerabilities(
0165 |                 scan_result.vulnerabilities, language
0166 |             )
0167 |     
0168 |     async def _analyze_with_chunking(self, scan_result: ScanResult, language: Optional[str]):
0169 |         """Perform chunked analysis and consolidate results"""
0170 |         
0171 |         chunks = self.chunker.create_chunks(scan_result)
0172 |         logger.info(f"Processing {len(chunks)} chunks")
0173 |         
0174 |         # Process chunks with concurrency limit
0175 |         semaphore = asyncio.Semaphore(2)
0176 |         
0177 |         async def process_chunk(chunk):
0178 |             async with semaphore:
0179 |                 return await self.triage_service.analyze_vulnerabilities(
0180 |                     chunk.vulnerabilities, language, chunk.id
0181 |                 )
0182 |         
0183 |         # Execute chunk analysis
0184 |         chunk_results = await asyncio.gather(
0185 |             *[process_chunk(chunk) for chunk in chunks],
0186 |             return_exceptions=True
0187 |         )
0188 |         
0189 |         # Filter successful results
0190 |         successful_results = [r for r in chunk_results if not isinstance(r, Exception)]
0191 |         
0192 |         if not successful_results:
0193 |             raise Exception("All chunk analyses failed")
0194 |         
0195 |         # Consolidate results
0196 |         return self._consolidate_chunk_results(successful_results)
0197 |     
0198 |     def _consolidate_chunk_results(self, chunk_results):
0199 |         """Consolidate multiple chunk results into unified result"""
0200 |         
0201 |         all_decisions = []
0202 |         seen_ids = set()
0203 |         
0204 |         # Merge decisions avoiding duplicates from overlap
0205 |         for result in chunk_results:
0206 |             for decision in result.decisions:
0207 |                 if decision.vulnerability_id not in seen_ids:
0208 |                     all_decisions.append(decision)
0209 |                     seen_ids.add(decision.vulnerability_id)
0210 |         
0211 |         # Create consolidated summary
0212 |         summary = f"Consolidated analysis from {len(chunk_results)} chunks. "
0213 |         summary += f"Total decisions: {len(all_decisions)}. "
0214 |         
0215 |         from collections import Counter
0216 |         decision_counts = Counter(d.decision.value for d in all_decisions)
0217 |         summary += f"Distribution: {dict(decision_counts)}"
0218 |         
0219 |         from core.models import TriageResult
0220 |         return TriageResult(
0221 |             decisions=all_decisions,
0222 |             analysis_summary=summary,
0223 |             llm_analysis_time_seconds=sum(r.llm_analysis_time_seconds for r in chunk_results)
0224 |         )
0225 |     
0226 |     def _extract_confirmed_vulnerabilities(self, vulnerabilities: List[Vulnerability], 
0227 |                                          triage_result) -> List[Vulnerability]:
0228 |         """Extract confirmed vulnerabilities from triage result"""
0229 |         
0230 |         from core.models import AnalysisStatus
0231 |         confirmed_ids = {
0232 |             d.vulnerability_id for d in triage_result.decisions 
0233 |             if d.decision == AnalysisStatus.CONFIRMED
0234 |         }
0235 |         
0236 |         return [v for v in vulnerabilities if v.id in confirmed_ids]
0237 |     
0238 |     def _create_analysis_report(self, scan_result: ScanResult, triage_result, 
0239 |                               remediation_plans: List, total_time: float,
0240 |                               force_chunking: bool, disable_chunking: bool,
0241 |                               language: Optional[str], tool_hint: Optional[str]) -> AnalysisReport:
0242 |         """Create comprehensive analysis report"""
0243 |         
0244 |         chunking_used = self._was_chunking_used(scan_result, force_chunking, disable_chunking)
0245 |         
0246 |         return AnalysisReport(
0247 |             scan_result=scan_result,
0248 |             triage_result=triage_result,
0249 |             remediation_plans=remediation_plans,
0250 |             analysis_config={
0251 |                 "language": language,
0252 |                 "tool_hint": tool_hint,
0253 |                 "force_chunking": force_chunking,
0254 |                 "disable_chunking": disable_chunking,
0255 |                 "chunking_used": chunking_used,
0256 |                 "chunks_processed": len(self.chunker.create_chunks(scan_result)) if chunking_used else 0
0257 |             },
0258 |             total_processing_time_seconds=total_time,
0259 |             chunking_enabled=chunking_used
0260 |         )
0261 |     
0262 |     def _create_clean_report(self, scan_result: ScanResult, start_time: float) -> AnalysisReport:
0263 |         """Create report for files with no vulnerabilities"""
0264 |         
0265 |         total_time = asyncio.get_event_loop().time() - start_time
0266 |         
0267 |         return AnalysisReport(
0268 |             scan_result=scan_result,
0269 |             triage_result=None,
0270 |             remediation_plans=[],
0271 |             analysis_config={"no_vulnerabilities_found": True},
0272 |             total_processing_time_seconds=total_time,
0273 |             chunking_enabled=False
0274 |         )
0275 |     
0276 |     def _was_chunking_used(self, scan_result: ScanResult, force_chunking: bool, 
0277 |                           disable_chunking: bool) -> bool:
0278 |         """Determine if chunking was actually used - CORRECTED LOGIC"""
0279 |         
0280 |         # Prioridad 1: Si está deshabilitado explícitamente, nunca usar chunking
0281 |         if disable_chunking:
0282 |             logger.debug("Chunking disabled by flag")
0283 |             return False
0284 |         
0285 |         # Prioridad 2: Si está forzado explícitamente, siempre usar chunking
0286 |         # (siempre que haya vulnerabilidades y chunker esté disponible)
0287 |         if force_chunking:
0288 |             has_vulns = len(scan_result.vulnerabilities) > 0
0289 |             has_chunker = self.chunker is not None
0290 |             
0291 |             if has_chunker and has_vulns:
0292 |                 logger.debug("Chunking forced by flag")
0293 |                 return True
0294 |             else:
0295 |                 logger.warning(f"Chunking forced but not possible: "
0296 |                              f"chunker={has_chunker}, vulns={has_vulns}")
0297 |                 return False
0298 |         
0299 |         # Prioridad 3: Decisión automática basada en heurísticas
0300 |         if not self.chunker:
0301 |             logger.debug("Chunking not available (no chunker)")
0302 |             return False
0303 |         
0304 |         if len(scan_result.vulnerabilities) == 0:
0305 |             logger.debug("Chunking not needed (no vulnerabilities)")
0306 |             return False
0307 |         
0308 |         should_chunk = self.chunker.should_chunk(scan_result)
0309 |         logger.debug(f"Automatic chunking decision: {should_chunk}")
0310 |         
0311 |         return should_chunk
0312 | 
0313 | 
0314 | class CLIUseCase:
0315 |     """Caso de uso específico para CLI con manejo de errores robusto"""
0316 |     
0317 |     def __init__(self, analysis_use_case: AnalysisUseCase):
0318 |         self.analysis_use_case = analysis_use_case
0319 |     
0320 |     async def execute_cli_analysis(self,
0321 |                                   input_file: str,
0322 |                                   output_file: str = "security_report.html",
0323 |                                   language: Optional[str] = None,
0324 |                                   verbose: bool = False,
0325 |                                   disable_llm: bool = False,
0326 |                                   force_chunking: bool = False,
0327 |                                   min_cvss: float = 0.0,  # 🆕 AÑADIR ESTE PARÁMETRO
0328 |                                   severity_filter: Optional[List[str]] = None) -> bool:  # 🆕 AÑADIR ESTE PARÁMETRO
0329 |         """Execute analysis from CLI with comprehensive error handling"""
0330 |         
0331 |         try:
0332 |             # Validate input file
0333 |             input_path = Path(input_file)
0334 |             if not input_path.exists():
0335 |                 print(f"❌ Error: Input file not found: {input_file}")
0336 |                 return False
0337 |             
0338 |             print(f"🔍 Analyzing: {input_path.name}")
0339 |             
0340 |             # 🆕 Show filter info
0341 |             if min_cvss > 0.0:
0342 |                 print(f"🎯 Applying CVSS filter: >= {min_cvss}")
0343 |             if severity_filter:
0344 |                 print(f"📊 Applying severity filter: {', '.join(severity_filter)}")
0345 |             
0346 |             # Execute appropriate analysis
0347 |             if disable_llm:
0348 |                 result = await self.analysis_use_case.execute_basic_analysis(
0349 |                     input_file, output_file
0350 |                 )
0351 |                 print("✅ Basic analysis completed")
0352 |             else:
0353 |                 result = await self.analysis_use_case.execute_full_analysis(
0354 |                     file_path=input_file,
0355 |                     output_file=output_file,
0356 |                     language=language,
0357 |                     force_chunking=force_chunking
0358 |                     # 🆕 Nota: min_cvss y severity_filter se aplicarían aquí si los implementas
0359 |                 )
0360 |                 print("✅ Full analysis completed")
0361 |             
0362 |             # Display results
0363 |             self._display_results(result, output_file)
0364 |             return True
0365 |             
0366 |         except KeyboardInterrupt:
0367 |             print("\n🛑 Analysis interrupted by user")
0368 |             return False
0369 |         except Exception as e:
0370 |             print(f"\n❌ Analysis failed: {e}")
0371 |             if verbose:
0372 |                 import traceback
0373 |                 traceback.print_exc()
0374 |             return False
0375 |     
0376 |     def _display_results(self, result: AnalysisReport, output_file: str) -> None:
0377 |         """Display analysis results in CLI format"""
0378 |         
0379 |         print("\n" + "="*50)
0380 |         print("📊 ANALYSIS RESULTS")
0381 |         print("="*50)
0382 |         
0383 |         # Basic statistics
0384 |         scan_result = result.scan_result
0385 |         print(f"📁 File: {scan_result.file_info['filename']}")
0386 |         print(f"🔢 Total vulnerabilities: {len(scan_result.vulnerabilities)}")
0387 |         
0388 |         # Deduplication stats
0389 |         if 'duplicates_removed' in scan_result.file_info:
0390 |             dups = scan_result.file_info['duplicates_removed']
0391 |             if dups > 0:
0392 |                 print(f"🔄 Duplicates removed: {dups}")
0393 |         
0394 |         if scan_result.vulnerabilities:
0395 |             severity_dist = scan_result.severity_distribution
0396 |             print("\n📊 Severity Distribution:")
0397 |             for severity, count in severity_dist.items():
0398 |                 if count > 0:
0399 |                     icon = {"CRÍTICA": "🔥", "ALTA": "⚡", "MEDIA": "⚠️", "BAJA": "📝", "INFO": "ℹ️"}
0400 |                     print(f"  {icon.get(severity, '•')} {severity}: {count}")
0401 |         
0402 |         # Triage results
0403 |         if result.triage_result:
0404 |             triage = result.triage_result
0405 |             print(f"\n🤖 LLM Analysis:")
0406 |             print(f"  ✅ Confirmed: {triage.confirmed_count}")
0407 |             print(f"  ❌ False positives: {triage.false_positive_count}")
0408 |             print(f"  🔍 Need review: {triage.needs_review_count}")
0409 |         
0410 |         # Remediation plans
0411 |         if result.remediation_plans:
0412 |             print(f"\n🛠️  Remediation plans: {len(result.remediation_plans)}")
0413 |             priority_counts = {}
0414 |             for plan in result.remediation_plans:
0415 |                 priority_counts[plan.priority_level] = priority_counts.get(plan.priority_level, 0) + 1
0416 |             
0417 |             for priority in ["immediate", "high", "medium", "low"]:
0418 |                 count = priority_counts.get(priority, 0)
0419 |                 if count > 0:
0420 |                     icons = {"immediate": "🚨", "high": "⚡", "medium": "⚠️", "low": "📝"}
0421 |                     print(f"  {icons[priority]} {priority.title()}: {count}")
0422 |         
0423 |         # Performance metrics
0424 |         print(f"\n⏱️  Processing time: {result.total_processing_time_seconds:.2f}s")
0425 |         if result.chunking_enabled:
0426 |             print("🧩 Chunking: Enabled")
0427 |         
0428 |         # Output file
0429 |         if Path(output_file).exists():
0430 |             size_kb = Path(output_file).stat().st_size / 1024
0431 |             print(f"\n📄 Report generated: {output_file} ({size_kb:.1f} KB)")
0432 |         
0433 |         print("\n💡 Open the HTML file in your browser to view the detailed report")```

---

### application\__init__.py

**Ruta:** `application\__init__.py`

```py
```

---

### core\exceptions.py

**Ruta:** `core\exceptions.py`

```py
0001 | # core/exceptions.py
0002 | """Excepciones específicas del dominio"""
0003 | class SecurityAnalysisError(Exception):
0004 |     """Excepción base del sistema"""
0005 |     def __init__(self, message: str, details: dict = None):
0006 |         self.message = message
0007 |         self.details = details or {}
0008 |         super().__init__(self.message)
0009 | class ValidationError(SecurityAnalysisError):
0010 |     """Error de validación de datos"""
0011 |     pass
0012 | class ParsingError(SecurityAnalysisError):
0013 |     """Error de parsing de vulnerabilidades"""
0014 |     pass
0015 | class LLMError(SecurityAnalysisError):
0016 |     """Error del proveedor LLM"""
0017 |     pass
0018 | class ChunkingError(SecurityAnalysisError):
0019 |     """Error en el proceso de chunking"""
0020 |     pass```

---

### core\models.py

**Ruta:** `core\models.py`

```py
0001 | # core/models.py
0002 | from pydantic import BaseModel, Field, field_validator, computed_field
0003 | from typing import List, Optional, Dict, Any, Union
0004 | from datetime import datetime
0005 | from enum import Enum
0006 | 
0007 | # === ENUMS CONSOLIDADOS ===
0008 | class SeverityLevel(str, Enum):
0009 |     CRITICAL = "CRÍTICA"
0010 |     HIGH = "ALTA"
0011 |     MEDIUM = "MEDIA"
0012 |     LOW = "BAJA"
0013 |     INFO = "INFO"
0014 |     
0015 | class VulnerabilityType(str, Enum):
0016 |     SQL_INJECTION = "SQL Injection"
0017 |     XSS = "Cross-Site Scripting"
0018 |     PATH_TRAVERSAL = "Directory Traversal"
0019 |     CODE_INJECTION = "Code Injection"
0020 |     AUTH_BYPASS = "Authentication Bypass"
0021 |     BROKEN_ACCESS_CONTROL = "Broken Access Control"
0022 |     INSECURE_CRYPTO = "Insecure Cryptography"
0023 |     SENSITIVE_DATA_EXPOSURE = "Sensitive Data Exposure"
0024 |     SECURITY_MISCONFIGURATION = "Security Misconfiguration"
0025 |     OTHER = "Other Security Issue"
0026 | 
0027 | class AnalysisStatus(str, Enum):
0028 |     CONFIRMED = "confirmed"
0029 |     FALSE_POSITIVE = "false_positive"
0030 |     NEEDS_MANUAL_REVIEW = "needs_manual_review"
0031 | 
0032 | class LLMProvider(str, Enum):
0033 |     OPENAI = "openai"
0034 |     WATSONX = "watsonx"
0035 | 
0036 | class ChunkingStrategy(str, Enum):
0037 |     NO_CHUNKING = "no_chunking"
0038 |     BY_COUNT = "by_vulnerability_count"
0039 |     BY_SIZE = "by_size"
0040 |     ADAPTIVE = "adaptive"
0041 | 
0042 | class Vulnerability(BaseModel):
0043 |     """Modelo central optimizado de vulnerabilidad"""
0044 |     id: str = Field(..., description="ID único de la vulnerabilidad")
0045 |     type: VulnerabilityType
0046 |     severity: SeverityLevel
0047 |     title: str = Field(..., min_length=1)
0048 |     description: str = Field(..., min_length=10)
0049 |     
0050 |     # Ubicación
0051 |     file_path: str = Field(..., min_length=1)
0052 |     line_number: int = Field(ge=0, default=0)
0053 |     code_snippet: Optional[str] = None
0054 |     
0055 |     # Metadatos de seguridad
0056 |     cwe_id: Optional[str] = Field(None, pattern=r"^CWE-\d+$")
0057 |     confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
0058 |     
0059 |     # Origen
0060 |     source_tool: Optional[str] = None
0061 |     rule_id: Optional[str] = None
0062 |     
0063 |     # Contexto adicional
0064 |     impact_description: Optional[str] = None
0065 |     remediation_advice: Optional[str] = None
0066 |     
0067 |     # Metadatos
0068 |     created_at: datetime = Field(default_factory=datetime.now)
0069 |     meta: Dict[str, Any] = Field(default_factory=dict)
0070 |     
0071 |     @field_validator('severity', mode='before')
0072 |     @classmethod
0073 |     def normalize_severity(cls, v):
0074 |         """Normalización inteligente de severidad"""
0075 |         if isinstance(v, str):
0076 |             mapping = {
0077 |                 'CRITICAL': SeverityLevel.CRITICAL, 'HIGH': SeverityLevel.HIGH,
0078 |                 'MEDIUM': SeverityLevel.MEDIUM, 'LOW': SeverityLevel.LOW,
0079 |                 'INFO': SeverityLevel.INFO, 'BLOCKER': SeverityLevel.CRITICAL,
0080 |                 'MAJOR': SeverityLevel.HIGH, 'MINOR': SeverityLevel.MEDIUM,
0081 |                 'CRÍTICA': SeverityLevel.CRITICAL, 'ALTA': SeverityLevel.HIGH,
0082 |                 'MEDIA': SeverityLevel.MEDIUM, 'BAJA': SeverityLevel.LOW
0083 |             }
0084 |             return mapping.get(v.upper(), SeverityLevel.MEDIUM)
0085 |         return v
0086 |     
0087 |     @computed_field
0088 |     @property
0089 |     def priority_score(self) -> int:
0090 |         """Score para ordenamiento por prioridad"""
0091 |         base_score = {
0092 |             SeverityLevel.CRITICAL: 100, SeverityLevel.HIGH: 80,
0093 |             SeverityLevel.MEDIUM: 60, SeverityLevel.LOW: 40, SeverityLevel.INFO: 20
0094 |         }[self.severity]
0095 |         
0096 |         # Ajustar por confianza
0097 |         if self.confidence_level:
0098 |             base_score = int(base_score * self.confidence_level)
0099 |         
0100 |         return base_score
0101 |     
0102 |     @computed_field
0103 |     @property
0104 |     def is_high_priority(self) -> bool:
0105 |         """Determinar si es alta prioridad"""
0106 |         return self.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
0107 | 
0108 | class TriageDecision(BaseModel):
0109 |     """Decisión de triaje optimizada"""
0110 |     vulnerability_id: str
0111 |     decision: AnalysisStatus
0112 |     confidence_score: float = Field(ge=0.0, le=1.0)
0113 |     reasoning: str = Field(..., min_length=10)
0114 |     llm_model_used: str
0115 |     analyzed_at: datetime = Field(default_factory=datetime.now)
0116 | 
0117 | class TriageResult(BaseModel):
0118 |     """Resultado de triaje con validación automática"""
0119 |     decisions: List[TriageDecision] = Field(default_factory=list)
0120 |     analysis_summary: str
0121 |     llm_analysis_time_seconds: float = Field(ge=0.0)
0122 |     
0123 |     @computed_field
0124 |     @property
0125 |     def total_analyzed(self) -> int:
0126 |         return len(self.decisions)
0127 |     
0128 |     @computed_field
0129 |     @property
0130 |     def confirmed_count(self) -> int:
0131 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.CONFIRMED)
0132 |     
0133 |     @computed_field
0134 |     @property
0135 |     def false_positive_count(self) -> int:
0136 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.FALSE_POSITIVE)
0137 |     
0138 |     @computed_field
0139 |     @property
0140 |     def needs_review_count(self) -> int:
0141 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.NEEDS_MANUAL_REVIEW)
0142 | 
0143 | class RemediationStep(BaseModel):
0144 |     """Paso de remediación optimizado"""
0145 |     step_number: int = Field(ge=1)
0146 |     title: str = Field(..., min_length=1)
0147 |     description: str = Field(..., min_length=10)
0148 |     code_example: Optional[str] = None
0149 |     estimated_minutes: Optional[int] = Field(None, ge=1)
0150 |     difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
0151 |     tools_required: List[str] = Field(default_factory=list)
0152 |     
0153 | class RemediationPlan(BaseModel):
0154 |     vulnerability_id: str
0155 |     vulnerability_type: VulnerabilityType
0156 |     priority_level: str
0157 |     estimated_effort: Optional[str] = None
0158 |     risk_if_not_fixed: Optional[str] = "Security vulnerability should be remediated to prevent potential exploitation."  # ✨ Default value
0159 |     steps: List[RemediationStep]
0160 |     llm_model_used: Optional[str] = "meta-llama/llama-3-3-70b-instruct"
0161 | 
0162 | class RemediationPlan(BaseModel):
0163 |     """Plan de remediación consolidado"""
0164 |     vulnerability_id: str
0165 |     vulnerability_type: VulnerabilityType
0166 |     priority_level: str = Field(..., pattern=r"^(immediate|high|medium|low)$")
0167 |     estimated_effort: float = Field(ge=0.0, le=10.0, default=5.0)
0168 |     complexity_score: float = Field(ge=0.0, le=10.0, default=5.0)
0169 |     steps: List[RemediationStep] = Field(..., min_length=1)
0170 |     risk_if_not_fixed: Optional[str]= "Security vulnerability should be remediated to prevent potential exploitation."  # ✨ Default value
0171 |     references: List[str] = Field(default_factory=list)
0172 |     llm_model_used: str
0173 |     created_at: datetime = Field(default_factory=datetime.now)
0174 | 
0175 | class ScanResult(BaseModel):
0176 |     """Resultado de escaneo optimizado"""
0177 |     file_info: Dict[str, Any]
0178 |     vulnerabilities: List[Vulnerability] = Field(default_factory=list)
0179 |     scan_timestamp: datetime = Field(default_factory=datetime.now)
0180 |     scan_duration_seconds: float = Field(ge=0.0, default=0.0)
0181 |     language_detected: Optional[str] = None
0182 |     
0183 |     @computed_field
0184 |     @property
0185 |     def vulnerability_count(self) -> int:
0186 |         return len(self.vulnerabilities)
0187 |     
0188 |     @computed_field
0189 |     @property
0190 |     def severity_distribution(self) -> Dict[str, int]:
0191 |         from collections import Counter
0192 |         return dict(Counter(v.severity.value for v in self.vulnerabilities))
0193 |     
0194 |     @computed_field
0195 |     @property
0196 |     def high_priority_count(self) -> int:
0197 |         return sum(1 for v in self.vulnerabilities if v.is_high_priority)
0198 | 
0199 | class AnalysisReport(BaseModel):
0200 |     """Reporte de análisis completo"""
0201 |     report_id: str = Field(default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
0202 |     generated_at: datetime = Field(default_factory=datetime.now)
0203 |     scan_result: ScanResult
0204 |     triage_result: Optional[TriageResult] = None
0205 |     remediation_plans: List[RemediationPlan] = Field(default_factory=list)
0206 |     analysis_config: Dict[str, Any] = Field(default_factory=dict)
0207 |     total_processing_time_seconds: float = Field(ge=0.0)
0208 |     chunking_enabled: bool = False
0209 |     
0210 |     @computed_field
0211 |     @property
0212 |     def executive_summary(self) -> Dict[str, Any]:
0213 |         """Resumen ejecutivo automático"""
0214 |         return {
0215 |             "total_vulnerabilities": self.scan_result.vulnerability_count,
0216 |             "high_priority_count": self.scan_result.high_priority_count,
0217 |             "severity_distribution": self.scan_result.severity_distribution,
0218 |             "processing_time": f"{self.total_processing_time_seconds:.2f}s",
0219 |             "confirmed_vulnerabilities": self.triage_result.confirmed_count if self.triage_result else 0,
0220 |             "remediation_plans_generated": len(self.remediation_plans)
0221 |         }
```

---

### core\__init__.py

**Ruta:** `core\__init__.py`

```py
```

---

### core\services\remediation.py

**Ruta:** `core\services\remediation.py`

```py
0001 | # core/services/remediation.py
0002 | import logging
0003 | import asyncio
0004 | from typing import List, Optional, Dict
0005 | from collections import defaultdict
0006 | 
0007 | from ..models import Vulnerability, RemediationPlan, RemediationStep, VulnerabilityType
0008 | from ..exceptions import LLMError
0009 | from infrastructure.llm.client import LLMClient
0010 | from shared.metrics import MetricsCollector
0011 | 
0012 | logger = logging.getLogger(__name__)
0013 | 
0014 | class RemediationService:
0015 |     """Servicio de remediación optimizado sin duplicación"""
0016 |     
0017 |     def __init__(self, llm_client: LLMClient, metrics: Optional[MetricsCollector] = None):
0018 |         self.llm_client = llm_client
0019 |         self.metrics = metrics
0020 |     
0021 |     async def generate_remediation_plans(self, 
0022 |                                        confirmed_vulnerabilities: List[Vulnerability],
0023 |                                        language: Optional[str] = None) -> List[RemediationPlan]:
0024 |         """Generate remediation plans for confirmed vulnerabilities"""
0025 |         
0026 |         if not confirmed_vulnerabilities:
0027 |             logger.info("No confirmed vulnerabilities - no plans needed")
0028 |             return []
0029 |         
0030 |         logger.info(f"Generating remediation plans for {len(confirmed_vulnerabilities)} vulnerabilities")
0031 |         
0032 |         # Group by type for efficient batch processing
0033 |         grouped_vulns = self._group_by_type(confirmed_vulnerabilities)
0034 |         
0035 |         all_plans = []
0036 |         for vuln_type, vulns in grouped_vulns.items():
0037 |             try:
0038 |                 plans = await self._generate_plans_for_type(vuln_type, vulns, language)
0039 |                 all_plans.extend(plans)
0040 |             except Exception as e:
0041 |                 logger.error(f"Failed to generate plans for {vuln_type}: {e}")
0042 |                 # Add fallback plans
0043 |                 fallback_plans = self._create_fallback_plans(vulns)
0044 |                 all_plans.extend(fallback_plans)
0045 |         
0046 |         # Sort by priority
0047 |         prioritized_plans = self._prioritize_plans(all_plans)
0048 |         
0049 |         logger.info(f"Generated {len(prioritized_plans)} remediation plans")
0050 |         return prioritized_plans
0051 |     
0052 |     def _group_by_type(self, vulnerabilities: List[Vulnerability]) -> Dict[VulnerabilityType, List[Vulnerability]]:
0053 |         """Group vulnerabilities by type for batch processing"""
0054 |         groups = defaultdict(list)
0055 |         for vuln in vulnerabilities:
0056 |             groups[vuln.type].append(vuln)
0057 |         return dict(groups)
0058 |     
0059 |     async def _generate_plans_for_type(self, vuln_type: VulnerabilityType, 
0060 |                                      vulnerabilities: List[Vulnerability],
0061 |                                      language: Optional[str]) -> List[RemediationPlan]:
0062 |         """Generate plans for specific vulnerability type"""
0063 |         
0064 |         start_time = asyncio.get_event_loop().time()
0065 |         
0066 |         try:
0067 |             # Prepare remediation request
0068 |             request = self._prepare_remediation_request(vuln_type, vulnerabilities, language)
0069 |             
0070 |             # Get LLM response
0071 |             response = await self.llm_client.generate_remediation_plan(request)
0072 |             
0073 |             # Create individual plans from response
0074 |             plans = self._create_individual_plans(response, vulnerabilities)
0075 |             
0076 |             # Record metrics
0077 |             if self.metrics:
0078 |                 generation_time = asyncio.get_event_loop().time() - start_time
0079 |                 self.metrics.record_remediation_generation(
0080 |                     vuln_type.value, len(vulnerabilities), generation_time, True
0081 |                 )
0082 |             
0083 |             return plans
0084 |         
0085 |         except Exception as e:
0086 |             if self.metrics:
0087 |                 generation_time = asyncio.get_event_loop().time() - start_time
0088 |                 self.metrics.record_remediation_generation(
0089 |                     vuln_type.value, len(vulnerabilities), generation_time, False, str(e)
0090 |                 )
0091 |             raise
0092 |     
0093 |     def _prepare_remediation_request(self, vuln_type: VulnerabilityType, 
0094 |                                    vulnerabilities: List[Vulnerability],
0095 |                                    language: Optional[str]) -> str:
0096 |         """Prepare structured remediation request"""
0097 |         
0098 |         header = f"# REMEDIATION PLAN REQUEST\n"
0099 |         header += f"Vulnerability Type: {vuln_type.value}\n"
0100 |         header += f"Language: {language or 'Unknown'}\n"
0101 |         header += f"Count: {len(vulnerabilities)}\n\n"
0102 |         
0103 |         vuln_details = []
0104 |         for i, vuln in enumerate(vulnerabilities, 1):
0105 |             detail = f"""## VULNERABILITY {i} - {vuln.id}
0106 | - Severity: {vuln.severity.value}
0107 | - File: {vuln.file_path}:{vuln.line_number}
0108 | - Title: {vuln.title}
0109 | - Description: {vuln.description}"""
0110 |             
0111 |             if vuln.code_snippet:
0112 |                 detail += f"\n- Code Context:\n{vuln.code_snippet[:500]}"
0113 |             
0114 |             vuln_details.append(detail)
0115 |         
0116 |         return header + "\n\n".join(vuln_details)
0117 |     
0118 |     def _create_individual_plans(self, template_plan: RemediationPlan, 
0119 |                                vulnerabilities: List[Vulnerability]) -> List[RemediationPlan]:
0120 |         """Create individual plans from template"""
0121 |         
0122 |         individual_plans = []
0123 |         for vuln in vulnerabilities:
0124 |             # Customize plan for specific vulnerability
0125 |             customized_plan = RemediationPlan(
0126 |                 vulnerability_id=vuln.id,
0127 |                 vulnerability_type=vuln.type,
0128 |                 priority_level=self._calculate_priority(vuln),
0129 |                 steps=self._customize_steps(template_plan.steps, vuln),
0130 |                 risk_if_not_fixed=template_plan.risk_if_not_fixed,
0131 |                 references=template_plan.references,
0132 |                 total_estimated_hours=template_plan.total_estimated_hours,
0133 |                 complexity_score=self._adjust_complexity(template_plan.complexity_score, vuln),
0134 |                 llm_model_used=template_plan.llm_model_used
0135 |             )
0136 |             individual_plans.append(customized_plan)
0137 |         
0138 |         return individual_plans
0139 |     
0140 |     def _calculate_priority(self, vulnerability: Vulnerability) -> str:
0141 |         """Calculate priority level based on vulnerability characteristics"""
0142 |         priority_map = {
0143 |             "CRÍTICA": "immediate",
0144 |             "ALTA": "high", 
0145 |             "MEDIA": "medium",
0146 |             "BAJA": "low",
0147 |             "INFO": "low"
0148 |         }
0149 |         return priority_map.get(vulnerability.severity.value, "medium")
0150 |     
0151 |     def _customize_steps(self, template_steps: List[RemediationStep], 
0152 |                         vulnerability: Vulnerability) -> List[RemediationStep]:
0153 |         """Customize remediation steps for specific vulnerability"""
0154 |         
0155 |         customized_steps = []
0156 |         for step in template_steps:
0157 |             try:
0158 |                 # Intentar formatear con placeholders
0159 |                 formatted_title = step.title.format(
0160 |                     file=vulnerability.file_path,
0161 |                     line=vulnerability.line_number,
0162 |                     vuln_type=vulnerability.type.value
0163 |                 )
0164 |                 formatted_description = step.description.format(
0165 |                     vulnerability_id=vulnerability.id,
0166 |                     file_path=vulnerability.file_path,
0167 |                     severity=vulnerability.severity.value
0168 |                 )
0169 |             except KeyError as e:
0170 |                 # Si no hay placeholders, usar texto original
0171 |                 logger.debug(f"No format placeholders in step {step.step_number}: {e}")
0172 |                 formatted_title = step.title
0173 |                 formatted_description = step.description
0174 |             
0175 |             customized_step = RemediationStep(
0176 |                 step_number=step.step_number,
0177 |                 title=formatted_title,
0178 |                 description=formatted_description,
0179 |                 code_example=step.code_example,
0180 |                 estimated_minutes=step.estimated_minutes,
0181 |                 difficulty=step.difficulty,
0182 |                 tools_required=step.tools_required
0183 |             )
0184 |             customized_steps.append(customized_step)
0185 |         
0186 |         return customized_steps
0187 |     
0188 |     def _adjust_complexity(self, base_complexity: float, vulnerability: Vulnerability) -> float:
0189 |         """Adjust complexity based on vulnerability characteristics"""
0190 |         
0191 |         # Adjust based on severity
0192 |         severity_multipliers = {
0193 |             "CRÍTICA": 1.2,
0194 |             "ALTA": 1.1,
0195 |             "MEDIA": 1.0,
0196 |             "BAJA": 0.9,
0197 |             "INFO": 0.8
0198 |         }
0199 |         
0200 |         multiplier = severity_multipliers.get(vulnerability.severity.value, 1.0)
0201 |         adjusted = base_complexity * multiplier
0202 |         
0203 |         return min(max(adjusted, 1.0), 10.0)  # Clamp to 1-10 range
0204 |     
0205 |     def _create_fallback_plans(self, vulnerabilities: List[Vulnerability]) -> List[RemediationPlan]:
0206 |         """Create basic fallback plans when LLM fails"""
0207 |         
0208 |         logger.warning("Creating fallback remediation plans")
0209 |         
0210 |         fallback_plans = []
0211 |         for vuln in vulnerabilities:
0212 |             basic_steps = [
0213 |                 RemediationStep(
0214 |                     step_number=1,
0215 |                     title="Manual Security Review",
0216 |                     description=f"Manually review {vuln.type.value} vulnerability in {vuln.file_path}",
0217 |                     estimated_minutes=30,
0218 |                     difficulty="medium"
0219 |                 ),
0220 |                 RemediationStep(
0221 |                     step_number=2,
0222 |                     title="Research Best Practices", 
0223 |                     description=f"Research security best practices for {vuln.type.value}",
0224 |                     estimated_minutes=15,
0225 |                     difficulty="easy"
0226 |                 ),
0227 |                 RemediationStep(
0228 |                     step_number=3,
0229 |                     title="Implement Fix",
0230 |                     description="Apply appropriate security fix based on research",
0231 |                     estimated_minutes=120,
0232 |                     difficulty="hard"
0233 |                 ),
0234 |                 RemediationStep(
0235 |                     step_number=4,
0236 |                     title="Validate Fix",
0237 |                     description="Test that vulnerability has been properly addressed",
0238 |                     estimated_minutes=30,
0239 |                     difficulty="medium"
0240 |                 )
0241 |             ]
0242 |             
0243 |             plan = RemediationPlan(
0244 |                 vulnerability_id=vuln.id,
0245 |                 vulnerability_type=vuln.type,
0246 |                 priority_level=self._calculate_priority(vuln),
0247 |                 steps=basic_steps,
0248 |                 risk_if_not_fixed=f"Security risk associated with {vuln.type.value}",
0249 |                 total_estimated_hours=3.25,
0250 |                 complexity_score=5.0,
0251 |                 llm_model_used="fallback"
0252 |             )
0253 |             
0254 |             fallback_plans.append(plan)
0255 |         
0256 |         return fallback_plans
0257 |     
0258 |     def _prioritize_plans(self, plans: List[RemediationPlan]) -> List[RemediationPlan]:
0259 |         """Sort plans by priority and complexity"""
0260 |         
0261 |         priority_weights = {"immediate": 4, "high": 3, "medium": 2, "low": 1}
0262 |         
0263 |         return sorted(plans, key=lambda p: (
0264 |             priority_weights.get(p.priority_level, 0),
0265 |             -p.complexity_score  # Lower complexity = higher priority
0266 |         ), reverse=True)
```

---

### core\services\reporter.py

**Ruta:** `core\services\reporter.py`

```py
0001 | # core/services/reporter.py
0002 | import logging
0003 | from pathlib import Path
0004 | from typing import Optional
0005 | 
0006 | from ..models import AnalysisReport
0007 | from adapters.output.html_generator import OptimizedHTMLGenerator
0008 | from shared.metrics import MetricsCollector
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | class ReporterService:
0013 |     """Servicio de reportes simplificado y optimizado"""
0014 |     
0015 |     def __init__(self, 
0016 |                  html_generator: Optional[OptimizedHTMLGenerator] = None,
0017 |                  metrics: Optional[MetricsCollector] = None):
0018 |         self.html_generator = html_generator or OptimizedHTMLGenerator()
0019 |         self.metrics = metrics
0020 |     
0021 |     async def generate_html_report(self, 
0022 |                                  analysis_report: AnalysisReport,
0023 |                                  output_file: str) -> bool:
0024 |         """Generate HTML report with metrics tracking"""
0025 |         
0026 |         try:
0027 |             logger.info(f"Generating HTML report: {output_file}")
0028 |             
0029 |             success = self.html_generator.generate_report(analysis_report, output_file)
0030 |             
0031 |             if success:
0032 |                 file_size = Path(output_file).stat().st_size
0033 |                 if self.metrics:
0034 |                     self.metrics.record_report_generation(
0035 |                         "html", file_size, len(analysis_report.scan_result.vulnerabilities), True
0036 |                     )
0037 |                 logger.info(f"Report generated successfully: {output_file} ({file_size:,} bytes)")
0038 |             else:
0039 |                 if self.metrics:
0040 |                     self.metrics.record_report_generation("html", success=False)
0041 |                 logger.error(f"Failed to generate report: {output_file}")
0042 |             
0043 |             return success
0044 |             
0045 |         except Exception as e:
0046 |             if self.metrics:
0047 |                 self.metrics.record_report_generation("html", success=False, error=str(e))
0048 |             logger.error(f"Report generation failed: {e}")
0049 |             return False
```

---

### core\services\scanner.py

**Ruta:** `core\services\scanner.py`

```py
0001 | # core/services/scanner.py
0002 | import json
0003 | import logging
0004 | from pathlib import Path
0005 | from typing import Optional, Dict, Any, List, Tuple
0006 | from datetime import datetime
0007 | 
0008 | from ..models import ScanResult, Vulnerability, VulnerabilityType, SeverityLevel
0009 | from ..exceptions import ValidationError, ParsingError
0010 | 
0011 | logger = logging.getLogger(__name__)
0012 | 
0013 | class DuplicateDetector:
0014 |     """
0015 |     🔄 Intelligent duplicate detection system
0016 |     
0017 |     Strategies:
0018 |     - strict: Exact match (file, line, type, description hash)
0019 |     - moderate: Similar location and type (default)
0020 |     - loose: Fuzzy matching on type and description
0021 |     """
0022 |     
0023 |     def __init__(self, strategy: str = 'moderate'):
0024 |         self.strategy = strategy
0025 |         logger.info(f"🔄 Duplicate detector initialized: strategy={strategy}")
0026 |     
0027 |     def remove_duplicates(self, vulnerabilities: List[Vulnerability]) -> tuple[List[Vulnerability], int]:
0028 |         """Remove duplicates, returns (unique_list, removed_count)"""
0029 |         if not vulnerabilities or len(vulnerabilities) <= 1:
0030 |             return vulnerabilities, 0
0031 |         
0032 |         original_count = len(vulnerabilities)
0033 |         logger.info(f"🔍 Checking {original_count} vulnerabilities for duplicates ({self.strategy})")
0034 |         
0035 |         if self.strategy == 'strict':
0036 |             unique = self._dedup_strict(vulnerabilities)
0037 |         elif self.strategy == 'loose':
0038 |             unique = self._dedup_loose(vulnerabilities)
0039 |         else:  # moderate
0040 |             unique = self._dedup_moderate(vulnerabilities)
0041 |         
0042 |         removed = original_count - len(unique)
0043 |         if removed > 0:
0044 |             logger.info(f"✅ Removed {removed} duplicates, kept {len(unique)} unique")
0045 |         
0046 |         return unique, removed
0047 |     
0048 |     def _dedup_strict(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
0049 |         """Exact match on file+line+type+description"""
0050 |         seen: set = set()
0051 |         unique = []
0052 |         
0053 |         for vuln in vulnerabilities:
0054 |             sig = f"{vuln.file_path}|{vuln.line_number}|{vuln.type.value}|{hash(vuln.description)}"
0055 |             if sig not in seen:
0056 |                 seen.add(sig)
0057 |                 unique.append(vuln)
0058 |         
0059 |         return unique
0060 |     
0061 |     def _dedup_moderate(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
0062 |         """Same file+type, nearby location (±5 lines), similar description"""
0063 |         from collections import defaultdict
0064 |         
0065 |         groups = defaultdict(list)
0066 |         for vuln in vulnerabilities:
0067 |             key = (vuln.file_path, vuln.type.value)
0068 |             groups[key].append(vuln)
0069 |         
0070 |         unique = []
0071 |         for group_vulns in groups.values():
0072 |             group_vulns.sort(key=lambda v: v.line_number)
0073 |             kept = []
0074 |             
0075 |             for vuln in group_vulns:
0076 |                 is_dup = False
0077 |                 for kept_vuln in kept:
0078 |                     if abs(vuln.line_number - kept_vuln.line_number) <= 5:
0079 |                         similarity = self._similarity(vuln.description, kept_vuln.description)
0080 |                         if similarity > 0.8:
0081 |                             is_dup = True
0082 |                             break
0083 |                 
0084 |                 if not is_dup:
0085 |                     kept.append(vuln)
0086 |             
0087 |             unique.extend(kept)
0088 |         
0089 |         return unique
0090 |     
0091 |     def _dedup_loose(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
0092 |         """Same type, similar description (70%+)"""
0093 |         from collections import defaultdict
0094 |         
0095 |         groups = defaultdict(list)
0096 |         for vuln in vulnerabilities:
0097 |             groups[vuln.type.value].append(vuln)
0098 |         
0099 |         unique = []
0100 |         for group_vulns in groups.values():
0101 |             kept = []
0102 |             for vuln in group_vulns:
0103 |                 is_dup = False
0104 |                 for kept_vuln in kept:
0105 |                     if self._similarity(vuln.description, kept_vuln.description) > 0.7:
0106 |                         is_dup = True
0107 |                         break
0108 |                 
0109 |                 if not is_dup:
0110 |                     kept.append(vuln)
0111 |             
0112 |             unique.extend(kept)
0113 |         
0114 |         return unique
0115 |     
0116 |     def _similarity(self, text1: str, text2: str) -> float:
0117 |         """Simple Jaccard similarity"""
0118 |         if text1 == text2:
0119 |             return 1.0
0120 |         
0121 |         tokens1 = set(text1.lower().split())
0122 |         tokens2 = set(text2.lower().split())
0123 |         
0124 |         if not tokens1 or not tokens2:
0125 |             return 0.0
0126 |         
0127 |         intersection = len(tokens1 & tokens2)
0128 |         union = len(tokens1 | tokens2)
0129 |         
0130 |         return intersection / union if union > 0 else 0.0
0131 | 
0132 | 
0133 | class UnifiedVulnerabilityParser:
0134 |     """Parser unificado que maneja múltiples formatos"""
0135 |     
0136 |     def parse(self, data: Dict[str, Any], tool_hint: Optional[str] = None) -> List[Vulnerability]:
0137 |         """Parse vulnerabilities from any supported format"""
0138 |         
0139 |         # Extract findings from different structures
0140 |         findings = self._extract_findings(data)
0141 |         if not findings:
0142 |             logger.warning("No findings found in data")
0143 |             return []
0144 |         
0145 |         # Determine parser strategy
0146 |         parser_strategy = self._detect_format(findings[0], tool_hint)
0147 |         logger.info(f"Using parser strategy: {parser_strategy}")
0148 |         
0149 |         vulnerabilities = []
0150 |         for i, finding in enumerate(findings):
0151 |             try:
0152 |                 vuln = self._parse_finding(finding, i + 1, parser_strategy)
0153 |                 if vuln:
0154 |                     vulnerabilities.append(vuln)
0155 |             except Exception as e:
0156 |                 logger.warning(f"Failed to parse finding {i+1}: {e}")
0157 |         
0158 |         logger.info(f"Parsed {len(vulnerabilities)} vulnerabilities")
0159 |         return vulnerabilities
0160 |     
0161 |     def _extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
0162 |         """Extract findings from various container structures"""
0163 |         
0164 |         # Direct list
0165 |         if isinstance(data, list):
0166 |             return data
0167 |         
0168 |         # Single object
0169 |         if isinstance(data, dict) and 'rule_id' in data:
0170 |             return [data]
0171 |         
0172 |         # Nested containers
0173 |         if isinstance(data, dict):
0174 |             for key in ['findings', 'vulnerabilities', 'issues', 'results', 'scan_results']:
0175 |                 if key in data and isinstance(data[key], list):
0176 |                     return data[key]
0177 |         
0178 |         return []
0179 |     
0180 |     def _extract_cvss(self, finding: Dict[str, Any]) -> Optional[float]:
0181 |         """Extraer CVSS de múltiples ubicaciones posibles"""
0182 |         for key in ['cvss_score', 'cvss', 'score']:
0183 |             if key in finding:
0184 |                 try:
0185 |                     score = float(finding[key])
0186 |                     if 0 <= score <= 10:
0187 |                         return score
0188 |                 except:
0189 |                     pass
0190 |         return None
0191 |     
0192 |     def _detect_format(self, sample_finding: Dict[str, Any], tool_hint: Optional[str]) -> str:
0193 |         """Detect the format of findings"""
0194 |         
0195 |         if tool_hint:
0196 |             if 'abap' in tool_hint.lower():
0197 |                 return 'abap'
0198 |         
0199 |         # Auto-detection based on structure
0200 |         if 'rule_id' in sample_finding and str(sample_finding.get('rule_id', '')).startswith('abap-'):
0201 |             return 'abap'
0202 |         
0203 |         if 'check_id' in sample_finding:
0204 |             return 'semgrep'
0205 |         
0206 |         if 'ruleId' in sample_finding:
0207 |             return 'sonarqube'
0208 |         
0209 |         return 'generic'
0210 |     
0211 |     def _parse_finding(self, finding: Dict[str, Any], index: int, strategy: str) -> Optional[Vulnerability]:
0212 |         """Parse individual finding based on strategy"""
0213 |         
0214 |         try:
0215 |             if strategy == 'abap':
0216 |                 return self._parse_abap_finding(finding, index)
0217 |             else:
0218 |                 return self._parse_generic_finding(finding, index)
0219 |         
0220 |         except Exception as e:
0221 |             logger.error(f"Failed to parse finding {index}: {e}")
0222 |             return None
0223 |     
0224 |     def _parse_abap_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
0225 |         """Parse ABAP-specific finding"""
0226 |         
0227 |         location = finding.get('location', {})
0228 |         
0229 |         return Vulnerability(
0230 |             id=finding.get('rule_id', f'ABAP-{index}'),
0231 |             type=self._normalize_vulnerability_type(finding.get('title', 'Unknown')),
0232 |             severity=self._normalize_severity(finding.get('severity', 'MEDIUM')),
0233 |             title=str(finding.get('title', 'ABAP Security Issue')).replace(' Vulnerability', '').strip(),
0234 |             description=finding.get('message', 'No description provided'),
0235 |             file_path=location.get('file', 'Unknown file'),
0236 |             line_number=int(location.get('line', 0)) if location.get('line') else 0,
0237 |             code_snippet=self._extract_code_context(location),
0238 |             cwe_id=self._normalize_cwe(finding.get('cwe')),
0239 |             source_tool='ABAP Security Scanner',
0240 |             rule_id=finding.get('rule_id'),
0241 |             confidence_level=self._extract_confidence(finding),
0242 |             remediation_advice=finding.get('remediation'),
0243 |             meta={
0244 |                 'original_finding': finding,
0245 |                 'parser_strategy': 'abap',
0246 |                 'parser_version': '3.0',
0247 |                 'cvss_score': self._extract_cvss(finding)
0248 |             }
0249 |         )
0250 |     
0251 |     def _parse_generic_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
0252 |         """Parse generic finding format"""
0253 |         
0254 |         return Vulnerability(
0255 |             id=finding.get('id', f'GENERIC-{index}'),
0256 |             type=VulnerabilityType.OTHER,
0257 |             severity=SeverityLevel.MEDIUM,
0258 |             title=str(finding.get('title', finding.get('message', 'Security Issue')))[:100],
0259 |             description=finding.get('description', finding.get('message', 'No description')),
0260 |             file_path=finding.get('file', finding.get('path', 'Unknown')),
0261 |             line_number=finding.get('line', 0),
0262 |             source_tool=finding.get('tool', 'Generic Scanner'),
0263 |             meta={'original_finding': finding, 'parser_strategy': 'generic'}
0264 |         )
0265 |     
0266 |     def _normalize_vulnerability_type(self, title: str) -> VulnerabilityType:
0267 |         """Smart vulnerability type mapping"""
0268 |         if not title:
0269 |             return VulnerabilityType.OTHER
0270 |             
0271 |         title_lower = str(title).lower()
0272 |         
0273 |         mappings = {
0274 |             'sql injection': VulnerabilityType.SQL_INJECTION,
0275 |             'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
0276 |             'path traversal': VulnerabilityType.PATH_TRAVERSAL,
0277 |             'code injection': VulnerabilityType.CODE_INJECTION,
0278 |             'cross-site scripting': VulnerabilityType.XSS,
0279 |             'xss': VulnerabilityType.XSS,
0280 |             'authentication': VulnerabilityType.AUTH_BYPASS,
0281 |             'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
0282 |             'crypto': VulnerabilityType.INSECURE_CRYPTO,
0283 |         }
0284 |         
0285 |         for pattern, vuln_type in mappings.items():
0286 |             if pattern in title_lower:
0287 |                 return vuln_type
0288 |         
0289 |         return VulnerabilityType.OTHER
0290 |     
0291 |     def _normalize_severity(self, severity: str) -> SeverityLevel:
0292 |         """Normalize severity levels"""
0293 |         if not severity:
0294 |             return SeverityLevel.MEDIUM
0295 |         
0296 |         severity_upper = str(severity).upper().strip()
0297 |         mappings = {
0298 |             'CRITICAL': SeverityLevel.CRITICAL,
0299 |             'HIGH': SeverityLevel.HIGH,
0300 |             'MEDIUM': SeverityLevel.MEDIUM,
0301 |             'LOW': SeverityLevel.LOW,
0302 |             'INFO': SeverityLevel.INFO,
0303 |             'CRÍTICA': SeverityLevel.CRITICAL,
0304 |             'ALTA': SeverityLevel.HIGH,
0305 |             'MEDIA': SeverityLevel.MEDIUM,
0306 |             'BAJA': SeverityLevel.LOW,
0307 |         }
0308 |         
0309 |         return mappings.get(severity_upper, SeverityLevel.MEDIUM)
0310 |     
0311 |     def _extract_code_context(self, location: Dict[str, Any]) -> Optional[str]:
0312 |         """Extract and format code context - SAFE VERSION"""
0313 |         context = location.get('context', [])
0314 |         line_content = location.get('line_content', '')
0315 |         
0316 |         if isinstance(context, list) and context:
0317 |             # Validar y convertir cada línea a string de forma segura
0318 |             safe_lines = []
0319 |             for i, line in enumerate(context):
0320 |                 # Validación robusta
0321 |                 if line is None:
0322 |                     continue  # Saltar None
0323 |                 elif isinstance(line, (int, float, bool)):
0324 |                     line_str = str(line)  # Convertir números a string
0325 |                 elif isinstance(line, dict):
0326 |                     line_str = str(line)  # Convertir dict a string
0327 |                 elif isinstance(line, str):
0328 |                     line_str = line
0329 |                 else:
0330 |                     line_str = repr(line)  # Fallback para tipos extraños
0331 |                 
0332 |                 # Solo agregar si no está vacío
0333 |                 if line_str.strip():
0334 |                     safe_lines.append(f"{i+1:3d} | {line_str}")
0335 |             
0336 |             if safe_lines:
0337 |                 return '\n'.join(safe_lines)
0338 |         
0339 |         # Fallback: usar line_content si existe
0340 |         if line_content:
0341 |             # Validar line_content también
0342 |             if isinstance(line_content, str):
0343 |                 return f">>> {line_content.strip()}"
0344 |             else:
0345 |                 return f">>> {str(line_content).strip()}"
0346 |         
0347 |         return None
0348 | 
0349 |     def _normalize_cwe(self, cwe: Optional[str]) -> Optional[str]:
0350 |         """Normalize CWE ID format"""
0351 |         if not cwe:
0352 |             return None
0353 |         
0354 |         cwe_str = str(cwe).strip()
0355 |         if cwe_str.isdigit():
0356 |             return f"CWE-{cwe_str}"
0357 |         elif cwe_str.startswith('CWE-'):
0358 |             return cwe_str
0359 |         
0360 |         return None
0361 |     
0362 |     def _extract_confidence(self, finding: Dict[str, Any]) -> Optional[float]:
0363 |         """Extract confidence level"""
0364 |         confidence = finding.get('confidence')
0365 |         if confidence:
0366 |             try:
0367 |                 if isinstance(confidence, str) and '%' in confidence:
0368 |                     return float(confidence.replace('%', '')) / 100.0
0369 |                 return float(confidence)
0370 |             except (ValueError, TypeError):
0371 |                 pass
0372 |         return None
0373 | 
0374 | class ScannerService:
0375 |     """Servicio de escaneo optimizado y consolidado"""
0376 |     
0377 |     def __init__(self, cache=None, enable_deduplication: bool = True, dedup_strategy: str = 'moderate'):
0378 |         self.parser = UnifiedVulnerabilityParser()
0379 |         self.cache = cache
0380 |         self.dedup_detector = DuplicateDetector(dedup_strategy) if enable_deduplication else None
0381 | 
0382 |     
0383 |     async def scan_file(self, 
0384 |                        file_path: str,
0385 |                        language: Optional[str] = None,
0386 |                        tool_hint: Optional[str] = None) -> ScanResult:
0387 |         """Scan and normalize vulnerability file"""
0388 |         
0389 |         logger.info(f"Scanning file: {file_path}")
0390 |         start_time = datetime.now()
0391 |         
0392 |         # Validate file
0393 |         self._validate_file(file_path)
0394 |         
0395 |         # Check cache
0396 |         if self.cache:
0397 |             cached_result = await self._check_cache(file_path, language, tool_hint)
0398 |             if cached_result:
0399 |                 logger.info("Using cached scan result")
0400 |                 return cached_result
0401 |         
0402 |         # Load and parse
0403 |         raw_data = self._load_file(file_path)
0404 |         vulnerabilities = self.parser.parse(raw_data, tool_hint)
0405 |         removed_dups = 0
0406 |         if self.dedup_detector:
0407 |             vulnerabilities, removed_dups = self.dedup_detector.remove_duplicates(vulnerabilities)
0408 |             if removed_dups > 0:
0409 |                 logger.info(f"🔄 Removed {removed_dups} duplicates")
0410 |         
0411 |         # Create result
0412 |         file_info = {
0413 |             'filename': Path(file_path).name,
0414 |             'full_path': str(Path(file_path).absolute()),
0415 |             'size_bytes': Path(file_path).stat().st_size,
0416 |             'language': language,
0417 |             'tool_hint': tool_hint,
0418 |             'duplicates_removed': removed_dups  # 🆕 AÑADIR ESTA LÍNEA
0419 |         }
0420 |         
0421 |         scan_duration = (datetime.now() - start_time).total_seconds()
0422 |         
0423 |         scan_result = ScanResult(
0424 |             file_info=file_info,
0425 |             vulnerabilities=vulnerabilities,
0426 |             scan_duration_seconds=scan_duration,
0427 |             language_detected=language
0428 |         )
0429 |         
0430 |         # Cache result
0431 |         if self.cache:
0432 |             await self._save_to_cache(file_path, scan_result, language, tool_hint)
0433 |         
0434 |         logger.info(f"Scan completed: {len(vulnerabilities)} vulnerabilities in {scan_duration:.2f}s")
0435 |         return scan_result
0436 |     
0437 |     def _validate_file(self, file_path: str) -> None:
0438 |         """Validate input file"""
0439 |         path = Path(file_path)
0440 |         
0441 |         if not path.exists():
0442 |             raise ValidationError(f"File not found: {file_path}")
0443 |         
0444 |         if path.suffix.lower() not in ['.json']:
0445 |             raise ValidationError(f"Unsupported file type: {path.suffix}")
0446 |         
0447 |         if path.stat().st_size > 100 * 1024 * 1024:  # 100MB
0448 |             raise ValidationError(f"File too large: {path.stat().st_size / 1024 / 1024:.1f}MB")
0449 |     
0450 |     def _load_file(self, file_path: str) -> Dict[str, Any]:
0451 |         """Load and parse JSON file"""
0452 |         try:
0453 |             with open(file_path, 'r', encoding='utf-8') as f:
0454 |                 return json.load(f)
0455 |         except json.JSONDecodeError as e:
0456 |             raise ParsingError(f"Invalid JSON in {file_path}: {e}")
0457 |         except Exception as e:
0458 |             raise ParsingError(f"Error reading {file_path}: {e}")
0459 |     
0460 |     async def _check_cache(self, file_path: str, language: Optional[str], tool_hint: Optional[str]):
0461 |         """Check cache for existing result"""
0462 |         if not self.cache:
0463 |             return None
0464 |         
0465 |         try:
0466 |             with open(file_path, 'r', encoding='utf-8') as f:
0467 |                 content = f.read()
0468 |             
0469 |             cached_data = self.cache.get(content, language, tool_hint)
0470 |             if cached_data:
0471 |                 return ScanResult(**cached_data)
0472 |         except Exception as e:
0473 |             logger.warning(f"Cache check failed: {e}")
0474 |         
0475 |         return None
0476 |     
0477 |     async def _save_to_cache(self, file_path: str, scan_result: ScanResult, 
0478 |                            language: Optional[str], tool_hint: Optional[str]) -> None:
0479 |         """Save result to cache"""
0480 |         if not self.cache:
0481 |             return
0482 |         
0483 |         try:
0484 |             with open(file_path, 'r', encoding='utf-8') as f:
0485 |                 content = f.read()
0486 |             
0487 |             # Usar model_dump en lugar de dict()
0488 |             self.cache.put(content, scan_result.model_dump(), language, tool_hint)
0489 |             logger.debug("Scan result cached")
0490 |         except Exception as e:
0491 |             logger.warning(f"Cache save failed: {e}")
0492 | 
0493 | # ============================================================================
0494 | # AÑADIR ESTA CLASE ANTES DE ScannerService
0495 | # ============================================================================
0496 | 
0497 | class DuplicateDetector:
0498 |     """Detector de duplicados con 3 estrategias"""
0499 |     
0500 |     def __init__(self, strategy: str = 'moderate'):
0501 |         self.strategy = strategy.lower()
0502 |     
0503 |     def remove_duplicates(self, vulnerabilities: List[Vulnerability]) -> Tuple[List[Vulnerability], int]:
0504 |         """Retorna (lista_sin_duplicados, cantidad_removida)"""
0505 |         if len(vulnerabilities) <= 1:
0506 |             return vulnerabilities, 0
0507 |         
0508 |         original = len(vulnerabilities)
0509 |         
0510 |         if self.strategy == 'strict':
0511 |             unique = self._strict(vulnerabilities)
0512 |         elif self.strategy == 'loose':
0513 |             unique = self._loose(vulnerabilities)
0514 |         else:
0515 |             unique = self._moderate(vulnerabilities)
0516 |         
0517 |         return unique, original - len(unique)
0518 |     
0519 |     def _strict(self, vulns):
0520 |         """Mismo file+line+type+description"""
0521 |         seen = set()
0522 |         unique = []
0523 |         for v in vulns:
0524 |             key = f"{v.file_path}|{v.line_number}|{v.type.value}|{hash(v.description)}"
0525 |             if key not in seen:
0526 |                 seen.add(key)
0527 |                 unique.append(v)
0528 |         return unique
0529 |     
0530 |     def _moderate(self, vulns):
0531 |         """Mismo file+type, ±5 líneas, 80% similar"""
0532 |         from collections import defaultdict
0533 |         groups = defaultdict(list)
0534 |         for v in vulns:
0535 |             groups[(v.file_path, v.type.value)].append(v)
0536 |         
0537 |         unique = []
0538 |         for group in groups.values():
0539 |             group.sort(key=lambda v: v.line_number)
0540 |             kept = []
0541 |             for v in group:
0542 |                 if not any(abs(v.line_number - k.line_number) <= 5 and 
0543 |                           self._sim(v.description, k.description) > 0.8 
0544 |                           for k in kept):
0545 |                     kept.append(v)
0546 |             unique.extend(kept)
0547 |         return unique
0548 |     
0549 |     def _loose(self, vulns):
0550 |         """Mismo type, 70% similar"""
0551 |         from collections import defaultdict
0552 |         groups = defaultdict(list)
0553 |         for v in vulns:
0554 |             groups[v.type.value].append(v)
0555 |         
0556 |         unique = []
0557 |         for group in groups.values():
0558 |             kept = []
0559 |             for v in group:
0560 |                 if not any(self._sim(v.description, k.description) > 0.7 for k in kept):
0561 |                     kept.append(v)
0562 |             unique.extend(kept)
0563 |         return unique
0564 |     
0565 |     def _sim(self, a: str, b: str) -> float:
0566 |         """Jaccard similarity"""
0567 |         if a == b:
0568 |             return 1.0
0569 |         t1, t2 = set(a.lower().split()), set(b.lower().split())
0570 |         return len(t1 & t2) / len(t1 | t2) if t1 and t2 else 0.0
```

---

### core\services\triage.py

**Ruta:** `core\services\triage.py`

```py
0001 | # core/services/triage.py
0002 | import logging
0003 | import asyncio
0004 | from typing import List, Optional
0005 | 
0006 | from ..models import Vulnerability, TriageResult, TriageDecision, AnalysisStatus
0007 | from ..exceptions import LLMError
0008 | from infrastructure.llm.client import LLMClient
0009 | from shared.metrics import MetricsCollector
0010 | 
0011 | logger = logging.getLogger(__name__)
0012 | 
0013 | class TriageService:
0014 |     """Servicio de triaje optimizado con fallbacks inteligentes"""
0015 |     
0016 |     def __init__(self, llm_client: LLMClient, metrics: Optional[MetricsCollector] = None):
0017 |         self.llm_client = llm_client
0018 |         self.metrics = metrics
0019 |     
0020 |     async def analyze_vulnerabilities(self, 
0021 |                                     vulnerabilities: List[Vulnerability],
0022 |                                     language: Optional[str] = None,
0023 |                                     chunk_id: Optional[int] = None) -> TriageResult:
0024 |         """Analyze vulnerabilities with intelligent triage"""
0025 |         
0026 |         if not vulnerabilities:
0027 |             return self._create_empty_result()
0028 |         
0029 |         start_time = asyncio.get_event_loop().time()
0030 |         
0031 |         try:
0032 |             logger.info(f"Starting triage analysis for {len(vulnerabilities)} vulnerabilities")
0033 |             
0034 |             # Prepare analysis request
0035 |             analysis_request = self._prepare_analysis_request(vulnerabilities, language, chunk_id)
0036 |             
0037 |             # Get LLM analysis
0038 |             llm_response = await self.llm_client.analyze_vulnerabilities(analysis_request)
0039 |             
0040 |             # Validate and enrich result
0041 |             validated_result = self._validate_and_complete_result(llm_response, vulnerabilities)
0042 |             
0043 |             # Record metrics
0044 |             analysis_time = asyncio.get_event_loop().time() - start_time
0045 |             if self.metrics:
0046 |                 self.metrics.record_triage_analysis(
0047 |                     len(vulnerabilities), analysis_time, True, chunk_id
0048 |                 )
0049 |             
0050 |             logger.info(f"Triage completed: {validated_result.confirmed_count} confirmed, "
0051 |                        f"{validated_result.false_positive_count} false positives")
0052 |             
0053 |             return validated_result
0054 |         
0055 |         except Exception as e:
0056 |             analysis_time = asyncio.get_event_loop().time() - start_time
0057 |             if self.metrics:
0058 |                 self.metrics.record_triage_analysis(
0059 |                     len(vulnerabilities), analysis_time, False, chunk_id, str(e)
0060 |                 )
0061 |             
0062 |             logger.error(f"Triage analysis failed: {e}")
0063 |             return self._create_fallback_result(vulnerabilities, str(e))
0064 |     
0065 |     def _prepare_analysis_request(self, vulnerabilities: List[Vulnerability], 
0066 |                                 language: Optional[str], chunk_id: Optional[int]) -> str:
0067 |         """Prepare structured analysis request for LLM"""
0068 |         
0069 |         header = f"# VULNERABILITY TRIAGE REQUEST\n"
0070 |         if chunk_id:
0071 |             header += f"Chunk ID: {chunk_id}\n"
0072 |         header += f"Language: {language or 'Unknown'}\n"
0073 |         header += f"Total Vulnerabilities: {len(vulnerabilities)}\n\n"
0074 |         
0075 |         vuln_blocks = []
0076 |         for i, vuln in enumerate(vulnerabilities, 1):
0077 |             block = f"""## VULNERABILITY {i}
0078 | - ID: {vuln.id}
0079 | - TYPE: {vuln.type.value}
0080 | - SEVERITY: {vuln.severity.value}
0081 | - FILE: {vuln.file_path}:{vuln.line_number}
0082 | - TITLE: {vuln.title}
0083 | - DESCRIPTION: {vuln.description}"""
0084 |             
0085 |             if vuln.code_snippet:
0086 |                 # Truncate code snippet for LLM context
0087 |                 snippet = vuln.code_snippet[:300] + "..." if len(vuln.code_snippet) > 300 else vuln.code_snippet
0088 |                 block += f"\n- CODE: {snippet}"
0089 |             
0090 |             if vuln.cwe_id:
0091 |                 block += f"\n- CWE: {vuln.cwe_id}"
0092 |             
0093 |             vuln_blocks.append(block)
0094 |         
0095 |         return header + "\n\n".join(vuln_blocks)
0096 |     
0097 |     def _validate_and_complete_result(self, llm_result: TriageResult, 
0098 |                                     original_vulnerabilities: List[Vulnerability]) -> TriageResult:
0099 |         """Validate LLM result and complete missing decisions"""
0100 |         
0101 |         original_ids = {v.id for v in original_vulnerabilities}
0102 |         analyzed_ids = {d.vulnerability_id for d in llm_result.decisions}
0103 |         
0104 |         # Add conservative decisions for missing vulnerabilities
0105 |         missing_ids = original_ids - analyzed_ids
0106 |         if missing_ids:
0107 |             logger.warning(f"LLM missed {len(missing_ids)} vulnerabilities, adding conservative decisions")
0108 |             
0109 |             for missing_id in missing_ids:
0110 |                 missing_vuln = next(v for v in original_vulnerabilities if v.id == missing_id)
0111 |                 conservative_decision = self._create_conservative_decision(missing_vuln)
0112 |                 llm_result.decisions.append(conservative_decision)
0113 |         
0114 |         return llm_result
0115 |     
0116 |     def _create_conservative_decision(self, vulnerability: Vulnerability) -> TriageDecision:
0117 |         """Create conservative decision for unanalyzed vulnerability"""
0118 |         
0119 |         # High severity = confirmed, others = manual review
0120 |         if vulnerability.severity in ["CRÍTICA", "ALTA"]:
0121 |             decision = AnalysisStatus.CONFIRMED
0122 |             confidence = 0.7
0123 |             reasoning = f"Conservative classification - {vulnerability.severity.value} severity assumed confirmed"
0124 |         else:
0125 |             decision = AnalysisStatus.NEEDS_MANUAL_REVIEW
0126 |             confidence = 0.5
0127 |             reasoning = f"Conservative classification - requires manual review"
0128 |         
0129 |         return TriageDecision(
0130 |             vulnerability_id=vulnerability.id,
0131 |             decision=decision,
0132 |             confidence_score=confidence,
0133 |             reasoning=reasoning,
0134 |             llm_model_used="conservative_fallback"
0135 |         )
0136 |     
0137 |     def _create_fallback_result(self, vulnerabilities: List[Vulnerability], error: str) -> TriageResult:
0138 |         """Create fallback result when LLM analysis fails"""
0139 |         
0140 |         logger.warning("Creating conservative fallback triage result")
0141 |         
0142 |         decisions = [self._create_conservative_decision(vuln) for vuln in vulnerabilities]
0143 |         
0144 |         return TriageResult(
0145 |             decisions=decisions,
0146 |             analysis_summary=f"Conservative fallback analysis due to LLM error: {error}",
0147 |             llm_analysis_time_seconds=0.0
0148 |         )
0149 |     
0150 |     def _create_empty_result(self) -> TriageResult:
0151 |         """Create empty result for no vulnerabilities"""
0152 |         return TriageResult(
0153 |             decisions=[],
0154 |             analysis_summary="No vulnerabilities to analyze",
0155 |             llm_analysis_time_seconds=0.0
0156 |         )
```

---

### core\services\__init__.py

**Ruta:** `core\services\__init__.py`

```py
```

---

### debug\llm_debugger.py

**Ruta:** `debug\llm_debugger.py`

```py
0001 | # debug/llm_debugger.py - VERSIÓN ACTUALIZADA CON CONTROL DE DEBUG EN CLIENT
0002 | import json
0003 | import logging
0004 | import os
0005 | import time
0006 | from datetime import datetime
0007 | from pathlib import Path
0008 | from typing import Any, Dict, Optional
0009 | import functools
0010 | import traceback
0011 | 
0012 | class LLMDebugger:
0013 |     """Debugger que controla automáticamente el debug en LLMClient"""
0014 |     
0015 |     def __init__(self, log_file: str = None, full_content: bool = True, max_content_length: int = 100000):
0016 |         # Crear directorio debug si no existe
0017 |         debug_dir = Path("debug")
0018 |         debug_dir.mkdir(exist_ok=True)
0019 |         
0020 |         # Archivo de log con timestamp
0021 |         if not log_file:
0022 |             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
0023 |             log_file = f"debug/llm_calls_{timestamp}.log"
0024 |         
0025 |         self.log_file = log_file
0026 |         self.full_content = full_content
0027 |         self.max_content_length = max_content_length
0028 |         
0029 |         # Lista de clientes LLM activos para controlar debug
0030 |         self.llm_clients = []
0031 |         
0032 |         # Configurar logger específico para LLM
0033 |         self.logger = logging.getLogger("LLM_DEBUG")
0034 |         self.logger.setLevel(logging.DEBUG)
0035 |         
0036 |         # Remover handlers existentes
0037 |         for handler in self.logger.handlers[:]:
0038 |             self.logger.removeHandler(handler)
0039 |         
0040 |         # Handler para archivo de debug con encoding UTF-8
0041 |         file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
0042 |         file_handler.setLevel(logging.DEBUG)
0043 |         
0044 |         # Formatter detallado sin límites de longitud
0045 |         formatter = logging.Formatter(
0046 |             '%(asctime)s | %(levelname)8s | %(message)s',
0047 |             datefmt='%Y-%m-%d %H:%M:%S'
0048 |         )
0049 |         file_handler.setFormatter(formatter)
0050 |         self.logger.addHandler(file_handler)
0051 |         
0052 |         # Handler para consola (con contenido limitado)
0053 |         console_handler = logging.StreamHandler()
0054 |         console_handler.setLevel(logging.INFO)
0055 |         console_formatter = logging.Formatter('🔍 DEBUG: %(message)s')
0056 |         console_handler.setFormatter(console_formatter)
0057 |         self.logger.addHandler(console_handler)
0058 |         
0059 |         # Estadísticas
0060 |         self.call_count = 0
0061 |         self.total_time = 0
0062 |         self.errors = []
0063 |         
0064 |         self.logger.info("="*100)
0065 |         self.logger.info("🔍 LLM DEBUGGER INICIADO - ACTIVANDO DEBUG EN CLIENTES")
0066 |         self.logger.info(f"📄 Log file: {log_file}")
0067 |         self.logger.info(f"📝 Full content mode: {self.full_content}")
0068 |         self.logger.info(f"📏 Max content length: {self.max_content_length if not self.full_content else 'UNLIMITED'}")
0069 |         self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
0070 |         self.logger.info("="*100)
0071 |         
0072 |         print(f"🔍 LLM Debug logging to: {log_file} (Full Content: {self.full_content})")
0073 |         
0074 |         # Activar debug en todos los clientes LLM existentes
0075 |         self._activate_debug_in_existing_clients()
0076 |     
0077 |     def _activate_debug_in_existing_clients(self):
0078 |         """Activar debug en clientes LLM ya existentes"""
0079 |         try:
0080 |             # Buscar clientes LLM en el sistema usando introspección
0081 |             import gc
0082 |             
0083 |             for obj in gc.get_objects():
0084 |                 if hasattr(obj, '__class__') and obj.__class__.__name__ == 'LLMClient':
0085 |                     self.register_llm_client(obj)
0086 |                     
0087 |         except Exception as e:
0088 |             self.logger.warning(f"Could not auto-activate debug in existing clients: {e}")
0089 |     
0090 |     def register_llm_client(self, llm_client):
0091 |         """Registrar y activar debug en un cliente LLM"""
0092 |         if llm_client not in self.llm_clients:
0093 |             self.llm_clients.append(llm_client)
0094 |             llm_client.enable_debug_mode()
0095 |             self.logger.info(f"✅ Debug enabled for LLM Client: {id(llm_client)}")
0096 |     
0097 |     def unregister_llm_client(self, llm_client):
0098 |         """Desregistrar cliente LLM"""
0099 |         if llm_client in self.llm_clients:
0100 |             self.llm_clients.remove(llm_client)
0101 |             llm_client.disable_debug_mode()
0102 |             self.logger.info(f"❌ Debug disabled for LLM Client: {id(llm_client)}")
0103 |     
0104 |     def log_api_call(self, 
0105 |                      call_type: str,
0106 |                      provider: str,
0107 |                      payload: Dict[str, Any],
0108 |                      response: Any = None,
0109 |                      error: Exception = None,
0110 |                      duration: float = None,
0111 |                      metadata: Dict[str, Any] = None):
0112 |         """Log detallado de llamada API con contenido completo"""
0113 |         
0114 |         self.call_count += 1
0115 |         call_id = f"CALL_{self.call_count:03d}"
0116 |         
0117 |         # === HEADER ===
0118 |         self.logger.info(f"\n{'='*100}")
0119 |         self.logger.info(f"🚀 {call_id} - {call_type.upper()} | Provider: {provider}")
0120 |         self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
0121 |         self.logger.info(f"{'='*100}")
0122 |         
0123 |         # === PAYLOAD DETAILS (CONTENIDO COMPLETO) ===
0124 |         self.logger.info("📤 PAYLOAD ENVIADO (REQUEST):")
0125 |         self._log_content_section(payload, "REQUEST", is_json=True)
0126 |         
0127 |         # === RESPONSE DETAILS (CONTENIDO COMPLETO) ===
0128 |         if response is not None:
0129 |             self.logger.info("\n📥 RESPUESTA RECIBIDA (RESPONSE):")
0130 |             self._log_content_section(response, "RESPONSE", is_json=None)
0131 |         
0132 |         # === ERROR DETAILS (COMPLETO) ===
0133 |         if error:
0134 |             self.logger.error(f"\n❌ ERROR OCURRIDO:")
0135 |             self.logger.error(f"   🔧 Type: {type(error).__name__}")
0136 |             self.logger.error(f"   💬 Message: {str(error)}")
0137 |             self.logger.error(f"   📍 Traceback completo:")
0138 |             
0139 |             # Traceback completo
0140 |             tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
0141 |             for line in tb_lines:
0142 |                 self.logger.error(f"     {line.rstrip()}")
0143 |             
0144 |             self.errors.append({
0145 |                 'call_id': call_id,
0146 |                 'error_type': type(error).__name__,
0147 |                 'error_message': str(error),
0148 |                 'traceback': ''.join(tb_lines),
0149 |                 'timestamp': datetime.now().isoformat()
0150 |             })
0151 |         
0152 |         # === PERFORMANCE METRICS ===
0153 |         if duration:
0154 |             self.total_time += duration
0155 |             self.logger.info(f"\n⏱️  MÉTRICAS DE RENDIMIENTO:")
0156 |             self.logger.info(f"   🕐 Duración de llamada: {duration:.3f}s")
0157 |             self.logger.info(f"   📊 Tiempo total acumulado: {self.total_time:.3f}s")
0158 |             self.logger.info(f"   📈 Promedio por llamada: {self.total_time/self.call_count:.3f}s")
0159 |             
0160 |             # Throughput si hay datos de vulnerabilidades
0161 |             if metadata and 'vulnerabilities_count' in metadata:
0162 |                 vuln_count = metadata['vulnerabilities_count']
0163 |                 throughput = vuln_count / duration if duration > 0 else 0
0164 |                 self.logger.info(f"   🚀 Throughput: {throughput:.2f} vulnerabilidades/segundo")
0165 |         
0166 |         # === METADATA ===
0167 |         if metadata:
0168 |             self.logger.info(f"\n📊 METADATOS:")
0169 |             for key, value in metadata.items():
0170 |                 self.logger.info(f"   📋 {key}: {value}")
0171 |         
0172 |         # === FOOTER ===
0173 |         self.logger.info(f"{'='*100}")
0174 |         self.logger.info(f"✅ {call_id} COMPLETADO")
0175 |         self.logger.info(f"{'='*100}\n")
0176 |     
0177 |     def _log_content_section(self, content: Any, section_name: str, is_json: bool = None):
0178 |         """Log una sección de contenido completo con análisis automático"""
0179 |         
0180 |         # Determinar el tipo de contenido y convertir a string
0181 |         if isinstance(content, dict):
0182 |             content_str = json.dumps(content, indent=2, ensure_ascii=False)
0183 |             is_json = True
0184 |         elif isinstance(content, str):
0185 |             content_str = content
0186 |             # Intentar detectar si es JSON
0187 |             if is_json is None:
0188 |                 try:
0189 |                     json.loads(content)
0190 |                     is_json = True
0191 |                 except:
0192 |                     is_json = False
0193 |         else:
0194 |             content_str = str(content)
0195 |             is_json = False
0196 |         
0197 |         # Calcular métricas
0198 |         content_size = len(content_str.encode('utf-8'))
0199 |         line_count = content_str.count('\n') + 1
0200 |         
0201 |         self.logger.info(f"   📏 Size: {content_size:,} bytes")
0202 |         self.logger.info(f"   📄 Lines: {line_count:,}")
0203 |         self.logger.info(f"   🔧 Type: {type(content).__name__}")
0204 |         self.logger.info(f"   📋 Format: {'JSON' if is_json else 'Text'}")
0205 |         
0206 |         # Si es un dict, mostrar estructura
0207 |         if isinstance(content, dict):
0208 |             self.logger.info(f"   🔑 Keys: {list(content.keys())}")
0209 |         
0210 |         # Log del contenido completo
0211 |         if self.full_content or content_size <= self.max_content_length:
0212 |             self.logger.info(f"   📋 CONTENIDO COMPLETO DE {section_name}:")
0213 |             self.logger.info("   " + "─" * 80)
0214 |             
0215 |             # Formatear con numeración de líneas
0216 |             formatted_content = self._format_with_line_numbers(content_str)
0217 |             self.logger.info(formatted_content)
0218 |             
0219 |             self.logger.info("   " + "─" * 80)
0220 |         else:
0221 |             # Modo truncado
0222 |             self.logger.info(f"   📋 CONTENIDO DE {section_name} (TRUNCADO):")
0223 |             self.logger.info("   " + "─" * 80)
0224 |             
0225 |             # Mostrar inicio y final
0226 |             preview_length = min(2000, self.max_content_length // 2)
0227 |             
0228 |             self.logger.info("   📝 INICIO:")
0229 |             start_content = content_str[:preview_length]
0230 |             self.logger.info(self._format_with_line_numbers(start_content))
0231 |             
0232 |             if len(content_str) > preview_length * 2:
0233 |                 self.logger.info(f"\n   ⚠️  ... CONTENIDO MEDIO OMITIDO ({len(content_str) - preview_length * 2:,} chars) ...\n")
0234 |             
0235 |             self.logger.info("   📝 FINAL:")
0236 |             end_content = content_str[-preview_length:]
0237 |             # Calcular número de línea inicial para el final
0238 |             start_line = content_str[:len(content_str) - preview_length].count('\n') + 1
0239 |             self.logger.info(self._format_with_line_numbers(end_content, start_line))
0240 |             
0241 |             self.logger.info("   " + "─" * 80)
0242 |             self.logger.info(f"   ⚠️  NOTA: Contenido truncado - longitud original: {content_size:,} bytes")
0243 |     
0244 |     def _format_with_line_numbers(self, text: str, start_line: int = 1) -> str:
0245 |         """Formatear texto con numeración de líneas"""
0246 |         lines = text.split('\n')
0247 |         formatted_lines = []
0248 |         
0249 |         for i, line in enumerate(lines):
0250 |             line_num = start_line + i
0251 |             formatted_lines.append(f"   [{line_num:5d}] {line}")
0252 |         
0253 |         return '\n'.join(formatted_lines)
0254 |     
0255 |     def log_triage_analysis(self, vulnerabilities_data: str, system_prompt: str, response: Any, duration: float = None):
0256 |         """Log específico para análisis de triage con contenido completo"""
0257 |         
0258 |         vuln_count = vulnerabilities_data.count("## VULNERABILITY")
0259 |         
0260 |         metadata = {
0261 |             'analysis_type': 'vulnerability_triage',
0262 |             'vulnerabilities_count': vuln_count,
0263 |             'system_prompt_length': len(system_prompt),
0264 |             'vulnerabilities_data_length': len(vulnerabilities_data),
0265 |             'total_input_size': len(system_prompt) + len(vulnerabilities_data)
0266 |         }
0267 |         
0268 |         # Payload completo para triage - CONTENIDO REAL
0269 |         full_message = f"{system_prompt}\n\nDATA TO ANALYZE:\n{vulnerabilities_data}"
0270 |         payload = {
0271 |             'message': {
0272 |                 'role': 'user',
0273 |                 'content': full_message
0274 |             },
0275 |             'temperature': 0.1,
0276 |             'model': 'meta-llama/llama-3-3-70b-instruct',
0277 |             'analysis_metadata': metadata
0278 |         }
0279 |         
0280 |         self.log_api_call(
0281 |             call_type="triage_analysis",
0282 |             provider="research_api",
0283 |             payload=payload,
0284 |             response=response,
0285 |             duration=duration,
0286 |             metadata=metadata
0287 |         )
0288 |     
0289 |     def log_remediation_generation(self, vulnerability_data: str, system_prompt: str, response: Any, duration: float = None):
0290 |         """Log específico para generación de remediación con contenido completo"""
0291 |         
0292 |         metadata = {
0293 |             'analysis_type': 'remediation_generation',
0294 |             'system_prompt_length': len(system_prompt),
0295 |             'vulnerability_data_length': len(vulnerability_data),
0296 |             'total_input_size': len(system_prompt) + len(vulnerability_data)
0297 |         }
0298 |         
0299 |         # Payload completo para remediación - CONTENIDO REAL
0300 |         full_message = f"{system_prompt}\n\nVULNERABILITY DATA:\n{vulnerability_data}"
0301 |         payload = {
0302 |             'message': {
0303 |                 'role': 'user',
0304 |                 'content': full_message
0305 |             },
0306 |             'temperature': 0.2,
0307 |             'model': 'meta-llama/llama-3-3-70b-instruct',
0308 |             'remediation_metadata': metadata
0309 |         }
0310 |         
0311 |         self.log_api_call(
0312 |             call_type="remediation_generation",
0313 |             provider="research_api",
0314 |             payload=payload,
0315 |             response=response,
0316 |             duration=duration,
0317 |             metadata=metadata
0318 |         )
0319 |     
0320 |     def log_raw_http_call(self, url: str, method: str, headers: Dict, request_body: Any, 
0321 |                          response_status: int, response_headers: Dict, response_body: Any, 
0322 |                          duration: float = None):
0323 |         """Log de llamada HTTP cruda con todos los detalles"""
0324 |         
0325 |         self.call_count += 1
0326 |         call_id = f"HTTP_{self.call_count:03d}"
0327 |         
0328 |         self.logger.info(f"\n{'='*100}")
0329 |         self.logger.info(f"🌐 {call_id} - HTTP {method.upper()} | URL: {url}")
0330 |         self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
0331 |         self.logger.info(f"{'='*100}")
0332 |         
0333 |         # REQUEST DETAILS
0334 |         self.logger.info("📤 HTTP REQUEST:")
0335 |         self.logger.info(f"   🔗 URL: {url}")
0336 |         self.logger.info(f"   🔧 Method: {method}")
0337 |         self.logger.info(f"   📋 Headers:")
0338 |         for header, value in headers.items():
0339 |             # Ocultar parcialmente API keys por seguridad
0340 |             if 'api' in header.lower() or 'key' in header.lower() or 'auth' in header.lower():
0341 |                 masked_value = value[:8] + "***" + value[-4:] if len(value) > 12 else "***"
0342 |                 self.logger.info(f"      {header}: {masked_value}")
0343 |             else:
0344 |                 self.logger.info(f"      {header}: {value}")
0345 |         
0346 |         # REQUEST BODY
0347 |         if request_body:
0348 |             self.logger.info(f"\n   📤 REQUEST BODY:")
0349 |             self._log_content_section(request_body, "REQUEST_BODY")
0350 |         
0351 |         # RESPONSE DETAILS
0352 |         self.logger.info(f"\n📥 HTTP RESPONSE:")
0353 |         self.logger.info(f"   📊 Status: {response_status}")
0354 |         self.logger.info(f"   📋 Headers:")
0355 |         for header, value in response_headers.items():
0356 |             self.logger.info(f"      {header}: {value}")
0357 |         
0358 |         # RESPONSE BODY
0359 |         if response_body:
0360 |             self.logger.info(f"\n   📥 RESPONSE BODY:")
0361 |             self._log_content_section(response_body, "RESPONSE_BODY")
0362 |         
0363 |         # PERFORMANCE
0364 |         if duration:
0365 |             self.total_time += duration
0366 |             self.logger.info(f"\n⏱️  HTTP PERFORMANCE:")
0367 |             self.logger.info(f"   🕐 Duration: {duration:.3f}s")
0368 |             self.logger.info(f"   📊 Status: {'✅ Success' if 200 <= response_status < 300 else '❌ Error'}")
0369 |         
0370 |         self.logger.info(f"{'='*100}\n")
0371 |     
0372 |     def get_summary_stats(self) -> Dict[str, Any]:
0373 |         """Obtener estadísticas resumidas"""
0374 |         return {
0375 |             'total_calls': self.call_count,
0376 |             'total_time_seconds': self.total_time,
0377 |             'average_time_per_call': self.total_time / self.call_count if self.call_count > 0 else 0,
0378 |             'error_count': len(self.errors),
0379 |             'success_rate': (self.call_count - len(self.errors)) / self.call_count if self.call_count > 0 else 0,
0380 |             'errors': self.errors,
0381 |             'log_file': self.log_file,
0382 |             'full_content_mode': self.full_content,
0383 |             'active_llm_clients': len(self.llm_clients)
0384 |         }
0385 |     
0386 |     def finalize_log(self):
0387 |         """Finalizar el log con estadísticas completas y desactivar debug en clientes"""
0388 |         
0389 |         # Desactivar debug en todos los clientes registrados
0390 |         for client in self.llm_clients[:]:  # Copia la lista para evitar modificaciones concurrentes
0391 |             self.unregister_llm_client(client)
0392 |         
0393 |         stats = self.get_summary_stats()
0394 |         
0395 |         self.logger.info("\n" + "="*100)
0396 |         self.logger.info("📊 RESUMEN FINAL - LLM DEBUG SESSION")
0397 |         self.logger.info("="*100)
0398 |         self.logger.info(f"🔢 Total de llamadas: {stats['total_calls']}")
0399 |         self.logger.info(f"⏱️  Tiempo total: {stats['total_time_seconds']:.2f}s")
0400 |         self.logger.info(f"📊 Tiempo promedio: {stats['average_time_per_call']:.2f}s por llamada")
0401 |         self.logger.info(f"❌ Errores: {stats['error_count']}")
0402 |         self.logger.info(f"✅ Tasa de éxito: {stats['success_rate']:.1%}")
0403 |         self.logger.info(f"📄 Archivo de log: {stats['log_file']}")
0404 |         self.logger.info(f"📝 Modo contenido completo: {stats['full_content_mode']}")
0405 |         self.logger.info(f"🔧 Clientes LLM controlados: {stats['active_llm_clients']}")
0406 |         
0407 |         if self.errors:
0408 |             self.logger.info("\n🚨 ERRORES DETECTADOS:")
0409 |             for error in self.errors:
0410 |                 self.logger.info(f"   {error['call_id']}: {error['error_type']} - {error['error_message']}")
0411 |         
0412 |         # Estadísticas de contenido
0413 |         log_size = Path(self.log_file).stat().st_size if Path(self.log_file).exists() else 0
0414 |         self.logger.info(f"\n📏 ESTADÍSTICAS DEL LOG:")
0415 |         self.logger.info(f"   📄 Tamaño del archivo: {log_size:,} bytes ({log_size/1024/1024:.2f} MB)")
0416 |         self.logger.info(f"   📝 Modo: {'Contenido completo' if self.full_content else 'Contenido limitado'}")
0417 |         
0418 |         self.logger.info("="*100)
0419 |         print(f"📄 Debug completo guardado en: {self.log_file} ({log_size/1024/1024:.2f} MB)")
0420 | 
0421 | 
0422 | # Instancia global del debugger
0423 | _debugger = None
0424 | 
0425 | def get_debugger(full_content: bool = True) -> LLMDebugger:
0426 |     """Obtener instancia singleton del debugger"""
0427 |     global _debugger
0428 |     if _debugger is None:
0429 |         _debugger = LLMDebugger(full_content=full_content)
0430 |     return _debugger
0431 | 
0432 | def debug_llm_call(func):
0433 |     """Decorador para debuggear automáticamente llamadas LLM"""
0434 |     
0435 |     @functools.wraps(func)
0436 |     async def wrapper(*args, **kwargs):
0437 |         debugger = get_debugger()
0438 |         start_time = time.time()
0439 |         
0440 |         try:
0441 |             result = await func(*args, **kwargs)
0442 |             duration = time.time() - start_time
0443 |             
0444 |             debugger.log_api_call(
0445 |                 call_type=func.__name__,
0446 |                 provider="auto_detected",
0447 |                 payload={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]},
0448 |                 response=str(result)[:1000] if len(str(result)) <= 1000 else result,
0449 |                 duration=duration
0450 |             )
0451 |             
0452 |             return result
0453 |             
0454 |         except Exception as e:
0455 |             duration = time.time() - start_time
0456 |             
0457 |             debugger.log_api_call(
0458 |                 call_type=func.__name__,
0459 |                 provider="auto_detected", 
0460 |                 payload={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]},
0461 |                 error=e,
0462 |                 duration=duration
0463 |             )
0464 |             
0465 |             raise
0466 |     
0467 |     return wrapper
0468 | 
0469 | # === FUNCIONES DE UTILIDAD ===
0470 | 
0471 | def start_debug_session(full_content: bool = True):
0472 |     """Iniciar nueva sesión de debug y activar debug automáticamente en clientes LLM"""
0473 |     global _debugger
0474 |     _debugger = LLMDebugger(full_content=full_content)
0475 |     print(f"🔍 Debug session started: {_debugger.log_file}")
0476 |     print(f"📡 Auto-activating debug in LLM clients...")
0477 | 
0478 | def end_debug_session():
0479 |     """Finalizar sesión de debug y desactivar debug en clientes"""
0480 |     global _debugger
0481 |     if _debugger:
0482 |         _debugger.finalize_log()
0483 |         _debugger = None
0484 | 
0485 | def log_research_api_call(url: str, payload: Dict[str, Any], response: Any, 
0486 |                          duration: float = None, error: Exception = None):
0487 |     """Log específico para Research API con contenido completo"""
0488 |     debugger = get_debugger()
0489 |     debugger.log_api_call(
0490 |         call_type="research_api_call",
0491 |         provider="research_api",
0492 |         payload=payload,
0493 |         response=response,
0494 |         duration=duration,
0495 |         error=error,
0496 |         metadata={
0497 |             'url': url,
0498 |             'payload_size': len(json.dumps(payload, ensure_ascii=False)) if isinstance(payload, dict) else len(str(payload)),
0499 |             'response_size': len(str(response)) if response else 0
0500 |         }
0501 |     )
0502 | 
0503 | def log_http_details(url: str, method: str, headers: Dict, request_body: Any,
0504 |                     response_status: int, response_headers: Dict, response_body: Any,
0505 |                     duration: float = None):
0506 |     """Log detallado de llamada HTTP"""
0507 |     debugger = get_debugger()
0508 |     debugger.log_raw_http_call(
0509 |         url=url,
0510 |         method=method,
0511 |         headers=headers,
0512 |         request_body=request_body,
0513 |         response_status=response_status,
0514 |         response_headers=response_headers,
0515 |         response_body=response_body,
0516 |         duration=duration
0517 |     )
0518 | 
0519 | def register_llm_client_for_debug(llm_client):
0520 |     """Registrar manualmente un cliente LLM para debug"""
0521 |     try:
0522 |         debugger = get_debugger()
0523 |         debugger.register_llm_client(llm_client)
0524 |     except:
0525 |         pass  # Si no hay sesión de debug activa, no hacer nada
```

---

### debug\run_with_debug.py

**Ruta:** `debug\run_with_debug.py`

```py
0001 | # debug/run_with_full_debug.py - VERSIÓN MEJORADA
0002 | #!/usr/bin/env python3
0003 | """
0004 | Script para ejecutar análisis con debug completo y automático
0005 | """
0006 | 
0007 | import sys
0008 | import asyncio
0009 | import os
0010 | from pathlib import Path
0011 | 
0012 | # Agregar directorio raíz al path
0013 | project_root = Path(__file__).parent.parent
0014 | sys.path.insert(0, str(project_root))
0015 | 
0016 | def setup_debug_environment():
0017 |     """Configurar entorno para debug completo"""
0018 |     
0019 |     # Importar y configurar debugger
0020 |     from debug.llm_debugger import start_debug_session, get_debugger
0021 |     from application.factory import create_debug_factory
0022 |     
0023 |     print("🔍 Starting FULL CONTENT LLM Debug Session...")
0024 |     print("📝 This will log complete requests and responses to debug file")
0025 |     
0026 |     # Verificar si hay API key
0027 |     api_key = os.getenv("RESEARCH_API_KEY")
0028 |     if api_key:
0029 |         print(f"🔑 API Key detected: {api_key[:8]}***{api_key[-4:]}")
0030 |     else:
0031 |         print("⚠️  No API key - will use mock responses")
0032 |     
0033 |     # Iniciar debug session con contenido completo
0034 |     start_debug_session(full_content=True)
0035 |     
0036 |     debugger = get_debugger()
0037 |     print(f"📄 Debug file: {debugger.log_file}")
0038 |     
0039 |     return debugger
0040 | 
0041 | def patch_factory_for_debug():
0042 |     """Patchear el factory por defecto para usar debug"""
0043 |     
0044 |     import application.factory as factory_module
0045 |     
0046 |     # Guardar la función original
0047 |     original_create_factory = factory_module.create_factory
0048 |     
0049 |     # Crear función de reemplazo que habilita debug
0050 |     def create_debug_enabled_factory():
0051 |         factory = original_create_factory()
0052 |         factory.enable_debug_mode()
0053 |         return factory
0054 |     
0055 |     # Reemplazar la función
0056 |     factory_module.create_factory = create_debug_enabled_factory
0057 |     
0058 |     print("🔧 Factory patched to enable debug mode")
0059 | 
0060 | def main():
0061 |     """Ejecutar CLI con debug completo habilitado automáticamente"""
0062 |     
0063 |     debugger = None
0064 |     
0065 |     try:
0066 |         # Configurar debug
0067 |         debugger = setup_debug_environment()
0068 |         
0069 |         # Patchear factory para habilitar debug automáticamente
0070 |         patch_factory_for_debug()
0071 |         
0072 |         # Importar CLI después del patch
0073 |         from application.cli import cli
0074 |         
0075 |         print("\n🚀 Starting analysis with full debug logging...")
0076 |         print("📡 All LLM clients will be automatically configured for debug")
0077 |         
0078 |         # Ejecutar CLI normal - ahora con debug automático
0079 |         cli()
0080 |         
0081 |     except SystemExit as e:
0082 |         # SystemExit es normal para CLI
0083 |         if e.code != 0:
0084 |             print(f"⚠️  CLI exited with code: {e.code}")
0085 |     except KeyboardInterrupt:
0086 |         print("\n⚠️  Analysis interrupted by user")
0087 |     except Exception as e:
0088 |         print(f"❌ Unexpected error: {e}")
0089 |         import traceback
0090 |         traceback.print_exc()
0091 |     finally:
0092 |         # Finalizar debug session
0093 |         if debugger:
0094 |             print("\n📊 Finalizing debug session...")
0095 |             from debug.llm_debugger import end_debug_session
0096 |             end_debug_session()
0097 |             
0098 |             # Mostrar estadísticas finales
0099 |             stats = debugger.get_summary_stats()
0100 |             print(f"\n✅ Debug session completed!")
0101 |             print(f"   📞 Total calls: {stats['total_calls']}")
0102 |             print(f"   ⏱️  Total time: {stats['total_time_seconds']:.2f}s")
0103 |             print(f"   🔧 LLM clients controlled: {stats['active_llm_clients']}")
0104 |             
0105 |             if Path(debugger.log_file).exists():
0106 |                 log_size = Path(debugger.log_file).stat().st_size / 1024 / 1024
0107 |                 print(f"   📄 Log file size: {log_size:.2f} MB")
0108 |                 print(f"   📂 Log location: {debugger.log_file}")
0109 | 
0110 | if __name__ == '__main__':
0111 |     main()
```

---

### infrastructure\cache.py

**Ruta:** `infrastructure\cache.py`

```py
0001 | # infrastructure/cache.py
0002 | import hashlib
0003 | import json
0004 | import pickle
0005 | from pathlib import Path
0006 | from typing import Dict, Any, Optional
0007 | from datetime import datetime, timedelta
0008 | import logging
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | class AnalysisCache:
0013 |     """Cache optimizado para resultados de análisis"""
0014 |     
0015 |     def __init__(self, cache_dir: str = ".security_cache", ttl_hours: int = 24):
0016 |         self.cache_dir = Path(cache_dir)
0017 |         self.ttl_hours = ttl_hours
0018 |         self.cache_dir.mkdir(exist_ok=True)
0019 |         self._cleanup_expired()
0020 |     
0021 |     def _get_cache_key(self, content: str, language: Optional[str], tool_hint: Optional[str]) -> str:
0022 |         """Generate cache key from content hash"""
0023 |         key_data = f"{content}|{language or ''}|{tool_hint or ''}"
0024 |         return hashlib.sha256(key_data.encode()).hexdigest()[:16]
0025 |     
0026 |     def get(self, content: str, language: Optional[str] = None, 
0027 |             tool_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
0028 |         """Get from cache with TTL check"""
0029 |         try:
0030 |             cache_key = self._get_cache_key(content, language, tool_hint)
0031 |             cache_file = self.cache_dir / f"{cache_key}.cache"
0032 |             
0033 |             if not cache_file.exists():
0034 |                 return None
0035 |             
0036 |             # Check TTL
0037 |             file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
0038 |             if file_age > timedelta(hours=self.ttl_hours):
0039 |                 cache_file.unlink()
0040 |                 return None
0041 |             
0042 |             with open(cache_file, 'rb') as f:
0043 |                 return pickle.load(f)
0044 |                 
0045 |         except Exception as e:
0046 |             logger.warning(f"Cache read failed: {e}")
0047 |             return None
0048 |     
0049 |     def put(self, content: str, data: Dict[str, Any], 
0050 |             language: Optional[str] = None, tool_hint: Optional[str] = None) -> None:
0051 |         """Store in cache"""
0052 |         try:
0053 |             cache_key = self._get_cache_key(content, language, tool_hint)
0054 |             cache_file = self.cache_dir / f"{cache_key}.cache"
0055 |             
0056 |             with open(cache_file, 'wb') as f:
0057 |                 pickle.dump(data, f)
0058 |                 
0059 |             logger.debug(f"Cached result: {cache_key}")
0060 |             
0061 |         except Exception as e:
0062 |             logger.warning(f"Cache write failed: {e}")
0063 |     
0064 |     def _cleanup_expired(self) -> None:
0065 |         """Clean up expired cache files"""
0066 |         try:
0067 |             cutoff_time = datetime.now() - timedelta(hours=self.ttl_hours)
0068 |             
0069 |             for cache_file in self.cache_dir.glob("*.cache"):
0070 |                 file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
0071 |                 if file_time < cutoff_time:
0072 |                     cache_file.unlink()
0073 |                     
0074 |         except Exception as e:
0075 |             logger.warning(f"Cache cleanup failed: {e}")
```

---

### infrastructure\config.py

**Ruta:** `infrastructure\config.py`

```py
0001 | # infrastructure/config.py - VERSIÓN SIMPLIFICADA TEMPORAL
0002 | import os
0003 | from typing import Optional, Dict, Any
0004 | 
0005 | class UnifiedSettings:
0006 |     """Configuración simplificada sin Pydantic Settings"""
0007 |     
0008 |     def __init__(self):
0009 |         # 🔑 API Keys
0010 |         self.openai_api_key = os.getenv("OPENAI_API_KEY")
0011 |         self.watsonx_api_key = os.getenv("RESEARCH_API_KEY")
0012 |         
0013 |         # 🤖 LLM Configuration
0014 |         self.llm_primary_provider = os.getenv("LLM_PRIMARY_PROVIDER", "openai")
0015 |         self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
0016 |         self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
0017 |         self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT", "180"))
0018 |         
0019 |         # 🧩 Chunking Configuration
0020 |         self.chunking_max_vulnerabilities = int(os.getenv("CHUNKING_MAX_VULNS", "5"))
0021 |         self.chunking_max_size_bytes = int(os.getenv("CHUNKING_MAX_SIZE", "8000"))
0022 |         self.chunking_overlap = int(os.getenv("CHUNKING_OVERLAP", "1"))
0023 |         self.chunking_min_size = int(os.getenv("CHUNKING_MIN_SIZE", "3"))
0024 |         
0025 |         # 💾 Cache Configuration
0026 |         self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
0027 |         self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "24"))
0028 |         self.cache_directory = os.getenv("CACHE_DIR", ".security_cache")
0029 |         
0030 |         # 🔒 Security Configuration
0031 |         self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
0032 |         self.input_validation_enabled = os.getenv("INPUT_VALIDATION", "true").lower() == "true"
0033 |         
0034 |         # 📊 Reporting Configuration
0035 |         self.report_max_code_length = int(os.getenv("REPORT_MAX_CODE_LENGTH", "1000"))
0036 |         
0037 |         # 📈 Observability
0038 |         self.log_level = os.getenv("LOG_LEVEL", "INFO")
0039 |         self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
0040 |     
0041 |     @property
0042 |     def has_llm_provider(self) -> bool:
0043 |         """Check if at least one LLM provider is configured"""
0044 |         return bool(self.openai_api_key or self.watsonx_api_key)
0045 |     
0046 |     @property
0047 |     def chunking_config(self) -> Dict[str, Any]:
0048 |         """Get chunking configuration as dict"""
0049 |         return {
0050 |             "max_vulnerabilities_per_chunk": self.chunking_max_vulnerabilities,
0051 |             "max_size_bytes": self.chunking_max_size_bytes,
0052 |             "overlap_vulnerabilities": self.chunking_overlap,
0053 |             "min_chunk_size": self.chunking_min_size
0054 |         }
0055 |     
0056 |     def get_available_llm_provider(self) -> str:
0057 |         """Get the first available LLM provider"""
0058 |         if self.llm_primary_provider == "openai" and self.openai_api_key:
0059 |             return "openai"
0060 |         elif self.llm_primary_provider == "watsonx" and self.watsonx_api_key:
0061 |             return "watsonx"
0062 |         elif self.openai_api_key:
0063 |             return "openai"
0064 |         elif self.watsonx_api_key:
0065 |             return "watsonx"
0066 |         else:
0067 |             raise ValueError("No LLM provider configured")
0068 | 
0069 | # Global settings instance
0070 | settings = UnifiedSettings()
```

---

### infrastructure\__init__.py

**Ruta:** `infrastructure\__init__.py`

```py
```

---

### infrastructure\llm\client.py

**Ruta:** `infrastructure\llm\client.py`

```py
0001 | # infrastructure/llm/client.py
0002 | """
0003 | 🤖 LLM Client - Comunicación con Research API
0004 | 
0005 | Features:
0006 | - ✅ Comunicación HTTP con Research API
0007 | - ✅ Retry logic con backoff exponencial
0008 | - ✅ Debug mode integrado
0009 | - ✅ Manejo robusto de errores
0010 | - ✅ Métodos de alto nivel para triage y remediation
0011 | """
0012 | 
0013 | import requests
0014 | import json
0015 | import logging
0016 | import time
0017 | import os
0018 | import uuid
0019 | import asyncio
0020 | from typing import Dict, Any, Optional
0021 | from datetime import datetime
0022 | 
0023 | from core.models import TriageResult, RemediationPlan
0024 | from core.exceptions import LLMError
0025 | from .response_parser import LLMResponseParser
0026 | from .prompts import PromptManager
0027 | 
0028 | logger = logging.getLogger(__name__)
0029 | 
0030 | 
0031 | class LLMClient:
0032 |     """
0033 |     Cliente LLM para Research API
0034 |     
0035 |     Responsabilidades:
0036 |     - Comunicación HTTP con Research API
0037 |     - Manejo de reintentos y timeouts
0038 |     - Control de debug mode
0039 |     - Métodos de alto nivel (analyze_vulnerabilities, generate_remediation_plan)
0040 |     
0041 |     No maneja parsing - delega a LLMResponseParser
0042 |     """
0043 |     
0044 |     def __init__(self, primary_provider: str = "watsonx", enable_debug: bool = False):
0045 |         """
0046 |         Initialize LLM Client
0047 |         
0048 |         Args:
0049 |             primary_provider: LLM provider ("watsonx" or "openai")
0050 |             enable_debug: Enable debug mode with detailed logging
0051 |         """
0052 |         self.api_key = os.getenv("RESEARCH_API_KEY", "")
0053 |         self.primary_provider = primary_provider
0054 |         self.base_url = "https://ia-research-dev.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud"
0055 |         self.timeout = 300  # 5 minutos
0056 |         self.user_email = os.getenv("LLM_USER_EMAIL", "franciscojavier.suarez_css@research.com")
0057 |         
0058 |         # Configuración de retry
0059 |         self.max_retries = 3
0060 |         self.retry_delay_base = 2  # segundos
0061 |         
0062 |         # Debug mode
0063 |         self.debug_enabled = enable_debug
0064 |         self.debugger = None
0065 |         
0066 |         # Parser y prompt manager
0067 |         self.parser = LLMResponseParser(debug_enabled=enable_debug)
0068 |         self.prompt_manager = PromptManager()
0069 |         
0070 |         # Configurar sesión HTTP
0071 |         self.session = requests.Session()
0072 |         self.session.headers.update({
0073 |             "Content-Type": "application/json",
0074 |             "x-api-key": self.api_key
0075 |         })
0076 |         
0077 |         # Endpoints según provider
0078 |         self.endpoints = {
0079 |             "watsonx": "/research/llm/wx/clients",
0080 |             "openai": "/research/llm/openai/clients"
0081 |         }
0082 |         
0083 |         # Validación de API key
0084 |         if not self.api_key:
0085 |             raise ValueError("RESEARCH_API_KEY environment variable is required")
0086 |         
0087 |         logger.info(f"🤖 LLM Client initialized: {self.primary_provider}")
0088 |         logger.debug(f"   Base URL: {self.base_url}")
0089 |         logger.debug(f"   Timeout: {self.timeout}s")
0090 |         logger.debug(f"   Max retries: {self.max_retries}")
0091 |     
0092 |     
0093 |     # ============================================================================
0094 |     # DEBUG MODE CONTROL
0095 |     # ============================================================================
0096 |     
0097 |     def enable_debug_mode(self):
0098 |         """Habilitar modo debug con logging detallado"""
0099 |         self.debug_enabled = True
0100 |         self.parser.debug_enabled = True
0101 |         
0102 |         try:
0103 |             from debug.llm_debugger import get_debugger
0104 |             self.debugger = get_debugger()
0105 |             logger.info("🔍 Debug mode ENABLED for LLM Client")
0106 |         except ImportError:
0107 |             logger.warning("⚠️ Debug module not available")
0108 |             self.debug_enabled = False
0109 |     
0110 |     
0111 |     def disable_debug_mode(self):
0112 |         """Deshabilitar modo debug"""
0113 |         self.debug_enabled = False
0114 |         self.parser.debug_enabled = False
0115 |         self.debugger = None
0116 |         logger.info("🔍 Debug mode DISABLED for LLM Client")
0117 |     
0118 |     
0119 |     # ============================================================================
0120 |     # PUBLIC API - HIGH-LEVEL METHODS
0121 |     # ============================================================================
0122 |     
0123 |     async def analyze_vulnerabilities(self, 
0124 |                                      vulnerabilities_data: str,
0125 |                                      language: Optional[str] = None,
0126 |                                      framework: Optional[str] = None) -> TriageResult:
0127 |         """
0128 |         Analizar vulnerabilidades usando Research API
0129 |         
0130 |         Args:
0131 |             vulnerabilities_ Datos de vulnerabilidades en formato texto
0132 |             language: Lenguaje de programación (opcional)
0133 |             framework: Framework utilizado (opcional)
0134 |             
0135 |         Returns:
0136 |             TriageResult con decisiones de clasificación
0137 |             
0138 |         Raises:
0139 |             LLMError: Si el análisis falla después de reintentos
0140 |         """
0141 |         
0142 |         try:
0143 |             logger.info(f"🔍 Starting vulnerability triage analysis")
0144 |             logger.debug(f"   Language: {language or 'Auto-detect'}")
0145 |             logger.debug(f"   Data length: {len(vulnerabilities_data)} chars")
0146 |             
0147 |             # Obtener prompt optimizado
0148 |             system_prompt = self.prompt_manager.get_triage_system_prompt(language=language)
0149 |             logger.info(f"📝 Using enhanced triage prompt ({len(system_prompt)} chars)")
0150 |             
0151 |             # Construir mensaje completo
0152 |             full_message = self._build_triage_message(system_prompt, vulnerabilities_data)
0153 |             
0154 |             # Llamar a Research API con retry
0155 |             start_time = time.time()
0156 |             response = await self._call_research_api_with_retry(
0157 |                 message=full_message,
0158 |                 temperature=0.1,
0159 |                 operation_name="triage_analysis"
0160 |             )
0161 |             duration = time.time() - start_time
0162 |             
0163 |             logger.info(f"✅ Triage response received in {duration:.2f}s")
0164 |             
0165 |             # Log debug si está habilitado
0166 |             if self.debug_enabled and self.debugger:
0167 |                 self.debugger.log_triage_analysis(
0168 |                     vulnerabilities_data=vulnerabilities_data,
0169 |                     system_prompt=system_prompt,
0170 |                     response=response,
0171 |                     duration=duration
0172 |                 )
0173 |             
0174 |             # Parsear respuesta (delegar a parser)
0175 |             result = self.parser.parse_triage_response(response, vulnerabilities_data)
0176 |             
0177 |             logger.info(f"✅ Triage completed successfully")
0178 |             logger.info(f"   Total analyzed: {result.total_analyzed}")
0179 |             logger.info(f"   Confirmed: {result.confirmed_count}")
0180 |             logger.info(f"   False positives: {result.false_positive_count}")
0181 |             logger.info(f"   Needs review: {result.needs_review_count}")
0182 |             
0183 |             return result
0184 |             
0185 |         except Exception as e:
0186 |             logger.error(f"❌ LLM triage analysis failed: {e}")
0187 |             logger.exception("Full traceback:")
0188 |             raise LLMError(f"Triage analysis failed: {e}")
0189 |     
0190 |     
0191 |     async def generate_remediation_plan(self, 
0192 |                                        vulnerability_data: str,
0193 |                                        vuln_type: str = None, 
0194 |                                        language: Optional[str] = None,
0195 |                                        severity: str = "HIGH") -> RemediationPlan:
0196 |         """
0197 |         Generar plan de remediación usando Research API
0198 |         
0199 |         Args:
0200 |             vulnerability_ Datos de la vulnerabilidad
0201 |             vuln_type: Tipo de vulnerabilidad
0202 |             language: Lenguaje de programación
0203 |             severity: Nivel de severidad
0204 |             
0205 |         Returns:
0206 |             RemediationPlan con pasos detallados
0207 |             
0208 |         Raises:
0209 |             LLMError: Si la generación falla después de reintentos
0210 |         """
0211 |         
0212 |         try:
0213 |             logger.info(f"🛠️ Starting remediation plan generation")
0214 |             logger.debug(f"   Type: {vuln_type or 'Unknown'}")
0215 |             logger.debug(f"   Language: {language or 'Generic'}")
0216 |             logger.debug(f"   Severity: {severity}")
0217 |             
0218 |             # Obtener prompt optimizado
0219 |             system_prompt = self.prompt_manager.get_remediation_system_prompt(
0220 |                 vuln_type=vuln_type or "Security Issue",
0221 |                 language=language,
0222 |                 severity=severity
0223 |             )
0224 |             logger.info(f"📝 Using enhanced remediation prompt ({len(system_prompt)} chars)")
0225 |             
0226 |             # Construir mensaje completo
0227 |             full_message = self._build_remediation_message(system_prompt, vulnerability_data)
0228 |             
0229 |             # Llamar a Research API con retry
0230 |             start_time = time.time()
0231 |             response = await self._call_research_api_with_retry(
0232 |                 message=full_message,
0233 |                 temperature=0.2,  # Ligeramente más alta para creatividad
0234 |                 operation_name="remediation_generation"
0235 |             )
0236 |             duration = time.time() - start_time
0237 |             
0238 |             logger.info(f"✅ Remediation response received in {duration:.2f}s")
0239 |             
0240 |             # Log debug si está habilitado
0241 |             if self.debug_enabled and self.debugger:
0242 |                 self.debugger.log_remediation_generation(
0243 |                     vulnerability_data=vulnerability_data,
0244 |                     system_prompt=system_prompt,
0245 |                     response=response,
0246 |                     duration=duration
0247 |                 )
0248 |             
0249 |             # Parsear respuesta (delegar a parser)
0250 |             result = self.parser.parse_remediation_response(response, vuln_type, language)
0251 |             
0252 |             logger.info(f"✅ Remediation plan created successfully")
0253 |             logger.info(f"   Priority: {result.priority_level}")
0254 |             logger.info(f"   Steps: {len(result.steps)}")
0255 |             logger.info(f"   Estimated hours: {result.total_estimated_hours}h")
0256 |             logger.info(f"   Complexity: {result.complexity_score}/10")
0257 |             
0258 |             return result
0259 |             
0260 |         except Exception as e:
0261 |             logger.error(f"❌ LLM remediation generation failed: {e}")
0262 |             logger.exception("Full traceback:")
0263 |             raise LLMError(f"Remediation generation failed: {e}")
0264 |     
0265 |     
0266 |     # ============================================================================
0267 |     # RESEARCH API COMMUNICATION
0268 |     # ============================================================================
0269 |     
0270 |     async def _call_research_api_with_retry(self, 
0271 |                                           message: str, 
0272 |                                           temperature: float = 0.1,
0273 |                                           operation_name: str = "llm_call") -> str:
0274 |         """
0275 |         Llamar a Research API con lógica de reintento
0276 |         
0277 |         Args:
0278 |             message: Mensaje completo para enviar
0279 |             temperature: Temperatura del LLM (0.0-1.0)
0280 |             operation_name: Nombre de la operación (para logging)
0281 |             
0282 |         Returns:
0283 |             Respuesta del LLM (texto limpio)
0284 |             
0285 |         Raises:
0286 |             LLMError: Si todos los intentos fallan
0287 |         """
0288 |         
0289 |         last_error = None
0290 |         
0291 |         for attempt in range(self.max_retries):
0292 |             try:
0293 |                 logger.info(f"🔄 Attempt {attempt + 1}/{self.max_retries} - {operation_name}")
0294 |                 
0295 |                 response = await self._call_research_api(message, temperature)
0296 |                 
0297 |                 # Si llegamos aquí, el llamado fue exitoso
0298 |                 if attempt > 0:
0299 |                     logger.info(f"✅ Succeeded on retry {attempt + 1}")
0300 |                 
0301 |                 return response
0302 |                 
0303 |             except LLMError as e:
0304 |                 last_error = e
0305 |                 
0306 |                 if attempt < self.max_retries - 1:
0307 |                     # Calcular delay con backoff exponencial
0308 |                     delay = self.retry_delay_base ** (attempt + 1)
0309 |                     logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
0310 |                     logger.warning(f"⏳ Retrying in {delay}s...")
0311 |                     await asyncio.sleep(delay)
0312 |                 else:
0313 |                     # Último intento falló
0314 |                     logger.error(f"❌ All {self.max_retries} attempts failed")
0315 |                     raise
0316 |         
0317 |         # Si llegamos aquí, todos los reintentos fallaron
0318 |         raise last_error or LLMError(f"All {self.max_retries} attempts failed")
0319 |     
0320 |     
0321 |     async def _call_research_api(self, message: str, temperature: float = 0.1) -> str:
0322 |         """
0323 |         Llamar a Research API (single attempt)
0324 |         
0325 |         Args:
0326 |             message: Mensaje completo
0327 |             temperature: Temperatura del LLM
0328 |             
0329 |         Returns:
0330 |             Contenido de la respuesta (limpio)
0331 |             
0332 |         Raises:
0333 |             LLMError: Si la llamada falla
0334 |         """
0335 |         
0336 |         url = f"{self.base_url}{self.endpoints[self.primary_provider]}"
0337 |         session_uuid = str(uuid.uuid4())
0338 |         
0339 |         # Preparar payload
0340 |         payload = {
0341 |             "message": {
0342 |                 "role": "user",
0343 |                 "content": message
0344 |             },
0345 |             "temperature": temperature,
0346 |             "model": "meta-llama/llama-3-3-70b-instruct",
0347 |             "prompt": None,
0348 |             "uuid": session_uuid,
0349 |             "language": "es",
0350 |             "user": self.user_email
0351 |         }
0352 |         
0353 |         start_time = time.time()
0354 |         
0355 |         try:
0356 |             logger.info(f"📡 Calling Research API")
0357 |             logger.debug(f"   URL: {url}")
0358 |             logger.debug(f"   Provider: {self.primary_provider}")
0359 |             logger.debug(f"   Temperature: {temperature}")
0360 |             logger.debug(f"   Message length: {len(message):,} chars")
0361 |             logger.debug(f"   Session UUID: {session_uuid}")
0362 |             
0363 |             # Hacer la llamada HTTP
0364 |             response = self.session.post(url, json=payload, timeout=self.timeout)
0365 |             duration = time.time() - start_time
0366 |             
0367 |             # Logging de respuesta
0368 |             logger.info(f"📡 HTTP Status: {response.status_code}")
0369 |             logger.info(f"📏 Response size: {len(response.text):,} chars")
0370 |             logger.info(f"⏱️ Duration: {duration:.2f}s")
0371 |             logger.debug(f"   Response headers: {dict(response.headers)}")
0372 |             
0373 |             # Log preview de respuesta
0374 |             preview_length = min(300, len(response.text))
0375 |             logger.debug(f"   Response preview (first {preview_length} chars):")
0376 |             logger.debug(f"   {response.text[:preview_length]}")
0377 |             
0378 |             # Validar status code
0379 |             if response.status_code != 200:
0380 |                 error_msg = f"HTTP {response.status_code}: {response.text[:500]}"
0381 |                 logger.error(f"❌ Research API error: {error_msg}")
0382 |                 raise LLMError(f"Research API failed: {error_msg}")
0383 |             
0384 |             response_text = response.text
0385 |             
0386 |             # Validar que no esté vacía
0387 |             if not response_text or response_text.strip() == "":
0388 |                 logger.error("❌ Empty response from Research API")
0389 |                 raise LLMError("Empty response from LLM")
0390 |             
0391 |             # Intentar parsear como JSON para extraer el contenido real
0392 |             try:
0393 |                 result = response.json()
0394 |                 logger.debug(f"   Response is valid JSON")
0395 |                 logger.debug(f"   JSON keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
0396 |             except json.JSONDecodeError as e:
0397 |                 logger.warning(f"⚠️ Response is not JSON (using as plain text): {e}")
0398 |                 result = response_text
0399 |             
0400 |             # Extraer contenido según la estructura de respuesta
0401 |             content = self._extract_content_from_response(result)
0402 |             
0403 |             # Validar contenido extraído
0404 |             if not content or (isinstance(content, str) and content.strip() == ""):
0405 |                 logger.error("❌ No content in LLM response")
0406 |                 logger.error(f"   Original result type: {type(result)}")
0407 |                 logger.error(f"   Original result: {str(result)[:500]}")
0408 |                 raise LLMError("No content in LLM response")
0409 |             
0410 |             logger.info(f"✅ Content extracted: {len(content):,} chars")
0411 |             logger.debug(f"   Content preview (first 300 chars):")
0412 |             logger.debug(f"   {content[:300]}")
0413 |             logger.info(f"✅ Research API call successful - {duration:.2f}s")
0414 |             
0415 |             return content
0416 |             
0417 |         except requests.exceptions.Timeout:
0418 |             duration = time.time() - start_time
0419 |             error_msg = f"Research API timeout after {self.timeout}s"
0420 |             logger.error(f"❌ {error_msg}")
0421 |             raise LLMError(error_msg)
0422 |             
0423 |         except requests.exceptions.ConnectionError as e:
0424 |             duration = time.time() - start_time
0425 |             error_msg = f"Research API connection error: {e}"
0426 |             logger.error(f"❌ {error_msg}")
0427 |             raise LLMError(error_msg)
0428 |             
0429 |         except LLMError:
0430 |             # Re-raise LLMError sin envolver
0431 |             raise
0432 |             
0433 |         except Exception as e:
0434 |             duration = time.time() - start_time
0435 |             error_msg = f"Research API unexpected error: {e}"
0436 |             logger.error(f"❌ {error_msg}")
0437 |             logger.exception("Full traceback:")
0438 |             raise LLMError(error_msg)
0439 |     
0440 |     
0441 |     def _extract_content_from_response(self, result: Any) -> str:
0442 |         """
0443 |         Extraer contenido real de la estructura de respuesta API
0444 |         
0445 |         Args:
0446 |             result: Respuesta cruda (dict, str, etc)
0447 |             
0448 |         Returns:
0449 |             Contenido extraído como string
0450 |         """
0451 |         
0452 |         if isinstance(result, dict):
0453 |             logger.debug("Response is dict, searching for content field...")
0454 |             
0455 |             # Posibles campos donde puede estar el contenido
0456 |             possible_keys = [
0457 |                 'content', 'response', 'message', 'text', 
0458 |                 'output', 'result', 'data', 'answer', 'completion'
0459 |             ]
0460 |             
0461 |             for key in possible_keys:
0462 |                 if key in result and result[key]:
0463 |                     value = result[key]
0464 |                     
0465 |                     # Si el valor es un dict, extraer recursivamente
0466 |                     if isinstance(value, dict):
0467 |                         nested_content = self._extract_content_from_response(value)
0468 |                         if nested_content:
0469 |                             logger.info(f"✅ Found content in nested field: {key}")
0470 |                             return nested_content
0471 |                     elif value:
0472 |                         logger.info(f"✅ Found content in field: {key}")
0473 |                         return str(value)
0474 |             
0475 |             # Si no encontramos campo conocido, serializar todo el dict
0476 |             logger.warning(f"⚠️ No standard content field found")
0477 |             logger.debug(f"   Available fields: {list(result.keys())}")
0478 |             return json.dumps(result)
0479 |         
0480 |         else:
0481 |             return str(result)
0482 |     
0483 |     
0484 |     # ============================================================================
0485 |     # MESSAGE BUILDERS
0486 |     # ============================================================================
0487 |     
0488 |     def _build_triage_message(self, system_prompt: str, vulnerabilities_data: str) -> str:
0489 |         """
0490 |         Construir mensaje completo para triage
0491 |         
0492 |         Args:
0493 |             system_prompt: Prompt del sistema
0494 |             vulnerabilities_ Datos de vulnerabilidades
0495 |             
0496 |         Returns:
0497 |             Mensaje formateado
0498 |         """
0499 |         
0500 |         return f"""{system_prompt}
0501 | 
0502 | # VULNERABILITIES TO ANALYZE
0503 | 
0504 | {vulnerabilities_data}
0505 | 
0506 | # CRITICAL INSTRUCTIONS
0507 | 
0508 | 1. Return ONLY valid JSON - NO markdown code blocks
0509 | 2. Do NOT include any text before or after the JSON object
0510 | 3. Ensure all strings are properly escaped
0511 | 4. Follow the exact schema provided in the system prompt
0512 | 5. Each decision MUST have all required fields
0513 | 
0514 | Now analyze the vulnerabilities above and return the JSON response:"""
0515 |     
0516 |     
0517 |     def _build_remediation_message(self, system_prompt: str, vulnerability_data: str) -> str:
0518 |         """
0519 |         Construir mensaje completo para remediation
0520 |         
0521 |         Args:
0522 |             system_prompt: Prompt del sistema
0523 |             vulnerability_ Datos de la vulnerabilidad
0524 |             
0525 |         Returns:
0526 |             Mensaje formateado
0527 |         """
0528 |         
0529 |         return f"""{system_prompt}
0530 | 
0531 | # VULNERABILITY DATA TO ANALYZE
0532 | 
0533 | {vulnerability_data}
0534 | 
0535 | # CRITICAL INSTRUCTIONS
0536 | 
0537 | 1. Return ONLY valid JSON - NO markdown wrapper (no ```json)
0538 | 2. Do NOT include any text before or after the JSON
0539 | 3. Include ALL required fields in the schema
0540 | 4. Each step MUST have detailed description (minimum 100 words)
0541 | 5. Include specific code examples with before/after
0542 | 6. Provide concrete validation tests
0543 | 7. NO placeholder text like "implement security fix"
0544 | 8. Ensure all strings are properly escaped
0545 | 9. Keep individual string fields under 1000 characters
0546 | 10. If a field needs more text, split into structured object
0547 | 
0548 | Now generate the remediation plan following the exact JSON schema:"""
0549 | 
0550 | 
0551 | # ============================================================================
0552 | # FACTORY FUNCTIONS
0553 | # ============================================================================
0554 | 
0555 | def create_llm_client(provider: str = "watsonx", enable_debug: bool = False) -> LLMClient:
0556 |     """
0557 |     Factory function para crear cliente LLM
0558 |     
0559 |     Args:
0560 |         provider: Provider a usar ("watsonx" o "openai")
0561 |         enable_debug: Habilitar modo debug
0562 |         
0563 |     Returns:
0564 |         LLMClient configurado
0565 |         
0566 |     Example:
0567 |         >>> client = create_llm_client(provider="watsonx", enable_debug=True)
0568 |         >>> result = await client.analyze_vulnerabilities(data)
0569 |     """
0570 |     return LLMClient(primary_provider=provider, enable_debug=enable_debug)
0571 | 
0572 | 
0573 | def validate_api_key() -> bool:
0574 |     """
0575 |     Validar que la API key esté configurada
0576 |     
0577 |     Returns:
0578 |         True si la API key está presente
0579 |     """
0580 |     api_key = os.getenv("RESEARCH_API_KEY", "")
0581 |     return bool(api_key and len(api_key) > 0)
0582 | 
0583 | 
0584 | # ============================================================================
0585 | # TESTING & DEBUGGING
0586 | # ============================================================================
0587 | 
0588 | async def test_llm_connection(provider: str = "watsonx") -> Dict[str, Any]:
0589 |     """
0590 |     Probar conexión con el LLM
0591 |     
0592 |     Args:
0593 |         provider: Provider a probar
0594 |         
0595 |     Returns:
0596 |         Dict con resultados de la prueba
0597 |         
0598 |     Example:
0599 |         >>> result = await test_llm_connection("watsonx")
0600 |         >>> print(f"Status: {result['status']}")
0601 |     """
0602 |     
0603 |     try:
0604 |         logger.info(f"🧪 Testing LLM connection to {provider}...")
0605 |         
0606 |         client = LLMClient(primary_provider=provider)
0607 |         
0608 |         # Test simple: pedir que devuelva JSON básico
0609 |         test_message = """Return only this JSON object with no additional text:
0610 | {
0611 |   "test": "success",
0612 |   "timestamp": "2024-01-01T00:00:00Z",
0613 |   "message": "Connection test successful"
0614 | }"""
0615 |         
0616 |         start_time = time.time()
0617 |         response = await client._call_research_api(test_message, temperature=0.0)
0618 |         duration = time.time() - start_time
0619 |         
0620 |         # Intentar parsear
0621 |         cleaned = client.parser.clean_json_response(response)
0622 |         parsed = json.loads(cleaned)
0623 |         
0624 |         result = {
0625 |             "status": "success",
0626 |             "provider": provider,
0627 |             "duration_seconds": round(duration, 2),
0628 |             "response_length": len(response),
0629 |             "parsed_successfully": True,
0630 |             "response_preview": str(parsed)[:200]
0631 |         }
0632 |         
0633 |         logger.info(f"✅ Connection test successful")
0634 |         return result
0635 |         
0636 |     except Exception as e:
0637 |         logger.error(f"❌ Connection test failed: {e}")
0638 |         return {
0639 |             "status": "failed",
0640 |             "provider": provider,
0641 |             "error": str(e),
0642 |             "error_type": type(e).__name__
0643 |         }
0644 | 
0645 | 
0646 | # ============================================================================
0647 | # MAIN - FOR TESTING
0648 | # ============================================================================
0649 | 
0650 | if __name__ == "__main__":
0651 |     """
0652 |     Test básico del cliente LLM
0653 |     
0654 |     Usage:
0655 |         python infrastructure/llm/client.py
0656 |     """
0657 |     
0658 |     import asyncio
0659 |     from shared.logger import setup_logging
0660 |     
0661 |     # Setup logging
0662 |     setup_logging(log_level="DEBUG")
0663 |     
0664 |     async def main():
0665 |         print("\n" + "="*70 + "\n")
0666 |         print("🤖 LLM Client Test Suite")
0667 |         print("="*70 + "\n")
0668 |         
0669 |         # Test 1: Validar API key
0670 |         print("1️⃣ Testing API key validation...")
0671 |         if validate_api_key():
0672 |             print("   ✅ API key is configured\n")
0673 |         else:
0674 |             print("   ❌ API key is NOT configured")
0675 |             print("   Set RESEARCH_API_KEY environment variable\n")
0676 |             return
0677 |         
0678 |         # Test 2: Test conexión
0679 |         print("2️⃣ Testing connection...")
0680 |         result = await test_llm_connection("watsonx")
0681 |         print(f"   Status: {result['status']}")
0682 |         if result['status'] == 'success':
0683 |             print(f"   Duration: {result['duration_seconds']}s")
0684 |             print(f"   Response length: {result['response_length']} chars")
0685 |         else:
0686 |             print(f"   Error: {result.get('error', 'Unknown')}\n")
0687 |             return
0688 |         
0689 |         # Test 3: Test triage simple
0690 |         print("\n3️⃣ Testing triage analysis...")
0691 |         client = LLMClient(primary_provider="watsonx", enable_debug=False)
0692 |         
0693 |         test_vulnerabilities = """## VULNERABILITY 1
0694 | - ID: test-vuln-001
0695 | - TYPE: SQL Injection
0696 | - SEVERITY: HIGH
0697 | - FILE: test.py:42
0698 | - TITLE: SQL Injection in login function
0699 | - DESCRIPTION: User input is directly concatenated into SQL query without sanitization
0700 | - CODE: cursor.execute("SELECT * FROM users WHERE username='" + username + "'")"""
0701 |         
0702 |         try:
0703 |             result = await client.analyze_vulnerabilities(test_vulnerabilities, language="python")
0704 |             print(f"   ✅ Triage successful")
0705 |             print(f"   Total analyzed: {result.total_analyzed}")
0706 |             print(f"   Confirmed: {result.confirmed_count}")
0707 |             print(f"   False positives: {result.false_positive_count}")
0708 |         except Exception as e:
0709 |             print(f"   ❌ Triage failed: {e}")
0710 |         
0711 |         # Test 4: Test remediation simple
0712 |         print("\n4️⃣ Testing remediation generation...")
0713 |         
0714 |         test_vulnerability = """## VULNERABILITY
0715 | - ID: test-vuln-001
0716 | - TYPE: SQL Injection
0717 | - SEVERITY: HIGH
0718 | - FILE: test.py:42
0719 | - TITLE: SQL Injection in login function
0720 | - DESCRIPTION: User input is directly concatenated into SQL query
0721 | - CODE: cursor.execute("SELECT * FROM users WHERE username='" + username + "'")"""
0722 |         
0723 |         try:
0724 |             result = await client.generate_remediation_plan(
0725 |                 test_vulnerability,
0726 |                 vuln_type="SQL Injection",
0727 |                 language="python",
0728 |                 severity="HIGH"
0729 |             )
0730 |             print(f"   ✅ Remediation successful")
0731 |             print(f"   Priority: {result.priority_level}")
0732 |             print(f"   Steps: {len(result.steps)}")
0733 |             print(f"   Estimated hours: {result.total_estimated_hours}h")
0734 |         except Exception as e:
0735 |             print(f"   ❌ Remediation failed: {e}")
0736 |         
0737 |         print("\n" + "="*70)
0738 |         print("✅ Test Suite Completed")
0739 |         print("="*70 + "\n")
0740 |     
0741 |     # Ejecutar tests
0742 |     asyncio.run(main())
0743 | 
```

---

### infrastructure\llm\exceptions.py

**Ruta:** `infrastructure\llm\exceptions.py`

```py
0001 | # infrastructure/llm/exceptions.py
0002 | """
0003 | 🚨 Excepciones específicas para LLM Client
0004 | """
0005 | 
0006 | class LLMClientError(Exception):
0007 |     """Error base para cliente LLM"""
0008 |     pass
0009 | 
0010 | class LLMConnectionError(LLMClientError):
0011 |     """Error de conexión con LLM"""
0012 |     pass
0013 | 
0014 | class LLMTimeoutError(LLMClientError):
0015 |     """Timeout en llamada LLM"""
0016 |     pass
0017 | 
0018 | class LLMParsingError(LLMClientError):
0019 |     """Error al parsear respuesta LLM"""
0020 |     def __init__(self, message: str, raw_response: str = None, partial_data: dict = None):
0021 |         self.raw_response = raw_response
0022 |         self.partial_data = partial_data
0023 |         super().__init__(message)
0024 | 
0025 | class LLMValidationError(LLMClientError):
0026 |     """Error de validación de respuesta LLM"""
0027 |     def __init__(self, message: str, missing_fields: list = None, available_fields: list = None):
0028 |         self.missing_fields = missing_fields or []
0029 |         self.available_fields = available_fields or []
0030 |         super().__init__(message)
```

---

### infrastructure\llm\prompts.py

**Ruta:** `infrastructure\llm\prompts.py`

```py
0001 | # infrastructure/llm/prompts.py
0002 | from typing import Optional
0003 | 
0004 | class PromptManager:
0005 |     """Gestión centralizada y optimizada de prompts"""
0006 |     
0007 |     def get_triage_system_prompt(self, language: Optional[str] = None) -> str:
0008 |         """System prompt optimizado para triaje"""
0009 |         model_name = self._get_model_name()
0010 |         
0011 |         return f"""You are a cybersecurity expert specializing in vulnerability analysis.
0012 | 
0013 | TASK: Analyze the provided vulnerabilities and classify each one as:
0014 | - "confirmed": Real security vulnerability that needs fixing
0015 | - "false_positive": Scanner false alarm, not a real issue  
0016 | - "needs_manual_review": Uncertain case requiring human expert review
0017 | 
0018 | CONTEXT: Language/Technology: {language or 'Unknown'}
0019 | 
0020 | OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
0021 | {{
0022 |   "decisions": [
0023 |     {{
0024 |       "vulnerability_id": "vuln_id_here",
0025 |       "decision": "confirmed|false_positive|needs_manual_review",
0026 |       "confidence_score": 0.0-1.0,
0027 |       "reasoning": "Brief technical explanation of your decision",
0028 |       "llm_model_used": "{model_name}"
0029 |     }}
0030 |   ],
0031 |   "analysis_summary": "Overall analysis summary",
0032 |   "llm_analysis_time_seconds": 1.5
0033 | }}
0034 | 
0035 | GUIDELINES:
0036 | - Be conservative: when uncertain, choose "needs_manual_review"
0037 | - Consider code context, severity, and vulnerability type
0038 | - Provide clear, technical reasoning
0039 | - Focus on actual exploitability, not theoretical risks"""
0040 | 
0041 |     def get_remediation_system_prompt(self, vuln_type: str, 
0042 |                                      language: Optional[str] = None,
0043 |                                      severity: str = "HIGH") -> str:
0044 |         """Sistema prompt mejorado para remediation - ACCIONABLE Y DETALLADO"""
0045 |         
0046 |         lang_guide = self._get_language_specific_remediation_guide(language)
0047 |         model_name = self._get_model_name()
0048 |         lang_or_generic = language or 'generic'
0049 |         
0050 |         return f"""You are a senior security engineer creating DETAILED, STEP-BY-STEP remediation plans that developers can implement immediately WITHOUT consulting additional documentation.
0051 | 
0052 | # CONTEXT
0053 | - Vulnerability Type: {vuln_type}
0054 | - Programming Language: {language or 'Not specified'}
0055 | - Severity Level: {severity}
0056 | - Target Audience: Mid-level developers (3-5 years experience)
0057 | - Expected Outcome: Production-ready secure code
0058 | 
0059 | # CRITICAL REQUIREMENTS FOR EACH STEP
0060 | 
0061 | Each remediation step MUST include:
0062 | 
0063 | 1. **Specific Title**: What exactly to do
0064 |    ❌ BAD: "Implement security fix"
0065 |    ✅ GOOD: "Replace string concatenation with FILE_VALIDATE_NAME function"
0066 | 
0067 | 2. **Detailed Description**: WHY this prevents the vulnerability (minimum 100 words)
0068 |    - Explain the security principle
0069 |    - Explain how the vulnerability is exploited
0070 |    - Explain how this fix prevents exploitation
0071 |    - Include edge cases handled
0072 | 
0073 | 3. **Complete Code Example**: BOTH vulnerable and fixed code
0074 |    - BEFORE: Exact code showing the vulnerability (5-10 lines with context)
0075 |    - AFTER: Complete working code with the fix (10-20 lines)
0076 |    - Include ALL necessary declarations
0077 |    - Include error handling and validation
0078 |    - Add inline comments explaining security improvements
0079 | 
0080 | 4. **Concrete Validation Test**: Specific test to verify the fix
0081 |    ❌ BAD: "Test that it works"
0082 |    ✅ GOOD: "Test with input='../../etc/passwd' and verify error 'Invalid filename' with return code 4"
0083 | 
0084 | 5. **Tools & Prerequisites**: What's needed to implement
0085 |    - Specific versions if relevant
0086 |    - Configuration requirements
0087 |    - Permissions needed
0088 | 
0089 | # OUTPUT FORMAT (STRICT JSON)
0090 | 
0091 | Return ONLY valid JSON (no markdown, no code block wrapper):
0092 | 
0093 | {{
0094 |   "vulnerability_id": "exact_id_from_input",
0095 |   "vulnerability_type": "{vuln_type}",
0096 |   "priority_level": "immediate|high|medium|low",
0097 |   "estimated_effort": "30min-1h|1-2h|2-4h|1-2 days",
0098 |   
0099 |   "steps": [
0100 |     {{
0101 |       "step_number": 1,
0102 |       "title": "Action-oriented title (verb + specific action)",
0103 |       "description": "Detailed explanation (minimum 100 words) covering: What (specific change), Why (security principle), How (implementation), Edge cases handled",
0104 |       "code_example": "Complete code showing BEFORE and AFTER with inline security comments",
0105 |       "validation_test": "SPECIFIC TEST: Input 'malicious_value' → Expected: 'error_message'",
0106 |       "estimated_minutes": 30,
0107 |       "difficulty": "easy|medium|hard",
0108 |       "tools_required": ["Tool name version X.Y"],
0109 |       "prerequisites": ["Required permission or configuration"]
0110 |     }}
0111 |   ],
0112 |   
0113 |   "verification_checklist": [
0114 |     "✓ Specific verification item with measurable criteria"
0115 |   ],
0116 |   
0117 |   "risk_if_not_fixed": "CONCRETE IMPACT: Attack scenario, data at risk, business impact, compliance violations, real CVE example, CVSS score",
0118 |   
0119 |   "common_mistakes": [
0120 |     "❌ Specific mistake with explanation why it fails and correct approach"
0121 |   ],
0122 |   
0123 |   "security_testing": {{
0124 |     "unit_tests": "Copy-paste test code with expected results",
0125 |     "integration_tests": "Step-by-step test procedure",
0126 |     "penetration_tests": "Specific payloads with expected blocking behavior"
0127 |   }},
0128 |   
0129 |   "references": [
0130 |     "https://owasp.org/specific-page",
0131 |     "https://cwe.mitre.org/data/definitions/[number].html"
0132 |   ],
0133 |   
0134 |   "total_estimated_hours": 2.5,
0135 |   "complexity_score": 6.5,
0136 |   "llm_model_used": "{model_name}",
0137 |   
0138 |   "dependencies": [
0139 |     "Specific library name==version or configuration requirement"
0140 |   ],
0141 |   
0142 |   "rollback_plan": "DETAILED ROLLBACK: Backup steps, monitoring metrics, rollback triggers, rollback procedure, time limit"
0143 | }}
0144 | 
0145 | # LANGUAGE-SPECIFIC GUIDANCE
0146 | 
0147 | {lang_guide}
0148 | 
0149 | # QUALITY CHECKS BEFORE RESPONDING
0150 | 
0151 | Before sending your response, verify:
0152 | - [ ] Each step has code example with BOTH before AND after
0153 | - [ ] Each "after" code is COMPLETE (can copy-paste and run)
0154 | - [ ] Each step description has at least 100 words
0155 | - [ ] Validation tests are SPECIFIC with exact inputs and expected outputs
0156 | - [ ] No generic phrases like "implement security" or "add validation"
0157 | - [ ] Risk section mentions specific CVE or real breach example
0158 | - [ ] All code includes error handling
0159 | - [ ] Prerequisites list exact requirements
0160 | 
0161 | Now analyze the vulnerability data below and create a comprehensive remediation plan following this template:"""
0162 | 
0163 |     def _get_language_specific_remediation_guide(self, language: Optional[str]) -> str:
0164 |         """Retorna guía detallada específica del lenguaje"""
0165 |         
0166 |         if not language:
0167 |             return ""
0168 |         
0169 |         lang_lower = language.lower()
0170 |         
0171 |         if 'abap' in lang_lower:
0172 |             return """
0173 | ## ABAP-SPECIFIC REMEDIATION PATTERNS
0174 | 
0175 | ### Directory Traversal Prevention:
0176 | 1. **Use logical filenames** (transaction FILE)
0177 | 2. **Validate with FILE_VALIDATE_NAME and FILE_GET_NAME**
0178 | 3. **Character validation:** `IF filename CA '/..\\\\':\\x00'. " Block`
0179 | 4. **Authorization check:** AUTHORITY-CHECK OBJECT 'S_DATASET' ID 'ACTVT' FIELD '34'
0180 | 5. **Security logging:** Use BAL_LOG_CREATE and BAL_LOG_MSG_ADD
0181 | 
0182 | ### SQL Injection Prevention:
0183 | 1. **NEVER use dynamic WHERE with concatenation**
0184 | 2. **Use host variables:** SELECT * WHERE username = @lv_username
0185 | 3. **Use SELECT-OPTIONS** for complex dynamic queries
0186 | 
0187 | ### Best Practices:
0188 | - Always check sy-subrc after function calls
0189 | - Use MESSAGE TYPE 'E' for security failures
0190 | - Log all security events to application log (BAL)
0191 | - Run Code Vulnerability Analyzer (CVA) regularly
0192 | """
0193 |         
0194 |         elif 'python' in lang_lower:
0195 |             return """
0196 | ## PYTHON-SPECIFIC REMEDIATION PATTERNS
0197 | 
0198 | ### Path Traversal Prevention:
0199 | 1. **Use pathlib.Path.resolve()** with is_relative_to() check
0200 | 2. **Use secure_filename()** from werkzeug
0201 | 3. **Validate with regex:** `^[a-zA-Z0-9_-]+\\.[a-z]{2,4}$`
0202 | 
0203 | ### SQL Injection Prevention:
0204 | 1. **Django ORM:** Use .filter(), never .raw() with f-strings
0205 | 2. **SQLAlchemy:** Use bound parameters with text()
0206 | 3. **Flask-SQLAlchemy:** Use parameterized queries
0207 | 
0208 | ### Best Practices:
0209 | - Use framework auto-escaping for XSS prevention
0210 | - Validate all user inputs with Pydantic or similar
0211 | - Use environment variables for secrets (never hardcode)
0212 | """
0213 |         
0214 |         elif 'java' in lang_lower:
0215 |             return """
0216 | ## JAVA-SPECIFIC REMEDIATION PATTERNS
0217 | 
0218 | ### SQL Injection Prevention:
0219 | 1. **Always use PreparedStatement** (never Statement)
0220 | 2. **JPA:** Use named parameters (:name syntax)
0221 | 3. **Hibernate:** Avoid native queries with concatenation
0222 | 
0223 | ### Path Traversal Prevention:
0224 | 1. **Use Path.resolve()** with startsWith() check
0225 | 2. **Normalize paths** before validation
0226 | 3. **Check canonical path** stays within base directory
0227 | 
0228 | ### Best Practices:
0229 | - Disable XXE with DocumentBuilderFactory features
0230 | - Use @PreAuthorize for method-level security
0231 | - Enable CSRF protection in Spring Security
0232 | """
0233 |         
0234 |         else:
0235 |             return ""
0236 |     
0237 |     def _get_model_name(self) -> str:
0238 |         """Get current model name for tracking"""
0239 |         return "meta-llama/llama-3-3-70b-instruct"
```

---

### infrastructure\llm\response_parser.py

**Ruta:** `infrastructure\llm\response_parser.py`

```py
0001 | # infrastructure/llm/response_parser.py
0002 | """
0003 | LLM Response Parser - Cleaning, validation and parsing of JSON responses
0004 | 
0005 | Features:
0006 | - Advanced cleaning with markdown wrappers
0007 | - Intelligent extraction with stack balancing
0008 | - Pre-parsing validation
0009 | - Parsing to Pydantic models
0010 | - Invalid escape correction
0011 | """
0012 | 
0013 | import json
0014 | import re
0015 | import logging
0016 | import time
0017 | from typing import Dict, Any, Optional, List
0018 | 
0019 | from core.models import (
0020 |     TriageResult, 
0021 |     RemediationPlan, 
0022 |     TriageDecision, 
0023 |     AnalysisStatus, 
0024 |     RemediationStep, 
0025 |     VulnerabilityType
0026 | )
0027 | from core.exceptions import LLMError
0028 | 
0029 | logger = logging.getLogger(__name__)
0030 | 
0031 | 
0032 | class LLMResponseParser:
0033 |     """
0034 |     Specialized parser for LLM responses
0035 |     
0036 |     Responsibilities:
0037 |     - Cleaning JSON with markdown/noise
0038 |     - JSON structure validation
0039 |     - Intelligent JSON extraction
0040 |     - Parsing to domain models (TriageResult, RemediationPlan)
0041 |     """
0042 |     
0043 |     def __init__(self, debug_enabled: bool = False):
0044 |         self.debug_enabled = debug_enabled
0045 |     
0046 |     
0047 |     # ============================================================================
0048 |     # PUBLIC API - PARSING METHODS
0049 |     # ============================================================================
0050 |     
0051 |     def parse_triage_response(self, llm_response: str, original_data: str = None) -> TriageResult:
0052 |         """
0053 |         Parse LLM response to TriageResult
0054 |         
0055 |         Args:
0056 |             llm_response: Raw LLM response
0057 |             original_ Original data (for context in errors)
0058 |             
0059 |         Returns:
0060 |             Validated TriageResult
0061 |             
0062 |         Raises:
0063 |             LLMError: If parsing fails after recovery attempts
0064 |         """
0065 |         
0066 |         logger.info(f"Parsing triage response ({len(llm_response):,} chars)...")
0067 |         
0068 |         try:
0069 |             # Step 1: Clean response
0070 |             cleaned = self.clean_json_response(llm_response)
0071 |             
0072 |             # Step 2: Validate structure
0073 |             validation = self.validate_json_structure(cleaned)
0074 |             
0075 |             if not validation['is_valid']:
0076 |                 logger.error(f"JSON structure validation failed:")
0077 |                 for error in validation['errors']:
0078 |                     logger.error(f"   - {error}")
0079 |                 
0080 |                 # Attempt recovery
0081 |                 logger.info("Attempting recovery...")
0082 |                 extracted = self.extract_json(
0083 |                     cleaned, 
0084 |                     required_fields=['decisions', 'analysis_summary']
0085 |                 )
0086 |                 
0087 |                 if extracted:
0088 |                     cleaned = extracted
0089 |                     logger.info("Recovery successful")
0090 |                 else:
0091 |                     raise LLMError(f"JSON structure invalid: {validation['errors']}")
0092 |             
0093 |             # Step 3: Parse JSON
0094 |             try:
0095 |                 response_data = json.loads(cleaned)
0096 |                 logger.info(f"JSON parsed successfully")
0097 |             except json.JSONDecodeError as e:
0098 |                 logger.error(f"JSON parsing failed: {e}")
0099 |                 
0100 |                 # Last recovery attempt
0101 |                 extracted = self.extract_json(
0102 |                     llm_response,
0103 |                     required_fields=['decisions', 'analysis_summary']
0104 |                 )
0105 |                 
0106 |                 if extracted:
0107 |                     try:
0108 |                         response_data = json.loads(extracted)
0109 |                         logger.info("Recovery parse successful")
0110 |                     except Exception:
0111 |                         raise LLMError(f"Failed to parse triage response: {e}")
0112 |                 else:
0113 |                     raise LLMError(f"Failed to parse triage response: {e}")
0114 |             
0115 |             # Step 4: Validate required fields
0116 |             self._validate_required_fields(
0117 |                 response_data,
0118 |                 required_fields=['decisions'],
0119 |                 response_type='triage'
0120 |             )
0121 |             
0122 |             # Step 5: Create TriageResult (Pydantic will validate)
0123 |             triage_result = TriageResult(**response_data)
0124 |             
0125 |             # Step 6: Log results
0126 |             logger.info(f"TriageResult created successfully")
0127 |             logger.info(f"   Total analyzed: {triage_result.total_analyzed}")
0128 |             logger.info(f"   Confirmed: {triage_result.confirmed_count}")
0129 |             logger.info(f"   False positives: {triage_result.false_positive_count}")
0130 |             logger.info(f"   Needs review: {triage_result.needs_review_count}")
0131 |             
0132 |             return triage_result
0133 |             
0134 |         except Exception as e:
0135 |             logger.error(f"Triage parsing failed: {e}")
0136 |             logger.exception("Full traceback:")
0137 |             raise LLMError(f"Failed to parse triage response: {e}")
0138 |     
0139 |     
0140 |     def parse_remediation_response(self, 
0141 |                                    llm_response: str, 
0142 |                                    vuln_type: str = None, 
0143 |                                    language: str = None) -> RemediationPlan:
0144 |         """
0145 |         Parse LLM response to RemediationPlan
0146 |         
0147 |         Args:
0148 |             llm_response: Raw LLM response
0149 |             vuln_type: Vulnerability type (for logging)
0150 |             language: Language (for normalization)
0151 |             
0152 |         Returns:
0153 |             Validated RemediationPlan
0154 |             
0155 |         Raises:
0156 |             LLMError: If parsing fails
0157 |         """
0158 |         
0159 |         logger.info(f"Parsing remediation response ({len(llm_response):,} chars)...")
0160 |         
0161 |         try:
0162 |             # Step 1: Clean response
0163 |             cleaned = self.clean_json_response(llm_response)
0164 |             
0165 |             # Step 2: Validate structure
0166 |             validation = self.validate_json_structure(cleaned)
0167 |             
0168 |             if not validation['is_valid']:
0169 |                 logger.error(f"JSON structure validation failed:")
0170 |                 for error in validation['errors']:
0171 |                     logger.error(f"   - {error}")
0172 |                 
0173 |                 # Attempt recovery
0174 |                 extracted = self.extract_json(
0175 |                     cleaned,
0176 |                     required_fields=['vulnerability_type', 'priority_level', 'steps']
0177 |                 )
0178 |                 
0179 |                 if extracted:
0180 |                     cleaned = extracted
0181 |                     logger.info("Recovery successful")
0182 |                 else:
0183 |                     raise LLMError(f"JSON structure invalid: {validation['errors']}")
0184 |             
0185 |             # Step 3: Parse JSON
0186 |             try:
0187 |                 response_data = json.loads(cleaned)
0188 |                 logger.info(f"JSON parsed successfully")
0189 |             except json.JSONDecodeError as e:
0190 |                 logger.error(f"JSON parsing failed: {e}")
0191 |                 
0192 |                 # Last attempt
0193 |                 extracted = self.extract_json(
0194 |                     llm_response,
0195 |                     required_fields=['vulnerability_type', 'priority_level', 'steps']
0196 |                 )
0197 |                 
0198 |                 if extracted:
0199 |                     try:
0200 |                         response_data = json.loads(extracted)
0201 |                         logger.info("Recovery parse successful")
0202 |                     except Exception:
0203 |                         raise LLMError(f"Failed to parse remediation response: {e}")
0204 |                 else:
0205 |                     raise LLMError(f"Failed to parse remediation response: {e}")
0206 |             
0207 |             # Step 4: Validate required fields
0208 |             self._validate_required_fields(
0209 |                 response_data,
0210 |                 required_fields=['vulnerability_type', 'priority_level', 'steps'],
0211 |                 response_type='remediation'
0212 |             )
0213 |             
0214 |             # Step 5: Normalize data
0215 |             response_data = self._normalize_remediation_data(response_data, vuln_type)
0216 |             
0217 |             # Step 6: Create RemediationPlan
0218 |             remediation_plan = RemediationPlan(**response_data)
0219 |             
0220 |             # Step 7: Validate quality
0221 |             self._validate_remediation_quality(remediation_plan)
0222 |             
0223 |             # Step 8: Log results
0224 |             logger.info(f"RemediationPlan created successfully")
0225 |             logger.info(f"   Type: {remediation_plan.vulnerability_type.value}")
0226 |             logger.info(f"   Priority: {remediation_plan.priority_level}")
0227 |             logger.info(f"   Steps: {len(remediation_plan.steps)}")
0228 |             
0229 |             return remediation_plan
0230 |             
0231 |         except Exception as e:
0232 |             logger.error(f"Remediation parsing failed: {e}")
0233 |             logger.exception("Full traceback:")
0234 |             raise LLMError(f"Failed to parse remediation response: {e}")
0235 |     
0236 |     
0237 |     # ============================================================================
0238 |     # JSON CLEANING & EXTRACTION
0239 |     # ============================================================================
0240 |     
0241 |     def clean_json_response(self, response: str) -> str:
0242 |         """
0243 |         Clean response by removing markdown, prefixes and noise
0244 |         
0245 |         Handles:
0246 |         - Markdown wrappers: ```json ... ```
0247 |         - Anomalous prefixes: L3##, etc
0248 |         - Non-JSON lines at start/end
0249 |         - Invalid escape characters
0250 |         
0251 |         Args:
0252 |             response: Raw LLM response
0253 |             
0254 |         Returns:
0255 |             Clean and valid JSON
0256 |         """
0257 |         
0258 |         original_length = len(response)
0259 |         cleaned = response.strip()
0260 |         
0261 |         if self.debug_enabled:
0262 |             logger.debug(f"Starting JSON cleaning (original: {original_length} chars)")
0263 |         
0264 |         # Step 1: Remove complete markdown wrapper
0265 |         markdown_pattern = r'^```(?:json)?\s*\n(.*?)\n\s*```$'
0266 |         markdown_match = re.match(markdown_pattern, cleaned, re.DOTALL)
0267 |         
0268 |         if markdown_match:
0269 |             cleaned = markdown_match.group(1).strip()
0270 |             if self.debug_enabled:
0271 |                 logger.debug("Removed markdown wrapper (```json ...```)")
0272 |         
0273 |         # Step 2: Remove anomalous prefixes
0274 |         anomalous_prefixes = [
0275 |             'L3##```json\n', 'L3##json', 'L3##\n', 'L3##',
0276 |             '```json\n', '```json', '```\n', '```', 'json\n'
0277 |         ]
0278 |         
0279 |         for prefix in anomalous_prefixes:
0280 |             if cleaned.startswith(prefix):
0281 |                 cleaned = cleaned[len(prefix):].lstrip()
0282 |                 if self.debug_enabled:
0283 |                     logger.debug(f"Removed prefix: '{prefix[:15]}'")
0284 |                 break
0285 |         
0286 |         # Step 3: Remove suffixes
0287 |         anomalous_suffixes = ['\n```', '```', '`']
0288 |         
0289 |         for suffix in anomalous_suffixes:
0290 |             if cleaned.endswith(suffix):
0291 |                 cleaned = cleaned[:-len(suffix)].rstrip()
0292 |                 if self.debug_enabled:
0293 |                     logger.debug(f"Removed suffix: '{suffix}'")
0294 |                 break
0295 |         
0296 |         # Step 4: Clean non-JSON lines at start
0297 |         lines = cleaned.split('\n')
0298 |         json_start_index = 0
0299 |         
0300 |         for i, line in enumerate(lines):
0301 |             stripped = line.strip()
0302 |             if stripped.startswith(('{', '[')):
0303 |                 json_start_index = i
0304 |                 break
0305 |         
0306 |         if json_start_index > 0:
0307 |             cleaned = '\n'.join(lines[json_start_index:])
0308 |             if self.debug_enabled:
0309 |                 logger.debug(f"Skipped {json_start_index} non-JSON lines at start")
0310 |         
0311 |         # Step 5: Clean non-JSON lines at end
0312 |         lines = cleaned.split('\n')
0313 |         json_end_index = len(lines)
0314 |         
0315 |         for i in range(len(lines) - 1, -1, -1):
0316 |             stripped = lines[i].strip()
0317 |             if stripped.endswith(('}', ']')):
0318 |                 json_end_index = i + 1
0319 |                 break
0320 |         
0321 |         if json_end_index < len(lines):
0322 |             skipped = len(lines) - json_end_index
0323 |             cleaned = '\n'.join(lines[:json_end_index])
0324 |             if self.debug_enabled:
0325 |                 logger.debug(f"Skipped {skipped} non-JSON lines at end")
0326 |         
0327 |         # Step 6: Validate not empty
0328 |         cleaned = cleaned.strip()
0329 |         if not cleaned:
0330 |             raise ValueError("Response is empty after cleaning")
0331 |         
0332 |         # Step 7: Fix invalid escapes
0333 |         cleaned = self._fix_escape_sequences(cleaned)
0334 |         
0335 |         # Final log
0336 |         final_length = len(cleaned)
0337 |         bytes_removed = original_length - final_length
0338 |         if self.debug_enabled:
0339 |             logger.debug(f"Cleaning complete: {bytes_removed} bytes removed ({original_length} -> {final_length})")
0340 |         
0341 |         return cleaned
0342 |     
0343 |     
0344 |     def validate_json_structure(self, text: str) -> Dict[str, Any]:
0345 |         """
0346 |         Validate JSON structure before parsing
0347 |         
0348 |         Args:
0349 |             text: Text that should be JSON
0350 |             
0351 |         Returns:
0352 |             Dict with validation info:
0353 |             {
0354 |                 'is_valid': bool,
0355 |                 'errors': List[str],
0356 |                 'warnings': List[str]
0357 |             }
0358 |         """
0359 |         
0360 |         validation = {
0361 |             'is_valid': True,
0362 |             'errors': [],
0363 |             'warnings': []
0364 |         }
0365 |         
0366 |         # Check balanced delimiters
0367 |         open_braces = text.count('{')
0368 |         close_braces = text.count('}')
0369 |         open_brackets = text.count('[')
0370 |         close_brackets = text.count(']')
0371 |         
0372 |         if open_braces != close_braces:
0373 |             validation['is_valid'] = False
0374 |             validation['errors'].append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
0375 |         
0376 |         if open_brackets != close_brackets:
0377 |             validation['is_valid'] = False
0378 |             validation['errors'].append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
0379 |         
0380 |         # Check starts with { or [
0381 |         if not text.startswith(('{', '[')):
0382 |             validation['warnings'].append(f"JSON doesn't start with {{ or [")
0383 |         
0384 |         # Check ends with } or ]
0385 |         if not text.endswith(('}', ']')):
0386 |             validation['warnings'].append(f"JSON doesn't end with }} or ]")
0387 |         
0388 |         return validation
0389 |     
0390 |     def extract_json(self, text: str, required_fields: List[str] = None) -> Optional[str]:
0391 |         """
0392 |         Extract JSON from noisy text using multiple strategies
0393 |         
0394 |         Strategies (in priority order):
0395 |         1. Stack-based balancing with structure validation
0396 |         2. Regex pattern matching
0397 |         3. Simple first/last delimiter
0398 |         
0399 |         Args:
0400 |             text: Text with JSON mixed with noise
0401 |             required_fields: Required fields to consider JSON valid
0402 |             
0403 |         Returns:
0404 |             Extracted JSON or None if fails
0405 |         """
0406 |         
0407 |         logger.info("Attempting aggressive JSON extraction...")
0408 |         if required_fields:
0409 |             logger.debug(f"   Required fields: {required_fields}")
0410 |         
0411 |         # === METHOD 0: Try to balance brackets/braces FIRST ===
0412 |         try:
0413 |             logger.info("Trying auto-balance method...")
0414 |             balanced = self._balance_json_delimiters(text)
0415 |             if balanced and balanced != text:  # Only if changes were made
0416 |                 try:
0417 |                     parsed = json.loads(balanced)
0418 |                     has_required = self._has_required_fields(parsed, required_fields)
0419 |                     
0420 |                     if has_required:
0421 |                         logger.info(f"Auto-balance successful with all required fields ({len(balanced)} chars)")
0422 |                         return balanced
0423 |                     else:
0424 |                         logger.warning("Auto-balanced JSON missing required fields")
0425 |                         # Continue to other methods
0426 |                 except json.JSONDecodeError as e:
0427 |                     logger.debug(f"   Auto-balanced JSON invalid: {e}")
0428 |         except Exception as e:
0429 |             logger.debug(f"   Balance attempt failed: {e}")
0430 |         
0431 |         # === METHOD 1: Stack-based balancing (existing code) ===
0432 |         try:
0433 |             possible_jsons = []
0434 |             
0435 |             i = 0
0436 |             while i < len(text):
0437 |                 if text[i] == '{':
0438 |                     stack = ['{']
0439 |                     start_pos = i
0440 |                     j = i + 1
0441 |                     
0442 |                     while j < len(text) and stack:
0443 |                         if text[j] == '{':
0444 |                             stack.append('{')
0445 |                         elif text[j] == '}':
0446 |                             stack.pop()
0447 |                             if not stack:  # Complete JSON found
0448 |                                 end_pos = j + 1
0449 |                                 candidate = text[start_pos:end_pos]
0450 |                                 
0451 |                                 # Try to parse and validate
0452 |                                 try:
0453 |                                     parsed = json.loads(candidate)
0454 |                                     has_required = self._has_required_fields(parsed, required_fields)
0455 |                                     
0456 |                                     possible_jsons.append({
0457 |                                         'json': candidate,
0458 |                                         'parsed': parsed,
0459 |                                         'length': len(candidate),
0460 |                                         'start': start_pos,
0461 |                                         'has_required_fields': has_required,
0462 |                                         'available_fields': list(parsed.keys()) if isinstance(parsed, dict) else []
0463 |                                     })
0464 |                                 except json.JSONDecodeError:
0465 |                                     pass
0466 |                                 
0467 |                                 break
0468 |                         j += 1
0469 |                 i += 1
0470 |             
0471 |             if possible_jsons:
0472 |                 logger.info(f"   Found {len(possible_jsons)} valid JSON objects")
0473 |                 
0474 |                 # Prioritize by: required fields > size
0475 |                 possible_jsons.sort(key=lambda x: (
0476 |                     x['has_required_fields'],
0477 |                     x['length']
0478 |                 ), reverse=True)
0479 |                 
0480 |                 best_candidate = possible_jsons[0]
0481 |                 
0482 |                 if best_candidate['has_required_fields']:
0483 |                     logger.info(f"Stack extraction successful ({best_candidate['length']} chars)")
0484 |                     logger.debug(f"   Fields found: {best_candidate['available_fields']}")
0485 |                     return best_candidate['json']
0486 |                 else:
0487 |                     logger.warning(f"Best candidate missing required fields")
0488 |                     logger.warning(f"   Required: {required_fields}")
0489 |                     logger.warning(f"   Available: {best_candidate['available_fields']}")
0490 |                     logger.info(f"   Using largest JSON anyway ({best_candidate['length']} chars)")
0491 |                     return best_candidate['json']
0492 |             
0493 |             logger.debug("   Stack method found no valid JSON")
0494 |         
0495 |         except Exception as e:
0496 |             logger.debug(f"   Stack extraction failed: {e}")
0497 |         
0498 |         # === METHOD 2: Regex pattern matching ===
0499 |         logger.info("Trying regex extraction...")
0500 |         
0501 |         try:
0502 |             # Search for {...} pattern with content
0503 |             pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
0504 |             matches = re.findall(pattern, text, re.DOTALL)
0505 |             
0506 |             if matches:
0507 |                 logger.info(f"   Found {len(matches)} potential JSON objects via regex")
0508 |                 
0509 |                 valid_matches = []
0510 |                 for match in matches:
0511 |                     try:
0512 |                         parsed = json.loads(match)
0513 |                         has_required = self._has_required_fields(parsed, required_fields)
0514 |                         
0515 |                         valid_matches.append({
0516 |                             'json': match,
0517 |                             'parsed': parsed,
0518 |                             'length': len(match),
0519 |                             'has_required_fields': has_required,
0520 |                             'available_fields': list(parsed.keys()) if isinstance(parsed, dict) else []
0521 |                         })
0522 |                     except json.JSONDecodeError:
0523 |                         continue
0524 |                 
0525 |                 if valid_matches:
0526 |                     # Sort by required fields + size
0527 |                     valid_matches.sort(key=lambda x: (
0528 |                         x['has_required_fields'],
0529 |                         x['length']
0530 |                     ), reverse=True)
0531 |                     
0532 |                     best = valid_matches[0]
0533 |                     
0534 |                     if best['has_required_fields']:
0535 |                         logger.info(f"Regex extracted valid JSON ({best['length']} chars)")
0536 |                         return best['json']
0537 |                     else:
0538 |                         logger.warning(f"Using largest regex match without required fields")
0539 |                         return best['json']
0540 |         
0541 |         except Exception as e:
0542 |             logger.debug(f"   Regex extraction failed: {e}")
0543 |         
0544 |         # === METHOD 3: Simple first/last delimiter ===
0545 |         logger.info("Trying simple first/last delimiter...")
0546 |         
0547 |         try:
0548 |             first_brace = text.find('{')
0549 |             last_brace = text.rfind('}')
0550 |             
0551 |             if first_brace >= 0 and last_brace > first_brace:
0552 |                 extracted = text[first_brace:last_brace + 1]
0553 |                 try:
0554 |                     parsed = json.loads(extracted)
0555 |                     has_required = self._has_required_fields(parsed, required_fields)
0556 |                     
0557 |                     if has_required or not required_fields:
0558 |                         logger.info(f"Simple extraction successful ({len(extracted)} chars)")
0559 |                         return extracted
0560 |                     else:
0561 |                         logger.warning(f"Simple extraction missing required fields")
0562 |                         return extracted
0563 |                 
0564 |                 except json.JSONDecodeError as e:
0565 |                     logger.debug(f"   Simple extraction not valid JSON: {e}")
0566 |         
0567 |         except Exception as e:
0568 |             logger.debug(f"   Simple extraction failed: {e}")
0569 |         
0570 |         # All methods failed
0571 |         logger.error("All extraction methods failed")
0572 |         return None
0573 |     
0574 |     def _balance_json_delimiters(self, text: str) -> Optional[str]:
0575 |         """
0576 |         Attempt to balance unbalanced JSON by adding missing delimiters
0577 |         
0578 |         This handles cases where LLM responses are truncated or incomplete.
0579 |         
0580 |         Args:
0581 |             text: Potentially unbalanced JSON
0582 |             
0583 |         Returns:
0584 |             Balanced JSON or None
0585 |         """
0586 |         
0587 |         # Count all delimiters
0588 |         open_braces = text.count('{')
0589 |         close_braces = text.count('}')
0590 |         open_brackets = text.count('[')
0591 |         close_brackets = text.count(']')
0592 |         
0593 |         if self.debug_enabled:
0594 |             logger.debug(f"   Delimiters: {{:{open_braces}/{close_braces}, [:{open_brackets}/{close_brackets}")
0595 |         
0596 |         # If already balanced, return None (no changes needed)
0597 |         if open_braces == close_braces and open_brackets == close_brackets:
0598 |             return None
0599 |         
0600 |         balanced = text.strip()
0601 |         changes_made = False
0602 |         
0603 |         # Add missing closing brackets (for arrays)
0604 |         if open_brackets > close_brackets:
0605 |             missing = open_brackets - close_brackets
0606 |             logger.info(f"   ?? Adding {missing} closing bracket(s) ]")
0607 |             balanced += '\n' + ('  ' * (missing - 1)) + ']' * missing
0608 |             changes_made = True
0609 |         
0610 |         # Add missing closing braces (for objects)
0611 |         if open_braces > close_braces:
0612 |             missing = open_braces - close_braces
0613 |             logger.info(f"   ?? Adding {missing} closing brace(s) }}")
0614 |             # Add with proper indentation
0615 |             for i in range(missing):
0616 |                 indent = '  ' * (missing - i - 1)
0617 |                 balanced += '\n' + indent + '}'
0618 |             changes_made = True
0619 |         
0620 |         # Handle excess closing delimiters (less common but possible)
0621 |         if close_brackets > open_brackets:
0622 |             excess = close_brackets - open_brackets
0623 |             logger.warning(f"   ?? Removing {excess} excess closing bracket(s)")
0624 |             # Remove from end
0625 |             for _ in range(excess):
0626 |                 last_bracket = balanced.rfind(']')
0627 |                 if last_bracket >= 0:
0628 |                     balanced = balanced[:last_bracket] + balanced[last_bracket+1:]
0629 |             changes_made = True
0630 |         
0631 |         if close_braces > open_braces:
0632 |             excess = close_braces - open_braces
0633 |             logger.warning(f"   ?? Removing {excess} excess closing brace(s)")
0634 |             for _ in range(excess):
0635 |                 last_brace = balanced.rfind('}')
0636 |                 if last_brace >= 0:
0637 |                     balanced = balanced[:last_brace] + balanced[last_brace+1:]
0638 |             changes_made = True
0639 |         
0640 |         if changes_made:
0641 |             if self.debug_enabled:
0642 |                 logger.debug(f"   Balanced result ({len(balanced)} chars)")
0643 |             return balanced
0644 |         
0645 |         return None
0646 | 
0647 |     # ============================================================================
0648 |     # HELPER METHODS - PRIVATE
0649 |     # ============================================================================
0650 |     
0651 |     def _fix_escape_sequences(self, text: str) -> str:
0652 |         """
0653 |         Fix invalid escape sequences in JSON
0654 |         
0655 |         Valid JSON only accepts: \\", \\\\, \\/, \\b, \\f, \\n, \\r, \\t, \\uXXXX
0656 |         
0657 |         Args:
0658 |             text: Text with possible invalid escapes
0659 |             
0660 |         Returns:
0661 |             Text with corrected escapes
0662 |         """
0663 |         
0664 |         result = []
0665 |         i = 0
0666 |         
0667 |         while i < len(text):
0668 |             if text[i] == '\\' and i + 1 < len(text):
0669 |                 next_char = text[i + 1]
0670 |                 
0671 |                 # Valid simple escapes
0672 |                 if next_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']:
0673 |                     result.append(text[i:i+2])
0674 |                     i += 2
0675 |                     continue
0676 |                 
0677 |                 # Unicode escape: \uXXXX
0678 |                 elif next_char == 'u' and i + 5 < len(text):
0679 |                     hex_part = text[i+2:i+6]
0680 |                     if re.match(r'^[0-9a-fA-F]{4}$', hex_part):
0681 |                         result.append(text[i:i+6])
0682 |                         i += 6
0683 |                         continue
0684 |                 
0685 |                 # Invalid escape - escape the backslash
0686 |                 if self.debug_enabled:
0687 |                     logger.debug(f"Fixed invalid escape: \\{next_char}")
0688 |                 result.append('\\\\' + next_char)
0689 |                 i += 2
0690 |             else:
0691 |                 result.append(text[i])
0692 |                 i += 1
0693 |         
0694 |         return ''.join(result)
0695 |     
0696 |     
0697 |     def _has_required_fields(self, parsed: Any, required_fields: Optional[List[str]]) -> bool:
0698 |         """
0699 |         Check if a parsed object has required fields
0700 |         
0701 |         Args:
0702 |             parsed: Parsed object (dict, list, etc)
0703 |             required_fields: List of required fields
0704 |             
0705 |         Returns:
0706 |             True if has all required fields (or if no fields required)
0707 |         """
0708 |         
0709 |         if not required_fields:
0710 |             return True
0711 |         
0712 |         if not isinstance(parsed, dict):
0713 |             return False
0714 |         
0715 |         return all(field in parsed for field in required_fields)
0716 |     
0717 |     
0718 |     def _validate_required_fields(self, 
0719 |                                    response_data: Dict[str, Any],  # ? CORREGIDO
0720 |                                    required_fields: List[str],
0721 |                                    response_type: str) -> None:
0722 |         """
0723 |         Validate that a dict has required fields
0724 |         
0725 |         Args:
0726 |             response_data: Dict with parsed response
0727 |             required_fields: Fields that must be present
0728 |             response_type: Response type (for error messages)
0729 |             
0730 |         Raises:
0731 |             LLMError: If required fields are missing
0732 |         """
0733 |         
0734 |         if not isinstance(response_data, dict):
0735 |             raise LLMError(f"{response_type} response is not a dict: {type(response_data)}")
0736 |         
0737 |         missing = [f for f in required_fields if f not in response_data]
0738 |         
0739 |         if missing:
0740 |             available = list(response_data.keys())
0741 |             raise LLMError(
0742 |                 f"{response_type} response missing required fields: {missing}. "
0743 |                 f"Available: {available}"
0744 |             )
0745 |         
0746 |         logger.debug(f"All required fields present: {required_fields}")
0747 |     
0748 |     
0749 |     def _normalize_remediation_data(self, 
0750 |                                      response_data: Dict[str, Any],
0751 |                                      vuln_type: str = None) -> Dict[str, Any]:
0752 |         """
0753 |         Normalize remediation data to ensure compatibility with RemediationPlan
0754 |         
0755 |         Args:
0756 |             response_data: Parsed data from LLM
0757 |             vuln_type: Vulnerability type (fallback)
0758 |             
0759 |         Returns:
0760 |             Normalized data
0761 |         """
0762 |         
0763 |         # Ensure vulnerability_id exists
0764 |         if 'vulnerability_id' not in response_data:
0765 |             response_data['vulnerability_id'] = f"{vuln_type or 'unknown'}-remediation-{int(time.time())}"
0766 |             logger.warning(f"Added missing vulnerability_id: {response_data['vulnerability_id']}")
0767 |         
0768 |         # Ensure llm_model_used exists
0769 |         if 'llm_model_used' not in response_data:
0770 |             response_data['llm_model_used'] = 'meta-llama/llama-3-3-70b-instruct'
0771 |             logger.debug("   Added default llm_model_used")
0772 |         
0773 |         # Validate steps has content
0774 |         if not response_data.get('steps') or len(response_data['steps']) < 1:
0775 |             raise LLMError("Response has no remediation steps")
0776 |         
0777 |         return response_data
0778 |     
0779 |     
0780 |     def _validate_remediation_quality(self, plan: RemediationPlan) -> None:
0781 |         """
0782 |         Validate quality of remediation plan steps
0783 |         
0784 |         Args:
0785 |             plan: Remediation plan to validate
0786 |             
0787 |         Warnings:
0788 |             Generates warnings if steps have low quality
0789 |         """
0790 |         
0791 |         for i, step in enumerate(plan.steps, 1):
0792 |             desc_length = len(step.description)
0793 |             if desc_length < 50:
0794 |                 logger.warning(f"Step {i} has short description ({desc_length} chars)")
0795 |             
0796 |             if not step.title or len(step.title) < 10:
0797 |                 logger.warning(f"Step {i} has very short title")
0798 | 
0799 | 
0800 | # ============================================================================
0801 | # FACTORY FUNCTION
0802 | # ============================================================================
0803 | 
0804 | def create_response_parser(debug_enabled: bool = False) -> LLMResponseParser:
0805 |     """
0806 |     Factory function to create parser
0807 |     
0808 |     Args:
0809 |         debug_enabled: Enable detailed debug logging
0810 |         
0811 |     Returns:
0812 |         Configured LLMResponseParser
0813 |     """
0814 |     return LLMResponseParser(debug_enabled=debug_enabled)
```

---

### infrastructure\llm\__init__.py

**Ruta:** `infrastructure\llm\__init__.py`

```py
```

---

### shared\logger.py

**Ruta:** `shared\logger.py`

```py
0001 | # shared/logger.py
0002 | import logging
0003 | import logging.handlers
0004 | import sys
0005 | from pathlib import Path
0006 | from datetime import datetime
0007 | from typing import Optional
0008 | import json
0009 | 
0010 | class JSONFormatter(logging.Formatter):
0011 |     """Formatter JSON optimizado para logs estructurados"""
0012 |     
0013 |     def format(self, record):
0014 |         log_data = {
0015 |             "timestamp": datetime.fromtimestamp(record.created).isoformat(),
0016 |             "level": record.levelname,
0017 |             "logger": record.name,
0018 |             "message": record.getMessage(),
0019 |             "module": record.module,
0020 |             "function": record.funcName,
0021 |             "line": record.lineno
0022 |         }
0023 |         
0024 |         if hasattr(record, 'extra'):
0025 |             log_data["extra"] = record.extra
0026 |         
0027 |         if record.exc_info:
0028 |             log_data["exception"] = self.formatException(record.exc_info)
0029 |         
0030 |         return json.dumps(log_data, ensure_ascii=False)
0031 | 
0032 | class ColoredFormatter(logging.Formatter):
0033 |     """Formatter con colores para consola"""
0034 |     
0035 |     COLORS = {
0036 |         'DEBUG': '\033[36m',    # Cyan
0037 |         'INFO': '\033[32m',     # Green
0038 |         'WARNING': '\033[33m',  # Yellow
0039 |         'ERROR': '\033[31m',    # Red
0040 |         'CRITICAL': '\033[35m', # Magenta
0041 |         'RESET': '\033[0m'      # Reset
0042 |     }
0043 |     
0044 |     def format(self, record):
0045 |         color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
0046 |         reset = self.COLORS['RESET']
0047 |         
0048 |         return (
0049 |             f"{color}[{datetime.fromtimestamp(record.created).strftime('%H:%M:%S')}] "
0050 |             f"{record.levelname:<8}{reset} - "
0051 |             f"{record.module}.{record.funcName}:{record.lineno} - "
0052 |             f"{record.getMessage()}"
0053 |         )
0054 | 
0055 | def setup_logging(log_level: str = "INFO", 
0056 |                  log_file: Optional[str] = None,
0057 |                  structured: bool = False) -> None:
0058 |     """Configurar logging optimizado y simplificado"""
0059 |     
0060 |     level = getattr(logging, log_level.upper(), logging.INFO)
0061 |     
0062 |     # Clear existing handlers
0063 |     root_logger = logging.getLogger()
0064 |     root_logger.handlers.clear()
0065 |     root_logger.setLevel(level)
0066 |     
0067 |     # Console handler
0068 |     console_handler = logging.StreamHandler(sys.stdout)
0069 |     console_handler.setLevel(level)
0070 |     
0071 |     if structured:
0072 |         console_formatter = JSONFormatter()
0073 |     else:
0074 |         console_formatter = ColoredFormatter()
0075 |     
0076 |     console_handler.setFormatter(console_formatter)
0077 |     root_logger.addHandler(console_handler)
0078 |     
0079 |     # File handler (optional)
0080 |     if log_file:
0081 |         log_path = Path(log_file)
0082 |         log_path.parent.mkdir(parents=True, exist_ok=True)
0083 |         
0084 |         file_handler = logging.handlers.RotatingFileHandler(
0085 |             log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
0086 |         )
0087 |         file_handler.setLevel(logging.DEBUG)
0088 |         file_handler.setFormatter(JSONFormatter())
0089 |         root_logger.addHandler(file_handler)
0090 |     
0091 |     # Suppress noisy loggers
0092 |     for noisy_logger in ['urllib3', 'requests', 'openai']:
0093 |         logging.getLogger(noisy_logger).setLevel(logging.WARNING)
0094 |     
0095 |     logger = logging.getLogger(__name__)
0096 |     logger.info(f"Logging configured - Level: {log_level}")
```

---

### shared\metrics.py

**Ruta:** `shared\metrics.py`

```py
0001 | # shared/metrics.py
0002 | import time
0003 | import logging
0004 | from typing import Dict, Any, Optional, List
0005 | from dataclasses import dataclass, field
0006 | from datetime import datetime
0007 | from collections import defaultdict, Counter
0008 | import json
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | @dataclass
0013 | class PerformanceMetrics:
0014 |     """Métricas de rendimiento simplificadas"""
0015 |     operation: str
0016 |     start_time: float
0017 |     end_time: Optional[float] = None
0018 |     success: bool = True
0019 |     error: Optional[str] = None
0020 |     metadata: Dict[str, Any] = field(default_factory=dict)
0021 |     
0022 |     @property
0023 |     def duration_seconds(self) -> float:
0024 |         if self.end_time:
0025 |             return self.end_time - self.start_time
0026 |         return 0.0
0027 | 
0028 | class MetricsCollector:
0029 |     """Colector de métricas optimizado y simplificado"""
0030 |     
0031 |     def __init__(self):
0032 |         self.metrics: List[PerformanceMetrics] = []
0033 |         self.counters: Dict[str, int] = defaultdict(int)
0034 |         self.start_time = time.time()
0035 |     
0036 |     def record_complete_analysis(self, file_path: str, vulnerability_count: int = 0,
0037 |                                confirmed_count: int = 0, total_time: float = 0.0,
0038 |                                chunking_used: bool = False, language: Optional[str] = None,
0039 |                                success: bool = True, error: Optional[str] = None):
0040 |         """Record complete analysis metrics"""
0041 |         
0042 |         metric = PerformanceMetrics(
0043 |             operation="complete_analysis",
0044 |             start_time=time.time() - total_time,
0045 |             end_time=time.time(),
0046 |             success=success,
0047 |             error=error,
0048 |             metadata={
0049 |                 "file_path": file_path,
0050 |                 "vulnerability_count": vulnerability_count,
0051 |                 "confirmed_count": confirmed_count,
0052 |                 "chunking_used": chunking_used,
0053 |                 "language": language
0054 |             }
0055 |         )
0056 |         
0057 |         self.metrics.append(metric)
0058 |         self.counters["analyses_total"] += 1
0059 |         if success:
0060 |             self.counters["analyses_successful"] += 1
0061 |         
0062 |         logger.info(f"Analysis metrics recorded: {vulnerability_count} vulns, {total_time:.2f}s")
0063 |     
0064 |     def record_triage_analysis(self, vulnerability_count: int, analysis_time: float,
0065 |                              success: bool, chunk_id: Optional[int] = None,
0066 |                              error: Optional[str] = None):
0067 |         """Record triage analysis metrics"""
0068 |         
0069 |         metric = PerformanceMetrics(
0070 |             operation="triage_analysis",
0071 |             start_time=time.time() - analysis_time,
0072 |             end_time=time.time(),
0073 |             success=success,
0074 |             error=error,
0075 |             metadata={
0076 |                 "vulnerability_count": vulnerability_count,
0077 |                 "chunk_id": chunk_id,
0078 |                 "throughput": vulnerability_count / analysis_time if analysis_time > 0 else 0
0079 |             }
0080 |         )
0081 |         
0082 |         self.metrics.append(metric)
0083 |         self.counters["triage_calls"] += 1
0084 |     
0085 |     def record_remediation_generation(self, vulnerability_type: str, count: int,
0086 |                                     generation_time: float, success: bool,
0087 |                                     error: Optional[str] = None):
0088 |         """Record remediation generation metrics"""
0089 |         
0090 |         metric = PerformanceMetrics(
0091 |             operation="remediation_generation",
0092 |             start_time=time.time() - generation_time,
0093 |             end_time=time.time(),
0094 |             success=success,
0095 |             error=error,
0096 |             metadata={
0097 |                 "vulnerability_type": vulnerability_type,
0098 |                 "count": count
0099 |             }
0100 |         )
0101 |         
0102 |         self.metrics.append(metric)
0103 |         self.counters["remediation_calls"] += 1
0104 |     
0105 |     def record_report_generation(self, report_type: str, file_size: int = 0,
0106 |                                vulnerability_count: int = 0, success: bool = True,
0107 |                                error: Optional[str] = None):
0108 |         """Record report generation metrics"""
0109 |         
0110 |         metric = PerformanceMetrics(
0111 |             operation="report_generation",
0112 |             start_time=time.time(),
0113 |             end_time=time.time(),
0114 |             success=success,
0115 |             error=error,
0116 |             metadata={
0117 |                 "report_type": report_type,
0118 |                 "file_size": file_size,
0119 |                 "vulnerability_count": vulnerability_count
0120 |             }
0121 |         )
0122 |         
0123 |         self.metrics.append(metric)
0124 |         self.counters["reports_generated"] += 1
0125 |     
0126 |     def get_summary(self) -> Dict[str, Any]:
0127 |         """Get performance summary"""
0128 |         
0129 |         total_analyses = self.counters.get("analyses_total", 0)
0130 |         successful_analyses = self.counters.get("analyses_successful", 0)
0131 |         
0132 |         if total_analyses == 0:
0133 |             return {"message": "No metrics recorded"}
0134 |         
0135 |         # Calculate averages
0136 |         analysis_metrics = [m for m in self.metrics if m.operation == "complete_analysis"]
0137 |         avg_analysis_time = sum(m.duration_seconds for m in analysis_metrics) / len(analysis_metrics) if analysis_metrics else 0
0138 |         
0139 |         session_duration = time.time() - self.start_time
0140 |         
0141 |         return {
0142 |             "session_duration_seconds": session_duration,
0143 |             "total_analyses": total_analyses,
0144 |             "successful_analyses": successful_analyses,
0145 |             "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
0146 |             "average_analysis_time": avg_analysis_time,
0147 |             "triage_calls": self.counters.get("triage_calls", 0),
0148 |             "remediation_calls": self.counters.get("remediation_calls", 0),
0149 |             "reports_generated": self.counters.get("reports_generated", 0)
0150 |         }
0151 |     
0152 |     def export_metrics(self, output_file: Optional[str] = None) -> str:
0153 |         """Export all metrics to JSON"""
0154 |         
0155 |         export_data = {
0156 |             "export_timestamp": datetime.now().isoformat(),
0157 |             "session_start": datetime.fromtimestamp(self.start_time).isoformat(),
0158 |             "summary": self.get_summary(),
0159 |             "detailed_metrics": [
0160 |                 {
0161 |                     "operation": m.operation,
0162 |                     "duration_seconds": m.duration_seconds,
0163 |                     "success": m.success,
0164 |                     "error": m.error,
0165 |                     "metadata": m.metadata
0166 |                 } for m in self.metrics
0167 |             ],
0168 |             "counters": dict(self.counters)
0169 |         }
0170 |         
0171 |         json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
0172 |         
0173 |         if output_file:
0174 |             with open(output_file, 'w', encoding='utf-8') as f:
0175 |                 f.write(json_data)
0176 |             logger.info(f"Metrics exported to {output_file}")
0177 |         
0178 |         return json_data
```

---

### shared\__init__.py

**Ruta:** `shared\__init__.py`

```py
```

---

## Resumen del Análisis

- **Total de archivos en el proyecto:** 244
- **Archivos procesados:** 37
- **Archivos excluidos:** 207
- **Total de líneas de código:** 8,933
