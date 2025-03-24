# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from typing import Any, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator

# **************************************************************************************


class PlanewaveDeviceInterfaceVersion(BaseModel):
    version: Tuple[int, int, int] = Field((0, 0, 0), alias="pwi4.version")

    @model_validator(mode="before")
    @classmethod
    def flatten_and_merge_pwi4(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        pwi4 = data.get("pwi4", {})

        data["pwi4.version"] = pwi4.get("version", "<unknown>")

        if "version_field" in pwi4:
            data["pwi4.version"] = pwi4["version_field"]

        return data

    @field_validator("version", mode="before")
    @classmethod
    def parse_version(cls, value: Any) -> Tuple[int, int, int]:
        parts = []

        # If the value is a list or tuple, convert it to a list of integers:
        if isinstance(value, (list, tuple)):
            parts = [int(item) for item in value]

        # If the value is a string, split it into parts:
        if isinstance(value, str):
            parts = [int(part) for part in value.split(".")]

        # If there are less than 4 parts, pad the list with zeros to 4 parts:
        while len(parts) < 4:
            parts.append(0)

        # If there are more than 4 parts, truncate the list to 4 parts:
        if len(parts) > 4:
            parts = parts[:4]

        return (parts[0], parts[1], parts[2])


# **************************************************************************************
