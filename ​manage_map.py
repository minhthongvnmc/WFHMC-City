import os
import io
import struct
import zipfile
import nbtlib
from nbtlib.tag import String, Byte, Int

WORLD_DIR = "world"
LEVEL_DAT = os.path.join(WORLD_DIR, "level.dat")
OUTPUT_MCWORLD = "WFHMC_City_V2.5_Beta.mcworld"

def update_level_dat(map_name="WFHMC City V2.5 Beta", allow_cheats=True):
    """
    Cập nhật tên map và thuộc tính NBT cơ bản trong level.dat của Minecraft Bedrock.
    """
    if not os.path.exists(LEVEL_DAT):
        print(f"[!] Không tìm thấy tệp {LEVEL_DAT}. Bỏ qua bước cập nhật NBT.")
        return False

    try:
        with open(LEVEL_DAT, "rb") as f:
            data = f.read()

        # Cấu trúc level.dat Bedrock: 4 bytes Header Version + 4 bytes Payload Length + NBT Payload
        header_version = struct.unpack("<I", data[0:4])[0]
        data_length = struct.unpack("<I", data[4:8])[0]
        nbt_payload = data[8:8 + data_length]

        # Đọc dữ liệu NBT Little-Endian
        buffer = io.BytesIO(nbt_payload)
        nbt_data = nbtlib.File.parse(buffer, byteorder="little")

        # Điều chỉnh thuộc tính tên thế giới và gian lận (cheats)
        nbt_data["LevelName"] = String(map_name)
        nbt_data["hasBeenLoadedInCreative"] = Byte(1 if allow_cheats else 0)

        # Ghi lại NBT Payload
        out_buffer = io.BytesIO()
        nbt_data.write(out_buffer, byteorder="little")
        new_payload = out_buffer.getvalue()

        # Tạo lại Header chính xác
        new_header = struct.pack("<I", header_version) + struct.pack("<I", len(new_payload))

        with open(LEVEL_DAT, "wb") as f:
            f.write(new_header + new_payload)

        print(f"[✓] Cập nhật thành công level.dat: Tên map = '{map_name}'")
        return True
    except Exception as e:
        print(f"[!] Lỗi khi ghi file level.dat: {e}")
        return False

def build_mcworld():
    """
    Đóng gói thư mục 'world' thành định dạng .mcworld (Zip chuẩn của Minecraft Bedrock).
    """
    if not os.path.exists(WORLD_DIR):
        print(f"[!] Lỗi: Không tìm thấy thư mục '{WORLD_DIR}'.")
        return

    # Danh sách các tệp khóa/rác tạm thời của LevelDB cần loại bỏ
    ignored_files = {"LOCK", "LOG", "LOG.old"}

    print(f"[*] Đang đóng gói thư mục '{WORLD_DIR}' thành '{OUTPUT_MCWORLD}'...")
    
    with zipfile.ZipFile(OUTPUT_MCWORLD, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(WORLD_DIR):
            for file in files:
                if file in ignored_files or file.endswith(".tmp"):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, WORLD_DIR)
                zipf.write(file_path, arcname)

    print(f"[✓] Đã tạo thành công gói cài đặt: {OUTPUT_MCWORLD}")

if __name__ == "__main__":
    # 1. Cập nhật thuộc tính map
    update_level_dat(map_name="WFHMC City V2.5 Beta", allow_cheats=True)
    
    # 2. Xuất bản tệp .mcworld
    build_mcworld()
