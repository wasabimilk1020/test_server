import schedule
import threading
import time

class Scheduler:
  def __init__(self):
    scheduleThread=threading.Thread(target=waiting_schedule)
    scheduleThread.daemon=True
    scheduleThread.start()
    
def waiting_schedule():
    while True:
      schedule.run_pending()
      time.sleep(1)
    
  


