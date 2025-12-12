from typing import Optional

from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    project_uid: str = Field(primary_key=True)
    crs: str = Field(description="Coordinate Reference System")


class Location(SQLModel, table=True):
    location_uid: str = Field(primary_key=True)
    project_uid: str = Field(foreign_key="project.project_uid")
    source_id: str
    location_type: str
    easting: float
    northing: float
    ground_level: float
    depth_to_base: float
    elevation_at_base: float
    latitude: float
    longitude: float


class DepthInformation(SQLModel):
    depth_to_top: float
    depth_to_base: Optional[float] = None
    elevation_at_top: float
    elevation_at_base: Optional[float] = None


class Sample(DepthInformation, table=True):
    sample_uid: Optional[int] = Field(default=None, primary_key=True)
    project_uid: str = Field(foreign_key="project.project_uid")
    location_uid: str = Field(foreign_key="location.location_uid")
    source_id: str


class InSitu(DepthInformation):
    project_uid: str = Field(foreign_key="project.project_uid")
    location_uid: str = Field(foreign_key="location.location_uid")


class Lab(SQLModel):
    project_uid: str = Field(foreign_key="project.project_uid")
    location_uid: str = Field(foreign_key="location.location_uid")
    sample_uid: str = Field(foreign_key="sample.sample_uid")


class Material(InSitu, table=True):
    """Material descriptions from the field. GEOL group in AGS 3 and AGS 4."""

    id: Optional[int] = Field(default=None, primary_key=True)
    material_name: str
    material_description: Optional[str] = None


class SPT(InSitu, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    spt_count: int


class RockCore(InSitu, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tcr: Optional[float] = Field(default=None, description="Total Core Recovery (%)")
    scr: Optional[float] = Field(default=None, description="Solid Core Recovery (%)")
    rqd: Optional[float] = Field(
        default=None, description="Rock Quality Designation (%)"
    )


class Weathering(InSitu, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    weathering: str
