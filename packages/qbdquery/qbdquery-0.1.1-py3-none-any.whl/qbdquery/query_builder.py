"""Query builder for constructing and parsing QBXML requests."""

import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any


class QueryBuilder:
    """Builds QBXML queries and parses responses."""

    # Common fields for different entity types
    DEFAULT_FIELDS = {
        "Customer": ["ListID", "FullName", "IsActive", "Email", "Phone", "Balance"],
        "Vendor": ["ListID", "Name", "IsActive", "Email", "Phone", "Balance"],
        "Invoice": ["TxnID", "RefNumber", "CustomerRef", "TxnDate", "DueDate", "BalanceRemaining"],
        "Item": ["ListID", "FullName", "IsActive", "Type", "Description", "Price"],
        "Employee": ["ListID", "Name", "IsActive", "Email", "Phone"],
        "Account": ["ListID", "FullName", "IsActive", "AccountType", "Balance"],
    }

    # Mapping of entity types to their query request names
    ENTITY_QUERY_MAPPING = {
        "Customer": "CustomerQueryRq",
        "Vendor": "VendorQueryRq",
        "Invoice": "InvoiceQueryRq",
        "Item": "ItemQueryRq",
        "Employee": "EmployeeQueryRq",
        "Account": "AccountQueryRq",
        "Bill": "BillQueryRq",
        "Check": "CheckQueryRq",
        "CreditMemo": "CreditMemoQueryRq",
        "Estimate": "EstimateQueryRq",
        "PurchaseOrder": "PurchaseOrderQueryRq",
        "SalesOrder": "SalesOrderQueryRq",
        "SalesReceipt": "SalesReceiptQueryRq",
    }

    # Mapping of entity types to their response element names
    ENTITY_RESPONSE_MAPPING = {
        "Customer": "CustomerRet",
        "Vendor": "VendorRet",
        "Invoice": "InvoiceRet",
        "Item": "ItemRet",
        "Employee": "EmployeeRet",
        "Account": "AccountRet",
        "Bill": "BillRet",
        "Check": "CheckRet",
        "CreditMemo": "CreditMemoRet",
        "Estimate": "EstimateRet",
        "PurchaseOrder": "PurchaseOrderRet",
        "SalesOrder": "SalesOrderRet",
        "SalesReceipt": "SalesReceiptRet",
    }

    def __init__(self, entity_type: str, qbxml_version: str = "13.0"):
        """
        Initialize query builder.

        Args:
            entity_type: Type of entity to query (e.g., "Customer", "Invoice").
            qbxml_version: QBXML version to use.
        """
        self.entity_type = entity_type
        self.qbxml_version = qbxml_version

        if entity_type not in self.ENTITY_QUERY_MAPPING:
            raise ValueError(
                f"Unsupported entity type: {entity_type}. "
                f"Supported types: {', '.join(self.ENTITY_QUERY_MAPPING.keys())}"
            )

    def build(
        self,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = None
    ) -> str:
        """
        Build QBXML query request.

        Args:
            fields: List of fields to include in response.
            filters: Dictionary of filter criteria.
            max_results: Maximum number of results.

        Returns:
            QBXML request string.
        """
        query_type = self.ENTITY_QUERY_MAPPING[self.entity_type]

        xml_parts = [
            f'<?xml version="1.0" encoding="utf-8"?>',
            f'<?qbxml version="{self.qbxml_version}"?>',
            '<QBXML>',
            '    <QBXMLMsgsRq onError="continueOnError">',
            f'        <{query_type}>',
        ]

        # Add filters
        if filters:
            for key, value in filters.items():
                xml_parts.append(f'            <{key}>{value}</{key}>')

        # Add max results if specified
        if max_results:
            xml_parts.append(f'            <MaxReturned>{max_results}</MaxReturned>')

        # Add field selection if specified
        if fields:
            for field in fields:
                xml_parts.append(f'            <IncludeRetElement>{field}</IncludeRetElement>')

        xml_parts.extend([
            f'        </{query_type}>',
            '    </QBXMLMsgsRq>',
            '</QBXML>'
        ])

        return '\n'.join(xml_parts)

    def parse_response(
        self,
        root: ET.Element,
        requested_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Parse QBXML response into list of dictionaries.

        Args:
            root: Root element of parsed QBXML response.
            requested_fields: Fields that were requested (for filtering output).

        Returns:
            List of dictionaries containing entity data.
        """
        response_type = self.ENTITY_RESPONSE_MAPPING[self.entity_type]
        results = []

        for entity in root.findall(f'.//{response_type}'):
            entity_data = self._parse_entity(entity, requested_fields)
            results.append(entity_data)

        return results

    def _parse_entity(
        self,
        element: ET.Element,
        requested_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse a single entity element into a dictionary.

        Args:
            element: XML element representing the entity.
            requested_fields: Fields to include in output.

        Returns:
            Dictionary of entity data.
        """
        data = {}

        # If no specific fields requested, use defaults for this entity type
        if requested_fields is None:
            requested_fields = self.DEFAULT_FIELDS.get(self.entity_type, [])

        # Parse all child elements
        for child in element:
            field_name = child.tag
            field_value = self._parse_field(child)

            # Include field if it was requested or if no specific fields were requested
            if not requested_fields or field_name in requested_fields:
                data[field_name] = field_value

        return data

    def _parse_field(self, element: ET.Element) -> Any:
        """
        Parse a field element, handling nested structures.

        Args:
            element: XML element representing a field.

        Returns:
            Parsed field value (string, dict, or list).
        """
        # If element has children, it's a complex type
        if len(element) > 0:
            # Check if it's a reference (ListID + FullName pattern)
            if element.find('ListID') is not None or element.find('FullName') is not None:
                ref_data = {}
                for child in element:
                    ref_data[child.tag] = child.text
                return ref_data
            else:
                # Parse as nested dictionary
                nested = {}
                for child in element:
                    nested[child.tag] = self._parse_field(child)
                return nested

        # Simple text value
        return element.text

    def get_available_fields(self) -> List[str]:
        """
        Get list of common fields for this entity type.

        Returns:
            List of field names.
        """
        return self.DEFAULT_FIELDS.get(self.entity_type, [])
