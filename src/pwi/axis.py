# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# **************************************************************************************


class PlaneWaveMountDeviceInterfaceAxis(BaseModel):
    # Whether the axis is currently enabled:
    is_enabled: Optional[bool] = Field(None, alias="mount.axis.is_enabled")

    # RMS error (in arcseconds):
    rms_error: Optional[float] = Field(None, alias="mount.axis.rms_error_arcsec")

    # Distance to target (in arcseconds):
    distance_to_target: Optional[float] = Field(
        None, alias="mount.axis.dist_to_target_arcsec"
    )

    # Servo error (in arcseconds):
    servo_error: Optional[float] = Field(None, alias="mount.axis.servo_error_arcsec")

    # Minimum mechanical position (in degrees):
    minimum_mechanical_position: Optional[float] = Field(
        None, alias="mount.axis.min_mech_position_degs"
    )

    # Maximum mechanical position (in degrees):
    maximum_mechanical_position: Optional[float] = Field(
        None, alias="mount.axis.max_mech_position_degs"
    )

    # Target mechanical position (in degrees):
    target_mechanical_position: Optional[float] = Field(
        None, alias="mount.axis.target_mech_position_degs"
    )

    # Current mechanical position (in degrees):
    mechanical_position: Optional[float] = Field(None, alias="mount.axis.position_degs")

    # Timestamp of the last mechanical position update:
    last_mechanical_position_datetime: Optional[datetime] = Field(
        None, alias="mount.axis.position_timestamp"
    )

    # Maximum velocity (degrees per second):
    maximum_velocity: Optional[float] = Field(
        None, alias="mount.axis.max_velocity_degs_per_sec"
    )

    # Setpoint velocity (degrees per second):
    setpoint_velocity: Optional[float] = Field(
        None, alias="mount.axis.setpoint_velocity_degs_per_sec"
    )

    # Measured velocity (degrees per second):
    measured_velocity: Optional[float] = Field(
        None, alias="mount.axis.measured_velocity_degs_per_sec"
    )

    # Acceleration (degrees per second squared):
    acceleration: Optional[float] = Field(
        None, alias="mount.axis.acceleration_degs_per_sec_sqr"
    )

    # Measured current (amps):
    measured_current_amps: Optional[float] = Field(
        None, alias="mount.axis.measured_current_amps"
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_and_merge_axis(cls, data: Any):
        if not isinstance(data, dict):
            return data

        axis_number = data.get("axis_number", 0)

        axis_key = f"axis{axis_number}"

        axis_data = data.get("mount", {}).get(axis_key, {})

        for key, value in axis_data.items():
            data[f"mount.axis.{key}"] = value

        return data

    @field_validator("is_enabled", mode="before")
    @classmethod
    def parse_boolean(cls, value: Any):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.lower() == "true"

        return bool(value)

    @field_validator("last_mechanical_position_datetime", mode="before")
    @classmethod
    def parse_datetime(cls, value: Any):
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return None


# **************************************************************************************
