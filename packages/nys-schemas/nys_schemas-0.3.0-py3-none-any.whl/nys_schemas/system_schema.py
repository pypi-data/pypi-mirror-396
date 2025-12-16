from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class StorageResponse(BaseModel):
    """Standard response model for maintenance operations like starting/stopping brain or tests"""
    status: str
    details: str
    # For backward compatibility
    brain_status: Optional[str] = Field(None, description="Deprecated: Use status instead")
    testing_script: Optional[str] = Field(None, description="Deprecated: Use status instead")

    def __init__(self, **data):
        super().__init__(**data)
        # Maintain backward compatibility
        if self.status in ["started", "stopped"]:
            self.brain_status = self.status
            self.testing_script = self.status

class ReportResponse(BaseModel):
    """Response model for report generation endpoint"""
    status: str = Field(..., description="Status of report generation")
    tar_filename: str = Field(..., description="Name of the generated tar file")
    report_path: str = Field(..., description="Path where the report is saved")
    # For backward compatibility
    report: str = Field("generated", description="Deprecated: Use status instead")

class EnvFileResponse(BaseModel):
    """Response model for environment file endpoint"""
    properties: Dict[str, Any] = Field(..., description="Environment variables and their values")
    definitions: Dict[str, str] = Field({}, description="JSON schema definitions")
    title: str = Field(..., description="Schema title")
    type: str = Field(..., description="Schema type")



class BalconyResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True

class LevelResponse(BaseModel):
    id: int
    height: Optional[int]

    class Config:
        orm_mode = True



class StorageStatus(str, Enum):
    """Storage status, ordered depending on their "weight". 
    While calculating overall storage status: 
        - if all the levels are in the same status, that will be the overall storage status;
        - if at least one level is in a status with a bigger "weight", that will become the overall storage status.
    """
    __PRIORITIES__ = {
        "RUNNING": 1,
        "PAUSED": 2,
        "STARTING_UP": 3,
        "MAINTENANCE": 4,
        "ERROR": 5,
        "OFF": 6,
        "SHUTTING_DOWN": 7
    }
    
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"
    OFF = "OFF"
    STARTING_UP = "STARTING_UP"
    SHUTTING_DOWN = "SHUTTING_DOWN"
 
    @property
    def priority(self) -> int:
        return type(self).__PRIORITIES__[self.value]


class StorageStatusResponse(BaseModel):
    storage_status: StorageStatus

    class Config:
        orm_mode = True


class LevelStatus(str, Enum):
    # Priority mapping for level statuses, kept inside the class
    __PRIORITIES__ = {
        "RUNNING": 1,
        "PAUSED": 2,
        "STARTING_UP": 3,
        "MAINTENANCE": 4,
        "ERROR": 5,
        "OFF": 6,
        "SHUTTING_DOWN": 7
    }

    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    MAINTENANCE = "MAINTENANCE"
    STARTING_UP = "STARTING_UP"
    ERROR = "ERROR"
    OFF = "OFF"
    SHUTTING_DOWN = "SHUTTING_DOWN"

    @property
    def priority(self) -> int:
        return type(self).__PRIORITIES__[self.value]





