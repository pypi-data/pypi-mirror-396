"""
Connectors API client
"""

from typing import Dict, Any, Optional, List

from gomask.api.client import GoMaskAPIClient, APIError
from gomask.utils.logger import logger


class ConnectorsAPI:
    """API client for connector operations"""

    def __init__(self, client: GoMaskAPIClient):
        """
        Initialize connectors API

        Args:
            client: Base API client
        """
        self.client = client

    def list_connectors(self) -> List[Dict[str, Any]]:
        """
        List all connectors for the authenticated team

        Returns:
            List of connector dictionaries
        """
        response = self.client.get("/cli/connectors")
        # The API returns a list directly, not a dict with "connectors" key
        return response if isinstance(response, list) else []

    def get_connector(self, connector_id: int) -> Dict[str, Any]:
        """
        Get a connector by ID

        Args:
            connector_id: Connector ID

        Returns:
            Connector data
        """
        return self.client.get(f"/cli/connectors/{connector_id}")

    def get_connector_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a connector by name

        Args:
            name: Connector name

        Returns:
            Connector data or None if not found
        """
        try:
            return self.client.get(f"/cli/connectors/by-name/{name}")
        except APIError as e:
            if e.status_code == 404:
                return None
            raise

    def create_connector(self, connector_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new connector

        Args:
            connector_data: Connector configuration

        Returns:
            Created connector data
        """
        # Ensure required fields
        required_fields = ['name', 'type', 'host', 'port', 'database', 'username', 'password']
        for field in required_fields:
            if field not in connector_data:
                raise ValueError(f"Missing required field: {field}")

        logger.info(f"Creating connector: {connector_data['name']}")
        return self.client.post("/cli/connectors", data=connector_data)

    def update_connector(
        self,
        connector_id: int,
        connector_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing connector

        Args:
            connector_id: Connector ID
            connector_data: Updated connector configuration

        Returns:
            Updated connector data
        """
        logger.info(f"Updating connector ID: {connector_id}")
        return self.client.put(f"/cli/connectors/{connector_id}", data=connector_data)

    def delete_connector(self, connector_id: int) -> bool:
        """
        Delete a connector

        Args:
            connector_id: Connector ID

        Returns:
            True if successful
        """
        logger.info(f"Deleting connector ID: {connector_id}")
        self.client.delete(f"/cli/connectors/{connector_id}")
        return True

    def test_connector(self, connector_id: int) -> Dict[str, Any]:
        """
        Test a connector connection

        Args:
            connector_id: Connector ID

        Returns:
            Test results with status and message
        """
        logger.info(f"Testing connector ID: {connector_id}")
        return self.client.post(f"/cli/connectors/{connector_id}/test")

    def test_connector_config(self, connector_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a connector configuration without saving

        Args:
            connector_data: Connector configuration to test

        Returns:
            Test results with status and message
        """
        logger.info("Testing connector configuration")
        return self.client.post("/cli/connectors/test", data=connector_data)

    def get_connector_schemas(self, connector_id: int) -> List[str]:
        """
        Get available schemas for a connector

        Args:
            connector_id: Connector ID

        Returns:
            List of schema names
        """
        response = self.client.get(f"/cli/connectors/{connector_id}/schemas")
        # Handle both list and dict response formats
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("schemas", [])
        return []

    def get_connector_tables(
        self,
        connector_id: int,
        schema_name: str = "public"
    ) -> List[Dict[str, Any]]:
        """
        Get tables for a connector and schema

        Args:
            connector_id: Connector ID
            schema_name: Database schema name

        Returns:
            List of table information
        """
        params = {"schema": schema_name}
        response = self.client.get(f"/cli/connectors/{connector_id}/tables", params=params)
        # Handle both list and dict response formats
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("tables", [])
        return []

    def get_table_columns(
        self,
        connector_id: int,
        table_name: str,
        schema_name: str = "public"
    ) -> List[Dict[str, Any]]:
        """
        Get columns for a specific table

        Args:
            connector_id: Connector ID
            table_name: Table name
            schema_name: Database schema name

        Returns:
            List of column information
        """
        params = {"schema": schema_name, "table": table_name}
        response = self.client.get(f"/cli/connectors/{connector_id}/columns", params=params)
        # Handle both list and dict response formats
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("columns", [])
        return []