from gevent import monkey, pywsgi, spawn, sleep,lock
# monkey.patch_all()
from PyQt5.QtCore import QTimer,pyqtSignal,QObject
from PyQt5.QtWidgets import QApplication
from socketio import Server, WSGIApp
import datetime
from urllib.parse import parse_qs
import sys
from gui_main import MainWindow
import json
import base64
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") # 로깅 설정


class SignalGenerator(QObject):
  user_signal_log = pyqtSignal(object, object, object, object, object)
  user_signal_treeview_populate = pyqtSignal(object)
  user_signal_client_status_label = pyqtSignal(object,object)
  user_signal_stop_animation = pyqtSignal(object,object)
  user_signal_captured_img = pyqtSignal(object,object,object,object)
  user_signal_diamond = pyqtSignal(object, object, object)
  # user_signal_statusChk = pyqtSignal(object)


class WebSocketServer:
  def __init__(self, host='127.0.0.1', port=4000, window=None):
    self.host=host
    self.port=port
    self.sio = Server(async_mode='gevent')
    socketApp = WSGIApp(self.sio)
    self.server = pywsgi.WSGIServer((self.host, self.port), socketApp)
    self.pcList = {}  # 클라이언트 리스트 {"PC01": sid}
    self.cleanup_done=False #정리 작업을 위한 플래그
    self.cleanup_lock=lock.Semaphore()
    self.greenlet=None  #greenlet 저장용
    self.window=window
    self.signal_generator = SignalGenerator()  # SignalGenerator를 속성으로 생성 
    self.signal_generator.user_signal_treeview_populate.connect(window.tab_tree_view.populate_data)
    self.signal_generator.user_signal_log.connect(window.tab_tree_view.addLog)
    self.signal_generator.user_signal_client_status_label.connect(window.tab_tree_view.client_status_label)
    self.signal_generator.user_signal_stop_animation.connect(window.tab_tree_view.stop_animation)
    self.signal_generator.user_signal_captured_img.connect(window.tab_tree_view.image_layout)
    self.signal_generator.user_signal_diamond.connect(window.tab_tree_view.diamond_update_sum)
    # self.signal_generator.user_signal_statusChk.connect(window.tab_tree_view.diamond_update_sum)


    # 이벤트 핸들러 등록
    self.sio.on('connect', self.connect)
    self.sio.on('disconnect', self.disconnect)
    self.sio.on('ping', self.handle_ping)
    self.sio.on("revAccount", self.revAccount)
    self.sio.on("logEvent", self.logEvent)
    self.sio.on("stop_animation", self.stop_animation)
    self.sio.on("captured_image", self.captured_image)
    self.sio.on("get_diamond", self.get_diamond)
  
  def connect(self, sid, environ):
    query_string = environ.get("QUERY_STRING")
    query_params = parse_qs(query_string)
    computer_id = query_params["computer_id"][0]  # "PC01"
    self.pcList[computer_id] = sid  #클라이언트 리스트 생성

    self.signal_generator.user_signal_treeview_populate.emit(computer_id)  #어카운트 세팅
    self.signal_generator.user_signal_client_status_label.emit("Client Status:ON",computer_id)
    window.tab_tree_view.tab_contents[computer_id].tabTreeview_btn_img.setup_data(self.pcList, self.sio)  #버튼 클래스 pcList setup
    window.send_to_image.setup_data(self.sio)
   
    print(f"connect {computer_id} 클라이언트", sid)

  #어떤 컴퓨터의 요청인지 sid로 구분
  def get_computer_id(self,sid):
    for computer_id in self.pcList.keys():  
      if(self.pcList[computer_id] == sid):
        return computer_id
      
  def disconnect(self, sid):
    print("클라이언트 연결 끊김")
    computer_id=self.get_computer_id(sid)
    self.signal_generator.user_signal_client_status_label.emit("Client Status:OFF",computer_id)
    # self.tab_contents[computer_id].tabTreeview_btn_img.checkStatusRun(False)
    #여기서 checkStatusRun(False)를 해줘야 하는데 btn클래스 안에 있어서 호출을 못함 나중에 treeview로 뺴서하자
   

  def handle_ping(self, sid, data):
    # logging.info(f"Received ping from {sid}: {data['time']}")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.sio.emit('pong', {"time": f"{current_time}"}, to=sid)
  
  #set up 버튼으로 캐릭터리스트를 갱신함
  def revAccount(self, sid, data):
    character_list=data  #{"아이디":핸들 값...}
    computer_id=self.get_computer_id(sid)
    
    try:
      with open(f"./json_files/character_list/{computer_id}.json", "w", encoding="utf-8") as json_file:
        json.dump(character_list, json_file, indent=4, ensure_ascii=False)
        json_file.flush()  # OS 버퍼에 있는 내용을 즉시 디스크에 반영
        os.fsync(json_file.fileno())  # 디스크 기록 완료 보장
      self.signal_generator.user_signal_treeview_populate.emit(computer_id)
    except Exception as e:
      print(f"Error saving JSON file for {computer_id}: {e}")  

    # self.signal_generator.user_signal_treeview.emit(computer_id)
    
  def logEvent(self, sid, data):
    #[log_message, id, flag]
    log_message=data[0]
    character_name=data[1]
    flag=data[2]
    computer_id=self.get_computer_id(sid)
    
    #현재 시간
    now = datetime.datetime.now()
    nowDatetime=now.strftime('%Y-%m-%d %H:%M')
    self.signal_generator.user_signal_log.emit(log_message,character_name, nowDatetime, flag, computer_id)

  def stop_animation(self, sid, btn_name):
    button_name=btn_name
    computer_id=self.get_computer_id(sid)
    self.signal_generator.user_signal_stop_animation.emit(button_name, computer_id)
  
  def captured_image(self, sid, data):
    id=data[0]
    current_time=data[1]
    img=data[2]
    computer_id=self.get_computer_id(sid)

    image_data = base64.b64decode(img)
    # 파일로 저장
    with open(f"./image_files/{id}.png", "wb") as f:
      f.write(image_data)
    self.signal_generator.user_signal_captured_img.emit(id, current_time, f"./image_files/{id}.png", computer_id)
    # self.tabTreeview_btn_img.image_layout("이해의시계", "00:00", "test.png")  
    
  def get_diamond(self, sid, data):
    diamond=data[0]
    character_name=data[1]
    computer_id=self.get_computer_id(sid)
    self.signal_generator.user_signal_diamond.emit(diamond, computer_id, character_name)

  def cleanup(self):
    with self.cleanup_lock:  # Lock으로 보호 (메인스레드와 그린렛이 동시 접근)
      if self.cleanup_done:
        return
      self.cleanup_done = True  # Cleanup 시작
      print("Cleanup 시작")
      try:
        # 클라이언트 종료 및 서버 종료 로직
        for pc, sid in list(self.pcList.items()):
          print(f"Disconnecting client: {pc}")
          try:
            self.sio.disconnect(sid)
          except Exception as e:
            print(f"Error disconnecting client {sid}: {e}")

        if self.server.started:
          try:
            self.server.stop()
            print("서버가 정상적으로 종료되었습니다.")
          except Exception as e:
            print(f"서버 종료 중 오류 발생: {e}")

        if self.greenlet and not self.greenlet.dead:
          try:
            self.greenlet.kill()
            print("Greenlet이 종료되었습니다.")
          except Exception as e:
            print(f"Greenlet 종료 중 오류 발생: {e}")
      except Exception as e:
            print(f"Cleanup 중 예외 발생: {e}")

  def runServer(self, server):  # 서버 실행
    try:
      print("서버 실행")
      server.serve_forever()  # 서버 실행
    except Exception as e:
        print(f"Server error: {e}")
    finally:
      self.cleanup()  # Gevent Lock을 사용해 안전하게 Cleanup
    
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  # ws_server=WebSocketServer("127.0.0.1", 4000, window)  
  ws_server=WebSocketServer('192.168.50.29', 5000, window)


  # 서버 실행 (Greenlet 스레드)
  ws_server.greenlet = spawn(ws_server.runServer, ws_server.server)  

  window.setup_server(ws_server.cleanup) 
  window.show()

  # PyQt 타이머로 gevent 이벤트 루프 실행
  timer = QTimer()
  timer.timeout.connect(lambda: sleep(0.1))  # gevent 루프 실행
  timer.start(100)  # 100ms마다 실행

  sys.exit(app.exec_())



#run 만들면된다
#statusCheck 스케쥴이 짧을 때 다른 버튼과 겹쳐서 statusChk가 두 번 이상 쌓이면 start가 stop보다 먼지 일어나면서
#같은 key로 뒤에 하나는 덮어씌워진다.즉, 객체가 2개라야 하는대 1개이고 첫 번째 실행만 마치면 객체는 비어 있게 되서 두 번째 실행 때 오류남
