# adapters/processing/chunker.py
import logging
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from core.models import ScanResult, Vulnerability, ChunkingStrategy
from core.exceptions import ChunkingError

logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Metadatos optimizados de chunk"""
    id: int
    strategy: str
    total_chunks: int
    vulnerability_count: int
    estimated_size_bytes: int
    has_overlap: bool = False

@dataclass
class VulnerabilityChunk:
    """Chunk optimizado de vulnerabilidades"""
    id: int
    vulnerabilities: List[Vulnerability]
    metadata: ChunkMetadata
    
    @property
    def size_estimate(self) -> int:
        """Estimación rápida de tamaño"""
        return sum(len(v.title) + len(v.description) + len(v.code_snippet or "") 
                  for v in self.vulnerabilities)

class OptimizedChunker:
    """Chunker optimizado con estrategias inteligentes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_vulns_per_chunk = config.get("max_vulnerabilities_per_chunk", 5)
        self.max_size_bytes = config.get("max_size_bytes", 8000)
        self.overlap_vulns = config.get("overlap_vulnerabilities", 1)
        self.min_chunk_size = config.get("min_chunk_size", 3)
    
    def should_chunk(self, scan_result: ScanResult) -> bool:
        """Determinar si se necesita chunking con heurísticas optimizadas"""
        
        vuln_count = len(scan_result.vulnerabilities)
        
        # Chunking por cantidad
        if vuln_count > self.max_vulns_per_chunk:
            logger.info(f"Chunking needed: {vuln_count} vulnerabilities > {self.max_vulns_per_chunk}")
            return True
        
        # Chunking por tamaño estimado
        estimated_size = self._estimate_total_size(scan_result.vulnerabilities)
        if estimated_size > self.max_size_bytes:
            logger.info(f"Chunking needed: {estimated_size} bytes > {self.max_size_bytes}")
            return True
        
        return False
    
    def create_chunks(self, scan_result: ScanResult) -> List[VulnerabilityChunk]:
        """Crear chunks usando estrategia óptima"""
        
        vulnerabilities = scan_result.vulnerabilities
        
        if not vulnerabilities:
            return []
        
        if not self.should_chunk(scan_result):
            # Chunk único
            return [VulnerabilityChunk(
                id=1,
                vulnerabilities=vulnerabilities,
                metadata=ChunkMetadata(
                    id=1, strategy="no_chunking", total_chunks=1,
                    vulnerability_count=len(vulnerabilities),
                    estimated_size_bytes=self._estimate_total_size(vulnerabilities)
                )
            )]
        
        # Seleccionar estrategia óptima
        strategy = self._select_strategy(vulnerabilities)
        
        try:
            if strategy == "by_count":
                return self._chunk_by_count(vulnerabilities)
            else:  # by_size
                return self._chunk_by_size(vulnerabilities)
        
        except Exception as e:
            logger.error(f"Chunking failed: {e}")
            return self._emergency_chunking(vulnerabilities)
    
    def _select_strategy(self, vulnerabilities: List[Vulnerability]) -> str:
        """Seleccionar estrategia óptima basada en características"""
        
        avg_desc_length = sum(len(v.description) for v in vulnerabilities) / len(vulnerabilities)
        
        # Si las descripciones son muy largas, usar estrategia por tamaño
        if avg_desc_length > 300:
            return "by_size"
        
        return "by_count"
    
    def _chunk_by_count(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
        """Chunking optimizado por cantidad"""
        
        chunks = []
        chunk_size = self.max_vulns_per_chunk
        
        for i in range(0, len(vulnerabilities), chunk_size - self.overlap_vulns):
            chunk_vulns = vulnerabilities[i:i + chunk_size]
            
            # Evitar chunks muy pequeños al final
            if i > 0 and len(chunk_vulns) < self.min_chunk_size:
                if chunks:
                    chunks[-1].vulnerabilities.extend(chunk_vulns)
                    chunks[-1].metadata.vulnerability_count += len(chunk_vulns)
                break
            
            chunk = VulnerabilityChunk(
                id=len(chunks) + 1,
                vulnerabilities=chunk_vulns,
                metadata=ChunkMetadata(
                    id=len(chunks) + 1,
                    strategy="by_count",
                    total_chunks=math.ceil(len(vulnerabilities) / chunk_size),
                    vulnerability_count=len(chunk_vulns),
                    estimated_size_bytes=self._estimate_total_size(chunk_vulns),
                    has_overlap=i > 0 and self.overlap_vulns > 0
                )
            )
            chunks.append(chunk)
        
        # Actualizar total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        logger.info(f"Created {len(chunks)} chunks by count strategy")
        return chunks
    
    def _chunk_by_size(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
        """Chunking optimizado por tamaño"""
        
        chunks = []
        current_vulns = []
        current_size = 0
        
        for vuln in vulnerabilities:
            vuln_size = self._estimate_vuln_size(vuln)
            
            if current_size + vuln_size > self.max_size_bytes and current_vulns:
                # Crear chunk actual
                chunk = VulnerabilityChunk(
                    id=len(chunks) + 1,
                    vulnerabilities=current_vulns.copy(),
                    metadata=ChunkMetadata(
                        id=len(chunks) + 1,
                        strategy="by_size",
                        total_chunks=0,  # Se actualizará después
                        vulnerability_count=len(current_vulns),
                        estimated_size_bytes=current_size
                    )
                )
                chunks.append(chunk)
                
                # Nuevo chunk con overlap
                overlap_vulns = current_vulns[-self.overlap_vulns:] if self.overlap_vulns > 0 else []
                current_vulns = overlap_vulns + [vuln]
                current_size = sum(self._estimate_vuln_size(v) for v in current_vulns)
            else:
                current_vulns.append(vuln)
                current_size += vuln_size
        
        # Último chunk
        if current_vulns:
            chunk = VulnerabilityChunk(
                id=len(chunks) + 1,
                vulnerabilities=current_vulns,
                metadata=ChunkMetadata(
                    id=len(chunks) + 1,
                    strategy="by_size",
                    total_chunks=0,
                    vulnerability_count=len(current_vulns),
                    estimated_size_bytes=current_size
                )
            )
            chunks.append(chunk)
        
        # Actualizar total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        logger.info(f"Created {len(chunks)} chunks by size strategy")
        return chunks
    
    def _emergency_chunking(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
        """Chunking de emergencia ultra-conservador"""
        
        logger.warning("Using emergency chunking with very small chunks")
        
        emergency_size = 3  # Chunks muy pequeños
        chunks = []
        
        for i in range(0, len(vulnerabilities), emergency_size):
            chunk_vulns = vulnerabilities[i:i + emergency_size]
            
            chunk = VulnerabilityChunk(
                id=len(chunks) + 1,
                vulnerabilities=chunk_vulns,
                metadata=ChunkMetadata(
                    id=len(chunks) + 1,
                    strategy="emergency",
                    total_chunks=math.ceil(len(vulnerabilities) / emergency_size),
                    vulnerability_count=len(chunk_vulns),
                    estimated_size_bytes=self._estimate_total_size(chunk_vulns)
                )
            )
            chunks.append(chunk)
        
        return chunks
    
    def _estimate_total_size(self, vulnerabilities: List[Vulnerability]) -> int:
        """Estimación rápida de tamaño total"""
        return sum(self._estimate_vuln_size(v) for v in vulnerabilities)
    
    def _estimate_vuln_size(self, vulnerability: Vulnerability) -> int:
        """Estimación optimizada de tamaño de vulnerabilidad"""
        base_size = len(vulnerability.title) + len(vulnerability.description)
        code_size = len(vulnerability.code_snippet or "")
        
        # Factor de multiplicación para metadatos JSON (reducido)
        return int((base_size + code_size) * 1.3)

        
        