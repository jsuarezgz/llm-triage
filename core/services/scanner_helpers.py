# core/services/scanner_helpers.py
"""
Scanner Helper Classes
======================

Separated from main scanner for clarity.
"""

import logging
from typing import List, Tuple
from functools import lru_cache

from core.models import Vulnerability

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Intelligent duplicate detection with multiple strategies"""
    
    def __init__(self, strategy: str = 'moderate'):
        """
        Args:
            strategy: 'strict', 'moderate', or 'loose'
        """
        self.strategy = strategy.lower()
        self._similarity_cache = {}
        
        if self.strategy not in ('strict', 'moderate', 'loose'):
            logger.warning(
                f"Invalid strategy '{strategy}', using 'moderate'"
            )
            self.strategy = 'moderate'
    
    def remove_duplicates(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> Tuple[List[Vulnerability], int]:
        """
        Remove duplicates from vulnerability list
        
        Returns:
            Tuple of (unique_vulnerabilities, count_removed)
        """
        if len(vulnerabilities) <= 1:
            return vulnerabilities, 0
        
        original_count = len(vulnerabilities)
        
        # Select strategy
        strategies = {
            'strict': self._dedup_strict,
            'moderate': self._dedup_moderate,
            'loose': self._dedup_loose
        }
        
        dedup_func = strategies[self.strategy]
        unique = dedup_func(vulnerabilities)
        
        removed = original_count - len(unique)
        if removed > 0:
            logger.info(
                f"✅ Removed {removed} duplicates ({self.strategy} strategy)"
            )
        
        return unique, removed
    
    def _dedup_strict(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Exact match: file+line+type+description hash"""
        seen = set()
        unique = []
        
        for v in vulns:
            # Crear signature única
            signature = (
                v.file_path,
                v.line_number,
                v.type.value,
                hash(v.description)
            )
            
            if signature not in seen:
                seen.add(signature)
                unique.append(v)
        
        return unique
    
    def _dedup_moderate(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Same file+type, nearby location (±5 lines), 80% similar description"""
        from collections import defaultdict
        
        # Agrupar por file + type
        groups = defaultdict(list)
        for v in vulns:
            key = (v.file_path, v.type.value)
            groups[key].append(v)
        
        unique = []
        
        for group_vulns in groups.values():
            # Ordenar por línea
            group_vulns.sort(key=lambda v: v.line_number)
            kept = []
            
            for v in group_vulns:
                # Verificar si es duplicado de alguno ya guardado
                is_duplicate = any(
                    abs(v.line_number - k.line_number) <= 5 and
                    self._similarity(v.description, k.description) > 0.8
                    for k in kept
                )
                
                if not is_duplicate:
                    kept.append(v)
                else:
                    # Log duplicado encontrado
                    logger.debug(
                        f"Duplicate found: {v.id} near line {v.line_number}"
                    )
            
            unique.extend(kept)
        
        return unique
    
    def _dedup_loose(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Same type, 70% similar description (ignora ubicación)"""
        from collections import defaultdict
        
        # Agrupar solo por tipo
        groups = defaultdict(list)
        for v in vulns:
            groups[v.type.value].append(v)
        
        unique = []
        
        for group_vulns in groups.values():
            kept = []
            
            for v in group_vulns:
                is_duplicate = any(
                    self._similarity(v.description, k.description) > 0.7
                    for k in kept
                )
                
                if not is_duplicate:
                    kept.append(v)
            
            unique.extend(kept)
        
        return unique
    
    @lru_cache(maxsize=1024)
    def _similarity(self, text1: str, text2: str) -> float:
        """
        Jaccard similarity with caching
        
        Returns:
            Similarity score 0.0-1.0
        """
        if text1 == text2:
            return 1.0
        
        # Tokenizar
        tokens1 = frozenset(text1.lower().split())
        tokens2 = frozenset(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard: intersection / union
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0

        