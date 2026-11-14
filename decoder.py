#!/usr/bin/env python3
"""decoder.py -- CSCE 2303 Cortex-M0 Thumb instruction decoder."""
from dataclasses import dataclass
from typing import Optional




class DecodeFault(Exception):
    
    pass


@dataclass
class Instruction:
    op: str                          # Unique operation name (e.g., "ADDS_REG", "LDR_IMM")
    rd: Optional[int] = None         # Destination register (0..15)
    rn: Optional[int] = None         # First source / base register (0..15)
    rm: Optional[int] = None         # Second source / offset register (0..15)
    rt: Optional[int] = None         # Target register for LDR/STR (0..15)
    imm32: Optional[int] = None      # Decoded (sign- or zero-extended) immediate
    cond: Optional[int] = None       # 4-bit condition code for B<c>
    registers: Optional[int] = None  # 16-bit register bitmask for LDM/STM/PUSH/POP
    wback: bool = False              # Write-back flag for LDM/STM/PUSH/POP
    setflags: bool = False           # True if instruction updates APSR flags


def decode(hw: int, hw2: Optional[int] = None) -> Instruction:


 
                              # TODO: BL, from hw and hw2
    if (hw & 0xF800) == 0xF000 and (hw2 & 0xD000) == 0xD000:   # BL <label>
            S = (hw >> 10) & 0x1               # extract S from hw bit 10
            imm10 = (hw >> 0) & 0x3FF          # extract imm10 from hw bits 9-0
            J1 = (hw2 >> 13) & 0x1             # extract J1 from hw2 bit 13
            J2 = (hw2 >> 11) & 0x1             # extract J2 from hw2 bit 11
            imm11 = (hw2 >> 0) & 0x7FF         # extract imm11 from hw2 bits 10-0

            I1 = ~(J1 ^ S) & 0x1               # NOT(J1 EOR S)      
            I2 = ~(J2 ^ S) & 0x1               # NOT(J2 EOR S)

            # SignExtend(S:I1:I2:imm10:imm11:'0', 32)
            imm25 = imm11 << 1             # bits 11-1 (with '0' at bit 0)
            imm25 += imm10 << 12           # bits 21-12
            imm25 += I2 << 22              # bit 22
            imm25 += I1 << 23              # bit 23
            imm25 += S << 24               # bit 24 (sign bit)

            # Sign-extend from 25 bits to 32 bits
            if S == 1:
                imm32 = imm25 - (1 << 25)  # subtract 2^25 (0x2000000) if negative
            else:
                imm32 = imm25

                        # return 
    else:
            raise DecodeFault("UNDEFINED")


    if (hw & 0xF800) == 0x2000:                     # MOVS Rd, #imm8
        rd = (hw >> 8) & 7
        
        #.........
    elif (hw & 0xF800) == 0xE000:                     # B label (unconditional)
        imm11 = hw & 0x7FF
        if imm11 & 0x400:
            imm11 -= 0x800                             # sign-extend 11 bits
        imm32 = imm11 << 1                             # multiply by 2 (imm11:'0')
        
        #return Instruction(op="B", imm32=imm32)        # match the op name in your handout

    elif (hw & 0xFF00) == 0xDF00:                     # SVC #imm8
        iss.svc(hw & 0xFF)
    # TODO: the other instructions in section 4 of the handout

    # B label conditional 
    # imm8
    elif (hw & 0xF000) == 0xD000:              # B<c> <label>
        imm8 = (hw >> 0) & 0xFF                # extract imm8 from bits 7-0
        cond = (hw >> 8) & 0xF                 # extract cond from bits 11-8

        # Validate structure before creating Instruction object
        if cond == 0xE:                        # cond == '1110' -> UNDEFINED (UDF)
            raise DecodeFault("UNDEFINED")

        if cond == 0xF: 
            # instruc svc(hw & 0xFF)
            pass 
        # SignExtend(imm8:'0', 32)
        if imm8 & 0x80:     # signed
            imm32 = (imm8 - 0x100) << 1 #
        else:
            imm32 = imm8 << 1   

        # ret inst
    
    
#------------------------------------------

# BX 

    elif (hw & 0xFF80) == 0x4700:              # BX <Rm>
        rm = (hw >> 3) & 0xF                   # extract rm from bits 6-3 (4-bit register)
        m = rm

        # Validate structure before creating Instruction object
        if ((hw & 0x7) != 0 ) or m == 15:         # bits [2:0] != '000' or m == 15 -> UNPREDICTABLE
            raise DecodeFault ("UNPREDICTABLE")

        # instruc...

# BLX register 
    elif (hw & 0xFF80) == 0x4780:              # BLX <Rm>
        rm = (hw >> 3) & 0xF                   # extract rm from bits 6-3 (4-bit register)
        m = rm

        # Validate structure before creating Instruction object
        if (hw & 0x7) != 0 or m == 15:         # bits [2:0] != '000' or m == 15 -> UNPREDICTABLE
            raise DecodeFault("UNPREDICTABLE")

        #............


#_-----------_-------------------

    # NOP 
    elif (hw & 0xFFFF) == 0xBF00:              
        pass
    
#_--------------------------------
    #MVN
    elif (hw & 0xFFC0) == 0x43C0:
       # MVN Rd, Rm
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3
        
        #set flags true
        # .......

    
# Arithmetic instructins: 
#------------------------------
    #ADCS register

    # ADCS <Rdn>,<Rm>
    elif (hw & 0xFC00) == 0x4000 and (hw & 0x03C0) == 0x0140:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.....

#------------------------------
    #ADD immediate

    #ADDS <Rd>,<Rn>,#<imm3>
    elif (hw & 0xFE00) == 0x1C00:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        imm3 = (hw >> 6) & 0x7      # extract imm3 from bits 8-6
        
        
        # set flags true
        #.....


    #ADDS <Rdn>,#<imm8>
    elif (hw & 0xF800) == 0x3000:
        imm8  = (hw >> 0) & 0xFF       # extract imm8 from bits 7-0
        rdn = (hw >> 8) & 0x7          # extract rdn from bits 10-8

        # set flags true
        #.....

#-----------------------------

# 
# decoding add (sp + register) before add register to aovid 
# special cases collision. we first check the edge case if not 
# applicable we move to check the rest of cases.
    
    #ADD (SP + register)

    #ADD SP,<Rm>
    elif (hw & 0xFF87) == 0x4485:
        rm = (hw >> 3) & 0x000F        # extract rm from bits 3-6
        d = 13
        if (rm == 0b1101): 
            raise DecodeFault("UNPREDICTABLE")
        

        # set flags false
        #.........


    #ADD <Rdm>, SP, <Rdm>
    elif (hw & 0xFF78) == 0x4468: 
        rdm = (hw >> 0) & 0x7        # extract rdm from bits 2-0
        dm = (hw >> 7) & 0x1        # extract dm from bit 7
        d = (dm << 3) | rdm        # d = dm:rdm
        m = (dm << 3) | rdm        # m = dm:rdm

        # set flags false
        #.........
        
    

#__________________________
    #ADD register
    
    #ADDS <Rd>,<Rn>,<Rm>
    elif (hw & 0xF000) == 0x1000 and (hw & 0x0E00) == 0x0800:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

        # set flags true
        #.....

    #ADD <Rdn>,<Rm>
    elif (hw & 0xFF00) == 0x4400:
        rdn = (hw >> 0 ) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0xF        # extract rm from bits 3 - 6
        dn = (hw >>7) & 0x1        # extract dn from bit 7  
        d =  (dn << 3) | rdn        # d dn:rdn

        
        if d == 0b1101 or rm == 0b1101:
            #ADD (SP + register) operation
            pass

        elif d == 15 and rm == 15:
            raise DecodeFault("UNPREDICTABLE")
#_________________________

    #ADD (SP + immediate )
    #ADD <Rd>,SP,#<imm8>

    elif (hw & 0xF800) == 0xA800:
        imm8 = (hw >> 0) & 0x00FF        # extract imm8 from bits 7-0
        rd = (hw >> 8) & 0x7        # extract rd from bits 10-8
        imm32 = imm8 << 2              # imm32 = imm8 * 4

        # flags false
        #..........
        
    #ADD SP,SP,#<imm7>
    elif (hw & 0xFF80) == 0xB000:
        imm7 = (hw >> 0) & 0x007F        # extract imm7 from bits 6-0
        imm32 = imm7 << 2              # imm32 = imm7 * 4 , zero extension imm7:00,32
        d = 13
    
        # set flags false
        #........

#__________________________
    #ADR 
    #ADR <Rd>,<label>
    elif (hw & 0xF800) == 0xA000:
        imm8 = (hw >> 0) & 0x00FF        # extract imm8 from bits 7-0
        rd = (hw >> 8) & 0x0007        # extract rd from bits 10-8
        imm32 = imm8 << 2              # imm32 = imm8 * 4, zero extension imm8:00, 32

        # set flags false
        # add true
        #........


#__________________________
    #SUB immediate 

    #SUBS <Rd>,<Rn>,#<imm3>
    elif (hw & 0xFE00) == 0x1E00:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        imm3 = (hw >> 6) & 0x7      # extract imm3 from bits 8-6


        # set flags true
        #.......

    #SUBS <Rdn>,#<imm8> 
    elif (hw & 0xF800) == 0x3800:
        imm8  = (hw >> 0) & 0xFF       # extract imm8 from bits 7-0
        rdn = (hw >> 8) & 0x7          # extract rdn from bits 10-8


        # set flags true
        #.......

#__________________________
    #SUB register 

    #SUBS <Rd>,<Rn>,<Rm>
    elif (hw & 0xFE00) == 0x1A00:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        rm = (hw >> 6) & 0x7        # extract rm from bits 8-6



        # set flags true
        #.......

#__________________________
    #SUB (SP - immediate)

    #SSUB SP,SP,#<imm7>
    elif (hw& 0xFF80) == 0xB080:
        imm7 = (hw >> 0) & 0x007F        # extract imm7 from bits 6-0
        imm32 = imm7 << 2              # imm32 = imm7 * 4 , zero extension imm7:00,32
        d = 13


        # set flags false
        #.......


    #__________________________
    #SBC register 

    #SBCS <Rdn>,<Rm>

    elif (hw & 0xFFC0) == 0x4180: 
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3


        # set flags true
        #.......

    
#__________________________
    #RSB immediate 

    #RSBS <Rd>,<Rn>,#0
    elif (hw & 0xFFC0) == 0x4240:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        imm32 = 0                   # immediate = 0

        # set flags true
        #.......




#__________________________
    #MUL 

    #MULS <Rdm>,<Rn>,<Rdm>
    elif (hw & 0xFFC0) == 0x4340:
        rdm = (hw >> 0) & 0x7        # extract rdm from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
  

        # set flags true
        #.......

#__________________________

# Logic and shifts: 
#__________________________

    #AND register 

    # ANDS <Rdn>,<Rm> 
    elif (hw& 0xFFC0) == 0x4000:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3


        # set flags true
        #....... 


#__________________________
    # ORR register 

    # ORRS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4300:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......
    
#__________________________
    #EOR register
    
    #EORS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4040:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......
 
#__________________________
    #BIC register 
    
    #BICS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4380:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......
    
#__________________________
    #TST register 
    
    #TST <Rn>,<Rm>
    elif (hw & 0xFFC0) == 0x4200:
        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......
    

#__________________________
    #LSL register 
    
    #LSLS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4080:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......


#__________________________
    #LSR register 
    
    #LSRS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x40C0:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......

#__________________________
    #ASR register 
    
    #ASRS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4100:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......

#__________________________
    #ROR register 
    
    #RORS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x41C0:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......
    
#__________________________
    # Compare: 
#__________________________
    #CMP register

    #CMP <Rn>,<Rm>
    elif (hw & 0xFFC0) == 0x4280:   
        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        # set flags true
        #.......

    #CMP <Rn>,<Rm>
    elif (hw & 0xFF00) == 0x4500:
        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0xF        # extract rm from bits 3-6
        N = (hw >> 7) & 0x1        # extract N from bit 7
        n = (N << 3) | rn          # n = N:rn

        if n < 8 and rm < 8:
            raise DecodeFault("UNPREDICTABLE")

        if n == 15 and rm == 15:
            raise DecodeFault("UNPREDICTABLE")
     

    #CMP immediate 
    #CMP <Rn>,#<imm8>
    elif (hw & 0xF800) == 0x2800:
        imm8 = (hw >> 0) & 0x00FF     # extract imm8 from bits 7-0
        rn = (hw >> 8) & 0x0007       # extract rn from bits 10-8

        n = rn
        imm32 = imm8  #zero extension imm8:00, 32

    
    # CMN register

    #CMN <Rn>,<Rm>
    elif (hw & 0xFFC0) == 0x42C0:

        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 3-5

        n = rn 
        m = rm 
        
#__________________________
    # Extend and Reverse: 
#__________________________
    #SXTB 


    #SXTB <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xB240:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 3-5

        d = rd 
        m = rm 
        rotate = 0

        # set flags true
        #.......


    #SXTH 


    #SXTH <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xB200:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 3-5

        d = rd 
        m = rm 
        rotate = 0

        # set flags true
        #.......

#__________________________
    # Load and Store: 
#__________________________

    # register
    elif (hw & 0xF000) == 0x5000:
        if (hw & 0x0E00) == 0x0000:      # STR register # STR <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt
            n =rn 
            m = rm 
            
            #index = true
            # add = true 
            #wback = false

            

        elif (hw & 0x0E00) == 0x0200:    # STRH register # STRH <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt
            n =rn 
            m = rm 
            
            #index = true
            # add = true 
            #wback = false
            

        elif (hw & 0x0E00) == 0x0400:    # STRB register # STRB <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt
            n =rn 
            m = rm 
            
            #index = true
            # add = true 
            #wback = false

        elif (hw & 0x0E00) == 0x0600:    # LDRSB register # LDRSB <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt
            n =rn 
            m = rm 
            
            #index = true
            # add = true 
            #wback = false

        elif (hw & 0x0E00) == 0x0800:    # LDR register # LDR <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt
            n = rn 
            m = rm 

            #index = true
            # add = true 
            #wback = false

        elif (hw & 0x0E00) == 0x0A00:    # LDRH register # LDRH <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt 
            n = rn 
            m = rm 

            #index = true
            #add true 
            #wback false

        elif (hw & 0x0E00) == 0x0C00:    # LDRB register # LDRB <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt 
            n = rn 
            m = rm 

            #index = true
            #add true 
            #wback false

        elif (hw & 0x0E00) == 0x0E00:    # LDRSH register # LDRSH <Rt>,[<Rn>,<Rm>]
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            t = rt
            n =rn 
            m = rm 
            
            #index = true
            # add = true 
            #wback = false

        # immediate ---------------


    # STR immediate 

    # STR <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x6000:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        t = rt
        n = rn
        imm32 = imm5 << 2              # ZeroExtend(imm5:'00', 32)

        #index = true
        #add = true
        #wback = false

    
     # STR <Rt>,[SP,#<imm8>]
    elif (hw & 0xF800) == 0x9000:      
        imm8 = (hw >> 0) & 0xFF        # extract imm8 from bits 7-0
        rt = (hw >> 8) & 0x7           # extract rt from bits 10-8

        t = rt
        n = 13                         # SP
        imm32 = imm8 << 2              # ZeroExtend(imm8:'00', 32)

        #index = true
        #add = true
        #wback = false

    # LDR immediate 

    # LDR <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x6800:     
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        t = rt
        n = rn
        imm32 = imm5 << 2              # ZeroExtend(imm5:'00', 32)

        #index = true
        #add = true
        #wback = false

   
    # LDR <Rt>,[SP{,#<imm8>}]
    elif (hw & 0xF800) == 0x9800:     
        imm8 = (hw >> 0) & 0xFF        # extract imm8 from bits 7-0
        rt = (hw >> 8) & 0x7           # extract rt from bits 10-8

        t = rt
        n = 13                         # SP
        imm32 = imm8 << 2              # ZeroExtend(imm8:'00', 32)

        #index = true
        #add = true
        #wback = false


    # STRB immediate 


    # STRB <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x7000:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        t = rt
        n = rn
        imm32 = imm5                   # ZeroExtend(imm5, 32)

        #index = true
        #add = true
        #wback = false


    # LDRB immediate 


    # LDRB <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x7800:     
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        t = rt
        n = rn
        imm32 = imm5                   # ZeroExtend(imm5, 32)

        #index = true
        #add = true
        #wback = false

    # STRH immediate 


    # STRH <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x8000:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        t = rt
        n = rn
        imm32 = imm5 << 1              # ZeroExtend(imm5:'0', 32)

        #index = true
        #add = true
        #wback = false

    # LDRH immediate 


    # LDRH <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x8800:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        t = rt
        n = rn
        imm32 = imm5 << 1              # ZeroExtend(imm5:'0', 32)

        #index = true
        #add = true
        #wback = false



#--------------------------------
#  Multiple instructions: 
#--------------------------------


    # LDM =
    elif (hw & 0xF800) == 0xC800:      # LDM <Rn>{!},<registers>

        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        rn = (hw >> 8) & 0x7               # extract rn from bits 10-8

        n = rn
        registers = register_list          # '00000000':register_list
        
        # wback true (( registers >> n ) & 1 )== 0
        if registers.bit_count() < 1: 
            raise DecodeFault ("UNPREDICTABLE")


    # STM 
    elif (hw & 0xF800) == 0xC000:      # STM <Rn>!,<registers>
        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        rn = (hw >> 8) & 0x7               # extract rn from bits 10-8

        n = rn
        registers = register_list          # '00000000':register_list
        
        # wback true 

        if registers.bit_count() < 1: 
            raise DecodeFault ("UNPREDICTABLE")

    # PUSH 
    elif (hw & 0xFE00) == 0xB400:      # PUSH <registers>
        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        M = (hw >> 8) & 0x1                # extract M (LR) from bit 8

        n = 13                             # SP

        if M == 1:
            registers = 0x4000 | register_list   # include LR (bit 14)
        else:
            registers = register_list
         
        
        #unalignedAllowed is false

        if registers.bit_count() < 1: 
            raise DecodeFault ("UNPREDICTABLE")

    # POP 
    elif (hw & 0xFE00) == 0xBC00:      # POP <registers>
        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        P = (hw >> 8) & 0x1                # extract P (PC) from bit 8

        n = 13                             # SP

        if P == 1:           # P:'0000000':register_list
            registers = 0x8000 | register_list
        else:
            registers = register_list

        
        #unalignedAllowed is false

        if registers.bit_count() < 1: 
            raise DecodeFault ("UNPREDICTABLE")


    else:
        raise DecodeFault("UNDEFINED")