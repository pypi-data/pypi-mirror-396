from typing import Dict, List, Any, Union

from trinity_connect_client.decorators import handle_exceptions
from trinity_connect_client.mixins import ResourceMixin
from trinity_connect_client.validators import validate_id


class OrgsAPI(ResourceMixin):
    @handle_exceptions
    def get(self, company_id: int) -> Dict[str, Any]:
        """
        GET a company by ID.

        :param company_id: The ID of the company to retrieve
        :return: A Company object as dictionary or error response
        """
        validate_id(company_id)
        url = self._url(f"orgs/company/{company_id}/")
        return self.make_get_request(url)

    @handle_exceptions
    def get_folders(
        self, company_id: int, **filters
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        GET company folders for a given company ID.

        :param company_id: The ID of the company whose folders to retrieve
        :param filters: Optional filters to apply to the request
        :return: List of folder objects as dictionaries or error response
        """
        validate_id(company_id)
        url = self._url(f"orgs/folders/company/{company_id}/")
        return self.make_get_request(url, params=filters)

    @handle_exceptions
    def get_folder(
        self, folder_id: int, **filters
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        GET folder for a given folder ID.

        :param folder_id: The ID of the folder to retrieve
        :param filters: Optional filters to apply to the request
        :return: List of folder objects as dictionaries or error response
        """
        validate_id(folder_id)
        url = self._url(f"orgs/folder/{folder_id}/")
        return self.make_get_request(url, params=filters)
