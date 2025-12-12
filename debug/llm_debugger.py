# debug/llm_debugger.py - VERSIÓN ACTUALIZADA CON CONTROL DE DEBUG EN CLIENT
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import functools
import traceback

class LLMDebugger:
    """Debugger que controla automáticamente el debug en LLMClient"""
    
    def __init__(self, log_file: str = None, full_content: bool = True, max_content_length: int = 100000):
        # Crear directorio debug si no existe
        debug_dir = Path("debug")
        debug_dir.mkdir(exist_ok=True)
        
        # Archivo de log con timestamp
        if not log_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"debug/llm_calls_{timestamp}.log"
        
        self.log_file = log_file
        self.full_content = full_content
        self.max_content_length = max_content_length
        
        # Lista de clientes LLM activos para controlar debug
        self.llm_clients = []
        
        # Configurar logger específico para LLM
        self.logger = logging.getLogger("LLM_DEBUG")
        self.logger.setLevel(logging.DEBUG)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para archivo de debug con encoding UTF-8
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter detallado sin límites de longitud
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para consola (con contenido limitado)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('🔍 DEBUG: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Estadísticas
        self.call_count = 0
        self.total_time = 0
        self.errors = []
        
        self.logger.info("="*100)
        self.logger.info("🔍 LLM DEBUGGER INICIADO - ACTIVANDO DEBUG EN CLIENTES")
        self.logger.info(f"📄 Log file: {log_file}")
        self.logger.info(f"📝 Full content mode: {self.full_content}")
        self.logger.info(f"📏 Max content length: {self.max_content_length if not self.full_content else 'UNLIMITED'}")
        self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
        self.logger.info("="*100)
        
        print(f"🔍 LLM Debug logging to: {log_file} (Full Content: {self.full_content})")
        
        # Activar debug en todos los clientes LLM existentes
        self._activate_debug_in_existing_clients()
    
    def _activate_debug_in_existing_clients(self):
        """Activar debug en clientes LLM ya existentes"""
        try:
            # Buscar clientes LLM en el sistema usando introspección
            import gc
            
            for obj in gc.get_objects():
                if hasattr(obj, '__class__') and obj.__class__.__name__ == 'LLMClient':
                    self.register_llm_client(obj)
                    
        except Exception as e:
            self.logger.warning(f"Could not auto-activate debug in existing clients: {e}")
    
    def register_llm_client(self, llm_client):
        """Registrar y activar debug en un cliente LLM"""
        if llm_client not in self.llm_clients:
            self.llm_clients.append(llm_client)
            llm_client.enable_debug_mode()
            self.logger.info(f"✅ Debug enabled for LLM Client: {id(llm_client)}")
    
    def unregister_llm_client(self, llm_client):
        """Desregistrar cliente LLM"""
        if llm_client in self.llm_clients:
            self.llm_clients.remove(llm_client)
            llm_client.disable_debug_mode()
            self.logger.info(f"❌ Debug disabled for LLM Client: {id(llm_client)}")
    
    def log_api_call(self, 
                     call_type: str,
                     provider: str,
                     payload: Dict[str, Any],
                     response: Any = None,
                     error: Exception = None,
                     duration: float = None,
                     metadata: Dict[str, Any] = None):
        """Log detallado de llamada API con contenido completo"""
        
        self.call_count += 1
        call_id = f"CALL_{self.call_count:03d}"
        
        # === HEADER ===
        self.logger.info(f"\n{'='*100}")
        self.logger.info(f"🚀 {call_id} - {call_type.upper()} | Provider: {provider}")
        self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"{'='*100}")
        
        # === PAYLOAD DETAILS (CONTENIDO COMPLETO) ===
        self.logger.info("📤 PAYLOAD ENVIADO (REQUEST):")
        self._log_content_section(payload, "REQUEST", is_json=True)
        
        # === RESPONSE DETAILS (CONTENIDO COMPLETO) ===
        if response is not None:
            self.logger.info("\n📥 RESPUESTA RECIBIDA (RESPONSE):")
            self._log_content_section(response, "RESPONSE", is_json=None)
        
        # === ERROR DETAILS (COMPLETO) ===
        if error:
            self.logger.error(f"\n❌ ERROR OCURRIDO:")
            self.logger.error(f"   🔧 Type: {type(error).__name__}")
            self.logger.error(f"   💬 Message: {str(error)}")
            self.logger.error(f"   📍 Traceback completo:")
            
            # Traceback completo
            tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
            for line in tb_lines:
                self.logger.error(f"     {line.rstrip()}")
            
            self.errors.append({
                'call_id': call_id,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': ''.join(tb_lines),
                'timestamp': datetime.now().isoformat()
            })
        
        # === PERFORMANCE METRICS ===
        if duration:
            self.total_time += duration
            self.logger.info(f"\n⏱️  MÉTRICAS DE RENDIMIENTO:")
            self.logger.info(f"   🕐 Duración de llamada: {duration:.3f}s")
            self.logger.info(f"   📊 Tiempo total acumulado: {self.total_time:.3f}s")
            self.logger.info(f"   📈 Promedio por llamada: {self.total_time/self.call_count:.3f}s")
            
            # Throughput si hay datos de vulnerabilidades
            if metadata and 'vulnerabilities_count' in metadata:
                vuln_count = metadata['vulnerabilities_count']
                throughput = vuln_count / duration if duration > 0 else 0
                self.logger.info(f"   🚀 Throughput: {throughput:.2f} vulnerabilidades/segundo")
        
        # === METADATA ===
        if metadata:
            self.logger.info(f"\n📊 METADATOS:")
            for key, value in metadata.items():
                self.logger.info(f"   📋 {key}: {value}")
        
        # === FOOTER ===
        self.logger.info(f"{'='*100}")
        self.logger.info(f"✅ {call_id} COMPLETADO")
        self.logger.info(f"{'='*100}\n")
    
    def _log_content_section(self, content: Any, section_name: str, is_json: bool = None):
        """Log una sección de contenido completo con análisis automático"""
        
        # Determinar el tipo de contenido y convertir a string
        if isinstance(content, dict):
            content_str = json.dumps(content, indent=2, ensure_ascii=False)
            is_json = True
        elif isinstance(content, str):
            content_str = content
            # Intentar detectar si es JSON
            if is_json is None:
                try:
                    json.loads(content)
                    is_json = True
                except:
                    is_json = False
        else:
            content_str = str(content)
            is_json = False
        
        # Calcular métricas
        content_size = len(content_str.encode('utf-8'))
        line_count = content_str.count('\n') + 1
        
        self.logger.info(f"   📏 Size: {content_size:,} bytes")
        self.logger.info(f"   📄 Lines: {line_count:,}")
        self.logger.info(f"   🔧 Type: {type(content).__name__}")
        self.logger.info(f"   📋 Format: {'JSON' if is_json else 'Text'}")
        
        # Si es un dict, mostrar estructura
        if isinstance(content, dict):
            self.logger.info(f"   🔑 Keys: {list(content.keys())}")
        
        # Log del contenido completo
        if self.full_content or content_size <= self.max_content_length:
            self.logger.info(f"   📋 CONTENIDO COMPLETO DE {section_name}:")
            self.logger.info("   " + "─" * 80)
            
            # Formatear con numeración de líneas
            formatted_content = self._format_with_line_numbers(content_str)
            self.logger.info(formatted_content)
            
            self.logger.info("   " + "─" * 80)
        else:
            # Modo truncado
            self.logger.info(f"   📋 CONTENIDO DE {section_name} (TRUNCADO):")
            self.logger.info("   " + "─" * 80)
            
            # Mostrar inicio y final
            preview_length = min(2000, self.max_content_length // 2)
            
            self.logger.info("   📝 INICIO:")
            start_content = content_str[:preview_length]
            self.logger.info(self._format_with_line_numbers(start_content))
            
            if len(content_str) > preview_length * 2:
                self.logger.info(f"\n   ⚠️  ... CONTENIDO MEDIO OMITIDO ({len(content_str) - preview_length * 2:,} chars) ...\n")
            
            self.logger.info("   📝 FINAL:")
            end_content = content_str[-preview_length:]
            # Calcular número de línea inicial para el final
            start_line = content_str[:len(content_str) - preview_length].count('\n') + 1
            self.logger.info(self._format_with_line_numbers(end_content, start_line))
            
            self.logger.info("   " + "─" * 80)
            self.logger.info(f"   ⚠️  NOTA: Contenido truncado - longitud original: {content_size:,} bytes")
    
    def _format_with_line_numbers(self, text: str, start_line: int = 1) -> str:
        """Formatear texto con numeración de líneas"""
        lines = text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line_num = start_line + i
            formatted_lines.append(f"   [{line_num:5d}] {line}")
        
        return '\n'.join(formatted_lines)
    
    def log_triage_analysis(self, vulnerabilities_data: str, system_prompt: str, response: Any, duration: float = None):
        """Log específico para análisis de triage con contenido completo"""
        
        vuln_count = vulnerabilities_data.count("## VULNERABILITY")
        
        metadata = {
            'analysis_type': 'vulnerability_triage',
            'vulnerabilities_count': vuln_count,
            'system_prompt_length': len(system_prompt),
            'vulnerabilities_data_length': len(vulnerabilities_data),
            'total_input_size': len(system_prompt) + len(vulnerabilities_data)
        }
        
        # Payload completo para triage - CONTENIDO REAL
        full_message = f"{system_prompt}\n\nDATA TO ANALYZE:\n{vulnerabilities_data}"
        payload = {
            'message': {
                'role': 'user',
                'content': full_message
            },
            'temperature': 0.1,
            'model': 'meta-llama/llama-3-3-70b-instruct',
            'analysis_metadata': metadata
        }
        
        self.log_api_call(
            call_type="triage_analysis",
            provider="research_api",
            payload=payload,
            response=response,
            duration=duration,
            metadata=metadata
        )
    
    def log_remediation_generation(self, vulnerability_data: str, system_prompt: str, response: Any, duration: float = None):
        """Log específico para generación de remediación con contenido completo"""
        
        metadata = {
            'analysis_type': 'remediation_generation',
            'system_prompt_length': len(system_prompt),
            'vulnerability_data_length': len(vulnerability_data),
            'total_input_size': len(system_prompt) + len(vulnerability_data)
        }
        
        # Payload completo para remediación - CONTENIDO REAL
        full_message = f"{system_prompt}\n\nVULNERABILITY DATA:\n{vulnerability_data}"
        payload = {
            'message': {
                'role': 'user',
                'content': full_message
            },
            'temperature': 0.2,
            'model': 'meta-llama/llama-3-3-70b-instruct',
            'remediation_metadata': metadata
        }
        
        self.log_api_call(
            call_type="remediation_generation",
            provider="research_api",
            payload=payload,
            response=response,
            duration=duration,
            metadata=metadata
        )
    
    def log_raw_http_call(self, url: str, method: str, headers: Dict, request_body: Any, 
                         response_status: int, response_headers: Dict, response_body: Any, 
                         duration: float = None):
        """Log de llamada HTTP cruda con todos los detalles"""
        
        self.call_count += 1
        call_id = f"HTTP_{self.call_count:03d}"
        
        self.logger.info(f"\n{'='*100}")
        self.logger.info(f"🌐 {call_id} - HTTP {method.upper()} | URL: {url}")
        self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"{'='*100}")
        
        # REQUEST DETAILS
        self.logger.info("📤 HTTP REQUEST:")
        self.logger.info(f"   🔗 URL: {url}")
        self.logger.info(f"   🔧 Method: {method}")
        self.logger.info(f"   📋 Headers:")
        for header, value in headers.items():
            # Ocultar parcialmente API keys por seguridad
            if 'api' in header.lower() or 'key' in header.lower() or 'auth' in header.lower():
                masked_value = value[:8] + "***" + value[-4:] if len(value) > 12 else "***"
                self.logger.info(f"      {header}: {masked_value}")
            else:
                self.logger.info(f"      {header}: {value}")
        
        # REQUEST BODY
        if request_body:
            self.logger.info(f"\n   📤 REQUEST BODY:")
            self._log_content_section(request_body, "REQUEST_BODY")
        
        # RESPONSE DETAILS
        self.logger.info(f"\n📥 HTTP RESPONSE:")
        self.logger.info(f"   📊 Status: {response_status}")
        self.logger.info(f"   📋 Headers:")
        for header, value in response_headers.items():
            self.logger.info(f"      {header}: {value}")
        
        # RESPONSE BODY
        if response_body:
            self.logger.info(f"\n   📥 RESPONSE BODY:")
            self._log_content_section(response_body, "RESPONSE_BODY")
        
        # PERFORMANCE
        if duration:
            self.total_time += duration
            self.logger.info(f"\n⏱️  HTTP PERFORMANCE:")
            self.logger.info(f"   🕐 Duration: {duration:.3f}s")
            self.logger.info(f"   📊 Status: {'✅ Success' if 200 <= response_status < 300 else '❌ Error'}")
        
        self.logger.info(f"{'='*100}\n")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas resumidas"""
        return {
            'total_calls': self.call_count,
            'total_time_seconds': self.total_time,
            'average_time_per_call': self.total_time / self.call_count if self.call_count > 0 else 0,
            'error_count': len(self.errors),
            'success_rate': (self.call_count - len(self.errors)) / self.call_count if self.call_count > 0 else 0,
            'errors': self.errors,
            'log_file': self.log_file,
            'full_content_mode': self.full_content,
            'active_llm_clients': len(self.llm_clients)
        }
    
    def finalize_log(self):
        """Finalizar el log con estadísticas completas y desactivar debug en clientes"""
        
        # Desactivar debug en todos los clientes registrados
        for client in self.llm_clients[:]:  # Copia la lista para evitar modificaciones concurrentes
            self.unregister_llm_client(client)
        
        stats = self.get_summary_stats()
        
        self.logger.info("\n" + "="*100)
        self.logger.info("📊 RESUMEN FINAL - LLM DEBUG SESSION")
        self.logger.info("="*100)
        self.logger.info(f"🔢 Total de llamadas: {stats['total_calls']}")
        self.logger.info(f"⏱️  Tiempo total: {stats['total_time_seconds']:.2f}s")
        self.logger.info(f"📊 Tiempo promedio: {stats['average_time_per_call']:.2f}s por llamada")
        self.logger.info(f"❌ Errores: {stats['error_count']}")
        self.logger.info(f"✅ Tasa de éxito: {stats['success_rate']:.1%}")
        self.logger.info(f"📄 Archivo de log: {stats['log_file']}")
        self.logger.info(f"📝 Modo contenido completo: {stats['full_content_mode']}")
        self.logger.info(f"🔧 Clientes LLM controlados: {stats['active_llm_clients']}")
        
        if self.errors:
            self.logger.info("\n🚨 ERRORES DETECTADOS:")
            for error in self.errors:
                self.logger.info(f"   {error['call_id']}: {error['error_type']} - {error['error_message']}")
        
        # Estadísticas de contenido
        log_size = Path(self.log_file).stat().st_size if Path(self.log_file).exists() else 0
        self.logger.info(f"\n📏 ESTADÍSTICAS DEL LOG:")
        self.logger.info(f"   📄 Tamaño del archivo: {log_size:,} bytes ({log_size/1024/1024:.2f} MB)")
        self.logger.info(f"   📝 Modo: {'Contenido completo' if self.full_content else 'Contenido limitado'}")
        
        self.logger.info("="*100)
        print(f"📄 Debug completo guardado en: {self.log_file} ({log_size/1024/1024:.2f} MB)")


# Instancia global del debugger
_debugger = None

def get_debugger(full_content: bool = True) -> LLMDebugger:
    """Obtener instancia singleton del debugger"""
    global _debugger
    if _debugger is None:
        _debugger = LLMDebugger(full_content=full_content)
    return _debugger

def debug_llm_call(func):
    """Decorador para debuggear automáticamente llamadas LLM"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        debugger = get_debugger()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            debugger.log_api_call(
                call_type=func.__name__,
                provider="auto_detected",
                payload={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]},
                response=str(result)[:1000] if len(str(result)) <= 1000 else result,
                duration=duration
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            debugger.log_api_call(
                call_type=func.__name__,
                provider="auto_detected", 
                payload={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]},
                error=e,
                duration=duration
            )
            
            raise
    
    return wrapper

# === FUNCIONES DE UTILIDAD ===

def start_debug_session(full_content: bool = True):
    """Iniciar nueva sesión de debug y activar debug automáticamente en clientes LLM"""
    global _debugger
    _debugger = LLMDebugger(full_content=full_content)
    print(f"🔍 Debug session started: {_debugger.log_file}")
    print(f"📡 Auto-activating debug in LLM clients...")

def end_debug_session():
    """Finalizar sesión de debug y desactivar debug en clientes"""
    global _debugger
    if _debugger:
        _debugger.finalize_log()
        _debugger = None

def log_research_api_call(url: str, payload: Dict[str, Any], response: Any, 
                         duration: float = None, error: Exception = None):
    """Log específico para Research API con contenido completo"""
    debugger = get_debugger()
    debugger.log_api_call(
        call_type="research_api_call",
        provider="research_api",
        payload=payload,
        response=response,
        duration=duration,
        error=error,
        metadata={
            'url': url,
            'payload_size': len(json.dumps(payload, ensure_ascii=False)) if isinstance(payload, dict) else len(str(payload)),
            'response_size': len(str(response)) if response else 0
        }
    )

def log_http_details(url: str, method: str, headers: Dict, request_body: Any,
                    response_status: int, response_headers: Dict, response_body: Any,
                    duration: float = None):
    """Log detallado de llamada HTTP"""
    debugger = get_debugger()
    debugger.log_raw_http_call(
        url=url,
        method=method,
        headers=headers,
        request_body=request_body,
        response_status=response_status,
        response_headers=response_headers,
        response_body=response_body,
        duration=duration
    )

def register_llm_client_for_debug(llm_client):
    """Registrar manualmente un cliente LLM para debug"""
    try:
        debugger = get_debugger()
        debugger.register_llm_client(llm_client)
    except:
        pass  # Si no hay sesión de debug activa, no hacer nada
