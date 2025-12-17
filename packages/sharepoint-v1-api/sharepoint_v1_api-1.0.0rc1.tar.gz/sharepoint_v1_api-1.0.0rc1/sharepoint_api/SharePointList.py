# from .SharePointAPI import SharePointAPI as SP
from sharepoint_api.SharePointTimeRegistration import TimeRegistration
from .SharePointListItem import SharePointListItem, SharepointSiteCase
from typing import List
import json


class SharePointList:
    """
    Base class representing a SharePoint list.

    Provides common functionality for handling list items, including
    retrieval, addition, and serialization to JSON. Subclasses such as
    :class:`CasesList` and :class:`TimeRegistrationList` extend this
    class with domain-specific behavior.
    """

    settings = None
    _items = None
    _fields = None
    sharepoint_site = None
    SPItem = SharePointListItem

    CHANGE_DETECTED = False
    SAVE_ON_CHANGE = False
    JSON_FILENAME = None

    def __init__(self, sp, sharepoint_site, settings: dict = None, items: List[SPItem] = None):
        self.sp = sp
        self.sharepoint_site = sharepoint_site
        self.settings = settings
        self.append_items(items)

    def __str__(self):
        items = ''
        for _, _item in self.all_items.items():
            items = items+str(_item.Title)+'\n'
        return items

    def __del__(self):
        if self.CHANGE_DETECTED and self.SAVE_ON_CHANGE and self.JSON_FILENAME is not None:
            print('Change was definiteley detected')
            print('Saving items')
            self.save_as_json(self.JSON_FILENAME)

    @property
    def all_items(self) -> dict[int, SPItem]:
        '''
            Get list of all SharePointListItem objects
        '''
        if self._items is None:
            self._items = {}
        return self._items

    @property
    def list_all_items(self) -> List[SPItem]:
        '''
            Get list of all SharePointListItem objects
        '''
        if self._items is None:
            self._items = {}
        return list(self._items.values())

    @property
    def Title(self) -> str:
        return self.settings['Title']

    @property
    def guid(self):
        return self.settings['Id']

    def append_items(self, items):
        """
        Append a collection of items to the list.

        Parameters
        ----------
        items : list or SharePointListItem
            A list of :class:`SharePointListItem` instances or a single
            instance to be added to the internal ``_items`` dictionary.
        """
        if self._items is None:
            self._items = {}

        if isinstance(items, list):
            for item in items:
                item._list = self
                self._items[item.Id] = item

        elif isinstance(items, self.SPItem):
            items._list = self
            self.all_items[items.Id] = items

    def create_item(self, data):
        self.sp.create_item(self.sharepoint_site, self, data)

    def get_item_by_name(self, name):
        """
        Retrieve items from the list that match a given title.

        Parameters
        ----------
        name : str
            The title of the item to search for.

        Returns
        -------
        dict[int, SharePointListItem]
            A dictionary of matching items keyed by their IDs.
        """
        '''
        '''
        items = {}
        for item_id, item in self._items.items():
            if name == item.Title:
                items[item_id] = item
        return items

    def get_item_by_id(self, id):
        '''
        '''
        if id in self._items:
            return self._items[id]
        else:
            return None

    @property
    def fields(self) -> dict:
        """
        Retrieve all fields from the SharePoint list.

        Returns:
            dict: Field definitions keyed by Title, cached for subsequent calls

        Raises:
            ConnectionError: If API request fails
        """
        if not self._fields:
            try:
                response = self.sp._api_get_call(
                    f"{self.sp.sharepoint_url}/cases/{self.sharepoint_site}/_api/Web/Lists(guid'{self.guid}')/Fields"
                )
                response.raise_for_status()
                self._fields = {field["Title"]: field for field in response.json().get(
                    'd', {}).get('results', [])}
            except Exception as e:
                print(f"Failed to fetch fields: {str(e)}")
                raise ConnectionError("Field retrieval failed") from e
        return self._fields

    def get_items_by_assigned_id(self, id) -> List[SPItem]:
        '''
        '''
        items = {}
        for item_id, item in self._items.items():
            if id == item.ResponsibleId:
                items[item_id] = item
        return items

    def save_as_json(self, file_name):
        """
        Serialize the list to a JSON file.

        Parameters
        ----------
        file_name : str
            Path to the output JSON file.

        The resulting JSON contains the SharePoint site identifier, the list GUID,
        settings, and all case items with their settings and version information.
        """

        out_dict = {
            'sharepoint_site': self.sharepoint_site,
            'GUID': self.guid,
            'Settings': self.settings,
            "cases": [{'settings': case.settings, 'versions': case._versions} for _, case in self.all_items.items()]
        }

        with open(file_name, 'w') as fp:
            json.dump(out_dict, fp)


class CasesList(SharePointList):
    """
    Specialized list representing a collection of case items.

    Inherits all functionality from :class:`SharePointList` and sets the
    ``SPItem`` attribute to :class:`SharepointSiteCase` for proper item
    instantiation.
    """
    SPItem = SharepointSiteCase


class TimeRegistrationList(SharePointList):
    """
    Specialized list for time-registration entries.

    Inherits from :class:`SharePointList` and sets ``SPItem`` to the
    :class:`TimeRegistration` class.
    """
    SPItem = TimeRegistration
