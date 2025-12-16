from typing import Any, Optional, List, Callable, Awaitable
from typing_extensions import TypedDict
from thunkmetrc.client import MetrcClient
from .ratelimiter import MetrcRateLimiter, RateLimiterConfig

class MetrcWrapper:
    def __init__(self, client: MetrcClient, config: Optional[RateLimiterConfig] = None):
        self.client = client
        self.limiter = MetrcRateLimiter(config)

    async def locations_create_v1(self, body: Optional['List[LocationsCreateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        POST Create V1
        """
        async def op():
            return await self.client.locations_create_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def locations_create_v2(self, body: Optional['List[LocationsCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        POST Create V2
        """
        async def op():
            return await self.client.locations_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def locations_create_update_v1(self, body: Optional['List[LocationsCreateUpdateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        POST CreateUpdate V1
        """
        async def op():
            return await self.client.locations_create_update_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def locations_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        DELETE Delete V1
        """
        async def op():
            return await self.client.locations_delete_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def locations_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a specified Location, identified by its Id, for a Facility.
        
          Permissions Required:
          - Manage Locations

        DELETE Delete V2
        """
        async def op():
            return await self.client.locations_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def locations_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        GET Get V1
        """
        async def op():
            return await self.client.locations_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def locations_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Location by its Id.
        
          Permissions Required:
          - Manage Locations

        GET Get V2
        """
        async def op():
            return await self.client.locations_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def locations_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        GET GetActive V1
        """
        async def op():
            return await self.client.locations_get_active_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def locations_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetActive V2
        """
        async def op():
            return await self.client.locations_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def locations_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetInactive V2
        """
        async def op():
            return await self.client.locations_get_inactive_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def locations_get_types_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Locations

        GET GetTypes V1
        """
        async def op():
            return await self.client.locations_get_types_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def locations_get_types_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active location types for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetTypes V2
        """
        async def op():
            return await self.client.locations_get_types_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def locations_update_v2(self, body: Optional['List[LocationsUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing locations for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        PUT Update V2
        """
        async def op():
            return await self.client.locations_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sandbox_create_integrator_setup_v2(self, body: Any = None, user_key: Optional[str] = None) -> Any:
        """
        This endpoint is used to handle the setup of an external integrator for sandbox environments. It processes a request to create a new sandbox user for integration based on an external source's API key. It checks whether the API key is valid, manages the user creation process, and returns an appropriate status based on the current state of the request.
        
          Permissions Required:
          - None

        POST CreateIntegratorSetup V2
        """
        async def op():
            return await self.client.sandbox_create_integrator_setup_v2(body=body, user_key=user_key)
        return await self.limiter.execute(None, False, op)

    async def sublocations_create_v2(self, body: Optional['List[SublocationsCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new sublocation records for a Facility.
        
          Permissions Required:
          - Manage Locations

        POST Create V2
        """
        async def op():
            return await self.client.sublocations_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sublocations_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives an existing Sublocation record for a Facility.
        
          Permissions Required:
          - Manage Locations

        DELETE Delete V2
        """
        async def op():
            return await self.client.sublocations_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sublocations_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Sublocation by its Id, with an optional license number.
        
          Permissions Required:
          - Manage Locations

        GET Get V2
        """
        async def op():
            return await self.client.sublocations_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sublocations_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active sublocations for the current Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Locations

        GET GetActive V2
        """
        async def op():
            return await self.client.sublocations_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def sublocations_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive sublocations for the specified Facility.
        
          Permissions Required:
          - Manage Locations

        GET GetInactive V2
        """
        async def op():
            return await self.client.sublocations_get_inactive_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def sublocations_update_v2(self, body: Optional['List[SublocationsUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing sublocation records for a specified Facility.
        
          Permissions Required:
          - Manage Locations

        PUT Update V2
        """
        async def op():
            return await self.client.sublocations_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transporters_create_driver_v2(self, body: Optional['List[TransportersCreateDriverV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new driver records for a Facility.
        
          Permissions Required:
          - Manage Transporters

        POST CreateDriver V2
        """
        async def op():
            return await self.client.transporters_create_driver_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transporters_create_vehicle_v2(self, body: Optional['List[TransportersCreateVehicleV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new vehicle records for a Facility.
        
          Permissions Required:
          - Manage Transporters

        POST CreateVehicle V2
        """
        async def op():
            return await self.client.transporters_create_vehicle_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transporters_delete_driver_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Driver record for a Facility.  Please note: The {id} parameter above represents a Driver Id.
        
          Permissions Required:
          - Manage Transporters

        DELETE DeleteDriver V2
        """
        async def op():
            return await self.client.transporters_delete_driver_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transporters_delete_vehicle_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Vehicle for a facility.  Please note: The {id} parameter above represents a Vehicle Id.
        
          Permissions Required:
          - Manage Transporters

        DELETE DeleteVehicle V2
        """
        async def op():
            return await self.client.transporters_delete_vehicle_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transporters_get_driver_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Driver by its Id, with an optional license number. Please note: The {id} parameter above represents a Driver Id.
        
          Permissions Required:
          - Transporters

        GET GetDriver V2
        """
        async def op():
            return await self.client.transporters_get_driver_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transporters_get_drivers_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of drivers for a Facility.
        
          Permissions Required:
          - Transporters

        GET GetDrivers V2
        """
        async def op():
            return await self.client.transporters_get_drivers_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transporters_get_vehicle_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Vehicle by its Id, with an optional license number. Please note: The {id} parameter above represents a Vehicle Id.
        
          Permissions Required:
          - Transporters

        GET GetVehicle V2
        """
        async def op():
            return await self.client.transporters_get_vehicle_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transporters_get_vehicles_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of vehicles for a Facility.
        
          Permissions Required:
          - Transporters

        GET GetVehicles V2
        """
        async def op():
            return await self.client.transporters_get_vehicles_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transporters_update_driver_v2(self, body: Optional['List[TransportersUpdateDriverV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing driver records for a Facility.
        
          Permissions Required:
          - Manage Transporters

        PUT UpdateDriver V2
        """
        async def op():
            return await self.client.transporters_update_driver_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transporters_update_vehicle_v2(self, body: Optional['List[TransportersUpdateVehicleV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing vehicle records for a facility.
        
          Permissions Required:
          - Manage Transporters

        PUT UpdateVehicle V2
        """
        async def op():
            return await self.client.transporters_update_vehicle_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_v1(self, body: Optional['List[ItemsCreateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        NOTE: To include a photo with an item, first use POST /items/v1/photo to POST the photo, and then use the returned ID in the request body in this endpoint.
        
          Permissions Required:
          - Manage Items

        POST Create V1
        """
        async def op():
            return await self.client.items_create_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_v2(self, body: Optional['List[ItemsCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates one or more new products for the specified Facility. NOTE: To include a photo with an item, first use POST /items/v2/photo to POST the photo, and then use the returned Id in the request body in this endpoint.
        
          Permissions Required:
          - Manage Items

        POST Create V2
        """
        async def op():
            return await self.client.items_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_brand_v2(self, body: Optional['List[ItemsCreateBrandV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates one or more new item brands for the specified Facility identified by the License Number.
        
          Permissions Required:
          - Manage Items

        POST CreateBrand V2
        """
        async def op():
            return await self.client.items_create_brand_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_file_v2(self, body: Optional['List[ItemsCreateFileV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Uploads one or more image or PDF files for products, labels, packaging, or documents at the specified Facility.
        
          Permissions Required:
          - Manage Items

        POST CreateFile V2
        """
        async def op():
            return await self.client.items_create_file_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_photo_v1(self, body: Optional['List[ItemsCreatePhotoV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        This endpoint allows only BMP, GIF, JPG, and PNG files and uploaded files can be no more than 5 MB in size.
        
          Permissions Required:
          - Manage Items

        POST CreatePhoto V1
        """
        async def op():
            return await self.client.items_create_photo_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_photo_v2(self, body: Optional['List[ItemsCreatePhotoV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        This endpoint allows only BMP, GIF, JPG, and PNG files and uploaded files can be no more than 5 MB in size.
        
          Permissions Required:
          - Manage Items

        POST CreatePhoto V2
        """
        async def op():
            return await self.client.items_create_photo_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_create_update_v1(self, body: Optional['List[ItemsCreateUpdateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        POST CreateUpdate V1
        """
        async def op():
            return await self.client.items_create_update_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        DELETE Delete V1
        """
        async def op():
            return await self.client.items_delete_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives the specified Product by Id for the given Facility License Number.
        
          Permissions Required:
          - Manage Items

        DELETE Delete V2
        """
        async def op():
            return await self.client.items_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_delete_brand_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives the specified Item Brand by Id for the given Facility License Number.
        
          Permissions Required:
          - Manage Items

        DELETE DeleteBrand V2
        """
        async def op():
            return await self.client.items_delete_brand_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET Get V1
        """
        async def op():
            return await self.client.items_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves detailed information about a specific Item by Id.
        
          Permissions Required:
          - Manage Items

        GET Get V2
        """
        async def op():
            return await self.client.items_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetActive V1
        """
        async def op():
            return await self.client.items_get_active_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of active items for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetActive V2
        """
        async def op():
            return await self.client.items_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def items_get_brands_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetBrands V1
        """
        async def op():
            return await self.client.items_get_brands_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_brands_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active item brands for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetBrands V2
        """
        async def op():
            return await self.client.items_get_brands_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def items_get_categories_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetCategories V1
        """
        async def op():
            return await self.client.items_get_categories_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_categories_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of item categories.
        
          Permissions Required:
          - None

        GET GetCategories V2
        """
        async def op():
            return await self.client.items_get_categories_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def items_get_file_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a file by its Id for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetFile V2
        """
        async def op():
            return await self.client.items_get_file_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_inactive_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetInactive V1
        """
        async def op():
            return await self.client.items_get_inactive_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive items for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetInactive V2
        """
        async def op():
            return await self.client.items_get_inactive_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def items_get_photo_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Items

        GET GetPhoto V1
        """
        async def op():
            return await self.client.items_get_photo_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_get_photo_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves an image by its Id for the specified Facility.
        
          Permissions Required:
          - Manage Items

        GET GetPhoto V2
        """
        async def op():
            return await self.client.items_get_photo_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def items_update_v2(self, body: Optional['List[ItemsUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates one or more existing products for the specified Facility.
        
          Permissions Required:
          - Manage Items

        PUT Update V2
        """
        async def op():
            return await self.client.items_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def items_update_brand_v2(self, body: Optional['List[ItemsUpdateBrandV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates one or more existing item brands for the specified Facility.
        
          Permissions Required:
          - Manage Items

        PUT UpdateBrand V2
        """
        async def op():
            return await self.client.items_update_brand_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_v1(self, body: Optional['List[PackagesCreateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST Create V1
        """
        async def op():
            return await self.client.packages_create_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_v2(self, body: Optional['List[PackagesCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new packages for a specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST Create V2
        """
        async def op():
            return await self.client.packages_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_adjust_v1(self, body: Optional['List[PackagesCreateAdjustV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateAdjust V1
        """
        async def op():
            return await self.client.packages_create_adjust_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_adjust_v2(self, body: Optional['List[PackagesCreateAdjustV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records a list of adjustments for packages at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateAdjust V2
        """
        async def op():
            return await self.client.packages_create_adjust_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_change_item_v1(self, body: Optional['List[PackagesCreateChangeItemV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateChangeItem V1
        """
        async def op():
            return await self.client.packages_create_change_item_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_change_location_v1(self, body: Optional['List[PackagesCreateChangeLocationV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateChangeLocation V1
        """
        async def op():
            return await self.client.packages_create_change_location_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_finish_v1(self, body: Optional['List[PackagesCreateFinishV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateFinish V1
        """
        async def op():
            return await self.client.packages_create_finish_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_plantings_v1(self, body: Optional['List[PackagesCreatePlantingsV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants
          - View Packages
          - Manage Packages Inventory

        POST CreatePlantings V1
        """
        async def op():
            return await self.client.packages_create_plantings_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_plantings_v2(self, body: Optional['List[PackagesCreatePlantingsV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new plantings from packages for a specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants
          - View Packages
          - Manage Packages Inventory

        POST CreatePlantings V2
        """
        async def op():
            return await self.client.packages_create_plantings_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_remediate_v1(self, body: Optional['List[PackagesCreateRemediateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateRemediate V1
        """
        async def op():
            return await self.client.packages_create_remediate_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_testing_v1(self, body: Optional['List[PackagesCreateTestingV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateTesting V1
        """
        async def op():
            return await self.client.packages_create_testing_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_testing_v2(self, body: Optional['List[PackagesCreateTestingV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new packages for testing for a specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreateTesting V2
        """
        async def op():
            return await self.client.packages_create_testing_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_create_unfinish_v1(self, body: Optional['List[PackagesCreateUnfinishV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateUnfinish V1
        """
        async def op():
            return await self.client.packages_create_unfinish_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Discontinues a Package at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        DELETE Delete V2
        """
        async def op():
            return await self.client.packages_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET Get V1
        """
        async def op():
            return await self.client.packages_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Package by its Id.
        
          Permissions Required:
          - View Packages

        GET Get V2
        """
        async def op():
            return await self.client.packages_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetActive V1
        """
        async def op():
            return await self.client.packages_get_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active packages for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetActive V2
        """
        async def op():
            return await self.client.packages_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_adjust_reasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetAdjustReasons V1
        """
        async def op():
            return await self.client.packages_get_adjust_reasons_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_adjust_reasons_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of adjustment reasons for packages at a specified Facility.
        
          Permissions Required:
          - None

        GET GetAdjustReasons V2
        """
        async def op():
            return await self.client.packages_get_adjust_reasons_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_by_label_v1(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetByLabel V1
        """
        async def op():
            return await self.client.packages_get_by_label_v1(label, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_by_label_v2(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Package by its label.
        
          Permissions Required:
          - View Packages

        GET GetByLabel V2
        """
        async def op():
            return await self.client.packages_get_by_label_v2(label, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetInactive V1
        """
        async def op():
            return await self.client.packages_get_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive packages for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetInactive V2
        """
        async def op():
            return await self.client.packages_get_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_intransit_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of packages in transit for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetIntransit V2
        """
        async def op():
            return await self.client.packages_get_intransit_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_labsamples_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of lab sample packages created or sent for testing for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetLabsamples V2
        """
        async def op():
            return await self.client.packages_get_labsamples_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_onhold_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetOnhold V1
        """
        async def op():
            return await self.client.packages_get_onhold_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of packages on hold for a specified Facility.
        
          Permissions Required:
          - View Packages

        GET GetOnhold V2
        """
        async def op():
            return await self.client.packages_get_onhold_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_source_harvest_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the source harvests for a Package by its Id.
        
          Permissions Required:
          - View Package Source Harvests

        GET GetSourceHarvest V2
        """
        async def op():
            return await self.client.packages_get_source_harvest_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def packages_get_transferred_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transferred packages for a specific Facility.
        
          Permissions Required:
          - View Packages

        GET GetTransferred V2
        """
        async def op():
            return await self.client.packages_get_transferred_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def packages_get_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        async def op():
            return await self.client.packages_get_types_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def packages_get_types_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves a list of available Package types.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        async def op():
            return await self.client.packages_get_types_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def packages_update_adjust_v2(self, body: Optional['List[PackagesUpdateAdjustV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Set the final quantity for a Package.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateAdjust V2
        """
        async def op():
            return await self.client.packages_update_adjust_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_change_note_v1(self, body: Optional['List[PackagesUpdateChangeNoteV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory
          - Manage Package Notes

        PUT UpdateChangeNote V1
        """
        async def op():
            return await self.client.packages_update_change_note_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_decontaminate_v2(self, body: Optional['List[PackagesUpdateDecontaminateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the Product decontaminate information for a list of packages at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateDecontaminate V2
        """
        async def op():
            return await self.client.packages_update_decontaminate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_donation_flag_v2(self, body: Optional['List[PackagesUpdateDonationFlagV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Flags one or more packages for donation at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateDonationFlag V2
        """
        async def op():
            return await self.client.packages_update_donation_flag_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_donation_unflag_v2(self, body: Optional['List[PackagesUpdateDonationUnflagV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Removes the donation flag from one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateDonationUnflag V2
        """
        async def op():
            return await self.client.packages_update_donation_unflag_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_externalid_v2(self, body: Optional['List[PackagesUpdateExternalidV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the external identifiers for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Package Inventory
          - External Id Enabled

        PUT UpdateExternalid V2
        """
        async def op():
            return await self.client.packages_update_externalid_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_finish_v2(self, body: Optional['List[PackagesUpdateFinishV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates a list of packages as finished for a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateFinish V2
        """
        async def op():
            return await self.client.packages_update_finish_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_item_v2(self, body: Optional['List[PackagesUpdateItemV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the associated Item for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateItem V2
        """
        async def op():
            return await self.client.packages_update_item_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_lab_test_required_v2(self, body: Optional['List[PackagesUpdateLabTestRequiredV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the list of required lab test batches for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateLabTestRequired V2
        """
        async def op():
            return await self.client.packages_update_lab_test_required_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_location_v2(self, body: Optional['List[PackagesUpdateLocationV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the Location and Sublocation for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateLocation V2
        """
        async def op():
            return await self.client.packages_update_location_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_note_v2(self, body: Optional['List[PackagesUpdateNoteV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates notes associated with one or more packages for the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory
          - Manage Package Notes

        PUT UpdateNote V2
        """
        async def op():
            return await self.client.packages_update_note_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_remediate_v2(self, body: Optional['List[PackagesUpdateRemediateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates a list of Product remediations for packages at a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateRemediate V2
        """
        async def op():
            return await self.client.packages_update_remediate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_tradesample_flag_v2(self, body: Optional['List[PackagesUpdateTradesampleFlagV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Flags or unflags one or more packages at the specified Facility as trade samples.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateTradesampleFlag V2
        """
        async def op():
            return await self.client.packages_update_tradesample_flag_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_tradesample_unflag_v2(self, body: Optional['List[PackagesUpdateTradesampleUnflagV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Removes the trade sample flag from one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateTradesampleUnflag V2
        """
        async def op():
            return await self.client.packages_update_tradesample_unflag_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_unfinish_v2(self, body: Optional['List[PackagesUpdateUnfinishV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates a list of packages as unfinished for a specific Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateUnfinish V2
        """
        async def op():
            return await self.client.packages_update_unfinish_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def packages_update_usebydate_v2(self, body: Optional['List[PackagesUpdateUsebydateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the use-by date for one or more packages at the specified Facility.
        
          Permissions Required:
          - View Packages
          - Create/Submit/Discontinue Packages

        PUT UpdateUsebydate V2
        """
        async def op():
            return await self.client.packages_update_usebydate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_create_v2(self, body: Optional['List[PatientsCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Adds new patients to a specified Facility.
        
          Permissions Required:
          - Manage Patients

        POST Create V2
        """
        async def op():
            return await self.client.patients_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_create_add_v1(self, body: Optional['List[PatientsCreateAddV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        POST CreateAdd V1
        """
        async def op():
            return await self.client.patients_create_add_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_create_update_v1(self, body: Optional['List[PatientsCreateUpdateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        POST CreateUpdate V1
        """
        async def op():
            return await self.client.patients_create_update_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        DELETE Delete V1
        """
        async def op():
            return await self.client.patients_delete_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Removes a Patient, identified by an Id, from a specified Facility.
        
          Permissions Required:
          - Manage Patients

        DELETE Delete V2
        """
        async def op():
            return await self.client.patients_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        GET Get V1
        """
        async def op():
            return await self.client.patients_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def patients_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Patient by Id.
        
          Permissions Required:
          - Manage Patients

        GET Get V2
        """
        async def op():
            return await self.client.patients_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def patients_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Patients

        GET GetActive V1
        """
        async def op():
            return await self.client.patients_get_active_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def patients_get_active_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active patients for a specified Facility.
        
          Permissions Required:
          - Manage Patients

        GET GetActive V2
        """
        async def op():
            return await self.client.patients_get_active_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def patients_update_v2(self, body: Optional['List[PatientsUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates Patient information for a specified Facility.
        
          Permissions Required:
          - Manage Patients

        PUT Update V2
        """
        async def op():
            return await self.client.patients_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_additives_v1(self, body: Optional['List[Plant_batchesCreateAdditivesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V1
        """
        async def op():
            return await self.client.plant_batches_create_additives_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_additives_v2(self, body: Optional['List[Plant_batchesCreateAdditivesV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records Additive usage details for plant batches at a specific Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V2
        """
        async def op():
            return await self.client.plant_batches_create_additives_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_additives_usingtemplate_v2(self, body: Optional['List[Plant_batchesCreateAdditivesUsingtemplateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records Additive usage for plant batches at a Facility using predefined additive templates.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditivesUsingtemplate V2
        """
        async def op():
            return await self.client.plant_batches_create_additives_usingtemplate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_adjust_v1(self, body: Optional['List[Plant_batchesCreateAdjustV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateAdjust V1
        """
        async def op():
            return await self.client.plant_batches_create_adjust_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_adjust_v2(self, body: Optional['List[Plant_batchesCreateAdjustV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Applies Facility specific adjustments to plant batches based on submitted reasons and input data.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateAdjust V2
        """
        async def op():
            return await self.client.plant_batches_create_adjust_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_changegrowthphase_v1(self, body: Optional['List[Plant_batchesCreateChangegrowthphaseV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateChangegrowthphase V1
        """
        async def op():
            return await self.client.plant_batches_create_changegrowthphase_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_growthphase_v2(self, body: Optional['List[Plant_batchesCreateGrowthphaseV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the growth phase of plants at a specified Facility based on tracking information.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateGrowthphase V2
        """
        async def op():
            return await self.client.plant_batches_create_growthphase_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_package_v2(self, body: Optional['List[Plant_batchesCreatePackageV2RequestItem]'] = None, is_from_mother_plant: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from plant batches at a Facility, with optional support for packaging from mother plants.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackage V2
        """
        async def op():
            return await self.client.plant_batches_create_package_v2(body=body, is_from_mother_plant=is_from_mother_plant, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_package_frommotherplant_v1(self, body: Optional['List[Plant_batchesCreatePackageFrommotherplantV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageFrommotherplant V1
        """
        async def op():
            return await self.client.plant_batches_create_package_frommotherplant_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_package_frommotherplant_v2(self, body: Optional['List[Plant_batchesCreatePackageFrommotherplantV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from mother plants at the specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageFrommotherplant V2
        """
        async def op():
            return await self.client.plant_batches_create_package_frommotherplant_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_plantings_v2(self, body: Optional['List[Plant_batchesCreatePlantingsV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new plantings for a Facility by generating plant batches based on provided planting details.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreatePlantings V2
        """
        async def op():
            return await self.client.plant_batches_create_plantings_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_split_v1(self, body: Optional['List[Plant_batchesCreateSplitV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateSplit V1
        """
        async def op():
            return await self.client.plant_batches_create_split_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_split_v2(self, body: Optional['List[Plant_batchesCreateSplitV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Splits an existing Plant Batch into multiple groups at the specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST CreateSplit V2
        """
        async def op():
            return await self.client.plant_batches_create_split_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_waste_v1(self, body: Optional['List[Plant_batchesCreateWasteV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V1
        """
        async def op():
            return await self.client.plant_batches_create_waste_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_create_waste_v2(self, body: Optional['List[Plant_batchesCreateWasteV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records waste information for plant batches based on the submitted data for the specified Facility.
        
          Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V2
        """
        async def op():
            return await self.client.plant_batches_create_waste_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_createpackages_v1(self, body: Optional['List[Plant_batchesCreatepackagesV1RequestItem]'] = None, is_from_mother_plant: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST Createpackages V1
        """
        async def op():
            return await self.client.plant_batches_createpackages_v1(body=body, is_from_mother_plant=is_from_mother_plant, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_createplantings_v1(self, body: Optional['List[Plant_batchesCreateplantingsV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory

        POST Createplantings V1
        """
        async def op():
            return await self.client.plant_batches_createplantings_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_delete_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Destroy Immature Plants

        DELETE Delete V1
        """
        async def op():
            return await self.client.plant_batches_delete_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_delete_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Completes the destruction of plant batches based on the provided input data.
        
          Permissions Required:
          - View Immature Plants
          - Destroy Immature Plants

        DELETE Delete V2
        """
        async def op():
            return await self.client.plant_batches_delete_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        GET Get V1
        """
        async def op():
            return await self.client.plant_batches_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Plant Batch by Id.
        
          Permissions Required:
          - View Immature Plants

        GET Get V2
        """
        async def op():
            return await self.client.plant_batches_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        GET GetActive V1
        """
        async def op():
            return await self.client.plant_batches_get_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active plant batches for the specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Immature Plants

        GET GetActive V2
        """
        async def op():
            return await self.client.plant_batches_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        GET GetInactive V1
        """
        async def op():
            return await self.client.plant_batches_get_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive plant batches for the specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Immature Plants

        GET GetInactive V2
        """
        async def op():
            return await self.client.plant_batches_get_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        async def op():
            return await self.client.plant_batches_get_types_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_types_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of plant batch types.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        async def op():
            return await self.client.plant_batches_get_types_v2(body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_waste_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves waste details associated with plant batches at a specified Facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWaste V2
        """
        async def op():
            return await self.client.plant_batches_get_waste_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_waste_reasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteReasons V1
        """
        async def op():
            return await self.client.plant_batches_get_waste_reasons_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_get_waste_reasons_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a list of valid waste reasons associated with immature plant batches for the specified Facility.
        
          Permissions Required:
          - None

        GET GetWasteReasons V2
        """
        async def op():
            return await self.client.plant_batches_get_waste_reasons_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plant_batches_update_location_v2(self, body: Optional['List[Plant_batchesUpdateLocationV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Moves one or more plant batches to new locations with in a specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants

        PUT UpdateLocation V2
        """
        async def op():
            return await self.client.plant_batches_update_location_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_update_moveplantbatches_v1(self, body: Optional['List[Plant_batchesUpdateMoveplantbatchesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants

        PUT UpdateMoveplantbatches V1
        """
        async def op():
            return await self.client.plant_batches_update_moveplantbatches_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_update_name_v2(self, body: Optional['List[Plant_batchesUpdateNameV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Renames plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateName V2
        """
        async def op():
            return await self.client.plant_batches_update_name_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_update_strain_v2(self, body: Optional['List[Plant_batchesUpdateStrainV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Changes the strain of plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateStrain V2
        """
        async def op():
            return await self.client.plant_batches_update_strain_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plant_batches_update_tag_v2(self, body: Optional['List[Plant_batchesUpdateTagV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Replaces tags for plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateTag V2
        """
        async def op():
            return await self.client.plant_batches_update_tag_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_create_adjust_v1(self, body: Optional['List[Processing_jobsCreateAdjustV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManageProcessingJobs

        POST CreateAdjust V1
        """
        async def op():
            return await self.client.processing_jobs_create_adjust_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_create_adjust_v2(self, body: Optional['List[Processing_jobsCreateAdjustV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Adjusts the details of existing processing jobs at a Facility, including units of measure and associated packages.
        
          Permissions Required:
          - Manage Processing Job

        POST CreateAdjust V2
        """
        async def op():
            return await self.client.processing_jobs_create_adjust_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_create_jobtypes_v1(self, body: Optional['List[Processing_jobsCreateJobtypesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        POST CreateJobtypes V1
        """
        async def op():
            return await self.client.processing_jobs_create_jobtypes_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_create_jobtypes_v2(self, body: Optional['List[Processing_jobsCreateJobtypesV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new processing job types for a Facility, including name, category, description, steps, and attributes.
        
          Permissions Required:
          - Manage Processing Job

        POST CreateJobtypes V2
        """
        async def op():
            return await self.client.processing_jobs_create_jobtypes_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_create_start_v1(self, body: Optional['List[Processing_jobsCreateStartV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManageProcessingJobs

        POST CreateStart V1
        """
        async def op():
            return await self.client.processing_jobs_create_start_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_create_start_v2(self, body: Optional['List[Processing_jobsCreateStartV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Initiates new processing jobs at a Facility, including job details and associated packages.
        
          Permissions Required:
          - Manage Processing Job

        POST CreateStart V2
        """
        async def op():
            return await self.client.processing_jobs_create_start_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_createpackages_v1(self, body: Optional['List[Processing_jobsCreatepackagesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManageProcessingJobs

        POST Createpackages V1
        """
        async def op():
            return await self.client.processing_jobs_createpackages_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_createpackages_v2(self, body: Optional['List[Processing_jobsCreatepackagesV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from processing jobs at a Facility, including optional location and note assignments.
        
          Permissions Required:
          - Manage Processing Job

        POST Createpackages V2
        """
        async def op():
            return await self.client.processing_jobs_createpackages_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        DELETE Delete V1
        """
        async def op():
            return await self.client.processing_jobs_delete_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Processing Job at a Facility by marking it as inactive and removing it from active use.
        
          Permissions Required:
          - Manage Processing Job

        DELETE Delete V2
        """
        async def op():
            return await self.client.processing_jobs_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_delete_jobtypes_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        DELETE DeleteJobtypes V1
        """
        async def op():
            return await self.client.processing_jobs_delete_jobtypes_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_delete_jobtypes_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Processing Job Type at a Facility, making it inactive for future use.
        
          Permissions Required:
          - Manage Processing Job

        DELETE DeleteJobtypes V2
        """
        async def op():
            return await self.client.processing_jobs_delete_jobtypes_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET Get V1
        """
        async def op():
            return await self.client.processing_jobs_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a ProcessingJob by Id.
        
          Permissions Required:
          - Manage Processing Job

        GET Get V2
        """
        async def op():
            return await self.client.processing_jobs_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetActive V1
        """
        async def op():
            return await self.client.processing_jobs_get_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves active processing jobs at a specified Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetActive V2
        """
        async def op():
            return await self.client.processing_jobs_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetInactive V1
        """
        async def op():
            return await self.client.processing_jobs_get_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves inactive processing jobs at a specified Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetInactive V2
        """
        async def op():
            return await self.client.processing_jobs_get_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesActive V1
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of all active processing job types defined within a Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesActive V2
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_attributes_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesAttributes V1
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_attributes_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_attributes_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves all processing job attributes available for a Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesAttributes V2
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_attributes_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_categories_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesCategories V1
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_categories_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_categories_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves all processing job categories available for a specified Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesCategories V2
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_categories_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        GET GetJobtypesInactive V1
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_get_jobtypes_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of all inactive processing job types defined within a Facility.
        
          Permissions Required:
          - Manage Processing Job

        GET GetJobtypesInactive V2
        """
        async def op():
            return await self.client.processing_jobs_get_jobtypes_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def processing_jobs_update_finish_v1(self, body: Optional['List[Processing_jobsUpdateFinishV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        PUT UpdateFinish V1
        """
        async def op():
            return await self.client.processing_jobs_update_finish_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_update_finish_v2(self, body: Optional['List[Processing_jobsUpdateFinishV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Completes processing jobs at a Facility by recording final notes and waste measurements.
        
          Permissions Required:
          - Manage Processing Job

        PUT UpdateFinish V2
        """
        async def op():
            return await self.client.processing_jobs_update_finish_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_update_jobtypes_v1(self, body: Optional['List[Processing_jobsUpdateJobtypesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        PUT UpdateJobtypes V1
        """
        async def op():
            return await self.client.processing_jobs_update_jobtypes_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_update_jobtypes_v2(self, body: Optional['List[Processing_jobsUpdateJobtypesV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing processing job types at a Facility, including their name, category, description, steps, and attributes.
        
          Permissions Required:
          - Manage Processing Job

        PUT UpdateJobtypes V2
        """
        async def op():
            return await self.client.processing_jobs_update_jobtypes_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_update_unfinish_v1(self, body: Optional['List[Processing_jobsUpdateUnfinishV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Processing Job

        PUT UpdateUnfinish V1
        """
        async def op():
            return await self.client.processing_jobs_update_unfinish_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def processing_jobs_update_unfinish_v2(self, body: Optional['List[Processing_jobsUpdateUnfinishV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Reopens previously completed processing jobs at a Facility to allow further updates or corrections.
        
          Permissions Required:
          - Manage Processing Job

        PUT UpdateUnfinish V2
        """
        async def op():
            return await self.client.processing_jobs_update_unfinish_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_v1(self, body: Optional['List[SalesCreateDeliveryV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales Delivery

        POST CreateDelivery V1
        """
        async def op():
            return await self.client.sales_create_delivery_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_v2(self, body: Optional['List[SalesCreateDeliveryV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records new sales delivery entries for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.

        POST CreateDelivery V2
        """
        async def op():
            return await self.client.sales_create_delivery_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_v1(self, body: Optional['List[SalesCreateDeliveryRetailerV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The DateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailer V1
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_v2(self, body: Optional['List[SalesCreateDeliveryRetailerV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records retailer delivery data for a given License Number, including delivery destinations. Please note: The DateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.
          - Manage Retailer Delivery

        POST CreateDeliveryRetailer V2
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_depart_v1(self, body: Optional['List[SalesCreateDeliveryRetailerDepartV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerDepart V1
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_depart_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_depart_v2(self, body: Optional['List[SalesCreateDeliveryRetailerDepartV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Processes the departure of retailer deliveries for a Facility using the provided License Number and delivery data.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        POST CreateDeliveryRetailerDepart V2
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_depart_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_end_v1(self, body: Optional['List[SalesCreateDeliveryRetailerEndV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The ActualArrivalDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerEnd V1
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_end_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_end_v2(self, body: Optional['List[SalesCreateDeliveryRetailerEndV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Ends retailer delivery records for a given License Number. Please note: The ActualArrivalDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        POST CreateDeliveryRetailerEnd V2
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_end_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_restock_v1(self, body: Optional['List[SalesCreateDeliveryRetailerRestockV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The DateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerRestock V1
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_restock_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_restock_v2(self, body: Optional['List[SalesCreateDeliveryRetailerRestockV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records restock deliveries for retailer facilities using the provided License Number. Please note: The DateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        POST CreateDeliveryRetailerRestock V2
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_restock_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_sale_v1(self, body: Optional['List[SalesCreateDeliveryRetailerSaleV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        POST CreateDeliveryRetailerSale V1
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_sale_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_delivery_retailer_sale_v2(self, body: Optional['List[SalesCreateDeliveryRetailerSaleV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records sales deliveries originating from a retailer delivery for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.

        POST CreateDeliveryRetailerSale V2
        """
        async def op():
            return await self.client.sales_create_delivery_retailer_sale_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_receipt_v1(self, body: Optional['List[SalesCreateReceiptV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales

        POST CreateReceipt V1
        """
        async def op():
            return await self.client.sales_create_receipt_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_receipt_v2(self, body: Optional['List[SalesCreateReceiptV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records a list of sales deliveries for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales (Write)
          - Industry/Facility Type/Consumer Sales or Industry/Facility Type/Patient Sales or Industry/Facility Type/External Patient Sales or Industry/Facility Type/Caregiver Sales
          - Industry/Facility Type/Advanced Sales
          - WebApi Sales Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.

        POST CreateReceipt V2
        """
        async def op():
            return await self.client.sales_create_receipt_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_create_transaction_by_date_v1(self, date: str, body: Optional['List[SalesCreateTransactionByDateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        POST CreateTransactionByDate V1
        """
        async def op():
            return await self.client.sales_create_transaction_by_date_v1(date, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_delete_delivery_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        DELETE DeleteDelivery V1
        """
        async def op():
            return await self.client.sales_delete_delivery_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_delete_delivery_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Voids a sales delivery for a Facility using the provided License Number and delivery Id.
        
          Permissions Required:
          - Manage Sales Delivery

        DELETE DeleteDelivery V2
        """
        async def op():
            return await self.client.sales_delete_delivery_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_delete_delivery_retailer_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        DELETE DeleteDeliveryRetailer V1
        """
        async def op():
            return await self.client.sales_delete_delivery_retailer_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_delete_delivery_retailer_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Voids a retailer delivery for a Facility using the provided License Number and delivery Id.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - Manage Retailer Delivery

        DELETE DeleteDeliveryRetailer V2
        """
        async def op():
            return await self.client.sales_delete_delivery_retailer_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_delete_receipt_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        DELETE DeleteReceipt V1
        """
        async def op():
            return await self.client.sales_delete_receipt_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_delete_receipt_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a sales receipt for a Facility using the provided License Number and receipt Id.
        
          Permissions Required:
          - Manage Sales

        DELETE DeleteReceipt V2
        """
        async def op():
            return await self.client.sales_delete_receipt_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_get_counties_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetCounties V1
        """
        async def op():
            return await self.client.sales_get_counties_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def sales_get_counties_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of counties available for sales deliveries.
        
          Permissions Required:
          - None

        GET GetCounties V2
        """
        async def op():
            return await self.client.sales_get_counties_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def sales_get_customertypes_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetCustomertypes V1
        """
        async def op():
            return await self.client.sales_get_customertypes_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def sales_get_customertypes_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of customer types.
        
          Permissions Required:
          - None

        GET GetCustomertypes V2
        """
        async def op():
            return await self.client.sales_get_customertypes_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetDeliveriesActive V1
        """
        async def op():
            return await self.client.sales_get_deliveries_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of active sales deliveries for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetDeliveriesActive V2
        """
        async def op():
            return await self.client.sales_get_deliveries_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetDeliveriesInactive V1
        """
        async def op():
            return await self.client.sales_get_deliveries_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of inactive sales deliveries for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetDeliveriesInactive V2
        """
        async def op():
            return await self.client.sales_get_deliveries_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_retailer_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        GET GetDeliveriesRetailerActive V1
        """
        async def op():
            return await self.client.sales_get_deliveries_retailer_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_retailer_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of active retailer deliveries for a Facility, optionally filtered by last modified date range
        
          Permissions Required:
          - View Retailer Delivery
          - Manage Retailer Delivery

        GET GetDeliveriesRetailerActive V2
        """
        async def op():
            return await self.client.sales_get_deliveries_retailer_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_retailer_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        GET GetDeliveriesRetailerInactive V1
        """
        async def op():
            return await self.client.sales_get_deliveries_retailer_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_retailer_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of inactive retailer deliveries for a Facility, optionally filtered by last modified date range
        
          Permissions Required:
          - View Retailer Delivery
          - Manage Retailer Delivery

        GET GetDeliveriesRetailerInactive V2
        """
        async def op():
            return await self.client.sales_get_deliveries_retailer_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_returnreasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          -

        GET GetDeliveriesReturnreasons V1
        """
        async def op():
            return await self.client.sales_get_deliveries_returnreasons_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_deliveries_returnreasons_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of return reasons for sales deliveries based on the provided License Number.
        
          Permissions Required:
          - Sales Delivery

        GET GetDeliveriesReturnreasons V2
        """
        async def op():
            return await self.client.sales_get_deliveries_returnreasons_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def sales_get_delivery_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetDelivery V1
        """
        async def op():
            return await self.client.sales_get_delivery_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_delivery_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a sales delivery record by its Id, with an optional License Number.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetDelivery V2
        """
        async def op():
            return await self.client.sales_get_delivery_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_delivery_retailer_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Retailer Delivery

        GET GetDeliveryRetailer V1
        """
        async def op():
            return await self.client.sales_get_delivery_retailer_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_delivery_retailer_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a retailer delivery record by its ID, with an optional License Number.
        
          Permissions Required:
          - View Retailer Delivery
          - Manage Retailer Delivery

        GET GetDeliveryRetailer V2
        """
        async def op():
            return await self.client.sales_get_delivery_retailer_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_patient_registrations_locations_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          -

        GET GetPatientRegistrationsLocations V1
        """
        async def op():
            return await self.client.sales_get_patient_registrations_locations_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def sales_get_patient_registrations_locations_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of valid Patient registration locations for sales.
        
          Permissions Required:
          -

        GET GetPatientRegistrationsLocations V2
        """
        async def op():
            return await self.client.sales_get_patient_registrations_locations_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def sales_get_paymenttypes_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        GET GetPaymenttypes V1
        """
        async def op():
            return await self.client.sales_get_paymenttypes_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_paymenttypes_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of available payment types for the specified License Number.
        
          Permissions Required:
          - View Sales Delivery
          - Manage Sales Delivery

        GET GetPaymenttypes V2
        """
        async def op():
            return await self.client.sales_get_paymenttypes_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipt_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetReceipt V1
        """
        async def op():
            return await self.client.sales_get_receipt_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipt_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a sales receipt by its Id, with an optional License Number.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceipt V2
        """
        async def op():
            return await self.client.sales_get_receipt_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipts_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetReceiptsActive V1
        """
        async def op():
            return await self.client.sales_get_receipts_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipts_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of active sales receipts for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceiptsActive V2
        """
        async def op():
            return await self.client.sales_get_receipts_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipts_external_by_external_number_v2(self, external_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Sales Receipt by its external number, with an optional License Number.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceiptsExternalByExternalNumber V2
        """
        async def op():
            return await self.client.sales_get_receipts_external_by_external_number_v2(external_number, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipts_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetReceiptsInactive V1
        """
        async def op():
            return await self.client.sales_get_receipts_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_receipts_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None, sales_date_end: Optional[str] = None, sales_date_start: Optional[str] = None) -> Any:
        """
        Returns a list of inactive sales receipts for a Facility, filtered by optional sales or last modified date ranges.
        
          Permissions Required:
          - View Sales
          - Manage Sales

        GET GetReceiptsInactive V2
        """
        async def op():
            return await self.client.sales_get_receipts_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size, sales_date_end=sales_date_end, sales_date_start=sales_date_start)
        return await self.limiter.execute(None, True, op)

    async def sales_get_transactions_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetTransactions V1
        """
        async def op():
            return await self.client.sales_get_transactions_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_get_transactions_by_sales_date_start_and_sales_date_end_v1(self, sales_date_start: str, sales_date_end: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        GET GetTransactionsBySalesDateStartAndSalesDateEnd V1
        """
        async def op():
            return await self.client.sales_get_transactions_by_sales_date_start_and_sales_date_end_v1(sales_date_start, sales_date_end, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def sales_update_delivery_v1(self, body: Optional['List[SalesUpdateDeliveryV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales Delivery

        PUT UpdateDelivery V1
        """
        async def op():
            return await self.client.sales_update_delivery_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_v2(self, body: Optional['List[SalesUpdateDeliveryV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates sales delivery records for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Manage Sales Delivery

        PUT UpdateDelivery V2
        """
        async def op():
            return await self.client.sales_update_delivery_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_complete_v1(self, body: Optional['List[SalesUpdateDeliveryCompleteV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales Delivery

        PUT UpdateDeliveryComplete V1
        """
        async def op():
            return await self.client.sales_update_delivery_complete_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_complete_v2(self, body: Optional['List[SalesUpdateDeliveryCompleteV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Completes a list of sales deliveries for a Facility using the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery

        PUT UpdateDeliveryComplete V2
        """
        async def op():
            return await self.client.sales_update_delivery_complete_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_v1(self, body: Optional['List[SalesUpdateDeliveryHubV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales Delivery

        PUT UpdateDeliveryHub V1
        """
        async def op():
            return await self.client.sales_update_delivery_hub_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_v2(self, body: Optional['List[SalesUpdateDeliveryHubV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates hub transporter details for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Manage Sales Delivery, Manage Sales Delivery Hub

        PUT UpdateDeliveryHub V2
        """
        async def op():
            return await self.client.sales_update_delivery_hub_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_accept_v1(self, body: Optional['List[SalesUpdateDeliveryHubAcceptV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateDeliveryHubAccept V1
        """
        async def op():
            return await self.client.sales_update_delivery_hub_accept_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_accept_v2(self, body: Optional['List[SalesUpdateDeliveryHubAcceptV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Accepts a list of hub sales deliveries for a Facility based on the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery Hub

        PUT UpdateDeliveryHubAccept V2
        """
        async def op():
            return await self.client.sales_update_delivery_hub_accept_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_depart_v1(self, body: Optional['List[SalesUpdateDeliveryHubDepartV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateDeliveryHubDepart V1
        """
        async def op():
            return await self.client.sales_update_delivery_hub_depart_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_depart_v2(self, body: Optional['List[SalesUpdateDeliveryHubDepartV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Processes the departure of hub sales deliveries for a Facility using the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery Hub

        PUT UpdateDeliveryHubDepart V2
        """
        async def op():
            return await self.client.sales_update_delivery_hub_depart_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_verify_id_v1(self, body: Optional['List[SalesUpdateDeliveryHubVerifyIdV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateDeliveryHubVerifyID V1
        """
        async def op():
            return await self.client.sales_update_delivery_hub_verify_id_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_hub_verify_id_v2(self, body: Optional['List[SalesUpdateDeliveryHubVerifyIdV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Verifies identification for a list of hub sales deliveries using the provided License Number and delivery data.
        
          Permissions Required:
          - Manage Sales Delivery Hub

        PUT UpdateDeliveryHubVerifyID V2
        """
        async def op():
            return await self.client.sales_update_delivery_hub_verify_id_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_retailer_v1(self, body: Optional['List[SalesUpdateDeliveryRetailerV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The DateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Retailer Delivery

        PUT UpdateDeliveryRetailer V1
        """
        async def op():
            return await self.client.sales_update_delivery_retailer_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_delivery_retailer_v2(self, body: Optional['List[SalesUpdateDeliveryRetailerV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates retailer delivery records for a given License Number. Please note: The DateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Sales Deliveries(Write)
          - Industry/Facility Type/Retailer Delivery
          - Industry/Facility Type/Consumer Sales Delivery or Industry/Facility Type/Patient Sales Delivery
          - WebApi Sales Deliveries Read Write State (All or WriteOnly)
          - WebApi Retail ID Read Write State (All or WriteOnly) - Required for RID only.
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write) - Required for RID only.
          - Manage Retailer Delivery

        PUT UpdateDeliveryRetailer V2
        """
        async def op():
            return await self.client.sales_update_delivery_retailer_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_receipt_v1(self, body: Optional['List[SalesUpdateReceiptV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Please note: The SalesDateTime field must be the actual date and time of the transaction without time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Sales

        PUT UpdateReceipt V1
        """
        async def op():
            return await self.client.sales_update_receipt_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_receipt_v2(self, body: Optional['List[SalesUpdateReceiptV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates sales receipt records for a given License Number. Please note: The SalesDateTime field must be the actual date and time of the transaction without the time zone. This date/time must already be in the same time zone as the Facility recording the sales. For example, if the Facility is in Pacific Time, then this time must be in Pacific Standard (or Daylight Savings) Time and not in UTC.
        
          Permissions Required:
          - Manage Sales

        PUT UpdateReceipt V2
        """
        async def op():
            return await self.client.sales_update_receipt_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_receipt_finalize_v2(self, body: Optional['List[SalesUpdateReceiptFinalizeV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Finalizes a list of sales receipts for a Facility using the provided License Number and receipt data.
        
          Permissions Required:
          - Manage Sales

        PUT UpdateReceiptFinalize V2
        """
        async def op():
            return await self.client.sales_update_receipt_finalize_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_receipt_unfinalize_v2(self, body: Optional['List[SalesUpdateReceiptUnfinalizeV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Unfinalizes a list of sales receipts for a Facility using the provided License Number and receipt data.
        
          Permissions Required:
          - Manage Sales

        PUT UpdateReceiptUnfinalize V2
        """
        async def op():
            return await self.client.sales_update_receipt_unfinalize_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def sales_update_transaction_by_date_v1(self, date: str, body: Optional['List[SalesUpdateTransactionByDateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Sales

        PUT UpdateTransactionByDate V1
        """
        async def op():
            return await self.client.sales_update_transaction_by_date_v1(date, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def strains_create_v1(self, body: Optional['List[StrainsCreateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        POST Create V1
        """
        async def op():
            return await self.client.strains_create_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def strains_create_v2(self, body: Optional['List[StrainsCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new strain records for a specified Facility.
        
          Permissions Required:
          - Manage Strains

        POST Create V2
        """
        async def op():
            return await self.client.strains_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def strains_create_update_v1(self, body: Optional['List[StrainsCreateUpdateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        POST CreateUpdate V1
        """
        async def op():
            return await self.client.strains_create_update_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def strains_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        DELETE Delete V1
        """
        async def op():
            return await self.client.strains_delete_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def strains_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives an existing strain record for a Facility
        
          Permissions Required:
          - Manage Strains

        DELETE Delete V2
        """
        async def op():
            return await self.client.strains_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def strains_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        GET Get V1
        """
        async def op():
            return await self.client.strains_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def strains_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Strain record by its Id, with an optional license number.
        
          Permissions Required:
          - Manage Strains

        GET Get V2
        """
        async def op():
            return await self.client.strains_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def strains_get_active_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Strains

        GET GetActive V1
        """
        async def op():
            return await self.client.strains_get_active_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def strains_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active strains for the current Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Strains

        GET GetActive V2
        """
        async def op():
            return await self.client.strains_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def strains_get_inactive_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive strains for the current Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Strains

        GET GetInactive V2
        """
        async def op():
            return await self.client.strains_get_inactive_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def strains_update_v2(self, body: Optional['List[StrainsUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing strain records for a specified Facility.
        
          Permissions Required:
          - Manage Strains

        PUT Update V2
        """
        async def op():
            return await self.client.strains_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def tags_get_package_available_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of available package tags. NOTE: This is a premium endpoint.
        
          Permissions Required:
          - Manage Tags

        GET GetPackageAvailable V2
        """
        async def op():
            return await self.client.tags_get_package_available_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def tags_get_plant_available_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of available plant tags. NOTE: This is a premium endpoint.
        
          Permissions Required:
          - Manage Tags

        GET GetPlantAvailable V2
        """
        async def op():
            return await self.client.tags_get_plant_available_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def tags_get_staged_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Returns a list of staged tags. NOTE: This is a premium endpoint.
        
          Permissions Required:
          - Manage Tags
          - RetailId.AllowPackageStaging Key Value enabled

        GET GetStaged V2
        """
        async def op():
            return await self.client.tags_get_staged_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def additives_templates_create_v2(self, body: Optional['List[Additives_templatesCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        POST Create V2
        """
        async def op():
            return await self.client.additives_templates_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def additives_templates_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves an Additive Template by its Id.
        
          Permissions Required:
          - Manage Additives

        GET Get V2
        """
        async def op():
            return await self.client.additives_templates_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def additives_templates_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        GET GetActive V2
        """
        async def op():
            return await self.client.additives_templates_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def additives_templates_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        GET GetInactive V2
        """
        async def op():
            return await self.client.additives_templates_get_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def additives_templates_update_v2(self, body: Optional['List[Additives_templatesUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing additive templates for a specified Facility.
        
          Permissions Required:
          - Manage Additives

        PUT Update V2
        """
        async def op():
            return await self.client.additives_templates_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patients_status_get_statuses_by_patient_license_number_v1(self, patient_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Patients

        GET GetStatusesByPatientLicenseNumber V1
        """
        async def op():
            return await self.client.patients_status_get_statuses_by_patient_license_number_v1(patient_license_number, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def patients_status_get_statuses_by_patient_license_number_v2(self, patient_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a list of statuses for a Patient License Number for a specified Facility. Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Patients

        GET GetStatusesByPatientLicenseNumber V2
        """
        async def op():
            return await self.client.patients_status_get_statuses_by_patient_license_number_v2(patient_license_number, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_create_additives_v1(self, body: Optional['List[PlantsCreateAdditivesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V1
        """
        async def op():
            return await self.client.plants_create_additives_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_additives_v2(self, body: Optional['List[PlantsCreateAdditivesV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage details applied to specific plants at a Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditives V2
        """
        async def op():
            return await self.client.plants_create_additives_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_additives_bylocation_v1(self, body: Optional['List[PlantsCreateAdditivesBylocationV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants
          - Manage Plants Additives

        POST CreateAdditivesBylocation V1
        """
        async def op():
            return await self.client.plants_create_additives_bylocation_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_additives_bylocation_v2(self, body: Optional['List[PlantsCreateAdditivesBylocationV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage for plants based on their location within a specified Facility.
        
          Permissions Required:
          - Manage Plants
          - Manage Plants Additives

        POST CreateAdditivesBylocation V2
        """
        async def op():
            return await self.client.plants_create_additives_bylocation_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_additives_bylocation_usingtemplate_v2(self, body: Optional['List[PlantsCreateAdditivesBylocationUsingtemplateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage for plants by location using a predefined additive template at a specified Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditivesBylocationUsingtemplate V2
        """
        async def op():
            return await self.client.plants_create_additives_bylocation_usingtemplate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_additives_usingtemplate_v2(self, body: Optional['List[PlantsCreateAdditivesUsingtemplateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records additive usage for plants using predefined additive templates at a specified Facility.
        
          Permissions Required:
          - Manage Plants Additives

        POST CreateAdditivesUsingtemplate V2
        """
        async def op():
            return await self.client.plants_create_additives_usingtemplate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_changegrowthphases_v1(self, body: Optional['List[PlantsCreateChangegrowthphasesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateChangegrowthphases V1
        """
        async def op():
            return await self.client.plants_create_changegrowthphases_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_harvestplants_v1(self, body: Optional['List[PlantsCreateHarvestplantsV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        NOTE: If HarvestName is excluded from the request body, or if it is passed in as null, the harvest name is auto-generated.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        POST CreateHarvestplants V1
        """
        async def op():
            return await self.client.plants_create_harvestplants_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_manicure_v2(self, body: Optional['List[PlantsCreateManicureV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates harvest product records from plant batches at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        POST CreateManicure V2
        """
        async def op():
            return await self.client.plants_create_manicure_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_manicureplants_v1(self, body: Optional['List[PlantsCreateManicureplantsV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        POST CreateManicureplants V1
        """
        async def op():
            return await self.client.plants_create_manicureplants_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_moveplants_v1(self, body: Optional['List[PlantsCreateMoveplantsV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreateMoveplants V1
        """
        async def op():
            return await self.client.plants_create_moveplants_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_plantbatch_package_v1(self, body: Optional['List[PlantsCreatePlantbatchPackageV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePlantbatchPackage V1
        """
        async def op():
            return await self.client.plants_create_plantbatch_package_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_plantbatch_package_v2(self, body: Optional['List[PlantsCreatePlantbatchPackageV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from plant batches at a specified Facility.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePlantbatchPackage V2
        """
        async def op():
            return await self.client.plants_create_plantbatch_package_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_plantings_v1(self, body: Optional['List[PlantsCreatePlantingsV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreatePlantings V1
        """
        async def op():
            return await self.client.plants_create_plantings_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_plantings_v2(self, body: Optional['List[PlantsCreatePlantingsV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new plant batches at a specified Facility from existing plant data.
        
          Permissions Required:
          - View Immature Plants
          - Manage Immature Plants Inventory
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        POST CreatePlantings V2
        """
        async def op():
            return await self.client.plants_create_plantings_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_waste_v1(self, body: Optional['List[PlantsCreateWasteV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V1
        """
        async def op():
            return await self.client.plants_create_waste_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_create_waste_v2(self, body: Optional['List[PlantsCreateWasteV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records waste events for plants at a Facility, including method, reason, and location details.
        
          Permissions Required:
          - Manage Plants Waste

        POST CreateWaste V2
        """
        async def op():
            return await self.client.plants_create_waste_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_delete_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants
          - Destroy Veg/Flower Plants

        DELETE Delete V1
        """
        async def op():
            return await self.client.plants_delete_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_delete_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Removes plants from a Facility’s inventory while recording the reason for their disposal.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Destroy Veg/Flower Plants

        DELETE Delete V2
        """
        async def op():
            return await self.client.plants_delete_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET Get V1
        """
        async def op():
            return await self.client.plants_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Plant by Id.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET Get V2
        """
        async def op():
            return await self.client.plants_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_additives_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View/Manage Plants Additives

        GET GetAdditives V1
        """
        async def op():
            return await self.client.plants_get_additives_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_additives_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves additive records applied to plants at a specified Facility.
        
          Permissions Required:
          - View/Manage Plants Additives

        GET GetAdditives V2
        """
        async def op():
            return await self.client.plants_get_additives_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_additives_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          -

        GET GetAdditivesTypes V1
        """
        async def op():
            return await self.client.plants_get_additives_types_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def plants_get_additives_types_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves a list of all plant additive types defined within a Facility.
        
          Permissions Required:
          - None

        GET GetAdditivesTypes V2
        """
        async def op():
            return await self.client.plants_get_additives_types_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def plants_get_by_label_v1(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetByLabel V1
        """
        async def op():
            return await self.client.plants_get_by_label_v1(label, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_by_label_v2(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Plant by label.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetByLabel V2
        """
        async def op():
            return await self.client.plants_get_by_label_v2(label, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_flowering_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetFlowering V1
        """
        async def op():
            return await self.client.plants_get_flowering_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_flowering_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves flowering-phase plants at a specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetFlowering V2
        """
        async def op():
            return await self.client.plants_get_flowering_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_growth_phases_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetGrowthPhases V1
        """
        async def op():
            return await self.client.plants_get_growth_phases_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_growth_phases_v2(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the list of growth phases supported by a specified Facility.
        
          Permissions Required:
          - None

        GET GetGrowthPhases V2
        """
        async def op():
            return await self.client.plants_get_growth_phases_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetInactive V1
        """
        async def op():
            return await self.client.plants_get_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves inactive plants at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetInactive V2
        """
        async def op():
            return await self.client.plants_get_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_mother_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves mother-phase plants at a specified Facility.
        
          Permissions Required:
          - View Mother Plants

        GET GetMother V2
        """
        async def op():
            return await self.client.plants_get_mother_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_mother_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves inactive mother-phase plants at a specified Facility.
        
          Permissions Required:
          - View Mother Plants

        GET GetMotherInactive V2
        """
        async def op():
            return await self.client.plants_get_mother_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_mother_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves mother-phase plants currently marked as on hold at a specified Facility.
        
          Permissions Required:
          - View Mother Plants

        GET GetMotherOnhold V2
        """
        async def op():
            return await self.client.plants_get_mother_onhold_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_onhold_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetOnhold V1
        """
        async def op():
            return await self.client.plants_get_onhold_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves plants that are currently on hold at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetOnhold V2
        """
        async def op():
            return await self.client.plants_get_onhold_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_vegetative_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Veg/Flower Plants

        GET GetVegetative V1
        """
        async def op():
            return await self.client.plants_get_vegetative_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_vegetative_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves vegetative-phase plants at a specified Facility, optionally filtered by last modified date.
        
          Permissions Required:
          - View Veg/Flower Plants

        GET GetVegetative V2
        """
        async def op():
            return await self.client.plants_get_vegetative_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of recorded plant waste events for a specific Facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWaste V2
        """
        async def op():
            return await self.client.plants_get_waste_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_methods_all_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteMethodsAll V1
        """
        async def op():
            return await self.client.plants_get_waste_methods_all_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_methods_all_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of all available plant waste methods for use within a Facility.
        
          Permissions Required:
          - None

        GET GetWasteMethodsAll V2
        """
        async def op():
            return await self.client.plants_get_waste_methods_all_v2(body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_package_v2(self, id: str, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of package records linked to the specified plantWasteId for a given facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWastePackage V2
        """
        async def op():
            return await self.client.plants_get_waste_package_v2(id, body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_plant_v2(self, id: str, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of plants records linked to the specified plantWasteId for a given facility.
        
          Permissions Required:
          - View Plants Waste

        GET GetWastePlant V2
        """
        async def op():
            return await self.client.plants_get_waste_plant_v2(id, body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_reasons_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteReasons V1
        """
        async def op():
            return await self.client.plants_get_waste_reasons_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def plants_get_waste_reasons_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retriveves available reasons for recording mature plant waste at a specified Facility.
        
          Permissions Required:
          - None

        GET GetWasteReasons V2
        """
        async def op():
            return await self.client.plants_get_waste_reasons_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def plants_update_adjust_v2(self, body: Optional['List[PlantsUpdateAdjustV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Adjusts the recorded count of plants at a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateAdjust V2
        """
        async def op():
            return await self.client.plants_update_adjust_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_growthphase_v2(self, body: Optional['List[PlantsUpdateGrowthphaseV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Changes the growth phases of plants within a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateGrowthphase V2
        """
        async def op():
            return await self.client.plants_update_growthphase_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_harvest_v2(self, body: Optional['List[PlantsUpdateHarvestV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Processes whole plant Harvest data for a specific Facility. NOTE: If HarvestName is excluded from the request body, or if it is passed in as null, the harvest name is auto-generated.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        PUT UpdateHarvest V2
        """
        async def op():
            return await self.client.plants_update_harvest_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_location_v2(self, body: Optional['List[PlantsUpdateLocationV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Moves plant batches to new locations within a specified Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateLocation V2
        """
        async def op():
            return await self.client.plants_update_location_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_merge_v2(self, body: Optional['List[PlantsUpdateMergeV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Merges multiple plant groups into a single group within a Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manicure/Harvest Veg/Flower Plants

        PUT UpdateMerge V2
        """
        async def op():
            return await self.client.plants_update_merge_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_split_v2(self, body: Optional['List[PlantsUpdateSplitV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Splits an existing plant group into multiple groups within a Facility.
        
          Permissions Required:
          - View Plant

        PUT UpdateSplit V2
        """
        async def op():
            return await self.client.plants_update_split_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_strain_v2(self, body: Optional['List[PlantsUpdateStrainV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the strain information for plants within a Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateStrain V2
        """
        async def op():
            return await self.client.plants_update_strain_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def plants_update_tag_v2(self, body: Optional['List[PlantsUpdateTagV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Replaces existing plant tags with new tags for plants within a Facility.
        
          Permissions Required:
          - View Veg/Flower Plants
          - Manage Veg/Flower Plants Inventory

        PUT UpdateTag V2
        """
        async def op():
            return await self.client.plants_update_tag_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_create_external_incoming_v1(self, body: Optional['List[TransfersCreateExternalIncomingV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        POST CreateExternalIncoming V1
        """
        async def op():
            return await self.client.transfers_create_external_incoming_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_create_external_incoming_v2(self, body: Optional['List[TransfersCreateExternalIncomingV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates external incoming shipment plans for a Facility.
        
          Permissions Required:
          - Manage Transfers

        POST CreateExternalIncoming V2
        """
        async def op():
            return await self.client.transfers_create_external_incoming_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_create_templates_v1(self, body: Optional['List[TransfersCreateTemplatesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        POST CreateTemplates V1
        """
        async def op():
            return await self.client.transfers_create_templates_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_create_templates_outgoing_v2(self, body: Optional['List[TransfersCreateTemplatesOutgoingV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates new transfer templates for a Facility.
        
          Permissions Required:
          - Manage Transfer Templates

        POST CreateTemplatesOutgoing V2
        """
        async def op():
            return await self.client.transfers_create_templates_outgoing_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_delete_external_incoming_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        DELETE DeleteExternalIncoming V1
        """
        async def op():
            return await self.client.transfers_delete_external_incoming_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_delete_external_incoming_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Voids an external incoming shipment plan for a Facility.
        
          Permissions Required:
          - Manage Transfers

        DELETE DeleteExternalIncoming V2
        """
        async def op():
            return await self.client.transfers_delete_external_incoming_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_delete_templates_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        DELETE DeleteTemplates V1
        """
        async def op():
            return await self.client.transfers_delete_templates_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_delete_templates_outgoing_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a transfer template for a Facility.
        
          Permissions Required:
          - Manage Transfer Templates

        DELETE DeleteTemplatesOutgoing V2
        """
        async def op():
            return await self.client.transfers_delete_templates_outgoing_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_get_deliveries_packages_states_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetDeliveriesPackagesStates V1
        """
        async def op():
            return await self.client.transfers_get_deliveries_packages_states_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_deliveries_packages_states_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of available shipment Package states.
        
          Permissions Required:
          - None

        GET GetDeliveriesPackagesStates V2
        """
        async def op():
            return await self.client.transfers_get_deliveries_packages_states_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: that the {id} parameter above represents a Shipment Plan ID.
        
          Permissions Required:
          - Transfers

        GET GetDelivery V1
        """
        async def op():
            return await self.client.transfers_get_delivery_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of shipment deliveries for a given Transfer Id. Please note: The {id} parameter above represents a Transfer Id.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDelivery V2
        """
        async def op():
            return await self.client.transfers_get_delivery_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_package_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryPackage V1
        """
        async def op():
            return await self.client.transfers_get_delivery_package_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_package_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of packages associated with a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryPackage V2
        """
        async def op():
            return await self.client.transfers_get_delivery_package_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_package_requiredlabtestbatches_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Delivery Package ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryPackageRequiredlabtestbatches V1
        """
        async def op():
            return await self.client.transfers_get_delivery_package_requiredlabtestbatches_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_package_requiredlabtestbatches_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of required lab test batches for a given Transfer Delivery Package Id. Please note: The {id} parameter above represents a Transfer Delivery Package Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryPackageRequiredlabtestbatches V2
        """
        async def op():
            return await self.client.transfers_get_delivery_package_requiredlabtestbatches_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_package_wholesale_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryPackageWholesale V1
        """
        async def op():
            return await self.client.transfers_get_delivery_package_wholesale_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_package_wholesale_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of wholesale shipment packages for a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryPackageWholesale V2
        """
        async def op():
            return await self.client.transfers_get_delivery_package_wholesale_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_transporters_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: that the {id} parameter above represents a Shipment Delivery ID.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryTransporters V1
        """
        async def op():
            return await self.client.transfers_get_delivery_transporters_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_transporters_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transporters for a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryTransporters V2
        """
        async def op():
            return await self.client.transfers_get_delivery_transporters_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_transporters_details_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Shipment Delivery ID.
        
          Permissions Required:
          - Transfers

        GET GetDeliveryTransportersDetails V1
        """
        async def op():
            return await self.client.transfers_get_delivery_transporters_details_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_delivery_transporters_details_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transporter details for a given Transfer Delivery Id. Please note: The {id} parameter above represents a Transfer Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetDeliveryTransportersDetails V2
        """
        async def op():
            return await self.client.transfers_get_delivery_transporters_details_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_hub_v2(self, body: Any = None, estimated_arrival_end: Optional[str] = None, estimated_arrival_start: Optional[str] = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transfer hub shipments for a Facility, filtered by either last modified or estimated arrival date range.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetHub V2
        """
        async def op():
            return await self.client.transfers_get_hub_v2(body=body, estimated_arrival_end=estimated_arrival_end, estimated_arrival_start=estimated_arrival_start, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_incoming_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        GET GetIncoming V1
        """
        async def op():
            return await self.client.transfers_get_incoming_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_incoming_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of incoming shipments for a Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetIncoming V2
        """
        async def op():
            return await self.client.transfers_get_incoming_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_outgoing_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        GET GetOutgoing V1
        """
        async def op():
            return await self.client.transfers_get_outgoing_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_outgoing_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of outgoing shipments for a Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetOutgoing V2
        """
        async def op():
            return await self.client.transfers_get_outgoing_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_rejected_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        GET GetRejected V1
        """
        async def op():
            return await self.client.transfers_get_rejected_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_rejected_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of shipments with rejected packages for a Facility.
        
          Permissions Required:
          - Manage Transfers
          - View Transfers

        GET GetRejected V2
        """
        async def op():
            return await self.client.transfers_get_rejected_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        GET GetTemplates V1
        """
        async def op():
            return await self.client.transfers_get_templates_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_delivery_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        GET GetTemplatesDelivery V1
        """
        async def op():
            return await self.client.transfers_get_templates_delivery_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_delivery_package_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Template Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfers

        GET GetTemplatesDeliveryPackage V1
        """
        async def op():
            return await self.client.transfers_get_templates_delivery_package_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_delivery_transporters_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Template Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfer Templates

        GET GetTemplatesDeliveryTransporters V1
        """
        async def op():
            return await self.client.transfers_get_templates_delivery_transporters_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_delivery_transporters_details_v1(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Please note: The {id} parameter above represents a Transfer Template Delivery ID, not a Manifest Number.
        
          Permissions Required:
          - Transfer Templates

        GET GetTemplatesDeliveryTransportersDetails V1
        """
        async def op():
            return await self.client.transfers_get_templates_delivery_transporters_details_v1(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_outgoing_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transfer templates for a Facility, optionally filtered by last modified date range.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoing V2
        """
        async def op():
            return await self.client.transfers_get_templates_outgoing_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_outgoing_delivery_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of deliveries associated with a specific transfer template.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDelivery V2
        """
        async def op():
            return await self.client.transfers_get_templates_outgoing_delivery_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_outgoing_delivery_package_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of delivery package templates for a given Transfer Template Delivery Id. Please note: The {id} parameter above represents a Transfer Template Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDeliveryPackage V2
        """
        async def op():
            return await self.client.transfers_get_templates_outgoing_delivery_package_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_outgoing_delivery_transporters_v2(self, id: str, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of transporter templates for a given Transfer Template Delivery Id. Please note: The {id} parameter above represents a Transfer Template Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDeliveryTransporters V2
        """
        async def op():
            return await self.client.transfers_get_templates_outgoing_delivery_transporters_v2(id, body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_templates_outgoing_delivery_transporters_details_v2(self, id: str, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves detailed transporter templates for a given Transfer Template Delivery Id. Please note: The {id} parameter above represents a Transfer Template Delivery Id, not a Manifest Number.
        
          Permissions Required:
          - Manage Transfer Templates
          - View Transfer Templates

        GET GetTemplatesOutgoingDeliveryTransportersDetails V2
        """
        async def op():
            return await self.client.transfers_get_templates_outgoing_delivery_transporters_details_v2(id, body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_types_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        async def op():
            return await self.client.transfers_get_types_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def transfers_get_types_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of available transfer types for a Facility based on its license number.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        async def op():
            return await self.client.transfers_get_types_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def transfers_update_external_incoming_v1(self, body: Optional['List[TransfersUpdateExternalIncomingV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfers

        PUT UpdateExternalIncoming V1
        """
        async def op():
            return await self.client.transfers_update_external_incoming_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_update_external_incoming_v2(self, body: Optional['List[TransfersUpdateExternalIncomingV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates external incoming shipment plans for a Facility.
        
          Permissions Required:
          - Manage Transfers

        PUT UpdateExternalIncoming V2
        """
        async def op():
            return await self.client.transfers_update_external_incoming_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_update_templates_v1(self, body: Optional['List[TransfersUpdateTemplatesV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Transfer Templates

        PUT UpdateTemplates V1
        """
        async def op():
            return await self.client.transfers_update_templates_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def transfers_update_templates_outgoing_v2(self, body: Optional['List[TransfersUpdateTemplatesOutgoingV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates existing transfer templates for a Facility.
        
          Permissions Required:
          - Manage Transfer Templates

        PUT UpdateTemplatesOutgoing V2
        """
        async def op():
            return await self.client.transfers_update_templates_outgoing_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def units_of_measure_get_active_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetActive V1
        """
        async def op():
            return await self.client.units_of_measure_get_active_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def units_of_measure_get_active_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves all active units of measure.
        
          Permissions Required:
          - None

        GET GetActive V2
        """
        async def op():
            return await self.client.units_of_measure_get_active_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def units_of_measure_get_inactive_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves all inactive units of measure.
        
          Permissions Required:
          - None

        GET GetInactive V2
        """
        async def op():
            return await self.client.units_of_measure_get_inactive_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def waste_methods_get_all_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves all available waste methods.
        
          Permissions Required:
          - None

        GET GetAll V2
        """
        async def op():
            return await self.client.waste_methods_get_all_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def facilities_get_all_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        This endpoint provides a list of facilities for which the authenticated user has access.
        
          Permissions Required:
          - None

        GET GetAll V1
        """
        async def op():
            return await self.client.facilities_get_all_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def facilities_get_all_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        This endpoint provides a list of facilities for which the authenticated user has access.
        
          Permissions Required:
          - None

        GET GetAll V2
        """
        async def op():
            return await self.client.facilities_get_all_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_create_record_v1(self, body: Optional['List[Lab_testsCreateRecordV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateRecord V1
        """
        async def op():
            return await self.client.lab_tests_create_record_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def lab_tests_create_record_v2(self, body: Optional['List[Lab_testsCreateRecordV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Submits Lab Test results for one or more packages. NOTE: This endpoint allows only PDF files, and uploaded files can be no more than 5 MB in size. The Label element in the request is a Package Label.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        POST CreateRecord V2
        """
        async def op():
            return await self.client.lab_tests_create_record_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def lab_tests_get_batches_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of Lab Test batches.
        
          Permissions Required:
          - None

        GET GetBatches V2
        """
        async def op():
            return await self.client.lab_tests_get_batches_v2(body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_labtestdocument_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        GET GetLabtestdocument V1
        """
        async def op():
            return await self.client.lab_tests_get_labtestdocument_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_labtestdocument_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a specific Lab Test result document by its Id for a given Facility.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        GET GetLabtestdocument V2
        """
        async def op():
            return await self.client.lab_tests_get_labtestdocument_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_results_v1(self, body: Any = None, license_number: Optional[str] = None, package_id: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages

        GET GetResults V1
        """
        async def op():
            return await self.client.lab_tests_get_results_v1(body=body, license_number=license_number, package_id=package_id)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_results_v2(self, body: Any = None, license_number: Optional[str] = None, package_id: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves Lab Test results for a specified Package.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        GET GetResults V2
        """
        async def op():
            return await self.client.lab_tests_get_results_v2(body=body, license_number=license_number, package_id=package_id, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_states_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetStates V1
        """
        async def op():
            return await self.client.lab_tests_get_states_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_states_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Returns a list of all lab testing states.
        
          Permissions Required:
          - None

        GET GetStates V2
        """
        async def op():
            return await self.client.lab_tests_get_states_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetTypes V1
        """
        async def op():
            return await self.client.lab_tests_get_types_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_get_types_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Returns a list of Lab Test types.
        
          Permissions Required:
          - None

        GET GetTypes V2
        """
        async def op():
            return await self.client.lab_tests_get_types_v2(body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def lab_tests_update_labtestdocument_v1(self, body: Optional['List[Lab_testsUpdateLabtestdocumentV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateLabtestdocument V1
        """
        async def op():
            return await self.client.lab_tests_update_labtestdocument_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def lab_tests_update_labtestdocument_v2(self, body: Optional['List[Lab_testsUpdateLabtestdocumentV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates one or more documents for previously submitted lab tests.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateLabtestdocument V2
        """
        async def op():
            return await self.client.lab_tests_update_labtestdocument_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def lab_tests_update_result_release_v1(self, body: Optional['List[Lab_testsUpdateResultReleaseV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateResultRelease V1
        """
        async def op():
            return await self.client.lab_tests_update_result_release_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def lab_tests_update_result_release_v2(self, body: Optional['List[Lab_testsUpdateResultReleaseV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Releases Lab Test results for one or more packages.
        
          Permissions Required:
          - View Packages
          - Manage Packages Inventory

        PUT UpdateResultRelease V2
        """
        async def op():
            return await self.client.lab_tests_update_result_release_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patient_check_ins_create_v1(self, body: Optional['List[Patient_check_insCreateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        POST Create V1
        """
        async def op():
            return await self.client.patient_check_ins_create_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patient_check_ins_create_v2(self, body: Optional['List[Patient_check_insCreateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records patient check-ins for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        POST Create V2
        """
        async def op():
            return await self.client.patient_check_ins_create_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patient_check_ins_delete_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        DELETE Delete V1
        """
        async def op():
            return await self.client.patient_check_ins_delete_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patient_check_ins_delete_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Archives a Patient Check-In, identified by its Id, for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        DELETE Delete V2
        """
        async def op():
            return await self.client.patient_check_ins_delete_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patient_check_ins_get_all_v1(self, body: Any = None, checkin_date_end: Optional[str] = None, checkin_date_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        GET GetAll V1
        """
        async def op():
            return await self.client.patient_check_ins_get_all_v1(body=body, checkin_date_end=checkin_date_end, checkin_date_start=checkin_date_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def patient_check_ins_get_all_v2(self, body: Any = None, checkin_date_end: Optional[str] = None, checkin_date_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a list of patient check-ins for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        GET GetAll V2
        """
        async def op():
            return await self.client.patient_check_ins_get_all_v2(body=body, checkin_date_end=checkin_date_end, checkin_date_start=checkin_date_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def patient_check_ins_get_locations_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetLocations V1
        """
        async def op():
            return await self.client.patient_check_ins_get_locations_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def patient_check_ins_get_locations_v2(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Retrieves a list of Patient Check-In locations.
        
          Permissions Required:
          - None

        GET GetLocations V2
        """
        async def op():
            return await self.client.patient_check_ins_get_locations_v2(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def patient_check_ins_update_v1(self, body: Optional['List[Patient_check_insUpdateV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - ManagePatientsCheckIns

        PUT Update V1
        """
        async def op():
            return await self.client.patient_check_ins_update_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def patient_check_ins_update_v2(self, body: Optional['List[Patient_check_insUpdateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates patient check-ins for a specified Facility.
        
          Permissions Required:
          - ManagePatientsCheckIns

        PUT Update V2
        """
        async def op():
            return await self.client.patient_check_ins_update_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def retail_id_create_associate_v2(self, body: Optional['List[Retail_idCreateAssociateV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Facilitate association of QR codes and Package labels. This will return the count of packages and QR codes associated that were added or replaced.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Receive Associate Product Label, Licensee/Receive Associate Product Label or Admin/Employees/Packages Page/Product Labels(Manage)

        POST CreateAssociate V2
        """
        async def op():
            return await self.client.retail_id_create_associate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def retail_id_create_generate_v2(self, body: Optional['Retail_idCreateGenerateV2Request'] = None, license_number: Optional[str] = None) -> Any:
        """
        Allows you to generate a specific quantity of QR codes. Id value returned (issuance ID) could be used for printing.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Download Product Label, Licensee/Download Product Label or Admin/Employees/Packages Page/Product Labels(Manage)

        POST CreateGenerate V2
        """
        async def op():
            return await self.client.retail_id_create_generate_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def retail_id_create_merge_v2(self, body: Optional['Retail_idCreateMergeV2Request'] = None, license_number: Optional[str] = None) -> Any:
        """
        Merge and adjust one source to one target Package. First Package detected will be processed as target Package. This requires an action reason with name containing the 'Merge' word and setup with 'Package adjustment' area.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Key Value Settings/Retail ID Merge Packages Enabled

        POST CreateMerge V2
        """
        async def op():
            return await self.client.retail_id_create_merge_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def retail_id_create_package_info_v2(self, body: Optional['Retail_idCreatePackageInfoV2Request'] = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves Package information for given list of Package labels.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Retail ID(Write)
          - WebApi Retail ID Read Write State (All or WriteOnly)
          - Industry/View Packages
          - Admin/Employees/Packages Page/Product Labels(Manage)

        POST CreatePackageInfo V2
        """
        async def op():
            return await self.client.retail_id_create_package_info_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def retail_id_get_receive_by_label_v2(self, label: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Get a list of eaches (Retail ID QR code URL) and sibling tags based on given Package label.
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Manage RetailId
          - WebApi Retail ID Read Write State (All or ReadOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Receive Associate Product Label, Licensee/Receive Associate Product Label or Admin/Employees/Packages Page/Product Labels(View or Manage)

        GET GetReceiveByLabel V2
        """
        async def op():
            return await self.client.retail_id_get_receive_by_label_v2(label, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def retail_id_get_receive_qr_by_short_code_v2(self, short_code: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Get a list of eaches (Retail ID QR code URL) and sibling tags based on given short code value (first segment in Retail ID QR code URL).
        
          Permissions Required:
          - External Sources(ThirdPartyVendorV2)/Manage RetailId
          - WebApi Retail ID Read Write State (All or ReadOnly)
          - Industry/View Packages
          - One of the following: Industry/Facility Type/Can Receive Associate Product Label, Licensee/Receive Associate Product Label or Admin/Employees/Packages Page/Product Labels(View or Manage)

        GET GetReceiveQrByShortCode V2
        """
        async def op():
            return await self.client.retail_id_get_receive_qr_by_short_code_v2(short_code, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def caregivers_status_get_by_caregiver_license_number_v1(self, caregiver_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Caregivers

        GET GetByCaregiverLicenseNumber V1
        """
        async def op():
            return await self.client.caregivers_status_get_by_caregiver_license_number_v1(caregiver_license_number, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def caregivers_status_get_by_caregiver_license_number_v2(self, caregiver_license_number: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the status of a Caregiver by their License Number for a specified Facility. Data returned by this endpoint is cached for up to one minute.
        
          Permissions Required:
          - Lookup Caregivers

        GET GetByCaregiverLicenseNumber V2
        """
        async def op():
            return await self.client.caregivers_status_get_by_caregiver_license_number_v2(caregiver_license_number, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def employees_get_all_v1(self, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - Manage Employees

        GET GetAll V1
        """
        async def op():
            return await self.client.employees_get_all_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def employees_get_all_v2(self, body: Any = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of employees for a specified Facility.
        
          Permissions Required:
          - Manage Employees
          - View Employees

        GET GetAll V2
        """
        async def op():
            return await self.client.employees_get_all_v2(body=body, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def employees_get_permissions_v2(self, body: Any = None, employee_license_number: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves the permissions of a specified Employee, identified by their Employee License Number, for a given Facility.
        
          Permissions Required:
          - Manage Employees

        GET GetPermissions V2
        """
        async def op():
            return await self.client.employees_get_permissions_v2(body=body, employee_license_number=employee_license_number, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def harvests_create_finish_v1(self, body: Optional['List[HarvestsCreateFinishV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        POST CreateFinish V1
        """
        async def op():
            return await self.client.harvests_create_finish_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_package_v1(self, body: Optional['List[HarvestsCreatePackageV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackage V1
        """
        async def op():
            return await self.client.harvests_create_package_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_package_v2(self, body: Optional['List[HarvestsCreatePackageV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages from harvested products for a specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackage V2
        """
        async def op():
            return await self.client.harvests_create_package_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_package_testing_v1(self, body: Optional['List[HarvestsCreatePackageTestingV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageTesting V1
        """
        async def op():
            return await self.client.harvests_create_package_testing_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_package_testing_v2(self, body: Optional['List[HarvestsCreatePackageTestingV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Creates packages for testing from harvested products for a specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests
          - View Packages
          - Create/Submit/Discontinue Packages

        POST CreatePackageTesting V2
        """
        async def op():
            return await self.client.harvests_create_package_testing_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_remove_waste_v1(self, body: Optional['List[HarvestsCreateRemoveWasteV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests

        POST CreateRemoveWaste V1
        """
        async def op():
            return await self.client.harvests_create_remove_waste_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_unfinish_v1(self, body: Optional['List[HarvestsCreateUnfinishV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        POST CreateUnfinish V1
        """
        async def op():
            return await self.client.harvests_create_unfinish_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_create_waste_v2(self, body: Optional['List[HarvestsCreateWasteV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Records Waste from harvests for a specified Facility. NOTE: The IDs passed in the request body are the harvest IDs for which you are documenting waste.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests

        POST CreateWaste V2
        """
        async def op():
            return await self.client.harvests_create_waste_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_delete_waste_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Discontinues a specific harvest waste record by Id for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Discontinue Harvest Waste

        DELETE DeleteWaste V2
        """
        async def op():
            return await self.client.harvests_delete_waste_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_get_v1(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET Get V1
        """
        async def op():
            return await self.client.harvests_get_v1(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_v2(self, id: str, body: Any = None, license_number: Optional[str] = None) -> Any:
        """
        Retrieves a Harvest by its Id, optionally validated against a specified Facility License Number.
        
          Permissions Required:
          - View Harvests

        GET Get V2
        """
        async def op():
            return await self.client.harvests_get_v2(id, body=body, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_active_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET GetActive V1
        """
        async def op():
            return await self.client.harvests_get_active_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_active_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of active harvests for a specified Facility.
        
          Permissions Required:
          - View Harvests

        GET GetActive V2
        """
        async def op():
            return await self.client.harvests_get_active_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_inactive_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET GetInactive V1
        """
        async def op():
            return await self.client.harvests_get_inactive_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_inactive_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of inactive harvests for a specified Facility.
        
          Permissions Required:
          - View Harvests

        GET GetInactive V2
        """
        async def op():
            return await self.client.harvests_get_inactive_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_onhold_v1(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests

        GET GetOnhold V1
        """
        async def op():
            return await self.client.harvests_get_onhold_v1(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_onhold_v2(self, body: Any = None, last_modified_end: Optional[str] = None, last_modified_start: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of harvests on hold for a specified Facility.
        
          Permissions Required:
          - View Harvests

        GET GetOnhold V2
        """
        async def op():
            return await self.client.harvests_get_onhold_v2(body=body, last_modified_end=last_modified_end, last_modified_start=last_modified_start, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_waste_v2(self, body: Any = None, harvest_id: Optional[str] = None, license_number: Optional[str] = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of Waste records for a specified Harvest, identified by its Harvest Id, within a Facility identified by its License Number.
        
          Permissions Required:
          - View Harvests

        GET GetWaste V2
        """
        async def op():
            return await self.client.harvests_get_waste_v2(body=body, harvest_id=harvest_id, license_number=license_number, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_waste_types_v1(self, body: Any = None, no: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - None

        GET GetWasteTypes V1
        """
        async def op():
            return await self.client.harvests_get_waste_types_v1(body=body, no=no)
        return await self.limiter.execute(None, True, op)

    async def harvests_get_waste_types_v2(self, body: Any = None, page_number: Optional[str] = None, page_size: Optional[str] = None) -> Any:
        """
        Retrieves a list of Waste types for harvests.
        
          Permissions Required:
          - None

        GET GetWasteTypes V2
        """
        async def op():
            return await self.client.harvests_get_waste_types_v2(body=body, page_number=page_number, page_size=page_size)
        return await self.limiter.execute(None, True, op)

    async def harvests_update_finish_v2(self, body: Optional['List[HarvestsUpdateFinishV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Marks one or more harvests as finished for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        PUT UpdateFinish V2
        """
        async def op():
            return await self.client.harvests_update_finish_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_update_location_v2(self, body: Optional['List[HarvestsUpdateLocationV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Updates the Location of Harvest for a specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateLocation V2
        """
        async def op():
            return await self.client.harvests_update_location_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_update_move_v1(self, body: Optional['List[HarvestsUpdateMoveV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateMove V1
        """
        async def op():
            return await self.client.harvests_update_move_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_update_rename_v1(self, body: Optional['List[HarvestsUpdateRenameV1RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateRename V1
        """
        async def op():
            return await self.client.harvests_update_rename_v1(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_update_rename_v2(self, body: Optional['List[HarvestsUpdateRenameV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Renames one or more harvests for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Manage Harvests

        PUT UpdateRename V2
        """
        async def op():
            return await self.client.harvests_update_rename_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_update_restore_harvested_plants_v2(self, body: Optional['List[HarvestsUpdateRestoreHarvestedPlantsV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Restores previously harvested plants to their original state for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        PUT UpdateRestoreHarvestedPlants V2
        """
        async def op():
            return await self.client.harvests_update_restore_harvested_plants_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

    async def harvests_update_unfinish_v2(self, body: Optional['List[HarvestsUpdateUnfinishV2RequestItem]'] = None, license_number: Optional[str] = None) -> Any:
        """
        Reopens one or more previously finished harvests for the specified Facility.
        
          Permissions Required:
          - View Harvests
          - Finish/Discontinue Harvests

        PUT UpdateUnfinish V2
        """
        async def op():
            return await self.client.harvests_update_unfinish_v2(body=body, license_number=license_number)
        return await self.limiter.execute(None, False, op)

# --- Models ---

class LocationsCreateV1RequestItem(TypedDict, total=False):
    LocationTypeName: str
    Name: str

class LocationsCreateV2RequestItem(TypedDict, total=False):
    LocationTypeName: str
    Name: str

class LocationsCreateUpdateV1RequestItem(TypedDict, total=False):
    Id: int
    LocationTypeName: str
    Name: str

class LocationsUpdateV2RequestItem(TypedDict, total=False):
    Id: int
    LocationTypeName: str
    Name: str

class SublocationsCreateV2RequestItem(TypedDict, total=False):
    Name: str

class SublocationsUpdateV2RequestItem(TypedDict, total=False):
    Id: int
    Name: str

class TransportersCreateDriverV2RequestItem(TypedDict, total=False):
    DriversLicenseNumber: str
    EmployeeId: str
    Name: str

class TransportersCreateVehicleV2RequestItem(TypedDict, total=False):
    LicensePlateNumber: str
    Make: str
    Model: str

class TransportersUpdateDriverV2RequestItem(TypedDict, total=False):
    DriversLicenseNumber: str
    EmployeeId: str
    Id: str
    Name: str

class TransportersUpdateVehicleV2RequestItem(TypedDict, total=False):
    Id: str
    LicensePlateNumber: str
    Make: str
    Model: str

class ItemsCreateV1RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsCreateV2RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsCreateBrandV2RequestItem(TypedDict, total=False):
    Name: str

class ItemsCreateFileV2RequestItem(TypedDict, total=False):
    EncodedImageBase64: str
    FileName: str

class ItemsCreatePhotoV1RequestItem(TypedDict, total=False):
    EncodedImageBase64: str
    FileName: str

class ItemsCreatePhotoV2RequestItem(TypedDict, total=False):
    EncodedImageBase64: str
    FileName: str

class ItemsCreateUpdateV1RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    Id: int
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsUpdateV2RequestItem(TypedDict, total=False):
    AdministrationMethod: str
    Allergens: str
    Description: str
    GlobalProductName: str
    Id: int
    ItemBrand: str
    ItemCategory: str
    ItemIngredients: str
    LabelImageFileSystemIds: str
    LabelPhotoDescription: str
    Name: str
    NumberOfDoses: str
    PackagingImageFileSystemIds: str
    PackagingPhotoDescription: str
    ProcessingJobCategoryName: str
    ProcessingJobTypeName: str
    ProductImageFileSystemIds: str
    ProductPDFFileSystemIds: str
    ProductPhotoDescription: str
    PublicIngredients: str
    ServingSize: str
    Strain: str
    SupplyDurationDays: int
    UnitCbdAContent: float
    UnitCbdAContentDose: float
    UnitCbdAContentDoseUnitOfMeasure: str
    UnitCbdAContentUnitOfMeasure: str
    UnitCbdAPercent: float
    UnitCbdContent: float
    UnitCbdContentDose: float
    UnitCbdContentDoseUnitOfMeasure: str
    UnitCbdContentUnitOfMeasure: str
    UnitCbdPercent: float
    UnitOfMeasure: str
    UnitThcAContent: float
    UnitThcAContentDose: float
    UnitThcAContentDoseUnitOfMeasure: str
    UnitThcAContentUnitOfMeasure: str
    UnitThcAPercent: float
    UnitThcContent: float
    UnitThcContentDose: float
    UnitThcContentDoseUnitOfMeasure: str
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitVolume: float
    UnitVolumeUnitOfMeasure: str
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class ItemsUpdateBrandV2RequestItem(TypedDict, total=False):
    Id: int
    Name: str

class PackagesCreateV1RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreateV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreateV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: bool
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateV2RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreateV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: bool
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateAdjustV1RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    Label: str
    Quantity: int
    ReasonNote: str
    UnitOfMeasure: str

class PackagesCreateAdjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    Label: str
    Quantity: int
    ReasonNote: str
    UnitOfMeasure: str

class PackagesCreateChangeItemV1RequestItem(TypedDict, total=False):
    Item: str
    Label: str

class PackagesCreateChangeLocationV1RequestItem(TypedDict, total=False):
    Label: str
    Location: str
    MoveDate: str
    Sublocation: str

class PackagesCreateFinishV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Label: str

class PackagesCreatePlantingsV1RequestItem(TypedDict, total=False):
    LocationName: str
    PackageAdjustmentAmount: int
    PackageAdjustmentUnitOfMeasureName: str
    PackageLabel: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantedDate: str
    StrainName: str
    SublocationName: str
    UnpackagedDate: str

class PackagesCreatePlantingsV2RequestItem(TypedDict, total=False):
    LocationName: str
    PackageAdjustmentAmount: int
    PackageAdjustmentUnitOfMeasureName: str
    PackageLabel: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantedDate: str
    StrainName: str
    SublocationName: str
    UnpackagedDate: str

class PackagesCreateRemediateV1RequestItem(TypedDict, total=False):
    PackageLabel: str
    RemediationDate: str
    RemediationMethodName: str
    RemediationSteps: str

class PackagesCreateTestingV1RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreateTestingV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreateTestingV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: bool
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateTestingV2RequestItem_Ingredients(TypedDict, total=False):
    Package: str
    Quantity: int
    UnitOfMeasure: str

class PackagesCreateTestingV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ExpirationDate: str
    Ingredients: List[PackagesCreateTestingV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    Quantity: int
    RequiredLabTestBatches: List[str]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    UseSameItem: bool

class PackagesCreateUnfinishV1RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateAdjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    Label: str
    Quantity: int
    ReasonNote: str
    UnitOfMeasure: str

class PackagesUpdateChangeNoteV1RequestItem(TypedDict, total=False):
    Note: str
    PackageLabel: str

class PackagesUpdateDecontaminateV2RequestItem(TypedDict, total=False):
    DecontaminationDate: str
    DecontaminationMethodName: str
    DecontaminationSteps: str
    PackageLabel: str

class PackagesUpdateDonationFlagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateDonationUnflagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateExternalidV2RequestItem(TypedDict, total=False):
    ExternalId: str
    PackageLabel: str

class PackagesUpdateFinishV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Label: str

class PackagesUpdateItemV2RequestItem(TypedDict, total=False):
    Item: str
    Label: str

class PackagesUpdateLabTestRequiredV2RequestItem(TypedDict, total=False):
    Label: str
    RequiredLabTestBatches: List[str]

class PackagesUpdateLocationV2RequestItem(TypedDict, total=False):
    Label: str
    Location: str
    MoveDate: str
    Sublocation: str

class PackagesUpdateNoteV2RequestItem(TypedDict, total=False):
    Note: str
    PackageLabel: str

class PackagesUpdateRemediateV2RequestItem(TypedDict, total=False):
    PackageLabel: str
    RemediationDate: str
    RemediationMethodName: str
    RemediationSteps: str

class PackagesUpdateTradesampleFlagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateTradesampleUnflagV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateUnfinishV2RequestItem(TypedDict, total=False):
    Label: str

class PackagesUpdateUsebydateV2RequestItem(TypedDict, total=False):
    ExpirationDate: str
    Label: str
    SellByDate: str
    UseByDate: str

class PatientsCreateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class PatientsCreateAddV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class PatientsCreateUpdateV1RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    NewLicenseNumber: str
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class PatientsUpdateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    ConcentrateOuncesAllowed: int
    FlowerOuncesAllowed: int
    HasSalesLimitExemption: bool
    InfusedOuncesAllowed: int
    LicenseEffectiveEndDate: str
    LicenseEffectiveStartDate: str
    LicenseNumber: str
    MaxConcentrateThcPercentAllowed: int
    MaxFlowerThcPercentAllowed: int
    NewLicenseNumber: str
    RecommendedPlants: int
    RecommendedSmokableQuantity: int
    ThcOuncesAllowed: int

class Plant_batchesCreateAdditivesV1RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Plant_batchesCreateAdditivesV1RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Plant_batchesCreateAdditivesV1RequestItem_ActiveIngredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantBatchName: str
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class Plant_batchesCreateAdditivesV2RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Plant_batchesCreateAdditivesV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Plant_batchesCreateAdditivesV2RequestItem_ActiveIngredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantBatchName: str
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class Plant_batchesCreateAdditivesUsingtemplateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    AdditivesTemplateName: str
    PlantBatchName: str
    Rate: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str
    Volume: str

class Plant_batchesCreateAdjustV1RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    PlantBatchName: str
    Quantity: int
    ReasonNote: str

class Plant_batchesCreateAdjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentReason: str
    PlantBatchName: str
    Quantity: int
    ReasonNote: str

class Plant_batchesCreateChangegrowthphaseV1RequestItem(TypedDict, total=False):
    Count: int
    CountPerPlant: str
    GrowthDate: str
    GrowthPhase: str
    Name: str
    NewLocation: str
    NewSublocation: str
    PatientLicenseNumber: str
    StartingTag: str

class Plant_batchesCreateGrowthphaseV2RequestItem(TypedDict, total=False):
    Count: int
    CountPerPlant: str
    GrowthDate: str
    GrowthPhase: str
    Name: str
    NewLocation: str
    NewSublocation: str
    PatientLicenseNumber: str
    StartingTag: str

class Plant_batchesCreatePackageV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreatePackageFrommotherplantV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreatePackageFrommotherplantV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreatePlantingsV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    Location: str
    Name: str
    PatientLicenseNumber: str
    SourcePlantBatches: str
    Strain: str
    Sublocation: str
    Type: str

class Plant_batchesCreateSplitV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    GroupName: str
    Location: str
    PatientLicenseNumber: str
    PlantBatch: str
    Strain: str
    Sublocation: str

class Plant_batchesCreateSplitV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    GroupName: str
    Location: str
    PatientLicenseNumber: str
    PlantBatch: str
    Strain: str
    Sublocation: str

class Plant_batchesCreateWasteV1RequestItem(TypedDict, total=False):
    MixedMaterial: str
    Note: str
    PlantBatchName: str
    ReasonName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class Plant_batchesCreateWasteV2RequestItem(TypedDict, total=False):
    MixedMaterial: str
    Note: str
    PlantBatchName: str
    ReasonName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class Plant_batchesCreatepackagesV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    ExpirationDate: str
    Id: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PatientLicenseNumber: str
    PlantBatch: str
    SellByDate: str
    Sublocation: str
    Tag: str
    UseByDate: str

class Plant_batchesCreateplantingsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    Location: str
    Name: str
    PatientLicenseNumber: str
    SourcePlantBatches: str
    Strain: str
    Sublocation: str
    Type: str

class Plant_batchesUpdateLocationV2RequestItem(TypedDict, total=False):
    Location: str
    MoveDate: str
    Name: str
    Sublocation: str

class Plant_batchesUpdateMoveplantbatchesV1RequestItem(TypedDict, total=False):
    Location: str
    MoveDate: str
    Name: str
    Sublocation: str

class Plant_batchesUpdateNameV2RequestItem(TypedDict, total=False):
    Group: str
    Id: int
    NewGroup: str

class Plant_batchesUpdateStrainV2RequestItem(TypedDict, total=False):
    Id: int
    Name: str
    StrainId: int
    StrainName: str

class Plant_batchesUpdateTagV2RequestItem(TypedDict, total=False):
    Group: str
    Id: int
    NewTag: str
    ReplaceDate: str
    TagId: int

class Processing_jobsCreateAdjustV1RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreateAdjustV1RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentNote: str
    AdjustmentReason: str
    CountUnitOfMeasureName: str
    Id: int
    Packages: List[Processing_jobsCreateAdjustV1RequestItem_Packages]
    VolumeUnitOfMeasureName: str
    WeightUnitOfMeasureName: str

class Processing_jobsCreateAdjustV2RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreateAdjustV2RequestItem(TypedDict, total=False):
    AdjustmentDate: str
    AdjustmentNote: str
    AdjustmentReason: str
    CountUnitOfMeasureName: str
    Id: int
    Packages: List[Processing_jobsCreateAdjustV2RequestItem_Packages]
    VolumeUnitOfMeasureName: str
    WeightUnitOfMeasureName: str

class Processing_jobsCreateJobtypesV1RequestItem(TypedDict, total=False):
    Attributes: List[str]
    Category: str
    Description: str
    Name: str
    ProcessingSteps: str

class Processing_jobsCreateJobtypesV2RequestItem(TypedDict, total=False):
    Attributes: List[str]
    Category: str
    Description: str
    Name: str
    ProcessingSteps: str

class Processing_jobsCreateStartV1RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreateStartV1RequestItem(TypedDict, total=False):
    CountUnitOfMeasure: str
    JobName: str
    JobType: str
    Packages: List[Processing_jobsCreateStartV1RequestItem_Packages]
    StartDate: str
    VolumeUnitOfMeasure: str
    WeightUnitOfMeasure: str

class Processing_jobsCreateStartV2RequestItem_Packages(TypedDict, total=False):
    Label: str
    Quantity: int
    UnitOfMeasure: str

class Processing_jobsCreateStartV2RequestItem(TypedDict, total=False):
    CountUnitOfMeasure: str
    JobName: str
    JobType: str
    Packages: List[Processing_jobsCreateStartV2RequestItem_Packages]
    StartDate: str
    VolumeUnitOfMeasure: str
    WeightUnitOfMeasure: str

class Processing_jobsCreatepackagesV1RequestItem(TypedDict, total=False):
    ExpirationDate: str
    FinishDate: str
    FinishNote: str
    FinishProcessingJob: bool
    Item: str
    JobName: str
    Location: str
    Note: str
    PackageDate: str
    PatientLicenseNumber: str
    ProductionBatchNumber: str
    Quantity: int
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    WasteCountQuantity: str
    WasteCountUnitOfMeasureName: str
    WasteVolumeQuantity: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightQuantity: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsCreatepackagesV2RequestItem(TypedDict, total=False):
    ExpirationDate: str
    FinishDate: str
    FinishNote: str
    FinishProcessingJob: bool
    Item: str
    JobName: str
    Location: str
    Note: str
    PackageDate: str
    PatientLicenseNumber: str
    ProductionBatchNumber: str
    Quantity: int
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfMeasure: str
    UseByDate: str
    WasteCountQuantity: str
    WasteCountUnitOfMeasureName: str
    WasteVolumeQuantity: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightQuantity: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsUpdateFinishV1RequestItem(TypedDict, total=False):
    FinishDate: str
    FinishNote: str
    Id: int
    TotalCountWaste: str
    TotalVolumeWaste: str
    TotalWeightWaste: int
    WasteCountUnitOfMeasureName: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsUpdateFinishV2RequestItem(TypedDict, total=False):
    FinishDate: str
    FinishNote: str
    Id: int
    TotalCountWaste: str
    TotalVolumeWaste: str
    TotalWeightWaste: int
    WasteCountUnitOfMeasureName: str
    WasteVolumeUnitOfMeasureName: str
    WasteWeightUnitOfMeasureName: str

class Processing_jobsUpdateJobtypesV1RequestItem(TypedDict, total=False):
    Attributes: List[str]
    CategoryName: str
    Description: str
    Id: int
    Name: str
    ProcessingSteps: str

class Processing_jobsUpdateJobtypesV2RequestItem(TypedDict, total=False):
    Attributes: List[str]
    CategoryName: str
    Description: str
    Id: int
    Name: str
    ProcessingSteps: str

class Processing_jobsUpdateUnfinishV1RequestItem(TypedDict, total=False):
    Id: int

class Processing_jobsUpdateUnfinishV2RequestItem(TypedDict, total=False):
    Id: int

class SalesCreateDeliveryV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateDeliveryV1RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreateDeliveryV1RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreateDeliveryV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateDeliveryV2RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreateDeliveryV2RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreateDeliveryRetailerV1RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateDeliveryRetailerV1RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    EstimatedArrivalDateTime: str
    PatientLicenseNumber: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    Transactions: List[SalesCreateDeliveryRetailerV1RequestItem_Destinations_Transactions]

class SalesCreateDeliveryRetailerV1RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreateDeliveryRetailerV1RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesCreateDeliveryRetailerV1RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreateDeliveryRetailerV1RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreateDeliveryRetailerV2RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateDeliveryRetailerV2RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    EstimatedArrivalDateTime: str
    PatientLicenseNumber: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    Transactions: List[SalesCreateDeliveryRetailerV2RequestItem_Destinations_Transactions]

class SalesCreateDeliveryRetailerV2RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreateDeliveryRetailerV2RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesCreateDeliveryRetailerV2RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreateDeliveryRetailerV2RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesCreateDeliveryRetailerDepartV1RequestItem(TypedDict, total=False):
    RetailerDeliveryId: int

class SalesCreateDeliveryRetailerDepartV2RequestItem(TypedDict, total=False):
    RetailerDeliveryId: int

class SalesCreateDeliveryRetailerEndV1RequestItem_Packages(TypedDict, total=False):
    EndQuantity: int
    EndUnitOfMeasure: str
    Label: str

class SalesCreateDeliveryRetailerEndV1RequestItem(TypedDict, total=False):
    ActualArrivalDateTime: str
    Packages: List[SalesCreateDeliveryRetailerEndV1RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreateDeliveryRetailerEndV2RequestItem_Packages(TypedDict, total=False):
    EndQuantity: int
    EndUnitOfMeasure: str
    Label: str

class SalesCreateDeliveryRetailerEndV2RequestItem(TypedDict, total=False):
    ActualArrivalDateTime: str
    Packages: List[SalesCreateDeliveryRetailerEndV2RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreateDeliveryRetailerRestockV1RequestItem_Packages(TypedDict, total=False):
    PackageLabel: str
    Quantity: int
    RemoveCurrentPackage: bool
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreateDeliveryRetailerRestockV1RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreateDeliveryRetailerRestockV1RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreateDeliveryRetailerRestockV2RequestItem_Packages(TypedDict, total=False):
    PackageLabel: str
    Quantity: int
    RemoveCurrentPackage: bool
    TotalPrice: float
    UnitOfMeasure: str

class SalesCreateDeliveryRetailerRestockV2RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: str
    EstimatedDepartureDateTime: str
    Packages: List[SalesCreateDeliveryRetailerRestockV2RequestItem_Packages]
    RetailerDeliveryId: int

class SalesCreateDeliveryRetailerSaleV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateDeliveryRetailerSaleV1RequestItem(TypedDict, total=False):
    ConsumerId: int
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    RetailerDeliveryId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreateDeliveryRetailerSaleV1RequestItem_Transactions]

class SalesCreateDeliveryRetailerSaleV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateDeliveryRetailerSaleV2RequestItem(TypedDict, total=False):
    ConsumerId: int
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: int
    RetailerDeliveryId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreateDeliveryRetailerSaleV2RequestItem_Transactions]

class SalesCreateReceiptV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateReceiptV1RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreateReceiptV1RequestItem_Transactions]

class SalesCreateReceiptV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesCreateReceiptV2RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesCreateReceiptV2RequestItem_Transactions]

class SalesCreateTransactionByDateV1RequestItem(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateDeliveryV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateDeliveryV1RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdateDeliveryV1RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateDeliveryV2RequestItem(TypedDict, total=False):
    ConsumerId: int
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdateDeliveryV2RequestItem_Transactions]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryCompleteV1RequestItem_ReturnedPackages(TypedDict, total=False):
    Label: str
    ReturnQuantityVerified: int
    ReturnReason: str
    ReturnReasonNote: str
    ReturnUnitOfMeasure: str

class SalesUpdateDeliveryCompleteV1RequestItem(TypedDict, total=False):
    AcceptedPackages: List[str]
    ActualArrivalDateTime: str
    Id: int
    PaymentType: str
    ReturnedPackages: List[SalesUpdateDeliveryCompleteV1RequestItem_ReturnedPackages]

class SalesUpdateDeliveryCompleteV2RequestItem_ReturnedPackages(TypedDict, total=False):
    Label: str
    ReturnQuantityVerified: int
    ReturnReason: str
    ReturnReasonNote: str
    ReturnUnitOfMeasure: str

class SalesUpdateDeliveryCompleteV2RequestItem(TypedDict, total=False):
    AcceptedPackages: List[str]
    ActualArrivalDateTime: str
    Id: int
    PaymentType: str
    ReturnedPackages: List[SalesUpdateDeliveryCompleteV2RequestItem_ReturnedPackages]

class SalesUpdateDeliveryHubV1RequestItem(TypedDict, total=False):
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PhoneNumberForQuestions: str
    PlannedRoute: str
    TransporterFacilityId: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryHubV2RequestItem(TypedDict, total=False):
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PhoneNumberForQuestions: str
    PlannedRoute: str
    TransporterFacilityId: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryHubAcceptV1RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdateDeliveryHubAcceptV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdateDeliveryHubDepartV1RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdateDeliveryHubDepartV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdateDeliveryHubVerifyIdV1RequestItem(TypedDict, total=False):
    Id: int
    PaymentType: str

class SalesUpdateDeliveryHubVerifyIdV2RequestItem(TypedDict, total=False):
    Id: int
    PaymentType: str

class SalesUpdateDeliveryRetailerV1RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateDeliveryRetailerV1RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    DriverEmployeeId: int
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdateDeliveryRetailerV1RequestItem_Destinations_Transactions]
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryRetailerV1RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesUpdateDeliveryRetailerV1RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesUpdateDeliveryRetailerV1RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Id: int
    Packages: List[SalesUpdateDeliveryRetailerV1RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryRetailerV2RequestItem_Destinations_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateDeliveryRetailerV2RequestItem_Destinations(TypedDict, total=False):
    ConsumerId: str
    DriverEmployeeId: int
    DriverName: str
    DriversLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    Id: int
    PatientLicenseNumber: str
    PhoneNumberForQuestions: str
    PlannedRoute: str
    RecipientAddressCity: str
    RecipientAddressCounty: str
    RecipientAddressPostalCode: str
    RecipientAddressState: str
    RecipientAddressStreet1: str
    RecipientAddressStreet2: str
    RecipientName: str
    RecipientZoneId: str
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdateDeliveryRetailerV2RequestItem_Destinations_Transactions]
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateDeliveryRetailerV2RequestItem_Packages(TypedDict, total=False):
    DateTime: str
    PackageLabel: str
    Quantity: int
    TotalPrice: float
    UnitOfMeasure: str

class SalesUpdateDeliveryRetailerV2RequestItem(TypedDict, total=False):
    DateTime: str
    Destinations: List[SalesUpdateDeliveryRetailerV2RequestItem_Destinations]
    DriverEmployeeId: str
    DriverName: str
    DriversLicenseNumber: str
    EstimatedDepartureDateTime: str
    Id: int
    Packages: List[SalesUpdateDeliveryRetailerV2RequestItem_Packages]
    PhoneNumberForQuestions: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class SalesUpdateReceiptV1RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateReceiptV1RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    Id: int
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdateReceiptV1RequestItem_Transactions]

class SalesUpdateReceiptV2RequestItem_Transactions(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class SalesUpdateReceiptV2RequestItem(TypedDict, total=False):
    CaregiverLicenseNumber: str
    ExternalReceiptNumber: str
    Id: int
    IdentificationMethod: str
    PatientLicenseNumber: str
    PatientRegistrationLocationId: int
    SalesCustomerType: str
    SalesDateTime: str
    Transactions: List[SalesUpdateReceiptV2RequestItem_Transactions]

class SalesUpdateReceiptFinalizeV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdateReceiptUnfinalizeV2RequestItem(TypedDict, total=False):
    Id: int

class SalesUpdateTransactionByDateV1RequestItem(TypedDict, total=False):
    CityTax: str
    CountyTax: str
    DiscountAmount: str
    ExciseTax: str
    InvoiceNumber: str
    MunicipalTax: str
    PackageLabel: str
    Price: str
    QrCodes: str
    Quantity: int
    SalesTax: str
    SubTotal: str
    TotalAmount: float
    UnitOfMeasure: str
    UnitThcContent: float
    UnitThcContentUnitOfMeasure: str
    UnitThcPercent: float
    UnitWeight: float
    UnitWeightUnitOfMeasure: str

class StrainsCreateV1RequestItem(TypedDict, total=False):
    CbdLevel: float
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class StrainsCreateV2RequestItem(TypedDict, total=False):
    CbdLevel: float
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class StrainsCreateUpdateV1RequestItem(TypedDict, total=False):
    CbdLevel: float
    Id: int
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class StrainsUpdateV2RequestItem(TypedDict, total=False):
    CbdLevel: float
    Id: int
    IndicaPercentage: float
    Name: str
    SativaPercentage: float
    TestingStatus: str
    ThcLevel: float

class Additives_templatesCreateV2RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Additives_templatesCreateV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Additives_templatesCreateV2RequestItem_ActiveIngredients]
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    Name: str
    Note: str
    ProductSupplier: str
    ProductTradeName: str
    RestrictiveEntryIntervalQuantityDescription: str
    RestrictiveEntryIntervalTimeDescription: str

class Additives_templatesUpdateV2RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class Additives_templatesUpdateV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[Additives_templatesUpdateV2RequestItem_ActiveIngredients]
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    Id: int
    Name: str
    Note: str
    ProductSupplier: str
    ProductTradeName: str
    RestrictiveEntryIntervalQuantityDescription: str
    RestrictiveEntryIntervalTimeDescription: str

class PlantsCreateAdditivesV1RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateAdditivesV1RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateAdditivesV1RequestItem_ActiveIngredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantLabels: List[str]
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateAdditivesV2RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateAdditivesV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateAdditivesV2RequestItem_ActiveIngredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    PlantLabels: List[str]
    ProductSupplier: str
    ProductTradeName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateAdditivesBylocationV1RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateAdditivesBylocationV1RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateAdditivesBylocationV1RequestItem_ActiveIngredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    LocationName: str
    ProductSupplier: str
    ProductTradeName: str
    SublocationName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateAdditivesBylocationV2RequestItem_ActiveIngredients(TypedDict, total=False):
    Name: str
    Percentage: float

class PlantsCreateAdditivesBylocationV2RequestItem(TypedDict, total=False):
    ActiveIngredients: List[PlantsCreateAdditivesBylocationV2RequestItem_ActiveIngredients]
    ActualDate: str
    AdditiveType: str
    ApplicationDevice: str
    EpaRegistrationNumber: str
    LocationName: str
    ProductSupplier: str
    ProductTradeName: str
    SublocationName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str

class PlantsCreateAdditivesBylocationUsingtemplateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    AdditivesTemplateName: str
    LocationName: str
    Rate: str
    SublocationName: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str
    Volume: str

class PlantsCreateAdditivesUsingtemplateV2RequestItem(TypedDict, total=False):
    ActualDate: str
    AdditivesTemplateName: str
    PlantLabels: List[str]
    Rate: str
    TotalAmountApplied: int
    TotalAmountUnitOfMeasure: str
    Volume: str

class PlantsCreateChangegrowthphasesV1RequestItem(TypedDict, total=False):
    GrowthDate: str
    GrowthPhase: str
    Id: int
    Label: str
    NewLocation: str
    NewSublocation: str
    NewTag: str

class PlantsCreateHarvestplantsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    UnitOfWeight: str
    Weight: float

class PlantsCreateManicureV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    PlantCount: int
    UnitOfWeight: str
    Weight: float

class PlantsCreateManicureplantsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    PlantCount: int
    UnitOfWeight: str
    Weight: float

class PlantsCreateMoveplantsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    Label: str
    Location: str
    Sublocation: str

class PlantsCreatePlantbatchPackageV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PackageTag: str
    PatientLicenseNumber: str
    PlantBatchType: str
    PlantLabel: str
    Sublocation: str

class PlantsCreatePlantbatchPackageV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Count: int
    IsDonation: bool
    IsTradeSample: bool
    Item: str
    Location: str
    Note: str
    PackageTag: str
    PatientLicenseNumber: str
    PlantBatchType: str
    PlantLabel: str
    Sublocation: str

class PlantsCreatePlantingsV1RequestItem(TypedDict, total=False):
    ActualDate: str
    LocationName: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantLabel: str
    StrainName: str
    SublocationName: str

class PlantsCreatePlantingsV2RequestItem(TypedDict, total=False):
    ActualDate: str
    LocationName: str
    PatientLicenseNumber: str
    PlantBatchName: str
    PlantBatchType: str
    PlantCount: int
    PlantLabel: str
    StrainName: str
    SublocationName: str

class PlantsCreateWasteV1RequestItem(TypedDict, total=False):
    LocationName: str
    MixedMaterial: str
    Note: str
    PlantLabels: List[Any]
    ReasonName: str
    SublocationName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class PlantsCreateWasteV2RequestItem(TypedDict, total=False):
    LocationName: str
    MixedMaterial: str
    Note: str
    PlantLabels: List[Any]
    ReasonName: str
    SublocationName: str
    UnitOfMeasureName: str
    WasteDate: str
    WasteMethodName: str
    WasteWeight: float

class PlantsUpdateAdjustV2RequestItem(TypedDict, total=False):
    AdjustCount: int
    AdjustReason: str
    AdjustmentDate: str
    Id: int
    Label: str
    ReasonNote: str

class PlantsUpdateGrowthphaseV2RequestItem(TypedDict, total=False):
    GrowthDate: str
    GrowthPhase: str
    Id: int
    Label: str
    NewLocation: str
    NewSublocation: str
    NewTag: str

class PlantsUpdateHarvestV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    PatientLicenseNumber: str
    Plant: str
    UnitOfWeight: str
    Weight: float

class PlantsUpdateLocationV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    Label: str
    Location: str
    Sublocation: str

class PlantsUpdateMergeV2RequestItem(TypedDict, total=False):
    MergeDate: str
    SourcePlantGroupLabel: str
    TargetPlantGroupLabel: str

class PlantsUpdateSplitV2RequestItem(TypedDict, total=False):
    PlantCount: int
    SourcePlantLabel: str
    SplitDate: str
    StrainLabel: str
    TagLabel: str

class PlantsUpdateStrainV2RequestItem(TypedDict, total=False):
    Id: int
    Label: str
    StrainId: int
    StrainName: str

class PlantsUpdateTagV2RequestItem(TypedDict, total=False):
    Id: int
    Label: str
    NewTag: str
    ReplaceDate: str
    TagId: int

class TransfersCreateExternalIncomingV1RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersCreateExternalIncomingV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateExternalIncomingV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersCreateExternalIncomingV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreateExternalIncomingV1RequestItem_Destinations_Transporters]

class TransfersCreateExternalIncomingV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreateExternalIncomingV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateExternalIncomingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersCreateExternalIncomingV2RequestItem_Destinations_Transporters_TransporterDetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateExternalIncomingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersCreateExternalIncomingV2RequestItem_Destinations_Transporters_TransporterDetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateExternalIncomingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersCreateExternalIncomingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreateExternalIncomingV2RequestItem_Destinations_Transporters]

class TransfersCreateExternalIncomingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreateExternalIncomingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateTemplatesV1RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersCreateTemplatesV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateTemplatesV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersCreateTemplatesV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreateTemplatesV1RequestItem_Destinations_Transporters]

class TransfersCreateTemplatesV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreateTemplatesV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateTemplatesOutgoingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersCreateTemplatesOutgoingV2RequestItem_Destinations_Transporters_TransporterDetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateTemplatesOutgoingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersCreateTemplatesOutgoingV2RequestItem_Destinations_Transporters_TransporterDetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersCreateTemplatesOutgoingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersCreateTemplatesOutgoingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferTypeName: str
    Transporters: List[TransfersCreateTemplatesOutgoingV2RequestItem_Destinations_Transporters]

class TransfersCreateTemplatesOutgoingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersCreateTemplatesOutgoingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateExternalIncomingV1RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersUpdateExternalIncomingV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateExternalIncomingV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersUpdateExternalIncomingV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdateExternalIncomingV1RequestItem_Destinations_Transporters]

class TransfersUpdateExternalIncomingV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdateExternalIncomingV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransferId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateExternalIncomingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    ExpirationDate: str
    ExternalId: str
    GrossUnitOfWeightName: str
    GrossWeight: float
    ItemName: str
    PackagedDate: str
    Quantity: int
    SellByDate: str
    UnitOfMeasureName: str
    UseByDate: str
    WholesalePrice: str

class TransfersUpdateExternalIncomingV2RequestItem_Destinations_Transporters_TransporterDetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateExternalIncomingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersUpdateExternalIncomingV2RequestItem_Destinations_Transporters_TransporterDetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateExternalIncomingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    GrossUnitOfWeightId: int
    GrossWeight: float
    InvoiceNumber: str
    Packages: List[TransfersUpdateExternalIncomingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdateExternalIncomingV2RequestItem_Destinations_Transporters]

class TransfersUpdateExternalIncomingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdateExternalIncomingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    PhoneNumberForQuestions: str
    ShipperAddress1: str
    ShipperAddress2: str
    ShipperAddressCity: str
    ShipperAddressPostalCode: str
    ShipperAddressState: str
    ShipperLicenseNumber: str
    ShipperMainPhoneNumber: str
    ShipperName: str
    TransferId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateTemplatesV1RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersUpdateTemplatesV1RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: str
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateTemplatesV1RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersUpdateTemplatesV1RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdateTemplatesV1RequestItem_Destinations_Transporters]

class TransfersUpdateTemplatesV1RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdateTemplatesV1RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransferTemplateId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations_Packages(TypedDict, total=False):
    GrossUnitOfWeightName: str
    GrossWeight: float
    PackageLabel: str
    WholesalePrice: str

class TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations_Transporters_TransporterDetails(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations_Transporters(TypedDict, total=False):
    DriverLayoverLeg: str
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    IsLayover: bool
    PhoneNumberForQuestions: str
    TransporterDetails: List[TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations_Transporters_TransporterDetails]
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations(TypedDict, total=False):
    EstimatedArrivalDateTime: str
    EstimatedDepartureDateTime: str
    InvoiceNumber: str
    Packages: List[TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations_Packages]
    PlannedRoute: str
    RecipientLicenseNumber: str
    TransferDestinationId: int
    TransferTypeName: str
    Transporters: List[TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations_Transporters]

class TransfersUpdateTemplatesOutgoingV2RequestItem(TypedDict, total=False):
    Destinations: List[TransfersUpdateTemplatesOutgoingV2RequestItem_Destinations]
    DriverLicenseNumber: str
    DriverName: str
    DriverOccupationalLicenseNumber: str
    Name: str
    PhoneNumberForQuestions: str
    TransferTemplateId: int
    TransporterFacilityLicenseNumber: str
    VehicleLicensePlateNumber: str
    VehicleMake: str
    VehicleModel: str

class Lab_testsCreateRecordV1RequestItem_Results(TypedDict, total=False):
    LabTestTypeName: str
    Notes: str
    Passed: bool
    Quantity: float

class Lab_testsCreateRecordV1RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    Label: str
    ResultDate: str
    Results: List[Lab_testsCreateRecordV1RequestItem_Results]

class Lab_testsCreateRecordV2RequestItem_Results(TypedDict, total=False):
    LabTestTypeName: str
    Notes: str
    Passed: bool
    Quantity: float

class Lab_testsCreateRecordV2RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    Label: str
    ResultDate: str
    Results: List[Lab_testsCreateRecordV2RequestItem_Results]

class Lab_testsUpdateLabtestdocumentV1RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    LabTestResultId: int

class Lab_testsUpdateLabtestdocumentV2RequestItem(TypedDict, total=False):
    DocumentFileBase64: str
    DocumentFileName: str
    LabTestResultId: int

class Lab_testsUpdateResultReleaseV1RequestItem(TypedDict, total=False):
    PackageLabel: str

class Lab_testsUpdateResultReleaseV2RequestItem(TypedDict, total=False):
    PackageLabel: str

class Patient_check_insCreateV1RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Patient_check_insCreateV2RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Patient_check_insUpdateV1RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    Id: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Patient_check_insUpdateV2RequestItem(TypedDict, total=False):
    CheckInDate: str
    CheckInLocationId: int
    Id: int
    PatientLicenseNumber: str
    RegistrationExpiryDate: str
    RegistrationStartDate: str

class Retail_idCreateAssociateV2RequestItem(TypedDict, total=False):
    PackageLabel: str
    QrUrls: List[str]

class Retail_idCreateGenerateV2Request(TypedDict, total=False):
    PackageLabel: str
    Quantity: int

class Retail_idCreateMergeV2Request(TypedDict, total=False):
    packageLabels: List[str]

class Retail_idCreatePackageInfoV2Request(TypedDict, total=False):
    packageLabels: List[str]

class HarvestsCreateFinishV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int

class HarvestsCreatePackageV1RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatePackageV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatePackageV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreatePackageV2RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatePackageV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatePackageV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreatePackageTestingV1RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatePackageTestingV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatePackageTestingV1RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreatePackageTestingV2RequestItem_Ingredients(TypedDict, total=False):
    HarvestId: int
    HarvestName: str
    UnitOfWeight: str
    Weight: float

class HarvestsCreatePackageTestingV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DecontaminateProduct: bool
    DecontaminationDate: str
    DecontaminationSteps: str
    ExpirationDate: str
    Ingredients: List[HarvestsCreatePackageTestingV2RequestItem_Ingredients]
    IsDonation: bool
    IsProductionBatch: bool
    IsTradeSample: bool
    Item: str
    LabTestStageId: int
    Location: str
    Note: str
    PatientLicenseNumber: str
    ProcessingJobTypeId: int
    ProductRequiresDecontamination: bool
    ProductRequiresRemediation: bool
    ProductionBatchNumber: str
    RemediateProduct: bool
    RemediationDate: str
    RemediationMethodId: int
    RemediationSteps: str
    RequiredLabTestBatches: List[Any]
    SellByDate: str
    Sublocation: str
    Tag: str
    UnitOfWeight: str
    UseByDate: str

class HarvestsCreateRemoveWasteV1RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    UnitOfWeight: str
    WasteType: str
    WasteWeight: float

class HarvestsCreateUnfinishV1RequestItem(TypedDict, total=False):
    Id: int

class HarvestsCreateWasteV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int
    UnitOfWeight: str
    WasteType: str
    WasteWeight: float

class HarvestsUpdateFinishV2RequestItem(TypedDict, total=False):
    ActualDate: str
    Id: int

class HarvestsUpdateLocationV2RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    Id: int

class HarvestsUpdateMoveV1RequestItem(TypedDict, total=False):
    ActualDate: str
    DryingLocation: str
    DryingSublocation: str
    HarvestName: str
    Id: int

class HarvestsUpdateRenameV1RequestItem(TypedDict, total=False):
    Id: int
    NewName: str
    OldName: str

class HarvestsUpdateRenameV2RequestItem(TypedDict, total=False):
    Id: int
    NewName: str
    OldName: str

class HarvestsUpdateRestoreHarvestedPlantsV2RequestItem(TypedDict, total=False):
    HarvestId: int
    PlantTags: List[str]

class HarvestsUpdateUnfinishV2RequestItem(TypedDict, total=False):
    Id: int
