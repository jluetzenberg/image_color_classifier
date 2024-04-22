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
import sys
from utils import image_to_lab_histogram, lab_hist_weighed_average, handle_cli
import os
import platform

class ImageDataCell(QtWidgets.QWidget):
    """A cell for the image data. Contains a label for the image and a button to
    add an image. Can be classified as either a control or test image."""

    image_loaded = QtCore.Signal(dict)

    def __init__(self, image_class:str = "control"):
        super().__init__()

        self.image_class = image_class
        self.image_histogram = None
        self.image_averages = (None, None, None)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # add a text label to the layout indicating what class of image this represents
        self.label = QtWidgets.QLabel(f"{image_class.capitalize()} Image:")
        self.layout.addWidget(self.label)

        self.image_path = None
        self.image_label = self.__create_image_picker_label()
        self.layout.addWidget(self.image_label)

    def __create_image_picker_label(self):
        """Creates a label for selecting an image. When no image is selected, the label will display the SP_TitleBarContextHelpButton icon. When an image is selected, the label will display a thumbnail of the image. The user can click on the label to select an image."""
        label = QtWidgets.QPushButton()
        pixmapi = getattr(QtWidgets.QStyle, "SP_TitleBarContextHelpButton")
        icon = self.style().standardIcon(pixmapi)
        label.setIcon(icon)
        label.setFixedSize(100, 100)
        label.clicked.connect(self.add_image)
        return label


    @QtCore.Slot()
    def add_image(self):
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            self.load_image(image_path)

    def get_image_thumbnail(self, image_path):
        """Returns a thumbnail of the image at the specified path, using the QPixmap class."""
        image = QtGui.QPixmap(image_path)
        return image.scaled(100, 100, QtCore.Qt.KeepAspectRatio)

    def load_image(self, image_path):
        """Loads the image from the specified path and updates the image label.
        Also generates the LAB histogram and averages."""
        self.image_path = image_path
        image = self.get_image_thumbnail(image_path)
        #self.image_label.setPixmap(image)
        self.image_label.setIcon(QtGui.QIcon(image_path))
        self.image_label.setIconSize(QtCore.QSize(100,100))
        self.image_histogram = image_to_lab_histogram(image_path)
        self.image_averages = lab_hist_weighed_average(self.image_histogram)
        self.image_loaded.emit({ "img": self.image_path, "averages": self.image_averages})

class RowLabelCell(QtWidgets.QWidget):
    """A cell for the row label and summary. Contains a QLineEdit widget for the
    user to assign a label to the row. Contains a grid showing the average LAB
    values for the control and test images and the difference between the
    two."""
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QtWidgets.QLabel("Label:")
        self.layout.addWidget(self.label)
        self.textbox = QtWidgets.QLineEdit()
        self.layout.addWidget(self.textbox)
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        #self.setMaximumWidth(275)
        self.control_averages = []
        self.test_averages = []
        self.summary = QtWidgets.QGridLayout()
        self.layout.addLayout(self.summary)
        self.update_summary()

    def set_control_image_averages(self, event: dict):
        """Sets the average LAB values for the control image."""
        self.control_averages = event["averages"]
        self.update_summary()

    def set_test_image_averages(self, event: dict):
        """Sets the average LAB values for the test image."""
        self.test_averages = event["averages"]
        self.update_summary()

    def update_summary(self):
        """Shows a simple grid with the average LAB values for the control and test images"""
        # clear the existing summary
        for i in reversed(range(self.summary.count())):
            widget = self.summary.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.summary.addWidget(QtWidgets.QLabel("Control"), 0, 1)
        self.summary.addWidget(QtWidgets.QLabel("Test"), 0, 2)
        self.summary.addWidget(QtWidgets.QLabel("L*"), 1, 0)
        self.summary.addWidget(QtWidgets.QLabel("a*"), 2, 0)
        self.summary.addWidget(QtWidgets.QLabel("b*"), 3, 0)
        for i, value in enumerate(self.control_averages):
            self.summary.addWidget(QtWidgets.QLabel(str(value)), i+1, 1)
        for i, value in enumerate(self.test_averages):
            self.summary.addWidget(QtWidgets.QLabel(str(value)), i+1, 2)


class ImageDataRow(QtWidgets.QWidget):
    """A row for the image data. Contains three cells; one for assigning a label to the data set and two ImageDataCells. """

    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.label = RowLabelCell()
        self.layout.addWidget(self.label)

        self.control_image_cell = ImageDataCell("control")
        self.control_image_cell.image_loaded.connect(self.label.set_control_image_averages)
        self.layout.addWidget(self.control_image_cell)

        self.test_image_cell = ImageDataCell("test")
        self.test_image_cell.image_loaded.connect(self.label.set_test_image_averages)
        self.layout.addWidget(self.test_image_cell)

        self.setMaximumHeight(150)

        self.add_delete_button()
        self.layout.addWidget(self.delete_button)
        self.layout.setAlignment(QtCore.Qt.AlignBottom)

    def add_delete_button(self):
        """Adds a delete button to the row. When clicked, the row will be deleted."""
        self.delete_button = QtWidgets.QPushButton()
        pixmapi = getattr(QtWidgets.QStyle, "SP_TrashIcon")
        icon = self.style().standardIcon(pixmapi)
        self.delete_button.setIcon(icon)
        #self.delete_button.setFixedSize(2*icon.availableSizes()[0])
        self.delete_button.setFixedSize(25,25)
        self.delete_button.setStyleSheet("background-color: red")
        self.delete_button.clicked.connect(self.delete_row)
    
    def delete_row(self):
        """Deletes the row from the list of rows."""
        self.deleteLater()

    def is_complete(self):
        """Returns True if both the control and test images have been added."""
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
        icon = QtGui.QIcon.fromTheme("image-x-generic")
        self.setWindowIcon(icon)

        # set default size of the window to 800x600
        self.resize(600, 600)
        self.setFixedWidth(600)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_scrollable_rows()

        # Create a horizontal layout for the buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.add_row_button = QtWidgets.QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        button_layout.addWidget(self.add_row_button)

        self.generate_report_button = QtWidgets.QPushButton("Generate Report")
        self.generate_report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(self.generate_report_button)
        
        # Add the button layout to the main layout
        self.layout.addLayout(button_layout)

        self.add_row()

    def add_scrollable_rows(self):
        """Adds a scrollable area to the window where rows of image data can be
        added."""
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area_widget = QtWidgets.QWidget()
        self.scroll_area_layout = QtWidgets.QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.layout.addWidget(self.scroll_area)

    def check_generate_report_should_disable(self):
        """Whenever a row is removed, check to see if we have any rows. If there
        are no rows, disable the generate report button"""
        rows = self.rows()
        if len(rows) == 0:
            self.generate_report_button.setDisabled(True)

    def rows(self):
        """Returns the child widgets of the scroll area"""
        return self.scroll_area_widget.findChildren(ImageDataRow)

    @QtCore.Slot()
    def add_row(self):
        row = ImageDataRow()
        row.destroyed.connect(self.check_generate_report_should_disable)
        self.scroll_area_layout.addWidget(row)
        self.generate_report_button.setDisabled(False)

    @QtCore.Slot()
    def generate_report(self):
        """Generates a report of the images. The report will contain average LAB values for the images and the difference between the control and test images. The report will be saved to a CSV file of the user's choice. Each row in the CSV file will contain the following columns: row_label, control_L, control_a, control_b, test_L, test_a, test_b, delta_L, delta_a, delta_b."""
        # build the csv output
        csv_output = []
        rows = self.rows();
        for i in range(len(rows)):
            row = rows[i]
            #if row.is_complete():
            row_label = row.label.textbox.text()
            if not row_label:
                row_label = f"Row {i+1}"
            control_L, control_a, control_b = row.control_image_cell.image_averages
            test_L, test_a, test_b = row.test_image_cell.image_averages
            delta_L, delta_a, delta_b = None, None, None
            if test_L is not None and control_L is not None:
                delta_L = round(test_L - control_L, 3)
                delta_a = round(test_a - control_a, 3)
                delta_b = round(test_b - control_b, 3)
            csv_output.append([row_label, control_L, control_a, control_b, test_L, test_a, test_b, delta_L, delta_a, delta_b])
        # save the csv output to a file
        output_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Report", "", "CSV Files (*.csv)")
        if output_file:
            if not output_file.endswith(".csv"):
                output_file += ".csv"
            with open(output_file, 'w') as f:
                f.write("row_label,control_L,control_a,control_b,test_L,test_a,test_b,delta_L,delta_a,delta_b\n")
                for row in csv_output:
                    f.write(",".join([str(x) for x in row]) + "\n")

        # show the user a dialog indicating that the report has been generated and offering to open the containing folder
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle("Generated")
        dialog.setText("The report has been generated.")
        dialog.setInformativeText("Would you like to open the containing folder?")
        dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)
        result = dialog.exec()
        
        if result == QtWidgets.QMessageBox.Yes:
            folder_path = os.path.dirname(output_file)
            system = platform.system()
            if system == "Linux":
                os.system(f'xdg-open "{folder_path}"')
            elif system == "Darwin":  # macOS
                os.system(f'open "{folder_path}"')
            elif system == "Windows":
                os.system(f'start "" "{folder_path}"')



if __name__ == "__main__":
    # if any arguments were passed in, call the CLI handler
    if len(sys.argv) > 1:
        handle_cli()
    app = QtWidgets.QApplication([])
    window = ImageColorClassifier()
    window.show()
    app.exec()