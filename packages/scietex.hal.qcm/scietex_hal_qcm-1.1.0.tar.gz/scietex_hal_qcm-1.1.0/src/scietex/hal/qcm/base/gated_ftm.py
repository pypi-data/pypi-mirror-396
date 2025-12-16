"""Gated FTM abstract interface."""

from abc import ABC, abstractmethod

from .data import QCMError, PwmCTRLMode, OutCTRLMode, FTMParameters, Material


# pylint: disable=too-many-public-methods
class GatedFTM(ABC):
    """Gated Film Thickness Monitor interface class."""

    error_codes: dict[int, QCMError] = {0: QCMError(code=0, message="No error")}
    error_codes_com: dict[int, QCMError] = {0: QCMError(code=0, message="No error")}

    # Error processing methods
    @abstractmethod
    async def get_error_code(self, comm: bool = False) -> int:
        """Read error code from the FTM"""

    def parse_error_code(self, code: int, comm: bool = False) -> QCMError:
        """Parse error code from the FTM"""
        if comm:
            if code in self.error_codes_com:
                return self.error_codes_com[code]
        else:
            if code in self.error_codes:
                return self.error_codes[code]
        return QCMError(code=code, message="Unknown error")

    @abstractmethod
    async def clear_error(self, comm: bool = False) -> int:
        """Clear error from the FTM"""

    # Device information methods
    @abstractmethod
    async def get_vendor(self) -> str:
        """Get QCM vendor name."""

    @abstractmethod
    async def get_product_name(self) -> str:
        """Get QCM product name."""

    @abstractmethod
    async def get_serial_number(self) -> str:
        """Get QCM serial number."""

    @abstractmethod
    async def get_version(self) -> str:
        """get QCM firmware version"""

    # FTM measurement setup

    @abstractmethod
    async def get_mcu_frequency(self) -> int:
        """GET MCU frequency."""

    @abstractmethod
    async def get_gate_time(self) -> float:
        """Get gate time in ms"""

    @abstractmethod
    async def set_gate_time(self, gate_time_ms: float) -> float:
        """Set gate time in ms"""

    @abstractmethod
    async def get_averaging(self) -> int:
        """Get averaging window"""

    @abstractmethod
    async def set_averaging(self, averaging_window: int) -> int:
        """Set averaging window."""

    # FTM frequency measurement data access methods

    @abstractmethod
    async def get_counter(self) -> int:
        """Get FTM raw counts."""

    @abstractmethod
    async def get_frequency_instant(self) -> float:
        """Get instant frequency."""

    @abstractmethod
    async def get_averaging_progress(self) -> int:
        """Get averaging accumulation progress."""

    @abstractmethod
    async def get_frequency(self) -> float:
        """Get frequency."""

    @abstractmethod
    async def get_frequency_std(self) -> float:
        """Get frequency standard deviation."""

    # Thickness measurement methods

    @abstractmethod
    async def get_thickness(self) -> float:
        """Get thickness (Angstrom) value."""

    @abstractmethod
    async def get_thickness_std(self) -> float:
        """Parse thickness (Angstrom) standard deviation."""

    @abstractmethod
    async def get_rate(self) -> float:
        """Parse rate (Angstrom/s) value from register data"""

    @abstractmethod
    async def get_material_density(self) -> float:
        """Get material density g/cm3"""

    @abstractmethod
    async def set_material_density(self, density: float) -> float:
        """Set material density g/cm3."""

    @abstractmethod
    async def get_material_z_ratio(self) -> float:
        """Get material Z-ratio."""

    @abstractmethod
    async def set_material_z_ratio(self, z_ratio: float) -> float:
        """Set material Z-ratio."""

    @abstractmethod
    async def get_material(self) -> Material:
        """Get deposition material density and Z-ratio"""

    @abstractmethod
    async def set_material(self, material: Material) -> Material:
        """Set deposition material density and Z-ratio"""

    @abstractmethod
    async def get_ftm_scale(self) -> float:
        """Get FTM scale factor."""

    @abstractmethod
    async def set_ftm_scale(self, scale: float) -> float:
        """Set FTM scale factor."""

    @abstractmethod
    async def get_target_thickness(self) -> float:
        """Get target thickness (Angstrom)."""

    @abstractmethod
    async def set_target_thickness(self, target: float) -> float:
        """Set target thickness (Angstrom)."""

    async def get_target_nm(self) -> float:
        """Get target thickness (nm)."""
        return await self.get_target_thickness() / 10

    async def set_target_nm(self, target: float) -> float:
        """Set target thickness (nm)."""
        return await self.set_target_thickness(target * 10)

    async def get_target_um(self) -> float:
        """Get target thickness (nm)."""
        return await self.get_target_thickness() / 10_000

    async def set_target_um(self, target: float) -> float:
        """Set target thickness (um)."""
        return await self.set_target_thickness(target * 10_000)

    @abstractmethod
    async def reset_thickness(self) -> None:
        """Reset measured thickness."""

    # CTRL OUT parameters

    @abstractmethod
    async def get_ctrl_out_mode(self) -> OutCTRLMode:
        """Get the mode of the control output."""

    @abstractmethod
    async def set_ctrl_out_mode(self, mode: OutCTRLMode) -> OutCTRLMode:
        """Set the mode of the control output."""

    @abstractmethod
    async def get_ctrl_out_value(self) -> bool:
        """Get control output value."""

    @abstractmethod
    async def set_ctrl_out_value(self, value: bool) -> bool:
        """Set control output value."""

    @abstractmethod
    async def get_ctrl_pwm_mode(self) -> PwmCTRLMode:
        """Get the mode of the PWM output."""

    @abstractmethod
    async def set_ctrl_pwm_mode(self, mode: PwmCTRLMode) -> PwmCTRLMode:
        """Set the mode of the PWM output."""

    @abstractmethod
    async def get_ctrl_pwm_value(self) -> float:
        """Get PWM output value."""

    @abstractmethod
    async def set_ctrl_pwm_value(self, value: float) -> float:
        """Set PWM output value."""

    @abstractmethod
    async def get_ctrl_pwm_scale(self) -> int:
        """Get PWM output scale."""

    @abstractmethod
    async def set_ctrl_pwm_scale(self, scale: int) -> int:
        """Set PWM output scale."""

    # MEASUREMENT START/STOP

    @abstractmethod
    async def get_running_state(self) -> bool:
        """Get running state."""

    @abstractmethod
    async def set_running_state(self, running: bool) -> bool:
        """Set running state."""

    async def start_measurement(self, reset: bool = True) -> bool:
        """Start measurement"""
        if reset:
            await self.reset_thickness()
        return await self.set_running_state(True)

    async def stop_measurement(self) -> bool:
        """Stop measurement."""
        return await self.set_running_state(False)

    # Read FTM parameters in single call

    @abstractmethod
    async def read_parameters(self) -> FTMParameters:
        """Read FTM Parameters"""
