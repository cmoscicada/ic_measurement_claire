from pynq import Overlay
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

from pynq.lib import AxiGPIO
gpio_pynq_dsm_lpf_en_complete_flag_ip = ol.ip_dict['gpio_pynq_dsm_lpf_en_complete_flag']
gpio_pynq_dsm_lpf_en = AxiGPIO(gpio_pynq_dsm_lpf_en_complete_flag_ip).channel1
gpio_pynq_dsm_lpf_complete_flag = AxiGPIO(gpio_pynq_dsm_lpf_en_complete_flag_ip).channel2

from pynq import MMIO
IP_BASE_ADDR = 0x40000000
ADDR_RANGE = 0x2000  #0x1000 => 4096, 0x2000 => 8192
ADDR_OFFSET = 0x4   #0x10 => 16, 0x20 => 32
RST_DATA = 0x1f0a0c12
mmio_pynq_dsm_lpf = MMIO(IP_BASE_ADDR, ADDR_RANGE)

import numpy as np
import time 


def rst():
    addr_wr = 0
    addr_rd = 0
    #reset all bram (make lpf_en = 0)
    gpio_pynq_dsm_lpf_en.write(0,0xf)
    #reset all bram (write RST_DATA to all address)
    while(addr_wr < ADDR_RANGE): 
        mmio_pynq_dsm_lpf.write(addr_wr,RST_DATA)
        addr_wr = addr_wr + ADDR_OFFSET
      
    #read all bram data 
    while(addr_rd < ADDR_RANGE):
        rd_data = mmio_pynq_dsm_lpf.read(addr_rd)
        addr_index = addr_rd/4
        print("%ith address data: %s" %(addr_rd, hex(rd_data)))
        addr_rd = addr_rd + ADDR_OFFSET
    

def do_lpf():
    #reset bram memory
    gpio_pynq_dsm_lpf_en.write(1,0xf)
    time.sleep(0.01)
    gpio_pynq_dsm_lpf_en.write(0,0xf)
        
    #write 1b dsm data to bram while finish flag = 0
    #print("Do LPF. 1b DSM data recording start!")
    flag = 0
    while(flag == 0):
        gpio_pynq_dsm_lpf_en.write(1,0xf)
        flag = gpio_pynq_dsm_lpf_complete_flag.read()
    
    #make enable low after flag becomes 1 
    gpio_pynq_dsm_lpf_en.write(0,0xf)
    #print("Finished to record 32*2048 1b DSM data!")
    
    #calculate DC average value 
    lpf_dc_raw = 0
    addr_rd = 0
    while(addr_rd < ADDR_RANGE):
        index = 0
        rd_data = mmio_pynq_dsm_lpf.read(addr_rd)
        while(index < 32):
            data = rd_data >> index
            bit = data%2
            if(bit == 1 or bit == 0):
                #print("[DEBUG] current data: %s" %(bin(data)))
                #print("[DEBUG] current bit: %s" %(bin(bit)))
                lpf_dc_raw = lpf_dc_raw + bit
                index = index + 1
            else:
                print("ERROR: error on 1b DSM data write phase")
                return -1
        addr_rd = addr_rd + ADDR_OFFSET
    
    #plot data
    #plot_raw_data()
    
    #print("Accumulated raw data: %i" %(lpf_dc_raw))
    print("Average value: %f" %(lpf_dc_raw/65536))
    
    
    
def plot_raw_data():
    #read all bram data 
    addr_rd = 0
    while(addr_rd < ADDR_RANGE):
        rd_data = mmio_pynq_dsm_lpf.read(addr_rd)
        addr_index = addr_rd/4
        print("%s ==> %ith address data" %(bin(rd_data), addr_rd))
        addr_rd = addr_rd + ADDR_OFFSET
    
    

