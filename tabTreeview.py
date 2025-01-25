from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTabWidget,QTabBar,QHeaderView,QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from tabTreeview_btn_img import TabTreeview_btn
from json_editor import JsonEditor
import json

def load_json(json_file, PC_id):
  """JSON 파일 로드."""
  try:
      with open(json_file, "r", encoding="utf-8") as f:
          return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
      print(f"{PC_id} json 파일을 찾을 수 없음")
  
# 탭 클래스
class Tab(QWidget):
    def __init__(self,tab_name, tab_container, tab_contents,show_context_menu):
        super().__init__()
        self.tab_name = tab_name  # 탭 이름 설정
        self.tab_container = tab_container
        self.sio = None
        self.pcList = None
        self.character_list=None
        self.rowId={} #{"아이디":rowId}
        self.character_list={}
        self.tab_contents=tab_contents
        self.show_context_menu=show_context_menu

        # 레이아웃 설정
        self.tab_layout = QHBoxLayout()
        self.left_tab_layout = QVBoxLayout()
        self.right_tab_layout = QVBoxLayout()

        # QTreeWidget 생성
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(5)
        self.tree_widget.setHeaderLabels(["", "Name", "Status", "Log", "다이아"])
        self.tree_widget.setAlternatingRowColors(True)
        self.left_tab_layout.addWidget(self.tree_widget)
        
         # 컬럼별 폭 수동 설정
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.Fixed)  # 첫 번째 컬럼 고정
        self.tree_widget.header().resizeSection(0, 50)  # 첫 번째 컬럼 폭: 50px
        self.tree_widget.header().resizeSection(1, 100)  # 두 번째 컬럼 폭: 100px
        self.tree_widget.header().resizeSection(2, 150)  # 세 번째 컬럼 폭: 150px
        self.tree_widget.header().resizeSection(3, 200)  # 네 번째 컬럼 폭: 200px
        self.tree_widget.header().resizeSection(4, 75)  # 다섯 번째 컬럼 폭: 75px

        # 합산 결과 표시 라벨
        self.sum_label = QLabel("다이아 합계: 0")
        self.sum_label.setAlignment(Qt.AlignRight)
        self.left_tab_layout.addWidget(self.sum_label)

        # 버튼 및 이미지 레이아웃
        self.tabTreeview_btn_img = TabTreeview_btn(self.tab_name,self.rowId, self.tab_container, self.tab_contents, self.show_context_menu)
        self.json_editor = JsonEditor(self.tab_name, self.tab_container, self.tabTreeview_btn_img)

        self.left_tab_layout.addWidget(self.tabTreeview_btn_img)
        self.right_tab_layout.addWidget(self.json_editor)
        self.tab_layout.addLayout(self.left_tab_layout)
        self.tab_layout.addLayout(self.right_tab_layout)

        # 체크박스 상태 변경 이벤트 연결
        self.tree_widget.itemChanged.connect(self.on_check_allOrnot)

        #이미지 테스트용 데이터
        for i in range(10):
          self.tabTreeview_btn_img.image_layout("이해의시계", "00:00", "test.png", "test_gif.gif")  
          
        self.setLayout(self.tab_layout)

    def on_check_allOrnot(self, item, column):
      if column == 0:  # 체크박스 열만 처리
        total_items = self.tree_widget.topLevelItemCount()
        
        # 첫 번째 행 체크박스 상태 변경 시 전체 항목 체크/해제
        if item == self.tree_widget.topLevelItem(0):
          state = item.checkState(0)
          for i in range(1, total_items):
            child_item = self.tree_widget.topLevelItem(i)
            child_item.setCheckState(0, state)

    def update_sum(self):
      """다이아 컬럼의 숫자 합계 업데이트"""
      total = 0
      for i in range(1, self.tree_widget.topLevelItemCount()):
        item = self.tree_widget.topLevelItem(i)
        try:
          total += int(item.text(4))
        except ValueError:
          pass  # 숫자가 아니면 무시
      self.sum_label.setText(f"다이아 합계: {total}")
  
class TabTreeview(QWidget):
  def __init__(self):
    super().__init__()
    self.tab_container = QTabWidget()
    self.tab_layout = QVBoxLayout()
    self.pcList = None
    self.sio = None
    self.pcList = None
    # --- 탭 추가 ---
    self.tab_contents = {}  # 탭 객체 딕트 {"PC01":탭 객체}
    self.add_tabs(self.tab_container)
    self.tab_layout.addWidget(self.tab_container)
    self.setLayout(self.tab_layout)

  def setup_character_list(self, PC_id):
    pass
    # self.character_list=character_list
    # self.tab_contents[PC_id].tabTreeview_btn_img.setup_character_list(character_list)  #버튼 클래스 초기화

  def add_tabs(self, tab_container):
    for i in range(1, 11):
      tab_name = f"PC{i:02d}"
      tab = Tab(tab_name, tab_container, self.tab_contents, self.show_context_menu)
      tab_container.addTab(tab, tab_name)
      self.tab_contents[tab_name] = tab
  
  def addLog(self, log, id, time, flag, PC_id):
    #플래그가 0이면 에러 1이면 상태 메세지로 처리하자
    if flag==0:
      if(id in self.tab_contents[PC_id].rowId):  
        self.tab_contents[PC_id].rowId[id].setText(3,"O")
        self.tab_contents[PC_id].rowId[id].setTextAlignment(2,Qt.AlignHCenter)
        self.tab_contents[PC_id].rowId[id].addChild(QTreeWidgetItem(self.tab_contents[PC_id].rowId[id],["","",time,log]))  
        # 특정 탭 이름만 빨간색으로 변경
        tab_index = self.tab_container.indexOf(self.tab_contents[PC_id])  # 현재 탭의 인덱스 가져오기
        print("tab_index",tab_index)
        if tab_index != -1:  # 유효한 인덱스라면
          self.tab_container.tabBar().setTabTextColor(tab_index, QColor("red"))
        # self.tab_contents[PC_id].tabTreeview_btn_img.complete_task(self.tab_contents[PC_id].tabTreeview_btn_img.last_clicked_button.pop(0))
      else:
        print("없는 아이디")
    elif flag==1:
      if(id in self.tab_contents[PC_id].rowId):  
        self.tab_contents[PC_id].rowId[id].setText(2,time)
        self.tab_contents[PC_id].rowId[id].setText(3,log)
        self.tab_contents[PC_id].rowId[id].setTextAlignment(2,Qt.AlignHCenter)
        # self.tab_contents[PC_id].tabTreeview_btn_img.complete_task(self.tab_contents[PC_id].tabTreeview_btn_img.last_clicked_button.pop(0))
      else:
        print("없는 아이디")
  
  def tree_clear(self, PC_id):
    self.tab_contents[PC_id].tree_widget.clear()

  def populate_data(self, PC_id):
    # name_list=self.character_list.keys()  #{"아이디":핸들 값}
    character_list=load_json(f"./json_files/character_list/{PC_id}.json", PC_id)
    name_list=character_list.keys()

    if name_list==[]:  # 빈 딕셔너리일 경우
      print("name_list가 비어 있음")
    else:
      # 첫 번째 열 첫 번째 행에 전체 체크박스 추가
      header_item = QTreeWidgetItem([""])
      header_item.setFlags(header_item.flags() | Qt.ItemIsUserCheckable)
      header_item.setCheckState(0, Qt.Checked)
      self.tab_contents[PC_id].tree_widget.addTopLevelItem(header_item)
      # 데이터 추가
      for name in name_list:
        self.tab_contents[PC_id].rowId[name] = QTreeWidgetItem(["", name])
        self.tab_contents[PC_id].rowId[name].setFlags(self.tab_contents[PC_id].rowId[name].flags() | Qt.ItemIsUserCheckable)
        self.tab_contents[PC_id].rowId[name].setCheckState(0, Qt.Checked)
        self.tab_contents[PC_id].tree_widget.addTopLevelItem(self.tab_contents[PC_id].rowId[name])
        #컬럼 테스트용 데이터
        self.tab_contents[PC_id].rowId[name].setText(2,"아이템")
        self.tab_contents[PC_id].rowId[name].setText(3,"무야호")
        self.tab_contents[PC_id].rowId[name].setText(4,"220")
      # 합계 업데이트
      self.tab_contents[PC_id].update_sum()
  
  def client_status_label(self, status, PC_id):
    self.tab_contents[PC_id].tabTreeview_btn_img.client_status.setText(status)
    if status=="Client Status:ON":
      self.tab_contents[PC_id].tabTreeview_btn_img.client_status.setStyleSheet("color: green;")
    else:
      self.tab_contents[PC_id].tabTreeview_btn_img.client_status.setStyleSheet("color: red;")
  
  #---컨텍스트 메뉴 (버튼 오른쪽 클릭 메뉴 및 동작)
  def show_context_menu(self, position):
    clicked_button = self.sender()  # 이벤트를 보낸 버튼
    button_name=clicked_button.text()
    
    if not clicked_button:  # 버튼이 없으면 종료 (버튼이 없을 일이 있나? 뭐지 이거)
      return
    
    print("컨텍스트메뉴객체: ",clicked_button)
    # QMenu 생성
    menu = QMenu(self)
    # 메뉴 항목 추가
    action1 = menu.addAction(f"{button_name} 실행")

    # 클릭된 버튼의 위치를 전역 좌표로 변환
    global_position = clicked_button.mapToGlobal(position)  #오른쪽 클릭 했을 때 메뉴가 나오는 마우스 좌표

    # 메뉴 실행
    action = menu.exec_(global_position)

    # 선택된 항목 확인
    if action == action1:
      for computer_id in self.tab_contents.keys():
        self.tab_contents[computer_id].tabTreeview_btn_img.send_to_command()   
        # self.start_animation(clicked_button)  # 애니메이션 추가
  
  def stop_animation(self,btn_name,computer_id):
    button_name=btn_name

    # 작업 완료 시 애니메이션 중지 및 버튼 복원
    animation =  self.tab_contents[computer_id].tabTreeview_btn_img.animations.pop(button_name)  # 애니메이션 제거
    animation.stop()
    # print("last_clicked_button: ",self.tab_contents[computer_id].tabTreeview_btn_img.last_clicked_button)
    self.tab_contents[computer_id].tabTreeview_btn_img.last_clicked_button[button_name].setStyleSheet("background-color: none;")
    self.tab_contents[computer_id].tabTreeview_btn_img.last_clicked_button[button_name].setEnabled(True)

