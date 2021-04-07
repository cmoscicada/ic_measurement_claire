from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

import numpy as np
import time


dsm_bit_dsm_clk_ip = ol.ip_dict['gpio_dsm_bit_dsm_clk']
dsm_input_trig_ip = ol.ip_dict['gpio_dsm_input_trig']

dsm_bit_sel = AxiGPIO(dsm_bit_dsm_clk_ip).channel1 #2bit, dsm bit selection code
##(if dsm_bit_sel == 3) ==>  12bit DSM engine selected 
##(if dsm_bit_sel == 2) ==>  8bit DSM engine selected 
##(if dsm_bit_sel == 1) ==>  4bit DSM engine selected 
##(if dsm_bit_sel == 0) ==>  DSM engine disabled 

dsm_clk_sel = AxiGPIO(dsm_bit_dsm_clk_ip).channel2 #2bit, dsm clock speed selection code 
##(if dsm_clk_sel == 3) ==>  fastest dsm clock  
##(if dsm_clk_sel == 2) ==>  
##(if dsm_clk_sel == 1) ==>  
##(if dsm_clk_sel == 0) ==>  slowest dsm clock  

dsm_input = AxiGPIO(dsm_input_trig_ip).channel1 #12bit, dsm input code
##dsm_input[11:0] ==> full code
##dsm_input[11:0] ==> 12bit input for 12bit DSM engine
##dsm_input[7:0] ==> 8bit input for 8bit DSM engine
##dsm_input[3:0] ==> 4bit input for 4bit DSM engine

dsm_trig = AxiGPIO(dsm_input_trig_ip).channel2 #1bit, dsm trig bit 


def start(): #set all DSM control codes and start to output 1b DSM signal
    bit_ctl()
    clk_ctl()
    enter_input()
    send_trig()
    

def clk_ctl():
    clk_ctl_val = int(input("Enter clock speed (3~0, 3 ==> fastest): "))
    
    if( 0 <= clk_ctl_val <= 3):
        dsm_clk_sel.write(clk_ctl_val,0xf)  
        current_clk_val = dsm_clk_sel.read()
        if(current_clk_val == 0):
            print("DSM clk frequency: 4.9kHz")
        elif(current_clk_val == 1):
            print("DSM clk frequency: 19.5kHz")
        elif(current_clk_val == 2):
            print("DSM clk frequency: 78.2kHz")
        elif(current_clk_val == 3):
            print("DSM clk frequency: 312.9kHz")
    else:
        print("Invalid value!")
        return -1 

def bit_ctl():
    bit_ctl_val = int(input("Enter DSM engine bit (4, 8, 12): "))
    
    if(bit_ctl_val == 4):
        dsm_bit_sel.write(1,0xf)
    elif(bit_ctl_val == 8):
        dsm_bit_sel.write(2,0xf)
    elif(bit_ctl_val == 12):
        dsm_bit_sel.write(3,0xf)
    else:
        print("DSM engine disabled !")
        dsm_bit_sel.write(0,0xf)
    
    print('DSM bit selection code val: %i' %(dsm_bit_sel.read()))
    

def send_trig():
    trig_val = dsm_trig.read()
    #print('prev trig val: %i' %(trig_val))
    dsm_trig.write(trig_val^1,0xf)
    trig_val = dsm_trig.read()
    #print('current trig val: %i' %(trig_val))
    
def enter_input():
    dsm_bit_val = dsm_bit_sel.read()
    
    if(dsm_bit_val == 0):
        print("DSM engine disabled!")
    
    elif(dsm_bit_val == 1):
        print("Current DSM bit: 4")      
        dsm_input_4b = int(input("Enter 4b DSM input code (0~15): "))
        
        if(0<=dsm_input_4b<=15):
            dsm_input.write(dsm_input_4b,0xf)
            print("4b DSM input code in decimal: %i" %(dsm_input.read()))
        else:
            print("Invalid input!")
            return -1 
    elif(dsm_bit_val == 2):
        print("Current DSM bit: 8")      
        dsm_input_8b = int(input("Enter 8b DSM input code (0~255): "))
        if(0<=dsm_input_8b<=255):         
            dsm_input.write(dsm_input_8b,0xff)
            print("8b DSM input code in decimal: %i" %(dsm_input.read()))
        else:
            print("Invalid input!")
            return -1
    elif(dsm_bit_val == 3):
        print("Current DSM bit: 12")      
        dsm_input_12b = int(input("Enter 12b DSM input code (0~4095): "))
        if(0<=dsm_input_12b<=4095):         
            dsm_input.write(dsm_input_12b,0xfff)
            print("12b DSM input code in decimal: %i" %(dsm_input.read()))
        else:
            print("Invalid input!")
            return -1    
    else:
        print("Error: Strange DSM Bit register value")
        return -1 
        
        
       
    
    
    
    
    
    
    
    
