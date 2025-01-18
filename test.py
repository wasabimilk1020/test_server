import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class HoverImage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.image_label = QLabel(self)
        pixmap = QPixmap("test.png")  # 표시할 이미지 경로
        self.image_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
        
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.setWindowTitle("Mouse Hover Example")
        self.resize(220, 220)

        self.hover_window = None

    def enterEvent(self, event):
        if not self.hover_window:
            self.hover_window = QLabel()
            pixmap = QPixmap("test.png")  # 원본 이미지 경로
            self.hover_window.setPixmap(pixmap)
            self.hover_window.setWindowFlags(Qt.ToolTip)  # 말풍선처럼 보이게 설정
            self.hover_window.setAttribute(Qt.WA_TransparentForMouseEvents)  # 마우스 이벤트 무시
            self.hover_window.show()

        # 말풍선 위치 설정
        global_pos = self.mapToGlobal(QPoint(0, 0))
        self.hover_window.move(global_pos + QPoint(self.width(), 0))

    def leaveEvent(self, event):
        if self.hover_window:
            self.hover_window.close()
            self.hover_window = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HoverImage()
    ex.show()
    sys.exit(app.exec_())
