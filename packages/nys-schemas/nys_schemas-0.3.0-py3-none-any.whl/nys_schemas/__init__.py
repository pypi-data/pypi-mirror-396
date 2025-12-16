"""
This module contains the schemas for the nys_api and nys_client. they are intended to be customer-facing and are used to validate requests and responses.
"""


# Import customer-facing job and request types from local modules
from .request_schema import (
    RequestType, 
    RequestStatus, 
    RequestStatusV1,
    RequestPriority, 
    EntityType, 
    SkuEntityInput,
    CarrierEntityInput,
    FulfillmentRequestCreateInput, 
    FetchRequestCreateInput, 
    ReplenishmentRequestCreateInput, 
    OnboardingRequestCreateInput, 
    OffboardingRequestCreateInput, 
    RFIDWriteRequestCreateInput, 
    PauseRequestCreateInput, 
    ResumeRequestCreateInput, 
    RequestResponseComposite, 
    RequestFilter, 
    RequestSort,
)
from .job_schema import JobType, JobStatus, JobStatusV1, JobResponse, JobFilter, JobSort, UI_JOB_TYPES

# Import moved enums from local modules
from .auth_schema import LocaleEnum, RoleEnum, SignupRequest, SignUpResponse, LoginRequest, LoginResponse, ForgotPasswordRequest, ResetPasswordRequest, RefreshTokenRequest, TokenResponse, ApiKeyCreateInput, ApiKeyCreateResponse, ApiKeyInfo, ApiKeysGetResponse, ApiKeyDeleteResponse, UserUpdateRequest, UserUpdateResponse, PasswordPolicyResponse, ApiKeySort, ApiKeySearch, ApiKeyFilter
from .user_schema import UserSchema
from .box_schema import BoxResponse
from .carrier_schema import CarrierResponse
from .export_schema import ExportResponse
from .inventory_view_schema import InventoryViewResponse, InventoryViewFilter, InventoryViewSort
from .load_schema import LoadResponse
from .request_schema import RequestResponseComposite, RequestFilter, RequestSort
from .requests_and_jobs_view_schema import RequestsAndJobsViewResponse
from .sku_schema import SkuResponse, SkuCreate, SkuPatch, MeasurementUnit, MeasurementUnitShort, OnEmptySKUAction
from .trigger_schema import TriggerType, TriggerStatus
from .system_schema import StorageResponse, StorageStatus, LevelStatus
from .content_code import ContentCode, ContentCodeUpdateStatus
from .group_by_options import GroupByOptions
from .sort_enums import SortOrder
from .events_schema import EventsResponse, EventsFilter, EventsSort, LogLevel

__all__ = [
    # auth.py
    "LocaleEnum",
    "RoleEnum",
    "SignupRequest",
    "SignUpResponse",
    "LoginRequest",
    "LoginResponse",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "ApiKeyCreateInput",
    "ApiKeyCreateResponse",
    "ApiKeyInfo",
    "ApiKeysGetResponse",
    "ApiKeyDeleteResponse",
    "UserUpdateRequest",
    "UserUpdateResponse",
    "PasswordPolicyResponse",
    "ApiKeySort",
    "ApiKeySearch",
    "ApiKeyFilter",
    
    # box.py
    "BoxResponse",
    
    # carrier.py
    "CarrierResponse",
    
    # export.py
    "ExportResponse",
    
    # inventory.py
    "InventoryViewResponse",
    "InventoryViewFilter",
    "InventoryViewSort",
    
    # job.py
    "JobResponse",
    "JobFilter",
    "JobSort",
    
    # load.py
    "LoadResponse",
    
    # request.py
    "RequestResponseComposite",
    "RequestFilter",
    "RequestSort",
    "SkuEntityInput",
    "CarrierEntityInput",
    "FulfillmentRequestCreateInput",
    "FetchRequestCreateInput",
    "ReplenishmentRequestCreateInput",
    "OnboardingRequestCreateInput",
    "OffboardingRequestCreateInput",
    "RFIDWriteRequestCreateInput",
    "PauseRequestCreateInput",
    "ResumeRequestCreateInput",
    "RequestType",  
    "RequestStatus",
    "RequestStatusV1",

    # job_types.py
    "JobType",  
    "JobStatus",
    "JobStatusV1",
    "UI_JOB_TYPES",
    
    # requests_and_jobs_view.py
    "RequestsAndJobsViewResponse",
    
    # sku.py
    "SkuResponse",
    "SkuCreate",
    "SkuPatch",
    
    # storage.py
    "StorageResponse",
    
    # user.py
    "UserSchema",
    
    # events.py
    "EventsResponse",
    "EventsFilter",
    "EventsSort",
    "LogLevel",

    # group_by_options.py
    "GroupByOptions",

    # sort_enums.py
    "SortOrder",

    # system_schema.py
    "StorageStatus",
    "LevelStatus",
    
    # trigger_schema.py
    "TriggerType",
    "TriggerStatus",
] 