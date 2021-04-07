from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

import numpy as np
import time

import dut_spi
import controls

gpio_dir_2_3_ip = ol.ip_dict['gpio_dir_2_gpio_dir_3']
gpio_dir_4_5_ip = ol.ip_dict['gpio_dir_4_gpio_dir_5']

gpio_dir_2 = AxiGPIO(gpio_dir_2_3_ip).channel1
gpio_dir_3 = AxiGPIO(gpio_dir_2_3_ip).channel2
gpio_dir_4 = AxiGPIO(gpio_dir_4_5_ip).channel1
gpio_dir_5 = AxiGPIO(gpio_dir_4_5_ip).channel2


def rd_status():
    dir2 = gpio_dir_2.read()
    dir3 = gpio_dir_3.read()
    dir4 = gpio_dir_4.read()
    dir5 = gpio_dir_5.read()
    print('Current GPIO status (if val == 0 input(PYNQ)')
    print('GPIO 0: 0')
    print('GPIO 1: 0')
    print('GPIO 2: %i' %(dir2))
    print('GPIO 3: %i' %(dir3))
    print('GPIO 4: %i' %(dir4))
    print('GPIO 5: %i' %(dir5))


def rst():
    gpio_dir_2.write(0,0xf)
    gpio_dir_3.write(0,0xf)
    gpio_dir_4.write(0,0xf)
    gpio_dir_5.write(0,0xf)
    
    dut_spi.write_single(60,1,0,0,0,1,1,1,0)#GPIO1: addr60, driv. strength = 1 , ck_ctat(ck_fic in CLAIRE when chopping disabled), out dir
    dut_spi.write_single(59,1,0,0,0,1,1,1,0)#GPIO2: addr59, driv. strength = 1 , ck_fic_n(ck_ctat_n in CLAIRE when chopping disabled), out dir
    dut_spi.write_single(58,1,0,0,0,0,1,1,0)#GPIO3: addr58, driv. strength = 1 , fout_n, out dir
    dut_spi.write_single(57,1,0,0,0,1,1,1,0)#GPIO4: addr57, driv. strength = 1 , ck_ref_p, out dir
    dut_spi.write_single(56,1,0,0,0,0,0,1,0)#GPIO5: addr56, driv. strength = 1 , ck_swc_n, out dir
    print('All GPIO direction changed to input(PYNQ) & output(DUT) ')
    print('')    
    rd_status()

def set_out_claire01():
    #(IMPORTANT) Change gpio direction of dut first
    print("change gpio direction: PYNQ ==> DUT")
    gpio_num = int(input("Input the gpio number to control (""3"", ""4"", ""5""): "))
    if(gpio_num == 3):
        ##clk_stup
        print("supply CK_STUP_SWC to DUT GPIO3")
        dut_spi.write_single(58,0,0,0,0,0,0,0,0)#GPIO3: addr58, in dir
        gpio_dir_3.write(1,0xf)
        controls.clk_stup()
    elif(gpio_num == 4):
        print("supply PD_OFFSET_GAIN_B_DSM to DUT GPIO4")
        dut_spi.write_single(57,0,0,0,0,0,0,0,0)#GPIO4: addr57, in dir
        gpio_dir_4.write(1,0xf)
    elif(gpio_num == 5):
        print("supply CSW_DSM_CTL to DUT GPIO5")
        dut_spi.write_single(56,0,0,0,0,0,0,0,0)#GPIO5: addr56, in dir
        gpio_dir_5.write(1,0xf)
    else:
        print("invalid input!")
        return -1 
    rd_status()
    
def set_in_claire01():
    print("Change gpio direction: DUT ==> PYNQ")
    #(IMPORTANT: change gpio direction of pynq first)
    gpio_num = int(input("Input the gpio number to control (""1"", ""2"", ""3"", ""4"", ""5""): "))
    
    if(gpio_num == 1):
        #pynq direction fixed to input
        print("Choose the signal to be output")
        print(" ""0"": dsm_out_gpio")
        print(" ""1"": dsm_out_gpio")
        print(" ""2"": vss")
        print(" ""3"": ck_ctat (ck_fic when chopping disabled")
        sig_sel = int(input("Your Choice: "))
        
        if(sig_sel == 0):
            dut_spi.write_single(60,1,0,0,0,0,0,1,0)
        elif(sig_sel == 1):
            dut_spi.write_single(60,1,0,0,0,0,1,1,0)
        elif(sig_sel == 2):
            dut_spi.write_single(60,1,0,0,0,1,0,1,0)
        elif(sig_sel == 3):
            dut_spi.write_single(60,1,0,0,0,1,1,1,0)
        else: 
            print("Invalid Input!")
            return -1 
    
    elif(gpio_num == 2): 
        gpio_dir_2.write(0,0xf)
        
        print("Choose the signal to be output")
        print(" ""0"": ck_ref_tdc_n")
        print(" ""1"": ck_ref_tdc_p")
        print(" ""2"": vss")
        print(" ""3"": ck_fic_n (ck_ctat_n when chopping disabled) ")
        sig_sel = int(input("Your Choice: "))
        
        if(sig_sel == 0):
            dut_spi.write_single(59,1,0,0,0,0,0,1,0)
        elif(sig_sel == 1):
            dut_spi.write_single(59,1,0,0,0,0,1,1,0)
        elif(sig_sel == 2):
            dut_spi.write_single(59,1,0,0,0,1,0,1,0)
        elif(sig_sel == 3):
            dut_spi.write_single(59,1,0,0,0,1,1,1,0)
        else: 
            print("Invalid Input!")
            return -1 
    
    elif(gpio_num == 3): 
        gpio_dir_3.write(0,0xf)
        
        print("Choose the signal to be output")
        print(" ""0"": ck_chop_p")
        print(" ""1"": fout_n")
        print(" ""2"": ck_inj_p")
        print(" ""3"": ck_ref_n")
        sig_sel = int(input("Your Choice: "))
        
        if(sig_sel == 0):
            dut_spi.write_single(58,1,0,0,0,0,0,1,0)
        elif(sig_sel == 1):
            dut_spi.write_single(58,1,0,0,0,0,1,1,0)
        elif(sig_sel == 2):
            dut_spi.write_single(58,1,0,0,0,1,0,1,0)
        elif(sig_sel == 3):
            dut_spi.write_single(58,1,0,0,0,1,1,1,0)
        else: 
            print("Invalid Input!")
            return -1 
    
    elif(gpio_num == 4): 
        gpio_dir_4.write(0,0xf)
        
        print("Choose the signal to be output")
        print(" ""0"": vss")
        print(" ""1"": ck_swc_p")
        print(" ""2"": ck_injb_p")
        print(" ""3"": ck_ref_p")
        sig_sel = int(input("Your Choice: "))
        
        if(sig_sel == 0):
            dut_spi.write_single(57,1,0,0,0,0,0,1,0)
        elif(sig_sel == 1):
            dut_spi.write_single(57,1,0,0,0,0,1,1,0)
        elif(sig_sel == 2):
            dut_spi.write_single(57,1,0,0,0,1,0,1,0)
        elif(sig_sel == 3):
            dut_spi.write_single(57,1,0,0,0,1,1,1,0)
        else: 
            print("Invalid Input!")
            return -1 
        
    elif(gpio_num == 5):
        gpio_dir_5.write(0,0xf)
        
        print("Choose the signal to be output")
        print(" ""0"": ck_swc_n")
        print(" ""1"": ck_injb_n")
        print(" ""2"": ck_inj_n")
        print(" ""3"": ck_chop_n")
        sig_sel = int(input("Your Choice: "))
        
        if(sig_sel == 0):
            dut_spi.write_single(56,1,0,0,0,0,0,1,0)
        elif(sig_sel == 1):
            dut_spi.write_single(56,1,0,0,0,0,1,1,0)
        elif(sig_sel == 2):
            dut_spi.write_single(56,1,0,0,0,1,0,1,0)
        elif(sig_sel == 3):
            dut_spi.write_single(56,1,0,0,0,1,1,1,0)
        else: 
            print("Invalid Input!")
            return -1 
        
    else:
        print("invalid input!")
        return -1 
    rd_status()
    










