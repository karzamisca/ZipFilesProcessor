import sys
import os
import zipfile
import shutil
import tempfile
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
)


class ZipExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Zip File Extractor')
        self.setGeometry(400, 150, 400, 200)
        
        layout = QVBoxLayout()

        self.label_input = QLabel("Select Input Folder with ZIP Files", self)
        layout.addWidget(self.label_input)

        self.btn_input = QPushButton("Browse Input Folder", self)
        self.btn_input.clicked.connect(self.select_input_folder)
        layout.addWidget(self.btn_input)

        self.label_output = QLabel("Select Output Folder", self)
        layout.addWidget(self.label_output)

        self.btn_output = QPushButton("Browse Output Folder", self)
        self.btn_output.clicked.connect(self.select_output_folder)
        layout.addWidget(self.btn_output)

        self.btn_extract = QPushButton("Extract ZIP Files", self)
        self.btn_extract.clicked.connect(self.extract_zip_files)
        layout.addWidget(self.btn_extract)

        self.setLayout(layout)
        
        self.input_folder = ""
        self.output_folder = ""

    def select_input_folder(self):
        self.input_folder = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        self.label_input.setText(f"Input Folder: {self.input_folder}")

    def select_output_folder(self):
        self.output_folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        self.label_output.setText(f"Output Folder: {self.output_folder}")

    def clean_file_name(self, name):
        """
        Cleans the file name by:
        - Removing symbols and spaces
        - Preserving non-Latin characters (e.g., Chinese)
        """
        name = re.sub(r'[^\w\.\u4e00-\u9fff]', '', name)  # Remove non-word characters except dots, underscores, and Chinese characters
        return name

    def extract_zip_files(self):
        if not self.input_folder or not self.output_folder:
            QMessageBox.warning(self, "Error", "Please select both input and output folders.")
            return
        
        # Get a list of all zip files in the input directory
        zip_files = [f for f in os.listdir(self.input_folder) if f.endswith('.zip')]
        
        if not zip_files:
            QMessageBox.information(self, "No ZIP Files", "No ZIP files found in the selected folder.")
            return

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Copy and clean ZIP files to the temporary directory
                cleaned_zip_paths = []
                for zip_file in zip_files:
                    zip_path = os.path.join(self.input_folder, zip_file)
                    cleaned_name = self.clean_file_name(zip_file)
                    cleaned_zip_path = os.path.join(temp_dir, cleaned_name)
                    shutil.copy(zip_path, cleaned_zip_path)
                    cleaned_zip_paths.append(cleaned_zip_path)

                # Extract files from the cleaned ZIPs
                for cleaned_zip_path in cleaned_zip_paths:
                    output_dir_name = os.path.splitext(os.path.basename(cleaned_zip_path))[0]
                    output_path = os.path.join(self.output_folder, output_dir_name)

                    os.makedirs(output_path, exist_ok=True)

                    with zipfile.ZipFile(cleaned_zip_path, 'r') as zip_ref:
                        # Manually extract each member to handle spaces and slashes
                        for member in zip_ref.namelist():
                            # Normalize the path to handle mixed slashes and spaces
                            member_path = os.path.join(output_path, member)
                            member_path = os.path.normpath(member_path)

                            # If the member is a directory, ensure it exists
                            if member.endswith('/'):
                                os.makedirs(member_path, exist_ok=True)
                            else:
                                # Ensure the directory exists for the current file
                                member_dir = os.path.dirname(member_path)
                                if not os.path.exists(member_dir):
                                    os.makedirs(member_dir, exist_ok=True)
                                # Extract the file
                                with zip_ref.open(member) as source, open(member_path, 'wb') as target:
                                    target.write(source.read())

                    print(f"Extracted: {cleaned_zip_path} to {output_path}")

            except zipfile.BadZipFile:
                QMessageBox.warning(self, "Error", "One or more ZIP files might be corrupted.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {e}")
        
        QMessageBox.information(self, "Success", "All ZIP files extracted successfully!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    extractor = ZipExtractor()
    extractor.show()
    sys.exit(app.exec())
