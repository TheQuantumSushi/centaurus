from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget, QLabel, QFileDialog
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDrag
from PyQt6.QtCore import QFileInfo
import os
import sys

def handle_file_not_selected():
    print("Error: No file selected.")

def handle_file_not_found():
    print("Error: Selected file no longer exists.")

class FileSelectorWidget(QWidget):
    """
    A file selector PyQT6 widget that supports double clicking to open a file browser,
    or drag-dropping a file. The getSelectedFilePath() method returns either the file path
    as a string, or executes functions provided as arguments if :
    - no file was selected
    - the file was selected, but doesn't exist/can't be found anymore
    """
    # Define PyQT6 signals :
    fileSelected = pyqtSignal(str) # when a file is selected
    fileNotSelected = pyqtSignal() # if no file is selected when accessing path
    fileNotFound = pyqtSignal() # if the selected file no longer can be found when accessing path

    def __init__(self, file_not_selected_error_function : 'function', file_inexistant_error_function : 'function'):
        """
        Initialize the attributes, connect the signals and define the widget
        """
        super().__init__()

        # Connect the signals to their respective functions :
        self.fileNotSelected.connect(file_not_selected_error_function)
        self.fileNotFound.connect(file_inexistant_error_function)

        # Initialize attributes :
        self.selected_file_path = None

        # Define the label with a placeholder text :
        self.label = QLabel("Drag and drop a file here, or double-click to select a file")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 20px;")

        # Define the layout to hold the label :
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Enable drag and drop :
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event : QDragEnterEvent):
        """
        Handle the object being selected through drag and drop by checking if it is
        valid, i.e. :
        - there is an URL
        - it is a local file
        - it isn't a directory
        """
        if event.mimeData().hasUrls(): # check if there is an URL
            url = event.mimeData().urls()[0]
            if url.isLocalFile(): # check if it is a local file
                file_info = QFileInfo(url.toLocalFile())
                if file_info.isFile(): # check if it isn't a directory
                    event.acceptProposedAction() # accept the file for dropping

    def dropEvent(self, event : QDropEvent):
        """
        Handle the object being dropped by extracting the first file from the URL,
        and ensuring it's not a directory
        """
        file_path = event.mimeData().urls()[0].toLocalFile() # get the first file from the dropped URL
        file_info = QFileInfo(file_path) # get its path
        if file_info.isFile(): # check if it isn't a directory
            self.label.setText(f"Selected file : {file_path}") # update the label to display the path of the selected file
            self.selected_file_path = file_path  # store the selected file path
            self.fileSelected.emit(file_path)  # emit the file path
            event.acceptProposedAction() # accept the file

    def mouseDoubleClickEvent(self, event):
        """
        Open a file explorer on double clicking to select a file rather than drag and dropping
        The file explorer only accepts selecting a single object, and only accepts files
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", "", "All Files (*)")
        if file_path: # when a file is selected
            self.label.setText(f"Selected file: {file_path}")
            self.selected_file_path = file_path  # store the selected file path
            self.fileSelected.emit(file_path)  # emit the file path

    def getSelectedFilePath(self) -> str:
        """
        Checks if the selected file exists and sends an error signal or returns the file
        path accordingly
        - if no file is selected, emits the `fileNotSelected` signal
        - if the selected file can no longer be found, emits the `fileNotFound` signal
        Returns the selected file path if it exists; otherwise, an empty string
        """
        # If no file was selected :
        if not self.selected_file_path:
            self.fileNotSelected.emit()
            path = ""
        # If the file can no longer be found :
        elif not os.path.isfile(self.selected_file_path):
            self.fileNotFound.emit()
            path = ""
        # If the file is selected and exists :
        else:
            path = self.selected_file_path
        # Return the string, either empty if there was an error or the path :
        return path

# Example usage :
if __name__ == "__main__":
    # Create the window :
    app = QApplication(sys.argv)
    window = QMainWindow()
    # Create and add the file browser :
    file_selector = FileSelectorWidget()
    window.setCentralWidget(file_selector)
    # Add a button for checking :
    check_button = QPushButton("check file")
    check_button.connect(file_selector.getSelectedFilePath)
    # Show the window :
    window.show()
    # Start the event loop :
    app.exec()