from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QScrollBar

class SingleLineTextbox(QWidget):
    def __init__(self, parent=None, placeholder: str = "Enter file path...", width: int = 500):
        super().__init__(parent)
        
        # Create a QLineEdit widget
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText(placeholder)
        
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
        # Get the content's width using horizontalAdvance()
        text_width = self.line_edit.fontMetrics().horizontalAdvance(self.line_edit.text())
        
        # Compare it to the width of the widget
        if text_width > self.width():
            # Show the scrollbar if needed
            self.scrollbar.setVisible(True)
            self.scrollbar.setRange(0, text_width - self.width())
            self.scrollbar.setPageStep(self.width())
        else:
            # Hide the scrollbar if not needed
            self.scrollbar.setVisible(False)

    def resizeEvent(self, event):
        # Update scrollbar visibility on resizing
        self.update_scrollbar()
        super().resizeEvent(event)