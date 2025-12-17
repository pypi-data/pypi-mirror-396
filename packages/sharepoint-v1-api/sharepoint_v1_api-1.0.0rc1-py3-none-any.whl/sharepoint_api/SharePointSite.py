"""
Provides a high-level ``SharePointSite`` object that encapsulates site-wide
metadata and offers convenience wrappers around common ``SharePointAPI``
operations such as retrieving lists, users, and groups.
"""

from __future__ import annotations
from datetime import datetime
from ._datetime_utils import parse_sharepoint_datetime

from typing import List, Optional
import locale

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imported only for type checking to avoid circular imports at runtime
    from .SharePointAPI import SharePointAPI
from .SharePointList import SharePointList
from .SharePointLists import SharePointLists
from .SharePointUser import SharePointUser
from .SharePointUserList import SharePointUserList


class SharePointSite:
    """
    High-level representation of a SharePoint site.

    Parameters
    ----------
    api : SharePointAPI
        The low-level client used for HTTP calls.
    site_id : str
        Identifier of the SharePoint site (e.g. ``"mySite"``).
    """

    def __init__(self, sp: "SharePointAPI", site_id: str):
        self.sp = sp
        self.site_id = site_id
        self._metadata: Optional[dict] = None

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------
    def _ensure_metadata(self) -> dict:
        """Fetch site metadata on first use and cache it."""
        if self._metadata is None:
            self._metadata = self.sp.get_site_metadata(self.site_id)
        return self._metadata

    # -----------------------------------------------------------------
    # Exposed properties (lazy-loaded)
    # -----------------------------------------------------------------
    @property
    def title(self) -> str:
        """Site title."""
        return self._ensure_metadata().get("Title", "")

    @property
    def url(self) -> str:
        """Absolute URL of the site."""
        return self._ensure_metadata().get("Url", "")

    @property
    def description(self) -> str:
        """Site description, if present."""
        return self._ensure_metadata().get("Description", "")

    @property
    def Created(self) -> datetime | None:
        """
        Creation date of the SharePoint site.

        Returns a ``datetime`` object parsed from the ``Created`` metadata
        field, or ``None`` if the field is missing or cannot be parsed.
        """
        created_str = self._ensure_metadata().get("Created")
        return parse_sharepoint_datetime(created_str, self.sp.timezone)

    @property
    def language_id(self) -> int:
        """Raw LCID value returned by SharePoint."""
        return self._ensure_metadata().get("Language", 0)

    @property
    def language_name(self) -> str:
        """
        Human-readable language name derived from the LCID using the
        ``locale`` module. If the LCID is unknown or the locale cannot be set,
        a fallback string is returned.
        """
        lcid = self.language_id
        locale_code = locale.windows_locale.get(lcid)
        if not locale_code:
            return f"Unknown (LCID={lcid})"
        try:
            # Attempt to set the locale; may fail if not installed.
            locale.setlocale(locale.LC_ALL, locale_code)
            # locale.getlocale() returns a tuple like ('en_US', 'UTF-8')
            loc = locale.getlocale()[0]
            if loc:
                # Return the locale identifier (e.g., 'en_US')
                return loc
        except locale.Error:
            # Locale not available on the system; fall back to the code.
            pass
        # Fallback to the raw locale code string.
        return locale_code

    # -----------------------------------------------------------------
    # Convenience wrappers around ``SharePointAPI`` methods
    # -----------------------------------------------------------------
    def get_lists(self) -> SharePointLists:
        """Return a ``SharePointLists`` collection for this site."""
        return self.sp.get_lists(self.site_id)

    def get_users(
        self,
        filters: Optional[str] = None,
        select_fields: Optional[List[str]] = None,
    ) -> SharePointUserList:
        """Retrieve users from the site."""
        return self.sp.get_users(self.site_id, filters=filters, select_fields=select_fields)

    def get_group_users(
        self,
        group_name: str,
        filters: Optional[str] = None,
        select_fields: Optional[List[str]] = None,
    ) -> SharePointUserList:
        """Retrieve members of a SharePoint group."""
        return self.sp.get_group_users(
            self.site_id, group_name, filters=filters, select_fields=select_fields
        )

    def get_user(
        self,
        user_id: int,
        select_fields: Optional[List[str]] = None,
    ) -> SharePointUser:
        """Retrieve a single user by ID."""
        return self.sp.get_user(self.site_id, user_id, select_fields=select_fields)

    def get_list(
        self,
        sp_list,
        filters=None,
        top: int = 1000,
        view_path=None,
        select_fields=None,
        SPListType: SharePointList = SharePointList,
    ) -> SharePointList:
        """Delegate to ``SharePointAPI.get_list`` for this site."""
        return self.sp.get_list(
            self.site_id,
            sp_list,
            filters,
            top,
            view_path,
            select_fields,
            SPListType=SPListType,
        )

    def get_list_by_name(
        self,
        sp_list_name: str,
        filters=None,
        top: int = 1000,
        view_path=None,
        select_fields=None,
        SPListType: SharePointList = SharePointList,
    ) -> SharePointList:
        """Delegate to ``SharePointAPI.get_list_by_name`` for this site."""
        return self.sp.get_list_by_name(
            self.site_id,
            sp_list_name,
            filters,
            top,
            view_path,
            select_fields,
            SPListType=SPListType,
        )
