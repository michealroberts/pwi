![pypi](https://img.shields.io/pypi/v/pwi.svg)
![versions](https://img.shields.io/pypi/pyversions/pwi.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![pwi/test](https://github.com/michealroberts/pwi/actions/workflows/test.yml/badge.svg)](https://github.com/michealroberts/pwi/actions/workflows/test.yml)

# PlaneWave Interface

Modern, type-safe, zero-dependency python library for controlling PlaneWave devices through the PWI4 HTTP interface.

## Installation

```bash
uv add pwi
```

or

using your preferred environment / package manager of choice, e.g., `poetry`, `conda` or `pip`:

```bash
pip install pwi
```

```bash
poetry add pwi
```

```bash
conda install pwi
```

## Usage

```python
from pwi import (
    BaseMountAlignmentMode,
    PlaneWaveHTTPXClient,
    PlaneWaveMountDeviceInterface,
    PlaneWaveMountDeviceParameters,
)

# Create a new PlaneWave HTTPX client:
client = PlaneWaveHTTPXClient(host="localhost", port=8220)

# Define the parameters for the PlaneWave Mount device:
params: PlaneWaveMountDeviceParameters = PlaneWaveMountDeviceParameters(
    name="PlaneWave L350 Alt-Az Mount",
    description="PlaneWave Mount Interface (HTTP)",
    alignment=BaseMountAlignmentMode.ALT_AZ,
    latitude=33.87047,
    longitude=-118.24708,
    elevation=0.0,
    did="0", # Device ID
    vid="",  # Vendor ID
    pid="",  # Product ID
)

# Create a new PlaneWave Mount device interface:
mount = PlaneWaveMountDeviceInterface(
    id=0,
    params=params,
    client=client,
)

# Initialise the mount:
mount.initialise()

# Get the current status of the mount:
status = mount.get_status()

...
```

As the pwi instance is fully typed, you can use your IDE's autocompletion to see all the available methods and properties.

We have also provided further usage examples in the [examples](./examples) directory.

## Milestones

- [X] Type-safe modern 3.6+ Python
- [X] Fully unit tested
- [X] Simpler API (modelled around the ASCOM Alpaca API)
- [X] Integration testing with HIL testing (hardware-in-the-loop)
- [X] Zero-external dependencies (no numpy, astropy etc for portability)
- [X] Example API usage
- [X] Fully supported PlaneWave Mount operations
- [ ] Fully supported PlaneWave Focuser operations
- [ ] Fully supported PlaneWave Rotator operations
- [X] Fully seasoned recipes for usage with numpy, astropy et al.
- [ ] ASCOM Alpaca APIs w/Fast API

---

### Disclaimer

This project is not affiliated with PlaneWave Instruments or observable.space in any way. It is a community-driven project. All trademarks and logos are the property of their respective owners. The PWI4 software is the property of PlaneWave Instruments.

### License

This project is licensed under the terms of the MIT license.
