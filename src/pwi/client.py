# **************************************************************************************

# @package        pwi
# @license        MIT License Copyright (c) 2025 Michael J. Roberts

# **************************************************************************************

from httpx import Client, Timeout

# **************************************************************************************


class PlanewaveHTTPXMountClient:
    def __init__(self, host: str = "localhost", port: int = 8220, timeout: float = 3.0):
        self._client = Client(
            base_url=f"http://{host}:{port}",
            timeout=Timeout(timeout, connect=timeout, read=timeout, write=timeout),
        )


# **************************************************************************************
