"""Main window for the GUI application. The window contains a central scrollable
area where images can be added. The scrollable area is modeled as
a collection of rows. Each row may have up to two images side by side. The image
on the left will be considered the 'control', while the image on the right will
be considered the 'test'. The user can add a new row to the list by clicking on
the 'Add Row' button. A new row will be added to the bottom of the list. The
empty row will contain two blank image boxes where the user can add images.
There will be a bottom bar for the application that contains a 'Generate Report'
button. When the user clicks on the 'Generate Report' button, the program will
generate histograms of the LAB values of the images and save them to a CSV file
for further analysis. The program also generates a summary CSV file that
contains the average LAB values of the images and the difference between the
control and test images."""

from PySide6 import QtCore, QtWidgets, QtGui
import csv
import os
from PIL import Image, ImageCms
import colorspacious as cs
import matplotlib.pyplot as plt
import termplotlib as tpl

from image_histogram import image_to_lab_histogram, lab_hist_weighed_average

class ImageDataCell(QtWidgets.QWidget):
    """A cell for the image data. Contains a label for the image and a button to add an image. Can be classified as either a control or test image."""
    def __init__(self, image_class:str = "control"):
        super().__init__()

        self.image_class = image_class
        self.image_histogram = None
        self.image_averages = None

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.image_path = None
        self.image_label = QtWidgets.QLabel()
        self.layout.addWidget(self.image_label)

        self.add_image_button = QtWidgets.QPushButton("Add Image")
        self.add_image_button.clicked.connect(self.add_image)
        self.layout.addWidget(self.add_image_button)

    @QtCore.Slot()
    def add_image(self):
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            self.load_image(image_path)

    def load_image(self, image_path):
        self.image_path = image_path
        image = QtGui.QPixmap(image_path)
        self.image_label.setPixmap(image)
        self.image_histogram = image_to_lab_histogram(image_path)
        self.image_averages = lab_hist_weighed_average(self.image_histogram)

class RowLabelCell(QtWidgets.QWidget):
    """A cell for the row label. Contains a QLineEdit widget for the user to assign a label to the row."""
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QtWidgets.QLineEdit()
        self.layout.addWidget(self.label)

class ImageDataRow(QtWidgets.QWidget):
    """A row for the image data. Contains three cells; one for assigning a label to the data set and two ImageDataCells."""

    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.label = RowLabelCell()
        self.layout.addWidget(self.label)

        self.control_image_cell = ImageDataCell("control")
        self.layout.addWidget(self.control_image_cell)

        self.test_image_cell = ImageDataCell("test")
        self.layout.addWidget(self.test_image_cell)

    def is_complete(self):
        return self.control_image_cell.image_path and self.test_image_cell.image_path
    
class ImageColorClassifier(QtWidgets.QWidget):
    """Main window for the GUI application. The window contains a central scrollable
    area where images can be added. The scrollable area is modeled as
    a collection of rows. Each row may have up to two images side by side. The image
    on the left will be considered the 'control', while the image on the right will
    be considered the 'test'. The user can add a new row to the list by clicking on
    the 'Add Row' button. A new row will be added to the bottom of the list. The
    empty row will contain two blank image boxes where the user can add images.
    There will be a bottom bar for the application that contains a 'Generate Report'
    button. When the user clicks on the 'Generate Report' button, the program will
    generate histograms of the LAB values of the images and save them to a CSV file
    for further analysis. The program also generates a summary CSV file that
    contains the average LAB values of the images and the difference between the
    control and test images."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Color Classifier")
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area_widget = QtWidgets.QWidget()
        self.scroll_area_layout = QtWidgets.QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

        self.rows = []
        self.add_row()
        self.add_row_button = QtWidgets.QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        self.layout.addWidget(self.add_row_button)

        self.generate_report_button = QtWidgets.QPushButton("Generate Report")
        self.generate_report_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_report_button)

    @QtCore.Slot()
    def add_row(self):
        row = ImageDataRow()
        self.rows.append(row)
        self.scroll_area_layout.addWidget(row)

    @QtCore.Slot()
    def generate_report(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ImageColorClassifier()
    window.show()
    app.exec_()