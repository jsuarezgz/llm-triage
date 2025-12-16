# adapters/processing/chunker.py
"""
Chunker - Simplified
===================

Responsibilities:
- Split large vulnerability lists
- Apply intelligent chunking strategies
- Handle overlap for context
"""

import logging
import math
from typing import List, Optional
from dataclasses import dataclass

from core.models import ScanResult, Vulnerability

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ════════════════════════════════════════════════════════════════════

@dataclass
class ChunkMetadata:
    """Metadata for a chunk"""
    id: int
    strategy: str
    total_chunks: int
    vulnerability_count: int
    estimated_size_bytes: int
    has_overlap: bool = False


@dataclass
class VulnerabilityChunk:
    """Single chunk of vulnerabilities"""
    id: int
    vulnerabilities: List[Vulnerability]
    metadata: ChunkMetadata
    
    @property
    def size_estimate(self) -> int:
        """Quick size estimation"""
        return sum(
            len(v.title) + len(v.description) + len(v.code_snippet or "")
            for v in self.vulnerabilities
        )


# ════════════════════════════════════════════════════════════════════
# CHUNKER
# ════════════════════════════════════════════════════════════════════

class OptimizedChunker:
    """Intelligent chunker with multiple strategies"""
    
    def __init__(self, config: dict):
        """
        Initialize chunker
        
        Args:
            config: Configuration dict with:
                - max_vulnerabilities_per_chunk
                - max_size_bytes
                - overlap_vulnerabilities
                - min_chunk_size
        """
        self.max_vulns = config.get("max_vulnerabilities_per_chunk", 5)
        self.max_bytes = config.get("max_size_bytes", 8000)
        self.overlap = config.get("overlap_vulnerabilities", 1)
        self.min_size = config.get("min_chunk_size", 3)
    
    def should_chunk(self, scan_result: ScanResult) -> bool:
        """
        Determine if chunking is needed
        
        Args:
            scan_result: Scan result with vulnerabilities
        
        Returns:
            True if chunking is recommended
        """
        vuln_count = len(scan_result.vulnerabilities)
        
        # Check count threshold
        if vuln_count > self.max_vulns:
            logger.info(f"📦 Chunking needed: {vuln_count} > {self.max_vulns} vulnerabilities")
            return True
        
        # Check size threshold
        estimated_size = self._estimate_total_size(scan_result.vulnerabilities)
        if estimated_size > self.max_bytes:
            logger.info(f"📦 Chunking needed: {estimated_size} > {self.max_bytes} bytes")
            return True
        
        return False
    
    def create_chunks(self, scan_result: ScanResult) -> List[VulnerabilityChunk]:
        """
        Create chunks from scan result
        
        Args:
            scan_result: Scan result to chunk
        
        Returns:
            List of vulnerability chunks
        """
        vulnerabilities = scan_result.vulnerabilities
        
        if not vulnerabilities:
            return []
        
        # No chunking needed
        if not self.should_chunk(scan_result):
            return [self._create_single_chunk(vulnerabilities)]
        
        # Select strategy
        strategy = self._select_strategy(vulnerabilities)
        
        try:
            if strategy == "by_count":
                return self._chunk_by_count(vulnerabilities)
            else:  # by_size
                return self._chunk_by_size(vulnerabilities)
        except Exception as e:
            logger.error(f"Chunking failed: {e}, using emergency chunking")
            return self._emergency_chunking(vulnerabilities)
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE METHODS
    # ════════════════════════════════════════════════════════════════
    
    def _create_single_chunk(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> VulnerabilityChunk:
        """Create single chunk (no splitting)"""
        return VulnerabilityChunk(
            id=1,
            vulnerabilities=vulnerabilities,
            metadata=ChunkMetadata(
                id=1,
                strategy="no_chunking",
                total_chunks=1,
                vulnerability_count=len(vulnerabilities),
                estimated_size_bytes=self._estimate_total_size(vulnerabilities)
            )
        )
    
    def _select_strategy(self, vulnerabilities: List[Vulnerability]) -> str:
        """Select optimal chunking strategy"""
        avg_desc_length = sum(
            len(v.description) for v in vulnerabilities
        ) / len(vulnerabilities)
        
        # Long descriptions → chunk by size
        if avg_desc_length > 300:
            return "by_size"
        
        return "by_count"
    
    def _chunk_by_count(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> List[VulnerabilityChunk]:
        """Chunk by vulnerability count with overlap"""
        chunks = []
        chunk_size = self.max_vulns
        step = chunk_size - self.overlap
        
        for i in range(0, len(vulnerabilities), step):
            chunk_vulns = vulnerabilities[i:i + chunk_size]
            
            # Merge small final chunk into previous
            if i > 0 and len(chunk_vulns) < self.min_size and chunks:
                chunks[-1].vulnerabilities.extend(chunk_vulns)
                chunks[-1].metadata.vulnerability_count += len(chunk_vulns)
                break
            
            chunk = VulnerabilityChunk(
                id=len(chunks) + 1,
                vulnerabilities=chunk_vulns,
                metadata=ChunkMetadata(
                    id=len(chunks) + 1,
                    strategy="by_count",
                    total_chunks=0,  # Updated later
                    vulnerability_count=len(chunk_vulns),
                    estimated_size_bytes=self._estimate_total_size(chunk_vulns),
                    has_overlap=(i > 0 and self.overlap > 0)
                )
            )
            chunks.append(chunk)
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        logger.info(f"✅ Created {len(chunks)} chunks (by_count)")
        return chunks
    
    def _chunk_by_size(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> List[VulnerabilityChunk]:
        """Chunk by size with overlap"""
        chunks = []
        current_vulns = []
        current_size = 0
        
        for vuln in vulnerabilities:
            vuln_size = self._estimate_vuln_size(vuln)
            
            # Create new chunk if size exceeded
            if current_size + vuln_size > self.max_bytes and current_vulns:
                chunk = VulnerabilityChunk(
                    id=len(chunks) + 1,
                    vulnerabilities=current_vulns.copy(),
                    metadata=ChunkMetadata(
                        id=len(chunks) + 1,
                        strategy="by_size",
                        total_chunks=0,
                        vulnerability_count=len(current_vulns),
                        estimated_size_bytes=current_size
                    )
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_vulns = current_vulns[-self.overlap:] if self.overlap > 0 else []
                current_vulns = overlap_vulns + [vuln]
                current_size = sum(
                    self._estimate_vuln_size(v) for v in current_vulns
                )
            else:
                current_vulns.append(vuln)
                current_size += vuln_size
        
        # Add final chunk
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
        
        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)
        
        logger.info(f"✅ Created {len(chunks)} chunks (by_size)")
        return chunks
    
    def _emergency_chunking(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> List[VulnerabilityChunk]:
        """Emergency chunking with very small chunks"""
        logger.warning("⚠️  Using emergency chunking (3 vulns per chunk)")
        
        emergency_size = 3
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
        """Estimate total size of vulnerability list"""
        return sum(self._estimate_vuln_size(v) for v in vulnerabilities)
    
    def _estimate_vuln_size(self, vulnerability: Vulnerability) -> int:
        """Estimate size of single vulnerability"""
        base_size = len(vulnerability.title) + len(vulnerability.description)
        code_size = len(vulnerability.code_snippet or "")
        
        # Factor for JSON metadata (1.3x)
        return int((base_size + code_size) * 1.3)
