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
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = None,
        include_inactive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query any QuickBooks entity type.

        Args:
            entity_type: Entity type (e.g., "Customer", "Invoice", "Item")
            name: Filter by name or ref number (FullName/Name/RefNumber fields)
            search: Dict of field:value pairs to search (e.g., {"Email": "example.com"})
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
        results = builder.parse_response(root, fields)

        if name and len(name) > 2:
            results = self._filter_by_name(results, name)

        if search:
            results = self._filter_by_fields(results, search)

        return results

    def query_customers(
        self,
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query customers with optional filtering."""
        return self.query(
            "Customer",
            name=name,
            search=search,
            fields=fields,
            include_inactive=include_inactive,
            max_results=max_results
        )

    def _filter_by_name(
        self,
        results: List[Dict[str, Any]],
        name: str
    ) -> List[Dict[str, Any]]:
        """Filter results by name or reference number."""
        name_lower = name.lower()
        filtered = []

        for item in results:
            # Try different name fields depending on entity type
            item_name = (
                item.get("FullName") or  # Customer, Item, Account
                item.get("Name") or      # Vendor, Employee
                item.get("RefNumber") or # Invoice, Bill, Check, etc.
                ""
            )
            parts = item_name.split(":")

            if any(name_lower in part.lower() for part in parts):
                filtered.append(item)

        return filtered

    def _filter_by_fields(
        self,
        results: List[Dict[str, Any]],
        search_fields: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Filter results by arbitrary field values."""
        filtered = []

        for item in results:
            matches = True
            for field, value in search_fields.items():
                item_value = str(item.get(field, ""))
                if value.lower() not in item_value.lower():
                    matches = False
                    break
            if matches:
                filtered.append(item)

        return filtered

    def query_invoices(
        self,
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query invoices."""
        return self.query("Invoice", name=name, search=search, fields=fields, filters=filters, max_results=max_results)

    def query_items(
        self,
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query items (products/services)."""
        return self.query("Item", name=name, search=search, fields=fields, include_inactive=include_inactive, max_results=max_results)

    def query_vendors(
        self,
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query vendors."""
        return self.query("Vendor", name=name, search=search, fields=fields, include_inactive=include_inactive, max_results=max_results)

    def query_employees(
        self,
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query employees."""
        return self.query("Employee", name=name, search=search, fields=fields, include_inactive=include_inactive, max_results=max_results)

    def query_accounts(
        self,
        name: Optional[str] = None,
        search: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        include_inactive: bool = True,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query chart of accounts."""
        return self.query("Account", name=name, search=search, fields=fields, include_inactive=include_inactive, max_results=max_results)
