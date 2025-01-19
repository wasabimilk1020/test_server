from PyQt5.QtWidgets import QTableWidget,QHeaderView,QVBoxLayout,QTableWidgetItem,QWidget
from PyQt5.QtCore import Qt
import random

class ScheduleTable(QWidget):
  def __init__(self):
    super().__init__()
    self.tables=[]  #테이블 객체
    self.emit_schedule_time={}  #{'table_0': ['09:37', '10:43', '14:40', '18:44', '22:19'], 'table_1': ['13:43', '15:37', '16:44', '21:40', '23:44']}
    # 테이블 헤더 설정
    self.table_titles = [
        ["모닝","오전 우편", "오후 우편", "저녁 우편", "밤 우편"],
        ["파괴성채", "크루마탑", "안타라스","시즌패스", "격전의섬"]
    ]
    
    # 메인 레이아웃
    layout = QVBoxLayout()
    # 두 개의 테이블 생성
    for titles in self.table_titles:
      table = self.create_table(titles)
      self.tables.append(table)
      layout.addWidget(table)
    self.setLayout(layout)
      
  def create_table(self, titles):
    table = QTableWidget(1, 5)  # 1행 5열 테이블 생성
    table.setHorizontalHeaderLabels(titles)  # 열 제목 설정
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #수평헤더고 크기가 위젯에 맞춰짐
    table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch) #수직헤더고 크기가 위젯에 맞춰짐
    
    return table
    
  def set_data(self): #데이터를 이 함수를 이용해 세팅해줘야 한다
    pass
  
  def schedule_set_fct(self): 
    print("스케줄 설정 버튼 클릭됨")
    min=[]
    time_list=[]
    for i in range(5):
      min.append(str(random.randint(10, 50))) 
    
    hours_list=[
      ["09","10","14","18","22"],
      ["13","15","16","21","23"] #파괴, 크루마, 안타, 시즌패스, 격섬
    ]
    
    for idx, table in enumerate(self.tables):
      hours=hours_list[idx]
      for column, hour in enumerate(hours):  
        minutes=random.choice(min)
        time=f"{hour}:{minutes}"
        schedule_time=QTableWidgetItem(time)
        schedule_time.setTextAlignment(Qt.AlignCenter)
        table.setItem(0, column, schedule_time)
        time_list.append(time)
      self.emit_schedule_time[f"table_{idx}"]=time_list
      time_list=[]  #리스트 초기화
    print(self.emit_schedule_time)

  