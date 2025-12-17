# SharePoint API Python Client – Documentation

This repository provides a lightweight Python client for interacting with SharePoint sites via SharePoint's REST API. The library handles NTLM authentication, list operations, file management, and time registration while abstracting SharePoint-specific implementation details.

## Dependencies

- Python ≥3.9
- requests ≥2.32.2
- requests-ntlm ≥1.3.0

## Installation

```bash
pip install sharepoint-api
```

Or install from source:

```bash
git clone https://github.com/your-org/nc-devops-sharepoint-v1-api.git
cd nc-devops-sharepoint-v1-api
pip install -e .
```

## Authentication & Initialization

The client uses NTLM authentication via `requests-ntlm`. Choose between two initialization methods:

### Quick Initialization

```python
from sharepoint_api.SharePointAPI import SharePointAPI

creds = {
    "username": "your_user",
    "password": "your_password",
    "sharepoint_url": "https://your.sharepoint.com",
    "proxies": {}
}

# Recommended compact initialization (bypasses normal constructor)
sp: SharePointAPI = SharePointAPI._compact_init(creds)
```

### Full Initialization

```python
from requests_ntlm import HttpNtlmAuth
from sharepoint_api.SharePointAPI import SharePointAPI

sp = SharePointAPI(
    sharepoint_url="https://your.sharepoint.com",
    auth=HttpNtlmAuth("your_user", "your_password"),
    proxies={}
)
```

## Core Operations

### List Operations

```python
from sharepoint_api.SharePointList import SharePointList

# Get all lists in a site
site = "YOUR_SITE"
lists: list[SharePointList] = sp.get_lists(site)

# Access specific list
cases: SharePointList = sp.get_list_by_name(site, "Sager")
print(cases.Title)

# Filter items with CAML queries
filters = ' and '.join([
    "(TeamId == '3')",
    "(Status == '11 - Modtaget')",
    "((Status != '90 - Lukket') and (Status != '91 - Afvist'))"
])
filtered_items = sp.get_list_by_name(site, "Sager", filters).all_items
```

### File Operations

```python
from sharepoint_api.SharePointList import SharePointListItem

# Upload file
item: SharePointListItem = sp.upload_file(
    site="cases",
    folder="Documents",
    file_name="report.pdf",
    file_path="/local/path/report.pdf"
)

# Download file
sp.download_file(
    site="cases",
    file_url=item.FileRef,
    download_path="./downloads/report.pdf"
)

# Copy file
copy_result = sp.copy_file(
    site="cases",
    source_url=item.FileRef,
    target_folder="Archive",
    new_name="report_2023.pdf"
)

# Delete file
sp.delete_file(site="cases", file_url=item.FileRef)
```

### Folder Management

```python
# Check folder existence
if not sp.folder_exists(site="cases", folder_path="Documents/Archived"):
    sp.create_new_folder(site="cases", folder_path="Documents/Archived")
```

### Time Registration

```python
time_list = sp.get_time_registration_list_by_name(site="HR", list_name="TimeRegistrations")
entries = time_list.get_items(select=["Title", "Hours", "Date"])
for entry in entries:
    print(f"{entry.Date}: {entry.Hours} hours - {entry.Title}")
```

### Extended Operations

#### User Management

```python
# Get all users in a group
group_users = sp.get_group_users("hr-site", "Project Managers")

# Get user by ID
user = sp.get_user("cases", user_id=42)
```

#### Site Metadata

```python
# Get site details
site_metadata = sp.get_site_metadata("cases", select_fields=["Title", "Url"])

# Get full site object
site = sp.get_site("cases")
print(f"Site URL: {site.url}")
```

#### Version History

```python
contract_item = sp.get_list_by_name(site="Legal", list_name="Contracts").get_item_by_id(42)
versions = sp.get_item_versions(contract_item)
print(f"Item has {len(versions)} versions:")
for v in versions:
    print(f"Version {v.VersionLabel} by {v.CreatedBy}")
```

### Additional Classes

- `SharePointUser`: Represents a SharePoint user with properties
- `SharePointUserList`: Collection of users with filtering capabilities
- `SharePointSite`: High-level site management object
- `SharePointListItem`: Detailed item representation with version history
- `SharePointLists`: Container for multiple SharePointList objects

#### SharePointUser Example

```python
user = sp.get_user("cases", 42)
print(f"{user.Title} ({user.Email}) - Member since {user.Created}")
```

#### SharePointSite Example

```python
site = sp.get_site("cases")
print(f"Site URL: {site.url}")
print(f"Storage used: {site.storage_used}/{site.storage_max} MB")
```

#### SharePointListItem Example

```python
item = sp.get_list_by_name("cases", "Tasks").get_item_by_id(101)
print(f"Task '{item.Title}' versions: {len(item.versions)}")
```

- `SharePointUser`: Represents a user with properties/methods for group membership
- `SharePointUserList`: User collection with filtering/sorting
- `SharePointSite`: Site management with metadata/properties
- `SharePointListItem`: Item with version history and field access
- `SharePointLists`: Container for list operations
- `_datetime_utils`: Timezone-aware datetime conversions (internal)

### Future Changes

- Version 0.3.0:
  - Remove `_compact_init` in favor of session-based initialization
