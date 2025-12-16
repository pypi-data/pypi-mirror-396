"""Gated Film Thickness Monitor with RS485 communication interface."""

from typing import Any

from scietex.hal.serial import RS485Client

from ...version import __version__
from .. import GatedFTM
from ..data import OutCTRLMode, PwmCTRLMode, FTMParameters, FTMStartCMD, Material


# pylint: disable=too-many-public-methods
class RS485GatedFTM(GatedFTM, RS485Client):
    """Quartz crystal gated film thickness monitor"""

    # Error processing methods

    async def get_error_code(self, comm: bool = False) -> int:
        """Read error code from the FTM"""
        code = 0
        if comm:
            self.logger.debug("%s: Communication error code %d.", self.label, code)
        else:
            self.logger.debug("%s: Error code %d.", self.label, code)
        return code

    async def clear_error(self, comm: bool = False) -> int:
        """Clear error from the FTM"""
        if comm:
            self.logger.debug("%s: Clear communication error.", self.label)
        else:
            self.logger.debug("%s: Clear error.", self.label)
        return await self.get_error_code()

    # Device information methods

    async def get_vendor(self) -> str:
        """Get QCM vendor name."""
        vendor: str = "n/d"
        self.logger.debug("%s vendor: %s", self.label, vendor)
        return vendor

    async def get_product_name(self) -> str:
        """Get QCM product name."""
        self.logger.debug("%s prod. name: %s", self.label, self.label)
        return self.label

    async def get_serial_number(self) -> str:
        """Get QCM serial number."""
        sn = "n/d"
        self.logger.debug("%s SN: %s", self.label, sn)
        return sn

    async def get_version(self) -> str:
        """get QCM firmware version"""
        self.logger.debug("%s version: %s.", self.label, __version__)
        return __version__

    # FTM measurement setup

    async def get_mcu_frequency(self) -> int:
        """GET MCU frequency."""
        self.logger.debug("%s: get_mcu_frequency call", self.label)
        return 0

    async def get_gate_time(self) -> float:
        """Get gate time in ms"""
        self.logger.debug("%s: get_gate_time call", self.label)
        return 0.0

    async def set_gate_time(self, gate_time_ms: float) -> float:
        """Set gate time in ms"""
        self.logger.debug("%s: set_gate_time(%f) call", self.label, gate_time_ms)
        return await self.get_gate_time()

    async def get_averaging(self) -> int:
        """Get averaging window"""
        self.logger.debug("%s: get_averaging call", self.label)
        return 0

    async def set_averaging(self, averaging_window: int) -> int:
        """Set averaging window."""
        self.logger.debug("%s: set_averaging(%d) call", self.label, averaging_window)
        return await self.get_averaging()

    # FTM frequency measurement data access methods

    async def get_counter(self) -> int:
        """Get FTM raw counts."""
        self.logger.debug("%s: get_counter call", self.label)
        return 0

    async def get_frequency_instant(self) -> float:
        """Get instant frequency."""
        self.logger.debug("%s: get_frequency_instant call", self.label)
        return 0.0

    async def get_averaging_progress(self) -> int:
        """Get averaging accumulation progress."""
        self.logger.debug("%s: get_averaging_progress call", self.label)
        return await self.get_averaging()

    async def get_frequency(self) -> float:
        """Get frequency."""
        self.logger.debug("%s: get_frequency call", self.label)
        return await self.get_frequency_instant()

    async def get_frequency_std(self) -> float:
        """Get frequency standard deviation."""
        self.logger.debug("%s: get_frequency_std call", self.label)
        return 0.0

    # Thickness measurement methods

    async def get_thickness(self) -> float:
        """Get thickness (Angstrom) value."""
        self.logger.debug("%s: get_thickness call", self.label)
        return 0.0

    async def get_thickness_std(self) -> float:
        """Parse thickness (Angstrom) standard deviation."""
        self.logger.debug("%s: get_thickness_std call", self.label)
        return 0.0

    async def get_rate(self) -> float:
        """Parse rate (Angstrom/s) value from register data"""
        self.logger.debug("%s: get_rate call", self.label)
        return 0.0

    async def get_material_density(self) -> float:
        """Get material density g/cm3"""
        self.logger.debug("%s: get_material_density call", self.label)
        return 0.0

    async def set_material_density(self, density: float) -> float:
        """Set material density g/cm3."""
        self.logger.debug("%s: set_material_density(%f) call", self.label, density)
        return 0.0

    async def get_material_z_ratio(self) -> float:
        """Get material Z-ratio."""
        self.logger.debug("%s: get_material_z_ratio call", self.label)
        return 0.0

    async def set_material_z_ratio(self, z_ratio: float) -> float:
        """Set material Z-ratio."""
        self.logger.debug("%s: set_material_z_ratio(%f) call", self.label, z_ratio)
        return await self.get_material_z_ratio()

    async def get_material(self) -> Material:
        """Get deposition material density and Z-ratio"""
        density = await self.get_material_density()
        z_ratio = await self.get_material_z_ratio()
        return Material(density=density, z_ratio=z_ratio)

    async def set_material(self, material: Material) -> Material:
        """Set deposition material density and Z-ratio"""
        await self.set_material_density(material.density)
        await self.set_material_z_ratio(material.z_ratio)
        return await self.get_material()

    async def get_ftm_scale(self) -> float:
        """Get FTM scale factor."""
        self.logger.debug("%s: get_ftm_scale call", self.label)
        return 1.0

    async def set_ftm_scale(self, scale: float) -> float:
        """Set FTM scale factor."""
        self.logger.debug("%s: set_ftm_scale(%f) call", self.label, scale)
        return 1.0

    async def get_target_thickness(self) -> float:
        """Get target thickness (Angstrom)."""
        self.logger.debug("%s: get_target_thickness call", self.label)
        return 0.0

    async def set_target_thickness(self, target: float) -> float:
        """Set target thickness (Angstrom)."""
        self.logger.debug("%s: set_target_thickness(%f) call", self.label, target)
        return await self.get_target_thickness()

    async def reset_thickness(self) -> None:
        """Reset measured thickness."""
        self.logger.debug("%s: reset_thickness() call", self.label)

    # CTRL OUT parameters

    async def get_ctrl_out_mode(self) -> OutCTRLMode:
        """Get the mode of the control output."""
        self.logger.debug("%s: get_ctrl_out_mode call", self.label)
        return OutCTRLMode.DISABLED

    async def set_ctrl_out_mode(self, mode: OutCTRLMode) -> OutCTRLMode:
        """Set the mode of the control output."""
        self.logger.debug("%s: set_ctrl_out_mode(%s) call", self.label, mode.name.capitalize())
        return await self.get_ctrl_out_mode()

    async def get_ctrl_out_value(self) -> bool:
        """Get control output value."""
        self.logger.debug("%s: get_ctrl_out_value call", self.label)
        return False

    async def set_ctrl_out_value(self, value: bool) -> bool:
        """Set control output value."""
        self.logger.debug("%s: set_ctrl_out_value(%s) call", self.label, value)
        return await self.get_ctrl_out_value()

    async def get_ctrl_pwm_mode(self) -> PwmCTRLMode:
        """Get the mode of the PWM output."""
        self.logger.debug("%s: get_ctrl_pwm_mode call", self.label)
        return PwmCTRLMode.DISABLED

    async def set_ctrl_pwm_mode(self, mode: PwmCTRLMode) -> PwmCTRLMode:
        """Set the mode of the PWM output."""
        self.logger.debug("%s: set_ctrl_pwm_mode(%s) call", self.label, mode.name.capitalize())
        return await self.get_ctrl_pwm_mode()

    async def get_ctrl_pwm_value(self) -> float:
        """Get PWM output value."""
        self.logger.debug("%s: get_ctrl_pwm_value call", self.label)
        return 0.0

    async def set_ctrl_pwm_value(self, value: float) -> float:
        """Set PWM output value."""
        self.logger.debug("%s: set_ctrl_pwm_value(%f) call", self.label, value)
        return await self.get_ctrl_pwm_value()

    async def get_ctrl_pwm_scale(self) -> int:
        """Get PWM output scale."""
        self.logger.debug("%s: get_ctrl_pwm_scale call", self.label)
        return 0

    async def set_ctrl_pwm_scale(self, scale: int) -> int:
        """Set PWM output scale."""
        self.logger.debug("%s: set_ctrl_pwm_scale(%d) call", self.label, scale)
        return await self.get_ctrl_pwm_scale()

    # MEASUREMENT START/STOP
    async def get_running_state(self) -> bool:
        """Get running state."""
        self.logger.debug("%s: get_running_state call", self.label)
        return False

    async def set_running_state(self, running: bool) -> bool:
        """Set running state."""
        self.logger.debug("%s: set_running_state(%s) call", self.label, running)
        return await self.get_running_state()

    # RS485 address and baudrate

    async def get_address(self) -> int:
        """Get RS-485 address."""
        self.logger.debug("%s: get_address call", self.label)
        return 1

    async def set_address(self, address: int) -> int:
        """Set RS-485 address."""
        self.logger.debug("%s: set_address(%d) call", self.label, address)
        return await self.get_address()

    async def get_baudrate(self) -> int:
        """Get RS-485 baudrate value."""
        self.logger.debug("%s: get_baudrate call", self.label)
        return 9600

    async def set_baudrate(self, baudrate: int) -> int:
        """Set RS-485 baudrate."""
        self.logger.debug("%s: set_baudrate(%d) call", self.label, baudrate)
        return await self.get_baudrate()

    # Read FTM state in a single request

    # pylint: disable=duplicate-code
    async def read_parameters(self) -> FTMParameters:
        """Read FTM Parameters"""
        self.logger.debug("%s: read_parameters call", self.label)
        frequency = await self.get_frequency()
        frequency_std = await self.get_frequency_std()
        averaging_window = await self.get_averaging()
        averaging_progress = await self.get_averaging_progress()
        rate = await self.get_rate()
        thickness = await self.get_thickness()
        thickness_std = await self.get_thickness_std()
        target = await self.get_target_thickness()
        material_density = await self.get_material_density()
        material_z_ratio = await self.get_material_z_ratio()
        running = await self.get_running_state()
        scale = await self.get_ftm_scale()
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
        return parameters

    async def read_data(self) -> dict[str, int | float | list[int | float]]:
        """Read FTM data in a single request"""
        parameters = await self.read_parameters()
        return {f: getattr(parameters, f) for f in parameters.__struct_fields__}

    async def process_message(self, message: dict[str, Any]) -> None:
        await super().process_message(message)
        if "cmd" in message:
            if message["cmd"] == "start":
                start_params = FTMStartCMD()
                if "data" in message:
                    try:
                        start_params = FTMStartCMD(**message["data"])
                    except (TypeError, ValueError):
                        pass
                await self.start_measurement(reset=start_params.reset)
            elif message["cmd"] == "stop":
                await self.stop_measurement()
            elif message["cmd"] == "clear_error":
                await self.clear_error()
            elif message["cmd"] == "reset_thickness":
                await self.reset_thickness()
