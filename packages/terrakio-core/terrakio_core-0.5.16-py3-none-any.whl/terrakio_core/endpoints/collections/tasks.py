import time
from typing import Any, Dict, List, Optional

from dateutil import parser
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from ...exceptions import (
    CancelAllTasksError,
    CancelCollectionTasksError,
    CancelTaskError,
    CollectionNotFoundError,
    GetTaskError,
    ListTasksError,
    TaskNotFoundError,
)
from ...helper.decorators import require_api_key


class TasksMixin:
    """Task management operations."""
    
    async def track_progress(self, task_id, poll_interval: int = 10) -> None:
        task_info = await self.get_task(task_id=task_id)
        number_of_jobs = task_info["task"]["total"]
        start_time = parser.parse(task_info["task"]["createdAt"])
        
        self.console.print(f"[bold cyan]Tracking task: {task_id}[/bold cyan]")
        
        completed_jobs_info = []
        
        def get_job_description(job_info, include_status=False):
            if not job_info:
                return "No job info"
            
            service = job_info.get("service", "Unknown service")
            desc = service
            
            if include_status:
                status = job_info.get("status", "unknown")
                desc += f" - {status}"
            
            return desc
        
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        )
        
        with progress:
            last_completed_count = 0
            current_job_task = None
            current_job_description = None
            
            while len(completed_jobs_info) < number_of_jobs:
                task_info = await self.get_task(task_id=task_id)
                completed_number = task_info["task"]["completed"]
                current_job_info = task_info["currentJob"]
                
                # Check task-level status first
                task_status = task_info.get("task", {}).get("status", "").lower()
                if task_status in ["error", "failed", "cancelled"]:
                    progress.stop()
                    error_msg = f"\n[bold red]Task {task_status}![/bold red]"
                    
                    # Try to get error details from currentJob
                    if current_job_info and current_job_info.get("error"):
                        error_msg += f"\n[red]Reason: {current_job_info['error']}[/red]"
                    
                    self.console.print(error_msg)
                    return
                
                # Check for error/cancelled/failed status in current job
                if current_job_info:
                    status = current_job_info.get("status", "").lower()
                    if status in ["error", "failed", "cancelled"]:
                        progress.stop()
                        error_msg = f"\n[bold red]Job {status}![/bold red]"
                        
                        # Get error details if available
                        if current_job_info.get("error"):
                            error_msg += f"\n[red]Reason: {current_job_info['error']}[/red]"
                        
                        self.console.print(error_msg)
                        return
                
                if completed_number > last_completed_count:
                    if current_job_task is not None:
                        completed_description = current_job_description.replace(" - pending", "").replace(" - running", "").replace(" - waiting", "")
                        completed_description += " - completed"
                        
                        progress.update(
                            current_job_task,
                            description=f"[{last_completed_count + 1}/{number_of_jobs}] {completed_description}",
                            completed=100
                        )
                        completed_jobs_info.append({
                            "task": current_job_task,
                            "description": completed_description,
                            "job_number": last_completed_count + 1
                        })
                        current_job_task = None
                        current_job_description = None
                    
                    last_completed_count = completed_number
                
                if current_job_info:
                    status = current_job_info["status"]
                    current_job_description = get_job_description(current_job_info, include_status=True)
                    
                    total_value = current_job_info.get("total", 0)
                    completed_value = current_job_info.get("completed", 0)
                    
                    if total_value == -9999:
                        percent = 0
                    elif total_value > 0:
                        percent = int(completed_value / total_value * 100)
                    else:
                        percent = 0
                    
                    if current_job_task is None:
                        current_job_task = progress.add_task(
                            f"[{completed_number + 1}/{number_of_jobs}] {current_job_description}",
                            total=100,
                            start_time=start_time
                        )
                    else:
                        progress.update(
                            current_job_task,
                            description=f"[{completed_number + 1}/{number_of_jobs}] {current_job_description}",
                            completed=percent
                        )
                    
                    if status == "Completed":
                        completed_description = current_job_description.replace(" - pending", "").replace(" - running", "").replace(" - waiting", "")
                        completed_description += " - completed"
                        progress.update(
                            current_job_task, 
                            description=f"[{completed_number + 1}/{number_of_jobs}] {completed_description}",
                            completed=100
                        )
                
                if completed_number == number_of_jobs and current_job_info is None:
                    if current_job_task is not None:
                        completed_description = current_job_description.replace(" - pending", "").replace(" - running", "").replace(" - waiting", "")
                        completed_description += " - completed"
                        progress.update(
                            current_job_task,
                            description=f"[{number_of_jobs}/{number_of_jobs}] {completed_description}",
                            completed=100
                        )
                        completed_jobs_info.append({
                            "task": current_job_task,
                            "description": completed_description,
                            "job_number": number_of_jobs
                        })
                    break
                
                time.sleep(poll_interval)
        
        self.console.print(f"[bold green]All {number_of_jobs} jobs finished![/bold green]")

    @require_api_key
    async def list_tasks(
        self,
        limit: Optional[int] = 10,
        page: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """
        List tasks for the current user.

        Args:
            limit: Number of tasks to return (optional, defaults to 10)
            page: Page number (optional, defaults to 0)
        
        Returns:
            API response as a list of dictionaries containing task information
            
        Raises:
            ListTasksError: If the API request fails due to unknown reasons
        """
        params = {
            "limit": limit,
            "page": page
        }
        response, status = await self._client._terrakio_request("GET", "tasks", params=params)

        if status != 200:
            raise ListTasksError(f"List tasks failed with status {status}", status_code=status)

        return response
        
    @require_api_key
    async def get_task(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Get task information by task ID.

        Args:
            task_id: ID of task to track
        
        Returns:
            API response as a dictionary containing task information

        Raises:
            TaskNotFoundError: If the task is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"tasks/info/{task_id}")

        if status != 200:
            if status == 404:
                raise TaskNotFoundError(f"Task {task_id} not found", status_code=status)
            raise GetTaskError(f"Get task failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def cancel_task(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a task by task ID.

        Args:
            task_id: ID of task to cancel

        Returns:
            API response as a dictionary containing task information

        Raises:
            TaskNotFoundError: If the task is not found
            CancelTaskError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("POST", f"tasks/cancel/{task_id}")
        
        if status != 200:
            if status == 404:
                raise TaskNotFoundError(f"Task {task_id} not found", status_code=status)
            raise CancelTaskError(f"Cancel task failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def cancel_collection_tasks(
        self,
        collection: str
    ) -> Dict[str, Any]:
        """
        Cancel all tasks for a collection.

        Args:
            collection: Name of collection

        Returns:
            API response as a dictionary containing task information for the collection

        Raises:
            CollectionNotFoundError: If the collection is not found
            CancelCollectionTasksError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/cancel")
        
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise CancelCollectionTasksError(f"Cancel collection tasks failed with status {status}", status_code=status)
    
        return response

    @require_api_key
    async def cancel_all_tasks(
        self
    ) -> Dict[str, Any]:
        """
        Cancel all tasks for the current user.

        Returns:
            API response as a dictionary containing task information for all tasks

        Raises:
            CancelAllTasksError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("POST", "tasks/cancel")

        if status != 200:
            raise CancelAllTasksError(f"Cancel all tasks failed with status {status}", status_code=status)

        return response

