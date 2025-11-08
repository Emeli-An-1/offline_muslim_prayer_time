import os

def split_code_for_ai(source_folder, output_prefix="ai_part", max_size_mb=1):
    """
    source_folder: Proje klasörü
    output_prefix: Çıktı dosya prefixi
    max_size_mb: Tek dosya boyutu (AI için ideal)
    """
    max_size = max_size_mb * 1024 * 1024  # byte
    part_num = 1
    current_size = 0

    # export_txt klasörü oluştur
    output_folder = os.path.join(os.getcwd(), "export_txt")
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, f"{output_prefix}_{part_num}.txt")
    out = open(output_file, "w", encoding="utf-8")

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith(".py"):  # İstersen .json, .flet vs ekleyebilirsin
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except:
                    continue

                header = f"\n### FILE: {os.path.relpath(file_path, source_folder)} ###\n\n"
                lines = content.splitlines(keepends=True)

                for line in lines:
                    line_size = len(line.encode("utf-8"))
                    if current_size + line_size > max_size:
                        out.close()
                        part_num += 1
                        output_file = os.path.join(output_folder, f"{output_prefix}_{part_num}.txt")
                        out = open(output_file, "w", encoding="utf-8")
                        current_size = 0
                        out.write(header)
                        current_size += len(header.encode("utf-8"))
                    out.write(line)
                    current_size += line_size

    out.close()
    print(f"✅ Tamamlandı! Toplam {part_num} AI dostu dosya oluşturuldu. Dosyalar '{output_folder}' içinde.")

# Kullanım:
split_code_for_ai(r"D:\PTime_Flet\prayer_offline", max_size_mb=1)
