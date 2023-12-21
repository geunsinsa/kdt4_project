import cv2
import sys
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QApplication, QPushButton,QDesktopWidget
from PyQt5.QtCore import Qt, QPoint
from ultralytics import YOLO
from we_vision.second_video import MainWindow_video

class MainWindow_video_bounding(QMainWindow):
    def __init__(self, fname, model, conn_params):
        super().__init__()
        self.model = model
        self.conn_params = conn_params
        self.fname = fname

        self.setWindowTitle('실시간 위험 감지 프로그램')
        self.setWindowIcon(QIcon('../data/bee.png'))

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label,5)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_points)
        self.submit_button.setFixedSize(1280, 50)
        self.layout.addWidget(self.submit_button)

        self.display_first_frame()

        self.points = []
        self.points_cnt = 0

        self.width = 1280
        self.heigth = 720

    def display_first_frame(self):
        cap = cv2.VideoCapture(self.fname)
        if not cap.isOpened():
            print(f"Error: Could not open video file {self.fname}")
            return
        ret, frame = cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.image_label.setPixmap(QPixmap.fromImage(q_image))
        cap.release()
        self.center_window()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()

            # Clamp the x-coordinate to the image width
            x = min(x, self.width)
            print(x)
            # Clamp the y-coordinate to the image height
            y = min(y, self.heigth)
            print(y)
            self.points.append(QPoint(x, y))

            if self.points_cnt <= 3:
                print(self.points)
                self.update_image()
                self.points_cnt += 1
            else:
                self.points_cnt = 0
                self.points = []
    def update_image(self):
        cap = cv2.VideoCapture(self.fname)

        if not cap.isOpened():
            print(f"Error: Could not open video file {self.fname}")
            return

        ret, frame = cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(q_image)
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))

            for i in range(len(self.points)):
                p1 = self.points[i - 1]
                p2 = self.points[i]
                p1_image = self.image_label.mapFrom(self.central_widget, p1)
                p2_image = self.image_label.mapFrom(self.central_widget, p2)
                painter.drawLine(p1_image, p2_image)

            painter.end()
            self.image_label.setPixmap(pixmap)

        cap.release()
    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        center_point.setX(center_point.x() - 300)  # Adjust this value as needed
        center_point.setY(center_point.y() - 150)  # Adjust this value as needed
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    def submit_points(self):
        self.pointsList = []
        for cord in self.points:
            x, y = cord.x(), cord.y()
            self.pointsList.append((x-12, y-12))
        print(self.pointsList)
        self.main_window = MainWindow_video(self.fname, self.model, self.conn_params, self.pointsList)
        self.main_window.show()
        self.close()

if __name__ == '__main__':
    conn_params = {
            "host": "172.20.75.202",
            "port": 3306,
            "user": 'object_detection',
            "password": "object_detection",
            "db": 'object_detection',
            "autocommit": True
        }
    # 모델정의
    custom_model = YOLO('run/yolov8/best.pt')
    model = custom_model

    app = QApplication(sys.argv)

    window = MainWindow_video_bounding('data/test2.mp4', model, conn_params)
    window.show()

    sys.exit(app.exec_())