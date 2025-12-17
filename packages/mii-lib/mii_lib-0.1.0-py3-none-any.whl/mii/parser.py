"""Mii parser for converting raw bytes into Mii dataclass instances"""

from .models import Mii


class MiiParser:
    """Parses raw Mii bytes into Mii dataclass instances"""

    COLORS = [
        "Red",
        "Orange",
        "Yellow",
        "Green",
        "DarkGreen",
        "Blue",
        "LightBlue",
        "Pink",
        "Purple",
        "Brown",
        "White",
        "Black",
    ]

    @classmethod
    def _read_string(cls, data: bytes, offset: int, length: int) -> str:
        """Read UTF-16BE string from the data"""
        string_data = data[offset : offset + length]
        # Find the first null terminator (0x0000 in UTF-16BE)
        null_pos = string_data.find(b"\x00\x00")
        if null_pos != -1:
            # Ensure we align to 2-byte boundaries for UTF-16
            if null_pos % 2 != 0:
                null_pos -= 1
            string_data = string_data[: null_pos + 2]

        # Convert from UTF-16BE and remove null terminators
        return string_data.decode("utf-16be").rstrip("\x00")

    @classmethod
    def _read_mii_name(cls, data: bytes) -> str:
        """Read Mii name starting at offset 2"""
        return cls._read_string(data, 2, 20)

    @classmethod
    def _read_creator_name(cls, data: bytes) -> str:
        """Read creator name starting at offset 54"""
        return cls._read_string(data, 54, 20)

    @classmethod
    def _read_mii_metadata(cls, data: bytes) -> tuple:
        """Read and parse Mii metadata from first 2 bytes

        Returns:
            Tuple of (is_girl, birth_month, birth_day, favorite_color_index, is_favorite)
        """
        # Read first 2 bytes and convert to binary string
        metadata_bytes = data[0:2]
        binary_str = "".join(format(b, "08b") for b in metadata_bytes)

        # Extract metadata fields
        is_girl = int(binary_str[1], 2)
        birth_month = int(binary_str[2:6], 2)
        birth_day = int(binary_str[6:11], 2)
        favorite_color_index = int(binary_str[11:15], 2)
        is_favorite = int(binary_str[15], 2)

        return (is_girl, birth_month, birth_day, favorite_color_index, is_favorite)

    @classmethod
    def _read_mii_id(cls, data: bytes) -> bytes:
        """Read 4-byte Mii ID starting at offset 24"""
        return data[24:28]

    @classmethod
    def _get_color_name(cls, color_index: int) -> str:
        """Get color name from color index"""
        if 0 <= color_index < len(cls.COLORS):
            return cls.COLORS[color_index]
        return f"Unknown ({color_index})"

    @classmethod
    def parse(cls, data: bytes, padding: int = 0) -> Mii:
        """Parse raw Mii bytes into a Mii dataclass instance

        Args:
            data: Raw Mii bytes
            padding: Number of padding bytes to append when writing to disk

        Returns:
            Mii dataclass instance

        Examples:
            >>> with open("WII_PL00000.mii", "rb") as f:
            ...     mii_data = f.read()
            >>> mii = MiiParser.parse(mii_data)
            >>> print(mii.name)
        """
        mii_name = cls._read_mii_name(data)
        creator_name = cls._read_creator_name(data)
        metadata = cls._read_mii_metadata(data)
        mii_id = cls._read_mii_id(data)
        color_name = cls._get_color_name(metadata[3])

        return Mii(
            raw_data=data,
            name=mii_name or "Unnamed",
            creator_name=creator_name or "Unknown",
            mii_id=mii_id,
            is_girl=bool(metadata[0]),
            birth_month=metadata[1] if metadata[1] else None,
            birth_day=metadata[2] if metadata[2] else None,
            favorite_color_index=metadata[3],
            favorite_color=color_name,
            is_favorite=bool(metadata[4]),
            padding=padding,
        )
