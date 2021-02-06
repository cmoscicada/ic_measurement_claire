from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

import numpy as np
import time

trig_ldo_dut_ip = ol.ip_dict['gpio_spi_trig_ldo_dut']
dut_tx_rx_data_ip = ol.ip_dict['gpio_spi_dut_tx_rx_data']
ts_rst_dut_rst_ip = ol.ip_dict['gpio_spi_ts_rst_dut_rst']

trig_dut = AxiGPIO(trig_ldo_dut_ip).channel2
dut_tx_data = AxiGPIO(dut_tx_rx_data_ip).channel1
dut_rx_data = AxiGPIO(dut_tx_rx_data_ip).channel2
dut_rst = AxiGPIO(ts_rst_dut_rst_ip).channel2

def rst():
    dut_rst.write(0,0xf)
    time.sleep(0.1)
    dut_rst.write(1,0xf)
    time.sleep(0.1)
    dut_rst.write(0,0xf)
    time.sleep(0.1)


def send_trig():
    trig_val = trig_dut.read()
    #print('prev trig val: %i' %(trig_val))
    trig_dut.write(trig_val^1,0xf)
    trig_val = trig_dut.read()
    #print('current trig val: %i' %(trig_val))


def make_addr_packet(addr):
    addr_ld1 = addr%2
    addr_ld2 = addr%4
    addr_ld3 = addr%8
    addr_ld4 = addr%16
    addr_ld5 = addr%32
    addr_ld6 = addr%64
    addr_ld7 = addr%128
    
    addr0 = addr_ld1
    addr1 = (addr_ld2 - addr_ld1)>>1
    addr2 = (addr_ld3 - addr_ld2)>>2
    addr3 = (addr_ld4 - addr_ld3)>>3
    addr4 = (addr_ld5 - addr_ld4)>>4
    addr5 = (addr_ld6 - addr_ld5)>>5
    addr6 = (addr_ld7 - addr_ld6)>>6 
    
    #print(addr0, addr1, addr2, addr3, addr4, addr5, addr6)
    
    return (addr6) + (addr5 << 1) + (addr4 << 2) + (addr3 << 3) + (addr2 << 4) + (addr1<<5) + (addr0 << 6)

#def write_single(addr, d0, d1, d2, d3, d4, d5, d6, d7):
    

def write_single_wc(): #dut spi write with command
    addr = int(input("target addr: "))
    print(' ')
    """
    addr_ld1 = addr%2
    addr_ld2 = addr%4
    addr_ld3 = addr%8
    addr_ld4 = addr%16
    addr_ld5 = addr%32
    addr_ld6 = addr%64
    addr_ld7 = addr%128
    
    addr0 = addr_ld1
    addr1 = (addr_ld2 - addr_ld1)>>1
    addr2 = (addr_ld3 - addr_ld2)>>2
    addr3 = (addr_ld4 - addr_ld3)>>3
    addr4 = (addr_ld5 - addr_ld4)>>4
    addr5 = (addr_ld6 - addr_ld5)>>5
    addr6 = (addr_ld7 - addr_ld6)>>6 
    
    #print(addr0, addr1, addr2, addr3, addr4, addr5, addr6)
    
    addr_reversed = (addr6) + (addr5 << 1) + (addr4 << 2) + (addr3 << 3) + (addr2 << 4) + (addr1<<5) + (addr0 << 6)
    """
    addr_reversed = make_addr_packet(addr)

    #print(addr_reversed)
    
    weight_array = np.array([128,64,32,16,8,4,2,1])
    index = 0
    data_packet = 0 
    for weight in weight_array:
        #print(weight)
        print(index,"th bit")
        current_bit = int(input("enter the value (1,0):"))
        if(current_bit > 1): 
            print("FALSE INPUT!!!")
            return 0
        else:
            data_packet = data_packet + current_bit * weight 
        index = index + 1
        print(' ')
        
    spi_packet = (0<<15) + (addr_reversed<<8) + data_packet
    #print(hex(data_packet), hex(addr_reversed), hex(spi_packet))
 
    dut_tx_data.write(int(spi_packet),0xffff)
    send_trig()
    
    print("DUT SPI packet: ",hex(spi_packet),"sent")
    
def update_addr0to15():
    #write 1 to addr 127 & write 0 to addr 127 (after write addr 0 ~ 15)
    #update addr 0 ~ 15 together 
    
    spi_packet_127_0 = (0<<15) + (127<<8) + (0<<7)
    spi_packet_127_1 = (0<<15) + (127<<8) + (1<<7)
    
    dut_tx_data.write(spi_packet_127_1,0xffff)
    send_trig()
    
    dut_tx_data.write(spi_packet_127_0,0xffff)
    send_trig()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
