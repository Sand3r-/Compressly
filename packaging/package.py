import sys, os, shutil, platform
from typing import List
import PyInstaller.__main__

"""
Change directory to the root of the repository
"""
def cd_repo_root() -> None:
    abs_path = os.path.abspath(__file__)
    dir_name = os.path.dirname(abs_path)
    os.chdir(dir_name) # cd packaging
    os.chdir("..") # cd ..

def run_pyinstaller() -> None:
    arguments = [
        "--name",
        "Compressly",
        "--noconsole",
        "src/main.py",
        "--noconfirm"
        ]
    os_name = platform.system()
    os_specific_args = []
    if os_name == 'Windows':
        os_specific_args = [
            "--add-binary", "external/ffmpeg/ffmpeg.exe;external/ffmpeg/",
            "--add-binary", "external/ffmpeg/SvtAv1Enc.dll;external/ffmpeg/"
        ]
    elif os_name == 'Darwin':
        os_specific_args = [
            "--add-binary", "external/ffmpeg/ffmpeg;external/ffmpeg/"
        ]
    else:
        raise NotImplementedError("Unsupported OS: " + os_name)
    
    arguments.extend(os_specific_args)
    PyInstaller.__main__.run(arguments)

def create_licensing_txt() -> None:
    # Define the input and output file paths
    input_file = 'README.md'
    output_file = 'dist/Compressly/licensing.txt'

    # Define the start line to look for
    start_line = "# Licensing and Third-Party Software"

    # Read the file content
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the index where the start line appears
    start_index = None
    for i, line in enumerate(lines):
        if line.strip() == start_line:
            start_index = i
            break

    # Check if the start line was found
    if start_index is not None:
        # Extract the content from the start line to the end of the file
        extracted_content = lines[start_index:]

        # Write the extracted content to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(extracted_content)
        
        print("File licensing.txt created.")
    else:
        print("Failed to create licensing.txt")
        print(f"Start line '{start_line}' not found in the file.")


"""
1. Create licenses folder in dist/
2. Copy liceneses there
3. Create licensing.txt file in the dist folder from README.md
"""
def create_licensing_files() -> None:
    # Create licenses folder
    licenses_path = os.path.join("dist", "Compressly", "licenses")
    if not os.path.exists(licenses_path):
        os.makedirs(licenses_path)
        print("Licenses folder created.")

    # Copy licenses
    shutil.copy("external/ffmpeg/License_ffmpeg.md", licenses_path)
    shutil.copy("external/ffmpeg/License_SvtAv1.md", licenses_path)
    shutil.copy("external/PySide6/License_PySide6.md", licenses_path)
    print("License files copied.")

    # Create licensing.txt
    create_licensing_txt()


def compress_to_archive(sys_args : List[str]) -> None:
    zip_name = sys_args[1] if len(sys_args) > 1 else "Compressly"
    if ".zip" in zip_name:
        zip_name = zip_name.replace(".zip", "")
    zip_name_with_ext = zip_name + ".zip"
    if os.path.exists(zip_name_with_ext):
        os.remove(zip_name_with_ext)
    shutil.make_archive(zip_name, 'zip', 'dist/Compressly')
    print(f"{zip_name_with_ext} created.")

if __name__ == "__main__":
    cd_repo_root()
    run_pyinstaller()
    create_licensing_files()
    compress_to_archive(sys.argv)