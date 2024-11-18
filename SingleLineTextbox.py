# SingleLineTextbox.py

# Library imports :
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QPushButton, QLineEdit, QVBoxLayout, QScrollBar
import sys

def default_empty_error_function():
    """
    Default function to handle the fact that the textbox is empty
    """
    QMessageBox.warning(None, "Please input text", "Input is empty")

# Define the Widget class :
class SingleLineTextbox(QWidget):
    """
    A PyQT6 widget that acts as an input textbox which only accepts a single line,
    will display a scrollbar when needed, as well as a placeholder text when empty
    """
    # Define PyQT6 signals :
    empty = pyqtSignal() # if the textbox is empty

    def __init__(self, parent = None, placeholder : str = "Enter input...", width : int = 500, empty_error_function : 'function' = default_empty_error_function, is_mandatory = False):
        """
        Initialize the attributes, connect the signals and define the widget
        """
        super().__init__(parent)

        # Initialize attributes :
        self.empty_error_function = empty_error_function
        self.is_mandatory = is_mandatory
        self.placeholder = placeholder

        # Connect the error function to the signal :
        self.empty.connect(self.empty_error_function)
        
        # Create a QLineEdit widget
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(self.placeholder)
        
        # Set fixed size for the widget
        self.setFixedSize(width, 60)
        
        # Create a layout to hold the line edit widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.line_edit)
        
        # Initialize horizontal scrollbar
        self.scrollbar = QScrollBar(Qt.Orientation.Horizontal, self)
        self.scrollbar.setVisible(False)  # Initially hidden
        layout.addWidget(self.scrollbar)
        
        # Set up event handling
        self.line_edit.textChanged.connect(self.update_scrollbar)

    def update_scrollbar(self):
        """
        Hide/show the scrollbar depending on whether it is needed (text longer than
        size) or not
        """
        # Get the content's width :
        text_width = self.line_edit.fontMetrics().horizontalAdvance(self.line_edit.text())
        # Compare it to the width of the widget :
        if text_width > self.width(): # if the scrollbar is needed
            self.scrollbar.setVisible(True)
            self.scrollbar.setRange(0, text_width - self.width())
            self.scrollbar.setPageStep(self.width())
        else: # if it is not needed
            self.scrollbar.setVisible(False)

    def resizeEvent(self, event):
        """
        Update scrollbar in the event of the widget being resized
        """
        self.update_scrollbar()
        super().resizeEvent(event)

    def get_content(self):
        """
        Get the text that was inputed and handle the case where nothing was inputed
        """
        content = self.line_edit.text()
        if not content and self.is_mandatory:
            self.empty.emit()
        return content

# Example usage :
if __name__ == "__main__":
    # Create the window and a layout :
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    # Create and add the textbox :
    textbox = SingleLineTextbox(is_mandatory = True)
    layout.addWidget(textbox)
    # Create and add a button for checking :
    check_button = QPushButton("check if empty")
    check_button.clicked.connect(textbox.get_content)
    layout.addWidget(check_button)
    # Show the window :
    window.show()
    # Start the event loop :
    app.exec()