"""
Execution and monitoring API client
"""

import time
from typing import Dict, Any, Optional, List, Generator
from enum import Enum

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.utils.logger import logger


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionAPI:
    """API client for execution and monitoring operations"""

    def __init__(self, client: GoMaskAPIClient):
        """
        Initialize execution API

        Args:
            client: Base API client
        """
        self.client = client

    def start_execution(
        self,
        routine_id: int,
        parameters: Optional[Dict[str, Any]] = None,
        wait: bool = False,
        timeout: int = 3600
    ) -> Dict[str, Any]:
        """
        Start routine execution

        Args:
            routine_id: Routine ID to execute
            parameters: Runtime parameters
            wait: Whether to wait for completion
            timeout: Maximum time to wait in seconds

        Returns:
            Execution information
        """
        # Start execution
        data = {
            "routine_id": routine_id,
            "parameters": parameters or {},
            "source": "cli"
        }

        logger.info(f"Starting execution for routine {routine_id}")
        result = self.client.post(f"/cli/routines/{routine_id}/execute", data=data)

        execution_id = result.get("execution_id")
        if not execution_id:
            raise APIError("No execution ID returned")

        if wait:
            logger.info(f"Waiting for execution {execution_id} to complete...")
            return self.wait_for_completion(execution_id, timeout)

        return result

    def get_status(self, execution_id: int) -> Dict[str, Any]:
        """
        Get execution status

        Args:
            execution_id: Execution ID

        Returns:
            Status information
        """
        return self.client.get(f"/cli/executions/{execution_id}")

    def wait_for_completion(
        self,
        execution_id: int,
        timeout: int = 3600,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for execution to complete

        Args:
            execution_id: Execution ID
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            Final execution status

        Raises:
            TimeoutError: If execution doesn't complete within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status_info = self.get_status(execution_id)
            status = status_info.get("status")

            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                return status_info

            time.sleep(poll_interval)

        raise TimeoutError(f"Execution {execution_id} did not complete within {timeout} seconds")

    def stream_logs(
        self,
        execution_id: int,
        follow: bool = True,
        poll_interval: int = 2
    ) -> Generator[str, None, None]:
        """
        Stream execution logs

        Args:
            execution_id: Execution ID
            follow: Whether to keep following new logs
            poll_interval: Time between log checks in seconds

        Yields:
            Log entries as they become available
        """
        last_offset = 0
        execution_complete = False

        while not execution_complete or not follow:
            # Get logs
            response = self.client.get(
                f"/cli/executions/{execution_id}/logs",
                params={"offset": last_offset, "limit": 100}
            )

            logs = response.get("logs", [])
            for log in logs:
                yield log

            # Update offset
            if logs:
                last_offset += len(logs)

            # Check if execution is complete
            if follow:
                status_info = self.get_status(execution_id)
                status = status_info.get("status")
                execution_complete = status in [
                    ExecutionStatus.COMPLETED,
                    ExecutionStatus.FAILED,
                    ExecutionStatus.CANCELLED
                ]

                if not logs and not execution_complete:
                    time.sleep(poll_interval)
            else:
                break

    def get_progress(self, execution_id: int) -> Dict[str, Any]:
        """
        Get execution progress information

        Args:
            execution_id: Execution ID

        Returns:
            Progress information including percentage, current table, records processed
        """
        response = self.client.get(f"/cli/executions/{execution_id}/progress")
        return response

    def cancel(self, execution_id: int) -> bool:
        """
        Cancel a running execution

        Args:
            execution_id: Execution ID

        Returns:
            True if cancellation was successful
        """
        logger.info(f"Cancelling execution {execution_id}")
        self.client.post(f"/cli/executions/{execution_id}/cancel")
        return True

    def get_summary(self, execution_id: int) -> Dict[str, Any]:
        """
        Get execution summary

        Args:
            execution_id: Execution ID

        Returns:
            Summary with statistics, errors, and timing
        """
        return self.client.get(f"/cli/executions/{execution_id}/summary")

    def list_executions(
        self,
        routine_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List executions

        Args:
            routine_id: Filter by routine ID
            status: Filter by status
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of execution records
        """
        params = {
            "limit": limit,
            "offset": offset
        }

        if routine_id:
            params["routine_id"] = routine_id
        if status:
            params["status"] = status

        response = self.client.get("/cli/executions", params=params)
        return response.get("executions", [])