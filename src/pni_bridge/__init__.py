"""PNI hardware adapters for BCI devices."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List
import numpy as np

@dataclass
class EEGReading:
    timestamp: float
    channels: Dict[str, float]  # channel_name -> voltage (µV)
    sample_rate: int
    device_id: str

class BCIAdapter(ABC):
    """Abstract base for BCI hardware adapters."""
    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def stream(self) -> EEGReading:
        pass

    @abstractmethod
    def get_channels(self) -> List[str]:
        pass

class OpenBCIAdapter(BCIAdapter):
    """OpenBCI Cyton/Daisy adapter."""
    def __init__(self, port: str = "/dev/ttyUSB0", daisy: bool = False):
        self.port = port
        self.daisy = daisy
        self.channels = 16 if daisy else 8
        self._connected = False
    
    async def connect(self) -> bool:
        # In production: serial connection to OpenBCI board
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def stream(self) -> EEGReading:
        # Simulate EEG data
        ch_data = {f"ch{i}": np.random.randn() * 50 for i in range(self.channels)}
        return EEGReading(
            timestamp=time.time(),
            channels=ch_data,
            sample_rate=250,
            device_id="openbci_cyton",
        )

    def get_channels(self) -> List[str]:
        return [f"ch{i}" for i in range(self.channels)]

class GtecAdapter(BCIAdapter):
    """g.tec USBamp / g.Nautilus adapter."""
    def __init__(self, device_id: str = "gtec_001"):
        self.device_id = device_id
        self._connected = False

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def stream(self) -> EEGReading:
        ch_data = {f"ch{i}": np.random.randn() * 30 for i in range(32)}
        return EEGReading(
            timestamp=time.time(),
            channels=ch_data,
            sample_rate=600,
            device_id=self.device_id,
        )

    def get_channels(self) -> List[str]:
        return [f"ch{i}" for i in range(32)]

class EmotivAdapter(BCIAdapter):
    """Emotiv EPOC+ / Insight adapter."""
    def __init__(self, license_key: str = ""):
        self.license_key = license_key
        self._connected = False

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def stream(self) -> EEGReading:
        ch_names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2",
                    "P8", "T8", "FC6", "F4", "F8", "AF4"]
        ch_data = {ch: np.random.randn() * 20 for ch in ch_names}
        return EEGReading(
            timestamp=time.time(),
            channels=ch_data,
            sample_rate=128,
            device_id="emotiv_epoc",
        )

    def get_channels(self) -> List[str]:
        return ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2",
                "P8", "T8", "FC6", "F4", "F8", "AF4"]
