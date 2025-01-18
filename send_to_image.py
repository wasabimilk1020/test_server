import sys
import base64
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageDropLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("이미지를 드래그 앤 드롭 <br> 혹은  <br> 여기를 클릭하세요")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed gray;")
        self.setScaledContents(True)
        self.image_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.load_image(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "", "이미지 파일 (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                self.load_image(file_path)

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.setText("유효하지 않은 이미지 파일입니다.")
            self.image_path = None
        else:
            self.setPixmap(pixmap)
            self.setText("")
            self.image_path = file_path

class ImageAttachApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("드래그 앤 드롭 및 클릭 첨부")
        self.setGeometry(100, 100, 800, 400)

        # 메인 위젯과 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # 위젯 간 간격 설정
        main_layout.setContentsMargins(10, 5, 10, 5)  # 레이아웃 외부 여백 설정

        # 이미지 라벨을 묶는 수평 레이아웃
        hbox = QHBoxLayout()
        hbox.setSpacing(5)  # 수평 레이아웃 내부 간격 설정
        hbox.setContentsMargins(0, 0, 0, 0)  # 여백 제거

        self.image_label = ImageDropLabel()
        self.image_label.setFixedSize(130, 70)
        hbox.addWidget(self.image_label)

        self.confirm_label = QLabel("확인용 이미지가<br>여기에 표시됩니다")
        self.confirm_label.setAlignment(Qt.AlignCenter)
        self.confirm_label.setStyleSheet("border: 2px solid gray;")
        self.confirm_label.setFixedSize(130, 70)
        self.confirm_label.setScaledContents(True)
        hbox.addWidget(self.confirm_label)

        # 버튼을 아래쪽에 추가
        self.send_button = QPushButton("이미지 전송")
        self.send_button.clicked.connect(self.send_image)

        # 레이아웃 구성
        main_layout.addLayout(hbox)  # 수평 레이아웃 추가
        main_layout.addWidget(self.send_button, alignment=Qt.AlignCenter)  # 버튼은 가운데 정렬
        self.setLayout(main_layout)

        # 이미지 데이터를 저장할 변수
        self.received_data = None

    def send_image(self):
        if self.image_label.image_path:
            with open(self.image_label.image_path, "rb") as f:
                b64_string = base64.b64encode(f.read()).decode("utf-8")
            data = {"image": b64_string}
            print("이미지 데이터 준비 완료:", data)
            self.received_data = data
            self.display_received_image()
        else:
            print("첨부된 이미지가 없습니다.")

    def display_received_image(self):
        if self.received_data:
            b64_string = self.received_data["image"]
            img_data = base64.b64decode(b64_string)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.confirm_label.setPixmap(pixmap)
        else:
            print("수신된 이미지 데이터가 없습니다.")


# 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ImageAttachApp()
    main_window.show()
    sys.exit(app.exec_())
