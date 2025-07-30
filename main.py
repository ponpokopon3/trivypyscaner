import os
import csv
import tempfile
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "input.csv"
OUTPUT_DIR = os.path.abspath(r"sbom_outputs")
TRIVY_PATH = "/usr/local/bin/trivy"

def create_sbom_for_package(language, name, version, date_str):
    if language.lower() != "python":
        print(f"Skipping unsupported language: {language}")
        return

    file_name = f"{name}_{version}_{date_str}.json"
    output_path = os.path.join(OUTPUT_DIR, file_name)

    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)

            with open("requirements.txt", "w", encoding="utf-8") as f:
                f.write(f"{name}=={version}\n")

            cmd = [
                TRIVY_PATH,
                "rootfs",
                "--format", "cyclonedx",
                "--output", output_path,
                "--scanners", "vuln",
                "requirements.txt",
            ]

            subprocess.run(cmd, check=True)
            print(f"✔ SBOM created: {output_path}")

        except subprocess.CalledProcessError as e:
            print(f"✖ Failed to generate SBOM for {name}=={version}: {e}")
        finally:
            os.chdir(original_dir)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today_str = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")

    with open(CSV_FILE, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                print(f"Skipping invalid row: {row}")
                continue
            language, name, version = [item.strip() for item in row]
            create_sbom_for_package(language, name, version, today_str)

if __name__ == "__main__":
    main()
