import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from UI.MainWin import MainWinddow
import sys


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  #qt适应4k高清屏
app = QApplication(sys.argv)
win = MainWinddow()
win.show()
def close_fun():
    sys.exit(0)
    
win.hook_close_win(close_fun)
sys.exit(app.exec_())

