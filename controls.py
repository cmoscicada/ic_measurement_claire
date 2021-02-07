from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

import dut_spi
import numpy as np

xo_oe_clk_stup_on_ip = ol.ip_dict['gpio_xo_oe_clk_stup_on']

xo_oe = AxiGPIO(xo_oe_clk_stup_on_ip).channel1
clk_stup_on = AxiGPIO(xo_oe_clk_stup_on_ip).channel2

def tcxo(): # control on-board tcxo 
    bit = xo_oe.read()
    print("current status: %i (""1"": on, ""0"": off)" %(bit))
    bit = int(input("enter new status: "))
    xo_oe.write(bit,0xf)
    bit = xo_oe.read()
    print("current status: %i (""1"": on, ""0"": off)" %(bit))
    
    
def clk_stup(): #main clock startup function
    stup_en = int(input("enter the command 1) enable startup 0) disable startup : "))
    
    if(stup_en == 0):
        print('')
        print("main osc startup function disabled!")
        #change startup settings (addr 55 & up direction)
        dut_spi.write_single(55 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0) 
        print("Startup by switched capacitor disabled!")
        print('')
        print("disconnect clk_stup & GPIO3")
    elif(stup_en == 1):
        print('')
        clk_stup_on.write(stup_en,0xf)
        #change GPIO3 direction (addr 58, (1,1,1,1,1,0,0,0)) 
        dut_spi.write_single(58,1,1,1,1,1,0,0,0)
        print("GPIO3 direction changed to input! connect clk_stup to GPIO3")
        #change startup settings (addr 55 & up direction)
        
        stup_dir = int(input("enter stup direction 1) UP, 0) DN :"))
        if(stup_dir == 1): 
            dut_spi.write_single(55 ,1 ,1 ,0 ,1 ,1 ,0 ,0 ,0)  # (UP == 1 & DN == 0)
            print("Startup by switched capacitor enabled! (UP == 1 & DN == 0)")
        elif(stup_dir == 0 ):
            dut_spi.write_single(55 ,1 ,1 ,1 ,1 ,0 ,0 ,0 ,0)  # (UP == 0 & DN == 1)
            print("Startup by switched capacitor enabled! (UP == 0 & DN == 1)")
        
        print('')
        print("Connect clk_stup to GPIO3")

    else: 
        print("invalid command!")
        return -1 
    
def kvco():
    # kvco control (addr 10)
    # range: 0~8
    
    kvco_bit = [0,0,0,0]
    
    kvco = int(input("enter kvco value (0~8): "))
    if(kvco > 8 or kvco < 0):
        print("ERROR: invalid input!")
        return -1
    else: 
        kvco_bit[0] = kvco%2
        kvco_bit[1] = (kvco>>1)%2
        kvco_bit[2] = (kvco>>2)%2
        kvco_bit[3] = (kvco>>3)%2
        #print("debug", kvco_bit)

    dut_spi.write_single(10,kvco_bit[0],kvco_bit[1],kvco_bit[2],kvco_bit[3],0,0,0,0)
    dut_spi.commit_w_addr0to15()
    
def csw():
    ## csw control
    # range: 0 ~ 20
    csw_bit = [0, 0, 0, 0, 0]
    
    csw = int(input("enter csw value (0~20): "))
    if(csw > 20 or csw < 0):
        print("ERROR: invalid input!")
        return -1
    else: 
        csw_bit[0] = csw%2
        csw_bit[1] = (csw>>1)%2
        csw_bit[2] = (csw>>2)%2
        csw_bit[3] = (csw>>3)%2
        csw_bit[4] = (csw>>4)%2
        print("debug", csw_bit)
        
        dut_spi.write_single(11,csw_bit[0],csw_bit[1],csw_bit[2],csw_bit[3],csw_bit[4],0,0,0)
        dut_spi.commit_w_addr0to15()
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
    

    
    