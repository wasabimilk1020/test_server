from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QHBoxLayout, QPushButton, QLabel,QMainWindow,QGroupBox,QLineEdit,QGridLayout,QSpinBox,QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap,QMovie,QColor,QStandardItemModel
import sys,json
from PyQt5.QtCore import Qt,QVariantAnimation, QTimer


class ImageViewer(QLabel):
  def __init__(self, image_path):
    super().__init__()
    self.full_pixmap = QPixmap(image_path)  # 전체 이미지
    self.setPixmap(self.full_pixmap.copy(0, 0, 50, 30))  # 일부 이미지만 표시

  def enterEvent(self, event):
    """마우스가 들어왔을 때 전체 이미지를 표시"""
    self.setPixmap(self.full_pixmap.copy(0, 0, 100, 30))
    super().enterEvent(event)

  def leaveEvent(self, event):
    """마우스가 나갔을 때 이미지를 일부만 표시"""
    self.setPixmap(self.full_pixmap.copy(0, 0, 50, 30))
    super().leaveEvent(event)

class GifViewer(QLabel):
  def __init__(self, gif_path):
    super().__init__()
    self.movie = QMovie(gif_path)
    self.setMovie(self.movie)
    # GIF 시작
    self.movie.start()
    # 초기 크기 설정 (작게 표시)
    self.setFixedSize(50, 30)
    self.setScaledContents(True)

  def enterEvent(self, event):
    """마우스가 위로 올려졌을 때 원본 크기로 변경"""
    self.setFixedSize(100, 30)
    super().enterEvent(event)

  def leaveEvent(self, event):
    """마우스가 나갔을 때 작은 크기로 변경"""
    self.setFixedSize(40, 30)
    super().leaveEvent(event)

def load_json(json_file,tab_name):
  """JSON 파일 로드."""
  try:
      with open(json_file, "r", encoding="utf-8") as f:
          return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    print(f"{tab_name} json 파일을 찾을 수 없음")
  
#---이 파일의 메인 클래스
class TabTreeview_btn(QWidget):
  def __init__(self,tab_name,rowId, tab_widget, tab_contents, show_context_menu):
    super().__init__()
    self.tab_name=tab_name
    self.sio=None
    self.pcList=None
    # self.character_list=None
    self.rowId=rowId
    self.tab_widget=tab_widget
    self.tab_contents=tab_contents
    self.show_context_menu=show_context_menu
    self.last_clicked_button={}
    self.character_list=load_json(f"./json_files/character_list/{tab_name}.json", tab_name)
    
    #reset 및 client status 위젯 및 레이아웃 세팅
    self.client_status_layout = QVBoxLayout()
    self.client_status = QLabel("Client Status:OFF")
    self.client_status.setStyleSheet("color: red;")
    self.client_status.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.client_status_layout.addWidget(self.client_status)
    self.status_check = QLabel("Status Check:OFF")
    self.status_check.setStyleSheet("color: red;")
    self.status_check.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.client_status_layout.addWidget(self.status_check)
    
    self.run_cancel_layout=QHBoxLayout()
    self.run_cancel_layout.setAlignment(Qt.AlignLeft)
    self.run_cancel_layout.setContentsMargins(20, 0, 0, 0)
    self.run_btn = QPushButton("Run")
    self.cancel_btn = QPushButton("Cancel")
    self.run_cancel_layout.addWidget(self.run_btn)
    self.run_cancel_layout.addWidget(self.cancel_btn)

    self.client_status_horizontal=QHBoxLayout()
    self.client_status_horizontal.addLayout(self.client_status_layout)
    self.client_status_horizontal.addLayout(self.run_cancel_layout)

    #reset and Set Account buttons
    self.reset_button = QPushButton("reset")
    self.reset_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.reset_button.clicked.connect(self.reset_status_and_log)
    self.set_account=QPushButton("Set Account")
    self.set_account.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    self.set_account.clicked.connect(self.set_account_fct)

    self.status_reset_btn_layout = QHBoxLayout()  #status 라벨과 reset 버튼 메인 레이아웃
    self.status_reset_btn_layout.addLayout(self.client_status_horizontal)
    self.status_reset_btn_layout.addWidget(self.set_account)
    self.status_reset_btn_layout.addWidget(self.reset_button)

    #버튼 그룹박스 위젯에 각각 grid layout 세팅
    self.dungeon_grid_layout = QGridLayout()
    self.routine_grid_layout = QGridLayout()
    self.setting_grid_layout = QGridLayout()
    self.routine_group_btn_layout=QHBoxLayout()
    self.setting_group_btn_layout=QHBoxLayout()
    self.dungeon_group_btn=QGroupBox("던전")
    self.dungeon_group_btn.setLayout(self.dungeon_grid_layout)
    self.routine_group_btn=QGroupBox("루틴")
    self.routine_group_btn.setLayout(self.routine_grid_layout)
    self.setting_group_btn=QGroupBox("세팅")
    self.setting_group_btn.setLayout(self.setting_grid_layout)

    #메인 레이아웃에 세팅
    self.tabTreeView_btn_layout=QVBoxLayout() #여기서는 이게 main layout이다. 이게 main gui에서 원하는 곳에 위치하면된다
    self.tabTreeView_btn_layout.addLayout(self.status_reset_btn_layout)
    self.tabTreeView_btn_layout.addWidget(self.dungeon_group_btn)
    self.tabTreeView_btn_layout.addWidget(self.routine_group_btn)
    self.tabTreeView_btn_layout.addWidget(self.setting_group_btn)

    self.image_main_layout=QHBoxLayout()  #이미지 레이아웃
    self.tabTreeView_btn_layout.addLayout(self.image_main_layout)

    self.setLayout(self.tabTreeView_btn_layout) 

    # 그룹별 버튼 딕셔너리 {"버튼이름":[버튼위젯,데이터]} 
    #주된 용도는 그리드 레이아웃에서 버튼의 갯수를 판단해서 그리드레이아웃을 배치하는대 사용됨
    self.dungeon_buttons = {}
    self.routine_buttons = {}
    self.setting_buttons = {}
    self.animations = {}  #애니메이션 객체를 위한 딕트

    self.add_buttons()  #default button 생성

  def setup_data(self, pcList, sio):
    self.pcList=pcList
    self.sio=sio
  
  def create_button(self, grid_layout, button_list, buttons):
    #buttons=[{버튼속성},{버튼속성}]
    numOfbutton=len(buttons)
    
    # # 버튼 삭제 전에 연결된 애니메이션을 모두 중지하고 제거
    # for button, animation in self.animations.items():
    #     animation.stop()
    # self.animations.clear()
    

    while grid_layout.count():  # GridLayout의 모든 위젯 제거
        item = grid_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()  # 위젯 메모리에서 삭제

    button_list.clear()

    for i in range(numOfbutton):
      button_name=buttons[i]["name"]
      
      #버튼 생성해서 각각의 딕트에 저장해줌
      button = QPushButton(button_name)
      button_list[button_name]=[]
      button_list[button_name].append(button)
      # button.setFixedSize(100, 22)

      # 컨텍스트 메뉴 활성화 (우클릭 이벤트)
      button.setContextMenuPolicy(Qt.CustomContextMenu)
      button.customContextMenuRequested.connect(self.show_context_menu)

      #버튼 클릭 시 동작
      button.clicked.connect(self.send_to_command)
      button.clicked.connect(lambda _, btn=button, btn_name=button_name: self.start_animation(btn, btn_name))
      

      # GridLayout에 버튼을 다시 배치
      for index, (key,value) in enumerate(button_list.items()):
          row = index // 6  # 행 계산
          col = index % 6   # 열 계산
          grid_layout.addWidget(value[0], row, col)
      
      button_list[button_name].append(buttons[i]["x"])
      button_list[button_name].append(buttons[i]["y"])
      button_list[button_name].append(buttons[i]["xRange"])
      button_list[button_name].append(buttons[i]["yRange"])
      button_list[button_name].append(buttons[i]["delay"])
    
  def add_buttons(self):
    try:
      self.buttonsFromJson = load_json(f"./json_files/PC_buttons/{self.tab_name}_btn.json",self.tab_name)
      
      # defaultButton = self.load_buttons(file_path)  # {"그룹이름":[{버튼속성},{버튼속성}]}
      buttonFromJson=self.buttonsFromJson # {"그룹이름":[{버튼속성},{버튼속성}]}
      
      for groupBox_name, buttons in buttonFromJson.items():
        if groupBox_name == "던전":
          self.create_button(self.dungeon_grid_layout, self.dungeon_buttons, buttons)
        elif groupBox_name == "루틴":
          self.create_button(self.routine_grid_layout, self.routine_buttons, buttons)
        elif groupBox_name == "세팅":
          self.create_button(self.setting_grid_layout, self.setting_buttons, buttons)
    except FileNotFoundError:
      print(f"Default buttons file is not found.")
    except json.JSONDecodeError:
      print(f"Error decoding JSON file")
  
  def generate_button_data(self, button_name,button_dict_map,selected_characters,button):
    emit_data={}
    buttonFromJson=self.buttonsFromJson # {"그룹이름":[{버튼속성},{버튼속성}]}
    
    #버튼 데이터
    for groupBox_name, button_dict in button_dict_map.items():
      if groupBox_name in buttonFromJson:
        data_list = button_dict.get(button_name)
        if data_list:
          data_list = data_list[1:]  # 첫 번째 요소 제외
          break
    emit_data[button_name]=data_list
    
    #수행할 캐릭터 데이터
    for name,rowid in self.rowId.items():
      check_state=rowid.checkState(0) #컬럼 0을 가리킴 즉, 체크박스 상태
      if check_state== Qt.Checked:  #체크 된 아이디만 실행
        handle=self.character_list[name]
        selected_characters[name]=handle
        self.last_clicked_button[button_name]=button
    emit_data["character_list"]=selected_characters
    
    return emit_data

  #왼쪽 버튼 클릭 시 이벤트 핸들러  
  def send_to_command(self, button=None, title=None):
    clk_btn=self.sender()
    btn_name=clk_btn.text()

    if btn_name == "스케줄 설정":
      clicked_button=button
      button_name=title
    else:
      clicked_button=clk_btn
      button_name=btn_name
      
    data_list=[]
    selected_characters={}
    character_list=[]
    # emit_data={}
    # buttonFromJson=self.buttonsFromJson # {"그룹이름":[{버튼속성},{버튼속성}]}
    
    # 그룹 이름과 관련된 버튼 데이터를 매핑
    button_dict_map = {
      "던전": self.dungeon_buttons,
      "루틴": self.routine_buttons,
      "세팅": self.setting_buttons,
    }
    
    emit_data=self.generate_button_data(button_name,button_dict_map,selected_characters,clicked_button)
    
    if self.pcList is not None and self.sio is not None:
      sid=self.pcList[self.tab_name]
      #emit_data={"버튼이름":[데이터],"character_list":[{"아이디1":핸들 값1,"아이디2":핸들 값2}]}
      self.sio.emit('button_schedule', emit_data, to=sid)
    else:
      print("set account 필요함")

#---버튼 애니메이션 기능
  def update_button_color(self, color,button):
    # 버튼 배경색 업데이트
    button.setStyleSheet(f"background-color: {color.name()};")

  # def complete_task(self,button):
  #   # 작업 완료 시 애니메이션 중지 및 버튼 복원
  #   if button in self.animations:
  #       animation = self.animations.pop(button)  # 애니메이션 제거
  #       animation.stop()
  #   button.setStyleSheet("background-color: none;")
  #   button.setEnabled(True)

  def start_animation(self,btn, btn_name):
    button=btn
    button_name=btn_name
    # 버튼 클릭 비활성화 (중복 클릭 방지)
    button.setEnabled(False)

    # 애니메이션 생성
    animation = QVariantAnimation(
         self,
         startValue=QColor(255, 255, 255),  # 흰색 (원래 상태)
        endValue=QColor(128, 0, 128),  # 보라색
     )
    animation.setDuration(2000)  # 1초 동안 실행
    animation.valueChanged.connect(lambda color: self.update_button_color(color, button))  # 색상 변경 연결
    animation.setLoopCount(-1)  # 무한 반복
    animation.start()

    self.animations[button_name] = animation # 애니메이션 저장

#---이미지 섹션
  def image_layout(self, character_name, time, image_path, gif_path):
    """
    클라이언트 데이터 기반으로 UI 생성
    :param character_name: 캐릭터 이름 (str)
    :param time: 시간 (str)
    :param image_path: 이미지 경로 (str) 서버에 이미지를 저장해야됨
    :param gif_path: GIF 경로 (str) 서버에 gif를 저장해야함
    """
    # 수직 레이아웃 생성
    image_vertical_box = QVBoxLayout()
    # 캐릭터 이름 QLabel
    name_label = QLabel(character_name)
    image_vertical_box.addWidget(name_label)
    # 시간 QLabel
    time_label = QLabel(time)
    image_vertical_box.addWidget(time_label)
    # 이미지 뷰어
    image_viewer = ImageViewer(image_path)
    image_vertical_box.addWidget(image_viewer)
    # GIF 뷰어
    gif_viewer = GifViewer(gif_path)
    image_vertical_box.addWidget(gif_viewer)
    # 메인 레이아웃에 수직 레이아웃 추가
    self.image_main_layout.addLayout(image_vertical_box)
    
  #트리뷰 Status and Log 초기화 핸들러
  def reset_status_and_log(self):
    for row_id in self.rowId.values():
      row_id.setText(2,"")
      row_id.setText(3,"")
      row_id.takeChildren()
      # 특정 탭 이름만 빨간색으로 변경
      tab_index = self.tab_widget.indexOf(self.tab_contents[self.tab_name])  # 현재 탭의 인덱스 가져오기
      row_id.setCheckState(0,Qt.Checked)
      if tab_index != -1:  # 유효한 인덱스라면
          self.tab_widget.tabBar().setTabTextColor(tab_index, QColor("black"))
  
  def set_account_fct(self):
    pc_name=self.tab_name
    if self.pcList is not None:
      sid=self.pcList.get(pc_name)
      self.sio.emit("reqAccount","어카운트 정보 요청!",to=sid)
    else:
      print("클라이언트가 연결되지 않았습니다.")
   
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = TabTreeview_btn()
  window.show()
  # 예제: 클라이언트에서 호출하여 레이아웃 추가
  window.image_layout("이해의시계", "00:00", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")
  window.image_layout("빛의파편", "00:01", "test.png", "test_gif.gif")


  sys.exit(app.exec_())


