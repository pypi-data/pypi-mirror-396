"""sharepoint_api package

Provides a high-level Python client for interacting with SharePoint sites via the
`SharePointAPI` class. The package includes helpers for working with lists,
list items, users, and time registrations.

Typical usage:

```python
from sharepoint_api import SharePointAPI

creds = {
    "username": "my_user",
    "password": "my_pass",
    "sharepoint_url": "https://my.sharepoint.com"
}
api = SharePointAPI._compact_init(creds)
```
"""

from .SharePointAPI import SharePointAPI
from .SharePointSite import SharePointSite
