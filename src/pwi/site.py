# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .utils import parse_float_safely

# **************************************************************************************


class PlaneWaveMountDeviceInterfaceSite(BaseModel):
    # The site latitude (in degrees):
    latitude: Optional[float] = Field(
        None, alias="site.latitude_degs", description="The site latitude (in degrees)"
    )

    # The site longitude (in degrees):
    longitude: Optional[float] = Field(None, alias="site.longitude_degs")

    # The site elevation above sea level (in meters):
    elevation: Optional[float] = Field(None, alias="site.height_meters")

    # The Local Mean Sidereal Time (LMST) at the site (in hours):
    lmst: Optional[float] = Field(None, alias="site.lmst_hours")

    @model_validator(mode="before")
    @classmethod
    def flatten_and_merge_site(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        site = data.get("site", {})

        data["site.latitude_degs"] = site.get("latitude_degs")
        data["site.longitude_degs"] = site.get("longitude_degs")
        data["site.height_meters"] = site.get("height_meters")
        data["site.lmst_hours"] = site.get("lmst_hours")

        return data

    @field_validator("latitude", mode="before")
    @classmethod
    def parse_latitude(cls, value: Any):
        return parse_float_safely(value)

    @field_validator("longitude", mode="before")
    @classmethod
    def parse_longitude(cls, value: Any):
        return parse_float_safely(value)

    @field_validator("elevation", mode="before")
    @classmethod
    def parse_elevation(cls, value: Any):
        return parse_float_safely(value)

    @field_validator("lmst", mode="before")
    @classmethod
    def parse_lmst(cls, value: Any):
        return parse_float_safely(value)


# **************************************************************************************
