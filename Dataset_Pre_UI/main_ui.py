import sys
from PySide6.QtCore import QFile, Qt, QCoreApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox
)
from lib.VOC_and_YOLO_ui import VOC_and_YOLO
from lib.COCO_and_YOLO_ui import COCO_and_YOLO
from lib.COCO_and_VOC_ui import COCO_and_VOC
from lib.amp_main_ui import Amplification_ui
from lib.segmentation_ui import Segmentation_Ui
from lib.change_imagesize_ui import Change_imagesize_ui

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        qfile = QFile("ui/main_ui.ui")
        qfile.open(QFile.ReadOnly)
        qfile.close()
        self.ui = QUiLoader().load(qfile)
        if not self.ui:
            print(QUiLoader().errorString())
            sys.exit(-1)

        self.VOC_and_YOLO_UI = None
        self.COCO_and_YOLO_UI = None
        self.COCO_and_VOC_UI = None
        self.amp_UI = None
        self.segmentation_UI = None
        self.change_imagesize_UI = None

        self.ui.pushButton_VOC_to_YOLO.clicked.connect(self.open_VOC_and_YOLO_UI)
        self.ui.pushButton_YOLO_to_VOC.clicked.connect(self.open_VOC_and_YOLO_UI)
        self.ui.pushButton_COCO_to_YOLO.clicked.connect(self.open_COCO_and_YOLO_UI)
        self.ui.pushButton_YOLO_to_COCO.clicked.connect(self.open_COCO_and_YOLO_UI)
        self.ui.pushButton_COCO_to_VOC.clicked.connect(self.open_COCO_and_VOC_UI)
        self.ui.pushButton_VOC_to_COCO.clicked.connect(self.open_COCO_and_VOC_UI)
        self.ui.pushButton_amp.clicked.connect(self.open_amp_UI)
        self.ui.pushButton_COCO_to_Labelme.clicked.connect(self.open_segmentation_UI)
        self.ui.pushButton_Labelme_to_COCO.clicked.connect(self.open_segmentation_UI)
        self.ui.pushButton_COCO_to_YOLO_2.clicked.connect(self.open_segmentation_UI)

        self.ui.pushButton_change_size.clicked.connect(self.open_change_size_UI)

    def open_VOC_and_YOLO_UI(self):
        if self.VOC_and_YOLO_UI is None:
            self.VOC_and_YOLO_UI = VOC_and_YOLO()
        # 应用窗口模态
        self.VOC_and_YOLO_UI.ui.setWindowModality(Qt.ApplicationModal)
        self.VOC_and_YOLO_UI.ui.show()

    def open_COCO_and_YOLO_UI(self):
        if self.COCO_and_YOLO_UI is None:
            self.COCO_and_YOLO_UI = COCO_and_YOLO()
        self.COCO_and_YOLO_UI.ui.setWindowModality(Qt.ApplicationModal)
        self.COCO_and_YOLO_UI.ui.show()

    def open_COCO_and_VOC_UI(self):
        if self.COCO_and_VOC_UI is None:
            self.COCO_and_VOC_UI = COCO_and_VOC()
        self.COCO_and_VOC_UI.ui.setWindowModality(Qt.ApplicationModal)
        self.COCO_and_VOC_UI.ui.show()

    def open_amp_UI(self):
        if self.amp_UI is None:
            self.amp_UI = Amplification_ui()
        self.amp_UI.ui.setWindowModality(Qt.ApplicationModal)
        self.amp_UI.ui.show()

    def open_segmentation_UI(self):
        if self.segmentation_UI is None:
            self.segmentation_UI = Segmentation_Ui()
        self.segmentation_UI.ui.setWindowModality(Qt.ApplicationModal)
        self.segmentation_UI.ui.show()

    def open_change_size_UI(self):
        if self.change_imagesize_UI is None:
            self.change_imagesize_UI = Change_imagesize_ui()
        self.change_imagesize_UI.ui.setWindowModality(Qt.ApplicationModal)
        self.change_imagesize_UI.ui.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ui.show()
    sys.exit(app.exec())

