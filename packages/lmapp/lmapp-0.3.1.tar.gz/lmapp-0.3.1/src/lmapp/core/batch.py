"""
Batch processing module for LMAPP v0.2.4.

Enables running queries on multiple inputs and generating batch reports.
Supports processing files, directories, or stdin with progress tracking.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime


@dataclass
class BatchItem:
    """Represents a single item in a batch."""

    id: str
    input_data: str
    output_data: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BatchProcessor:
    """Processes multiple items in a batch."""

    def __init__(self, name: str, on_item: Callable):
        """
        Initialize batch processor.

        Args:
            name: Name of the batch job
            on_item: Callback function called for each item
        """
        self.name = name
        self.on_item = on_item
        self.items: List[BatchItem] = []
        self.results: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def add_item(self, id: str, data: str, metadata: Optional[Dict] = None) -> None:
        """Add item to batch."""
        item = BatchItem(id=id, input_data=data, metadata=metadata or {})
        self.items.append(item)

    def process(self) -> Dict[str, Any]:
        """Process all items in batch."""
        self.start_time = datetime.utcnow()
        self.results = {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "items_total": len(self.items),
            "items_completed": 0,
            "items_failed": 0,
            "results": [],
        }

        for item in self.items:
            item.status = "processing"

            try:
                output = self.on_item(item.input_data, item.metadata)
                item.output_data = output
                item.status = "completed"
                self.results["items_completed"] += 1
            except Exception as e:
                item.error = str(e)
                item.status = "failed"
                self.results["items_failed"] += 1

            self.results["results"].append(item.to_dict())

        self.end_time = datetime.utcnow()
        self.results["end_time"] = self.end_time.isoformat()
        self.results["duration_seconds"] = (
            self.end_time - self.start_time
        ).total_seconds()

        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get batch processing summary."""
        if not self.results:
            return {}

        return {
            "name": self.results["name"],
            "items_total": self.results["items_total"],
            "items_completed": self.results["items_completed"],
            "items_failed": self.results["items_failed"],
            "duration_seconds": self.results.get("duration_seconds", 0),
            "success_rate": (
                self.results["items_completed"] / self.results["items_total"]
                if self.results["items_total"] > 0
                else 0
            ),
        }

    def save_results(self, output_file: Path) -> None:
        """Save results to JSON file."""
        output_file.write_text(json.dumps(self.results, indent=2))

    def load_results(self, input_file: Path) -> bool:
        """Load results from JSON file."""
        try:
            self.results = json.loads(input_file.read_text())
            return True
        except (json.JSONDecodeError, IOError):
            return False


class BatchJobManager:
    """Manages multiple batch jobs."""

    def __init__(self, jobs_dir: Optional[Path] = None):
        """Initialize job manager."""
        if jobs_dir is None:
            home = Path.home()
            jobs_dir = home / ".lmapp" / "batch_jobs"

        self.jobs_dir = Path(jobs_dir)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

        self.jobs: Dict[str, BatchProcessor] = {}

    def create_job(self, job_name: str, on_item: Callable) -> BatchProcessor:
        """Create a new batch job."""
        processor = BatchProcessor(job_name, on_item)
        self.jobs[job_name] = processor
        return processor

    def process_file(
        self,
        job_name: str,
        file_path: Path,
        on_item: Callable,
        one_per_line: bool = True,
    ) -> Dict[str, Any]:
        """
        Process items from a file.

        Args:
            job_name: Name of batch job
            file_path: Path to input file
            on_item: Callback for processing each item
            one_per_line: If True, treat each line as separate item

        Returns:
            Batch results
        """
        processor = self.create_job(job_name, on_item)

        try:
            content = file_path.read_text()

            if one_per_line:
                for i, line in enumerate(content.splitlines()):
                    if line.strip():
                        processor.add_item(
                            id=f"line_{i}",
                            data=line,
                            metadata={"line_number": i},
                        )
            else:
                processor.add_item(id="file_0", data=content)

            results = processor.process()

            # Save results
            results_file = (
                self.jobs_dir / f"{job_name}_results.json"
            )
            processor.save_results(results_file)

            return results
        except Exception as e:
            return {"error": str(e)}

    def process_directory(
        self,
        job_name: str,
        dir_path: Path,
        on_item: Callable,
        pattern: str = "*.txt",
    ) -> Dict[str, Any]:
        """
        Process items from all files in directory.

        Args:
            job_name: Name of batch job
            dir_path: Directory path
            on_item: Callback for processing each item
            pattern: File pattern to match

        Returns:
            Batch results
        """
        processor = self.create_job(job_name, on_item)

        try:
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    processor.add_item(
                        id=str(file_path.name),
                        data=content,
                        metadata={"file_path": str(file_path)},
                    )

            results = processor.process()

            # Save results
            results_file = (
                self.jobs_dir / f"{job_name}_results.json"
            )
            processor.save_results(results_file)

            return results
        except Exception as e:
            return {"error": str(e)}

    def get_job(self, job_name: str) -> Optional[BatchProcessor]:
        """Get a batch job."""
        return self.jobs.get(job_name)

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all batch jobs."""
        jobs_list = []

        for job_name, processor in self.jobs.items():
            summary = processor.get_summary()
            summary["name"] = job_name
            jobs_list.append(summary)

        return jobs_list

    def load_results(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Load results from a previous job."""
        results_file = self.jobs_dir / f"{job_name}_results.json"

        if not results_file.exists():
            return None

        try:
            return json.loads(results_file.read_text())
        except json.JSONDecodeError:
            return None


_batch_manager: Optional[BatchJobManager] = None


def get_batch_manager(jobs_dir: Optional[Path] = None) -> BatchJobManager:
    """Get or create the global BatchJobManager instance."""
    global _batch_manager
    if _batch_manager is None:
        _batch_manager = BatchJobManager(jobs_dir)
    return _batch_manager
