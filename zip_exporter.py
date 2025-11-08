import os
import zipfile
from datetime import datetime

def zip_project(source_folder, output_folder="exports"):
    os.makedirs(output_folder, exist_ok=True)

    zip_filename = f"project_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
    zip_path = os.path.join(output_folder, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                # İstersen ek uzantılar ekleyebilirsin
                if file.endswith((".py", ".json", ".flet", ".txt")):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, source_folder))

    print(f"✅ Project zipped successfully: {zip_path}")

# Kullanım:
if __name__ == "__main__":
    zip_project(r"D:\PTime_Flet\prayer_offline")
