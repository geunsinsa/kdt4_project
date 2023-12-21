from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, QMutex, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
import os, sys
from datetime import datetime
from we_vision.db import Database
import cv2
import pandas as pd
from ultralytics import YOLO
from we_vision.tracker import Tracker
import numpy as np
import time
import threading
import depthai as dai
from we_vision import FirstPage

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    change_text_signal = pyqtSignal(str)
    warning_signal = pyqtSignal(list)
    def __init__(self):
        super().__init__()

        # 파이프라인 생성
        self.pipeline = dai.Pipeline()

        # RGB 카메라 생성
        self.rgb_cam = self.pipeline.createColorCamera()
        self.rgb_cam.setPreviewSize(1280, 720)
        self.rgb_cam.setInterleaved(False)

        # 출력을 위한 XLinkOut 노드 생성
        self.xout = self.pipeline.createXLinkOut()
        self.xout.setStreamName('rgb')
        self.rgb_cam.preview.link(self.xout.input)

        self.cap = None
        self.is_playing = True
        self.mutex = QMutex()
        self.exit_flag = False
        self.__is_recording=False
        self.__height=0
        self.__width=0
        self.text = None

        self.my_file = open("run/yolov8/coco.txt", "r")
        self.data = self.my_file.read()
        self.class_list = self.data.split("\n")
        self.tracker = Tracker()
        self.start_time = None
        self.end_time = None
        self.in_area = False  # 객체의 등장 여부를 나타내는 플래그
        self.warning_color = (0, 0, 255)  # Red color
        self.msg = None

        self.__is_recording_warning = False
        self.__video_writer_warning = None
        self.__is_video_writer_warning_loading=False


        self.__video_writer = None
    def get_detection_text(self):
        return self.text
    def get_widths_heights(self):
        return (self.__width, self.__height)
    def enable_record(self,video_writer):
        self.__video_writer = video_writer
        self.__is_recording = True

    def disable_record(self):
        self.__is_recording = False

    def enable_record_warning(self,video_writer):
        self.__video_writer_warning = video_writer
        self.__is_recording_warning = True

    def disable_record_warning(self):
        self.__is_recording_warning = False

    def run(self):
        with dai.Device(self.pipeline) as device:
            rgb_queue = device.getOutputQueue('rgb', maxSize=1, blocking=False)
            fps = 30
            frame_delay = int(1000/fps)

            while not self.exit_flag:
                self.mutex.lock()
                if self.is_playing:
                    frame = rgb_queue.get().getCvFrame()
                    ret = True
                    detection = self.model.predict(frame,verbose=False)
                    frame = self.conver_image_detection_cv2(frame,detection)
                    self.change_text_signal.emit(self.msg)
                    self.warning_signal.emit([self.start_time,self.end_time])
                    self.mutex.unlock()
                    if ret:
                        self.__width = frame.shape[1]
                        self.__height = frame.shape[0]

                        self.__is_video_writer_warning_loading = True

                        if(self.__is_recording):
                            self.__video_writer.write(frame)

                        if(self.__is_recording_warning):
                            self.__video_writer_warning.write(frame)

                        self.__is_video_writer_warning_loading = False

                        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb_image.shape
                        bytes_per_line = ch * w
                        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        p = convert_to_Qt_format.scaled(self.width, self.height, Qt.KeepAspectRatio)
                        self.change_pixmap_signal.emit(p)
                        cv2.waitKey(frame_delay)
                    else:
                        self.cap.release()

                else:
                    self.mutex.unlock()

                if cv2.waitKey(1) == ord('q'):
                    break

    def is_noend_stream(self):
        return self.__is_video_writer_warning_loading
    def conver_image_detection_cv2(self, frame, results):
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        person_list = []
        person_classes = []
        forklift_list = []
        forklift_classes = []

        _found_detect = {}

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])

            c = self.class_list[d]

            if (c in _found_detect):
                _found_detect[c] += 1
            else:
                _found_detect[c] = 1

            if 'person' in c:
                person_list.append([x1, y1, x2, y2])
                person_classes.append(c)
            elif 'forklift' in c:
                forklift_list.append([x1, y1, x2, y2])
                forklift_classes.append(c)

        if len(_found_detect) > 0:
            self.msg = str(_found_detect)[1:-1]
        else:
            self.msg = "'undefind': 0"

        bbox_idx_forklift = self.tracker.update(forklift_list, forklift_classes)

        for bbox_fork in bbox_idx_forklift:
            x3, y3, x4, y4, _, obj_class = bbox_fork

            cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 0), 2)
            cv2.putText(frame, f'{obj_class}', (x3, y3), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        bbox_idx = self.tracker.update(person_list, person_classes)

        # Warning message
        warning_message = "Warning!"
        blink_interval = 1  # 깜박이는 간격 (초)
        self.in_area = False
        for bbox in bbox_idx:
            x3, y3, x4, y4, _, obj_class = bbox

            cv2.circle(frame, (x3, y4), 4, (255, 0, 255), -1)
            cv2.circle(frame, (x4, y4), 4, (255, 0, 255), -1)
            cv2.putText(frame, f'{obj_class}', (x3, y3), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.line(frame, (x3, y4), (x4, y4), (255, 0, 255), 2)

            # 관심영역에 들어오면 빨간 선으로 바꾸기
            line_points = [(x, y) for x in range(x3, x4 + 1) for y in range(y4, y4 + 1)]
            if any(cv2.pointPolygonTest(np.array(self.area1, np.int32), (point[0], point[1]), False) >= 0 for point in
                   line_points):
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 0, 255), 2)
                self.in_area = True
                # 현재 시간 확인
                current_time = time.time()

                # 현재 시간이 짝수 초인 경우에만 깜박거리도록 함
                if int(current_time) % (2 * blink_interval) < blink_interval:
                    # 화면을 복사하여 새로운 배열을 만듦
                    frame_copy = frame.copy()
                    # 모든 픽셀을 투명한 빨간색으로 설정
                    frame_copy[:, :] = self.warning_color

                    # 원래 프레임에 투명도를 고려하여 더함
                    frame = cv2.addWeighted(frame, 1.0, frame_copy, 0.2, 0.0)

                    # 중앙에 "경고" 메시지 표시 (텍스트 크기 및 두께 조절)
                    text_size = 5
                    text_thickness = 10
                    (text_width, text_height), baseline = cv2.getTextSize(warning_message, cv2.FONT_HERSHEY_SIMPLEX,
                                                                          text_size, text_thickness)

                    text_x = int((frame.shape[1] - text_width) / 2)
                    text_y = int((frame.shape[0] + text_height) / 2)

                    cv2.putText(frame, warning_message, (text_x, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), text_thickness)
            else:
                # 경고상황이 아닐 경우 흰색바운딩박스주기
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 255, 255), 2)

        if self.in_area and self.start_time is None:
            # 객체가 처음으로 인식되기 시작한 시간을 저장
            self.start_time = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
            self.end_time = None  # 다시 영역에 들어오면 이전의 end_time을 초기화
        elif not self.in_area and self.start_time is not None and self.end_time is None:
            # 객체가 모두 영역을 빠져나가면 사라짐 시간을 저장
            self.end_time = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
            self.start_time = None  # 다음 시작 시간을 위해 초기화

        # area1그리기
        cv2.polylines(frame, [np.array(self.area1, np.int32)], True, (0, 0, 255), 2)  # 색상, 두께
        return frame
    def set_video(self, width, height, model, area):
        self.width = width
        self.height = height
        self.model = model
        self.area1 = area
    def play(self):
        self.is_playing = True

    def stop(self):
        self.is_playing = False

    def exit(self):
        self.exit_flag = True
        self.wait()
        cv2.destroyAllWindows()


class VideoThread2(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.is_playing = True
        self.mutex = QMutex()
        self.exit_flag = False
        self.__is_recording=False
        self.__height=0
        self.__width=0


        self.__video_writer = None

    def get_widths_heights(self):
        return (self.__width, self.__height)

    def enable_record(self,video_writer):
        self.__video_writer=video_writer
        self.__is_recording=True

    def disable_record(self):
        self.__is_recording=False


    def run(self):
        self.cap = cv2.VideoCapture(self.filename)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_delay = int(1000/30)

        while self.cap.isOpened() and not self.exit_flag:
            self.mutex.lock()
            if self.is_playing:
                ret, frame = self.cap.read()
                self.mutex.unlock()
                if ret:

                    self.__width = frame.shape[1]
                    self.__height = frame.shape[0]

                    if(self.__is_recording):
                        self.__video_writer.write(frame)
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    p = convert_to_Qt_format.scaled(self.width, self.height, Qt.KeepAspectRatio)
                    self.change_pixmap_signal.emit(p)
                    cv2.waitKey(frame_delay)
                else:
                    self.cap.release()
            else:
                self.mutex.unlock()
        pass


    def set_video(self, filename, width, height):
        self.filename = filename
        self.width = width
        self.height = height

    def play(self):
        self.is_playing = True

    def stop(self):
        self.is_playing = False


    def exit(self):
        self.exit_flag = True
        self.wait()
        cv2.destroyAllWindows()

class MainWindow(QMainWindow):
    def __init__(self,model, conn_params, area):
        super().__init__()
        self.model = model

        self.db = Database(conn_params)
        self.stime = None
        self.etime = None
        self.path = None
        self.cls = None
        self.area = area
        self.tbl_num = 1

        self.stime_warning = None
        self.etime_warning = None
        self.path_warning = None
        self.cls_warning = None
        self.opt = 0
        self.final_stime_warning = None
        self.warning_flag = False

        # 제목과 아이콘 설정
        self.setWindowTitle('실시간 위험 감지 프로그램')
        self.setWindowIcon(QIcon('../data/bee.png'))

        # 화면 전체 레이아웃
        layout = QHBoxLayout()

        # 영상과 버튼 담는 레이아웃 창(layout에 포함 됨)
        left_layout = QVBoxLayout()

        self.displayer = QLabel(self)
        self.displayer.setScaledContents(True)
        self.setLayout(layout)

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_video)
        self.thread.change_text_signal.connect(self.update_text)
        self.thread.warning_signal.connect(self.update_time)
        self.thread.set_video(1280, 720, self.model,self.area)
        self.thread.start()

        # 녹화 상태를 나타내는 변수
        self.recording = False
        self.video_writer = None
        self.video_writer_warning = None

        self.function = QHBoxLayout()
        self.exit_button = QPushButton('종료')
        self.exit_button.clicked.connect(self.homepage)
        self.exit_button.setFixedHeight(60)

        self.record_button = QPushButton('녹화')
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setFixedHeight(60)

        self.open_folder_button = QPushButton('폴더')
        self.open_folder_button.clicked.connect(self.open_file1)
        self.open_folder_button.setFixedHeight(60)

        self.function.addWidget(self.record_button, 2)
        self.function.addWidget(self.open_folder_button, 2)
        self.function.addWidget(self.exit_button, 1)

        left_layout.addWidget(self.displayer, 6)
        left_layout.addLayout(self.function)

        self.displayer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addLayout(left_layout, 3)

        tbl_layout = QVBoxLayout()

        self.textFile = QPlainTextEdit()
        tbl_layout.addWidget(self.textFile, 1)

        # tbl_layout 하단 tbl_warning 데이터 입력을 위한 객체 생성
        self.tbl_warning = QTableWidget(self.tbl_num, 4)
        hLabels = ['시작 시간', '종료 시간', '파일 경로', '구분']  # Column names
        self.tbl_warning.setHorizontalHeaderLabels(hLabels)  # Set column names
        self.tbl_warning.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tbl_warning.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tbl_warning.itemDoubleClicked.connect(self.on_item_double_clicked)

        # tbl_layout에서 tbl_warning 추가
        tbl_layout.addWidget(self.tbl_warning, 3)

        # 전체 layout에서 tbl_layout 추가하기
        layout.addLayout(tbl_layout, 2)

        # Create a QWidget instance and set the layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.center_window()
    def homepage(self):
        self.first = FirstPage()
        self.first.show()
        self.close()
        self.thread.stop()
    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        center_point.setX(center_point.x() - 500)  # Adjust this value as needed
        center_point.setY(center_point.y() - 150)  # Adjust this value as needed
        frame_geometry.moveCenter(center_point)
        self.setGeometry(frame_geometry)  # Set the geometry without moving
        self.resize(2000, 700)  # Adjust the width and height as needed
    def on_item_double_clicked(self, item):
        # item은 더블클릭한 셀에 해당하는 QTableWidgetItem입니다.
        if item.column() == 2:  # 파일 경로 열에 해당하는 경우
            file_path = item.text()
            self.open_file(file_path)

    def on_exit_button_clicked(self):
        self.db.disconnect()
        self.close()
    def toggle_recording(self):
        current_folder = os.path.dirname(os.path.abspath(__file__))
        # videoData 폴더 경로
        video_data_folder = os.path.join(current_folder, 'recordVideo')
        if not os.path.exists(video_data_folder):
            os.makedirs(video_data_folder)

        file_count = len(os.listdir(video_data_folder))
        self.cls = '사용자'
        if not self.recording:
            print("사용자 녹화 시작")
            self.stime = str(datetime.now())
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_path = os.path.join(video_data_folder, f'user_{file_count + 1}.avi')  # 경로를 올바르게 설정
            self.path = video_path
            size__ = self.thread.get_widths_heights()
            self.video_writer = cv2.VideoWriter(video_path, fourcc, 2, size__)
            self.thread.enable_record(self.video_writer)
            self.record_button.setText('녹화 저장')  # record -> record_button
            self.recording = True
        else:
            print("사용자 녹화 종료")
            self.recording = False
            self.etime = str(datetime.now())
            self.thread.disable_record()
            self.video_writer.release()  # 올바르게 릴리스
            self.video_writer = None
            self.record_button.setText('녹화')
            self.update_table()
    def update_table(self):
        data = (self.stime, self.etime, self.path, self.cls)
        self.db.put_tbl_warning(data)

        num, dbData = self.db.get_tbl_warning()
        self.tbl_num = num

        # 현재 테이블의 행 수 확인
        current_row_count = self.tbl_warning.rowCount()

        # 만약 현재 행 수가 가져온 데이터의 행 수와 다르다면 행 수 업데이트
        if current_row_count != self.tbl_num:
            self.tbl_warning.setRowCount(self.tbl_num)

        for row, rowData in enumerate(dbData):
            for col, value in enumerate(rowData):
                item = QTableWidgetItem(str(value))
                self.tbl_warning.setItem(row, col, item)

        # 행의 높이를 동적으로 조절
        self.tbl_warning.resizeRowsToContents()
    def open_file(self,file):
        if file == None:
            fname, _ = QFileDialog.getOpenFileName()
        else:
            fname = file
        if fname:
            self.new_window = QWidget()
            self.new_window.setWindowTitle('녹화 영상')
            self.new_window.resize(1200, 1000)
            self.video_label = QLabel(self.new_window)
            self.play_button = QPushButton('재생', self.new_window)
            self.play_button.setFixedHeight(60)
            self.stop_button = QPushButton('정지', self.new_window)
            self.stop_button.setFixedHeight(60)
            self.new_exit_button = QPushButton('종료(창닫기X 무조건 이걸로 해주세요)')
            self.new_exit_button.setFixedHeight(60)

            self.play_button.clicked.connect(self.play_video)
            self.stop_button.clicked.connect(self.stop_video)
            self.new_exit_button.clicked.connect(self.exit_video)

            # Connect custom_close to the clicked signal of new_exit_button
            self.new_exit_button.clicked.connect(self.custom_close)

            self.v_box = QVBoxLayout()
            self.v_box.addWidget(self.video_label, 4)

            self.h_box = QHBoxLayout()
            self.h_box.addWidget(self.play_button, 1)
            self.h_box.addWidget(self.stop_button, 1)
            self.h_box.addWidget(self.new_exit_button, 1)

            self.v_box.addLayout(self.h_box)
            self.new_window.setLayout(self.v_box)

            self.thread_video = VideoThread2()
            self.thread_video.change_pixmap_signal.connect(self.update_video_label)
            self.thread_video.set_video(fname, self.new_window.width(), self.new_window.height())
            self.thread_video.start()

            self.new_window.show()

    def open_file1(self):
        fname, _ = QFileDialog.getOpenFileName()
        if fname:
            self.new_window = QWidget()
            self.new_window.setWindowTitle('녹화 영상')
            self.new_window.resize(1200, 1000)
            self.video_label = QLabel(self.new_window)
            self.play_button = QPushButton('재생', self.new_window)
            self.play_button.setFixedHeight(60)
            self.stop_button = QPushButton('정지', self.new_window)
            self.stop_button.setFixedHeight(60)
            self.new_exit_button = QPushButton('종료(창닫기X 무조건 이걸로 해주세요)')
            self.new_exit_button.setFixedHeight(60)

            self.play_button.clicked.connect(self.play_video)
            self.stop_button.clicked.connect(self.stop_video)
            self.new_exit_button.clicked.connect(self.exit_video)

            # Connect custom_close to the clicked signal of new_exit_button
            self.new_exit_button.clicked.connect(self.custom_close)

            self.v_box = QVBoxLayout()
            self.v_box.addWidget(self.video_label, 4)

            self.h_box = QHBoxLayout()
            self.h_box.addWidget(self.play_button, 1)
            self.h_box.addWidget(self.stop_button, 1)
            self.h_box.addWidget(self.new_exit_button, 1)

            self.v_box.addLayout(self.h_box)
            self.new_window.setLayout(self.v_box)

            self.thread_video = VideoThread2()
            self.thread_video.change_pixmap_signal.connect(self.update_video_label)
            self.thread_video.set_video(fname, self.new_window.width(), self.new_window.height())
            self.thread_video.start()

            self.new_window.show()

    def custom_close(self):
        if hasattr(self, 'new_window') and self.new_window is not None:
            self.thread_video.exit()
            self.new_window.close()

    def closeEvent(self, event):
        # Your custom close logic goes here
        print("Window close event triggered")
        self.custom_close()  # Call your custom close method
        event.accept()  # This will close the window
    def warning_record(self,time):
        current_folder = os.path.dirname(os.path.abspath(__file__))
        video_data_folder = os.path.join(current_folder, 'recordVideo')
        if not os.path.exists(video_data_folder):
            os.makedirs(video_data_folder)

        # 현재 녹화 파일 개수
        file_count = len(os.listdir(video_data_folder))


        self.cls_warning = '위험 감지' # 구분자
        self.stime_warning = time[0]
        self.etime_warning = time[1]

        # 처음 위험구역에 들어갔는지 아닌지
        if self.stime_warning != None and self.etime_warning == None and self.opt == 0:
            # 첫 위험구역 진입시에만 녹화 flag 작동
            if self.warning_flag == False:
                print("위험 감지 녹화 시작")
                self.warning_flag = True
                self.final_stime_warning = self.stime_warning
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                video_path = os.path.join(video_data_folder, f'warning_{file_count + 1}.avi')  # 경로를 올바르게 설정
                self.path_warning = video_path

                size__ = self.thread.get_widths_heights()

                self.video_writer_warning = cv2.VideoWriter(video_path, fourcc, 2, size__)
                self.thread.enable_record_warning(self.video_writer_warning)

        # 위험구역 나오고 몇 초뒤까지 저장하기 위한 IF문
        elif self.stime_warning == None and self.etime_warning != None and self.warning_flag == True:
            if self.opt <= 20:
                self.opt += 1
            else:
                try:
                    print("위험 감지 녹화 종료")

                    st = threading.Thread(target=self.end_request_event_video_writer, args=(self,))
                    st.start()
                    self.warning_flag = False
                    self.update_table_warning()
                    self.opt = 0
                except Exception as e:
                    print(e)

    def end_request_event_video_writer(self, self2):
        print("StopThread Started!!")
        self2.thread.disable_record_warning()


        while(True):
            print("비디오 이벤트 녹화 플러시가 마무리 되기를 기다리는 중...")
            time.sleep(1)
            if(self2.thread.is_noend_stream()==False):

                break
        print("비디오 이벤트 녹화 플러시가 마무리 됨")


        self2.video_writer_warning.release()  # 올바르게 릴리스
        self2.video_writer_warning = None

    def update_table_warning(self):

        data = (self.final_stime_warning, self.etime_warning, self.path_warning, self.cls_warning)
        self.db.put_tbl_warning(data)

        num, dbData = self.db.get_tbl_warning()
        self.tbl_num = num

        # 현재 테이블의 행 수 확인
        current_row_count = self.tbl_warning.rowCount()

        # 만약 현재 행 수가 가져온 데이터의 행 수와 다르다면 행 수 업데이트
        if current_row_count != self.tbl_num:
            self.tbl_warning.setRowCount(self.tbl_num)

        for row, rowData in enumerate(dbData):
            for col, value in enumerate(rowData):
                item = QTableWidgetItem(str(value))
                self.tbl_warning.setItem(row, col, item)

        # 행의 높이를 동적으로 조절
        self.tbl_warning.resizeRowsToContents()

    @pyqtSlot(list)
    def update_time(self,qt_list):
        self.warning_record(qt_list)
    @pyqtSlot(str)
    def update_text(self,qt_str):
        self.textFile.appendPlainText(qt_str)
    @pyqtSlot(QImage)
    def update_video(self, qt_image):
        self.displayer.setPixmap(QPixmap.fromImage(qt_image))

    @pyqtSlot(QImage)
    def update_video_label(self, qt_image):
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def play_video(self):
        self.thread_video.play()

    def stop_video(self):
        self.thread_video.stop()

    def exit_video(self):
        self.new_window.close()
        self.thread_video.exit()

if __name__ == '__main__':
    conn_params = {
            "host": "172.20.75.214",
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

    window = MainWindow(model, conn_params, [(10,10),(10,20),(10,10),(10,10)])
    window.showMaximized()

    sys.exit(app.exec_())
