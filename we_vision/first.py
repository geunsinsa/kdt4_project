from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from ultralytics import YOLO
from PyQt5.QtCore import Qt
class FirstPage(QWidget):
    def __init__(self):
        super().__init__()

        # DB 연결정보
        self.conn_params = {
            "host": "172.20.75.173",
            "port": 3306,
            "user": 'object_detection',
            "password": "object_detection",
            "db": 'object_detection',
            "autocommit": True
        }

        self.custom_model = YOLO('run/yolov8/best.pt')
        self.model = self.custom_model

        # yolov5 모델 로딩
        self.setWindowTitle('WE VISION')
        self.setWindowIcon(QIcon('../data/bee.png'))
        self.setGeometry(600, 300, 400, 200)

        layout = QVBoxLayout()
        hlayout = QVBoxLayout()

        # 첫 번째 선택 버튼 - 웹캠으로 보기
        self.button1 = QPushButton("웹캠으로 보기", self)
        self.button1.clicked.connect(self.webcam_button_clicked)
        self.button1.setFixedHeight(70)
        hlayout.addWidget(self.button1, 1)

        # 두 번째 선택 버튼 - 영상 불러오기
        self.button2 = QPushButton("영상 불러오기", self)
        self.button2.clicked.connect(self.load_video_button_clicked)
        self.button2.setFixedHeight(70)
        hlayout.addWidget(self.button2, 1)

        self.image = QPixmap('../data/wevi_logo.jpg')  # 경로 문제로 상대경로로 변경함 추후 변경 요망.
        label = QLabel(self)
        label.setPixmap(self.image.scaled(345, 270, Qt.KeepAspectRatio))
        layout.addWidget(label, 6, alignment=Qt.AlignCenter)

        layout.addLayout(hlayout,2)
        self.setLayout(layout)

    # 웹캠 페이지 이동 함수
    def webcam_button_clicked(self):
        from we_vision import MainWindow_webcam_bounding
        self.main_window = MainWindow_webcam_bounding(self.model,self.conn_params)
        self.main_window.show()
        self.close()

    # 영상 페이지 이동 함수
    def load_video_button_clicked(self):
        from we_vision.bouding_video import MainWindow_video_bounding
        self.fname, _ = QFileDialog.getOpenFileName()
        if self.fname:
            self.main_window = MainWindow_video_bounding(self.fname, self.model, self.conn_params)
            self.main_window.show()
            self.close()



if __name__ == '__main__':
    app = QApplication([])
    window = FirstPage()
    window.show()
    app.exec_()
