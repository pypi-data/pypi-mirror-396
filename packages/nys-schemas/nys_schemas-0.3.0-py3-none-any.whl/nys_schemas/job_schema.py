from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from enum import Enum
from fastapi import Query




class JobType(str, Enum):
    # Logistic Requests
    BUFFERING = "BUFFERING" #TODO try to move to internal types. but magna integrated with

    PICKING = "PICKING"
    REFILLING = "REFILLING"
    CHECKING = "CHECKING"
    PACKING = "PACKING"

    # Onboard a Bot
    ONBOARDING = "ONBOARDING" # this is the one displayed in the UI
    CLEARING_BALCONY = "CLEARING_BALCONY"
    PLACING_NOYESBOT = "PLACING_NOYESBOT"
    STARTING_NOYESBOT = "STARTING_NOYESBOT"
    SENDING_NOYESBOT_IN = "SENDING_NOYESBOT_IN"


    # Offboard a Bot
    OFFBOARDING = "OFFBOARDING" # this is the one displayed in the UI
    WAITING_FOR_NOYESBOT = "WAITING_FOR_NOYESBOT"
    TURNING_OFF_NOYESBOT = "TURNING_OFF_NOYESBOT"
    REMOVING_NOYESBOT = "REMOVING_NOYESBOT"
    
    # System Control
    CHARGING = "CHARGING"
    UNCHARGING = "UNCHARGING"

    # Default
    NOT_DEFINED = "JOB_TYPE_NOT_FOUND"

    # Default enum member if the value is defined
    @classmethod
    def default(cls):
        return cls.NOT_DEFINED  # You can specify a different default enum

    _descriptions = {
        "BUFFERING" : "Moves a Carrier to a Buffer Space on the same Level.",
        "RETRIEVING" : "Moves a Carrier to a Balcony on the same Level.",
        "PICKING" : "Let's the User pick a given amount out of a Box.",
        "REFILLING" : "Let's the User refill a given amount into a Box.",
        "CHECKING" : "Let's the User check a given Carrier Label.",
        "PACKING" : "Let's the User check the summary of a Request after all Entities have been worked on.",
        "ONBOARDING" : "Let's the User onboard a Bot to any level.",
        "CLEARING_BALCONY" : "Gives the User the instruction to confirm that the Balcony is free. Used during Onboarding.",        
        "PLACING_NOYESBOT" : "Gives the User the instruction to place the Bot on the Balcony. Used during Onboarding.",
        "STARTING_NOYESBOT" : "Gives the User the instruction to start the Bot. Used during Onboarding.",
        "SENDING_NOYESBOT_IN": "Gives the User the instruction to send the Bot inside the Storage.",
        "OFFBOARDING" : "Moves a Bot to the Balcony.",
        "CHARGING" : "Moves a given bot to a Charging Station.",
        "UNCHARGING" : "Removes a given bot from the Charging Station.",
        "WAITING_FOR_NOYESBOT" : "Informs the User that he needs to wait for the bot to come to the balcony. Used during offboarding.",
        "TURNING_OFF_NOYESBOT" : "Informs the User that the bot needs to be turned off before it can be removed from the balcony. Used during offboarding.",
        "REMOVING_NOYESBOT" : "Informs the User that the bot is being removed from the balcony. Used during offboarding.",

    }

    @property
    def description(self):
        # Return the description or the default value if not found
        return self._descriptions.get(self.value, "No Description available.")
    


class JobStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    ERROR = "ERROR" # deprecated, update AGG, Tests and Cloud
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED" 

    _descriptions: Dict[str, str] = {  # type: ignore[assignment]
        "ACCEPTED" : "Job is ACCEPTED. These transitions are allowed: EXECUTING, ERROR, CANCELLING, ABORTED.",
        "EXECUTING" : "Job is EXECUTING and waiting to be triggered. These transitions are allowed: ERROR, CANCELLING, ABORTED.",
        "SUCCEEDED" : "Job is SUCCEEDED. No transitions are allowed. This is a final state.",
        "CANCELLING" : "Job is CANCELLING. A user requested this job to be cancelled. These transisitions are allowed: CANCELLED, ABORTED.",
        "CANCELLED" : "Job is CANCELLED. A user requested this job to be cancelled. The CANCELLING was successfull. This is final state.",
        "ABORTED" : "Job is ABORTED due to a system problem. The System will try to recover from this. This is a final state."
    }

    @property
    def description(self):
        # Return the description or the default value if not found
        return type(self)._descriptions.get(self.value, "No Description available.")


# depracate in future, should only be used in nys_test to model customer integrations
class JobStatusV1(str, Enum):
    """depracate in future, should only be used in nys_test to model customer integrations"""
    HOLD = "HOLD"
    SUCCEEDED = "SUCCEEDED"
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED" #TODO depracate
    EXECUTING = "EXECUTING"
    QUEUED = "QUEUED" #TODO depracate
    ABORTED = "ABORTED"
    CANCELLED = "CANCELLED"
    READY = "READY" #TODO what the heck is this
    WAITING_ON_WING = "WAITING_ON_WING" # TODO depracate
    RECOVERED = "RECOVERED" #TODO



class JobResponse(BaseModel):
    # Mandatory fields
    id: str
    type: JobType
    status: JobStatus
    request_id: str
    created_at: datetime
    updated_at: datetime

    # Optional fields
    box_id: Optional[int]
    carrier_id: Optional[str]
    sku_id: Optional[str]
    balcony_id: Optional[int]
    quantity: Optional[int]
    level_id: Optional[int]
    sku_name: Optional[str]
    bot_id: Optional[int]
    measurement_unit: Optional[str]

    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            type=obj.type,
            status=obj.status,
            request_id=str(obj.request.id),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            box_id=obj.details['box_id'] if obj.details and 'box_id' in obj.details else None,
            carrier_id=obj.details['carrier_id'] if obj.details and 'carrier_id' in obj.details else None,
            sku_id=obj.details['sku_id'] if obj.details and 'sku_id' in obj.details else None,
            sku_name=obj.details['sku_name'] if obj.details and 'sku_name' in obj.details else None,
            bot_id=obj.details['bot_id'] if obj.details and 'bot_id' in obj.details else None,
            measurement_unit=obj.details['measurement_unit'] if obj.details and 'measurement_unit' in obj.details else None,
            balcony_id=obj.balcony_id,
            quantity=obj.quantity,
            level_id=obj.level_id,
        )

class JobSort(str, Enum):
    TYPE = 'type'
    STATUS = 'status'
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
    BALCONY_ID = 'balcony_id'
    LEVEL_ID = 'level_id'


class JobFilter(BaseModel):
    id__eq: Optional[Union[str, UUID]] = Field(None, description="Filter by job ID (exact match)")
    status__eq: Optional[str] = Field(None, description="Filter by job status (exact match)")
    type__eq: Optional[str] = Field(None, description="Filter by job type (exact match)")
    balcony_id__eq: Optional[int] = Field(None, description="Filter by balcony ID (exact match)")
    request_id__eq: Optional[Union[str, UUID]] = Field(None, description="Filter by request ID (exact match)")
    request_id__in: Optional[Annotated[List[Union[str, UUID]], Query(None, description="Filter by multiple request IDs")]] = None
    created_at__lte: Optional[datetime] = Field(None, description="Filter by created_at end date")
    created_at__gte: Optional[datetime] = Field(None, description="Filter by created_at start date")
    updated_at__lte: Optional[datetime] = Field(None, description="Filter by updated_at end date")
    updated_at__gte: Optional[datetime] = Field(None, description="Filter by updated_at start date")
    status__in: Optional[Annotated[List[str], Query(None, description="Filter by multiple job statuses")]] = None
    type__in: Optional[Annotated[List[str], Query(None, description="Filter by multiple job types")]] = None
    level_id__eq: Optional[int] = Field(None, description="Filter by level ID (exact match)") 

    class Config:
        extra = "forbid"  # This makes the model reject unexpected fields


# Job types shown in the UI (external types only, used by nys_api and nys_store_db)
UI_JOB_TYPES = [
    JobType.PICKING,
    JobType.REFILLING,
    JobType.CHECKING,
    JobType.ONBOARDING,
    JobType.OFFBOARDING,
    JobType.PACKING,
    JobType.CLEARING_BALCONY,
    JobType.PLACING_NOYESBOT,
    JobType.STARTING_NOYESBOT,
    JobType.SENDING_NOYESBOT_IN,
    JobType.WAITING_FOR_NOYESBOT,
    JobType.TURNING_OFF_NOYESBOT,
    JobType.REMOVING_NOYESBOT,
]