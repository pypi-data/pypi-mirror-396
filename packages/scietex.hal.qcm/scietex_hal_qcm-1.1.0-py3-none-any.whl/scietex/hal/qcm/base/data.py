"""Data models for the QCM."""

from enum import Enum
import msgspec


class OutCTRLMode(Enum):
    """Modes of the control output."""

    HIGH = 1
    LOW = 2
    MANUAL = 3
    DISABLED = 4


class PwmCTRLMode(Enum):
    """Modes of the PWM output."""

    ABSOLUTE = 1
    RELATIVE = 2
    MANUAL = 3
    DISABLED = 4


# pylint: disable=too-few-public-methods
class QCMError(msgspec.Struct, frozen=True):
    """Model of a QCM error with code and message."""

    code: int
    message: str = "Unknown error"

    def __str__(self) -> str:
        return f"QCMError(code={self.code}, message='{self.message}')"


# pylint: disable=too-few-public-methods
class FTMParameters(msgspec.Struct, frozen=True):
    """Model for FTM operational parameters."""

    frequency: float = 0.0  # Sensor frequency
    frequency_std: float = 0.0  # Sensor frequency standard deviation
    averaging_window: int = 1  # Averaging window size
    averaging_progress: int = 1  # Averaging accumulation progress
    rate: float = 0.0  # Deposition rate A/s
    thickness: float = 0.0  # Film thickness A
    thickness_std: float = 0.0  # Film thickness standard deviation A
    target: float = 0.0  # Film target thickness A
    material_density: float = 0.0  # Material density g/cm^3
    material_z_ratio: float = 0.0  # Material Z-ratio
    running: bool = False  # Current FTM measurement running state
    scale: float = 1.0  # Scale (tooling) factor

    def __str__(self) -> str:
        return (
            f"FTMParameters(frequency={self.frequency:g} +- {self.frequency_std:g} Hz, "
            f"averaging={self.averaging_progress}/{self.averaging_window}, "
            f"deposition rate={self.rate} A/s, "
            f"film thickness={self.thickness} +- {self.thickness_std} A, "
            f"target thickness={self.target} A, "
            f"material density={self.material_density} g/cm^3, "
            f"material Z-ratio={self.material_z_ratio}, "
            f"running={self.running})"
        )


# pylint: disable=too-few-public-methods
class FTMStartCMD(msgspec.Struct, frozen=True):
    """FTM start command with parameters."""

    reset: bool = True  # Reset thickness at start

    def __str__(self) -> str:
        return f"FTMStartCMD(reset={self.reset})"


# pylint: disable=too-few-public-methods
class Material(msgspec.Struct, frozen=True):
    """Material parameters."""

    density: float  # Density g/cm^3
    z_ratio: float  # Z-ratio

    def __str__(self) -> str:
        return f"Material(density={self.density}, Z-ratio={self.z_ratio})"
