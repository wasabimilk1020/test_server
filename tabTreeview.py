from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTabWidget,QTabBar,QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from tabTreeview_btn_img import TabTreeview_btn
from json_editor import JsonEditor
import json

def load_json(json_file):
  """JSON 파일 로드."""
  try:
      with open(json_file, "r", encoding="utf-8") as f:
          return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
      return {}  # 파일이 없거나 잘못된 JSON이면 빈 데이터 반환
  
# 탭 클래스
class Tab(QWidget):
    def __init__(self,tab_name, tab_container, tab_contents):
        super().__init__()
        self.tab_name = tab_name  # 탭 이름 설정
        self.tab_container = tab_container
        self.sio = None
        self.pcList = None
        self.character_list=None
        self.rowId={} #{"아이디":rowId}
        self.character_list={}
        self.tab_contents=tab_contents

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
        self.tabTreeview_btn_img = TabTreeview_btn(self.tab_name,self.rowId, self.tab_container, self.tab_contents)
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
        
    def setup_initial_data(self, pcList, sio):
      self.pcList=pcList
      self.sio=sio
      self.tabTreeview_btn_img.setup_data(pcList,sio)  #버튼 클래스 초기화
    
    def setup_character_list(self, character_list):
      self.character_list=character_list
      self.tabTreeview_btn_img.setup_character_list(character_list)  #버튼 클래스 초기화

    def populate_data(self):
      name_list=self.character_list.keys()  #{"아이디":핸들 값}
      
      if name_list==[]:  # 빈 딕셔너리일 경우
        print("name_list가 비어 있음")
      else:
        # 첫 번째 열 첫 번째 행에 전체 체크박스 추가
        header_item = QTreeWidgetItem([""])
        header_item.setFlags(header_item.flags() | Qt.ItemIsUserCheckable)
        header_item.setCheckState(0, Qt.Checked)
        self.tree_widget.addTopLevelItem(header_item)

        # 데이터 추가
        for name in name_list:
          self.rowId[name] = QTreeWidgetItem(["", name])
          self.rowId[name].setFlags(self.rowId[name].flags() | Qt.ItemIsUserCheckable)
          self.rowId[name].setCheckState(0, Qt.Checked)
          self.tree_widget.addTopLevelItem(self.rowId[name])
          
          #컬럼 테스트용 데이터
          self.rowId[name].setText(2,"아이템")
          self.rowId[name].setText(3,"무야호")
          self.rowId[name].setText(4,"220")
          

        # 합계 업데이트
        self.update_sum()

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
    
    def addLog(self, log, id, time, flag):
      #플래그가 0이면 에러 1이면 상태 메세지로 처리하자
      if flag==0:
        if(id in self.rowId):  
          self.rowId[id].setText(3,"O")
          self.rowId[id].setTextAlignment(2,Qt.AlignHCenter)
          self.rowId[id].addChild(QTreeWidgetItem(self.rowId[id],["","",time,log]))  
          # 특정 탭 이름만 빨간색으로 변경
          tab_index = self.tab_container.indexOf(self)  # 현재 탭의 인덱스 가져오기
          if tab_index != -1:  # 유효한 인덱스라면
              self.tab_container.tabBar().setTabTextColor(tab_index, QColor("red"))
          self.tabTreeview_btn_img.complete_task(self.tabTreeview_btn_img.last_clicked_button.pop(0))
        else:
          print("없는 아이디")
      elif flag==1:
        if(id in self.rowId):  
          self.rowId[id].setText(2,time)
          self.rowId[id].setText(3,log)
          self.rowId[id].setTextAlignment(2,Qt.AlignHCenter)
          self.tabTreeview_btn_img.complete_task(self.tabTreeview_btn_img.last_clicked_button.pop(0))
        else:
          print("없는 아이디")
        
        
class TabTreeview(QWidget):
  def __init__(self):
    super().__init__()
    self.tab_container = QTabWidget()
    self.tab_layout = QVBoxLayout()
    # --- 탭 추가 ---
    self.tab_contents = {}  # 탭 객체 딕트 {"PC01":탭 객체}
    self.add_tabs(self.tab_container)
    self.tab_layout.addWidget(self.tab_container)
    self.setLayout(self.tab_layout)
      
  def add_tabs(self, tab_container):
    for i in range(1, 11):
      tab_name = f"PC{i:02d}"
      tab = Tab(tab_name, self.tab_container, self.tab_contents)
      tab_container.addTab(tab, tab_name)
      self.tab_contents[tab_name] = tab
  
  # def schedule_set_fct(self): #이게 왜 여기 있는거야??
  #     print("스케줄 설정 버튼 클릭됨")
