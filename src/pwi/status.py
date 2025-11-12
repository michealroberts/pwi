# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from datetime import datetime, timezone
from typing import Any, Optional

from celerity.common import (
    is_equatorial_coordinate,
    is_horizontal_coordinate,
)
from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import TypedDict

from .utils import parse_float_safely

# **************************************************************************************


class EquatorialCoordinate(TypedDict):
    ra: float
    dec: float


# **************************************************************************************


class HorizontalCoordinate(TypedDict):
    alt: float
    az: float


# **************************************************************************************


class PlaneWaveMountDeviceInterfaceStatus(BaseModel):
    # The current Julian Date as reported by the mount:
    JD: Optional[float] = Field(None, alias="mount.julian_date")

    # The current datetime signature as reported by the mount:
    utc: Optional[datetime] = Field(
        None,
        title="UTC",
        description="The UTC time of the mount",
        alias="mount.utc",
    )

    # Is the mount currently connected?
    is_connected: bool = Field(False, alias="mount.is_connected")

    # Is the mount currently slewing?
    is_slewing: bool = Field(False, alias="mount.is_slewing")

    # Is the mount currently tracking?
    is_tracking: bool = Field(False, alias="mount.is_tracking")

    # The current J2000 Right Ascension:
    j2000_equatorial_coordinate: Optional[EquatorialCoordinate] = Field(
        None, alias="mount.j2000_equatorial_coordinate"
    )

    # The current apparent Right Ascension:
    apparent_equatorial_coordinate: Optional[EquatorialCoordinate] = Field(
        None, alias="mount.apparent_equatorial_coordinate"
    )

    # The target J2000 Right Ascension:
    target_j2000_equatorial_coordinate: Optional[EquatorialCoordinate] = Field(
        None,
        title="Target J2000 Equatorial Coordinate",
        alias="mount.target_j2000_equatorial_coordinate",
        description="The target equatorial coordinate at epoch J2000",
    )

    # The target equatorial coordinate of the mount:
    target_apparent_equatorial_coordinate: Optional[EquatorialCoordinate] = Field(
        None, alias="mount.target_apparent_equatorial_coordinate"
    )

    # The current horizontal coordinate of the mount pointing:
    horizontal_coordinate: Optional[HorizontalCoordinate] = Field(
        None, alias="mount.horizontal_coordinate"
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_and_merge_status(cls, data: Any):
        if not isinstance(data, dict):
            return data

        mount = data.get("mount", {})

        data["mount.utc"] = mount.get("timestamp_utc")
        data["mount.julian_date"] = mount.get("julian_date")
        data["mount.is_slewing"] = mount.get("is_slewing")
        data["mount.is_connected"] = mount.get("is_connected")
        data["mount.is_tracking"] = mount.get("is_tracking")

        ra_j2000_hours = mount.get("ra_j2000_hours")

        dec_j2000_degrees = mount.get("dec_j2000_degs")

        if ra_j2000_hours is not None and dec_j2000_degrees is not None:
            data["mount.j2000_equatorial_coordinate"] = {
                "ra_hours": ra_j2000_hours,
                "dec_degrees": dec_j2000_degrees,
            }

        ra_apparent_hours = mount.get("ra_apparent_hours")
        dec_apparent_degrees = mount.get("dec_apparent_degs")
        if ra_apparent_hours is not None and dec_apparent_degrees is not None:
            data["mount.apparent_equatorial_coordinate"] = {
                "ra_hours": ra_apparent_hours,
                "dec_degrees": dec_apparent_degrees,
            }

        target_ra_j2000_hours = mount.get("target_ra_j2000_hours")
        target_dec_j2000_degrees = mount.get("target_dec_j2000_degs")
        if target_ra_j2000_hours is not None and target_dec_j2000_degrees is not None:
            data["mount.target_j2000_equatorial_coordinate"] = {
                "ra_hours": target_ra_j2000_hours,
                "dec_degrees": target_dec_j2000_degrees,
            }

        target_ra_apparent_hours = mount.get("target_ra_apparent_hours")
        target_dec_apparent_degrees = mount.get("target_dec_apparent_degs")
        if (
            target_ra_apparent_hours is not None
            and target_dec_apparent_degrees is not None
        ):
            data["mount.target_apparent_equatorial_coordinate"] = {
                "ra_hours": target_ra_apparent_hours,
                "dec_degrees": target_dec_apparent_degrees,
            }

        altitude_degrees = mount.get("altitude_degs")
        azimuth_degrees = mount.get("azimuth_degs")
        if altitude_degrees is not None and azimuth_degrees is not None:
            data["mount.horizontal_coordinate"] = {
                "altitude_degrees": altitude_degrees,
                "azimuth_degrees": azimuth_degrees,
            }

        return data

    @field_validator("JD", mode="before")
    @classmethod
    def parse_julian_date(cls, value: Any):
        if value is None:
            return None

        return parse_float_safely(value)

    @field_validator("utc", mode="before")
    @classmethod
    def parse_utc(cls, value: Any) -> Optional[datetime]:
        if value is None:
            return None

        # Coerce the str to datetime or accept datetime as-is:
        try:
            dt = value if isinstance(value, datetime) else datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid ISO datetime for utc field: {value!r}")

        # If the datetime is naïve, treat as UTC; then normalize any tz → UTC:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)

    @field_validator("is_slewing", "is_connected", "is_tracking", mode="before")
    @classmethod
    def parse_boolean(cls, value: Any):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.lower() == "true"

        return bool(value)

    @field_validator(
        "j2000_equatorial_coordinate",
        "apparent_equatorial_coordinate",
        "target_j2000_equatorial_coordinate",
        "target_apparent_equatorial_coordinate",
        mode="before",
    )
    @classmethod
    def parse_equatorial_coordinate(cls, value: Any):
        if not value:
            return None

        ra_hours = value.get("ra_hours")
        dec_degrees = value.get("dec_degrees")
        if ra_hours is None or dec_degrees is None:
            return None

        eq = EquatorialCoordinate(
            ra=parse_float_safely(ra_hours) * 15.0,
            dec=parse_float_safely(dec_degrees),
        )

        return is_equatorial_coordinate(eq)

    @field_validator("horizontal_coordinate", mode="before")
    @classmethod
    def parse_horizontal_coordinate(cls, value: Any):
        if not value:
            return None

        altitude = value.get("altitude_degrees")

        azimuth = value.get("azimuth_degrees")

        if altitude is None or azimuth is None:
            return None

        hz = HorizontalCoordinate(
            alt=parse_float_safely(altitude),
            az=parse_float_safely(azimuth),
        )

        return is_horizontal_coordinate(hz)


# **************************************************************************************
