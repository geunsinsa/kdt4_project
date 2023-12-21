from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QDesktopWidget
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
import cv2
import depthai as dai
from we_vision import MainWindow
class MainWindow_webcam_bounding(QMainWindow):
    def __init__(self, model, conn_params):
        super().__init__()
        self.model = model
        self.conn_params = conn_params

        self.setWindowTitle('실시간 위험 감지 프로그램')
        self.setWindowIcon(QIcon('../data/bee.png'))

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_points)
        self.layout.addWidget(self.submit_button)

        self.points = []
        self.points_cnt = 0
        self.display_first_frame()

        self.width = 1280
        self.height = 720

    def display_first_frame(self):
        self.pipeline = dai.Pipeline()
        self.rgb_cam = self.pipeline.createColorCamera()
        self.rgb_cam.setPreviewSize(1280, 720)
        self.rgb_cam.setInterleaved(False)


        # Create an XLinkOut node to get the video feed
        self.xout = self.pipeline.createXLinkOut()
        self.xout.setStreamName('rgb')
        self.rgb_cam.preview.link(self.xout.input)

        # Connect to the device and start the pipeline
        with dai.Device(self.pipeline) as device:
            videoQueue = device.getOutputQueue("rgb", maxSize=1, blocking=False)
            frame = None
            while frame is None:
                try:
                    # Grab a frame from the video feed
                    frame = videoQueue.get().getCvFrame()
                except Exception as e:
                    pass

            self.update_image(frame)
            self.center_window()

    def update_image(self, frame):
        self.rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = self.rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(self.rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()

            # Clamp the x-coordinate to the image width
            x = min(x, self.width)
            print(x)
            # Clamp the y-coordinate to the image height
            y = min(y, self.height)
            print(y)
            self.points.append(QPoint(x, y))

            if self.points_cnt <= 3:
                print(self.points)
                self.update_image(self.rgb_frame)
                self.points_cnt += 1
            else:
                self.points_cnt = 0
                self.points = []

    def submit_points(self):
        self.pointsList = []
        for cord in self.points:
            x, y = cord.x(), cord.y()
            self.pointsList.append((x-15, y-15))
        print(self.pointsList)
        self.main_window = MainWindow(self.model, self.conn_params, self.pointsList)
        self.main_window.show()
        self.close()

    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        center_point.setX(center_point.x() - 300)  # Adjust this value as needed
        center_point.setY(center_point.y() - 150)  # Adjust this value as needed
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

# if __name__ == '__main__':
#     conn_params = {
#             "host": "172.20.75.214",
#             "port": 3306,
#             "user": 'object_detection',
#             "password": "object_detection",
#             "db": 'object_detection',
#             "autocommit": True
#         }
#     # 모델정의
#     custom_model = YOLO('yolov8/best.pt')
#     model = custom_model
#
#     app = QApplication(sys.argv)
#
#     window = MainWindow_webcam_bounding(model, conn_params)
#     window.show()
#
#     sys.exit(app.exec_())
