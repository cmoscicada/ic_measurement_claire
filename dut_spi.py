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
   
    
def read_wc():
    addr = int(input("target read addr.:"))
    print('')
    
    if(addr > 63):
        print("invalid target address!")
        return -1 
    
    addr_reversed = make_addr_packet(addr)
    spi_packet = (1<<15) + (addr_reversed<<8) + 0
    
    dut_tx_data.write(spi_packet,0xffff)
    send_trig()
    
    data_read = dut_rx_data.read()
    bin_data_read = bin(data_read)
    
    #print("addr %i data: 0x%X",data_read)
    #print("addr %i data ==> ", bin_data_read)
    
    print("Addr:",addr,"|| data: ",bin_data_read[2:].zfill(8),"read")
    
    return bin_data_read
    
    

def write_single_wc(): #dut spi write with command
    addr = int(input("target addr: "))
    print(' ')
   
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
        
        
    spi_packet = (0<<15) + (addr_reversed<<8) + data_packet
    #print(hex(data_packet), hex(addr_reversed), hex(spi_packet))
 
    dut_tx_data.write(int(spi_packet),0xffff)
    send_trig()
    print(' ')
    print("Addr:",addr,"|| data: ",bin(spi_packet%256)[2:].zfill(8),"sent")
    
def write_single(addr,b0,b1,b2,b3,b4,b5,b6,b7): #dut spi write with input
    
    addr_reversed = make_addr_packet(addr)
    
    weight_array = np.array([128,64,32,16,8,4,2,1])
    data_array = np.array([b0,b1,b2,b3,b4,b5,b6,b7])
    
    index = 0
    data_packet = 0 
    for weight in weight_array:
        #print(weight)
        #print(index,"th bit")
        current_bit = data_array[index]
        #print("debug: data value ==>",current_bit)
        if(current_bit > 1): 
            print("FALSE INPUT!!!")
            return 0
        else:
            data_packet = data_packet + current_bit * weight 
        index = index + 1
        
    spi_packet = (0<<15) + (addr_reversed<<8) + data_packet
    #print(hex(data_packet), hex(addr_reversed), hex(spi_packet))
 
    dut_tx_data.write(int(spi_packet),0xffff)
    send_trig()
    
    print("Addr:",addr,"|| data: ",bin(spi_packet%256)[2:].zfill(8),"sent")
    
    
def commit_w_addr0to15():  ## write commit (from addr0 to addr15)
    #write 1 to addr 127 & write 0 to addr 127 (after write addr 0 ~ 15)
    #update addr 0 ~ 15 together 
    
    write_single(127,1,0,0,0,0,0,0,0)
    
    write_single(127,0,0,0,0,0,0,0,0)
    
    """
    spi_packet_127_0 = (0<<15) + (127<<8) + (0<<7)
    spi_packet_127_1 = (0<<15) + (127<<8) + (1<<7)
    
    dut_tx_data.write(spi_packet_127_1,0xffff)
    send_trig()
    
    dut_tx_data.write(spi_packet_127_0,0xffff)
    send_trig()
    """
    
def sel_io_50ohm(): ## select signal to plot by 50 ohm io 
    #signal selection & io enable 
    b0 = int(input("50Ohm driver on/off (""0"": on, ""1"": off): "))
    if (b0 == 1):
        print("50ohm driver shut down!")
        write_single(24,1,0,0,0,0,0,0,0)
        return 0
    elif (b0 == 0):
        sig_sel = int(input("select signal: 0) main clk 1) ck_gvco_ctat 2) ck_gvco_fic 3) vss ==> "))
        b1 = int(sig_sel%2)
        b2 = int((sig_sel>1))
        print("debug",b2,b1)
        addr = 24
        write_single(addr,b0,b1,b2,0,0,0,0,0)
    else:
        print("invalid input!")
        return -1 
    
    
def set_str_io_50ohm(): #program 50ohm io pull down strength
    pull_strength = int(input("enter 50-ohm io strength [PULL] (0~8)"))
    pull_str_bit = [1, 1, 1, 1, 1, 1, 1, 1]
    
    index_l = pull_strength
    while (index_l > 0):
        #print("        debug: index: ", index)
        pull_str_bit[index_l-1] = 0
        index_l = index_l - 1
    
    push_strength = int(input("enter 50-ohm io strength [PUSH] (0~8)"))
    push_str_bit = [1, 1, 1, 1, 1, 1, 1, 1]
    
    index_h = push_strength
    while (index_h > 0):
        #print("        debug: index: ", index)
        push_str_bit[index_h-1] = 0
        index_h = index_h - 1
    
    #print("debug", pull_str_bit)
    #write_single(22,1,1,1,1,1,1,1,1) ## disable push
    write_single(22,push_str_bit[0],push_str_bit[1],push_str_bit[2],push_str_bit[3],push_str_bit[4],push_str_bit[5],push_str_bit[6],push_str_bit[7])
    write_single(23,pull_str_bit[0],pull_str_bit[1],pull_str_bit[2],pull_str_bit[3],pull_str_bit[4],pull_str_bit[5],pull_str_bit[6],pull_str_bit[7])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
