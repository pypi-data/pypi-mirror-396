"""Core QuickBooks Desktop client for querying data."""

import win32com.client
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager

from .exceptions import QBDConnectionError, QBDSessionError
from .query_builder import QueryBuilder


class QuickBooksClient:
    """
    Main client for interacting with QuickBooks Desktop.

    Supports querying various QuickBooks lists and entities with flexible
    field selection, filtering, and result formatting.
    """

    def __init__(
        self,
        company_file: Optional[str] = None,
        app_name: str = "QBDQuery Python Client",
        qbxml_version: str = "13.0"
    ):
        """
        Initialize QuickBooks client.

        Args:
            company_file: Path to QuickBooks company file. If None, uses currently open file.
            app_name: Name of your application (shown in QuickBooks).
            qbxml_version: QBXML version to use (default: 13.0).
        """
        self.company_file = company_file or ""
        self.app_name = app_name
        self.qbxml_version = qbxml_version
        self._qb = None
        self._ticket = None

    @contextmanager
    def session(self):
        """Context manager for QuickBooks session."""
        try:
            self._connect()
            yield self
        finally:
            self._disconnect()

    def _connect(self):
        """Establish connection and session with QuickBooks."""
        try:
            self._qb = win32com.client.Dispatch("QBXMLRP2.RequestProcessor")
            self._qb.OpenConnection("", self.app_name)

            # BeginSession: first param is company file path, second is session mode
            # 0 = use currently open file, 1 = single user mode, 2 = multi-user mode
            mode = 0 if not self.company_file else 1
            self._ticket = self._qb.BeginSession(self.company_file, mode)
        except Exception as e:
            raise QBDConnectionError(f"Failed to connect to QuickBooks: {str(e)}")

    def _disconnect(self):
        """Close QuickBooks session and connection."""
        if self._ticket and self._qb:
            try:
                self._qb.EndSession(self._ticket)
            except Exception as e:
                raise QBDSessionError(f"Failed to end session: {str(e)}")

        if self._qb:
            try:
                self._qb.CloseConnection()
            except Exception as e:
                raise QBDConnectionError(f"Failed to close connection: {str(e)}")

        self._qb = None
        self._ticket = None

    def _execute_request(self, xml_request: str) -> ET.Element:
        """Execute QBXML request and return parsed response."""
        if not self._qb or not self._ticket:
            raise QBDSessionError("No active QuickBooks session")

        try:
            response = self._qb.ProcessRequest(self._ticket, xml_request)
            return ET.fromstring(response)
        except Exception as e:
            raise QBDSessionError(f"Failed to process request: {str(e)}")

    def query(
        self,
        entity_type: str,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = None,
        include_inactive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query any QuickBooks entity type.

        Args:
            entity_type: Entity type (e.g., "Customer", "Invoice", "Item")
            fields: List of fields to return
            filters: Filter criteria dict
            max_results: Maximum results to return
            include_inactive: Include inactive records

        Returns:
            List of dicts with entity data
        """
        builder = QueryBuilder(entity_type, self.qbxml_version)

        if not include_inactive and "ActiveStatus" not in (filters or {}):
            if filters is None:
                filters = {}
            filters["ActiveStatus"] = "ActiveOnly"

        xml_request = builder.build(
            fields=fields,
            filters=filters,
            max_results=max_results
        )

        root = self._execute_request(xml_request)
        return builder.parse_response(root, fields)

    def query_customers(
        self,
        search_term: Optional[str] = None,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query customers with optional search filtering.

        Args:
            search_term: Optional search term to filter customers.
            fields: List of fields to return.
            include_inactive: Include inactive customers.
            max_results: Maximum number of results.

        Returns:
            List of customer dictionaries.
        """
        filters = {}
        if not include_inactive:
            filters["ActiveStatus"] = "ActiveOnly"

        results = self.query("Customer", fields=fields, filters=filters, max_results=max_results)

        if search_term and len(search_term) > 2:
            return self._filter_customers_by_search(results, search_term)

        return results

    def _filter_customers_by_search(
        self,
        customers: List[Dict[str, Any]],
        search_term: str
    ) -> List[Dict[str, Any]]:
        """Filter customers by search term in their full name."""
        search_lower = search_term.lower()
        filtered = []

        for customer in customers:
            full_name = customer.get("FullName", "")
            parts = full_name.split(":")

            if any(search_lower in part.lower() for part in parts):
                filtered.append(customer)

        return filtered

    def query_invoices(
        self,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query invoices."""
        return self.query("Invoice", fields=fields, filters=filters, max_results=max_results)

    def query_items(
        self,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query items (products/services)."""
        return self.query("Item", fields=fields, include_inactive=include_inactive, max_results=max_results)

    def query_vendors(
        self,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query vendors."""
        return self.query("Vendor", fields=fields, include_inactive=include_inactive, max_results=max_results)

    def query_employees(
        self,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query employees."""
        return self.query("Employee", fields=fields, include_inactive=include_inactive, max_results=max_results)

    def query_accounts(
        self,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query chart of accounts."""
        return self.query("Account", fields=fields, include_inactive=include_inactive, max_results=max_results)
