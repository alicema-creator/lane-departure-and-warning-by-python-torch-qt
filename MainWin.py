import os
from PyQt5.QtWidgets import  QMainWindow
import cv2
from .form.mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
import json
from video_process import videoprocess
import time

from imutils.video import FileVideoStream
from imutils.video import FPS
import imutils
import time
from laneDeparture.detect_lane import *
from laneDeparture.preprocessing_image import *
from laneDeparture.lane_marking import *


class MainWinddow(QMainWindow):
    print_debug_signal = pyqtSignal(str) # 用于触发打印调试信息函数
    show_image_signal = pyqtSignal(str) # 用于触发图像处理结果函数
    # 初始化函数
    def __init__(self,parent=None):
        super(MainWinddow,self).__init__(parent)
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)
        # 设置软件名称

        # 设置初始视频源
        self.main_ui.pushButton_login.clicked.connect(self.login_function) # 登录信号
        self.main_ui.pushButton_registe.clicked.connect(self.registe_interface_change) # 进入到注册页面信号
        self.main_ui.pushButton_registe_2.clicked.connect(self.registe_function) # 注册信号
        self.main_ui.pushButton_login_2.clicked.connect(self.backLoginWindow) # 返回到登录界面信号
        self.main_ui.pushButton_open.clicked.connect(self.open_video_function) # 打开本地视频信号
        self.main_ui.pushButton_start.clicked.connect(self.predicte_function) # 开始测试信号
        self.main_ui.pushButton_stop.clicked.connect(self.stop_function) # 停止测试信号
        self.main_ui.pushButton_pause.clicked.connect(self.setpause_function) # 暂停信号
        self.print_debug_signal.connect(self.print_debug) # 文本浏览框打印信号
        self.show_image_signal.connect(self.showimgae) # 显示处理结果信号

        # 设置按钮的宽度和圆角样式
        self.main_ui.pushButton.setStyleSheet("QPushButton {"
                                              "    width: 50px;"  # 设置宽度为 100 像素
                                              "    border-radius: 5px;"  # 设置圆角半径为 10 像素
                                              "    background-color: #4CAF50;"  # 设置背景颜色为绿色
                                              "    color: black;"  # 设置文本颜色为白色
                                              "}")
        # 设置 QLabel 样式表来显示黄色叹号图标



    # 登录槽函数
    def login_function(self):
        # 获取界面账户、密码
        count = self.main_ui.lineEdit_count.text()
        secret = self.main_ui.lineEdit_secret.text()
        # 判断用户信息是否存在
        if count in self.count_dict.keys():
            # 判断密码是否正确
            if self.count_dict[count] == secret:
                # 弹出登录成功窗口
                QMessageBox.information(self,"Tip","登录成功！")
                # 切换页面
                self.main_ui.stackedWidget.setCurrentIndex(2)
            else:
                # 弹出密码错误窗口
                QMessageBox.critical(self,"error","密码错误！")
        else:
            # 弹出账户未注册窗口
            QMessageBox.critical(self,"error","账户未注册！")

    def registe_interface_change(self):
        # 切换页面
        self.main_ui.stackedWidget.setCurrentIndex(1)
        print("registe_interface_change")

    # 注册槽函数
    def registe_function(self):

        # 获取界面账户、密码
        count = self.main_ui.lineEdit_count_2.text()
        secret = self.main_ui.lineEdit_secret_2.text()

        # 判断账户、密码输入是否为空字符串
        if len(count) == 0 or len(secret) == 0:
            # 提示用户重新输入
            QMessageBox.warning(self,"warning","信息无效！")
        else:
            # 忽视用户信息是否存在，重新设置用户信息
            self.count_dict[count] = secret
            # 保存至本地，(如需删除账户信息可直接在UI\form\namelist.json中删除即可)
            with open(r"UI\form\namelist.json","w", encoding='utf-8') as f: ## 设置'utf-8'编码
                f.write(json.dumps(self.count_dict, ensure_ascii=False ,indent=4))  
            QMessageBox.information(self,"Tip","注册成功！")

    def backLoginWindow(self):
        # 切换页面
        self.main_ui.stackedWidget.setCurrentIndex(0)

    # 视频源改变槽函数
    def videosoure_change(self):
        #当视频源发生切换如果视频正在推理需要停止
        if not self.videoprocess.stopped:
            self.videoprocess.stopped = True
            self.clear_label()
        if self.main_ui.comboBox_source.currentIndex() == 0:
            self.main_ui.lineEdit_filepath.setVisible(True)
            self.main_ui.pushButton_open.setVisible(True)

        elif self.main_ui.comboBox_source.currentIndex() == 1:
            self.main_ui.lineEdit_filepath.setVisible(True)
            self.main_ui.pushButton_open.setVisible(True)
    # 打开视频与图片槽函数
    def open_video_function(self):
        # 打开本地路径
        if self.main_ui.comboBox_source.currentIndex() == 0:
            fileName, filetype = QFileDialog.getOpenFileName(self,"选取视频","./videos", "'Video Files (*.mp4 *.avi *.mkv)'") 
        elif self.main_ui.comboBox_source.currentIndex() == 1:
            fileName, filetype = QFileDialog.getOpenFileName(self, '选择图片',"./images", 'Image Files (*.png *.jpg *.jpeg *.gif)')
        # 显示本地路径
        self.main_ui.lineEdit_filepath.setText(fileName)
        # 打印信息
        self.print_debug_signal.emit("{}打开成功，请点击开始按钮！！！".format(fileName))

    # 开始测试
    def predicte_function(self):
        if not self.videoprocess.stopped:
            self.print_debug_signal.emit("已经开启，请关闭后再次开启！！")  
            return
        self.main_ui.pushButton_pause.setVisible(True)
        self.main_ui.pushButton_pause.setText("暂停测试")
        # 是否保存视频
        if self.main_ui.checkBox_save.isChecked():
            self.videoprocess.save_out = True
        else:
            self.videoprocess.save_out = False
        self.videoprocess.filename = self.main_ui.lineEdit_filepath.text()
        # 启动深度学习推理线程
        self.videoprocess.start()
        self.main_ui.pushButton_alarm.setStyleSheet("background-color:rgb(0,255,0);border-radius: 10px; border: 2px groove black;border-style: outset;")
            
    # 暂停测试
    def setpause_function(self):
        if self.videoprocess.is_pause:
            # 当前状态已经暂定
            self.videoprocess.is_pause = False
            self.main_ui.pushButton_pause.setText("暂停测试")
        else:
            self.videoprocess.is_pause = True
            self.main_ui.pushButton_pause.setText("继续测试")
    # 停止测试
    def stop_function(self):
        # 停止深度学习推理线程
        if self.videoprocess.stopped:
            self.print_debug_signal.emit("已经关闭！！")
        else:  
            self.videoprocess.stopped = True
            self.clear_label()
    # 清空标签,恢复初始状态
    def clear_label(self):
        self.main_ui.label_image_source.clear()
        self.main_ui.label_image_source.setText("原视频")
        self.main_ui.label_image_lane.clear()
        self.main_ui.label_image_lane.setText("车道线")
        self.main_ui.label_image_driving.clear()
        self.main_ui.label_image_driving.setText("可行驶区域")
        self.main_ui.label_image_result.clear()
        self.main_ui.label_image_result.setText("识别结果")
        self.main_ui.pushButton_alarm.setStyleSheet("background-color:rgb(150, 150, 150);border-radius: 10px; border: 2px groove black;border-style: outset;")
        self.main_ui.label_fps.setText("FPS: 00.00")
        self.main_ui.pushButton_pause.setVisible(False) # 停止运行后暂停按钮失效

    # 显示界面函数

    def showimgae(self,fps):
        if not self.videoprocess.stopped:
            # 转换格式
            img_source = cv2.cvtColor(self.videoprocess.img_source, cv2.COLOR_BGR2RGB)
            color_lane = cv2.cvtColor(self.videoprocess.color_lane, cv2.COLOR_BGR2RGB)
            color_driving = cv2.cvtColor(self.videoprocess.color_driving, cv2.COLOR_BGR2RGB)
            img_rs = cv2.cvtColor(self.videoprocess.img_rs, cv2.COLOR_BGR2RGB)

            # 显示原图 
            self.main_ui.label_image_source.setPixmap(QPixmap(QImage(img_source.data,img_source.shape[1],img_source.shape[0],QImage.Format_RGB888)))
            self.main_ui.label_image_source.setScaledContents(True)

            # 显示车道线
            self.main_ui.label_image_lane.setPixmap(QPixmap(QImage(color_lane.data,color_lane.shape[1],color_lane.shape[0],QImage.Format_RGB888)))
            self.main_ui.label_image_lane.setScaledContents(True)

            # 显示可行驶区域
            #车道线识别开始
            frame = imutils.resize(self.videoprocess.img_source, width=640)
            preprocessed_image = preprocess_image(frame)
            lane_marking_image = lane_marking_detection(preprocessed_image, True)
            detector = LaneDetector()
            color_driving = detector.process(frame, lane_marking_image)

            # 打开文件以读取模式（'r'）
            with open('aa.txt', 'r') as file:
                # 读取文件中的数据
                data = file.read()
            # 输出读取到的数据


            # cv2.imshow("Screen", color_driving)
            # cv2.waitKey(1)


            # 车道线识别结束


            # self.main_ui.label_image_driving.setPixmap(QPixmap(QImage(color_driving.data,color_driving.shape[1],color_driving.shape[0],QImage.Format_RGB888)))
            # self.main_ui.label_image_driving.setScaledContents(True)
            self.main_ui.label_image_result.setPixmap(QPixmap(QImage(color_driving.data,color_driving.shape[1],color_driving.shape[0],QImage.Format_RGB888)))
            self.main_ui.label_image_result.setScaledContents(True)


            # 显示结果
            # self.main_ui.label_image_result.setPixmap(QPixmap(QImage(img_rs.data,img_rs.shape[1],img_rs.shape[0],QImage.Format_RGB888)))
            # self.main_ui.label_image_result.setScaledContents(True)
            self.main_ui.label_image_driving.setPixmap(QPixmap(QImage(img_rs.data,img_rs.shape[1],img_rs.shape[0],QImage.Format_RGB888)))
            self.main_ui.label_image_driving.setScaledContents(True)
            # 显示帧率
            self.main_ui.label_fps.setText(fps)
        else:
            self.clear_label()

    # 文本框打印信息函数
    def print_debug(self,info):
        self.main_ui.textBrowser_debug.append(info)

    # 注册关闭窗口的回调函数
    def hook_close_win(self, close_fun):
        # 停止深度学习推理线程
        self.videoprocess.stopped = True
        time.sleep(1)
        self.close_fun = close_fun