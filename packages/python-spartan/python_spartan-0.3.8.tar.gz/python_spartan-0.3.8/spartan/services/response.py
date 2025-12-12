import os
import re


class ResponseService:
    def __init__(self, name: str):
        self.name = name
        self.home_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.current_directory = os.getcwd()
        self.parent_folder = "app"
        self.destination_folder = "responses"
        self.source_stub = os.path.join(
            self.home_directory, "stubs", "response", "default.stub"
        )
        self.file_name = re.sub(r"\d", "", f"{self.name}.py").lower()
        self.file_path = os.path.join(
            self.current_directory,
            self.parent_folder,
            self.destination_folder,
            self.file_name,
        )

    def create_response_file(self):
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

            updated_content = self.update_stub_content(handler_stub_content)

            try:
                with open(self.file_path, "w") as destination_file:
                    destination_file.write(updated_content)
                print(f"File '{self.file_path}' created successfully.")
            except Exception as e:
                print(f"An error occurred while writing the new response file: {e}")
        else:
            print(f"File '{self.file_path}' already exists. Skipping creation.")

    def delete_response_file(self):
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

    def update_stub_content(self, handler_stub_content):
        updated_content = handler_stub_content.replace("{{file_name}}", self.name)
        updated_content = updated_content.replace(
            "{{class_name_title_case_singular}}", self.name.capitalize()
        )
        updated_content = updated_content.replace(
            "{{class_name_lower_case_plural}}", self.name.lower() + "s"
        )
        return updated_content
