"""
Batch processing system for LMAPP v0.2.4.

Allows running queries on multiple inputs with efficient processing.
Supports batch files, directories, and URL lists.

Features:
- Process multiple queries on multiple inputs
- Results aggregation and export
- Progress tracking
- Error handling and recovery
- Output formatting (JSON, CSV, text)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class BatchStatus(Enum):
    """Status of a batch job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputFormat(Enum):
    """Output format for batch results."""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    JSONL = "jsonl"  # JSON Lines format


@dataclass
class BatchInput:
    """Represents a single input item in a batch."""
    
    input_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_id": self.input_id,
            "content": self.content,
            "metadata": self.metadata or {},
        }


@dataclass
class BatchResult:
    """Result from processing a single batch input."""
    
    input_id: str
    output: Any
    status: str = "success"
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_id": self.input_id,
            "output": self.output,
            "status": self.status,
            "error": self.error,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    
    job_id: str
    inputs: List[BatchInput]
    status: BatchStatus = BatchStatus.PENDING
    results: List[BatchResult] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_processed: int = 0
    total_failed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "inputs_count": len(self.inputs),
            "results_count": len(self.results),
            "total_processed": self.total_processed,
            "total_failed": self.total_failed,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "results": [r.to_dict() for r in self.results],
        }


class BatchProcessor:
    """Processes batch jobs with multiple inputs."""
    
    def __init__(self, jobs_dir: Optional[Path] = None):
        """
        Initialize BatchProcessor.
        
        Args:
            jobs_dir: Directory to store batch jobs (default: ~/.lmapp/batch/)
        """
        if jobs_dir is None:
            home = Path.home()
            jobs_dir = home / ".lmapp" / "batch"
        
        self.jobs_dir = Path(jobs_dir)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, BatchJob] = {}
    
    def create_batch_job(
        self,
        job_id: str,
        inputs: List[BatchInput],
    ) -> BatchJob:
        """
        Create a new batch job.
        
        Args:
            job_id: Unique job identifier
            inputs: List of inputs to process
        
        Returns:
            BatchJob instance
        """
        job = BatchJob(job_id=job_id, inputs=inputs)
        self.jobs[job_id] = job
        return job
    
    def process_batch(
        self,
        job_id: str,
        processor_fn: Callable[[str], Tuple[Any, Optional[str]]],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchJob:
        """
        Process a batch job.
        
        Args:
            job_id: Job ID to process
            processor_fn: Function to process each input. 
                         Takes content, returns (output, error_message)
            on_progress: Optional callback for progress updates (processed, total)
        
        Returns:
            Completed BatchJob
        """
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        job.status = BatchStatus.PROCESSING
        job.started_at = datetime.utcnow().isoformat() + "Z"
        
        import time
        
        for idx, input_item in enumerate(job.inputs):
            start_time = time.time()
            
            try:
                output, error = processor_fn(input_item.content)
                
                if error:
                    result = BatchResult(
                        input_id=input_item.input_id,
                        output=None,
                        status="error",
                        error=error,
                        processing_time=time.time() - start_time,
                    )
                    job.total_failed += 1
                else:
                    result = BatchResult(
                        input_id=input_item.input_id,
                        output=output,
                        status="success",
                        processing_time=time.time() - start_time,
                    )
                    job.total_processed += 1
            
            except Exception as e:
                result = BatchResult(
                    input_id=input_item.input_id,
                    output=None,
                    status="error",
                    error=str(e),
                    processing_time=time.time() - start_time,
                )
                job.total_failed += 1
            
            job.results.append(result)
            
            # Call progress callback
            if on_progress:
                on_progress(idx + 1, len(job.inputs))
        
        job.status = BatchStatus.COMPLETED
        job.completed_at = datetime.utcnow().isoformat() + "Z"
        self._save_job(job)
        
        return job
    
    def load_inputs_from_file(self, file_path: Path) -> List[BatchInput]:
        """
        Load batch inputs from a file.
        
        Supports:
        - JSON: List of {id, content} objects
        - JSONL: One JSON object per line
        - Text: One line per input
        
        Args:
            file_path: Path to input file
        
        Returns:
            List of BatchInput
        """
        if not file_path.exists():
            return []
        
        inputs = []
        
        try:
            if file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            if isinstance(item, dict):
                                inputs.append(BatchInput(
                                    input_id=item.get("id", f"input_{idx}"),
                                    content=item.get("content", ""),
                                    metadata=item.get("metadata"),
                                ))
                            else:
                                inputs.append(BatchInput(
                                    input_id=f"input_{idx}",
                                    content=str(item),
                                ))
            
            elif file_path.suffix == ".jsonl":
                with open(file_path, "r") as f:
                    for idx, line in enumerate(f):
                        if line.strip():
                            item = json.loads(line)
                            inputs.append(BatchInput(
                                input_id=item.get("id", f"input_{idx}"),
                                content=item.get("content", ""),
                                metadata=item.get("metadata"),
                            ))
            
            else:  # Text file
                with open(file_path, "r") as f:
                    for idx, line in enumerate(f):
                        content = line.strip()
                        if content:
                            inputs.append(BatchInput(
                                input_id=f"input_{idx}",
                                content=content,
                            ))
        
        except (json.JSONDecodeError, IOError):
            pass
        
        return inputs
    
    def save_results(
        self,
        job_id: str,
        output_path: Path,
        format: OutputFormat = OutputFormat.JSON,
    ) -> bool:
        """
        Save batch results to file.
        
        Args:
            job_id: Job ID
            output_path: Path to save results
            format: Output format
        
        Returns:
            True if successful
        """
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        try:
            if format == OutputFormat.JSON:
                with open(output_path, "w") as f:
                    json.dump(job.to_dict(), f, indent=2)
            
            elif format == OutputFormat.JSONL:
                with open(output_path, "w") as f:
                    for result in job.results:
                        f.write(json.dumps(result.to_dict()) + "\n")
            
            elif format == OutputFormat.CSV:
                import csv
                with open(output_path, "w", newline="") as f:
                    if job.results:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=["input_id", "status", "output", "error", "processing_time"]
                        )
                        writer.writeheader()
                        for result in job.results:
                            writer.writerow({
                                "input_id": result.input_id,
                                "status": result.status,
                                "output": str(result.output)[:200] if result.output else "",
                                "error": result.error or "",
                                "processing_time": f"{result.processing_time:.3f}s",
                            })
            
            elif format == OutputFormat.TEXT:
                with open(output_path, "w") as f:
                    f.write(f"Batch Job: {job.job_id}\n")
                    f.write(f"Status: {job.status.value}\n")
                    f.write(f"Processed: {job.total_processed}/{len(job.inputs)}\n")
                    f.write(f"Failed: {job.total_failed}\n\n")
                    
                    for result in job.results:
                        f.write(f"--- Input: {result.input_id} ---\n")
                        f.write(f"Status: {result.status}\n")
                        if result.output:
                            f.write(f"Output: {result.output}\n")
                        if result.error:
                            f.write(f"Error: {result.error}\n")
                        f.write(f"Time: {result.processing_time:.3f}s\n\n")
            
            return True
        
        except Exception:
            return False
    
    def get_job_stats(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a batch job."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        total_time = 0.0
        if job.started_at and job.completed_at:
            from datetime import datetime as dt
            start = dt.fromisoformat(job.started_at.replace("Z", ""))
            end = dt.fromisoformat(job.completed_at.replace("Z", ""))
            total_time = (end - start).total_seconds()
        
        return {
            "job_id": job_id,
            "total_inputs": len(job.inputs),
            "total_processed": job.total_processed,
            "total_failed": job.total_failed,
            "success_rate": job.total_processed / len(job.inputs) * 100 if job.inputs else 0,
            "total_time": total_time,
            "avg_time_per_item": total_time / len(job.inputs) if job.inputs else 0,
        }
    
    def _save_job(self, job: BatchJob) -> None:
        """Save job to disk."""
        job_file = self.jobs_dir / f"{job.job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job.to_dict(), f, indent=2)


# Global batch processor instance
_batch_processor: Optional[BatchProcessor] = None


def get_batch_processor(jobs_dir: Optional[Path] = None) -> BatchProcessor:
    """Get or create the global BatchProcessor instance."""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor(jobs_dir)
    return _batch_processor
