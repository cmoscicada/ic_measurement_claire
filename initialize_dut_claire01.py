import dut_spi
import numpy as np
import time

# 64*8 array 
spi_data_array = np.array(
        [
            [0,0,0,0,0,0,0,0],	##ADDR0
            [
                    1,	##DSM_OUT_GPIO_EN	("1" ==> CORE BUF ON) || DSM engine output
                    0,0,0,0,0,0,0
            ],	##ADDR1
            [
                    ##(PD) Decide offset amount Thermo code.
                    1,	##GAIN_B_THER<0>, "0" ==> offset path "ON"
                    1,	##GAIN_B_THER<1>, "0" ==> offset path "ON"
                    1,	##GAIN_B_THER<2>, "0" ==> offset path "ON"
                    1,	##GAIN_B_THER<3>, "0" ==> offset path "ON"
                    1,	##GAIN_B_THER<4>, "0" ==> offset path "ON"
                    1,	##GAIN_B_THER<5>, "0" ==> offset path "ON"
                    1,	##GAIN_B_THER<6>, "0" ==> offset path "ON"
                    1	##GAIN_B_THER<7>, "0" ==> offset path "ON"
            ],	##ADDR2
            [
                    ##(PD) Decide offset direction [11 ==> off || 01 or 10 ==> offset on]
                    1,	##OFFSET_P, "0" ==> offset path "ON"
                    1,	##OFFSET_N, "0" ==> offset path "ON"
                    0, 0, 0, 0, 0, 0
            ],	##ADDR3
            [
                    ##DSM engine PD offset amount control. 8bit Thermo code
                    ##more "0", more offset
                    1,1,1,1,1,1,1,1
            ],	##ADDR4
            [
                    ##DSM engine PD offset control
                    1, ##OFFSET_N, "0" ==> offset path "ON"
                    1, ##OFFSET_P, "0" ==> offset path "ON"
                    1, ##offset amount LSB control. "0" ==> offset path "ON"
                    1, ##DSM_CLK_SEL [1 ==> main clock || 0 ==> SWC clock ]
                    ##TODO: find below three bit functions
                    0, ##DSM_CLK_REF_DIR_SEL [1 ==> inverted || 0 ==> origin polarity] (TODO: what this means?)
                    0, ##PIN_UPB_DSM_DIR_SEL [1 ==> TPC_POUT_CTAT_B °¡ input À¸·Î µé¾î°¨]
                    0, ##PIN_DN_DSM_DIR_SEL [1 ==> DNA_TPC °¡ input À¸·Î µé¾î°¨]
                    0
            ],	##ADDR5
            [
                    0, ##CAP_INC_REF_DN<0> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_DN<1> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_DN<2> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_DN<3> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_DN<4> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_DN<5> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_DN<6> (TODO: What is the function of this?)
                    0 ##CAP_INC_REF_DN<7> (TODO: What is the function of this?)
            ],	##ADDR6
            [
                    0, ##CAP_INC_REF_DN<8> (TODO: What is the function of this?)
                    0,0,0,0,0,0,0
            ],	##ADDR7
            [
                    0, ##CAP_INC_REF_UP<0> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_UP<1> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_UP<2> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_UP<3> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_UP<4> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_UP<5> (TODO: What is the function of this?)
                    0, ##CAP_INC_REF_UP<6> (TODO: What is the function of this?)
                    0 ##CAP_INC_REF_UP<7> (TODO: What is the function of this?)
            ],	##ADDR8
            [
                    0, ##CAP_INC_REF_UP<8> (TODO: What is the function of this?)
                    0,0,0,0,0,0,0
            ],	##ADDR9
            [
                    ##KVCO Control || Target: O_THER_31_A<7:0>
                    ##Minimum: 0_0000 || Maximum: 0_1000
                    1,	##I_BIN_5B_CTL_A<0>
                    0,	##I_BIN_5B_CTL_A<1>
                    0,	##I_BIN_5B_CTL_A<2>
                    0,	##I_BIN_5B_CTL_A<3>
                    0,	##I_BIN_5B_CTL_A<4>
                    0, 0, 0
            ],	##ADDR10
            [
                    ##Csw Control || Target: O_THER_31_B<19:0>
                    ##Minimum: 0_0000 || Maximum: 1_0100
                    ##More "1" More Capacitance
                    0,	##I_BIN_5B_CTL_B<0>
                    1,	##I_BIN_5B_CTL_B<1>
                    0,	##I_BIN_5B_CTL_B<2>
                    1,	##I_BIN_5B_CTL_B<3>
                    0,	##I_BIN_5B_CTL_B<4>
                    0, 0, 0
            ],	##ADDR11
            [
                    ##DSM engine control. CAP_INC_UP<14:0> maximum: 0000_1111
                    ##(TODO: What is the function of this?)
                    0,	##I_BIN_8B_CTL_A<0>
                    0,	##I_BIN_8B_CTL_A<1>
                    0,	##I_BIN_8B_CTL_A<2>
                    0,	##I_BIN_8B_CTL_A<3>
                    0,	##I_BIN_8B_CTL_A<4>
                    0,	##I_BIN_8B_CTL_A<5>
                    0,	##I_BIN_8B_CTL_A<6>
                    0	##I_BIN_8B_CTL_A<7>
            ],	##ADDR12
            [
                    ##DSM engine control. CAP_INC_FBUP<14:0> maximum: 0000_1111
                    ##(TODO: What is the function of this?)
                    0,	##I_BIN_8B_CTL_B<0>
                    0,	##I_BIN_8B_CTL_B<1>
                    0,	##I_BIN_8B_CTL_B<2>
                    0,	##I_BIN_8B_CTL_B<3>
                    0,	##I_BIN_8B_CTL_B<4>
                    0,	##I_BIN_8B_CTL_B<5>
                    0,	##I_BIN_8B_CTL_B<6>
                    0	##I_BIN_8B_CTL_B<7>
            ],	##ADDR13
            [
                    ##DSM engine control. CAP_INC_DN<14:0> maximum: 0000_1111
                    ##(TODO: What is the function of this?)
                    0,	##I_BIN_8B_CTL_C<0>
                    0,	##I_BIN_8B_CTL_C<1>
                    0,	##I_BIN_8B_CTL_C<2>
                    0,	##I_BIN_8B_CTL_C<3>
                    0,	##I_BIN_8B_CTL_C<4>
                    0,	##I_BIN_8B_CTL_C<5>
                    0,	##I_BIN_8B_CTL_C<6>
                    0	##I_BIN_8B_CTL_C<7>
            ],	##ADDR14
            [
                    ##DSM engine control. CAP_INC_FBDN<14:0> maximum: 0000_1111
                    ##(TODO: What is the function of this?)
                    0,	##I_BIN_8B_CTL_D<0>
                    0,	##I_BIN_8B_CTL_D<1>
                    0,	##I_BIN_8B_CTL_D<2>
                    0,	##I_BIN_8B_CTL_D<3>
                    0,	##I_BIN_8B_CTL_D<4>
                    0,	##I_BIN_8B_CTL_D<5>
                    0,	##I_BIN_8B_CTL_D<6>
                    0	##I_BIN_8B_CTL_D<7>
            ],	##ADDR15
            [
                    1,	##PHI1#PHI2 buf ENABLE (DSM CLOCK)
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,	##TDC_CNT_SEL<0> ["11" ==> TDC_CNT<6> selected] (TODO: What is the function of this?)
                    1	##TDC_CNT_SEL<1> ["00" ==> TDC_CNT<3> selected] (TODO: What is the function of this?)
            ],	##ADDR16
            [
                    1,	##CK_SWC_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##CK_REF_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##CK_INJB_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##CK_INJ_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##CK_CHOP_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##CK_REF_TDC_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##TDC_RIPPLE_CNT_RET_EN ("1" ==> Core buffer ON (TEMP READOUT TO SDO))
                    0
            ],	##ADDR17
            [
                    0,	##RST_TIME_CTL_THER_OH<0> (ONE HOT CODE) (longest gvco reset time) (wide inj pulse)
                    1,	##RST_TIME_CTL_THER_OH<1> (ONE HOT CODE)
                    0,	##RST_TIME_CTL_THER_OH<2> (ONE HOT CODE)
                    0,	##RST_TIME_CTL_THER_OH<3> (ONE HOT CODE) (shortest gvco reset time) (narrow inj pulse)
                    0, 0, 0, 0
            ], ##ADDR18
            [
                    0,
                    1,	##BW_CTL_BIN<0> ==> "11": widest bandwidth (== short gvco accumulation time)
                    0,	##BW_CTL_BIN<1> ==> "00: longest gvco acc. time ==> large ti-amp gain
                    0,	##TDC_BW_CTL_BIN<0> "11" ==> fastest CK_REF_TDC
                    0,	##TDC_BW_CTL_BIN<1> (TODO: what this means?)
                    0,	##CK_REF_TDC_P_SEL	["0" ==> CK_REF_P selected || "1" ==> CK_REF_N selected] (TODO: what this means?)
                    1,	##TDC_EN ["1" TDC function enabled]
                    0
            ],	##ADDR19
            [
                    0,
                    1,	##CK_CTAT_GPIO_EN ("1" ==> CORE BUF ON)
                    1,	##CK_FIC_GPIO_EN ("1" ==> CORE BUF ON)
                    0, 0, 0, 0, 0
            ],	##ADDR20
            [
                    0,	##EN_CHOP
                    0,	##CK_CHOP_DIV_SEL ("0" ==> slow chopping clock (#2)
                    1,	##PFD_CLK_SWAP ["0" => Origin direction || "1" => direction change ]
                    0,	##CK_FIC_TO_GPIO_PREDRV_SEL ["0" => CK_PRE_CHOP || "1" => CK_POST_CHOP ]
                    0,	##CK_CTAT_TO_GPIO_PREDRV_SEL ["0" => CK_PRE_CHOP || "1" => CK_POST_CHOP ]
                    0,	##CK_CTAT_TO_TDC_RIPPLE_CNT_SEL ["0" => CK_PRE_CHOP || "1" => CK_POST_CHOP ]
                    0,	##CK_CTAT_TO_TDC_RIPPLE_CNT_POLARITY_SEL ["0" => Origin polarity || "1" => Inverted polarity]
                    0
            ],	##ADDR21
            [0,0,0,0,0,0,0,1],	##ADDR22 (CLK IO:: PUSH_ENB<7:0> ==> disable all push io)
            [1,1,1,1,1,1,1,1],	##ADDR23 (CLK IO:: PULL_ENB<7:0>: all "0" ==> strongest pull down)
            [
                    0,	##IO_ENB ("0": turn on 50-ohm matched push-pull io)
                    0,	##CKIO_SEL<0> ==> (00: main clock  || 01: CK_GVCO_CTAT)
                    0,	##CKIO_SEL<1> ==> (10: CK_GVCO_FIC || 11: VSS )
                    0, 0, 0, 0, 0
            ],	##ADDR24
            [
                    0,	##PD_OUT_DIR: toggle the polarity of the PD decision
                    0,	##SWITCH_PD_PFD: select the phase quantizer (PD or PFD) ["0" ==> PFD selected]
                    0,0,0,0,0,0
            ],	##ADDR25
            [0,0,0,0,0,0,0,0],	##ADDR26
            [0,0,0,0,0,0,0,0],	##ADDR27
            [0,0,0,0,0,0,0,0],	##ADDR28
            [0,0,0,0,0,0,0,0],	##ADDR29
            [0,0,0,0,0,0,0,0],	##ADDR30
            [0,0,0,0,0,0,0,0],	##ADDR31
            [0,0,0,0,0,0,0,0],	##ADDR32
            [0,0,0,0,0,0,0,0],	##ADDR33
            [0,0,0,0,0,0,0,0],	##ADDR34
            [0,0,0,0,0,0,0,0],	##ADDR35
            [0,0,0,0,0,0,0,0], ##ADDR36
            [0,0,0,0,0,0,0,0],	##ADDR37
            [0,0,0,0,0,0,0,0],	##ADDR38
            [0,0,0,0,0,0,0,0],	##ADDR39
            [0,0,0,0,0,0,0,0],	##ADDR40
            [0,0,0,0,0,0,0,0],	##ADDR41
            [0,0,0,0,0,0,0,0],	##ADDR42
            [0,0,0,0,0,0,0,0],	##ADDR43
            [0,0,0,0,0,0,0,0],	##ADDR44
            [0,0,0,0,0,0,0,0],	##ADDR45
            [0,0,0,0,0,0,0,0],	##ADDR46
            [0,0,0,0,0,0,0,0],	##ADDR47
            [0,0,0,0,0,0,0,0],	##ADDR48
            [0,0,0,0,0,0,0,0],	##ADDR49
            [0,0,0,0,0,0,0,0],	##ADDR50
            [0,0,0,0,0,0,0,0],	##ADDR51
            [0,0,0,0,0,0,0,0],	##ADDR52
            [0,0,0,0,0,0,0,0],	##ADDR53
            [0,0,0,0,0,0,0,0],	##ADDR54
            [
                    0,	##"1" ==> startup via CP & external clk_stup
                    0,	##"1" ==> startup via CP & external clk_stup
                    0,	##"1" ==> UP == 0 ||"0" ==> UP == 1 (when startup condition)
                    0,	##"1" ==> startup via CP & external clk_stup
                    0,	##"1" ==> DN == 0 ||"0" ==> DN == 1 (when startup condition)
                    0, 0, 0
            ],	##ADDR55
            [
                    ##GPIO5
                    1,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##S<0> (11: CK_CHOP_N, 10: CK_INJ_N)
                    0,	##S<1> (01: CK_INJB_N, 00: CK_SWC_N)
                    1,	##IO_DIR ("1" output direction) (input: CSW_DSM_CTL)
                    0
            ],	##ADDR56
            [
                    ##GPIO4
                    1,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    1,	##S<0> (11: CK_REF_P, 10: CK_INJB_P)
                    1,	##S<1> (01: CK_SWC_P, 00: VSS)
                    1,	##IO_DIR ("1" output direction) (input: PD_OFFSET_GAIN_B_DSM)
                    0
            ],	##ADDR57
            [
                    ##GPIO3
                    1,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##S<0> (11: CK_REF_N, 10:CK_INJ_P)
                    1,	##S<1> (01: FOUT_N, 00: CK_CHOP_P)
                    1,	##IO_DIR ("1" output direction) (input: ck_stup (~200kHz))
                    0
            ],	##ADDR58
            [
                    ##GPIO2
                    1,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    1,	##S<0> (11: CK_FIC_N, 10:VSS)["11" ==> CK_CTAT_N in CLAIRE01 when Chopping disabled]
                    1,	##S<1> (01: CK_REF_TDC_P, 00: CK_REF_TDC_N)
                    1,	##IO_DIR ("1" output direction)
                    0
            ],	##ADDR59
            [
                    ##GPIO1
                    1,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    1,	##S<0> (11: CK_CTAT, 10: VSS)["11" ==> CK_FIC in CLAIRE01 when Chopping disabled]
                    1,	##S<1> (01: DSM_OUT_GPIO, 00: DSM_OUT_GPIO)
                    1,	##IO_DIR ("1" output direction)
                    0
            ],	##ADDR60
            [
                    ##GPIO0 (fixed to ouput direction)
                    1,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0,	##gpio driving strength control ("1" stronger)
                    0, 0, 0, 0
            ],	##ADDR61
            [
                    ##GPIO0 (fixed to ouput direction)
                    0,	##S<0> [00: SDO, 01: O_REG<511>, 02: SPI_SCLK_TOP, 03: SPI_SDI_TP]
                    0,	##S<1>
                    0, 0, 0, 0, 0, 0
            ],	##ADDR62
            [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1	## SPI selftest bit. goes to I<1> @SPI slave in DUT
            ]	##ADDR63
        ]
    )


def init():
    #reset spi
    dut_spi.rst()
    
    addr = 0
    
    for data_packet in spi_data_array:
        
        if(addr == 16):
            print("   commit spi data change addr0 to addr 15")
            dut_spi.commit_w_addr0to15()
       
        data_index = 0
        if(len(data_packet) == 8):    
            #print("[debug] current data packet value: ", data_packet)
            #print("[debug] current addr: ", addr)
            data_set = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            print("invalid data packet in address %i !!" %(addr))
            return -1
        
        for bit in data_packet:
            #print("[debug] current bit value is: ", bit)
            #print("[debug] current data index: ", data_index)
            data_set[data_index] = bit
            #print("[debug] data set written by: ", data_set[data_index])
            data_index = data_index + 1
        
        #print("[debug] data set ", data_set)
        dut_spi.write_single(addr, data_set[0], data_set[1], data_set[2], data_set[3], data_set[4], data_set[5], data_set[6], data_set[7])    
        addr = addr + 1

        