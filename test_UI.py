import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt,pyqtSignal,QObject,pyqtSlot
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QApplication,QMessageBox,QDesktopWidget,QMainWindow,QAction,qApp,QApplication,QMenu,QTextEdit,QHBoxLayout,QVBoxLayout,QGridLayout,QLabel,QInputDialog,QLineEdit,QFileDialog)
from PyQt5.QtGui import QFont,QIcon    
import time
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np
import matplotlib.ticker as ticker
import math as m
import random

class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        
        self.get_object()
        btn1 = QPushButton("Emergency stop", self)
        btn1.move(150,50)
        btn2 = QPushButton("Start",self)
        btn2.move(30, 50)
        btn3 = QPushButton("Quit",self)
        btn3.move(90,100)
      
        btn1.clicked.connect(self.button1Clicked)
        btn2.clicked.connect(self.button2Clicked)
        btn3.clicked.connect(self.button3Clicked)   
        
        self.statusBar()
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('VdP & Hall measurements')
        self.show()
        
    def get_object(self):
        
        self.q_object=question()

    def button1Clicked(self,objet):
        
        # try:
            time.sleep(1)
            self.q_object.meas_object.emergency_stop()
            self.q_object.graph_object.close()
            self.close()
            print("\nProgram shut down. Please restart for further measurements.")
            time.sleep(0.1)
            os._exit(0)
        # except:
            # print('\nThe measurement has not started yet or is unable to stop for the moment.')

    def button2Clicked(self):
        
        # q=question()
        self.q_object.ask_questions(1,2,3,4,5)
        
    def button3Clicked(self):
        
        try:
            self.q_object.graph_object.close()
        except AttributeError:
            pass
        self.close()

    # def closeEvent(self, event):
    #         """Generate 'question' dialog on clicking 'X' button in title bar.
    # 
    #         Reimplement the closeEvent() event handler to include a 'Question'
    #         dialog with options on how to proceed - Save, Close, Cancel buttons
    #         """
    #         reply = QMessageBox.question(
    #             self, "Message",
    #             "Are you sure you want to quit? Any unsaved work will be lost.",
    #             QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
    #             QMessageBox.Save)
    # 
    #         if reply == QMessageBox.Close:
    #             event.accept()
    #         else:
    #             event.ignore()
###

class question:

    def __init__(self):
        
        self.data=[]
        self.can_pass=True
        
    def ask_questions(self,Lakeshore,current,voltmeter,scanner,caylar):
        
        # try:
            # self.data.append(input("Enter the name of the sample: "))
            # self.data.append(input("\nEnter the thickness of the sample(mm): "))
            # self.data.append(input("\nEnter the Starting Temperature,the Number of Steps, the value of a Step and the Number of Measurements for each temperature\nFormat Sarting T(K),Nb Steps,Step(K),Nb Measurements: ").split(','))
            # self.data.append(input("\nEnter the value of I for VdP measurements, the value of I for Hall measurements\nFormat I_VdP(mA),I_Hall(mA): ").split(','))
            # self.data.append(input("\nEnter the Minimum value of the Magnetic field, the Maximum value of the Magnetic field, the value of a Step\nFormat Min(G), Max(G), Step(G): ").split(','))
            # self.data.append(input("\nEnter the Heater resistance(Ohm)\n(Default value is 25 Ohm. Press Enter if you want to set the default value): "))
            # self.data.append(input("\nDo you want to perform only the resistivity measurement ?\nFormat (1 = Yes / 0 = No): "))
            # self.configure_data()
            self.data=['test',1,[300,2,30,1],[10,10],[-6000,6000,3000],'',0]
            self.is_ok(Lakeshore,current,voltmeter,scanner,caylar)
        # except:
        #     print('\nError in the values entered. Please check the format')
        #     self.can_pass=False    
    
    def configure_data(self):
        
        while float(self.data[2][0]) > 830:
            self.data[2][0]=input('\nValue entered for Starting Temperature too high.\nPlease enter a value below 830 K: ')
        if self.data[5] is '':
            self.data[5]=25
        
        if self.data[6] == '1' or self.data[6] == 'Yes':
            self.data[6]=True
        else:
            self.data[6]=False
            
    def is_ok(self,Lakeshore,current,voltmeter,scanner,caylar):
        
        self.retry=input("\nDo you want to start the experiment with these values?\nFormat (1 = Yes / 0 = No): ")
        if self.retry == '1' or self.retry == 'Yes':
            print('\nStarting the measurements')
            self.start_exp(Lakeshore,current,voltmeter,scanner,caylar)
        else:
            self.retry=input("\nDo you want to enter the parameters again?\nFormat (1= Yes / 0 = No): ")
            if self.retry == '1' or self.retry == 'Yes':
                self.data=[]
                self.ask_question(Lakeshore,current,voltmeter,scanner,caylar)
            else:
                print("\nExperiment stopped.")
    
    def start_exp(self,Lakeshore,current,voltmeter,scanner,caylar):

            self.meas_object=measure()
            self.meas_object.parameters(self.data[0], float(self.data[1]), float(self.data[2][0]),int(self.data[2][1]),float(self.data[2][2]),int(self.data[2][3]),float(self.data[3][0]),float(self.data[3][1]),float(self.data[4][0]),float(self.data[4][1]),float(self.data[4][2]),self.data[5],self.data[6])
            self.graph_object=Graph(self.meas_object.name)
            self.graph_object.set_lim(float(self.data[2][0]),float(self.data[2][0])+float(self.data[2][1])*float(self.data[2][2]),float(self.data[4][0]),float(self.data[4][1]))
            self.meas_object.execute_measures(self.graph_object,Lakeshore,current,voltmeter,scanner,caylar)

class list_data:
    
    def __init__(self,list_prop=None,list_T=None,prop_T=None):
        """concerning the properties (hence prop)"""
        if list_prop is None:
            list_prop = [0,0,0,0]
        self.prop=list_prop
        self.rho=[list_prop[0]]
        self.rh=list_prop[1]
        self.mu=list_prop[2]
        self.n=list_prop[3]
        
        """concerning the temperatures (hence T)"""
        self.lT=[] # will be used at the end to plot the data
        self.HIGH_T=300 #to set a default value
        self.T=list_T
        self.prop_T=prop_T
        if list_T is None:
            self.T=[]
        if prop_T is None:
            self.prop_T=[]
        
        #self.parameters()
    
    def parameters(self,name='',Sample_thick=1,Starting_temp=300,Nb_Temperature_Steps=1,Step_size=1,Nb_Measurements=3, Intensity_Rho=10, Intensity_Hall=20, Min_magnetic_field = -6000, Max_magnetic_field=6000, Step_size_B=3000, Heater_resistance=25, resistivity_alone=False,dTemp=0.3,dTime=30): #data taken from the panel
        
        self.name=name
        self.dTemp=dTemp
        self.dTime=dTime
        self.condi_T=[Starting_temp,Nb_Temperature_Steps,Step_size,Nb_Measurements]
        self.condi_I=[Intensity_Rho,Intensity_Hall]
        self.thick=Sample_thick
        self.heater_resistance=Heater_resistance
        self.resistivity_alone=resistivity_alone
        
        self.condi_B=[Min_magnetic_field,Max_magnetic_field,Step_size_B]
        self.B=[0,0]
        
        """voltage"""
        self.data_tensionrho=[] #reset
        self.tensionrho_avg=[]
        
        self.rangeV=''
        self.rangeV_pass= False
        self.rangeV_num=1
        self.V='' #check the format of the reading from the voltmeter
        
        
        self.tensionHall=[] #check the format of the reading from the voltmeter
        self.tensionHall_ch3_4=[]
        self.tensionHall_list=[[]]
        
        self.data_caylar=[]
        self.val_caylar='' #reset
        self.command_caylar=''
        
class command_instru:
    
    def __init__(self):
        pass
        
    def tensionHall_function(self,current,voltmeter,scanner,caylar,k):
        
        self.tensionHall=[]
        if k ==3:
            self.tensionHall_ch3_4.append((10**-4)*(self.B[1])+0.1*((10**-4)*(self.B[1]))**2+0.05) #10^-4 * x + 0.1 * (10^-4*x)^2
        else:
            self.tensionHall_ch3_4.append(-((10**-4)*(self.B[1])+0.1*((10**-4)*(self.B[1]))**2+0.05))
        
    def residual_scan(self,current,voltmeter,scanner):
        """self.data_residual is as follows : [average residual voltage measurement for channel n,standard deviation of the measurements of channel n] for the 6 of them]"""
        self.data_residual=[np.round(np.random.rand(1,2),5).tolist()[0] for j in range(6)]
        
    def read_magnetic_field(self,caylar):
        """data_caylar is as follows: [[data read from caylar, sign of the magnetic field, value of the magnetic field, sign+value /1000] repeated for each value of B]"""
        self.data_caylar.append([0,0,0,self.B[1]])
        
class Graph:
    
    def __init__(self,name):
        
        self.fig = plt.figure(figsize=(9,9))
        self.fig = plt.gcf()
        self.fig.canvas.set_window_title('%s'%(name,))
        self.set_position(800,60)
        self.init_subplot(80)
    
    def init_subplot(self,offset):
        #first subplot
        self.host1 = host_subplot(211, axes_class=AA.Axes)
        self.adjust(right=0.75)
        self.par11 = self.host1.twinx()
        self.par12 = self.host1.twinx()
        self.new_fixed_axis = self.par12.get_grid_helper().new_fixed_axis
        self.par12.axis["right"] = self.new_fixed_axis(loc="right",axes=self.par12,offset=(offset, 0)) #check
        #to display the axis
        self.par11.axis["right"].toggle(all=True)
        self.par12.axis["right"].toggle(all=True)
        #gives the names. First display that updates for each measurements done at a set temperature
        self.host1.set_title("Physical properties variations with temperature")
        self.host1.set_xlabel("Temperature [K]")
        self.host1.set_ylabel("Resistivity [Ohm.m]")
        self.par11.set_ylabel("Carrier concentration [cm-3]")
        self.par12.set_ylabel("Mobility [cm2.V-1.s-1]")
        #second subplot
        self.host2 = host_subplot(212, axes_class=AA.Axes)
        self.adjust(right=0.75)
        self.par21 = self.host2.twinx()
        self.par22 = self.host2.twinx()
        self.new_fixed_axis = self.par22.get_grid_helper().new_fixed_axis
        self.par22.axis["right"] = self.new_fixed_axis(loc="right",axes=self.par22,offset=(offset, 0))
        self.par21.axis["right"].toggle(all=True)
        self.par22.axis["right"].toggle(all=True)
        #Second display that updates for each measurements of properties
        self.host2.set_title("Hall tension dependency on the magnetic field")
        self.host2.set_xlabel("Magnetic field value [G]")
        self.host2.set_ylabel("Hall tension corrected [V]")
        self.par21.set_ylabel("Hall tension without MR [V]")
        self.par22.set_ylabel("MR contribution to Hall tension [V]")
        self.set_format_yaxis()
        self.fig.tight_layout()
        
    def adjust(self,top=None,bottom=None,left=None,right=None):
        
        plt.subplots_adjust(top,bottom,left,right)
        
    def set_position(self,x,y):
        #for TkAgg backend
        # plt.get_current_fig_manager().window.wm_geometry('+%s+%s' %(x,y)) #to reposition the window
        self.fig.canvas.manager.window.wm_geometry('+%s+%s' %(x,y))

    def set_lim(self,x1_left=None,x1_right=None,x2_left=None,x2_right=None):
    
        self.host1.set_xlim(x1_left,x1_right)
        self.host2.set_xlim(x2_left,x2_right)
        #self.host1.set_ylim(0, 10)
    
    def set_format_yaxis(self):
        
        self.host1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%5.2e'))
        self.par11.yaxis.set_major_formatter(ticker.FormatStrFormatter('%5.2e'))
        self.par12.yaxis.set_major_formatter(ticker.FormatStrFormatter('%5.2e'))
        self.host2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%5.2e'))
        self.par21.yaxis.set_major_formatter(ticker.FormatStrFormatter('%5.2e'))
        self.par22.yaxis.set_major_formatter(ticker.FormatStrFormatter('%5.2e'))
    
    def clear_data(self,splt_num):
        
        lhost=[self.host1,self.host2]
        lpar=[[self.par11,self.par12],[self.par21,self.par22]]
        del lhost[splt_num-1].lines[:] #to erase the data plotted within a subplot
        del lpar[splt_num-1][0].lines[:]
        del lpar[splt_num-1][1].lines[:]
    
    def plot(self,splt_num,x,y1,y2,y3):
        
        lhost=[self.host1,self.host2]
        lpar=[[self.par11,self.par12],[self.par21,self.par22]]
        self.p1,=lhost[splt_num-1].plot(x,y1,'C0')
        self.p2,=lpar[splt_num-1][0].plot(x,y2,'C1')
        self.p3,=lpar[splt_num-1][1].plot(x,y3,'C2')
        lhost[splt_num-1].axis["left"].label.set_color(self.p1.get_color())
        lpar[splt_num-1][0].axis["right"].label.set_color(self.p2.get_color())
        lpar[splt_num-1][1].axis["right"].label.set_color(self.p3.get_color())
        plt.pause(0.000001)
        
    def plot_simple(self,x,y):
        
        self.p1,=self.host2.plot(x,y,'C0')
        self.host2.axis["left"].label.set_color(self.p1.get_color())
        plt.pause(0.000001)
        
    def show(self):
        
        plt.show(block=True)
        
    def close(self):
        
        plt.close()

class measure(list_data,command_instru):

    def __init__(self):
        list_data.__init__(self)
        command_instru.__init__(self)
        
    def emergency_stop(self):
        
        print('Emergency stop asked, saving and shutting down the program')
        self.status_avg=False
        self.save_data()
        # self.save_data()
        # self.regulation_stand_by(caylar)
        # time.sleep(5)
        # self.Power_Off(caylar)
        # scanner.write('A4X')
        # scanner.write('RX')
        # current.write('F0X')
        # current.write('I+0.000E+0V+3.000E+0X')
        # nanovoltmeter.clear()
        # Lakeshore.write('SETP1,300')
        
    def reset_for_measures(self):
        
        self.result_tab=[]
        self.result_tab_avg=[]
        self.HIGH_T=self.condi_T[0]
        self.rho_list=[]
        self.n_list=[]
        self.mu_list=[]
        self.lTf=[]
        self.status_avg=True
        
    def reset_for_T(self):
        
        self.Vh_Table=[]
        
    def set_if_rho_alone(self):
        
        self.data_reg=[[0,0],0]
        self.Vh_Table=[[0]*6]
       
    def get_rho(self,current,voltmeter,scanner):
        
        """data_tensionrho will have the following format: [[1 V measured, 2nd V measured, 3rd V measure, 4th V measured, std, avg] for channel 1,2 & 5,6]
           data_tensionrho_avg will have the following format: [absolute values of tensionrho measured (4),sum of values of mean tensionrho, ration between V (= ration between R)]
           channel 1 & 2 are for U on BD and 5 & 6 are for U on CD"""
        self.data_tensionrho=[] #reset the file
        self.data_tensionrho_avg=[]
        self.data_tensionrho=[np.round(np.random.rand(1,6),5).tolist()[0] for j in range(4)]
        self.data_tensionrho_avg=[round(random.random(),5) for j in range(6)]
        self.rho=m.log(self.HIGH_T)*1e-4
        
    def get_B_data(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        """tensionHall_list contains the voltage without the influence of I and the magnetoresistance (MR)
           self.B is as follow [IncrementMax, value to set for the mag field]
           tensionHall_list is as follows: [[tensions without the influence of I for each value of B],[tensions minus the value obtained for B=0 (idealy 0)],[odd B dependency of tensions],[even B dependency of tensions]]
           data_caylar is as follows: [[data read from caylar, sign of the magnetic field, value of the magnetic field, sign+value /1000] repeated for each value of B]
           Vh_Table is as follows: [[value of B,value of tension without influence of I,temperature measured,tension minus tension measured for B=0 (idealy 0), odd B dependency of the tension, even B dependency of the tension] repeated of each value of B]"""
        self.tensionHall_list=[[]] 
        self.data_caylar=[]
        self.B[1]=self.condi_B[0]# gives the minimum of the set magnetic field
        graph.clear_data(2)
        for j in range(0,self.B[0]): #IncrementMax is given by self.B[0] and j needs to start at 1

            time.sleep(1) #wait 45 seconds
            self.tensionHall_ch3_4=[]
            for i in range(3,5):

                self.tensionHall_function(current,voltmeter,scanner,caylar,i)
            self.tensionHall_list[0].append((self.tensionHall_ch3_4[0]-self.tensionHall_ch3_4[1])/2)
            self.read_magnetic_field(caylar)

            graph.plot_simple([float(row[3]) for row in self.data_caylar],self.tensionHall_list[0])
            self.Vh_Table.append([self.data_caylar[j][3]]) #set the value of the sign + Mfield
            self.Vh_Table[j].append(self.tensionHall_list[0][j])
            self.Vh_Table[j].append(self.HIGH_T)
            self.B[1]+=self.condi_B[2] #corresponds to the increment of the magnetic field by the step of MField * Incremenent index
        #print(self.tensionHall_list)
        self.tensionHall_list.append(np.array(self.tensionHall_list[0])-self.tensionHall_list[0][int((len(self.tensionHall_list[0])+1)/2)-1]) #nulls out the midlle value corresponding to B=0 (supposely near to 0). Watch out. This only works if the ramp of B is made from one value to its opposite (i.e. from -B to B) with a constant step, divisor of B (needs to have B=0)
        self.tensionHall_list.append(((self.tensionHall_list[1]-np.flip(self.tensionHall_list[1],0))/2)) #gives the odd B dependency of the tension. Watch out. This only works if the ramp of B is made from one value to its opposite one (i.e. from -B to B) with a constant step and with the value at B=0
        self.tensionHall_list.append(((np.array(self.tensionHall_list[1])+np.flip(self.tensionHall_list[1],0))/2)) #gives the even dependency
        for j in range(0,self.B[0]):
            #print(self.Vh_Table,self.tensionHall_list)
            self.Vh_Table[j].append(self.tensionHall_list[1][j])
            self.Vh_Table[j].append(self.tensionHall_list[2][j])
            self.Vh_Table[j].append(self.tensionHall_list[3][j])
        graph.clear_data(2)
        self.B_list=[float(row[3]) for row in self.data_caylar]
        graph.plot(2,self.B_list,self.tensionHall_list[1],self.tensionHall_list[2],self.tensionHall_list[3])
        self.data_reg=np.polyfit(self.B_list,self.tensionHall_list[2],1,full=True)[:2]
        self.data_reg=[self.data_reg[0],self.data_reg[1][0]]
        self.rh=self.data_reg[0][0] #gives the coefficient a in the linear regression ax+b
        self.rh= self.rh*self.thick*10**10/self.condi_I[1] #10**10 to have the right unit
        self.mu=self.rh*0.01/self.rho #mu in cm2.V-1.s-1
        self.n=abs(1.6*10**19/self.rh) #n in cm-3

        
    def get_prop_data(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        self.lT.append(self.HIGH_T) #gives T_start
        print('\nResidual voltage measurement.')
        self.residual_scan(current,voltmeter,scanner)
        print('\nResistivity measurements.')
        self.get_rho(current,voltmeter,scanner)

        if self.resistivity_alone:
            self.set_if_rho_alone()
        else:
            print('\nCarrier concentration and mobility measurements.')
            self.B[0]=int(((self.condi_B[1]-self.condi_B[0])/self.condi_B[2])+1) #corresponds IncrementMax
            self.get_B_data(graph,Lakeshore,current,voltmeter,scanner,caylar)
        #if not self.rh, self.n and self.mu are left at the default value of 0

        time.sleep(0.3)

        self.lT.append(self.HIGH_T+1e-3*self.HIGH_T) #gives T_end
    
    def get_prop(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        print('\nTemperature stability reached')
        self.lT=[]
        self.T=[]
        self.get_prop_data(graph,Lakeshore,current,voltmeter,scanner,caylar) #gives rho,rh,mu,n
        self.T.append([0,0,0,0,self.HIGH_T,self.HIGH_T]) #Tb

    def add_results(self,position_T):
        
        #self.index=self.condi_T[3]*(position_T-1)+(nb_repetition-1)

        temp=[position_T,self.T[6],'{:04.3e}'.format(self.rho),'{:04.3e}'.format(self.rh),'{:04.3e}'.format(self.n),'{:04.3e}'.format(self.mu)]
        temp.extend(['{:04.3e}'.format(elem[5]) for elem in self.data_tensionrho])
        temp.extend(['{:04.3e}'.format(elem[4]) for elem in self.data_tensionrho])
        temp.extend(['{:04.3e}'.format(elem) for elem in self.data_reg[0]])
        temp.append(['{:04.3e}'.format(self.data_reg[1])])
        temp.extend(['{:04.3e}'.format(elem[0]) for elem in self.data_residual])
        temp.append(self.lT[0]) #corresponds to T_start
        temp.append(self.lT[1]) #corresponds to T_end
        self.result_tab.append(temp)
        
    def charge_PID(self):
        
        self.data_PID=[]
        link_PID_data="C://Users//Florian//Documents//Cours//Mines//Stage//Programmes//PID_H.txt"
        with open(link_PID_data,'r') as PID_read:
            val,val_add,transit=PID_read.readlines(),[],''
            for l in val[1:]:
                val_add.append([elem for elem in l if elem != '\t'][:-1])
            for row in val_add:
                tf=[]
                for el in row:
                    if el !='_':
                        transit+=el
                    else:
                        tf.append(float(transit))
                        transit=''
                self.data_PID.append(tf)
                
    def add_results_avg(self):
        
        if self.status_avg:
            for temperatureindex in range(self.condi_T[1]+1): #corresponds to Nb_Temperature_Steps
                temp=[]
                for j in range(1,6):
                    temp2=[]
                    for i in range(self.condi_T[3]): #corresponds to the number of measurements
                        temp2.append(float(self.result_tab[i+temperatureindex*self.condi_T[3]][j]))
    
                    temp.append('{:04.3e}'.format(np.average(temp2)))
                self.result_tab_avg.append(temp)
        
    def write_results(self,file):
        
        for row in self.result_tab:
            temp='\n'
            for elem in row[:5]:
                temp+=(str(elem)+'\t\t\t')
            for elem in row[5:]:
                temp+=(str(elem)+'\t\t\t\t')
            file.write(temp)
            
    def write_results_avg(self,file):
        
        for row in self.result_tab_avg:
            temp='\n'
            temp+=(str(row[0])+'\t\t')
            for elem in row[1:]:
                temp+=(str(elem)+'\t\t\t')
            file.write(temp)
                
    def reset_file(self,link):
        
        open(link, 'w').close()
        
    def save_exp_from_Vh(self,file):
            
        for line in self.Vh_Table:
            file.write('\n%s\t\t\t%s\t\t\t\t%s\t\t\t\t\t%s\t\t\t\t\t%s\t\t\t\t\t%s' % ('{:04.3e}'.format(line[0]),'{:04.3e}'.format(line[1]),str(line[2]),'{:04.3e}'.format(line[3]),'{:04.3e}'.format(line[4]),'{:04.3e}'.format(line[5])))
        
    def save_exp(self):
        
         link_HIGH_save_exp="C://Users//Florian//Documents//Cours//Mines//Stage//Programmes//test.txt"  #link needs to be changed once operating on a different computer   
         with open(link_HIGH_save_exp, 'a') as HallVoltage_Appliedfield:
            HallVoltage_Appliedfield.write('Measurement done at %s K' %(self.T[6])) #save average Ta,Tb temperature
            HallVoltage_Appliedfield.write('\nMagField(G)\t\t\tReadHallVoltage(V)\t\t\tTemperature(K)\t\t\t\tCorrectedVoltage(V)\t\t\t\tHVoltageWithoutMR(V)\t\t\t\tMRContribution(V)') #\n to embed a new line
            self.save_exp_from_Vh(HallVoltage_Appliedfield)
            HallVoltage_Appliedfield.write('\n ')
        
    def save_data(self):
        
        link_HIGH_save_data="C://Users//Florian//Documents//Cours//Mines//Stage//Programmes//test2.txt"  #link needs to be changed once operating on a different computer 
        with open(link_HIGH_save_data, 'w') as Results_data_file:
            Results_data_file=open(link_HIGH_save_data, 'w')
            Results_data_file.write('Sample name: %s' % (str(self.name)))
            Results_data_file.write('\nSample thickness [mm]: %s' %(str(self.thick)))
            Results_data_file.write('\nMeasurements between: %s K and %s K with %s steps of %s K' %(str(self.condi_T[0]),str(self.HIGH_T),str(self.condi_T[1]),str(self.condi_T[2])))
            Results_data_file.write('\nCurrent intensiy for resistivity [mA]: %s' %(str(self.condi_I[0])))
            Results_data_file.write('\nCurrent intensiy for Hall [mA]: %s' %(str(self.condi_I[1])))
            Results_data_file.write('\nMagnetic field applied between: %s (G) and %s (G), with a step of %s (G)' %(str(self.condi_B[0]),str(self.condi_B[1]),str(self.condi_B[2])))
            Results_data_file.write('\nn°\t\t\tT[K]\t\t\tRes[Ohm.m]\t\t\tRh[cm3.C-1]\t\t\tn [cm-3]\t\t\tMobility [cm2.V-1.s-1]\t\t\t<U resistivity Ch1 [V]>\t\t\t<U resistivity Ch2 [V]>\t\t\t<U resistivity Ch5 [V]>\t\t\t<U resistivity Ch6 [V]>\t\t\tU Standard dev Ch1 [V]\t\t\tU Standard dev Ch2 [V]\t\t\tU Standard dev Ch5 [V]\t\t\tU Standard dev Ch6 [V]\t\t\tSlope RegLin [V/mG]\t\t\tCoeff Affine RegLin [V]\t\t\tStrdDevRegLin [V/mG]\t\t\tResidual Ch1 [V]\t\t\tResidual Ch2 [V]\t\t\tResidual Ch3 [V]\t\t\tResidual Ch4 [V]\t\t\tResidual Ch5 [V]\t\t\tResidual Ch6 [V]\t\t\tT start [K]\t\t\tT end [K]')
            self.write_results(Results_data_file)
            Results_data_file.write('\nAveraged Results:')
            Results_data_file.write('\nT[K]\t\t\tRes[Ohm.m]\t\t\tRh[cm3.C-1]\t\t\tn [cm-3]\t\t\tMobility[cm2.V-1.s-1]')
            self.add_results_avg()
            self.write_results_avg(Results_data_file)
        
    def execute_measures(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        self.charge_PID()
        self.reset_for_measures()
        self.reset_file("C://Users//Florian//Documents//Cours//Mines//Stage//Programmes//test.txt")
        print('\n----------------------------------------------------')
        for HIGH_NbTemperature in range(self.condi_T[1]+1): # corresponds to Nb_Temperature_Steps
            
            for NbMeasure_rep in range(self.condi_T[3]): #corresponds to Nb_Measurements
                self.reset_for_T()
                self.get_prop(graph,Lakeshore,current,voltmeter,scanner,caylar)
                self.T=self.T[0]
                self.T.append((self.T[4]+self.T[5])/2)
                print('\nTemperature = %s K' %(self.T[6]))
                self.lTf.append(self.T[6])
                self.save_exp()
                self.rho_list.append(self.rho)
                self.n_list.append(self.n)
                self.mu_list.append(self.mu)
                graph.plot(1,self.lTf,self.rho_list,self.n_list,self.mu_list) 
                self.add_results(HIGH_NbTemperature)
                print('----------------------------------------------------')
            self.HIGH_T+=self.condi_T[2] #corresponds to Step size[K]
            print('----------------------------------------------------')
        self.HIGH_T-=self.condi_T[2]
        self.save_data()
        self.HIGH_T=300
        print('\nPlease wait...')


        time.sleep(1)
        print('\nMeasurements done.')
        graph.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    # else:
    #     print('QApplication instance already exists: %s' % str(app))

    aw = Window()
    app.exec_()