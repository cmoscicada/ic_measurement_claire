from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

import time

brd0_vref = 3924
brd1_vref = 3924
dac_fs_bin = 65535
one_us = 1/1000000

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

#print(color.BOLD + 'Hello World !' + color.END)



trig_ldo_dut_ip = ol.ip_dict['gpio_spi_trig_ldo_dut']
ldo_tx_rx_data_ip = ol.ip_dict['gpio_spi_ldo_tx_rx_data']
ldo_brd_sel_ts_trig_ip = ol.ip_dict['gpio_spi_ldo_brd_sel_ts_trig']

trig_ldo = AxiGPIO(trig_ldo_dut_ip).channel1
ldo_tx_data = AxiGPIO(ldo_tx_rx_data_ip).channel1
ldo_rx_data = AxiGPIO(ldo_tx_rx_data_ip).channel2
ldo_brd_sel = AxiGPIO(ldo_brd_sel_ts_trig_ip).channel1

def ldo_send_trig():
    trig_val = trig_ldo.read()
    #print('prev trig val: %i' %(trig_val))
    trig_ldo.write(trig_val^1,0xf)
    trig_val = trig_ldo.read()
    #print('current trig val: %i' %(trig_val))
    
#def ldo_brd_sel(brd_num):
#    ldo_brd_sel.write(brd_num,0xff)

def ldo_w_single_wc(): #ldo write with command 
    brd_num = int(input("target brd number (0 ~ 3): "))
    addr = int(input("target addr.: "))
    volt = float(input("target voltage(e.g. 400.1mV --> 400.1: "))
    #print('brd_num: %i addr: %i volt: %f'%(brd_num, addr, volt))
    if (brd_num == 0):
        vref = brd0_vref
    elif (brd_num == 1):
        vref = brd1_vref
    else:
        print("ERROR: invalid board number!")
        return -1
    
    if((volt)>vref):
        print("WARINING: input voltage EXCEEDS the VREF level of the ldo board!")
        dac_data = dac_fs_bin
    else:
        dac_data = ((volt)/vref)*dac_fs_bin
    
    
    #print ('dac_w_data: %d' %(dac_w_data))
    dac_packet = (3<<20) + (addr<<16) + int(dac_data)
    print('dac packet: %i' %(dac_packet))    
    print('dac packet in Hex: %X' %(dac_packet))
    
    ldo_brd_sel.write(brd_num,0xff)
    ldo_tx_data.write(dac_packet,0xffffff)
    ldo_send_trig()

def ldo_w_single(brd_num, addr, volt): #ldo write
    #print('brd_num: %i addr: %i volt: %f mV'%(brd_num, addr, volt))
    if (brd_num == 0):
        vref = brd0_vref
    elif (brd_num == 1):
        vref = brd1_vref
    else:
        print("ERROR: invalid board number!")
        return -1
        
    if((volt)>vref):
        print("WARINING: input voltage EXCEEDS the VREF level of the ldo board!")
        dac_data = dac_fs_bin
    else:
        dac_data = ((volt)/vref)*dac_fs_bin
    
    #print ('dac_w_data: %d' %(dac_w_data))
    dac_packet = (3<<20) + (addr<<16) + int(dac_data)
    #print('dac packet: %i' %(dac_packet))    
    #print('dac packet in Hex: %X' %(dac_packet))
    
    ldo_brd_sel.write(brd_num,0xf)
    ldo_tx_data.write(dac_packet,0xffffff)
    ldo_send_trig()    
    
def read_single(brd_num, addr): ## ldo read
    if (brd_num == 0):
        vref = brd0_vref
    elif (brd_num == 1):
        vref = brd1_vref
    else:
        print("ERROR: invalid board number!")
        return -1
        
    if(addr > 7):
        print("ERROR: invalid address value!")
        return -1
    
    #set board to be read 
    ldo_brd_sel.write(brd_num,0xf)
    time.sleep(100*one_us) #wait 100us
    
    #make spi packet (read instruction)
    #command: 1001 (setup redback reg.) 
    rd_inst_packet = (9<<20) + (addr<<16) + 0
    ldo_tx_data.write(rd_inst_packet,0xffffff)
    ldo_send_trig()
    time.sleep(10*one_us) #wait 10us
    
    #make read packet (NOP mode)
    #command: 0000 (no operation)
    rd_inst_packet = (0<<20) + (addr<<16) + 0
    ldo_tx_data.write(rd_inst_packet,0xffffff)
    ldo_send_trig()
    time.sleep(10*one_us) #wait 10us
    
    #read readback data and print
    rb_data_raw = ldo_rx_data.read()%0x10000
    #print("debug: rb_data_raw in Hex: ", hex(rb_data_raw))
    
    rb_data_mv = 0.0
    if(brd_num == 0):
        rb_data_mv = (rb_data_raw/dac_fs_bin)*brd0_vref
    elif(brd_num == 1):
        rb_data_mv = (rb_data_raw/dac_fs_bin)*brd1_vref
    
    #print("Current voltage: ",0.2f(rb_data_mv),"mV","      ","board: ",brd_num,"addr: ",addr, )
    print("Current voltage: %0.3fmV   [brd num: %i & addr.: %i]" %(rb_data_mv, brd_num, addr) )
    
    return rb_data_mv
    


    
    