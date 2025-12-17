from pyluga.api.base import BelugaAPI
from pyluga.exceptions import BadRequestError
from pyluga.responses import PaginatedResponse


class Locations(BelugaAPI):
    """Class for interacting with the Beluga Locations API."""

    def list_locations(self, includes=None, params=None):
        """List all locations.

        Args:
            includes(iter): List of includes, e.g. ('nodes', 'servers')
            params(dict): Extra parameters to pass, e.g. {'per_page': 300}
        """
        endpoint = 'application/locations'
        response = self._api_request(endpoint=endpoint, includes=includes,
                                     params=params)
        return PaginatedResponse(self, endpoint, response)

    def get_location_info(self, location_id, includes=None, params=None):
        """Get detailed info for the specified location.

        Args:
            location_id(int): Beluga Location ID.
            includes(iter): List of includes, e.g. ('nodes', 'servers')
            params(dict): Extra parameters to pass, e.g. {'per_page': 300}
        """
        response = self._api_request(
            endpoint='application/locations/{}'.format(location_id),
            includes=includes, params=params)
        return response

    def create_location(self, shortcode, description):
        """Creates a new location.

        Args:
            shortcode(str): Short identifier between 1 and 60 characters, e.g. us.nyc.lvl3
            description(str): A long description of the location.  Max 255 characters.
        """
        data = {'shortcode': shortcode, 'description': description}
        response = self._api_request(endpoint='application/locations',
                                     mode='POST', data=data)
        return response

    def edit_location(self, location_id, shortcode=None, description=None):
        """Modify an existing location.

        Args:
            location_id(int): Beluga Location ID.
            shortcode(str): Short identifier between 1 and 60 characters, e.g. us.nyc.lvl3
            description(str): A long description of the location.  Max 255 characters.
        """
        if not shortcode and not description:
            raise BadRequestError(
                'Must specify either shortcode or description for edit_location.')

        data = {}
        if shortcode:
            data['shortcode'] = shortcode
        if description:
            data['description'] = description

        response = self._api_request(
            endpoint='application/locations/{}'.format(location_id),
            mode='PATCH', data=data)
        return response

    def delete_location(self, location_id):
        """Delete an existing location.

        Args:
            location_id(int): Beluga Location ID.
        """
        response = self._api_request(
            endpoint='application/locations/{}'.format(location_id),
            mode='DELETE')
        return response
