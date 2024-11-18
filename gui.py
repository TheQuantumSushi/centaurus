# gui.py

# Library imports :
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
import sys
import os
import inspect
import json
import sass

# Module imports :
from LogWriter import LogWriter
from FileSelectorWidget import FileSelectorWidget
from SingleLineTextbox import SingleLineTextbox
from FileManager import FileManager

# Initialize LogWriter :
logger = LogWriter("log.txt")
# Write to log file :
logger.write("ACTION", {"action":"Initialize LogWriter", "invoker":f"file : {os.path.basename(__file__)}", "output":"0"})

# Main window :
class MainWindow(QWidget):
    """
    The GUI window
    """
    def __init__(self, logger):
        """
        Initialize the window and variables
        """
        super().__init__()
        self.method = "file"
        self.logger = logger

        # Write to log file :
        self.logger.write("ACTION", {"action":"Initialize MainWindow", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

        # Load config.json file :
        with open("config.json") as config_file:
            self.config = json.load(config_file)
        # Write to log file :
        self.logger.write("ACTION", {"action":"Load config.json", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        # Window style :
        self.setWindowTitle(' ')
        self.setGeometry(100, 100, 400, 300)
        self.stylesheet = self.compile_stylesheet('config.json')
        self.setStyleSheet(self.stylesheet)
        
        # Main vertical layout
        self.main_layout = QVBoxLayout()
        
        # 1. Layout 1 - Add a title label that stretches in width
        self.layout_1 = QVBoxLayout()

        self.title_label = QLabel("Centaurus")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFixedHeight(70)
        self.title_label.setStyleSheet("background-color: #f44336;")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.layout_1.addWidget(self.title_label)
        
        # 2. Layout 2 - Horizontal split layout with two parts
        self.layout_2 = QHBoxLayout()
        
        # Left part of layout_2 - fixed size with two buttons
        self.left_part = QVBoxLayout()

        self.file_button = QPushButton("Select file")
        self.file_button.setObjectName("file_button")
        self.file_button.setFixedSize(150, 40)
        self.file_button.setStyleSheet("background-color: #f44336;")
        self.file_button.clicked.connect(lambda : self.update_method("file"))

        self.path_button = QPushButton("Input path")
        self.path_button.setObjectName("path_button")
        self.path_button.setFixedSize(150, 40)
        self.path_button.setStyleSheet("background-color: #f44336;")
        self.path_button.clicked.connect(lambda : self.update_method("path"))

        self.left_part.addWidget(self.file_button)
        self.left_part.addWidget(self.path_button)
        
        # Fixed size for left part
        self.left_container = QWidget()  # Container widget to control size
        self.left_container.setLayout(self.left_part)
        self.left_container.setFixedWidth(170)
        
        # Right part of layout_2
        self.right_part = QVBoxLayout()

        self.path_textbox = SingleLineTextbox(is_mandatory = True)
        self.path_textbox.setObjectName("path_textbox")
        self.path_textbox.setFixedHeight(110)
        
        self.file_browser = FileSelectorWidget()
        self.file_browser.setObjectName("file_browser")
        self.file_browser.setStyleSheet("background-color: #f44336;")
        self.file_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.file_browser.setFixedHeight(110)
        
        self.right_part.addWidget(self.file_browser)
        
        # Right container to control size policy
        self.right_container = QWidget()
        self.right_container.setLayout(self.right_part)
        self.right_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Add left and right parts to layout_2
        self.layout_2.addWidget(self.left_container)
        self.layout_2.addWidget(self.right_container)
        
        # 3. Layout 3 - Four lines of text arranged vertically
        self.layout_3 = QVBoxLayout()
        
        self.name_textbox = SingleLineTextbox(placeholder = "Enter content name", is_mandatory = True)
        self.name_textbox.setObjectName("name_textbox")

        self.link_textbox = SingleLineTextbox(placeholder = "Enter TMDB or IMDB link...", is_mandatory = True)
        self.link_textbox.setObjectName("link_textbox")

        self.layout_3.addWidget(self.name_textbox)
        self.layout_3.addWidget(self.link_textbox)
        
        # 4. Layout 4 - Add a single button
        self.layout_4 = QVBoxLayout()
        self.confirm_button = QPushButton("Add torent")
        self.confirm_button.setObjectName("confirm_button")
        self.confirm_button.clicked.connect(self.confirm)
        self.layout_4.addWidget(self.confirm_button)
        
        # Add all sublayouts to the main layout
        self.main_layout.addLayout(self.layout_1)
        self.main_layout.addLayout(self.layout_2)
        self.main_layout.addLayout(self.layout_3)
        self.main_layout.addLayout(self.layout_4)
        
        # Set main layout to the main window
        self.setLayout(self.main_layout)

    def update_method(self, caller : str):
        """
        Update the widget to be a text box or a drag/drop file browser to select a file
        """
        if caller == "path":
            if self.method == "file": # no need to re-add the widget if it was already here
                self.method = "path"
                self.file_browser.setParent(None)
                self.right_part.addWidget(self.path_textbox)
        elif caller == "file":
            if self.method == "path": # no need to re-add the widget if it was already here
                self.method = "file"
                self.path_textbox.setParent(None)
                self.right_part.addWidget(self.file_browser)

    def confirm(self):
        """
        Start the downloading/file managing process
        """
        # Check if file/name/link are provided :
        path = self.file_browser.getSelectedFilePath() if self.method == "file" else self.path_textbox.get_content()
        name = self.name_textbox.get_content()
        link = self.link_textbox.get_content()
        if path and name and link:
            # Working directory :
            base_path = "/home/thomas/Documents"
            # Initialize FileManager :
            filemanager = FileManager(self.logger, "f0ceb830389ee3d912871135d4489911")
            # Extract metadata :
            id_type, id_no = filemanager.extract_id(link)
            if not movie_id:
                print("Error: Could not extract ID from the provided link")
            else:
                data = filemanager.fetch_data(id_type, id_no)
                if data:
                    # Generate NFO content and create folder structure :
                    nfo_content = filemanager.generate_nfo(data)
                    folder_name = movie_data.get("title", "Unknown").replace(" ", "_")
                    filemanager.create_data(base_path, folder_name, path, nfo_content)
                else:
                    print("Error: Could not fetch movie data from TMDb")

    def compile_stylesheet(self, json_file):
        """
        Compile a Scss file into CSS for the window's stylesheet to allow reading variables from config.json
        """
        with open(json_file, 'r') as config_file:
            config = json.load(config_file)
        colors = config["colors"]
        scss_content="""
            $background_color:{background_color};
            $list_background_color:{list_background_color};
            $border_color:{border_color};
            $item_background_color:{item_background_color};
            $selected_item_background_color:{selected_item_background_color};
            $main_text_color:{main_text_color};
            $small_text_color:{small_text_color};
            $button_text_color:{button_text_color};
            $connect_button_color:{connect_button_color};
            $disconnect_button_color:{disconnect_button_color};
            $scroll_border_color:{scroll_border_color};
            QWidget#central_widget {{
                background-color:$background_color;
            }}
            QListWidget {{
                background-color: $list_background_color;
                border:1px solid $border_color;
                padding: 5px;
            }}
            QListWidget::item {{
                background-color: $item_background_color;
                margin: 5px;
                padding: 10px;
                border-radius: 10px;
                color: $border_color;
            }}
            QListWidget::item:selected {{
                background-color: $selected_item_background_color;
            }}
            QLabel#title_label {{
                font-size: 28px;
                font-weight: bold;
                color: $main_text_color;
            }}
            QLabel#status_label {{
                font-size: 18px;
                font-weight: bold;
                color: $small_text_color;
            }}
            QLabel#address_label {{
                font-size: 14px;
                color: $small_text_color;
            }}
            QLabel#location_label {{
                font-size: 14px;
                color: $small_text_color;
            }}
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
            }}
            QPushButton#connect_button {{
                background-color: $connect_button_color;
                color: white;
            }}
            QPushButton#disconnect_button {{
                background-color: $disconnect_button_color;
                color: white;
            }}
            QScrollArea {{
                border: 2px solid $scroll_border_color;
            }}
        """
        scss_formatted = scss_content.format(**colors)
        stylesheet = sass.compile(string=scss_formatted)
        # Write to log file :
        self.logger.write("ACTION", {"action":"Formatted and compiled stylesheet", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        return stylesheet
    
# Start the application :
if __name__ == '__main__':
    # Write to log file :
    logger.write("EVENT", {"event":"Started application","triggered by":f"file : {os.path.basename(__file__)}", "output":"0"})
    # Create the window
    app = QApplication(sys.argv)
    main_window = MainWindow(logger)
    main_window.show()
    # Start the event loop
    sys.exit(app.exec())