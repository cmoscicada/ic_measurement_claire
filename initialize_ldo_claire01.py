import ldo
import numpy as np
import time

##define voltage values for each (e.g. 400.1mV ==> 4000)
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

# 2*8 array 
ldo_array = np.array(
        [
            [
             #LDO BOARD0
             VCTL_KVCO_BASE, #LDO0: VCTL_KVCO_BASE
             VDD_A_GL, #LDO1: VDD_A_GL
             VDDA_LDS, #LDO2: VDDA_LDS
             VDDAG25, #LDO3: VDDAG25
             VDD_CHOP, #LDO4: VDD_CHOP
             VDD_CP, #LDO5: VDD_CP
             VDD, #LDO6: VDD
             VDD_LEAK_DMY_IN #LDO7: VDD_LEAK_DMY_IN
            ],
            #LDO BOARD1
            [
             VDD_DIV_LOGIC, #LDO0: VDD_DIV_LOGIC
             VDD_BBPFD, #LDO1: VDD_BBPFD
             VDD_DIV_LOGIC_TEST,#LDO2: VDD_DIV_LOGIC_TEST
             VDD_GVCO_FIC, #LDO3: VDD_GVCO_FIC
             VDD_GVCO_CTAT, #LDO4: VDD_GVCO_CTAT
             VDD_CORE_DBUF, #LDO5: VDD_CORE_DBUF
             VDD03_TEST, #LDO6: VDD03_TEST
             VDD10_TEST #LDO7: VDD10_TEST
            ]
        ]
            )

def all_zero():
    brd_num = 0
    for ldo_brd in ldo_array:
        addr = 0
        for voltage in ldo_brd:
                ldo.ldo_w_single(brd_num,addr,0)
                #time.sleep(0.1)
                addr = addr + 1
        brd_num = brd_num + 1

def initialize_ldo():
    brd_num = 0
    for ldo_brd in ldo_array:
        addr = 0
        for voltage in ldo_brd:
                print("Target board:",brd_num," ||Addr.:",addr," ||Voltage:",voltage,"mV")
                ldo.ldo_w_single(brd_num,addr,voltage)
                #time.sleep(0.1)
                addr = addr + 1
        brd_num = brd_num + 1
        
        
    