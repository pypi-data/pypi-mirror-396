import os
import subprocess
from pathlib import Path

class CMDTool:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir or os.getcwd())

    # 1. Create a folder
    def create_folder(self, folder_name):
        path = self.base_dir / folder_name
        path.mkdir(parents=True, exist_ok=True)
        return f"Folder created: {path}"

    # 2. Create a file and write content
    def create_file(self, file_path, content=""):
        full_path = self.base_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File created: {full_path}"

    # 3. Append content to file
    def append_to_file(self, file_path, content):
        full_path = self.base_dir / file_path
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"Content appended to: {full_path}"

    # 4. Delete file or folder
    def delete_path(self, path_str):
        full_path = self.base_dir / path_str
        if full_path.is_dir():
            os.rmdir(full_path)
            return f"Folder deleted: {full_path}"
        elif full_path.is_file():
            os.remove(full_path)
            return f"File deleted: {full_path}"
        else:
            return f"Path not found: {full_path}"

    # 5. Execute shell command
    def execute_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            return f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
        except Exception as e:
            return f"Execution failed: {str(e)}"

#tool = CMDTool()
#print(tool.create_folder("test_folder"))
