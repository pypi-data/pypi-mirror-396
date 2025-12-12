import os
import re


class RequestService:
    def __init__(self, name: str):
        self.name = name
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.current_directory = os.getcwd()
        self.parent_folder = "app"
        self.destination_folder = "requests"
        self.source_stub = os.path.join(
            self.home_directory, "stubs", "request", "default.stub"
        )
        self.file_name = re.sub(r"\d", "", f"{self.name}.py").lower()
        self.file_path = os.path.join(
            self.current_directory,
            self.parent_folder,
            self.destination_folder,
            self.file_name,
        )

    def create_request_file(self):
        self.create_destination_folder()
        if not os.path.exists(self.file_path):
            try:
                with open(self.source_stub, "r") as source_file:
                    handler_stub_content = source_file.read()
            except FileNotFoundError:
                print(f"Stub file '{self.source_stub}' not found.")
                return
            except Exception as e:
                print(f"An error occurred while reading the stub file: {e}")
                return

            updated_content = handler_stub_content.replace("{{file_name}}", self.name)
            updated_content = updated_content.replace(
                "{{name}}", self.name.capitalize()
            )

            try:
                with open(self.file_path, "w") as destination_file:
                    destination_file.write(updated_content)
                print(f"File '{self.file_path}' created successfully.")
            except Exception as e:
                print(f"An error occurred while writing the new request file: {e}")
        else:
            print(f"File '{self.file_path}' already exists. Skipping creation.")

    def delete_request_file(self):
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
                print(f'File "{self.file_path}" deleted successfully.')
            except Exception as e:
                print(f"An error occurred while trying to delete the file: {e}")
        else:
            print(f'File "{self.file_path}" does not exist. No deletion needed.')

    def create_destination_folder(self):
        destination_folder_path = os.path.join(
            self.current_directory, self.parent_folder, self.destination_folder
        )
        if not os.path.exists(destination_folder_path):
            try:
                os.makedirs(destination_folder_path)
                print(f"Created '{self.destination_folder}' folder.")
            except OSError as e:
                print(f"Error creating directory: {e}")
                return
