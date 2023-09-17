



from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtChart import *
from scipy import  signal
import heartpy as hp
import numpy as np
from hrvanalysis import get_time_domain_features
#返回包含HRV分析的时域特征字典，通常用于24h的长期记录，也有些研究在2-5min的短期记录
from hrvanalysis import get_frequency_domain_features
# 返回包含用于HRV分析的频域特征的字典，必须在2-5min的窗口内使用
from hrvanalysis import get_poincare_plot_features
# 返回包含非线性域的3个特征字典，用于HRV分析，必须在5分钟的短期窗口使用
import csv
import joblib
from Ui_mainwindowgraph import Ui_MainWindow
import pandas as pd

class my_ui(Ui_MainWindow):
    def __init__(self):
        super(my_ui,self).__init__()
        self.timer = QTimer()
    def serial_init(self):
        self.ser=QSerialPort()
        port_list = QSerialPortInfo.availablePorts()
        for port in port_list:
            self.ser.setPort(port)
            if(self.ser.open(QIODevice.OpenModeFlag.ReadWrite)):
                self.comboBox.addItem(port.portName())
                # print(port.portName()+'可用')
                # print(self.ser.isOpen())
                self.ser.close()      
        if not port_list:
            self.comboBox.addItem('无串口')
        self.comboBox_2.setCurrentIndex(1)
        self.comboBox_4.setCurrentIndex(3)
        self.radioButton_2.setChecked(1)
        self.textEdit.setPlaceholderText('数据接收区')
        self.comboBox_6.setCurrentIndex(3)
        self.doubleSpinBox.setValue(2.5)
        self.doubleSpinBox_2.setValue(0.7)
        self.lineEdit.setText('10000')

        self.pushButton_3.setCheckable(True)
        self.pushButton_3.toggled.connect(self.pushButton3_slot)
        self.pushButton_4.clicked.connect(self.reception_slot)
        self.pushButton_5.clicked.connect(self.reception_slot)
        self.pushButton_6.clicked.connect(self.reception_slot)
        self.pushButton_7.clicked.connect(self.reception_slot)
        self.pushButton.clicked.connect(self.reception_slot)
        self.pushButton_2.clicked.connect(self.reception_slot)
        self.ser.readyRead.connect(self.readyall_slot) 
        self.checkBox.stateChanged.connect(self.checkBox_slot)
        self.timer.timeout.connect(self.timer_slot)
        self.pushButton_8.clicked.connect(self.pushButton_8_slot)
        self.pushButton_9.clicked.connect(self.pushButton_9_slot)

    def pushButton3_slot(self):

        if self.pushButton_3.isChecked():
            self.ser.setPortName(self.comboBox.currentText())  # 端口是COM3           
            self.ser.setBaudRate(eval(self.comboBox_2.currentText()))  # 设置波特率      
            match self.comboBox_3.currentText():
                case '无':  
                    self.ser.setParity(QSerialPort.Parity.NoParity)#无校验
                    
                case '奇': 
                    self.ser.setParity(QSerialPort.Parity.OddParity)
                case '偶':  
                    self.ser.setParity(QSerialPort.Parity.EvenParity)
                case _:  # Pattern not attempted
                    pass
                    
            match self.comboBox_4.currentText():
                case '5':
                    self.ser.setDataBits(QSerialPort.DataBits.Data5) #5位数据位
                case '6':
                    self.ser.setDataBits(QSerialPort.DataBits.Data6) #6位数据位
                case '7':
                    self.ser.setDataBits(QSerialPort.DataBits.Data7) #7位数据位
                case '8':
                    self.ser.setDataBits(QSerialPort.DataBits.Data8) #8位数据位
                  
            
            match self.comboBox_5.currentText():
                case '1':
                    self.ser.setStopBits(QSerialPort.StopBits.OneStop)#停止位
                    
                case '1.5':
                    self.ser.setStopBits(QSerialPort.StopBits.OneAndHalfStop)#停止位
                case '2':
                    self.ser.setStopBits(QSerialPort.StopBits.TwoStop)#停止位
            self.ser.setFlowControl(QSerialPort.FlowControl.NoFlowControl)
            self.ser.open(QIODevice.OpenModeFlag.ReadWrite)
        else:
            self.ser.close()


    def readyall_slot(self):
        self.serbuff=self.ser.readAll()
        if str(self.serbuff,encoding='utf-8').isdigit():
            if self.radioButton_2.isChecked():
                self.textEdit.insertPlainText(str(self.serbuff,encoding='utf-8')+'\n')#str还可指定编码格式            
            else:
                self.textEdit.insertPlainText(str(self.serbuff.toHex().toInt()[0])+'\n')
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)

            if self.radioButton_2.isChecked():
                self.series.append(self.x,self.serbuff.toFloat()[0])
            else:
                self.series.append(self.x,self.serbuff.toHex().toFloat()[0])
            self.x+=1
        if self.series.count() > 3000:
            self.series.removePoints(0, self.series.count() - 3000)

         

###################################################################################################    
    def chart_init(self):
        self.x=0.0
        #设置自由缩放
        #self.ChartView.setRubberBand(QChartView.RectangleRubberBand)
        self.ChartView.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        self.chart1 = QChart()  # 创建折线视图
        self.chart1.setBackgroundVisible(visible=False)      # 背景色透明
        self.chart1.setBackgroundBrush(QBrush(QColor("#000FFF")))     # 改变图背景色
        #  图形项默认无法接收悬停事件，可以使用QGraphicsItem的setAcceptHoverEvents()函数使图形项可以接收悬停事件。
        # self.chart1.setAcceptHoverEvents(True)
        # 4条折线的坐标值
        # 执行创建折线的函数
        self.series = QLineSeries()
        self.chart1.addSeries(self.series)

        self.chart1.createDefaultAxes()  # 创建默认的轴
        self.chart1.axisX().setRange(0, 4000)
        self.chart1.axisY().setTitleText('数值')
        self.chart1.legend().setVisible(False)
        self.chart1.axisY().setRange(115000, 118000)  # 设置y1轴范围
        self.ChartView.setChart(self.chart1)
########################################################################################################
        self.x2=0.0
        #设置自由缩放
        #self.ChartView_2.setRubberBand(QChartView.RectangleRubberBand)
        
        self.ChartView_2.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        self.chart2 = QChart()  # 创建折线视图
        self.chart2.setBackgroundVisible(visible=False)      # 背景色透明
        self.chart2.setBackgroundBrush(QBrush(QColor("#000FFF")))     # 改变图背景色
        self.series2 = QLineSeries()
        self.chart2.addSeries(self.series2)

        self.chart2.createDefaultAxes()  # 创建默认的轴
        self.chart2.axisX().setRange(0, 1000)
        self.chart2.axisY().setTitleText('数值')
        self.chart2.legend().setVisible(False)
        self.chart2.axisY().setRange(-100,100)  # 设置y1轴范围
        self.ChartView_2.setChart(self.chart2)
        self.chart1.zoom(0.99999)


    
    def reception_slot(self):
        pushbutton = self.sender()
        match pushbutton.text():      
            case '清除数据':
                self.textEdit.clear()
                self.x=0.0
                self.series.clear()
            case '导入数据':
                textFile = QFileDialog().getOpenFileName(self,'读取数据','','TEXT (*txt)')
                if textFile[0]:
                    self.x=0.0
                    self.series.clear()
                    with open(textFile[0],'r') as openfile:
                        my_date = openfile.read()
                        for point in my_date.splitlines():
                            if point.isdigit():
                                self.textEdit.insertPlainText(point+'\n')
                                self.series.append(self.x,float(point))
                                self.x+=1
                self.textEdit.moveCursor(QTextCursor.MoveOperation.End)  
            case '保存数据':
                textFile = QFileDialog().getSaveFileName(self,'保存数据','','TEXT (*txt)')
                if textFile[0]:
                    with open(textFile[0],'w') as save:
                        save.write(self.textEdit.toPlainText())

            case '保存波形':
                imagefile = QFileDialog().getSaveFileName(self,'保存图片','','PNG (*png)')
                if imagefile[0]:
                    self.ChartView.grab().toImage().save(imagefile[0])
            case '保存滤波后波形':
                imagefile = QFileDialog().getSaveFileName(self,'保存图片','','PNG (*png)')
                if imagefile[0]:
                    self.ChartView_2.grab().toImage().save(imagefile[0])               
            case '滤波':
                ppg_data = []
                sample_rate = 100
                self.textEdit_2.clear()
                self.x2=0.0
                self.series2.clear()

                for line in self.textEdit.toPlainText().splitlines():
                    ppg_data.append(int(line))
                #基线漂移处理
                b, a = signal.butter(8, 0.02, 'lowpass')   #基线漂移去除， 配置滤波器 8 表示滤波器的阶数 Wn为2*临界频率 / fs
                ppg_outline_data = signal.filtfilt(b, a, ppg_data)  #data为要过滤的信号

                ppg_norm_data = ppg_data - ppg_outline_data #新信号=原信号-基线
                #带通滤波
                
                b, a = signal.butter(int(self.comboBox_6.currentText()), [(2*self.doubleSpinBox_2.value())/sample_rate,(2*self.doubleSpinBox.value())/sample_rate], 'bandpass')   #最大只能设置为4阶，scipy函数限制
                ppg_filt_data = signal.filtfilt(b, a, ppg_norm_data)#为要过滤的信号
                for point in ppg_filt_data:
                    self.series2.append(self.x2,point)
                    self.x2+=1
                wd, m = hp.process(hp.scale_data(ppg_filt_data[0:2500]), sample_rate)
                hp.plotter(wd, m)
                for key, value in m.items():
                    # print(f'{key:8}====>{value:5f}')
                    self.textEdit_2.insertPlainText(f'{key:8}====>{value:5f}'+'\n')
                self.textEdit_2.moveCursor(QTextCursor.MoveOperation.EndOfLine)

                if 'RR_list' in wd.keys():
                    # print(wd['RR_list'])
                    rr=(wd['RR_list'])
                    np.savetxt("rr.txt",rr ,fmt='%s')
                
                    time_domain_features = get_time_domain_features(rr)
                    # 返回time_domain_features是一个字典，包含如下键-值：
                    # mean_nni     RR间期平均值
                    # sdnn         RR间期标准差
                    # sdsd         相邻RR之间差异的标准差
                    # rmssd        相邻RR间期的差方和的均值的平方根，反映高频(快速或副交感神经)对hrV的影响
                    # median_nni   RR间隔差的中位数的绝对值
                    # nni_50       连续RR间期间隔差大于50ms的数量
                    # pnni_50      用nni_50 / RR间期数量
                    # nni_20       连续RR间期间隔差大于20ms的数量
                    # pnni_20      用nni_20 / RR间期数量
                    # range_nni    RR间期最大值和最小值的差异
                    # cvcd         连续差异的变化系数 = rmssd / mean_nni
                    # cvnni        变异系数 = sdnn / mean_nni
                    # mean_hr      平均心率
                    # max_hr       最大心率
                    # min_hr       最小心率
                    # std_hr       心率标准差
                    frequency_domain_features = get_frequency_domain_features(rr)
                    # 返回字典，包含如下键值：
                    # total_power   总功率密度谱
                    # vlf           极低频时（0.003-0.04hz）HRV的方差，反映心脏产生的内在节律，受交感神经活动调节
                    # lf            低频时（0.04-0.15hz）HRV的方差，反映交感神经和副交感神经活动
                    # hf            高频时（0.15-40hz）HRV的方差，反映了由副交感神经(迷走神经)活动引起的一拍一拍变异性的快速变化。
                    # lf_hf_ratio   等于 lf / hf
                    # lfnu          归一化低频功率
                    # hfnu          归一化高频功率
                    poincare_plot_features = get_poincare_plot_features(rr)
                    #返回如下键值：
                    # Sd1      庞加莱图在垂直于等式的线的直线上投影的标准差
                    # Sd2      庞加莱投影的标准差
                    # ratio_sd2_sd1        sd2 / sd1


                    # print (time_domain_features )
                    # #输出时域参数
                    # print (frequency_domain_features )
                    # #输出频域参数
                    # print(poincare_plot_features)
                    # #输出非线性参数

                    with open('hrv1.csv', 'a', newline='') as csvfile:                     
                        writer = csv.DictWriter(csvfile, fieldnames=(list(time_domain_features)+list(frequency_domain_features)+list(poincare_plot_features)))
                        writer.writeheader()
                        writer.writerow({**time_domain_features,**frequency_domain_features,**poincare_plot_features})
                    with open('hrv2.csv', 'w', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile,fieldnames=list(m))
                        writer.writeheader()
                        writer.writerow({**m})
    def checkBox_slot(self):
        if self.checkBox.isChecked():
            self.pushButton_3.setChecked(True)
            self.timer.start(int(self.lineEdit.text()))
        else:      
            self.pushButton_3.setChecked(False)


    def timer_slot(self):
        self.pushButton_3.setChecked(False)
        self.timer.stop()
        self.checkBox.setChecked(False)

    def pushButton_8_slot(self):
        deg=[]
        for line in self.textEdit.toPlainText().splitlines():
            deg.append(float(line))
        self.series.clear()
        self.x = 0.0
        self.textEdit.clear()
        percentile = np.percentile(deg, (25, 50, 75), interpolation='midpoint')
        Q1 = percentile[0]#上四分位数
        Q3 = percentile[2]#下四分位数
        IQR = Q3 - Q1#四分位距
        ulim = Q3 + 1.5*IQR#上限 非异常范围内的最大值
        llim = Q1 - 1.5*IQR#下限 非异常范围内的最小值
        for i in range(len(deg)):
            if(llim<deg[i] and deg[i]<ulim):
                self.series.append(self.x, deg[i])
                self.x +=1
                self.textEdit.insertPlainText(str(int(deg[i]))+'\n')
        self.textEdit.moveCursor(QTextCursor.MoveOperation.End)

        
       
    def pushButton_9_slot(self):
        data2=pd.read_csv('hrv2.csv', sep=',')##要进行预测的数据
        data2=data2.drop(['sdsd','pnn50','hr_mad','sd1','sd2','s','breathingrate'],axis=1) 
        rf_reg = joblib.load('RandomForestRegressor1.pkl')#载入模型

        match np.round(rf_reg.predict(data2)[0]):
            case 1:
                self.label_9.setText('疲劳等级：清醒')
            case 2:
                self.label_9.setText('疲劳等级：轻度疲劳')
            case 3:
                self.label_9.setText('疲劳等级：重度疲劳')
