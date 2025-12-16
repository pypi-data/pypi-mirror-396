"""CYKY TM106B FTM."""

from typing import Optional
from logging import Logger

from scietex.hal.serial import ModbusSerialConnectionConfig
from scietex.hal.serial.utilities.numeric import ByteOrder, combine_32bit

from ..base.rs485 import RS485GatedFTM
from ..base.data import PwmCTRLMode, FTMParameters


# pylint: disable=too-many-public-methods
class TM106B(RS485GatedFTM):
    """TM106B RS485 driver."""

    def __init__(
        self,
        con_params: ModbusSerialConnectionConfig,
        address: int = 1,
        label: str = "FTM",
        logger: Optional[Logger] = None,
        **kwargs,
    ):

        # pylint: disable=too-many-arguments, duplicate-code
        con_params.framer = "ASCII"
        super().__init__(
            con_params=con_params,
            address=address,
            label=label,
            logger=logger,
            **kwargs,
        )

    async def get_vendor(self) -> str:
        return "CYKY"

    async def get_product_name(self) -> str:
        return "TM106B"

    async def get_version(self) -> str:
        version = await self.read_register_float(0, factor=100)
        if version is None:
            self.logger.error("%s: can not read register", self.label)
            return ""
        return f"{version:.2f}"

    # CON parameters

    @staticmethod
    def _parse_con(con: int) -> tuple[int, int, int]:
        """
        Parse CON parameters from register data.
        a: 0-11 gate time = a * 100ms
        b: Analog output (b=0 stop, b=1 auto, b=2 manual)
        c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
        """
        coded_str = f"{con:04x}"
        a = int(coded_str[0], 16)
        b = int(coded_str[1], 16)
        c = int(coded_str[2], 16)
        return a, b, c

    async def get_con(self) -> tuple[int, int, int]:
        """
        Get and parse CON parameters from register data.
        a: 0-11 gate time = a * 100ms
        b: Analog output (b=0 stop, b=1 auto, b=2 manual)
        c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
        """
        response = await self.read_register(8)
        if response is not None:
            a, b, c = self._parse_con(response)
            self.logger.debug(
                "%s: t: %d ms, PWM mode: %d, Rate mode: %d", self.label, a * 100, b, c
            )
            return a, b, c
        self.logger.error("%s: can not read register.", self.label)
        return 0, 0, 0

    async def set_con(self, a: int = 1, b: int = 1, c: int = 1) -> None:
        """
        Set CON values to register.
        a: 0-11 gate time = a * 100ms
        b: Analog output (b=0 stop, b=1 auto, b=2 manual)
        c: rate calculation algorythm (c=0 immediate, c=1 weighted, c=2 10-average)
        """
        a = int(round(max(1, min(a, 10))))
        b = int(round(max(0, min(b, 2))))
        c = int(round(max(0, min(c, 2))))
        value = int(f"0x{a:x}{b:x}{c:x}0", 16)
        await self.write_register(8, value)

    async def get_gate_time(self) -> float:
        a, _, _ = await self.get_con()
        return 100.0 * a

    async def set_gate_time(self, gate_time_ms: float) -> float:
        _, b, c = await self.get_con()
        a_new = int(round(gate_time_ms / 100))
        await self.set_con(a_new, b, c)
        return await self.get_gate_time()

    @staticmethod
    def _parse_averaging(c: int) -> int:
        """Convert CON code for averaging into actual averaging window size."""
        if c in (0, 1):
            return 1
        if c == 2:
            return 10
        return 0

    async def get_averaging(self) -> int:
        _, _, c = await self.get_con()
        return self._parse_averaging(c)

    async def set_averaging(self, averaging_window: int) -> int:
        a, b, _ = await self.get_con()
        c = 1
        if averaging_window == 0:
            c = 0
        elif averaging_window >= 10:
            c = 2
        await self.set_con(a, b, c)
        return await self.get_averaging()

    async def get_frequency_instant(self) -> float:
        frequency = await self.read_two_registers_float(
            5, factor=100, byteorder=ByteOrder.BIG_ENDIAN
        )
        if isinstance(frequency, float):
            return frequency
        self.logger.error("%s: can not read frequency data.", self.label)
        return 0.0

    async def get_counter(self) -> int:
        frequency = await self.get_frequency_instant()
        gate_time = await self.get_gate_time() / 1000  # in convert to seconds
        return int(round(frequency * gate_time))

    async def get_thickness(self) -> float:
        thickness = await self.read_two_registers_float(
            1, factor=100, byteorder=ByteOrder.BIG_ENDIAN
        )
        if isinstance(thickness, float):
            return thickness
        self.logger.error("%s: can not read thickness data.", self.label)
        return 0.0

    async def get_rate(self) -> float:
        rate = await self.read_two_registers_float(3, factor=100, byteorder=ByteOrder.BIG_ENDIAN)
        if isinstance(rate, float):
            return rate
        self.logger.error("%s: can not read rate data.", self.label)
        return 0.0

    async def get_material_density(self) -> float:
        density = await self.read_register_float(10, factor=100)
        if isinstance(density, float):
            return density
        self.logger.error("%s: can not read density data.", self.label)
        return 0.0

    async def set_material_density(self, density: float) -> float:
        await self.write_register_float(10, max(0.4, min(density, 99.99)), factor=100)
        return await self.get_material_density()

    async def get_material_z_ratio(self) -> float:
        z_ratio = await self.read_register_float(11, factor=1000)
        if isinstance(z_ratio, float):
            return z_ratio
        self.logger.error("%s: can not read Z-ratio data.", self.label)
        return 0.0

    async def set_material_z_ratio(self, z_ratio: float) -> float:
        await self.write_register_float(11, max(0.1, min(z_ratio, 9.999)), factor=1000)
        return await self.get_material_z_ratio()

    async def get_ftm_scale(self) -> float:
        scale = await self.read_register_float(12, factor=1000)
        if isinstance(scale, float):
            return scale
        self.logger.error("%s: can not read scale data.", self.label)
        return 0.0

    async def set_ftm_scale(self, scale: float) -> float:
        await self.write_register_float(11, max(0.001, min(scale, 65.535)), factor=1000)
        return await self.get_ftm_scale()

    async def get_target_thickness(self) -> float:
        return 0.0

    async def set_target_thickness(self, target: float) -> float:
        return await self.get_target_thickness()

    # PWM parameters

    async def get_ctrl_pwm_mode(self) -> PwmCTRLMode:
        _, b, _ = await self.get_con()
        if b == 0:
            return PwmCTRLMode.DISABLED
        if b == 1:
            return PwmCTRLMode.ABSOLUTE
        if b == 2:
            return PwmCTRLMode.MANUAL
        return PwmCTRLMode.DISABLED

    async def set_ctrl_pwm_mode(self, mode: PwmCTRLMode) -> PwmCTRLMode:
        a, _, c = await self.get_con()
        b = 0
        if mode == PwmCTRLMode.MANUAL:
            b = 2
        elif mode == PwmCTRLMode.ABSOLUTE:
            b = 1
        await self.set_con(a, b, c)
        return await self.get_ctrl_pwm_mode()

    async def get_ctrl_pwm_value(self) -> float:
        pwm = await self.read_register_float(7, factor=100)
        if isinstance(pwm, float):
            return pwm
        self.logger.error("%s: Can not get pwm value.", self.label)
        return 0.0

    async def set_ctrl_pwm_value(self, value: float) -> float:
        await self.write_register_float(7, max(0.0, min(value, 99.99)), factor=100)
        return await self.get_ctrl_pwm_value()

    async def get_ctrl_pwm_scale(self) -> int:
        scale = await self.read_register(13)
        if isinstance(scale, int):
            return scale
        self.logger.error("%s: Can not get pwm scale value.", self.label)
        return 0

    async def set_ctrl_pwm_scale(self, scale: int) -> int:
        await self.write_register(13, max(1, min(scale, 9999)))
        return await self.get_ctrl_pwm_scale()

    # RUN parameters

    @staticmethod
    def _parse_run_code(code: int) -> tuple[int, int]:
        """
        Parse measurement run status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stopped, x=1 started; y=0 no thickness reset, y=1 thickness reset.
        """
        coded_str: str = f"{code:04x}"
        y = int(coded_str[2], 16)
        x = int(coded_str[3], 16)
        return x, y

    async def get_run(self) -> tuple[int, int]:
        """
        Get and parse measurement run status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stopped, x=1 started; y=0 no thickness reset, y=1 thickness reset.
        """
        response = await self.read_register(9)
        if response is not None:
            x, y = self._parse_run_code(response)
            self.logger.debug("X: %d, Y: %d", x, y)
            return x, y
        return 0, 0

    async def set_run(self, x: int = 0, y: int = 0) -> None:
        """
        Parse running status.
        (x, y) X: running status, Y: film thickness measurement reset.
        x=0 stop, x=1 start; y=0 no reset, y=1 reset.
        """
        x = max(0, min(x, 1))
        y = max(0, min(y, 1))
        data = int(f"0x00{int(y):x}{int(x):x}", 16)
        await self.write_register(9, data)

    async def reset_thickness(self) -> None:
        running, _ = await self.get_run()
        await self.set_run(running, 1)

    async def get_running_state(self) -> bool:
        running, _ = await self.get_run()
        return bool(running)

    async def set_running_state(self, running: bool) -> bool:
        await self.set_run(int(bool(running)), 0)
        return await self.get_running_state()

    async def start_measurement(self, reset: bool = True) -> bool:
        await self.set_run(1, int(bool(reset)))
        return await self.get_running_state()

    # RS485 address and baudrate

    async def get_address(self) -> int:
        address = await self.read_register(14)
        if isinstance(address, int):
            return address
        self.logger.error("%s: can not read address data.", self.label)
        return 0

    async def set_address(self, address: int) -> int:
        new_address = max(1, min(address, 254))
        await self.write_register(14, new_address)
        self.address = new_address
        response = await self.get_address()
        if response is not None and response > 0:
            return response
        return 0

    @staticmethod
    def _code_to_baudrate(code: int) -> int:
        """get baudrate value for a given register code (0-5)"""
        baudrate = 0
        code = int(f"{code:04x}"[0], base=10)
        if code == 0:
            baudrate = 1200
        elif code == 1:
            baudrate = 2400
        elif code == 2:
            baudrate = 4800
        elif code == 3:
            baudrate = 9600
        elif code == 4:
            baudrate = 19200
        elif code == 5:
            baudrate = 38400
        return baudrate

    @staticmethod
    def _baudrate_to_code(baudrate: int) -> int:
        """Get a register code (0-5) for a given baudrate value"""
        code: int = 3  # default code is 3, which is 9600
        if baudrate == 1200:
            code = 0
        elif baudrate == 2400:
            code = 1
        elif baudrate == 4800:
            code = 2
        elif baudrate == 9600:
            code = 3
        elif baudrate == 19200:
            code = 4
        elif baudrate == 38400:
            code = 5
        code = int(f"{code}000", base=16)
        return code

    async def get_baudrate(self) -> int:
        baudrate_code = await self.read_register(15)
        if isinstance(baudrate_code, int):
            return self._code_to_baudrate(baudrate_code)
        return 0

    async def set_baudrate(self, baudrate: int) -> int:
        if baudrate <= 1200:
            new_baudrate = 1200
        elif baudrate <= 2400:
            new_baudrate = 2400
        elif baudrate <= 4800:
            new_baudrate = 4800
        elif baudrate <= 9600:
            new_baudrate = 9600
        elif baudrate <= 19200:
            new_baudrate = 19200
        else:
            new_baudrate = 38400
        await self.write_register(15, self._baudrate_to_code(new_baudrate))
        new_con_params = self.con_params
        new_con_params.baudrate = new_baudrate
        self.con_params = new_con_params
        return await self.get_baudrate()

    # Read FTM state in a single request

    async def read_parameters(self) -> FTMParameters:
        reg_data = await self.read_registers(1, count=12)
        if reg_data is not None:
            thickness = (
                combine_32bit(reg_data[0], reg_data[1], byteorder=ByteOrder.BIG_ENDIAN) / 100.0
            )
            rate = combine_32bit(reg_data[2], reg_data[3], byteorder=ByteOrder.BIG_ENDIAN) / 100.0
            frequency = (
                combine_32bit(reg_data[4], reg_data[5], byteorder=ByteOrder.BIG_ENDIAN) / 100.0
            )
            _, _, c = self._parse_con(reg_data[7])
            averaging_window = self._parse_averaging(c)
            x, _ = self._parse_run_code(reg_data[8])
            running = bool(x)
            material_density = reg_data[9] / 100.0
            material_z_ratio = reg_data[10] / 1000.0
            scale = reg_data[11] / 1000.0
            parameters = FTMParameters(
                frequency=frequency,
                frequency_std=0.0,
                averaging_window=averaging_window,
                averaging_progress=averaging_window,
                rate=rate,
                thickness=thickness,
                thickness_std=0.0,
                target=0,
                material_density=material_density,
                material_z_ratio=material_z_ratio,
                running=running,
                scale=scale,
            )
        else:
            parameters = FTMParameters()
        return parameters
