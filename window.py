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

from image_histogram import image_to_lab_histogram, lab_hist_weighed_average

class ImageDataCell(QtWidgets.QWidget):
    """A cell for the image data. Contains a label for the image and a button to
    add an image. Can be classified as either a control or test image."""
    def __init__(self, image_class:str = "control"):
        super().__init__()

        self.image_class = image_class
        self.image_histogram = None
        self.image_averages = None

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.image_path = None
        self.image_label = self.__create_image_picker_label()
        self.layout.addWidget(self.image_label)

    def __create_image_picker_label(self):
        """Creates a label for selecting an image. When no image is selected, the label will display the SP_TitleBarContextHelpButton icon. When an image is selected, the label will display a thumbnail of the image. The user can click on the label to select an image."""

        #label = QtWidgets.QLabel()
        #label.setFixedSize(100, 100)
        #label.setStyleSheet("border: 1px solid black")

        #pixmapi = getattr(QtWidgets.QStyle, "SP_TitleBarCloseButton")
        #label.setPixmap(pixmapi)
        #label.mousePressEvent = self.add_image
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

class RowLabelCell(QtWidgets.QWidget):
    """A cell for the row label. Contains a QLineEdit widget for the user to assign a label to the row."""
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QtWidgets.QLabel("Row Label:")
        self.layout.addWidget(self.label)
        self.textbox = QtWidgets.QLineEdit()
        self.layout.addWidget(self.textbox)
        self.layout.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)
        self.setMaximumWidth(200)

class ImageDataRow(QtWidgets.QWidget):
    """A row for the image data. Contains three cells; one for assigning a label to the data set and two ImageDataCells. """

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

        self.setMaximumHeight(150)

        self.add_delete_button()
        self.layout.addWidget(self.delete_button)
        self.layout.setAlignment(QtCore.Qt.AlignBottom)

    def add_delete_button(self):
        """Adds a delete button to the row. When clicked, the row will be deleted."""
        self.delete_button = QtWidgets.QPushButton()
        pixmapi = getattr(QtWidgets.QStyle, "SP_TitleBarCloseButton")
        icon = self.style().standardIcon(pixmapi)
        self.delete_button.setIcon(icon)
        self.delete_button.setFixedSize(2*icon.availableSizes()[0])
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

        # set default size of the window to 800x600
        self.resize(800, 600)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_scrollable_rows()

        self.rows = []
        self.add_row()
        
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

    @QtCore.Slot()
    def add_row(self):
        row = ImageDataRow()
        self.rows.append(row)
        self.scroll_area_layout.addWidget(row)

    @QtCore.Slot()
    def generate_report(self):
        """Generates a report of the images. The report will contain average LAB values for the images and the difference between the control and test images. The report will be saved to a CSV file of the user's choice. Each row in the CSV file will contain the following columns: row_label, control_L, control_a, control_b, test_L, test_a, test_b, delta_L, delta_a, delta_b."""
        # build the csv output
        csv_output = []
        for row in self.rows:
            if row.is_complete():
                row_label = row.label.textbox.text()
                control_L, control_a, control_b = row.control_image_cell.image_averages
                test_L, test_a, test_b = row.test_image_cell.image_averages
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

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ImageColorClassifier()
    window.setMaximumWidth(550)
    window.show()
    app.exec()