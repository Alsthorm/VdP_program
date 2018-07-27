###imports

import visa
import sys
#from PyQt5.QtWidgets import QApplication, QWidget
import time
import matplotlib as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np

#Fonction mesures hautes temperatures

### To initialise
class question:

    def __init__(self):
        
        self.data=[]
        self.can_pass=True
        
    def ask_question(self,Lakeshore,current,voltmeter,scanner,caylar):
        
        try:
            self.data.append(input("Enter the name of the sample: "))
            self.data.append(input("\nEnter the thickness of the sample(mm): "))
            self.data.append(input("\nEnter the Starting Temperature,the Number of Steps, the value of a Step and the Number of Measurements for each temperature\nFormat Sarting T(K),Nb Steps,Step(K),Nb Measurements: ").split(','))
            self.data.append(input("\nEnter the value of I for VdP measurements, the value of I for Hall measurements\nFormat I_VdP(mA),I_Hall(mA): ").split(','))
            self.data.append(input("\nEnter the Minimum value of the Magnetic field, the Maximum value of the Magnetic field, the value of a Step\nFormat Min(G), Max(G), Step(G): ").split(','))
            self.data.append(input("\nEnter the Heater resistance(Ohm)\n(Default value is 25 Ohm. Press Enter if you want to set the default value): "))
            self.data.append(input("\nDo you want to perform only the resistivity measurement ?\nFormat (1 = Yes / 0 = No): "))
            self.configure_data()
            self.is_ok(Lakeshore,current,voltmeter,scanner,caylar)
        except:
            print('\nError in the values entered. Please check the format')
            self.can_pass=False    
    
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
            self.can_pass=True
            self.start_exp(Lakeshore,current,voltmeter,scanner,caylar)
        else:
            self.retry=input("\nDo you want to enter the parameters again?\nFormat (1= Yes / 0 = No): ")
            if self.retry == '1' or self.retry == 'Yes':
                self.data=[]
                self.ask_question(Lakeshore,current,voltmeter,scanner,caylar)
            else:
                self.can_pass=False
                print("\nExperiment stopped.")
    
    def start_exp(self,Lakeshore,current,voltmeter,scanner,caylar):
        
        if self.can_pass:
            meas=measure()
            meas.parameters(self.data[0], float(self.data[1]), float(self.data[2][0]),int(self.data[2][1]),float(self.data[2][2]),int(self.data[2][3]),float(self.data[3][0]),float(self.data[3][1]),float(self.data[4][0]),float(self.data[4][1]),float(self.data[4][2]),self.data[5],self.data[6])
            graph_data=Graph(meas.name)
            graph_data.set_lim(float(self.data[2][0]),float(self.data[2][0])+float(self.data[2][1])*float(self.data[2][2]),float(self.data[4][0]),float(self.data[4][1]))
            meas.execute_measures(graph_data,Lakeshore,current,voltmeter,scanner,caylar)
        else:
            print('\nExperiment cancelled.')


####Measure variables (objects)
"""convention -> the properties are given in the following order: [rho,rh,mu,n]. Convention -> the temperature data are given in the following order: [HIGH_T,Other temperatures]."""
"""The purpose of this class is to create lists containing the properties and the data concerning the temperature"""
""" For the moment, self.T=[HIGH_T,[T1,T2,T3,T4,Tb,Ta,Tmoyen]]"""

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
        
        ## Reset whithin the program
        # self.pass_test_Ta_Tb=False
        # self.pass_stability= False
        # self.data_PID=[]
        # self.J=0
        # self.Tmin=300
        # self.Tamx=300
        # self.condi_Ls=[]
        # self.residual_val_stock=[]
        # self.data_residual=[]
        # self.range_pass=False
        # self.I_caylar
        # self.lTf=[]

###Class graph used to display the results
            
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
        self.host2.set_ylabel("Hall tension [V]")
        self.par21.set_ylabel("Hall tension without MR [V]")
        self.par22.set_ylabel("MR contribution to Hall tension [V]")
        self.set_format_yaxis()
        self.fig.tight_layout()
        
    def adjust(self,top=None,bottom=None,left=None,right=None):
        
        plt.subplots_adjust(top,bottom,left,right)
        
    def set_position(self,x,y):
        #for TkAgg backend
        plt.get_current_fig_manager().window.wm_geometry('+%s+%s' %(x,y)) #to reposition the window
        
    def set_lim(self,x1_left=None,x1_right=None,x2_left=None,x2_right=None):
    
        self.host1.set_xlim(x1_left,x1_right)
        self.host2.set_xlim(x2_left,x2_right)

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
        
        plt.show()
        
    def close(self):
        
        plt.close()
        
### class comand_instru used to give instructions to the devices
    
class command_instru:
    
    def __init__(self):
        pass
    
    def initialisation_measures(self,Lakeshore,current,scanner=0):
        
        current.write('F0X') #output off
        current.write('I+0.000E+0V+3.000E+0X')
        Lakeshore.write('display1,50')
        Lakeshore.write('dispfld1,A,1')
        Lakeshore.write('cset1,a,1,1,1')
        Lakeshore.write('range1')
        Lakeshore.write('cmode1,1')
        Lakeshore.write('intypeA,4,2,2,10,9')
        Lakeshore.write('ramp1,0,0')
        
    def init_display(Lakeshore):
        
        Lakeshore.write('CDISP 1, 1, %s, 2, 0' %(str(self.heater_resistance))) #corresponds to the heater resistance [Ohm]. Default value is 25.
        
    def command_Ls_measT(self,Lakeshore):
        
        Lakeshore.write("krdg?a")
        HIGH_Ls_val=Lakeshore.read()
        time.sleep(1) #delay 1 second
        return HIGH_Ls_val
        
    def control_T(self,Lakeshore,current,voltmeter,scanner,caylar):
        
        if self.HIGH_T > 830:
            self.save_data()
            self.regulation_standby_caylar(caylar)
            time.sleep(5)
            self.Power_Off_Caylar(caylar)
            scanner.write('A4X')
            scanner.write('RX')
            current.write('F0X')
            current.write('I+0.000E+0V+3.000E+0X')
            voltmeter.clear()
            Lakeshore.write('setp1,300')
            time.sleep(2)
            sys.exit("Temperature asked too high. Saving and turning off the program.")
        
    def Power_On_Caylar(self,caylar):
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        caylar.write('SET_POWER_ON')
        self.val_caylar=caylar.read() #should be a string
        print('\nStatus obtained for caylar: %s' %(str(self.val_caylar)))
        if self.val_caylar[0:12] == 'POWER_IS_ON': #we need to retrieve the string from the 1  digit to the 12th
            print('\nCaylar is ON')
        caylar.close()
        
        
    def canal_function(self,scanner,k):
        
        time.sleep(1)
        scanner.write('A4X') #configures in 4-pole mode
        scanner.write('RX') #Opens all channels and displays the first one
        scanner.write('B%sC%sX' %(k,k)) #displays the channel k and then closes it
        time.sleep(2)
        
    def VoltageReading(self,current,voltmeter,mode):

        while not self.range_pass:
            voltmeter.write('T0X') #updates continually
            voltmeter.write(self.rangeV)
            time.sleep(2)
            voltmeter.write('Z1X') #to null out stray voltages picked on connections
            time.sleep(1)
            current.write('I%sV+2.500E+1X' % (str(format(0.001*self.condi_I[mode])))) #set right format for the current intesity (=condi_I[mode]). mode=0 corresponds to VdP and 1 to Hall. 0.001 to convert mA to A.
            current.write('F1X')
            time.sleep(1)
            self.V=self.format_to_comp(self.V)
            current.write('F0X')
            current.write('I+0.000E+0V+3.000E+0X')
            voltmeter.write('Z0X')
            #self.control_V could be set in this method 
            if self.is_V_not_ok():
                self.rangeV_num+=1
                self.rangeV='R%sX' %(str(self.rangeV_num))
            else:
                self.range_pass=True
            time.sleep(0.5)
            
    def tensionHall_function(self,current,voltmeter,scanner,caylar,k):
        
        self.tensionHall=[]
        self.canal_function(scanner,k)
        for l in range(6):
            self.range_pass=False
            self.rangeV_num=1
            self.VoltageReading(current,voltmeter,1)
            self.tensionHall.append(self.V)
        self.tensionHall_ch3_4.append(np.average(self.tensionHall))
        
    def command_caylar_value(self):
        
        #filled with '0' until 9 digits are obtained. Value given in G and converted in mG (*1000)
        self.command_caylar='SG%s%s' %('{:+f}'.format(self.B[1])[0],str(abs(self.B[1]*1000)).zfill(9)) #returns 'SG+ val of magfield' or 'SG- val of magfield' depending on the sign of self.B[1] and the value written with 9 digits
        
    def set_field_value(self,caylar):
        """need to be checked"""
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        self.command_caylar_value()
        caylar.write(self.command_caylar)
        print('\nThe MagField is at : %s (mG) ' % (str(caylar.read()))) #"""check what is obtained in that case"""
        time.sleep(1) #to let the time to display
        caylar.close()
        
    def set_field_regulation(self,caylar):
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        caylar.write('SETREGUL_FLD')
        print('\nRegulation of the magnetic field : %s ' % (str(caylar.read()))) #"""check what is obtained in that case"""
        caylar.close()
        
    def regulation_standby_caylar(self,caylar):
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        caylar.write('SET_STAND_BY')
        print('\nField standby : %s ' % (str(caylar.read()))) #check what is obtained in that case
        caylar.close()
    
    def read_magnetic_field(self,caylar):
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        """self.data_caylar will have the following format: [[data read from caylar, sign of the magnetic field, value of the magnetic field, sign+value /1000] repeated for each value of B]"""
        caylar.open()
        temp_caylar=[]
        caylar.write('READMAGFIELD')
        caylar.read() #check because the EOI is said to be "." 
        temp_caylar.append(str(caylar.read()))
        caylar.close()
        temp_caylar.append(temp_caylar[0][2:][0]) ##takes the digit starting from the 3rd to the end (the length is that of caylar.read()) and gives the sign
        temp_caylar.append(temp_caylar[0][2:][1:]) #gives the value of the magnetic field
        
        if temp_caylar[1] == '+':
            temp_caylar.append(float(temp_caylar[0][2:])/1000)
        print('\nValue of the magnetic field is +%s' % (temp_caylar[2]/1000))
            self.data_caylar.append(temp_caylar)
            time.sleep(2)
        else:
            temp_caylar.append(-float(temp_caylar[0][2:])/1000)
            print('\nValue of the magnetic field is -%s' % (temp_caylar[2]/1000))
            self.data_caylar.append(temp_caylar)
            time.sleep(2)
        
        #/!\#    
    def command_caylar_value_I(self):
        
        self.command_caylar='SA%s%s' %('{:+f}'.format(self.I_caylar)[0],str(abs(self.I_caylar*1000)).zfill(9)) #returns 'SA+ val of magfield' or 'SA- val of magfield' with self.I_caylar the sign and the val written with 9 digits
        
    def set_current_value(self,caylar):
        """need to be checked"""
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        self.command_caylar_value_I()
        caylar.write(self.command_caylar_I)
        print('\nThe caylar current is at : %s (mA) ' % (str(caylar.read()))) #"""check what is obtained in that case"""
        time.sleep(1) #to let the time to display
        caylar.close()
        
    def set_current_regulation(self,caylar):
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        caylar.write('SETREGUL_AMP')
        print('\nRegulation of the current : %s ' % (str(caylar.read()))) #"""check what is obtained in that case"""
        caylar.close()
        
    def Power_Off_Caylar(self,caylar):
        #amm = rm.open_resource('ASRL2::INSTR', baud_rate = 9600, data_bits = 8, read_termination= '\r') """to set the baud rate and the number of bits. Need to be called on opening caylar and stops on CR
        caylar.open()
        caylar.write('SET_POWEROFF') # and not SET_POWER_OFF strangely
        self.val_caylar=caylar.read() #should be a string
        print('\nStatus obtained for caylar: %s' %(str(self.val_caylar)))
        if val_caylar[0:12] == 'POWER_IS_OFF': #we need to retrieve from the 1st to the 12th digit of the string
            print('\nCaylar is OFF')
        caylar.close()
    
    def residual_of_channel(self,current,voltmeter,scanner,n):
        
        """self.data_residual is as follows : [average residual voltage measurement for channel n,standard deviation of the measurements of channel n] for the 6 of them]"""
        self.residual_val_stock=[]
        current.write('F0X')
        current.write('I+0.000E+0V+3.000E+0X')
        scanner.write('A2X')
        scanner.write('RX')
        scanner.write('B%sC%sX' %str(11+n)) #to gives the channel 11,12,13,14,15
        time.sleep(0.1)
        #range voltmeter
        for idx in range(10):
            voltmeter.write('T0X')
            voltmeter.write('B1X')
            voltmeter.write('R1X') #range to set. Default value is R1 <=> 0.002 V
            voltmeter.write('Z0X')
            time.sleep(1)
            self.residual_val_stock.append(self.format_to_comp(voltmeter.read()))
        self.data_residual.append([np.average(self.residual_val_stock)])
        self.data_residual[n].append(np.std(self.residual_val_stock))
        # self.data_residual.extend([[self.average(self.residual_val_stock),self.std(self.residual_val_stock)]])
        time.sleep(0.1)

### Class measure used to give all the operations

class measure(list_data,command_instru):

    def __init__(self):
        list_data.__init__(self)
        command_instru.__init__(self)
        
    def reset_for_measures(self)
        
        self.result_tab=[]
        self.result_tab_avg=[]
        
        self.HIGH_T=self.condi_T[0]
        self.rho_list=[]
        self.n_list=[]
        self.mu_list=[]
        self.lTf=[]
        
    def reset_for_T(self):
        
        self.Vh_Table=[]
        
    def set_if_rho_alone(self):
        
        self.data_reg=[[0,0],0]
        self.Vh_Table=[[0]*6]
        
## Methods to test and use data. Found within operation methods    
    
    def test_Ta_Tb(self):
        self.T.append(sum(self.T[0:4])) # append Ta (=sum) to self.T
        #Tb=self.T[4] #because Tb is appended before Ta, self.T looks like [...Tb,Ta (=sum)]
        self.pass_test_Ta_Tb = abs(self.T[5]-self.T[4]) < 0.5
        
    def test_stability(self):
        self.pass_stability = (abs(self.T[0]-self.T[1]) < self.dTemp) and (abs(self.T[0] - self.T[2]) < self.dTemp) and (abs(self.T[0]-self.T[3]) < self.dTemp) and (abs(self.T[3]-self.HIGH_T) < 1.0)
        
    def get_4_T(self,Lakeshore):
        self.T=[]
        for k in range(4):
            self.T.append(self.command_Ls_measT(Lakeshore))
            time.sleep(self.dTime)
        
    def affiche_Ta_Tb_ok(self):
        
        self.test_Ta_Tb()
        if self.pass_test_Ta_Tb(self):
            print('Condition Ta-Tb < 0.5°C is verified')
        else:
            print('Condition Ta-Tb < 0.5°C is not verified')    
    
    def is_V_not_ok(self):
        
        return abs(self.V) >= (0.0004*10**self.rangeV_num)
            
    def format(self,val_to_format):
        """set the format of value from InstensityHall, need to pay attention to how they are entered"""
        #works for values below 1
        n=len(str(val_to_format))
        nw=int(val_to_format*10**(n-2))
        p=len(str(nw))
        return str(nw)[0]+'.'+str(nw)[1:4]+'0E-'+str(n-2-(p-1)) #[1:4] may need to be changed to [1:3] depending on the accuracy (accurate to 1 mA or to 0.1 mA)
        
    def format_to_comp(self,val):
        
        return float(val[4:16]) #to have a readible value
    
    def is_canal_rho(self,val):
        
        return val < 3 or val > 4
    
    def order_res(self):
        
        """stock r= V_BD/V_CD or V_CD/V_BD in data_tensionrho_avg"""
        if self.data_tensionrho_avg[0] > self.data_tensionrho_avg[2]:
            self.data_tensionrho_avg.append(self.data_tensionrho_avg[0]/self.data_tensionrho_avg[2])
        else:
            self.data_tensionrho_avg.append(self.data_tensionrho_avg[2]/self.data_tensionrho_avg[0])
    
    def get_f(self):
        
        self.rho.append(0.717) #corresponds to the value f(9) near the maximum
        if self.data_tensionrho_avg[5] <= 9:
            for it in range(50):
                self.rho[1]=np.log(2)/np.log(2*np.cosh(np.log(2)*(self.data_tensionrho_avg[5]-1)/(self.rho[1]*(self.data_tensionrho_avg[5]+1))))
        else:
            for it in range(50):
                self.rho[1]=-2*self.data_tensionrho_avg[5]*np.log(2)/((self.data_tensionrho_avg[5]+1)*np.log(1-np.exp(-2*np.log(2)/((self.data_tensionrho_avg[5]+1)*self.rho[1]))))
                
    def find_J_for_T():
        
        self.J=0
        self.Tmin=self.data_PID[self.J][0]
        self.Tmax=self.data_PID[self.J][1]
        
        while not (self.Tmin < self.HIGH_T < self.Tmax):
            self.J+=1
            self.Tmin=self.data_PID[self.J][0]
            self.Tmax=self.data_PID[self.J][1]
            
    def residual_scan(self,current,voltmeter,scanner):
        
        self.data_residual=[]
        for r in range(6):
            self.residual_of_channel(current,voltmeter,scanner,r)
            
            
### Methods operation order
    
    def get_rho(self,current,voltmeter,scanner):
        
        """data_tensionrho will have the following format: [[1 V measured, 2nd V measured, 3rd V measure, 4th V measured, std, avg] for channel 1,2 & 5,6]
           data_tensionrho_avg will have the following format: [absolute values of tensionrho measured (4),sum of values of mean tensionrho, ration between V (= ration between R)]
           channel 1 & 2 are for U on BD and 5 & 6 are for U on CD"""
        self.data_tensionrho=[] #reset the file
        self.data_tensionrho_avg=[]
        for n in range(1,7):
            if self.is_canal_rho(n):
                self.canal_function(scanner,n)
                self.rangeV='R1X'
                temp=[]
                for p in range(4):
                    self.range_pass=False
                    self.rangeV_num=1
                    self.VoltageReading(current,voltmeter,0)
                    temp.append(self.V)
                self.data_tensionrho.append(temp)
                self.data_tensionrho[n].append(np.std(self.data_tensionrho[n]))
                self.data_tensionrho[n].append(np.average(self.data_tensionrho[n][:4]))
                self.data_tensionrho_avg.append(np.average(self.data_tensionrho[n][:4]))
        self.data_tensionrho_avg=np.absolute(self.data_tensionrho_avg)
        self.data_tensionrho_avg.append(sum(self.data_tensionrho_avg))
        self.rho=[(self.data_tension_avg[4]*np.pi*self.thick)/(4*self.condi_I[0]*np.log(2))] #first step to calculate rho without the f factor in the VdP method
        self.order_res()
        self.get_f()
        self.rho=self.rho[0]*self.rho[1]
        current.write('I+0.000E+0V+3.000E+0X')
        current.write('F0X')
        scanner.write('RX')
        
        
    def get_B_data(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        """tensionHall_list contains the voltage without the influence of I and the magnetoresistance (MR)
           self.B is as follow [IncrementMax, value to set for the mag field]
           tensionHall_list is as follows: [[tensions without the influence of I for each value of B],[tensions minus the value obtained for B=0 (idealy 0)],[odd B dependency of tensions],[even B dependency of tensions]]
           data_caylar is as follows: [[data read from caylar, sign of the magnetic field, value of the magnetic field, sign+value /1000] repeated for each value of B]
           Vh_Table is as follows: [[value of B,value of tension without influence of I,temperature measured,tension minus tension measured for B=0 (idealy 0), odd B dependency of the tension, even B dependency of the tension] repeated of each value of B]"""
        self.tensionHall_list=[[]] 
        self.data_caylar=[[]]
        self.B[1]=self.condi_B[0]# gives the minimum of the set magnetic field
        graph.clear_data(2)
        for j in range(0,self.B[0]): #IncrementMax is given by self.B[0] and j needs to start at 1
            self.set_field_value(caylar)
            self.set_field_regulation(caylar)
            time.sleep(45) #wait 45 seconds
            self.tensionHall_ch3_4=[]
            for i in range(3,5):
                self.rangeV='R1X'
                self.tensionHall_function(current,voltmeter,scanner,caylar,i)
            self.tensionHall_list[0].append((self.tensionHall_ch3_4[0]-self.tensionHall_ch3_4[1])/2)
            self.read_magnetic_field(caylar)
            graph.plot_simple([float(row[3]) for row in self.data_caylar],self.tensionHall_list[0])
            self.Vh_Table.append([self.data_caylar[j][3]]) #set the value of the sign + Mfield
            self.Vh_Table[j].append(self.tensionHall_list[0][j])
            self.Vh_Table[j].append(self.command_Ls_measT(Lakeshore))
            self.B[1]+=self.condi_B[2] #corresponds to the increment of the magnetic field by the step of MField * Incremenent index
        self.regulation_standby_caylar(caylar)
        self.tensionHall_list.append(np.array(self.tensionHall_list[0])-self.tensionHall_list[0][int((len(self.tensionHall_list[0])+1)/2)-1]) #nulls out the midlle value corresponding to B=0 (supposely near to 0). Watch out. This only works if the ramp of B is made from one value to its opposite (i.e. from -B to B) with a constant step, divisor of B (needs to have B=0)
        self.tensionHall_list.append(((self.tensionHall_list[1]-np.flip(self.tensionHall_list[1],0))/2)) #gives the odd B dependency of the tension. Watch out. This only works if the ramp of B is made from one value to its opposite one (i.e. from -B to B) with a constant step
        self.tensionHall_list.append(((np.array(self.tensionHall_list[1])+np.flip(self.tensionHall_list[1],0))/2)) #gives the even dependency
        for j in range(0,self.B[0]):
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
        
        self.lT.append(self.command_Ls_measT(Lakeshore)) #gives T_start
        print('\nResidual voltage measurement.')
        self.residual_scan(current,voltmeter,scanner)
        print('\nResistivity measurements.')
        self.get_rho(current,voltmeter,scanner)
        self.Power_On_Caylar(caylar)
        if self.resistivity_alone:
            self.set_if_rho_alone()
        else:
            print('\nCarrier concentration and mobility measurements.')
            self.B[0]=int(((self.condi_B[1]-self.condi_B[0])/self.condi_B[2])+1) #corresponds IncrementMax
            self.get_B_data(graph,Lakeshore,current,voltmeter,scanner,caylar)
        #if not self.rh, self.n and self.mu are left at the default value of 0
        self.I_caylar=0
        self.set_current_value(caylar)
        time.sleep(1)
        self.set_current_regulation(caylar)
        time.sleep(30)
        self.Power_Off_Caylar(caylar)
        scanner.write("A4X")
        scanner.write("RX")
        voltmeter.clear()
        current.write('I+0.000E+0V+3.000E+0X')
        current.write('F0X')
        self.lT.append(self.command_Ls_measT(Lakeshore)) #gives T_end
        
    def get_prop(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        self.pass_test_Ta_Tb = False
        while not self.pass_test_Ta_Tb :
            self.pass_stability = False
            while not self.pass_stability :
                print('\nWaiting for temperature stability')
                self.T=[]
                self.get_4_T(Lakeshore)
                self.test_stability()
            print('\nTemperature stability reached')
            self.lT=[]
            self.get_prop_data(graph,Lakeshore,current,voltmeter,scanner,caylar) #gives rho,rh,mu,n
            self.T.append(self.command_Ls_measT(Lakeshore)) #Tb
            self.affiche_Ta_Tb_ok()
            self.test_Ta_Tb()
            
            
    def consigne(self,Lakeshore,current,voltmeter,scanner,caylar):
        
        """self.condi_Ls will be as the following: [Heater range, Imax, P, I, D]. dTemp, dTime are added separately for more clarity"""
        self.control_T(Lakeshore,current,voltmeter,scanner,caylar)
        Lakeshore.write('setp1'+str(self.HIGH_T)) # gives the temperature to set for the Lakeshore
        print('\nThe value of the temperature asked is %s (K)' %str(self.HIGH_T)) #initial value
        self.find_J_for_T()
        self.condi_Ls=[self.data_PID[self.J][2],self.data_PID[self.J][3],self.data_PID[self.J][4],self.data_PID[self.J][5],self.data_PID[self.J][6]]
        self.dTemp, self.dTime= self.data_PID[self.J][7],self.data_PID[self.J][8]
        Lakeshore.write('pid1,%s,%s,%s' %(str(self.condi_Ls[2]),str(self.condi_Ls[3]),str(self.condi_Ls[4])))
        Lakeshore.write('range%s' %(str(condi_Ls[0])))
        Lakeshore.write('CLIMIT1,%s,%s,%s,%s,%s' %('840','0','0',str(self.condi_Ls[1]),'5')) #used this way to be more easily (possibly) changed 
        
    def charge_PID(self):
        
        self.data_PID=[]
        link_PID_data=""
        with open(link_PID_data,'r') as PID_read:
            transit=''
            for line in PID_read.readlines()[1:]:
                tf=[]
                for elem in line:
                    if elem !='_':
                        if elem != '\t' or elem != '':
                            transit +=elem
                    else:
                        tf.append(float(transit))
                        transit=''
                self.data_PID.append(tf)

    def add_results(self,position_T):
        
        temp=[position_T,self.T[6],'{:04.3e}'.format(self.rho),'{:04.3e}'.format(self.rh),'{:04.3e}'.format(self.n),'{:04.3e}'.format(self.mu)]
        for x in range(4):
            temp.append('{:04.3e}'.format(self.data_tensionrho[x][5]))
        for x in range(4):
            temp.append('{:04.3e}'.format(self.data_tensionrho[x][4]))
        for x in range(2):
            temp.append('{:04.3e}'.format(self.data_reg[0][x]))
        temp.append('{:04.3e}'.format(self.data_reg[1]))
        for x in range(6):
            temp.append('{:04.3e}'.format(self.data_residual[x][0]))
        temp.append(self.lT[0]) #corresponds to T_start
        temp.append(self.lT[1]) #corresponds to T_end
        self.result_tab.append(temp)

    #maximum precision of 10-3. Can be increased.
    def add_results_avg(self):
        
        for temperatureindex in range(self.condi_T[1]+1): #corresponds to Nb_Temperature_Steps
            temp=[]
            for j in range(1,6):
                temp2=[]
                for i in range(self.condi_T[3]): #corresponds to the number of measurements
                    temp2.append(self.result_tab[i+temperatureindex*self.condi_T[3]][j])
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
        
         link_HIGH_save_exp=""  #link needs to be changed once operating on a different computer   
         with open(link_HIGH_save_exp, 'a') as HallVoltage_Appliedfield:
            HallVoltage_Appliedfield.write('Measurement done at %s K' %(self.T[6])) #save average Ta,Tb temperature
            HallVoltage_Appliedfield.write('\nMagField(G)\t\t\tReadHallVoltage(V)\t\t\tTemperature(K)\t\t\t\tCorrectedVoltage(V)\t\t\t\tHVoltageWithoutMR(V)\t\t\t\tMRContribution(V)') #\n to embed a new line
            self.save_exp_from_Vh(HallVoltage_Appliedfield)
            HallVoltage_Appliedfield.write('\n ')

    def save_data(self):
        
        link_HIGH_save_data=""  #link needs to be changed once operating on a different computer 
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
        # link_HIGH_save_PID="C://Users//Florian//Documents//Cours//Mines//Stage//Programmes//PID_H.txt"
        # open(link_HIGH_save_PID, 'w').close() #erase the content
        # HIGH_FileSave_PID=open(link_HIGH_save_PID, 'w')
        # HIGH_FileSave_PID.close()
        
    def execute_measures(self,graph,Lakeshore,current,voltmeter,scanner,caylar):
        
        #self.parameters()
        self.initialisation_measures(Lakeshore,current)
        self.init_display(Lakeshore)
        self.charge_PID()
        self.reset_for_measures()
        self.reset_file("C://Users//Florian//Documents//Cours//Mines//Stage//Programmes//Fichier_secours_données.txt")
        print('\n----------------------------------------------------')
        for HIGH_NbTemperature in range(self.condi_T[1]+1): # corresponds to Nb_Temperature_Steps
            self.consigne(Lakeshore,current,voltmeter,scanner,caylar)
            for NbMeasure_rep in range(self.condi_T[3]): #corresponds to Nb_Measurements
                self.reset_for_T()
                self.get_prop(graph,Lakeshore,current,voltmeter,scanner,caylar)
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
        sel.consigne(Lakeshore,current,voltmeter,scanner,caylar)
        print('\nPlease wait...')
        self.initialisation_measures(Lakeshore,current)
        LakeShore340.write('setp1,300')
        Lakeshore340.write('range 0')
        time.sleep(1)
        print('\nMeasurements done.')
        graph.show()
    
### Main program

"""Implement the commands when we select the high temperature mode, commands are in the panel start"""

####Initialisation mesures
"""Lakeshore340 will be denoted as Ls or Lakeshore in the methods"""
"""The order of instruments given in the different methods is always : Lakeshore, current, voltmeter, scanner, caylar"""

# rm=visa.ResourceManager()
# #print(rm.list_resources()) # usefull to check all the devices detected. Erase # at the beginning of the line to be able to execute it.
# Lakeshore340 = rm.open_resource('GPIB0::15::INSTR')
# K224courant = rm.open_resource('GPIB0::13::INSTR')
# Nanovoltmeter = rm.open_resource('GPIB0::5::INSTR')
# Scanner = rm.open_resource('GPIB0::17::INSTR')
# Caylar = rm.open_resource("COM1", term_chars = "\r", timeout = 5) #check this line if it is working


## Asks for values then starts the measurements
q=question()
q.ask_question(1,2,3,4,5)
#q.ask_question(Lakeshore240,K224current,Nanovoltmeter,Scanner,Caylar)

