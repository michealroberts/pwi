# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .units import convert_arcseconds_to_degrees

# **************************************************************************************


class OffsetValue(BaseModel):
    offset: Optional[float] = Field(
        None,
        alias="total",
        description="Total offset (in degrees)",
    )

    rate: Optional[float] = Field(
        None,
        description="Rate of change of the offset (in degrees per second)",
    )

    gradual_progress_adjustment: Optional[float] = Field(
        None,
        alias="gradual_offset_progress",
        description="Progress of the gradual offset adjustment (0-1 scale)",
    )

    @field_validator("offset", "rate", mode="before")
    @classmethod
    def convert_arcsec_to_degrees(cls, v):
        if v is None:
            return v
        return convert_arcseconds_to_degrees(v)


# **************************************************************************************


class PlaneWaveMountDeviceInterfaceOffsets(BaseModel):
    ra: Optional[OffsetValue] = Field(
        None,
        alias="mount.offsets.ra_arcsec",
        description="Right Ascension offset parameter (in degrees)",
    )

    dec: Optional[OffsetValue] = Field(
        None,
        alias="mount.offsets.dec_arcsec",
        description="Declination offset parameter (in degrees)",
    )

    axis0: Optional[OffsetValue] = Field(
        None,
        alias="mount.offsets.axis0_arcsec",
        description="Offset along axis 0, e.g., azimuth, parameter (in degrees)",
    )

    axis1: Optional[OffsetValue] = Field(
        None,
        alias="mount.offsets.axis1_arcsec",
        description="Offset along axis 1, e.g., altitude, parameter (in degrees)",
    )

    path: Optional[OffsetValue] = Field(
        None,
        alias="mount.offsets.path_arcsec",
        description="Offset along the tracking path parameter",
    )

    transverse: Optional[OffsetValue] = Field(
        None,
        alias="mount.offsets.transverse_arcsec",
        description="Transverse offset relative to the tracking path parameter",
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_and_merge_offset(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        offsets = data.get("mount", {}).get("offsets", {})

        data["mount.offsets.ra_arcsec"] = offsets.get("ra_arcsec")
        data["mount.offsets.dec_arcsec"] = offsets.get("dec_arcsec")
        data["mount.offsets.axis0_arcsec"] = offsets.get("axis0_arcsec")
        data["mount.offsets.axis1_arcsec"] = offsets.get("axis1_arcsec")
        data["mount.offsets.path_arcsec"] = offsets.get("path_arcsec")
        data["mount.offsets.transverse_arcsec"] = offsets.get("transverse_arcsec")

        return data


# **************************************************************************************
