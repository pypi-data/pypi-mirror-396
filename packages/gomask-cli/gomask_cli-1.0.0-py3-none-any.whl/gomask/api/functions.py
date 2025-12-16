"""
Data Functions API client
"""

from typing import Dict, Any, List, Optional

from gomask.utils.logger import logger


class FunctionsAPI:
    """API client for data functions operations"""

    def __init__(self, client):
        self.client = client

    def list_functions(
        self,
        function_type: Optional[str] = None,
        data_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List data functions with optional filters

        Args:
            function_type: Filter by function type (utility, transformer, generator)
            data_type: Filter by data type (e.g., 'string', 'number')
            tags: Filter by tags (e.g., ['medical', 'healthcare'])
            category: Filter by category
            search: Search in function name and description
            limit: Limit number of results

        Returns:
            List of data functions
        """
        params = {}

        if function_type:
            params['function_type'] = function_type

        if data_type:
            params['data_type'] = data_type

        if tags:
            # Convert list of tags to comma-separated string for query param
            params['tags'] = ','.join(tags)

        if category:
            params['category'] = category

        if search:
            params['search'] = search

        if limit:
            params['limit'] = limit

        response = self.client.get(
            path='/cli/functions',
            params=params
        )

        functions = response.get('functions', [])

        # Apply client-side limit if backend didn't limit
        if limit and len(functions) > limit:
            functions = functions[:limit]

        return functions

    def get_function_by_id(self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific function by ID

        Args:
            function_id: ID of the function

        Returns:
            Function details or None if not found
        """
        try:
            response = self.client.get(
                path=f'/cli/functions/id/{function_id}'
            )
            return response
        except Exception:
            return None

    def get_functions_by_name(self, function_name: str) -> List[Dict[str, Any]]:
        """
        Get all functions with a specific name

        Args:
            function_name: Name of the function

        Returns:
            List of function details (may be empty or contain multiple functions)
        """
        response = self.client.get(
            path=f'/cli/functions/name/{function_name}'
        )

        return response.get('functions', [])

    def get_function_categories(self) -> List[str]:
        """
        Get list of available function categories

        Returns:
            List of category names
        """
        response = self.client.get(
            path='/cli/functions/categories'
        )

        return response.get('categories', [])

    def get_function_tags(self) -> List[str]:
        """
        Get list of all available tags

        Returns:
            List of tag names
        """
        response = self.client.get(
            path='/cli/functions/tags'
        )

        return response.get('tags', [])