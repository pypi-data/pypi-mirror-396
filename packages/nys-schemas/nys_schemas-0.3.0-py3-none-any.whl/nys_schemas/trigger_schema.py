from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from enum import Enum

class TriggerType(str, Enum):
    # TODO: Remove the concept of trigger type. The triggers are sent by job id
    NOT_SPECIFIED = "NOT_SPECIFIED"
    PICKING_TRIGGER = "PICKING_TRIGGER"
    REFILLING_TRIGGER = "REFILLING_TRIGGER"
    ONBOARDING_TRIGGER = "ONBOARDING_TRIGGER"
    OFFBOARDING_TRIGGER = "OFFBOARDING_TRIGGER"
    BRING_CARRIER_TO_BALCONY_TRIGGER = "BRING_CARRIER_TO_BALCONY_TRIGGER"
    FETCH_TRIGGER = "FETCH_TRIGGER"
    UNPLUG_TRIGGER = "UNPLUG_TRIGGER"


class TriggerStatus(str, Enum):
    SUCCEEDED_TRIGGER = "SUCCEEDED_TRIGGER"
    CANCELLED_TRIGGER = "CANCELLED_TRIGGER"



class TriggerRequest(BaseModel):
    """Schema for job trigger requests"""
    trigger_status: TriggerStatus = Field(default=TriggerStatus.SUCCEEDED_TRIGGER, alias="TriggerStatus")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

class TriggerResponse(BaseModel):
    """Schema for job trigger responses"""
    pass  # Empty response as per existing implementation 