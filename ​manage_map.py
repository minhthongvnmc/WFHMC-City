import os
import io
import struct
import zipfile
import nbtlib
from nbtlib.tag import String, Byte

WORLD_DIR = "world"
LEVEL_DAT = os.path.join(WORLD_DIR, "level.dat")
OUTPUT_MCWORLD = "WFHMC_City_v1.0.mcworld"

def update_level_dat(map_name, allow_cheats=True):
    if not os.path.exists(LEVEL_DAT):
        print(f"Error: {LEVEL_DAT} not found.")
        return

    with open(LEVEL_DAT, "rb") as f:
        data = f.read()

    header_version = struct.unpack("<I", data[0:4])[0]
    data_length = struct.unpack("<I", data[4:8])[0]
    nbt_payload = data[8:8 + data_length]

    buffer = io.BytesIO(nbt_payload)
    nbt_data = nbtlib.File.parse(buffer, byteorder="little")

    nbt_data["LevelName"] = String(map_name)
    nbt_data["hasBeenLoadedInCreative"] = Byte(1 if allow_cheats else 0)

    out_buffer = io.BytesIO()
    nbt_data.write(out_buffer, byteorder="little")
    new_payload = out_buffer.getvalue()

    new_header = struct.pack("<I", header_version) + struct.pack("<I", len(new_payload))

    with open(LEVEL_DAT, "wb") as f:
        f.write(new_header + new_payload)

    print(f"Updated level.dat successfully: {map_name}")

def build_mcworld():
    if not os.path.exists(WORLD_DIR):
        print("Error: World directory missing.")
        return

    with zipfile.ZipFile(OUTPUT_MCWORLD, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(WORLD_DIR):
            for file in files:
                if file in ["LOCK", "LOG", "LOG.old"]:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, WORLD_DIR)
                zipf.write(file_path, arcname)

    print(f"Package generated: {OUTPUT_MCWORLD}")

if __name__ == "__main__":
    build_mcworld()
