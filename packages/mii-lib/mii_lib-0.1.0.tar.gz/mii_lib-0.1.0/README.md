# mii-lib

https://pypi.org/project/mii-lib/

Library and CLI for extracting .mii files from misc. Wii/Dolphin data dumps, and extracting information from them (name, fav. color, gender, etc.)

## Installation

- Library only: `pip install mii-lib`
- With CLI: `pip install mii-lib[cli]` / `uvx mii-cli --help` / etc.

## Usage

```python
from pathlib import Path
from mii import MiiDatabase, MiiParser, MiiType

database = MiiDatabase(Path("RFL_DB.dat"), MiiType.WII_PLAZA)
mii = database[0]
print(mii.name)
print(mii.favorite_color)

for mii in database:
    print(f"{mii.name} by {mii.creator_name}")

with open("WII_PL00000.mii", "rb") as f:
    mii_data = f.read()

mii = MiiParser.parse(mii_data)
print(mii.get_birthday_string())
```

More complete examples can be found in [examples/library_usage.py](./examples/library_usage.py)

## RFL_DB.dat

This is all based around reading from a [`RFL_DB.dat` file](https://wiibrew.org/wiki//shared2/menu/FaceLib/RFL_DB.dat).

After having used the Mii Channel in Dolphin, and assuming its saved the contents of it to disk at some point, you'll find it in one of the following folders:

- `C:\Users\<Your Username>\Documents\Dolphin Emulator\Wii\shared2\menu\FaceLib\`
- `C:\Users\<Your Username>\AppData\Roaming\Dolphin Emulator\Wii\shared2\menu\FaceLib\`
- `~/.dolphin-emu/Wii/shared2/menu/FaceLib/`

If none of these exist, check where Dolphin is savings its data to in its settings.

---

Originally based on https://github.com/PuccamiteTech/PyMii/
