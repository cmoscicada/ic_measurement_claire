from pynq import Overlay
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

from pynq.lib import AxiGPIO
gpio_pynq_dsm_lpf_en_complete_flag_ip = ol.ip_dict['gpio_pynq_dsm_lpf_en_complete_flag']
gpio_pynq_dsm_lpf_en = AxiGPIO(gpio_pynq_dsm_lpf_en_complete_flag_ip).channel1
gpio_pynq_dsm_lpf_complete_flag = AxiGPIO(gpio_pynq_dsm_lpf_en_complete_flag_ip).channel2

from pynq import MMIO
IP_BASE_ADDRESS = 0x40000000
ADDRESS_RANGE = 0x2000  #0x1000 => 4096, 0x2000 => 8192
#ADDRESS_OFFSET = 0x10   #0x10 => 16, 0x20 => 32
RST_DATA = 0x00000000
mmio_pynq_dsm_lpf = MMIO(IP_BASE_ADDRESS, ADDRESS_RANGE)

import numpy as np
import time 


def rst():
    addr_wr = 0
    addr_rd = 0
    #reset all bram (make lpf_en = 0)
    gpio_pynq_dsm_lpf_en.write(0,0xf)
    #reset all bram (write RST_DATA to all address)
    while(addr_wr < 8192):
        mmio_pynq_dsm_lpf.write(addr_wr,RST_DATA)
        addr_wr = addr_wr + 1
      
    #read all bram data 
    while(addr_rd < 8192):
        rd_data = mmio.read(addr_rd)
        print("%i address data: %h" %(addr_rd) %(rd_data))
    

#def start_lpf():
    
    

