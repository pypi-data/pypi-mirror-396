"""USB-CDC driver for Scietex ftmONE."""

import asyncio
from typing import Optional
from logging import Logger
import json

from scietex.hal.serial import SerialConnectionConfig
from scietex.hal.serial.utilities.serial_port_finder import find_stm32_cdc

from ..base.serial import SerialGatedFTM, manage_connection
from ..base.data import QCMError, Material, OutCTRLMode
from .utils import baudrate_check, address_check


def find_ftm_one_usb() -> list[str]:
    """Find ftmONE USB CDC device."""
    return find_stm32_cdc()


TARGET_THICKNESS_SCALE = 10
RATE_SCALE = 100
DENSITY_SCALE = 1000
Z_RATIO_SCALE = 1000
SCALE_FACTOR_SCALE = 100


# pylint: disable=too-many-public-methods
class FtmOneUSB(SerialGatedFTM):
    """USB driver for Scietex ftmONE Film Thickness Monitor."""

    def __init__(
        self,
        con_params: SerialConnectionConfig,
        label: str = "FTM",
        logger: Optional[Logger] = None,
        keep_connection: bool = False,
    ):
        super().__init__(con_params, label, logger, keep_connection)
        self.error_codes = {
            0: QCMError(code=0, message="No error"),
            32: QCMError(code=32, message="Not implemented error"),
            128: QCMError(code=128, message="Crystal error"),
        }
        self.error_codes_com = {
            0: QCMError(code=0, message="No error"),
            1: QCMError(code=1, message="USB command error"),
            2: QCMError(code=2, message="USB connection error"),
            4: QCMError(code=4, message="MODBUS error"),
        }
        self._pin: int = 0

    @property
    def pin(self) -> int:
        """PIN code for protected data access."""
        return self._pin

    @pin.setter
    def pin(self, new_pin: int) -> None:
        self._pin = int(round(new_pin))

    # Error processing methods

    @manage_connection
    async def get_error_code(self, comm: bool = False) -> int:
        if self._connection is not None:
            command = b"e\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["e"]
        return 0

    # Device information methods

    @manage_connection
    async def get_vendor(self) -> str:
        if self._connection is not None:
            command = b"sn\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["vend"]
        return "n/d"

    @manage_connection
    async def get_product_name(self) -> str:
        if self._connection is not None:
            command = b"sn\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["prod"]
        return "n/d"

    @manage_connection
    async def get_version(self) -> str:
        if self._connection is not None:
            command = b"sn\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["v"]
        return "n/d"

    @manage_connection
    async def get_serial_number(self) -> str:
        if self._connection is not None:
            command = b"sn\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["sn"]
        return "n/d"

    @manage_connection
    async def set_serial_number(self, new_serial: int) -> str:
        """Change ftmONE serial number. Pin-code protected."""
        if self._connection is not None:
            command = b"sn:" + f"{int(round(new_serial)):d}:{self._pin:d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["sn"]
        return "n/d"

    # FTM measurement setup

    @manage_connection
    async def get_mcu_frequency(self) -> int:
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["clk"]
        return 0

    @manage_connection
    async def get_gate_time(self) -> float:
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["p"] * response["c"] / response["clk"] * 1000
        return 0.0

    @manage_connection
    async def set_gate_time(self, gate_time_ms: float) -> float:
        if self._connection is not None:
            command = b"g:" + f"{int(round(gate_time_ms)):d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["p"] * response["c"] / response["clk"] * 1000
        return 0.0

    @manage_connection
    async def get_gate_prescaler(self) -> int:
        """Get clock prescaler."""
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["p"]
        return 0

    @manage_connection
    async def set_gate_prescaler(self, prescaler: int) -> int:
        """Set clock prescaler."""
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = b"g:" + f"{int(round(prescaler)):d}:{response['c']:d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["p"]
        return 0

    @manage_connection
    async def get_gate_count(self) -> int:
        """Get clock max count."""
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["c"]
        return 0

    @manage_connection
    async def set_gate_count(self, count: int) -> int:
        """Set clock max count."""
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = b"g:" + f"{response['p']:d}:{int(round(count)):d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["c"]
        return 0

    @manage_connection
    async def get_gate_prescaler_count(self) -> dict[str, int]:
        """Get clock prescaler and max count."""
        if self._connection is not None:
            command = b"g\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return {"prescaler": response["p"], "count": response["c"]}
        return {"prescaler": 0, "count": 0}

    @manage_connection
    async def set_gate_prescaler_count(self, params: dict[str, int]) -> dict[str, int]:
        """Set clock prescaler and max count."""
        if self._connection is not None:
            command = (
                b"g:"
                + f"{int(round(params['prescaler'])):d}:{int(round(params['count'])):d}".encode()
                + b"\r\n"
            )
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return {"prescaler": response["p"], "count": response["c"]}
        return {"prescaler": 0, "count": 0}

    @manage_connection
    async def get_averaging(self) -> int:
        if self._connection is not None:
            command = b"a\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["w"]
        return 0

    @manage_connection
    async def set_averaging(self, averaging_window: int) -> int:
        if self._connection is not None:
            await asyncio.sleep(1)
            command = b"a:" + f"{int(round(averaging_window)):d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["w"]
        return 0

    # FTM frequency measurement data access methods

    @manage_connection
    async def get_counter(self) -> int:
        if self._connection is not None:
            command = b"c\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["c"]
        return 0

    @manage_connection
    async def get_frequency_instant(self) -> float:
        if self._connection is not None:
            gate_time = await self.get_gate_time()
            counter = await self.get_counter()
            return counter / gate_time * 1000
        return 0

    @manage_connection
    async def get_averaging_progress(self) -> int:
        if self._connection is not None:
            command = b"a\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["c"]
        return 0

    @manage_connection
    async def get_measurement_data(self) -> dict[str, float]:
        """Get measurement data."""
        if self._connection is not None:
            command = b"m\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return {
                "f": response["f"],
                "f_std": response["df"],
                "h": response["h"],
                "h_std": response["dh"],
                "rate": response["r"],
            }
        return {
            "f": 0,
            "f_std": 0,
            "h": 0,
            "h_std": 0,
            "rate": 0,
        }

    async def get_frequency(self) -> float:
        return (await self.get_measurement_data())["f"]

    async def get_frequency_std(self) -> float:
        return (await self.get_measurement_data())["f_std"]

    # Thickness measurement methods

    async def get_thickness(self) -> float:
        return (await self.get_measurement_data())["h"]

    async def get_thickness_std(self) -> float:
        return (await self.get_measurement_data())["h_std"]

    async def get_rate(self) -> float:
        return (await self.get_measurement_data())["rate"]

    @manage_connection
    async def get_material_density(self) -> float:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["d"] / DENSITY_SCALE
        return 0.0

    @manage_connection
    async def set_material_density(self, density: float) -> float:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = (
                b"p:"
                + f"{int(round(density * DENSITY_SCALE)):d}:".encode()
                + f"{response['z']:d}:{response['s']:d}".encode()
                + b"\r\n"
            )
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["d"] / DENSITY_SCALE
        return 0.0

    @manage_connection
    async def get_material_z_ratio(self) -> float:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["z"] / Z_RATIO_SCALE
        return 0.0

    @manage_connection
    async def set_material_z_ratio(self, z_ratio: float) -> float:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = (
                b"p:"
                + f"{response['d']:d}:".encode()
                + f"{int(round(z_ratio * Z_RATIO_SCALE)):d}:".encode()
                + f"{response['s']:d}".encode()
                + b"\r\n"
            )
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["z"] / Z_RATIO_SCALE
        return 0.0

    @manage_connection
    async def get_material(self) -> Material:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return Material(
                density=response["d"] / DENSITY_SCALE, z_ratio=response["z"] / Z_RATIO_SCALE
            )
        return Material(density=0.0, z_ratio=0.0)

    @manage_connection
    async def set_material(self, material: Material) -> Material:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            scale = f"{response['s']:d}".encode()
            density = f"{int(round(material.density * DENSITY_SCALE)):d}:".encode()
            z_ratio = f"{int(round(material.z_ratio * Z_RATIO_SCALE)):d}:".encode()
            command = b"p:" + density + z_ratio + scale + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return Material(
                density=response["d"] / DENSITY_SCALE, z_ratio=response["z"] / Z_RATIO_SCALE
            )
        return Material(density=0.0, z_ratio=0.0)

    @manage_connection
    async def get_ftm_scale(self) -> float:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["s"] / SCALE_FACTOR_SCALE
        return 0.0

    @manage_connection
    async def set_ftm_scale(self, scale: float) -> float:
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = (
                b"p:"
                + f"{response['d']:d}:{response['z']:d}:".encode()
                + f"{int(round(scale * SCALE_FACTOR_SCALE)):d}".encode()
                + b"\r\n"
            )
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["s"] / SCALE_FACTOR_SCALE
        return 0.0

    @manage_connection
    async def get_ftm_params(self) -> dict[str, float]:
        """Get FTM measurement parameters (material and scale factor)."""
        if self._connection is not None:
            command = b"p\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return {
                "density": response["d"] / DENSITY_SCALE,
                "z_ratio": response["z"] / Z_RATIO_SCALE,
                "scale": response["s"] / SCALE_FACTOR_SCALE,
            }
        return {
            "density": 0.0,
            "z_ratio": 0.0,
            "scale": 0.0,
        }

    @manage_connection
    async def set_ftm_params(self, new_params: dict[str, float]) -> dict[str, float]:
        """Set FTM measurement parameters (material and scale factor)."""
        if self._connection is not None:
            density = f"{int(round(new_params['density'] * DENSITY_SCALE)):d}:".encode()
            z_ratio = f"{int(round(new_params['z_ratio'] * Z_RATIO_SCALE)):d}:".encode()
            scale = f"{int(round(new_params['scale'] * SCALE_FACTOR_SCALE)):d}\r\n".encode()
            command = b"p:" + density + z_ratio + scale
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return {
                "density": response["d"] / DENSITY_SCALE,
                "z_ratio": response["z"] / Z_RATIO_SCALE,
                "scale": response["s"] / SCALE_FACTOR_SCALE,
            }
        return {
            "density": 0.0,
            "z_ratio": 0.0,
            "scale": 0.0,
        }

    @manage_connection
    async def get_target_thickness(self) -> float:
        if self._connection is not None:
            command = b"t\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["t"] / TARGET_THICKNESS_SCALE
        return 0.0

    @manage_connection
    async def set_target_thickness(self, target: float) -> float:
        if self._connection is not None:
            command = b"t:" + f"{int(round(target * TARGET_THICKNESS_SCALE)):d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["t"] / TARGET_THICKNESS_SCALE
        return 0.0

    @manage_connection
    async def reset_thickness(self) -> None:
        if self._connection is not None:
            command = b"r:3\r\n"
            self._connection.write(command)
            self._connection.readline()

    # CTRL OUT parameters

    @manage_connection
    async def get_ctrl_out_mode(self) -> OutCTRLMode:
        if self._connection is not None:
            command = b"o\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return OutCTRLMode(response["m"])
        return OutCTRLMode.DISABLED

    @manage_connection
    async def set_ctrl_out_mode(self, mode: OutCTRLMode) -> OutCTRLMode:
        if self._connection is not None:
            command = b"o\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = b"o:" + f"{int(round(mode.value)):d}:{response['v']:d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return OutCTRLMode(response["m"])
        return OutCTRLMode.DISABLED

    @manage_connection
    async def get_ctrl_out_value(self) -> bool:
        if self._connection is not None:
            command = b"o\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return bool(response["v"])
        return False

    @manage_connection
    async def set_ctrl_out_value(self, value: bool) -> bool:
        if self._connection is not None:
            command = b"o\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = b"o:" + f"{response['m']:d}:{int(bool(value)):d}".encode() + b"\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return bool(response["v"])
        return False

    # MEASUREMENT START/STOP

    @manage_connection
    async def get_running_state(self) -> bool:
        if self._connection is not None:
            command = b"r\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return bool(response["r"])
        return False

    @manage_connection
    async def set_running_state(self, running: bool) -> bool:
        if self._connection is not None:
            command = b"r:1\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return bool(response["r"])
        return False

    @manage_connection
    async def start_measurement(self, reset: bool = True) -> bool:
        if self._connection is not None:
            if reset:
                command = b"r:2\r\n"
            else:
                command = b"r:1\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return bool(response["r"])
        return False

    @manage_connection
    async def stop_measurement(self) -> bool:
        if self._connection is not None:
            command = b"r:0\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return bool(response["r"])
        return False

    # RS485 CON SETTINGS

    @manage_connection
    async def get_rs485_baudrate(self) -> int:
        """Get RS485 baudrate."""
        if self._connection is not None:
            command = b"b\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["b"]
        return 0

    @manage_connection
    async def set_rs485_baudrate(self, baudrate: int) -> int:
        """Set RS485 baudrate."""
        if self._connection is not None:
            command = b"b\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = (
                b"b:"
                + f"{response['a']:d}:".encode()
                + f"{int(round(baudrate_check(baudrate))):d}".encode()
                + b"\r\n"
            )
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["b"]
        return 0

    @manage_connection
    async def get_rs485_address(self) -> int:
        """Get RS485 address."""
        if self._connection is not None:
            command = b"b\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["a"]
        return 0

    @manage_connection
    async def set_rs485_address(self, address: int) -> int:
        """Set RS485 address."""
        if self._connection is not None:
            command = b"b\r\n"
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            command = (
                b"b:"
                + f"{int(round(address_check(address))):d}:".encode()
                + f"{response['b']:d}".encode()
                + b"\r\n"
            )
            self._connection.write(command)
            response = json.loads(self._connection.readline().decode().strip())
            return response["a"]
        return 0
