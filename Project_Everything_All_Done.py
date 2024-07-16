# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 15:09:23 2023
Finished on Tue Jun 27 21:46:30 2023

@author: kimhw
@team name: WooHoHo
"""

import sys  # default setting for pyqt
from PyQt5 import QtWidgets, uic   # default setting for pyqt
import numpy as np
import matplotlib.pyplot as plt # imported for graph
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas # imported for graph
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar # imported for graph
import pyvisa
import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()   
        uic.loadUi('UI of everything (0624).ui', self) #파일 오픈
        
        # AFG 2021
        self.AFG = None # same role as rm in the past experiments
        self.refreshButton_AFG.clicked.connect(self.connection_refresh_AFG)
        self.selectButton_AFG.clicked.connect(self.select_AFG) 
        
        self.radioButton_on.clicked.connect(self.on_Clicked) #on
        self.radioButton_off.clicked.connect(self.off_Clicked) #off
        self.selectButton_WF.clicked.connect(self.select_WF) # waveform select
        self.setButton_ampl.clicked.connect(self.select_ampl) # Amppl set
        self.setButton_freq.clicked.connect(self.select_freq) # freq set
        self.setButton_phase.clicked.connect(self.select_phase) # Phase set
        self.setButton_offset.clicked.connect(self.select_offset) # Offset set
        
        self.toolButton_1.clicked.connect(self.plot_reset)
        self.toolButton_2.clicked.connect(self.xy_set)
        self.toolButton_3.clicked.connect(self.yt_set)
        self.toolButton_4.clicked.connect(self.language_Kor)
        self.toolButton_5.clicked.connect(self.language_Eng)
        
        
        # OSCILLOSCOPE 
        self.OS = None
        self.refreshButton_OS.clicked.connect(self.connection_refresh_OS)
        self.selectButton_OS.clicked.connect(self.select_OS)

        self.runstop_count = 0 # to turn the states using one button
        self.pushButton_run.clicked.connect(self.runstop)
        self.toolButton_autoset.clicked.connect(self.autoset)
        self.measureButton_voltage.clicked.connect(self.measure_Vpp)
        
        self.ch1_count = 0 # to turn the states using on button
        self.ch2_count = 0
        self.pushButton_m1.clicked.connect(self.ch1_on)
        self.pushButton_m2.clicked.connect(self.ch2_on)  
        
        # Just test code for checking the dial button
        # self.label = QLabel(self)
        # self.label.setGeometry(150,150,100,30)
        # self.dial_multi.valueChanged.connect(self.dial_multi_value_changed)
        
        self.pushButton_xy.clicked.connect(self.xy_plot)
        self.pushButton_yt.clicked.connect(self.yt_plot)
                
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self) # useful tool for inspecting data
        self.graph.addWidget(self.canvas) # GUI에 띄움
        self.graph.addWidget(self.toolbar)
        self.ax = self.fig.add_subplot() 
         # default: (111) == 1행 1열의 첫번째에 subplot, subplot은 그래프를 한 도화지에 여러개 그리기 위함
        self.ax.set_facecolor('white')
        self.ax.set_title("Oscilloscope Waveform")
        
        self.closeButton.clicked.connect(self.close)
    
    
    # AFG 2021 functions    
    def connection_refresh_AFG(self):
        self.rm = pyvisa.ResourceManager()
        self.comboBox_AFG.clear() # combobox 초기화
        self.comboBox_AFG.addItems(self.rm.list_resources()) # 연결된 list_resources를 combobox에 추가
    
    def select_AFG(self):
        self.AFG = self.rm.open_resource(self.comboBox_AFG.currentText()) # 원하는 resource list를 select
    
    
    def select_WF(self): #waveorm select
        print("clicked!!")
        wave = self.comboBox_WF.currentText() # there are many waveforms in the comboBox_WF
        self.set_waveform(wave)
        
    def set_waveform(self, wave):
        wave_dict={'SIN':'SIN','SQUARE':'SQU','PULSE':'PULS','RAMP':'RAMP',
                  'GAUSIAN':'GAUS','LORENTZ':'LOR','HAVERSINE':'HAV','DC':'DC'}
        self.AFG.write('SOURce1:FUNCtion:SHAPe {}'.format(wave_dict[wave])) 
        self.output_on()
        
        
    def select_ampl(self): #Ampl
        print("clicked!!")
        number = self.lineEdit_ampl.text()     
        try:
           ampl_v = float(number)
           if abs(ampl_v) > 10:
               print("Input Numbers less than 10 in Absolute Value")
           else:
               self.AFG.write('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude {}VPP'.format(ampl_v))
        except ValueError:
            print("Input number")
        
        
    def select_freq(self): #Freq
        print("clicked!!")
        hz = self.lineEdit_freq.text()
        self.set_freq(hz)
        
    def set_freq(self, hz):
        self.AFG.write('SOURce1:FREQuency:FIXed {}kHz'.format(hz))
        self.output_on()
    
        
    def select_phase(self): #Phase
        print("clicked!!")
        degree = self.lineEdit_phase.text()
        self.set_phase(degree)
    
    def set_phase(self, degree):
        self.AFG.write('SOURce1:PHAse:ADJust {}DEG'.format(degree))
        self.output_on()
    
    
    def select_offset(self): #Offset 설정하는 코드로
        print("clicked!!")
        number=self.lineEdit_offset.text()
        self.set_offset(number) 
    
    def set_offset(self, volt):
        self.AFG.write('SOURce1:VOLTage:LEVel:IMMediate:OFFSet {}V'.format(volt))
        self.output_on()
    
   
    def on_Clicked(self):
        print("clicked!!")
        self.output_on()
    
    def off_Clicked(self):
        print("clicked!!")
        self.output_off()
    
        
    def output_on(self):
        self.AFG.write('OUTPUT1:STATE ON')
    
    def output_off(self):
        self.AFG.write('OUTPUT1:STATE OFF')


    # OSCILLOSCOPE functions
    def connection_refresh_OS(self):
        self.rm_2 = pyvisa.ResourceManager()
        self.comboBox_OS.clear()
        self.comboBox_OS.addItems(self.rm_2.list_resources())
    
    def select_OS(self):
        self.OS = self.rm_2.open_resource(self.comboBox_OS.currentText())         
    
    
    def runstop(self): # On / Off  전환 
        self.runstop_count += 1 # 첫 번째 누름은 무조건 Stop
        
        if self.runstop_count % 2 == 1: 
            command = 'ACQ:STATE STOP'
        else:
            command = 'ACQ:STATE RUN'
            
        self.OS.write(command)
    
        
    def autoset(self): 
        self.OS.write("AUTOS EXEC")
    
    
    def measure_Vpp(self):
        self.OS.write(":CH1:CURRENTPRObe 1") # 배율이 10배로 잡혀 있으면 Vpp도 10배로 잡히는 문제 해결
        self.OS.write(":CH2:CURRENTPRObe 1")
        
        # CH 1
        self.OS.write("MEASU:IMM:SOU CH1") # Source Channel == CH 1
        self.OS.write("MEASU:IMM:TYPE PK2PK")
        
        # 측정된 Vpp 값을 받아오는 부분
        self.Vpp_1 = float(self.OS.query("MEASU:IMM:VAL?"))
        self.Vpp_1 = round(self.Vpp_1, 5) # 반올림
        
        # CH 2
        self.OS.write("MEASU:IMM:SOU CH2")
        self.OS.write("MEASU:IMM:TYPE PK2PK")

        self.Vpp_2 = float(self.OS.query("MEASU:IMM:VAL?"))
        self.Vpp_2 = round(self.Vpp_2, 5)

        # QLineEdit에 결과 값 출력
        if self.Vpp_1 != 9.9e+37: # 9.9e+37: Channel Off 시 생기는 default value
            if self.Vpp_2 != 9.9e+37:
                self.lineEdit_Vmeasure.setText('Ch1: {} Ch2: {}'.format(str(self.Vpp_1),str(self.Vpp_2))) # Both On
            else: 
                self.lineEdit_Vmeasure.setText('Ch1: {}'.format(str(self.Vpp_1))) # CH1 On
        else: 
            if self.Vpp_2 != 9.9e+37:
                self.lineEdit_Vmeasure.setText('Ch2: {}'.format(str(self.Vpp_2))) # CH2 On
            else:
                self.lineEdit_Vmeasure.setText('Channel Off') # Both Off
    

    def ch1_on(self):
        self.ch1_count += 1 # 첫 번째 누름은 무조건 On
    
        if self.ch1_count % 2 == 1: 
            command = ":SELECT:CH1 ON"
        else:
            command = ":SELECT:CH1 OFF"
        
        self.OS.write(command)
            
    def ch2_on(self):
        self.ch2_count += 1
        
        if self.ch2_count % 2 == 1: 
            command = ":SELECT:CH2 ON"
        else:
            command = ":SELECT:CH2 OFF"
        
        self.OS.write(command)
        
    def plot_reset(self):
        self.ax.clear()
        self.canvas.draw_idle() 
        self.ax.grid()
    
    
    def xy_set(self):
        self.OS.write("DISPLAY:FORMAT XY")
    def yt_set(self):
        self.OS.write("DISPLAY:FORMAT YT")    
        
    def language_Kor(self):
        self.OS.write("LANG KORE")    
    def language_Eng(self):
        self.OS.write("LANG ENGL")
    
        
    def xy_plot(self):
        self.OS.write("DISPLAY:FORMAT XY")

        # 도화지 clear
        self.ax.clear()
        self.canvas.draw_idle() 
         # 화면을 다시 그리는 작업을 다른 작업과 병행하여 응답성 향상
         # 그래픽 업데이트를 지연시켜 마지막 변경사항만을 고려해 그래픽 업데이트 -> 연속적 그래픽 업데이트를 하나로 결합
        self.ax.grid() # 격자
        
        
        # CH1 Value
        self.OS.write(":SELECT:CH1 ON") 
        self.OS.write('DAT:SOU CH1') # data source Ch1 select
        self.OS.write('DAT:ENC CH1 RPB') # CH1 data를 RPB 방식으로 Encoding
        self.waveform_data = self.OS.query_binary_values('CURV?', datatype='B', container=np.array)
         # CURV?: Waveform data to external device in the form of binary numbers
        
        #Horizontal value setting
        self.ymult = float(self.OS.write("WFMPRE:YMULT?"))  # (vertical) scale factor
        self.yzero = float(self.OS.write("WFMPRE:YZEro?")) # units
        self.yoff = float(self.OS.write("WFMPRE:YOFF?")) # (vertical) position
        
        self.value_horizontal = ((((self.waveform_data - self.yoff) * self.ymult) + self.yzero - 1740) / 725) 
        
        
        # CH2 Value
        self.OS.write(":SELECT:CH2 ON")
        self.OS.write('DAT:SOU CH2')
        self.OS.write('DAT:ENC CH2 RPB')
        self.waveform_data_2 = self.OS.query_binary_values('CURV?', datatype='B', container=np.array)
       
        #verticla vlaue setting
        self.ymult_2 = float(self.OS.write("WFMPRE:YMULT?"))  
        self.yzero_2 = float(self.OS.write("WFMPRE:YZEro?"))
        self.yoff_2 = float(self.OS.write("WFMPRE:YOFF?"))   
        
        self.value_vertical = ((((self.waveform_data_2 - self.yoff_2) * self.ymult_2) + self.yzero_2 - 1740) / 725)
         # Reference from mannual p.240, value_in_YUNits = ((curve_in_dl - YOFF_in_dl) * YMUlt) + YZERO_in_YUNits
         # 1740 은 offset을 0으로 맞추기 위해.
         # offset을 맞춰도 실제값과 큰 차이를 내서 비율 맞춰 725로 나눔
        
        # Plotting
        self.ax.scatter(self.value_horizontal, self.value_vertical, color='r', label='I LOVE PROFESSOR & JOGYO') # Easter egg
        
        lim = np.max([-np.min(self.value_horizontal), np.max(self.value_horizontal)])
        self.ax.set_xlim(-lim - 0.5, lim + 0.5)
        lim = np.max([-np.min(self.value_vertical), np.max(self.value_vertical)])
        self.ax.set_ylim(-lim - 0.5, lim + 0.5)
        self.ax.set_xlabel('Ch1-Value (V)')
        self.ax.set_ylabel('Ch2-Value (V)')
        self.ax.set_title('Oscilloscope Waveform')
        self.ax.grid(True)
        self.ax.legend() # 범례
        self.canvas.draw()
        
    def yt_plot(self):
        self.OS.write("DISPLAY:FORMAT YT")

        # plot setting
        self.ax.clear()
        self.canvas.draw_idle()
        self.ax.grid()
        self.OS.write('AUTOS EXEC') # to adjust time_per_divistion 
        time.sleep(3) # to avoid TIMEOUT ERROR during autosetting
        
        if int(self.OS.query(":SELECT:CH1?")) == 1: # when Channel is State On
            
            self.OS.write('DAT:SOU CH1')
            self.OS.write('DAT:ENC RPB')    

            self.waveform_data = self.OS.query_binary_values('CURV?', datatype='B', container=np.array)

            # 수평축 설정
            self.time_per_division = float(self.OS.query(':HOR:SCA?')) 
             # self.time_per_division == 2.5e-05
             # 1 division == 1 grid on the oscilloscope display 
            self.time_units = self.OS.query('WFMP:XUN?').strip() # s
            self.time_scale = self.time_per_division * len(self.waveform_data) 
             # time scale == 0.125
            self.times = np.linspace(0, self.time_scale, len(self.waveform_data))
             # 0부터 time scale(0.125s)까지 waveform_data의 길이 만큼 분할하는 배열 생성.
        
            #수직축 설정
            self.ymult = float(self.OS.write("WFMPRE:YMULT?"))  
            self.yzero = float(self.OS.write("WFMPRE:YZEro?"))
            self.yoff = float(self.OS.write("WFMPRE:YOFF?"))
            
            self.value = ((((self.waveform_data - self.yoff) * self.ymult) + self.yzero - 1740) / 725) 

            # plotting            
            self.ax.scatter(self.times, self.value, color = 'y', label = 'CHannel 1')
            
            lim = np.max([-np.min(self.value), np.max(self.value)])
            self.ax.set_ylim(-lim - 0.5, lim - 0.5)
            self.ax.set_xlabel('Time ({})'.format(self.time_units))
      
        if int(self.OS.query(":SELECT:CH2?")) == 1:
                
            # Ch2 Value
            self.OS.write('DAT:SOU CH2')
            self.OS.write('DAT:ENC CH2 RPB')    
            self.waveform_data_2 = self.OS.query_binary_values('CURV?', datatype='B', container=np.array)
            
            # 수평축 설정
            self.time_per_division_2 = float(self.OS.query(':HOR:SCA?'))
            self.time_units_2 = self.OS.query('WFMP:XUN?').strip()
            self.time_scale_2 = self.time_per_division_2 * len(self.waveform_data_2)
            self.times_2 = np.linspace(0, self.time_scale_2, len(self.waveform_data_2))
                
            #수직축 설정
            self.ymult_2 = float(self.OS.write("WFMPRE:YMULT?"))  
            self.yzero_2 = float(self.OS.write("WFMPRE:YZEro?"))
            self.yoff_2 = float(self.OS.write("WFMPRE:YOFF?"))
            # self.xincr_2 = float(self.OS.write("WFMPRE:XINCR?"))   
                
            self.value_2 = ((((self.waveform_data_2 - self.yoff_2) * self.ymult_2) + self.yzero_2 - 1740) / 725)
            self.ax.scatter(self.times_2, self.value_2, color = 'b', label = 'CHannel 2')
            
            lim = np.max([-np.min(self.value_2), np.max(self.value_2)])
            self.ax.set_ylim(-lim - 0.5, lim - 0.5)
            self.ax.set_xlabel('Time ({})'.format(self.time_units_2))
            
            
        self.ax.grid(True)
        self.ax.set_title('Oscilloscope Waveform')            
        self.ax.set_ylabel("Amplitude (V)")
        self.ax.legend() 
         # canvas 하단 straigh line = outlier
         # can demonstrate by drawing plot no scatter       
        self.canvas.draw()
                
        
    def close(self):
        print("clicked!!")
        if self.AFG is not None:
            self.AFG.close()
        if self.OS is not None:
            self.OS.close()
        
        
 #### common setting for pyqt##########
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())