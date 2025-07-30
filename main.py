import os
import csv
import tempfile
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "input.csv"
OUTPUT_DIR = os.path.abspath("sbom_outputs")
TRIVY_PATH = "/usr/local/bin/trivy"  # Windows の場合は "trivy.exe" などに変更
COMBINED_OUTPUT = "python_package.json"

def create_individual_sbom(language, name, version, date_str):
    if language.lower() != "python":
        print(f"Skipping unsupported language: {language}")
        return

    file_name = f"{name}_{version}_{date_str}.json"
    output_path = os.path.join(OUTPUT_DIR, file_name)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)
            with open("requirements.txt", "w", encoding="utf-8") as f:
                f.write(f"{name}=={version}\n")

            cmd = [
                TRIVY_PATH,
                "fs",".",
                "--format", "cyclonedx",
                "--output", output_path,
                "--scanners", "vuln",
                "--file-patterns", "python:requirements.txt",
            ]

            subprocess.run(cmd, check=True)
            print(f"✔ Individual SBOM saved: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"✖ Failed to generate SBOM for {name}=={version}: {e}")
        finally:
            os.chdir(original_dir)

def create_combined_sbom(requirements_list, output_filename):
    if not requirements_list:
        print("No valid Python packages to generate combined SBOM.")
        return

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            os.chdir(tmpdir)
            with open("requirements.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(requirements_list) + "\n")

            cmd = [
                TRIVY_PATH,
                "fs",".",
                "--format", "cyclonedx",
                "--output", output_path,
                "--scanners", "vuln",
                "--file-patterns", "python:requirements.txt",
            ]

            subprocess.run(cmd, check=True)
            print(f"✔ Combined SBOM saved: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"✖ Failed to combined SBOM : {e}")
        finally:
            os.chdir(original_dir)
def main():
    today_str = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    requirements = []

    with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 3:
                continue
            language, name, version = row[0], row[1], row[2]
            create_individual_sbom(language, name, version, today_str)
            if language.lower() == "python":
                requirements.append(f"{name}=={version}")

    # まとめて一つのSBOMを出力
    create_combined_sbom(requirements, COMBINED_OUTPUT)

if __name__ == "__main__":
    main()
