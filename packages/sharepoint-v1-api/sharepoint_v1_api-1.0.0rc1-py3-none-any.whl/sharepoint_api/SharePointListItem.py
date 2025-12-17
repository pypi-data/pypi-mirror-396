from datetime import datetime
from ._datetime_utils import parse_sharepoint_datetime
# from .SharePointAPI import SharePointAPI as SP


class SharePointListItem:
    """
    Represents a generic item in a SharePoint list.

    Provides access to common fields such as ``Id``, ``Title``, ``Created`` and
    ``Modified`` and handles lazy loading of related list data and version
    history. Sub-classes (e.g. :class:`SharepointSiteCase` or
    :class:`TimeRegistration`) extend this base with domain-specific properties.
    """
    ''' 
    '''
    settings = {}

    def __init__(self, sp, sharepoint_site, settings: dict = None, versions: list = None):
        self.sp = sp
        self.sharepoint_site = sharepoint_site
        self._list = None
        self._list_guid = None
        self._versions = versions
        self.settings = settings

    def __str__(self):
        return self.Title

    @property
    def list_guid(self):
        if not self._list_guid:
            import re

            parent_list_url = self.settings.get(
                'ParentList', {}).get('__deferred', {}).get('uri')
            match = re.search(
                r"guid'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'", parent_list_url)

            self._list_guid = match.group(1) if match else None
        return self._list_guid

    @property
    def list(self):
        if not self._list:
            self._list = self.sp.get_list(self.sharepoint_site, self.list_guid)
        return self._list

    @property
    def versions(self) -> list:
        if not self._versions:
            self._versions = self.sp.get_item_versions(
                self.sharepoint_site, self.list_guid, self.Id)
            if self._list is not None:
                self._list.CHANGE_DETECTED = True
        return self._versions

    @property
    def Id(self) -> str:
        """Unique identifier of the list item."""
        return self.settings['Id']

    @property
    def Title(self) -> str:
        """Title of the list item."""
        return self.settings['Title']

    @property
    def Created(self) -> datetime | None:
        """
        Timestamp of when the item was created.

        Returns ``None`` if the ``Created`` field is missing or null.
        """
        return parse_sharepoint_datetime(self.settings.get('Created'), self.sp.timezone)

    @property
    def Modified(self) -> datetime | None:
        """
        Timestamp of when the item was modified.

        Returns ``None`` if the ``Modified`` field is missing or null.
        """
        return parse_sharepoint_datetime(self.settings.get('Modified'), self.sp.timezone)

    def attach_item(self, file_name, file_path):
        """
        Attach a file to this list item.

        Parameters
        ----------
        file_name : str
            The name of the file as it should appear in SharePoint.
        file_path : str
            Local path to the file to be uploaded.

        The method reads the file content and uses :meth:`SharePointAPI.attach_file`
        to upload it to the corresponding SharePoint list item.
        """
        with open(file_path, 'r') as f:
            file_content = f.read()

        self.sp.attach_file(self.sharepoint_site, self.list,
                            self, file_name, file_content)

    def versions_select_fields(self, select_fields=[]) -> list:
        if not self._versions:
            self._versions = self.sp.get_item_versions(
                self.sharepoint_site, self.list_guid, self.Id, select_fields)
        return self._versions

    def update_fields(self, data):
        self.sp.update_item(self.sharepoint_site,
                            self.list_guid, self.Id, data)


class SharepointSiteCase(SharePointListItem):

    @property
    def AssignmentType(self) -> str:
        return self.settings['AssignmentType']

    @property
    def CaseClosedTimestamp(self) -> datetime | None:
        'Timestamp of when the case was closed'
        return parse_sharepoint_datetime(self.settings.get('CaseClosed'), self.sp.timezone)

    @property
    def Due(self) -> datetime | None:
        'Timestamp of when the case is due'
        return parse_sharepoint_datetime(self.settings.get('DueDate'), self.sp.timezone)

    @property
    def Priority(self) -> str:
        return self.settings['Priority']

    @property
    def ResponsibleId(self) -> str:
        return self.settings['AssignedToId']

    @property
    def Status(self) -> str:
        return self.settings['Status']

    @property
    def SolvedInTime(self) -> bool:
        'Bool indicating whether work was solved in time'
        solved_in_time = False
        if self.Due:
            if not self.CaseClosedTimestamp:
                solved_in_time = True
            elif self.CaseClosedTimestamp <= self.Due:
                solved_in_time = True
        else:
            solved_in_time = True

        return solved_in_time

    @property
    def WorkBegunTimestamp(self) -> datetime | None:
        'Timestamp of when work was started on the case'
        return parse_sharepoint_datetime(self.settings.get('WorkBegun'), self.sp.timezone)

    @property
    def DeadlineWorkTimestamp(self) -> datetime | None:
        'Timestamp of when work should start on the case'
        return parse_sharepoint_datetime(self.settings.get('DeadlineWork'), self.sp.timezone)

    @property
    def ReactedInTime(self) -> bool:
        'Bool indicating whether work was started in time'
        reacted_in_time = False
        if self.DeadlineWorkTimestamp:
            if not self.WorkBegunTimestamp:
                reacted_in_time = True
            elif self.WorkBegunTimestamp <= self.DeadlineWorkTimestamp:
                reacted_in_time = True
        else:
            reacted_in_time = True
        return reacted_in_time
