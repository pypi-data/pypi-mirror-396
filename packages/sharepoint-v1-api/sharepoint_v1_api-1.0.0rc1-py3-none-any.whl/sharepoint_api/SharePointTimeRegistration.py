from datetime import datetime
from ._datetime_utils import parse_sharepoint_datetime

from sharepoint_api.SharePointListItem import SharePointListItem
# from .SharePointAPI import SharePointAPI as SP


class TimeRegistration(SharePointListItem):
    """
    Represents a time-registration entry associated with a SharePoint list item.

    Extends :class:`SharePointListItem` with fields specific to time tracking,
    such as ``Hours``, ``DoneBy`` and related timestamps. Provides lazy loading of the
    ``DoneBy`` user via the :meth:`SharePointAPI.get_users` call.
    """

    _DoneBy = None

    from ._datetime_utils import parse_sharepoint_datetime

    @property
    def Created(self) -> datetime | None:
        """Timestamp of when the item was created."""
        return parse_sharepoint_datetime(self.settings.get('DoneDate'), self.sp.timezone)

    @property
    def Hours(self) -> str:
        return self.settings['Hours']

    @property
    def DoneById(self) -> str:
        return self.settings['DoneById']

    @property
    def DoneBy(self) -> str:
        if not self._DoneBy:
            user_list = self.sp.get_users(self.sharepoint_site)
            self._DoneBy = user_list.get_user_by_id(self.DoneById)
        return self._DoneBy

    @property
    def DoneUsername(self) -> str:
        return self.DoneBy.UserName

    @property
    def CaseId(self) -> str:
        return self.settings['CaseId']

    @property
    def WorkPackageId(self) -> str:
        return self.settings['WorkPackageId']
