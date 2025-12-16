"""Scietex ftmONE."""

from scietex.hal.serial.utilities.numeric import ByteOrder, combine_32bit

from ..base.data import Material, OutCTRLMode, PwmCTRLMode, FTMParameters
from ..base.rs485 import RS485GatedFTM

# pylint: disable=duplicate-code
FREQUENCY_SCALE = 100
THICKNESS_SCALE = 100
THICKNESS_STD_SCALE = 100
TARGET_THICKNESS_SCALE = 10
RATE_SCALE = 100
DENSITY_SCALE = 1000
Z_RATIO_SCALE = 1000
SCALE_FACTOR_SCALE = 100
CTRL_PWM_VALUE_SCALE = 100


# pylint: disable=too-many-public-methods
class FtmOne(RS485GatedFTM):
    """Scietex ftmONE RS485 driver."""

    async def get_vendor(self) -> str:
        response = await self.read_registers(1000, 10, holding=False)
        if response is not None:
            return bytes(response).decode()
        return ""

    async def get_product_name(self) -> str:
        response = await self.read_registers(1010, 20, holding=False)
        if response is not None:
            return bytes(response).decode()
        return ""

    async def get_version(self) -> str:
        response = await self.read_registers(1030, 3, holding=False)
        if response is not None:
            return f"{response[0]:d}.{response[1]:d}.{response[2]:d}"
        return ""

    async def get_serial_number(self) -> str:
        response = await self.read_two_registers_int(
            1033, holding=False, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return f"{response:d}"
        return ""

    async def check_magick_code(self) -> bool:
        """Input register 1035 must contain constant value 7."""
        response = await self.read_register(1035, holding=False, signed=False)
        if response is not None:
            return response == 7
        return False

    async def get_mcu_frequency(self) -> int:
        response = await self.read_two_registers_int(2000, byteorder=ByteOrder.BIG_ENDIAN)
        if response is not None:
            return response
        return 0

    async def get_gate_prescaler_count(self) -> dict[str, int]:
        """Get clock prescaler and max count."""
        response = await self.read_registers(2002, 2)
        if response is not None:
            return {"prescaler": response[0], "count": response[1]}
        return {"prescaler": 0, "count": 0}

    async def set_gate_prescaler_count(self, params: dict[str, int]) -> dict[str, int]:
        """Set clock prescaler and max count."""
        values = [int(round(params["prescaler"])), int(round(params["count"]))]
        response = await self.write_registers(2002, values=values, signed=False)
        if response is not None:
            return {"prescaler": response[0], "count": response[1]}
        return {"prescaler": 0, "count": 0}

    async def get_gate_prescaler(self) -> int:
        """Get clock prescaler."""
        response = await self.read_register(2002, signed=False)
        if response is not None:
            return response
        return 0

    async def set_gate_prescaler(self, prescaler: int) -> int:
        """Set clock prescaler."""
        response = await self.write_register(2002, value=prescaler, signed=False)
        if response is not None:
            return response
        return 0

    async def get_gate_count(self) -> int:
        """Get clock max count."""
        response = await self.read_register(2003, signed=False)
        if response is not None:
            return response
        return 0

    async def set_gate_count(self, prescaler: int) -> int:
        """Set clock max count."""
        response = await self.write_register(2003, value=prescaler, signed=False)
        if response is not None:
            return response
        return 0

    async def get_gate_time(self) -> float:
        response = await self.read_registers(2000, count=4, signed=False)
        if response is not None:
            mcu_frequency = combine_32bit(response[0], response[1], byteorder=ByteOrder.BIG_ENDIAN)
            prescaler = response[2]
            count = response[3]
            gate_freq = mcu_frequency / prescaler
            return count / gate_freq * 1000
        return 0

    async def set_gate_time(self, gate_time_ms: float) -> float:
        mcu_frequency = await self.get_mcu_frequency()
        if mcu_frequency == 0:
            return 0.0
        if gate_time_ms < 10:
            time_ms = 10.0
        elif gate_time_ms > 32000:
            time_ms = 32000.0
        else:
            time_ms = gate_time_ms

        if time_ms <= 64:
            prescaler = mcu_frequency / 1e6
            count = time_ms * 1000
        elif time_ms <= 640:
            prescaler = mcu_frequency / 1e5
            count = time_ms * 100
        elif time_ms <= 6400:
            prescaler = mcu_frequency / 1e4
            count = time_ms * 10
        else:
            prescaler = mcu_frequency / 1e4 * 5
            count = time_ms * 2
        gate_params = await self.set_gate_prescaler_count(
            {"prescaler": int(round(prescaler)), "count": int(round(count))}
        )
        if gate_params is not None:
            gate_freq = mcu_frequency / gate_params["prescaler"]
            return gate_params["count"] / gate_freq * 1000
        return 0.0

    async def get_counter(self) -> int:
        response = await self.read_two_registers_int(2006, byteorder=ByteOrder.BIG_ENDIAN)
        if response is not None:
            return response
        return 0

    async def get_frequency_instant(self) -> float:
        gate_time = await self.get_gate_time()
        counter = await self.get_counter()
        if gate_time != 0:
            return counter / gate_time
        return 0

    async def get_averaging(self) -> int:
        response = await self.read_register(2023)
        if response is not None:
            return response
        return 0

    async def set_averaging(self, averaging_window: int) -> int:
        response = await self.write_register(2023, averaging_window)
        if response is not None:
            return response
        return 0

    async def get_averaging_progress(self) -> int:
        response = await self.read_register(2024)
        if response is not None:
            return response
        return 0

    async def get_frequency(self) -> float:
        response = await self.read_two_registers_float(
            2008, factor=FREQUENCY_SCALE, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0.0

    async def get_frequency_std(self) -> float:
        response = await self.read_two_registers_float(
            2010, factor=FREQUENCY_SCALE, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0.0

    async def get_thickness(self) -> float:
        response = await self.read_two_registers_float(
            2012, factor=THICKNESS_SCALE, signed=True, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0.0

    async def get_thickness_std(self) -> float:
        response = await self.read_two_registers_float(
            2014, factor=THICKNESS_STD_SCALE, signed=False, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0.0

    async def get_rate(self) -> float:
        response = await self.read_two_registers_float(
            2016, factor=RATE_SCALE, signed=True, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0.0

    async def get_material_density(self) -> float:
        response = await self.read_register_float(2018, factor=DENSITY_SCALE, signed=False)
        if response is not None:
            return response
        return 0.0

    async def set_material_density(self, density: float) -> float:
        response = await self.write_register_float(
            2018, density, factor=DENSITY_SCALE, signed=False
        )
        if response is not None:
            return response
        return 0.0

    async def get_material_z_ratio(self) -> float:
        response = await self.read_register_float(2019, factor=Z_RATIO_SCALE, signed=False)
        if response is not None:
            return response
        return 0.0

    async def set_material_z_ratio(self, z_ratio: float) -> float:
        response = await self.write_register_float(
            2019, z_ratio, factor=Z_RATIO_SCALE, signed=False
        )
        if response is not None:
            return response
        return 0.0

    async def get_material(self) -> Material:
        response = await self.read_registers(2018, count=2)
        if response is not None:
            return Material(
                density=response[0] / DENSITY_SCALE, z_ratio=response[1] / Z_RATIO_SCALE
            )
        return Material(density=0, z_ratio=0)

    async def set_material(self, material: Material) -> Material:
        response = await self.write_registers(
            2018,
            [
                int(round(material.density * DENSITY_SCALE)),
                int(round(material.z_ratio * Z_RATIO_SCALE)),
            ],
        )
        if response is not None:
            return Material(
                density=response[0] / DENSITY_SCALE, z_ratio=response[1] / Z_RATIO_SCALE
            )
        return Material(density=0, z_ratio=0)

    async def get_ftm_scale(self) -> float:
        response = await self.read_register_float(2020, factor=SCALE_FACTOR_SCALE, signed=False)
        if response is not None:
            return response
        return 0.0

    async def set_ftm_scale(self, scale: float) -> float:
        response = await self.write_register_float(
            2020, scale, factor=SCALE_FACTOR_SCALE, signed=False
        )
        if response is not None:
            return response
        return 0.0

    async def get_target_thickness(self) -> float:
        response = await self.read_two_registers_float(
            2021, factor=TARGET_THICKNESS_SCALE, signed=False
        )
        if response is not None:
            return response
        return 0.0

    async def set_target_thickness(self, target: float) -> float:
        response = await self.write_two_registers_float(
            2021, target, factor=TARGET_THICKNESS_SCALE, signed=False
        )
        if response is not None:
            return response
        return 0.0

    async def get_ctrl_out_mode(self) -> OutCTRLMode:
        response = await self.read_register(2026)
        if response is not None:
            return OutCTRLMode(response)
        return OutCTRLMode.DISABLED

    async def set_ctrl_out_mode(self, mode: OutCTRLMode) -> OutCTRLMode:
        response = await self.write_register(2026, mode.value)
        if response is not None:
            return OutCTRLMode(response)
        return OutCTRLMode.DISABLED

    async def get_ctrl_out_value(self) -> bool:
        response = await self.read_register(2027)
        if response is not None:
            return bool(response)
        return False

    async def set_ctrl_out_value(self, value: bool) -> bool:
        response = await self.write_register(2027, int(bool(value)))
        if response is not None:
            return bool(response)
        return False

    async def get_ctrl_pwm_mode(self) -> PwmCTRLMode:
        response = await self.read_register(2028)
        if response is not None:
            return PwmCTRLMode(response)
        return PwmCTRLMode.DISABLED

    async def set_ctrl_pwm_mode(self, mode: PwmCTRLMode) -> PwmCTRLMode:
        response = await self.write_register(2028, mode.value)
        if response is not None:
            return PwmCTRLMode(response)
        return PwmCTRLMode.DISABLED

    async def get_ctrl_pwm_value(self) -> float:
        response = await self.read_register(2029)
        if response is not None:
            return response / CTRL_PWM_VALUE_SCALE
        return 0.0

    async def set_ctrl_pwm_value(self, value: float) -> float:
        response = await self.write_register(2029, int(round(value * CTRL_PWM_VALUE_SCALE)))
        if response is not None:
            return response
        return 0.0

    async def get_ctrl_pwm_scale(self) -> int:
        response = await self.read_two_registers_int(
            2030, signed=False, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0

    async def set_ctrl_pwm_scale(self, scale: int) -> int:
        response = await self.write_two_registers(
            2030, scale, signed=False, byteorder=ByteOrder.BIG_ENDIAN
        )
        if response is not None:
            return response
        return 0

    async def get_address(self) -> int:
        response = await self.read_register(2032)
        if response is not None:
            return response
        return 0

    async def set_address(self, address: int) -> int:
        new_address = max(1, min(address, 247))
        await self.write_register(2032, new_address)
        self.address = new_address
        response = await self.get_address()
        if response is not None and response > 0:
            self.address = response
            return response
        return 0

    async def get_baudrate(self) -> int:
        response = await self.read_register(2033)
        if response is not None:
            return response
        return 0

    async def set_baudrate(self, baudrate: int) -> int:
        if baudrate <= 9600:
            new_baudrate = 9600
        elif baudrate <= 14400:
            new_baudrate = 14400
        elif baudrate <= 19200:
            new_baudrate = 19200
        elif baudrate <= 38400:
            new_baudrate = 38400
        elif baudrate <= 57600:
            new_baudrate = 57600
        else:
            new_baudrate = 115200
        response = await self.write_register(2033, new_baudrate)
        new_con_params = self.con_params
        new_con_params.baudrate = new_baudrate
        self.con_params = new_con_params
        if response is not None:
            return response
        response = await self.read_register(2033)
        if response is not None:
            return response
        return 0

    async def get_running_state(self) -> bool:
        response = self.read_register(2004)
        if response is not None:
            return bool(response)
        return False

    async def set_running_state(self, running: bool) -> bool:
        response = await self.write_register(2004, int(bool(running)))
        if response is not None:
            return bool(response)
        return False

    async def reset_thickness(self):
        await self.write_register(2005, 1)

    async def start_measurement(self, reset: bool = True) -> bool:
        response = await self.write_registers(2004, [1, int(bool(reset))])
        if response is not None:
            return bool(response[0])
        return False

    async def read_parameters(self) -> FTMParameters:
        # pylint: disable=duplicate-code
        response = await self.read_registers(2004, count=21)
        if response is not None:
            running = bool(response[0])
            frequency = (
                combine_32bit(response[4], response[5], byteorder=ByteOrder.BIG_ENDIAN)
                / FREQUENCY_SCALE
            )
            frequency_std = (
                combine_32bit(response[6], response[7], byteorder=ByteOrder.BIG_ENDIAN)
                / FREQUENCY_SCALE
            )
            thickness = (
                combine_32bit(response[8], response[9], byteorder=ByteOrder.BIG_ENDIAN)
                / THICKNESS_SCALE
            )
            thickness_std = (
                combine_32bit(response[10], response[11], byteorder=ByteOrder.BIG_ENDIAN)
                / THICKNESS_STD_SCALE
            )
            rate = (
                combine_32bit(response[12], response[13], byteorder=ByteOrder.BIG_ENDIAN)
                / RATE_SCALE
            )
            material_density = response[14] / DENSITY_SCALE
            material_z_ratio = response[15] / Z_RATIO_SCALE
            scale = response[16] / SCALE_FACTOR_SCALE
            target = (
                combine_32bit(response[17], response[18], byteorder=ByteOrder.BIG_ENDIAN)
                / TARGET_THICKNESS_SCALE
            )
            averaging_window = response[19]
            averaging_progress = response[20]

            parameters = FTMParameters(
                frequency=frequency,
                frequency_std=frequency_std,
                averaging_window=averaging_window,
                averaging_progress=averaging_progress,
                rate=rate,
                thickness=thickness,
                thickness_std=thickness_std,
                target=target,
                material_density=material_density,
                material_z_ratio=material_z_ratio,
                running=running,
                scale=scale,
            )
        else:
            parameters = FTMParameters()
        return parameters
