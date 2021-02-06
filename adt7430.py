from pynq import Overlay
from pynq.lib import AxiGPIO
ol = Overlay("./overlays/CICADA_N_CLAIRE.bit")

#import numpy as np
import time

ldo_brd_sel_ts_trig_ip = ol.ip_dict['gpio_spi_ldo_brd_sel_ts_trig']
ts_24b_tx_rx_data_ip = ol.ip_dict['gpio_spi_ts_24b_tx_rx_data']
ts_rst_dut_rst_ip = ol.ip_dict['gpio_spi_ts_rst_dut_rst']
ts_bit_sel_ip = ol.ip_dict['gpio_ts_bit_sel']

ts_trig = AxiGPIO(ldo_brd_sel_ts_trig_ip).channel2
ts_24b_tx_data = AxiGPIO(ts_24b_tx_rx_data_ip).channel1
ts_24b_rx_data = AxiGPIO(ts_24b_tx_rx_data_ip).channel2
ts_rst = AxiGPIO(ts_rst_dut_rst_ip).channel1
ts_bit_sel = AxiGPIO(ts_bit_sel_ip).channel1

####################################################################
#[7]: resolution (RES) //[6:5] operation mode (OP_MODE)
#[4] interrupt/comparator mode (INTCT) //[3]: int polarity (INT_P)
#[2] ct polarity (CT_P) //[1:0] fault number (F_QUE)
##################################################################
#*16bit resolution (1) *operation mode(10: 1 SPS mode) (01: one-shot mode) *comparator mode (1)
#*active high int (1) *active high ct (1) *4 faults (deci.: 3)
###################################################################

F_QUE = 3
CT_P = 1
INT_P = 1
INTCT = 1
OP_MODE = 1
RES = 1

T_CRIT = 100
T_HYST = 1
#TEMP_SIGN_TH = 0 # "1" ==> minus "0" ==> plus
#TEMP_SIGN_TL = 0 #"1" ==> minus "0" ==> plus
#T_HIGH = 25
#T_LOW = 23
READ_ITERATION = 20 # default iteration number 
TIME_INTERVAL_SEC = 2 

#######################################################################
def rst():
    ts_rst.write(0,0xf)
    time.sleep(0.1)
    ts_rst.write(1,0xf)
    time.sleep(0.1)
    ts_rst.write(0,0xf)
    
    #wait 100ms to device reset
    time.sleep(0.1)
 
    #read the device ID (register address 0x03). It should be read 0xC3
    #Set the read command packet (01011000_11111111 ==> 0x58FF)
    w_16b(0x58ff)
    #dev_id = ts_24b_rx_data.read()
    
    #time.sleep(0.1)
    
    #print("debug tx data:",ts_24b_tx_data.read())
    #print("debug rx data:",ts_24b_rx_data.read())
    
    
    dev_id = ts_24b_rx_data.read()%(0x100)
    
    print("read ad7430 device id: ",hex(dev_id))
    if(dev_id == 0xc3):
        print("device reset success!")
    else:
        print("device reset failed!")
        return -1   

def trig():
    trig_val = ts_trig.read()
    #print(trig_val)
    ts_trig.write(trig_val^1,0xf)
    trig_val = ts_trig.read()
    #print(trig_val)
    

def w_16b(data):
    ts_24b_tx_data.write(data,0xffff)
    ts_bit_sel.write(0,0xf)
    trig()
    time.sleep(100/1000000)
    
def w_24b(data):
    ts_24b_tx_data.write(data,0xffffff)
    ts_bit_sel.write(1,0xf)
    trig()
    time.sleep(100/1000000)
    
#def r_16b():
    
#def r_24b():

    

def set_dev():
    #F_QUE = int(input("enter fault number: "))
    #CT_P = int(input("enter ct polarity: "))
    #INT_P = int(input("enter int polarity: "))
    #INTCT = int(input("enter int/ct value: "))
    OP_MODE = int(input("enter operation mode (1: one-shot mode & 2: SPS mode: "))
    if(OP_MODE > 2):
        print("invalid OP_MODE!")
        return -1
    elif(OP_MODE <1):
        print("invalid OP_MODE")
        return -1
    #RES = int(input("enter resolution: "))
    
    config_reg_data = F_QUE + (CT_P<<2) + (INT_P<<3) + (INTCT<<4) + (OP_MODE<<5) + (RES<<7)
    config_reg_packet = 0x800 + config_reg_data;

    w_16b(config_reg_packet)
    
    #Set Tcrit (addr: 0x04)
    #[16bit critical overtemp limit, stored in twos complement format]
    #command byte: 00100000 (0x20)
    #data: 12800(decimal), (0x3200)
    T_CRIT = float(input("enter T_CRIT value: "))
    
    t_crit_packet = int(0x200000 + T_CRIT*128);
    
    w_24b(t_crit_packet)
    
    #Set Thyst (default value is 0101 (5deg)) (addr: 0x5)
    #[8bit, last 4 digit is vaild data]
    #e.g. 1deg Thyst ==> XXXX0001
    #set Thyst to 2deg
    #command byte: 00101000
    #data: 00000010
    T_HYST = float(input("enter T_HYST value: "))
    
    t_hyst_packet = int(0x2800 + T_HYST);

    w_16b(t_hyst_packet)
       
    ## set target temp and tolerance 
    T_TARGET = float(input("enter Target temp.: "))
    T_TOL = float(input("enter temp. tolerance in celcius: "))
    T_HIGH = T_TARGET + T_TOL/2
    T_LOW = T_TARGET - T_TOL/2
    
    #print("debug: h_high val: ", T_HIGH)
    #print("debug: h_low val: ", T_LOW)
    
    
    #Set Thigh
    #[16bit overtemp limit, stored in twos complement format]
    #command byte: 00110000 (0x30)
    
    if (T_HIGH < 0): #minus value case
        t_high_packet = 0x300000 - T_HIGH*128 + 65536
        #print("debug: t_high_packet is:", t_high_packet)
    else:
        t_high_packet = 0x300000 + T_HIGH*128
        #print("debug: t_high_packet is:", t_high_packet)
        
    w_24b(int(t_high_packet))
    print("Target T_HIGH: ", T_HIGH)
    
    #Set Tlow (addr: 0x07)
    #[16bit overtemp limit, stored in twos complement format]
    #command byte: 00111000 (0x38)
    if (T_LOW < 0): #minus value case
        t_low_packet = 0x380000 - T_LOW*128 + 65536
        #print("debug: t_low_packet is:", t_low_packet)
    else:
        t_low_packet = 0x380000 + T_LOW*128
        #print("debug: t_low_packet is:", t_low_packet)
    w_24b(int(t_low_packet))
    
    print("Target T_LOW: ", T_LOW)
    

def rd_temp():    
    #//Read the temp. register (register address 0x02).
    #//Set the read command packet (01010000_11111111_11111111 ==> 0x50FFFF)
    
    w_24b(0x50ffff);
    
    temp_rd = ts_24b_rx_data.read()%(0x10000)
    
    temp_sign = temp_rd/(0x8000);
    
    if(temp_sign == 1):
        temp_val = (temp_rd - 65536)/(128)
    else:
        temp_val = (temp_rd)/128
        
    print("Current temperature: %0.2f" %(temp_val))
        
    return float(temp_val)    
        
def consecutive_read():
    #reset device 
    rst()
    time.sleep(0.1)
    
    num = int(input("enter read iteration numbers: "))
    time_interval = float(input("enter time interval in sec: (>1s)"))
    
    if(time_interval < 1):
        print("Incorrect time interval value !")
        return 0
    
    
    temp = []
    
    index = 0
    temp_tot = 0
    
    while(index < num):
        #set config reg. to one-shot mode 
        config_reg_data = 4 + (1<<2) + (1<<3) + (1<<4) + (1<<5) + (1<<7)
        config_reg_packet = 0x800 + config_reg_data;
        w_16b(config_reg_packet)
         
        #temp[index] = rd_temp()
        temp_tot = temp_tot + rd_temp()
        index = index + 1
        #todo make one-shot mode 
        time.sleep(time_interval)
    
    temp_avg = temp_tot/num
    
    print("average temperature is: ", temp_avg)
    





    
    
"""
static int ADT7320_Rd_Tcrit_Reg()
{
	//Read the T_crit setpoint reg (register address 0x04). If dev. resetted, it should be read 0x4980
	//Set the read command packet (01100000_11111111_11111111 ==> 0x60FFFF)
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
			  ((SPI_TS_TX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
			  XGPIO_DATA_OFFSET, 0x60FFFF);
	//select 24bit SPI Master (write "1")
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_TRIG_N_BIT_SEL),
				  ((SPI_TS_BIT_SEL_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
				  XGPIO_DATA_OFFSET, 1);
	//send read command packet & wait 100us (24packet communication takes ~100us)
	GpioTSTrig();
	usleep(100);
	//read the packet
	u32 adt7320_data_rd = XGpio_ReadReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
								  ((SPI_TS_RX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
								  XGPIO_DATA_OFFSET);
	//xil_printf("Read spi packet: %X \n\r",adt7320_data_rd);
	u32 adt7320_tcrit = (adt7320_data_rd%0x10000); // extract last four digit in hex.
	//xil_printf("ADT7320 Tcrit val: %X \n\r",adt7320_tcrit);

	u32 temp_sign = adt7320_tcrit/(0x8000);
	float tmp_val_flt;

	if (temp_sign == 1 ){
		tmp_val_flt = ((float)adt7320_tcrit - 65536)/128;
		printf("Tcrit value: %.2f degree\n\r", tmp_val_flt);
	}
	else if (temp_sign == 0){
		tmp_val_flt = ((float)adt7320_tcrit)/(128);
		printf("Tcrit value: %.2f degree\n\r", tmp_val_flt);
	}

	// Return
	return XST_SUCCESS;
}        
 

static int ADT7320_Rst_N_Verify()
{
	//reset adt7320
	GpioTSRst();

	//Read the device ID (register address 0x03). It should be read 0xC3
	ADT7320_Rd_Dev_Id();

	xil_printf("\n\r* Read config reg value after reset.\n\r");
	ADT7320_Rd_Config_Reg();

	xil_printf("\n\r* Read default Tcrit value. value should be +147.00 degree\n\r");
	ADT7320_Rd_Tcrit_Reg();

	xil_printf("\n\r* Read default Thigh value. value should be +64.00 degree\n\r");
	ADT7320_Rd_Thigh_Reg();

	xil_printf("\n\r* Read default Thyst value. value should be 5 degree\n\r");
	ADT7320_Rd_Thyst_Reg();

	xil_printf("\n\r* Read default Tlow value. value should be +10.00 degree\n\r");
	ADT7320_Rd_Tlow_Reg();

	// Return
	return XST_SUCCESS;
}

static int ADT7320_Rd_Config_Reg()
{
	//Read the config. register (register address 0x01). If dev. resetted, it should be read 0x00
	//Set the read command packet (01001000_11111111 ==> 0x48FF)

	AD7320_W_16bit(0x48FF);

	//read the packet
	u32 adt7320_data_rd = XGpio_ReadReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
								  ((SPI_TS_RX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
								  XGPIO_DATA_OFFSET);
	//xil_printf("Read spi data packet is: %X \n\r",adt7320_data_rd);
	u32 config_reg_val = (adt7320_data_rd%0x100); // extract last two digit in hex.
	//xil_printf("ADT7320 config reg val: 0x%X \n\r",config_reg_val);
	u32 fault_queue = (config_reg_val%4);
	u32 ct_pin_polarity = (config_reg_val%8) - fault_queue;
	//xil_printf("[DEBUG] data8: %i",(config_reg_val%8));
	//xil_printf("[DEBUG] data16: %i",(config_reg_val%16));
	//xil_printf("[DEBUG] ct_pin polarity: %i\n\r",ct_pin_polarity);
	u32 int_pin_polarity = (config_reg_val%16) - (config_reg_val%8);
	//xil_printf("[DEBUG] int_pin polarity: %i\n\r",int_pin_polarity);
	u32 int_ct_mode = (config_reg_val%32) - (config_reg_val%16);
	//xil_printf("[DEBUG] int_ct_mode polarity: %i\n\r",int_ct_mode);
	u32 op_mode = (config_reg_val%128) - (config_reg_val%32);
	u32 resolution = (config_reg_val%256) - (config_reg_val%128);
	xil_printf("fault setup: %i faults\n\r",fault_queue+1);
	xil_printf("ct_pin_polarity value in binary: %i\n\r",ct_pin_polarity/4);
	xil_printf("int_pin_polarity value in binary: %i\n\r",int_pin_polarity/8);
	xil_printf("int_ct_mode value in binary: %i\n\r",int_ct_mode/16);
	xil_printf("op_mode value in binary: %i%i\n\r",(op_mode-(op_mode%64))/64,((op_mode%64)/32));
	xil_printf("resolution value in binary: %i\n\r",resolution/128);

	// Return
	return XST_SUCCESS;
}

static int ADT7320_W_Config_Reg(u32 RES, u32 OP_MODE, u32 INTCT, u32 INT_P, u32 CT_P, u32 F_QUE)
{
	//Write Configuration Reg (addr: 0x01)

	//[7]: resolution (RES) //[6:5] operation mode (OP_MODE)
	//[4] interrupt/comparator mode (INTCT) //[3]: int polarity (INT_P)
	//[2] ct polarity (CT_P) //[1:0] fault number (F_QUE)

	//*16bit resolution (1) *operation mode(10: 1 SPS mode) (01: one-shot mode) *comparator mode (1)
	//*active high int (1) *active high ct (1) *4 faults (deci.: 3)

	u32 config_reg_data;
	//data string conversion to decimal
	config_reg_data = F_QUE + (CT_P<<2) + (INT_P<<3) + (INTCT<<4) + (OP_MODE<<5) + (RES<<7);
	//xil_printf("[DEGUG] config_reg_data: %X\n\r", config_reg_data);
	u32 config_reg_packet = 0x800 + config_reg_data;

	AD7320_W_16bit(config_reg_packet);

	// Return
	return XST_SUCCESS;
}

static int ADT7320_Rd_Thyst_Reg()
{
	//Read the Thyst register (register address 0x05).
	//Set the read command packet (01101000_11111111 ==> 0x68FF)
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
			  ((SPI_TS_TX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
			  XGPIO_DATA_OFFSET, 0x68FF);
	//select 16bit SPI Master (write "0")
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_TRIG_N_BIT_SEL),
				  ((SPI_TS_BIT_SEL_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
				  XGPIO_DATA_OFFSET, 0);
	//send read command packet & wait 100us (24packet communication takes ~100us)
	GpioTSTrig();
	usleep(100);
	//read the packet
	u32 adt7320_data_rd = XGpio_ReadReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
								  ((SPI_TS_RX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
								  XGPIO_DATA_OFFSET);
	//xil_printf("Read spi data packet is: %X \n\r",adt7320_data_rd);
	u32 thyst_val = (adt7320_data_rd%0x10); // extract last one digit in hex.
	xil_printf("Thyst value: %i degree \n\r",thyst_val);

	// Return
	return XST_SUCCESS;
}

static int ADT7320_Rd_Tcrit_Reg()
{
	//Read the T_crit setpoint reg (register address 0x04). If dev. resetted, it should be read 0x4980
	//Set the read command packet (01100000_11111111_11111111 ==> 0x60FFFF)
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
			  ((SPI_TS_TX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
			  XGPIO_DATA_OFFSET, 0x60FFFF);
	//select 24bit SPI Master (write "1")
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_TRIG_N_BIT_SEL),
				  ((SPI_TS_BIT_SEL_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
				  XGPIO_DATA_OFFSET, 1);
	//send read command packet & wait 100us (24packet communication takes ~100us)
	GpioTSTrig();
	usleep(100);
	//read the packet
	u32 adt7320_data_rd = XGpio_ReadReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
								  ((SPI_TS_RX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
								  XGPIO_DATA_OFFSET);
	//xil_printf("Read spi packet: %X \n\r",adt7320_data_rd);
	u32 adt7320_tcrit = (adt7320_data_rd%0x10000); // extract last four digit in hex.
	//xil_printf("ADT7320 Tcrit val: %X \n\r",adt7320_tcrit);

	u32 temp_sign = adt7320_tcrit/(0x8000);
	float tmp_val_flt;

	if (temp_sign == 1 ){
		tmp_val_flt = ((float)adt7320_tcrit - 65536)/128;
		printf("Tcrit value: %.2f degree\n\r", tmp_val_flt);
	}
	else if (temp_sign == 0){
		tmp_val_flt = ((float)adt7320_tcrit)/(128);
		printf("Tcrit value: %.2f degree\n\r", tmp_val_flt);
	}

	// Return
	return XST_SUCCESS;
}

static int ADT7320_Rd_Thigh_Reg()
{
	//Read the T_high setpoint reg (register address 0x06). If dev. resetted, it should be read 0x2000
	//Set the read command packet (01110000_11111111_11111111 ==> 0x70FFFF)
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
			  ((SPI_TS_TX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
			  XGPIO_DATA_OFFSET, 0x70FFFF);
	//select 24bit SPI Master (write "1")
	XGpio_WriteReg((GPIO_REG_BASEADDR_SPI_TS_TRIG_N_BIT_SEL),
				  ((SPI_TS_BIT_SEL_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
				  XGPIO_DATA_OFFSET, 1);
	//send read command packet & wait 100us (24packet communication takes ~100us)
	GpioTSTrig();
	usleep(100);
	//read the packet
	u32 adt7320_data_rd = XGpio_ReadReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
								  ((SPI_TS_RX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
								  XGPIO_DATA_OFFSET);
	//xil_printf("Read spi packet: %X \n\r",adt7320_data_rd);
	u32 adt7320_thigh = (adt7320_data_rd%0x10000); // extract last four digit in hex.
	//xil_printf("ADT7320 Thigh val: %X \n\r",adt7320_thigh);

	u32 temp_sign = adt7320_thigh/(0x8000);
	float tmp_val_flt;

	if (temp_sign == 1 ){
		tmp_val_flt = ((float)adt7320_thigh - 65536)/128;
		printf("Thigh value: %.2f degree\n\r", tmp_val_flt);
	}
	else if (temp_sign == 0){
		tmp_val_flt = ((float)adt7320_thigh)/(128);
		printf("Thigh value: %.2f degree\n\r", tmp_val_flt);
	}

	// Return
	return XST_SUCCESS;
}

static int ADT7320_Rd_Tlow_Reg()
{
	//Read the T_low setpoint reg (register address 0x07). If dev. resetted, it should be read 0x0500
	//Set the read command packet (01111000_11111111_11111111 ==> 0x78FFFF)
	AD7320_W_24bit(0x78FFFF);

	//read the packet
	u32 adt7320_data_rd = XGpio_ReadReg((GPIO_REG_BASEADDR_SPI_TS_RX_DATA_TX_DATA),
								  ((SPI_TS_RX_DATA_CHANNEL - 1) * XGPIO_CHAN_OFFSET) +
								  XGPIO_DATA_OFFSET);
	//xil_printf("Read spi packet: %X \n\r",adt7320_data_rd);
	u32 adt7320_tlow = (adt7320_data_rd%0x10000); // extract last four digit in hex.
	//xil_printf("ADT7320 Tlow val plus celcius: %i \n\r",adt7320_tlow/128);
	//xil_printf("ADT7320 Tlow val in minus celcius: %i \n\r",(adt7320_tlow-65536)/128);
	u32 temp_sign = adt7320_tlow/(0x8000);
	float tmp_val_flt;

	if (temp_sign == 1 ){
		tmp_val_flt = ((float)adt7320_tlow - 65536)/128;
		printf("Tlow value: %.2f degree\n\r", tmp_val_flt);
	}
	else if (temp_sign == 0){
		tmp_val_flt = ((float)adt7320_tlow)/(128);
		printf("Tlow value: %.2f degree\n\r", tmp_val_flt);
	}

	// Return
	return XST_SUCCESS;
}
"""