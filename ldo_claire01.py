from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

import ldo


#LDO BOARD0
VCTL_KVCO_BASE = 100.0
VDD_A_GL = 400.0
VDDA_LDS = 400.0
VDDAG25 = 2500.0 
VDD_CHOP = 400.0 
VDD_CP = 400.0
VDD = 400.0
VDD_LEAK_DMY_IN = 400.0

#LDO BOARD1
VDD_DIV_LOGIC = 400.00 
VDD_BBPFD = 400.0
VDD_DIV_LOGIC_TEST = 400.0 
VDD_GVCO_FIC = 400.0
VDD_GVCO_CTAT = 400.0 
VDD_CORE_DBUF = 400.0
VDD03_TEST = 300.0
VDD10_TEST = 1000.0 

def change_core_supply_command():
    print("CLAIRE01: Target Info.")
    #board 0
    print("0)VCTL_KVCO_BASE 1)VDD_A_GL 2)VDDA_LDS 3)VDD_CHOP 4)VDD_CP 5)VDD ")
    #board 1 
    print("6)VDD_DIV_LOGIC 7)VDD_BBPFD 8)VDD_DIV_LOGIC_TEST 9)VDD_GVCO_FIC 10)VDD_GVCO_CTAT")
    print("11)VDD_CORE_DBUF 12)VDD03_TEST 13)VDD10_TEST")
  
    target_num = int(input("Choose the target (0 ~ 13): "))
    
    print('')
    
    ##map board number and address and read the current voltage value
    if(target_num == 0):
        brd_num = 0
        addr = 0
        print("Current VCTL_KVCO_BASE value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 1):
        brd_num = 0
        addr = 1 
        print("Current VDD_A_GL value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 2):
        brd_num = 0
        addr = 2 
        print("Current VDDA_LDS value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 3):
        brd_num = 0
        addr = 4
        print("Current VDD_CHOP value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 4):
        brd_num = 0
        addr = 5 
        print("Current VDD_CP value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 5):
        brd_num = 0
        addr = 6 
        print("Current VDD value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 6):
        brd_num = 1
        addr = 0
        print("Current VDD_DIV_LOGIC value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 7):
        brd_num = 1
        addr = 1
        print("Current VDD_BBPFD value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 8):
        brd_num = 1
        addr = 2 
        print("Current VDD_DIV_LOGIC_TEST value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 9):
        brd_num = 1
        addr = 3
        print("Current VDD_GVCO_FIC value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 10):
        brd_num = 1
        addr = 4 
        print("Current VDD_GVCO_CTAT value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 11):
        brd_num = 1
        addr = 5 
        print("Current VDD_CORE_DBUF value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 12):
        brd_num = 1
        addr = 6 
        print("Current VDD03_TEST value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    elif(target_num == 13):
        brd_num = 1
        addr = 7
        print("Current VDD10_TEST value: %0.3fmV" %(ldo.read_single(brd_num, addr)))
        
    else:
        print("invalid target number!")
        return -1
    
    #Write new value
    new_volt = float(input("Target voltage (e.g. 400.01 ==> 400.01mV): "))
    ldo.ldo_w_single(brd_num, addr, new_volt)
   