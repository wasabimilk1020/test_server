from PyQt5.QtWidgets import QTableWidget,QHeaderView

class Table(QTableWidget):
  def __init__(self,headerLabel_1,headerLabel_2,headerLabel_3,headerLabel_4):
    super().__init__(2,4)
    
    self.setHorizontalHeaderLabels([headerLabel_1, headerLabel_2, headerLabel_3, headerLabel_4])
    self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.setFixedHeight(90)
    
  def set_data(self): #데이터를 이 함수를 이용해 세팅해줘야 한다
    pass

  # def create_table(self, header_1, header_2, header_3, header_4):
  #   # 테이블 생성 함수. 별도 Table 클래스를 사용.
  #   return Table(header_1, header_2, header_3, header_4)