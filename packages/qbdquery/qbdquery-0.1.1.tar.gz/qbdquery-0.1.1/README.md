# QBDQuery

A Python package for querying QuickBooks Desktop data.

https://pypi.org/project/qbdquery/0.1.0/

## Features

- Query any QuickBooks Desktop list or transaction type
- Select specific fields to return
- Filter and search capabilities
- Automatic connection management
- Works with either currently open file or specified path


## Installation

```bash
pip install qbdquery
```

## Requirements

- Windows 10+ 
- QuickBooks Desktop (must be running upon inital connection to a company file)
- Python 3.7+

## Quick Start

### Basic Customer Query

```python
from qbdquery import QuickBooksClient

# Create client (uses currently open QuickBooks file by default)
client = QuickBooksClient()

# Query customers with automatic session management
with client.session():
    customers = client.query_customers()
    for customer in customers:
        print(f"{customer['FullName']}: {customer['Email']}")
```

### Specify a Company File

```python
# Connect to a specific company file
client = QuickBooksClient(
    company_file=r"C:\Path\To\Your\Company.QBW"
)

with client.session():
    customers = client.query_customers()
```

### Query with Field Selection

```python
with client.session():
    # Only get specific fields
    customers = client.query_customers(
        fields=["ListID", "FullName", "Email", "Phone", "Balance"]
    )
```

### Search Customers

```python
with client.session():
    # Search by name
    results = client.query_customers(name="smith")

    # Search with field selection
    results = client.query_customers(
        name="acme",
        fields=["FullName", "Email"],
        include_inactive=False
    )

    # Search by email
    results = client.query_customers(
        search={"Email": "gmail.com"}
    )

    # Combine name and field search
    results = client.query_customers(
        name="acme",
        search={"Email": "example.com"},
        fields=["FullName", "Email", "Phone"]
    )
```

### Generic Query Method

Query any QuickBooks entity type:

```python
with client.session():
    # Query invoices by reference number
    invoices = client.query(
        entity_type="Invoice",
        name="INV-2024",  # Searches RefNumber field
        fields=["TxnID", "RefNumber", "TxnDate", "BalanceRemaining"],
        filters={"PaidStatus": "NotPaidOnly"}
    )

    # Query items by name
    items = client.query(
        entity_type="Item",
        name="widget",
        fields=["FullName", "Type", "Price"],
        include_inactive=False
    )
```

### Convenience Methods

```python
with client.session():
    # Query vendors by name
    vendors = client.query_vendors(
        name="supply",
        fields=["Name", "Email", "Balance"],
        include_inactive=False
    )

    # Query items with multiple criteria
    items = client.query_items(
        name="widget",
        search={"Type": "Service"},
        fields=["FullName", "Type", "Description", "Price"]
    )
```

### Custom Filters

```python
with client.session():
    # Advanced filtering
    invoices = client.query(
        entity_type="Invoice",
        filters={
            "TxnDateRangeFilter": {
                "FromTxnDate": "2024-01-01",
                "ToTxnDate": "2024-12-31"
            },
            "PaidStatus": "NotPaidOnly",
            "MaxReturned": 500
        }
    )
```

## Supported Entity Types

- **Lists**: Customer, Vendor, Employee, Item, Account
- **Transactions**: Invoice, Bill, Check, CreditMemo, Estimate, PurchaseOrder, SalesOrder, SalesReceipt
- And more via the generic `query()` method

## API Reference

### QuickBooksClient

#### `__init__(company_file=None, app_name="QBDQuery Python Client", qbxml_version="13.0")`

Initialize the QuickBooks client.

- `company_file`: Path to company file. If `None`, uses currently open file.
- `app_name`: Application name shown in QuickBooks.
- `qbxml_version`: QBXML version to use (default: "13.0").

#### `session()`

Context manager for QuickBooks session. Always use this when querying.

#### `query(entity_type, name=None, search=None, fields=None, filters=None, max_results=None, include_inactive=True)`

Generic query method for any QuickBooks entity.

- `entity_type`: Type of entity (e.g., "Customer", "Invoice")
- `name`: Filter by name or reference number (FullName/Name/RefNumber)
- `search`: Dict of field:value pairs to search (e.g., `{"Email": "example"}`)
- `fields`: List of field names to return
- `filters`: Dictionary of filter criteria
- `max_results`: Maximum number of results
- `include_inactive`: Whether to include inactive records

#### Convenience Methods

- `query_customers(name=None, search=None, fields=None, include_inactive=True, max_results=None)`
- `query_vendors(name=None, search=None, fields=None, include_inactive=True, max_results=None)`
- `query_employees(name=None, search=None, fields=None, include_inactive=True, max_results=None)`
- `query_items(name=None, search=None, fields=None, include_inactive=True, max_results=None)`
- `query_accounts(name=None, search=None, fields=None, include_inactive=True, max_results=None)`
- `query_invoices(name=None, search=None, fields=None, filters=None, max_results=None)`


### Example: Export Customer List to CSV

```python
import csv
from qbdquery import QuickBooksClient

client = QuickBooksClient()

with client.session():
    customers = client.query_customers(
        fields=["FullName", "Email", "Phone", "Balance"],
        include_inactive=False
    )

    with open('customers.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["FullName", "Email", "Phone", "Balance"])
        writer.writeheader()
        writer.writerows(customers)
```

### Example: Find Overdue Invoices

```python
from qbdquery import QuickBooksClient
from datetime import date

client = QuickBooksClient()

with client.session():
    invoices = client.query_invoices(
        fields=["RefNumber", "CustomerRef", "TxnDate", "DueDate", "BalanceRemaining"],
        filters={"PaidStatus": "NotPaidOnly"}
    )

    today = date.today()
    for invoice in invoices:
        # Check if overdue (you'll need to parse the date)
        print(f"Invoice {invoice['RefNumber']}: ${invoice['BalanceRemaining']}")
```

## Error Handling

```python
from qbdquery import QuickBooksClient, QBDConnectionError, QBDSessionError

client = QuickBooksClient()

try:
    with client.session():
        customers = client.query_customers()
except QBDConnectionError as e:
    print(f"Failed to connect to QuickBooks: {e}")
except QBDSessionError as e:
    print(f"Session error: {e}")
```

## License

MIT License