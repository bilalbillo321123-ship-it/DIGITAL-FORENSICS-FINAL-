import os
import hashlib
import csv
import time

# Enable colors (Windows)
os.system("")

# Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Setup folders
os.makedirs("output", exist_ok=True)
LOG_FILE = "output/log.txt"

# ================= LOG FUNCTION =================
def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ================= HASH FUNCTION =================
def calculate_hashes(data):
    return hashlib.md5(data).hexdigest(), hashlib.sha256(data).hexdigest()

# ================= PROGRESS BAR =================
def show_progress(current, total):
    if total == 0:
        return
    percent = int((current / total) * 100)
    bar = "█" * (percent // 5) + "-" * (20 - percent // 5)
    print(f"\r[{bar}] {percent}%", end="", flush=True)

# ================= MAIN FUNCTION =================
def run_carver(filepath, file_type):

    start_time = time.time()
    file_size = os.path.getsize(filepath)

    data = b""
    chunk_size = 1024 * 1024  # 1MB
    read_bytes = 0

    print(YELLOW + "\nReading Image..." + RESET)

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            data += chunk
            read_bytes += len(chunk)
            show_progress(read_bytes, file_size)

    print("\n")
    log("Image loaded successfully")

    report_data = []
    jpeg_total = png_total = pdf_total = 0

    # ================= JPEG =================
    if file_type in ["jpeg", "all"]:
        log("[*] Scanning JPEG...")
        header = b'\xff\xd8'
        footer = b'\xff\xd9'
        offset = 0

        while True:
            start = data.find(header, offset)
            if start == -1:
                break
            end = data.find(footer, start)
            if end == -1:
                break

            end += 2
            recovered = data[start:end]

            if (b'JFIF' in recovered[:20] or b'Exif' in recovered[:20]) and len(recovered) > 5000:
                jpeg_total += 1
                filename = f"output/jpeg_{jpeg_total}.jpg"

                with open(filename, "wb") as f:
                    f.write(recovered)

                md5, sha256 = calculate_hashes(recovered)

                report_data.append({
                    "name": filename,
                    "type": "JPEG",
                    "offset": start,
                    "size": len(recovered),
                    "md5": md5,
                    "sha256": sha256
                })

                log(f"[JPEG] Recovered: {filename}")

            offset = end

    # ================= PNG =================
    if file_type in ["png", "all"]:
        log("[*] Scanning PNG...")
        header = b'\x89PNG\r\n\x1a\n'
        footer = b'IEND\xaeB`\x82'
        offset = 0

        while True:
            start = data.find(header, offset)
            if start == -1:
                break
            end = data.find(footer, start)
            if end == -1:
                break

            end += len(footer)
            recovered = data[start:end]

            if len(recovered) > 1000:
                png_total += 1
                filename = f"output/png_{png_total}.png"

                with open(filename, "wb") as f:
                    f.write(recovered)

                md5, sha256 = calculate_hashes(recovered)

                report_data.append({
                    "name": filename,
                    "type": "PNG",
                    "offset": start,
                    "size": len(recovered),
                    "md5": md5,
                    "sha256": sha256
                })

                log(f"[PNG] Recovered: {filename}")

            offset = end

    # ================= PDF =================
    if file_type in ["pdf", "all"]:
        log("[*] Scanning PDF...")
        header = b'%PDF'
        footer = b'%%EOF'
        offset = 0

        while True:
            start = data.find(header, offset)
            if start == -1:
                break
            end = data.find(footer, start)
            if end == -1:
                break

            end += len(footer)
            recovered = data[start:end]

            if len(recovered) > 1000:
                pdf_total += 1
                filename = f"output/pdf_{pdf_total}.pdf"

                with open(filename, "wb") as f:
                    f.write(recovered)

                md5, sha256 = calculate_hashes(recovered)

                report_data.append({
                    "name": filename,
                    "type": "PDF",
                    "offset": start,
                    "size": len(recovered),
                    "md5": md5,
                    "sha256": sha256
                })

                log(f"[PDF] Recovered: {filename}")

            offset = end

    # ================= CSV REPORT =================
    with open("output/report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["File Name", "Type", "Offset", "Size", "MD5", "SHA256"])

        for item in report_data:
            writer.writerow([
                item["name"],
                item["type"],
                item["offset"],
                item["size"],
                item["md5"],
                item["sha256"]
            ])

    log("CSV report generated")

    # ================= HTML REPORT =================
    html = """
    <html>
    <head>
        <title>Forensic Report</title>
        <style>
            body { font-family: Arial; background:#111; color:#fff; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #444; padding: 8px; }
            th { background-color: #222; }
        </style>
    </head>
    <body>
    <h2>Recovered Files Report</h2>
    <table>
    <tr>
    <th>File Name</th>
    <th>Type</th>
    <th>Offset</th>
    <th>Size</th>
    <th>MD5</th>
    <th>SHA256</th>
    </tr>
    """

    for item in report_data:
        html += f"""
        <tr>
            <td>{item['name']}</td>
            <td>{item['type']}</td>
            <td>{item['offset']}</td>
            <td>{item['size']}</td>
            <td>{item['md5']}</td>
            <td>{item['sha256']}</td>
        </tr>
        """

    html += "</table></body></html>"

    with open("output/report.html", "w") as f:
        f.write(html)

    log("HTML report generated")

    # ================= SUMMARY =================
    print("\n" + "="*40)
    print(BLUE + "RECOVERY SUMMARY" + RESET)
    print("="*40)

    print(f"JPEG: {jpeg_total}")
    print(f"PNG : {png_total}")
    print(f"PDF : {pdf_total}")
    print(f"TOTAL: {len(report_data)}")

    print("="*40)

    end_time = time.time()
    log(f"Execution Time: {round(end_time - start_time, 2)} seconds")

    return report_data


# ================= MAIN =================
if __name__ == "__main__":

    print("\n" + "="*40)
    print(BLUE + "NTFS FILE CARVER" + RESET)
    print("="*40)

    print("Select file type to recover:")
    print("1. JPEG")
    print("2. PDF")
    print("3. PNG")
    print("4. ALL")

    choice = input("\nEnter choice (1-4): ")

    if choice == "1":
        file_type = "jpeg"
    elif choice == "2":
        file_type = "pdf"
    elif choice == "3":
        file_type = "png"
    else:
        file_type = "all"

    results = run_carver("Rec.001", file_type)

    print("\nDone. Files saved in 'output/' folder")