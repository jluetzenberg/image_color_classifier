"""Provides a GUI for classifying images based on their color. The user can load
multiple images related to a surgery into the gui and classify them as pre-op or
post-op. The program will then generate histograms of the LAB values of the
images and save them to a CSV file for further analysis. The program also
generates a summary CSV file that contains the average LAB values of the images
and the difference between the pre-op and post-op images."""

from PySide6 import QtCore, QtWidgets, QtGui

class ImageColorClassifier(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Color Classifier")
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.images = []
        self.image_labels = []
        self.image_buttons = []
        self.image_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.image_layout)
        self.add_image_button = QtWidgets.QPushButton("Add Image")
        self.add_image_button.clicked.connect(self.add_image)
        self.layout.addWidget(self.add_image_button)
        self.classify_button = QtWidgets.QPushButton("Classify Images")
        self.classify_button.clicked.connect(self.classify_images)
        self.layout.addWidget(self.classify_button)
        self.show()

    @QtCore.Slot()
    def add_image(self):
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            image = QtGui.QPixmap(image_path)
            image_label = QtWidgets.QLabel()
            image_label.setPixmap(image)
            self.image_labels.append(image_label)
            self.image_layout.addWidget(image_label)
            self.images.append(image_path)

    def classify_images(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = ImageColorClassifier()
    window.show()
    app.exec_()