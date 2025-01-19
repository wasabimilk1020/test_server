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

class SignalGenerator(QObject):
  user_signal = pyqtSignal(object, object, object,object)
  
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

    # 이벤트 핸들러 등록
    self.sio.on('connect', self.connect)
    self.sio.on('disconnect', self.disconnect)
    self.sio.on('ping', self.handle_ping)
    self.sio.on("revAccount", self.revAccount)
    self.sio.on("logEvent", self.logEvent)
  
  def connect(self, sid, environ):
    print("connect 클라이언트", sid)
    query_string = environ.get("QUERY_STRING")
    query_params = parse_qs(query_string)
    computer_id = query_params["computer_id"][0]  # "PC01"
    self.pcList[computer_id] = sid  #클라이언트 리스트 생성
    window.tab_tree_view.tab_contents[computer_id].setup_initial_data(self.pcList, self.sio)  #탭 클래스 setup

  def disconnect(self, sid):
    print("클라이언트 연결 끊김")

  def handle_ping(self, sid, data):
    print(f"Received ping from {sid}: {data['time']}")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.sio.emit('pong', {"message": f"{current_time}"}, to=sid)
  
  #어떤 컴퓨터의 요청인지 sid로 구분
  def get_computer_id(self,sid):
    for computer_id in self.pcList.keys():  
      if(self.pcList[computer_id] == sid):
        return computer_id
      
  def revAccount(self, sid, data):
    character_list=data  #{"아이디":핸들 값}
    computer_id=self.get_computer_id(sid)
    
    #json으로 character_list를 만들어 놓는 이 부분이 필요 한가??
    try:
      with open(f"./json_files/character_list/{computer_id}.json", "w", encoding="utf-8") as json_file:
        json.dump(character_list, json_file, ensure_ascii=False)
    except Exception as e:
      print(f"Error saving JSON file for {computer_id}: {e}")  
  
    window.tab_tree_view.tab_contents[computer_id].setup_character_list(character_list)  #탭 클래스 character_list 세팅
    self.signal_generator.user_signal.connect(window.tab_tree_view.tab_contents[computer_id].tree_widget.clear)
    self.signal_generator.user_signal.connect(window.tab_tree_view.tab_contents[computer_id].populate_data)
    self.signal_generator.user_signal.emit(None,None,None,None)
    self.signal_generator.user_signal.disconnect()
    
  def logEvent(self, sid, data):
    #[log_message, id]
    log_message=data[0]
    character_name=data[1]
    flag=data[2]
    computer_id=self.get_computer_id(sid)
    
    #현재 시간
    now = datetime.datetime.now()
    nowDatetime=now.strftime('%Y-%m-%d %H:%M')
    self.signal_generator.user_signal.connect(window.tab_tree_view.tab_contents[computer_id].addLog)
    self.signal_generator.user_signal.emit(log_message,character_name, nowDatetime, flag)
    self.signal_generator.user_signal.disconnect()
          
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
  ws_server=WebSocketServer("127.0.0.1", 4000, window)

  # 서버 실행 (Greenlet 스레드)
  ws_server.greenlet = spawn(ws_server.runServer, ws_server.server)  

  window.setup_server(ws_server.cleanup) 
  window.show()

  # PyQt 타이머로 gevent 이벤트 루프 실행
  timer = QTimer()
  timer.timeout.connect(lambda: sleep(0.1))  # gevent 루프 실행
  timer.start(100)  # 100ms마다 실행

  sys.exit(app.exec_())

#스케쥴 테이블 설정 좀 하자
#1. 23시 55분에 초기화 되고 재설정되게 하자. 마지막 스케쥴(현재는 격섬)이 시작되면 window.schedule_table.schedule_set_fct()게 호출되게 하자
#2. 클래에서 진행 중은 빨간색 초록색은 완료로 표시되게 보내줘야 한다.
#3. 즉, 클라쪽 스케쥴 받는 부분 해주자

#run 3번째에는 아이템 분해 즉 1시간30분마다 분해. run도 그렇고 아이템 분해 할떄
#이미지 서치를 어떤 식으로 할지 생각 좀 해보자.
#1. 자동 사냥이 서치 안되면 죽었던지 사냥이 멈춰있는 상태다
#2. 무접속 플레이 확인해보고 있으면 죽어서 마을간거임
#3. 없는데 사냥이 멈춰 있으면 사냥터에 안돌아 가는중...
#4. 2번과 3번 어느쪽이든 절전모드 해제하고 사망페널티 클릭하게 하고 스케쥴 돌릴까?
#5. 사냥 안하고 그냥 멈춰 있어도 사망페널티 클릭은 아무 상관 없음 어차피 그냥 클릭으로 하니가
#6. 그러면 2번을 확인 할 필요가 없는거네? 무조건 스케쥴 사냥할거니가
#7. 결론, 자동사냥이 검색 안되면 사망페널티 클릭하고 스케쥴 사냥 돌아가게 하자
#8. 아이템분해 루틴에서는어떻게 할까?
#9. 자동사냥 없으면 페널티 클릭하고 아이템 분해 후 스케쥴 사냥
#10. 자동 사냥 있으면 바로 아이템 분해

