# shared/metrics.py
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento simplificadas"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return 0.0

class MetricsCollector:
    """Colector de métricas optimizado y simplificado"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.counters: Dict[str, int] = defaultdict(int)
        self.start_time = time.time()
    
    def record_complete_analysis(self, file_path: str, vulnerability_count: int = 0,
                               confirmed_count: int = 0, total_time: float = 0.0,
                               chunking_used: bool = False, language: Optional[str] = None,
                               success: bool = True, error: Optional[str] = None):
        """Record complete analysis metrics"""
        
        metric = PerformanceMetrics(
            operation="complete_analysis",
            start_time=time.time() - total_time,
            end_time=time.time(),
            success=success,
            error=error,
            metadata={
                "file_path": file_path,
                "vulnerability_count": vulnerability_count,
                "confirmed_count": confirmed_count,
                "chunking_used": chunking_used,
                "language": language
            }
        )
        
        self.metrics.append(metric)
        self.counters["analyses_total"] += 1
        if success:
            self.counters["analyses_successful"] += 1
        
        logger.info(f"Analysis metrics recorded: {vulnerability_count} vulns, {total_time:.2f}s")
    
    def record_triage_analysis(self, vulnerability_count: int, analysis_time: float,
                             success: bool, chunk_id: Optional[int] = None,
                             error: Optional[str] = None):
        """Record triage analysis metrics"""
        
        metric = PerformanceMetrics(
            operation="triage_analysis",
            start_time=time.time() - analysis_time,
            end_time=time.time(),
            success=success,
            error=error,
            metadata={
                "vulnerability_count": vulnerability_count,
                "chunk_id": chunk_id,
                "throughput": vulnerability_count / analysis_time if analysis_time > 0 else 0
            }
        )
        
        self.metrics.append(metric)
        self.counters["triage_calls"] += 1
    
    def record_remediation_generation(self, vulnerability_type: str, count: int,
                                    generation_time: float, success: bool,
                                    error: Optional[str] = None):
        """Record remediation generation metrics"""
        
        metric = PerformanceMetrics(
            operation="remediation_generation",
            start_time=time.time() - generation_time,
            end_time=time.time(),
            success=success,
            error=error,
            metadata={
                "vulnerability_type": vulnerability_type,
                "count": count
            }
        )
        
        self.metrics.append(metric)
        self.counters["remediation_calls"] += 1
    
    def record_report_generation(self, report_type: str, file_size: int = 0,
                               vulnerability_count: int = 0, success: bool = True,
                               error: Optional[str] = None):
        """Record report generation metrics"""
        
        metric = PerformanceMetrics(
            operation="report_generation",
            start_time=time.time(),
            end_time=time.time(),
            success=success,
            error=error,
            metadata={
                "report_type": report_type,
                "file_size": file_size,
                "vulnerability_count": vulnerability_count
            }
        )
        
        self.metrics.append(metric)
        self.counters["reports_generated"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        total_analyses = self.counters.get("analyses_total", 0)
        successful_analyses = self.counters.get("analyses_successful", 0)
        
        if total_analyses == 0:
            return {"message": "No metrics recorded"}
        
        # Calculate averages
        analysis_metrics = [m for m in self.metrics if m.operation == "complete_analysis"]
        avg_analysis_time = sum(m.duration_seconds for m in analysis_metrics) / len(analysis_metrics) if analysis_metrics else 0
        
        session_duration = time.time() - self.start_time
        
        return {
            "session_duration_seconds": session_duration,
            "total_analyses": total_analyses,
            "successful_analyses": successful_analyses,
            "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
            "average_analysis_time": avg_analysis_time,
            "triage_calls": self.counters.get("triage_calls", 0),
            "remediation_calls": self.counters.get("remediation_calls", 0),
            "reports_generated": self.counters.get("reports_generated", 0)
        }
    
    def export_metrics(self, output_file: Optional[str] = None) -> str:
        """Export all metrics to JSON"""
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "session_start": datetime.fromtimestamp(self.start_time).isoformat(),
            "summary": self.get_summary(),
            "detailed_metrics": [
                {
                    "operation": m.operation,
                    "duration_seconds": m.duration_seconds,
                    "success": m.success,
                    "error": m.error,
                    "metadata": m.metadata
                } for m in self.metrics
            ],
            "counters": dict(self.counters)
        }
        
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
            logger.info(f"Metrics exported to {output_file}")
        
        return json_data
