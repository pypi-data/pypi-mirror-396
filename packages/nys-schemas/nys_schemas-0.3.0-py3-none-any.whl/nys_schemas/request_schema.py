from datetime import datetime
from enum import Enum, IntEnum
from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field
from typing_extensions import Annotated


# TODO: Actually use this enum
class RequestPriority(IntEnum):
    LOW = 5
    MEDIUM = 10
    HIGH = 20


class RequestType(str, Enum):
    # Logistic Requests
    FULFILLMENT = "FULFILLMENT"
    REPLENISHMENT = "REPLENISHMENT"
    FETCH = "FETCH"

    # System Control
    RFID_MAINTENANCE = "RFID_MAINTENANCE"
    ONBOARD = "ONBOARD"
    OFFBOARD = "OFFBOARD"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    CHARGING = "CHARGING"
    UNCHARGING = "UNCHARGING"
    UPDATE_CONTENT_CODE = "UPDATE_CONTENT_CODE"

    _description = {
        "FULFILLMENT": "A Logistic Request consisting of Pick-Entities (SkuEntity).", 
        "REPLENISHMENT": "A Logistic Request consisting of Refill-Entities (SkuEntity).",
        "FETCH": "A Logistic Request consisting of Fetch-Carrier-Entities.",
        "RFID_MAINTENANCE": "A System Control Request to write and / or check RFID Tags on a specified Level.",
        "ONBOARD": "A System Control Request to add a Noyes Bot to any Level.",
        "OFFBOARD":  "A System Control Request to remove a specific Noyes Bot from a Level.",
        "PAUSE":  "A System Control Request to remove a specific Noyes Bot from a Level.",
        "RESUME":  "A System Control Request to allow all Bots to get new commands after a PAUSE Request.",
        "CHARGING": "A System Control Request to move a Noyes Bot to a Charging Station.",
        "UNCHARGING": "A System Control Request to remove a Noyes Bot from a Charging Station.",
        "UPDATE_CONTENT_CODE": "A Request to update the content code of a carrier.",
    }

    @property
    def description(self):
        # Return the description or the default value if not found
        return type(self)._description.get(self.value, "No Description available.")


class RequestStatus(str, Enum):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"


# TODO depracate in future, should only be used in nys_test to model customer integrations
class RequestStatusV1(str, Enum):
    """depracate in future, should only be used in nys_test to model customer integrations"""
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    QUEUED = "QUEUED" # deprecated
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    COMPLETED = "COMPLETED" # deprecated
    IN_PROGRESS = "IN_PROGRESS"  # deprecated
    STOPPED = "STOPPED" #TODO
    CANCELLED = "CANCELLED" #TODO combine with stopped
    ABORTED = "ABORTED" # backward compatibility to V1


class EntityType(str, Enum):
    SKU = "Sku"
    PRODUCT = "Product"  # TODO remove once the B2B API is updated to only use SKUs
    CARRIER = "Carrier"
    CONTENT_CODES = "CONTENT_CODES"  # TODO deprecate
    BOX = "Box"


# Sku entity for fulfillment and replenishment requests --------------------------
class SkuEntityInput(BaseModel):
    sku_id: str
    quantity: int

    class Config:
        orm_mode = True
        extra = "forbid"

class CarrierEntityInput(BaseModel):
    carrier_id: str

    class Config:
        orm_mode = True
        extra = "forbid"

class EntityResponse(BaseModel):
    id: str
    entity_type: EntityType
    completed_quantity: int
    total_quantity: int

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.entity_id,
            entity_type=obj.entity_type,
            completed_quantity=obj.completed_quantity,
            total_quantity=obj.total_quantity
        )


class RequestResponseComposite(BaseModel):
    id: str
    type: RequestType
    status: RequestStatus
    priority: int
    created_at: datetime
    updated_at: datetime

    # Optional fields
    """Response model for requests"""
    entities: Optional[List[EntityResponse]] = None
    counter: Optional[int] = None
    placing_pos: Optional[int] = None
    bot_id: Optional[int] = None
    level_id: Optional[int] = None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            type=obj.type,
            status=obj.status,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            priority=obj.priority,
            entities=[EntityResponse.from_orm(e) for e in obj.entities] if obj.type in [RequestType.FULFILLMENT, RequestType.REPLENISHMENT, RequestType.FETCH] else [], #TODO else return None is better but UI doesn't like it rn
            counter=obj.counter if hasattr(obj, 'counter') else None,
            placing_pos=obj.placing_position if hasattr(obj, 'placing_position') else None,
            bot_id=obj.bot_id if hasattr(obj, 'bot_id') else None,
            level_id=obj.level_id if hasattr(obj, 'level_id') else None,
        )


class RequestSort(str, Enum):
    """Valid sort options for requests."""
    TYPE = 'type'
    STATUS = 'status'
    PRIORITY = 'priority'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
    COUNTER = 'counter'
    PLACING_POS = 'placing_pos'

class RequestFilter(BaseModel):
    """Filter model for Request queries"""
    type__eq: Optional[str] = Field(None, description="Filter by request type (exact match)")
    status__eq: Optional[str] = Field(None, description="Filter by request status (exact match)")
    id__eq: Optional[Union[str, UUID]] = Field(None, description="Filter by id (exact match)")
    id__in: Optional[Annotated[List[Union[str, UUID]], Query(None, description="Filter for multiple ids")]] = None
    priority__eq: Optional[int] = Field(None, description="Filter by priority (exact match)")
    counter__eq: Optional[int] = Field(None, description="Filter by counter (exact match)")
    created_at__lte: Optional[datetime] = Field(None, description="Filter by created_at end date")
    created_at__gte: Optional[datetime] = Field(None, description="Filter by created_at start date")
    updated_at__lte: Optional[datetime] = Field(None, description="Filter by updated_at end date")
    updated_at__gte: Optional[datetime] = Field(None, description="Filter by updated_at start date")
    status__in: Optional[Annotated[List[str], Query(None, description="Filter by multiple statuses")]] = None
    type__in: Optional[Annotated[List[str], Query(None, description="Filter by multiple types")]] = None
    class Config:
        extra = "forbid"  # This makes the model reject unexpected fields


class RequestCreateInputGeneric(BaseModel):
    """Input model for creating a request"""
    id: Optional[str] = None
    # type: RequestType
    

# Fetch request ------------------------------------------------------------
class FetchRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating a fetch request"""
    type: Literal[RequestType.FETCH]
    priority: Optional[int] = 10
    entities: List[CarrierEntityInput] #TODO simpler would be to just use carrier_ids: List[str]


# Fulfillment request ------------------------------------------------------------
class FulfillmentRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating a fulfillment request"""
    type: Literal[RequestType.FULFILLMENT]
    priority: Optional[int] = 10
    entities: List[SkuEntityInput]

# Replenishment request ------------------------------------------------------------

class ReplenishmentRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating a replenishment request"""
    type: Literal[RequestType.REPLENISHMENT]
    priority: Optional[int] = 10
    entities: List[SkuEntityInput]


# Onboarding request ------------------------------------------------------------
class OnboardingRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating an onboarding request"""
    type: Literal[RequestType.ONBOARD]

# Offboarding request ------------------------------------------------------------
class OffboardingRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating an offboarding request"""
    type: Literal[RequestType.OFFBOARD]
    bot_id: int

# RFID write request ------------------------------------------------------------
class RFIDWriteRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating an RFID write request"""
    type: Literal[RequestType.RFID_MAINTENANCE]
    level_id: int
    action_type: str #TODO simplify and strong type
    start_from_scratch: bool = True #TODO: is this needed?

# Level pause request ------------------------------------------------------------
class PauseRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating a pause request"""
    type: Literal[RequestType.PAUSE]

# Level resume request ------------------------------------------------------------
class ResumeRequestCreateInput(RequestCreateInputGeneric):
    """Input model for creating a resume request"""
    type: Literal[RequestType.RESUME]

# Create the discriminated union
RequestCreateInput = Annotated[
    Union[
        FetchRequestCreateInput,
        FulfillmentRequestCreateInput,
        ReplenishmentRequestCreateInput,
        OnboardingRequestCreateInput,
        OffboardingRequestCreateInput,
        RFIDWriteRequestCreateInput,
        PauseRequestCreateInput,
        ResumeRequestCreateInput,
    ],
    Field(discriminator='type')
]

