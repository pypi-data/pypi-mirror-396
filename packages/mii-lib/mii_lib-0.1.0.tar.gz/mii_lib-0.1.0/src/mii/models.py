"""Mii data models"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path


@dataclass
class Mii:
    """Represents a single Mii with all its data"""

    raw_data: bytes  # Original Mii bytes (for writing back to disk)
    name: str
    creator_name: str
    mii_id: bytes
    is_girl: bool
    birth_month: Optional[int]
    birth_day: Optional[int]
    favorite_color_index: int
    favorite_color: str
    is_favorite: bool
    padding: int = 0  # Padding bytes to append when writing to disk

    @property
    def is_wii_mii(self) -> bool:
        """Determine if this Mii is from Wii (True) or 3DS/WiiU (False)"""
        file_size = len(self.raw_data)
        if file_size == 74:
            return True  # Wii Mii
        elif file_size == 92:
            return False  # 3DS/WiiU Mii
        else:
            raise ValueError(f"Mii format is unknown (size: {file_size})")

    def get_creation_seconds(self) -> int:
        """Extract timestamp seconds from Mii data"""
        multiplier = 4 if self.is_wii_mii else 2
        seek_pos = 0x18 if self.is_wii_mii else 0xC
        str_id = self.raw_data[seek_pos : seek_pos + 4].hex()
        int_id = int(str_id[1:], 16)
        return int_id * multiplier

    def get_creation_datetime(self) -> datetime:
        """Get creation datetime for this Mii

        Returns:
            Datetime object representing when the Mii was created

        Examples:
            >>> mii = database[0]
            >>> creation_time = mii.get_creation_datetime()
            >>> print(creation_time.strftime("%Y-%m-%d %H:%M:%S"))
        """
        seconds = self.get_creation_seconds()
        base_date = datetime(2006, 1, 1) if self.is_wii_mii else datetime(2010, 1, 1)
        shift = timedelta(seconds=seconds)
        return base_date + shift

    def get_birthday_string(self) -> str:
        """Get formatted birthday string

        Returns:
            Formatted birthday string (e.g., "1/15") or "Not set"

        Examples:
            >>> mii = database[0]
            >>> print(mii.get_birthday_string())
            "1/15"
        """
        if self.birth_month and self.birth_day:
            return f"{self.birth_month}/{self.birth_day}"
        return "Not set"

    def get_gender_string(self) -> str:
        """Get formatted gender string

        Returns:
            "Female" or "Male"

        Examples:
            >>> mii = database[0]
            >>> print(mii.get_gender_string())
            "Female"
        """
        return "Female" if self.is_girl else "Male"

    def to_bytes(self) -> bytes:
        """Returns raw_data with padding appended if needed"""
        if self.padding > 0:
            return self.raw_data + bytearray(self.padding)
        return self.raw_data

    def get_mii_id_hex(self) -> str:
        """Get Mii ID as uppercase hex string

        Returns:
            Mii ID as uppercase hexadecimal string

        Examples:
            >>> mii = database[0]
            >>> print(mii.get_mii_id_hex())
            "A1B2C3D4"
        """
        return self.mii_id.hex().upper()

    def export(self, path: Path) -> None:
        """Write this Mii to a file

        Args:
            path: Path where the Mii file should be written

        Examples:
            >>> mii = database[0]
            >>> mii.export(Path("./my_mii.mii"))
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.to_bytes())
