import json

import earthdaily.earthone as eo
import geojson
import requests
from shapely import Geometry
from shapely.geometry import shape
from shapely.ops import unary_union

from .operations import API_HOST, UnauthorizedUserError

FENCE_TABLE = "earthdaily:org-geofencing"


class GeoFencing:
    """A class for interacting with an org's geofence."""

    def __init__(self):
        self.org = eo.auth.Auth.get_default_auth().payload["org"]

        self.fence_table = eo.vector.Table.get(
            product_id=FENCE_TABLE,
            property_filter=eo.utils.Properties().orgname == self.org,
        ).collect()

    def check_fence(self) -> bool:
        return self.fence_table.shape[0] > 0

    def check_cached_fence(self) -> bool:
        response = requests.get(
            f"{API_HOST}/cache/orgfuncs/geofencing/{self.org}",
            headers={"Authorization": eo.auth.Auth.get_default_auth().token},
        )
        return response.content is not "".encode()

    def cache_fence(self):
        if not self.check_fence() and not self.check_cached_fence():
            return

        merged_geometry = unary_union([geom for geom in self.fence_table["geometry"]])
        as_bytes = json.dumps(merged_geometry.__geo_interface__).encode()
        # check the fence table against the current cache
        if self.check_cached_fence():
            cached_fence = self.get_cached_fence()
            if merged_geometry.equals(cached_fence):
                return

        files = {"fence": ("geofence.json", as_bytes, "application/json")}
        response = requests.post(
            f"{API_HOST}/cache/orgfuncs/geofencing/{self.org}",
            headers={"Authorization": eo.auth.Auth.get_default_auth().token},
            files=files,
        )
        try:
            response.raise_for_status()
        except Exception as e:
            if e.response.status_code == 403:
                raise UnauthorizedUserError(
                    "User does not have access to dynamic-compute. "
                    "If you believe this to be an error, contact support@earthdaily.com"
                )
            else:
                raise e

    def get_cached_fence(self) -> Geometry:
        response = requests.get(
            f"{API_HOST}/cache/orgfuncs/geofencing/{self.org}",
            headers={"Authorization": eo.auth.Auth.get_default_auth().token},
        )
        if response.content is not "".encode():
            fence_gj = json.loads(response.content.decode())
            return shape(fence_gj)
        else:
            return shape(geojson.GeometryCollection())
