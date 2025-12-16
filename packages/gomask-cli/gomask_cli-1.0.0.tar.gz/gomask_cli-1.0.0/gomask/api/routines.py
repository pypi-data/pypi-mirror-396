"""
Routines API client
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.utils.logger import logger
from gomask.utils.hash import calculate_config_hash


class RoutinesAPI:
    """API client for routine operations"""

    def __init__(self, client: GoMaskAPIClient):
        """
        Initialize routines API

        Args:
            client: Base API client
        """
        self.client = client

    def list_routines(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List routines for the authenticated team

        Args:
            limit: Maximum number of routines to return
            offset: Pagination offset

        Returns:
            List of routine dictionaries
        """
        params = {"limit": limit, "offset": offset}
        response = self.client.get("/cli/routines", params=params)
        return response.get("routines", [])

    def get_routine(self, routine_id: int) -> Dict[str, Any]:
        """
        Get a routine by ID

        Args:
            routine_id: Routine ID

        Returns:
            Routine data
        """
        return self.client.get(f"/cli/routines/{routine_id}/details")

    def get_routine_by_unique_id(self, unique_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a routine by unique ID

        Args:
            unique_id: Unique identifier

        Returns:
            Routine data or None if not found
        """
        try:
            return self.client.get(f"/cli/routines/by-unique-id/{unique_id}")
        except APIError as e:
            if e.status_code == 404:
                return None
            raise

    def get_routine_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a routine by name (for current team)

        Args:
            name: Routine name

        Returns:
            Routine data or None if not found
        """
        # Generate the same unique_id that would be created for this name
        import hashlib
        unique_id = f"{name.lower().replace(' ', '-')}-{hashlib.md5(name.encode()).hexdigest()[:8]}"
        return self.get_routine_by_unique_id(unique_id)

    def create_routine(self, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new routine

        Args:
            routine_data: Routine configuration

        Returns:
            Created routine data
        """
        return self.client.post("/cli/routines", data=routine_data)

    def update_routine(self, routine_id: int, routine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing routine

        Args:
            routine_id: Routine ID
            routine_data: Updated routine configuration

        Returns:
            Updated routine data
        """
        return self.client.put(f"/cli/routines/{routine_id}", data=routine_data)

    def delete_routine(self, routine_id: int) -> bool:
        """
        Delete a routine

        Args:
            routine_id: Routine ID

        Returns:
            True if successful
        """
        self.client.delete(f"/cli/routines/{routine_id}")
        return True

    def import_yaml(self, yaml_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import a routine from YAML configuration using new schema format

        Args:
            yaml_config: Parsed YAML configuration

        Returns:
            Imported routine data
        """
        # Calculate config hash
        config_hash = calculate_config_hash(yaml_config)

        # Add metadata
        import_data = {
            "yaml_config": yaml_config,
            "config_hash": config_hash,
            "source_type": "cli"
        }

        # With new schema format, we use name as identifier
        # Generate a unique_id from name for tracking
        routine_info = yaml_config.get("routine", {})
        name = routine_info.get("name", "")

        # Check if a routine with same name exists by looking for it with generated unique_id
        # The backend will handle the unique_id generation in the same way
        import hashlib
        unique_id = f"{name.lower().replace(' ', '-')}-{hashlib.md5(name.encode()).hexdigest()[:8]}"

        existing = None
        if unique_id:
            try:
                existing = self.get_routine_by_unique_id(unique_id)
            except APIError:
                pass  # Routine doesn't exist

        if existing:
            # Update existing routine
            logger.info(f"Updating existing routine: {name} (ID: {existing['id']})")
            return self.client.put(
                f"/cli/routines/import-yaml/{existing['id']}",
                data=import_data
            )

        # Create new routine
        logger.info(f"Creating new routine: {name}")
        return self.client.post("/cli/routines/import-yaml", data=import_data)

    def export_yaml(self, routine_id: int) -> Dict[str, Any]:
        """
        Export a routine to YAML format

        Args:
            routine_id: Routine ID

        Returns:
            YAML configuration dictionary
        """
        return self.client.get(f"/cli/routines/{routine_id}/export-yaml")

    def validate_yaml(self, yaml_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a YAML configuration

        Args:
            yaml_config: Parsed YAML configuration

        Returns:
            Validation results
        """
        return self.client.post("/cli/routines/validate", data=yaml_config)

    def execute_routine(
        self,
        routine_id: int,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a routine

        Args:
            routine_id: Routine ID
            parameters: Runtime parameters

        Returns:
            Execution information
        """
        data = {"parameters": parameters or {}}
        return self.client.post(f"/cli/routines/{routine_id}/execute", data=data)

    def get_execution_status(self, execution_id: int) -> Dict[str, Any]:
        """
        Get execution status

        Args:
            execution_id: Execution ID

        Returns:
            Execution status information
        """
        return self.client.get(f"/cli/executions/{execution_id}")

    def cancel_execution(self, execution_id: int) -> bool:
        """
        Cancel a running execution

        Args:
            execution_id: Execution ID

        Returns:
            True if successful
        """
        self.client.post(f"/cli/executions/{execution_id}/cancel")
        return True

    def get_execution_logs(
        self,
        execution_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[str]:
        """
        Get execution logs

        Args:
            execution_id: Execution ID
            limit: Maximum number of log entries
            offset: Pagination offset

        Returns:
            List of log entries
        """
        params = {"limit": limit, "offset": offset}
        response = self.client.get(f"/cli/executions/{execution_id}/logs", params=params)
        return response.get("logs", [])