#!/usr/bin/env python3
"""decoder.py -- CSCE 2303 Cortex-M0 Thumb instruction decoder."""

from typing import Optional
from instruction import INSTRUCTION, Op






class DecodeFault(Exception):
    
    pass

          


def decode(hw: int, hw2: Optional[int] = None) -> INSTRUCTION:

    sp = 13
 
                              # TODO: BL, from hw and hw2
    if (hw2 != None):
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
                imm32 = imm25 - (1 << 25)  # 
            else:
                imm32 = imm25

            return INSTRUCTION(op=Op.BL, imm32=imm32, isImm=True) 

        else:
            raise DecodeFault("UNDEFINED")


     
        
        


    #-----------------------------
    # B label (unconditional)
    if (hw & 0xF800) == 0xE000:                     
        imm11 = hw & 0x7FF
        if imm11 & 0x400:
            imm11 -= 0x800                             # sign-extend 11 bits
        imm32 = imm11 << 1                             # multiply by 2 (imm11:'0')
        
        return INSTRUCTION(op=Op.B, imm32=imm32)        

     
#-------------------------------------------------------------------------------------------

    # B label conditional 
    # imm8

      # B<c> <label>
    elif (hw & 0xF000) == 0xD000:            
        imm8 = (hw >> 0) & 0xFF                # extract imm8 from bits 7-0
        cond = (hw >> 8) & 0xF                 # extract cond from bits 11-8

        
   
        if cond == 0xE:                        # cond == '1110'  UNDEFINED 
            raise DecodeFault("UNDEFINED")

        if cond == 0xF: 
            
            return INSTRUCTION(op=Op.SVC, n=imm8) # set n for service calling
             
        # SignExtend(imm8:'0', 32)
        if imm8 & 0x80:     # signed
            imm32 = (imm8 - 0x100) << 1 
        else:
            imm32 = imm8 << 1   

        return INSTRUCTION(op= Op.B, isImm=True, imm32=imm32,condition =cond )
    
    
#------------------------------------------

# BX 
    # BX <Rm>
    elif (hw & 0xFF80) == 0x4700:              
        rm = (hw >> 3) & 0xF                   # extract rm from bits 6-3 (4-bit register)
        

        
        if ((hw & 0x7) != 0 ) or rm == 15:         
            raise DecodeFault ("UNDEFINED")

        return INSTRUCTION(op = Op.BX, rs1 = rm)

# BLX register 

    # BLX <Rm>
    elif (hw & 0xFF80) == 0x4780:              
        rm = (hw >> 3) & 0xF                   # extract rm from bits 6-3 (4-bit register)
        
       
        if (hw & 0x7) != 0 or rm == 15:         
            raise DecodeFault("UNDEFINED")

        return INSTRUCTION(op= Op.BLX, rs1= rm )



#-----------------------------------
        # SVC #imm8
    elif (hw & 0xFF00) == 0xDF00:                    
        imm8 = hw & 0x00FF

        return INSTRUCTION(op = Op.SVC, n = imm8)



#_-----------_-------------------

    # NOP
    elif (hw & 0xFFFF) == 0xBF00:              
        return INSTRUCTION(op = Op.NOP)
    
#_--------------------------------
    #MOV Register


    #MVN

    # MVNS <Rd>,<Rm>

    elif (hw & 0xFFC0) == 0x43C0:
       # MVN Rd, Rm
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3
        
        
        return INSTRUCTION(op = Op.MVN, setflags= True, rd = rd, rs1=rm)
    
    # MOVS Rd, #imm8
    if (hw & 0xF800) == 0x2000:     
        imm8 = (hw >> 0) & 0xFF
        rd =   (hw >> 8) & 7

        return INSTRUCTION(op= Op.MOV, setflags = True, isImm= True, rd = rd, imm32=imm8)



    # MOV <Rd>,<Rm> (high/all registers)
    elif (hw & 0xFF00) == 0x4600:                  
        rd_low = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0xF
        D = (hw >> 7) & 0x1
        rd = (D << 3) | rd_low

        return INSTRUCTION(op=Op.MOV, rd=rd, rs1=rm, isImm=False, setflags=False)

   
    # MOVS <Rd>,<Rm> ( low registers, updates N and Z)
    elif (hw & 0xFFC0) == 0x0000:                 
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        return INSTRUCTION(op=Op.MOV, rd=rd, rs1=rm, isImm=False, setflags=True)
    
# Arithmetic instructins: 
#------------------------------
    #ADCS register

    # ADCS <Rdn>,<Rm>
    elif (hw & 0xFC00) == 0x4000 and (hw & 0x03C0) == 0x0140:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op=Op.ADC, setflags=True, rd=rdn, rs1=rdn, rs2=rm)

#------------------------------
    #ADD immediate

    #ADDS <Rd>,<Rn>,#<imm3>
    elif (hw & 0xFE00) == 0x1C00:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        imm3 = (hw >> 6) & 0x7      # extract imm3 from bits 8-6
        
        
        return INSTRUCTION(op= Op.ADD, setflags=True,isImm= True, isImm3= True,   rd = rd, rs1= rn, imm32 = imm3)


    #ADDS <Rdn>,#<imm8>
    elif (hw & 0xF800) == 0x3000:
        imm8  = (hw >> 0) & 0xFF       # extract imm8 from bits 7-0
        rdn = (hw >> 8) & 0x7          # extract rdn from bits 10-8

        return INSTRUCTION(op= Op.ADD, setflags=True, isImm= True, rd = rdn, rs1= rdn, imm32= imm8 )

#-----------------------------

# 
# decoding add (sp + register) before add register to aovid 
# special cases collision. we first check the edge case if not 
# applicable we move to check the rest of cases.
    
    #ADD (SP + register)

    #ADD SP,<Rm>
    elif (hw & 0xFF87) == 0x4485:
        rm = (hw >> 3) & 0x000F        # extract rm from bits 3-6
        
        if (rm == 0b1101): # 01000100 1 1101 101
            rdm = 0b101
            dm = 1
            d = (dm << 3) | rdm        # d = dm:rdm
            
            return INSTRUCTION(op=Op.ADD, rd=d, rs1=sp, rs2=d)
        

        return INSTRUCTION(op= Op.ADD,rd = sp, rs1  =sp, rs2= rm)


    #ADD <Rdm>, SP, <Rdm>
    elif (hw & 0xFF78) == 0x4468: 
        rdm = (hw >> 0) & 0x7        # extract rdm from bits 2-0
        dm = (hw >> 7) & 0x1        # extract dm from bit 7
        d = (dm << 3) | rdm        # d = dm:rdm
        

        return INSTRUCTION(op=Op.ADD, rd=d, rs1=sp, rs2=d)
        
    

#__________________________
    #ADD register
    
    #ADDS <Rd>,<Rn>,<Rm>
    elif (hw & 0xF000) == 0x1000 and (hw & 0x0E00) == 0x0800:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

        return INSTRUCTION(op =Op.ADD, setflags= True, rd = rd, rs1 = rn, rs2= rm)

    #ADD <Rdn>,<Rm>
    elif (hw & 0xFF00) == 0x4400:
        rdn = (hw >> 0 ) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0xF        # extract rm from bits 3 - 6
        dn = (hw >>7) & 0x1        # extract dn from bit 7  
        d =  (dn << 3) | rdn        # d dn:rdn

        
        if rm == 0b1101: # ADD <Rdm>, SP, <Rdm>
            return INSTRUCTION(op=Op.ADD, rd=d, rs1=13, rs2=d)
           
        if d == 0b1101:                 # ADD SP, <Rm> 
            return INSTRUCTION(op=Op.ADD, rd=sp, rs1=sp, rs2=rm)


        if d == 15 and rm == 15:
            raise DecodeFault("UNDEFINED")


        return INSTRUCTION(op=Op.ADD, rd=d, rs1=d, rs2=rm, isImm=False, setflags=False)
#_________________________

    #ADD (SP + immediate )
    #ADD <Rd>,SP,#<imm8>

    elif (hw & 0xF800) == 0xA800:
        imm8 = (hw >> 0) & 0x00FF        # extract imm8 from bits 7-0
        rd = (hw >> 8) & 0x7        # extract rd from bits 10-8
        imm32 = imm8 << 2              # imm32 = imm8 * 4

        
        return INSTRUCTION(op=Op.ADD, setflags= False, rd = rd, rs1= sp, isImm= True, imm32 = imm32)
        
    #ADD SP,SP,#<imm7>
    elif (hw & 0xFF80) == 0xB000:
        imm7 = (hw >> 0) & 0x007F        # extract imm7 from bits 6-0
        imm32 = imm7 << 2              # imm32 = imm7 * 4 , zero extension imm7:00,32
        
    
        return INSTRUCTION(op=Op.ADD, setflags= False, rd= sp, rs1 = sp ,isImm= True, imm32= imm32)

#__________________________
    #ADR 
    #ADR <Rd>,<label>
    elif (hw & 0xF800) == 0xA000:
        imm8 = (hw >> 0) & 0x00FF        # extract imm8 from bits 7-0
        rd = (hw >> 8) & 0x0007        # extract rd from bits 10-8
        imm32 = imm8 << 2              # imm32 = imm8 * 4, zero extension imm8:00, 32

        return INSTRUCTION(op= Op.ADR,isImm=True, imm32= imm32, rd = rd )


#__________________________
    #SUB immediate 

    #SUBS <Rd>,<Rn>,#<imm3>
    elif (hw & 0xFE00) == 0x1E00:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        imm3 = (hw >> 6) & 0x7      # extract imm3 from bits 8-6


        return INSTRUCTION(op = Op.SUB, setflags = True, isImm=True, isImm3 = True, rd = rd, rs1 = rn, imm32 = imm3)


    #SUBS <Rdn>,#<imm8> 
    elif (hw & 0xF800) == 0x3800:
        imm8  = (hw >> 0) & 0xFF       # extract imm8 from bits 7-0
        rdn = (hw >> 8) & 0x7          # extract rdn from bits 10-8


        return INSTRUCTION(op = Op.SUB, setflags = True, isImm=True, rd = rdn, rs1 = rdn, imm32 = imm8)

#__________________________
    #SUB register 

    #SUBS <Rd>,<Rn>,<Rm>
    elif (hw & 0xFE00) == 0x1A00:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        rm = (hw >> 6) & 0x7        # extract rm from bits 8-6



        return INSTRUCTION(op = Op.SUB, setflags = True,  rd = rd, rs1 = rn, rs2= rm)

#__________________________
    #SUB (SP - immediate)

    #SSUB SP,SP,#<imm7>
    elif (hw& 0xFF80) == 0xB080:
        imm7 = (hw >> 0) & 0x007F        # extract imm7 from bits 6-0
        imm32 = imm7 << 2              # imm32 = imm7 * 4 , zero extension imm7:00,32
        


        return INSTRUCTION(op = Op.SUB, setflags = False, isImm=True, rd = sp, rs1 = sp, imm32 = imm32)


    #__________________________
    #SBC register 

    #SBCS <Rdn>,<Rm>

    elif (hw & 0xFFC0) == 0x4180: 
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3


        return INSTRUCTION(op = Op.SBC, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)

    
#__________________________
    #RSB immediate 

    #RSBS <Rd>,<Rn>,#0
    elif (hw & 0xFFC0) == 0x4240:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
        imm32 = 0                   # immediate = 0

      

        return INSTRUCTION(op=Op.RSB, setflags=True, isImm=True, rd=rd, rs1=rn, imm32=0)




#__________________________
    #MUL 

    #MULS <Rdm>,<Rn>,<Rdm>
    elif (hw & 0xFFC0) == 0x4340:
        rdm = (hw >> 0) & 0x7        # extract rdm from bits 2-0
        rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
  

        return INSTRUCTION(op = Op.MUL, setflags = True,  rd = rdm, rs1 = rn, rs2 = rdm)





#__________________________

# Logic and shifts: 
#__________________________





    #AND register 

    # ANDS <Rdn>,<Rm> 
    elif (hw& 0xFFC0) == 0x4000:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3


        return INSTRUCTION(op = Op.AND, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)


#__________________________
    # ORR register 

    # ORRS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4300:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.ORR, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)
    
#__________________________
    #EOR register
    
    #EORS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4040:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.EOR, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)
 
#__________________________
    #BIC register 
    
    #BICS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4380:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.BIC, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)
    
#__________________________
    #TST register 
    
    #TST <Rn>,<Rm>
    elif (hw & 0xFFC0) == 0x4200:
        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.TST, setflags = True, rs1 = rn, rs2 = rm)
    

#__________________________
    #LSL register 
    
    #LSLS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4080:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.LSL, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)  


    #LSL immediate


     # LSLS <Rd>,<Rm>,#<imm5> (or MOVS <Rd>,<Rm>)
    elif (hw & 0xF800) == 0x0000:                 
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        imm5 = (hw >> 6) & 0x1F
        if imm5 == 0:                              # ARMv6-M: imm5 == 0 encodes MOVS Rd, Rm (C unchanged)
            return INSTRUCTION(op=Op.MOV, rd=rd, rs1=rm, isImm=False, setflags=True)
        return INSTRUCTION(op=Op.LSL, rd=rd, rs1=rm, imm32=imm5, isImm=True, setflags=True)

#__________________________
    #LSR register 
    
    #LSRS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x40C0:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.LSR, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)
        

    #LSR immediate

     # LSRS <Rd>,<Rm>,#<imm5>
    elif (hw & 0xF800) == 0x0800:                 
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        imm5 = (hw >> 6) & 0x1F
        
        if imm5 == 0:                              # 0 encodes a shift of 32
            imm5 = 32
        return INSTRUCTION(op=Op.LSR, rd=rd, rs1=rm, imm32=imm5, isImm=True, setflags=True)
#__________________________
    #ASR register 
    
    #ASRS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x4100:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.ASR, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)


    #ASR immediate 
     # ASRS <Rd>,<Rm>,#<imm5>
    elif (hw & 0xF800) == 0x1000:                 
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        imm5 = (hw >> 6) & 0x1F

        if imm5 == 0:                              # 0 encodes a shift of 32
            imm5 = 32
        return INSTRUCTION(op=Op.ASR, rd=rd, rs1=rm, imm32=imm5, isImm=True, setflags=True)


#__________________________
    #ROR register 
    
    #RORS <Rdn>,<Rm>
    elif (hw & 0xFFC0) == 0x41C0:
        rdn = (hw >> 0) & 0x7        # extract rdn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.ROR, setflags = True,  rd = rdn, rs1 = rdn, rs2 = rm)
    
#__________________________
    # Compare: 
#__________________________
    #CMP register

    #CMP <Rn>,<Rm>
    elif (hw & 0xFFC0) == 0x4280:   
        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 5-3

        return INSTRUCTION(op = Op.CMP, setflags = True,   rs1 = rn, rs2 = rm)

    #CMP <Rn>,<Rm>
    elif (hw & 0xFF00) == 0x4500:
        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0xF        # extract rm from bits 3-6
        N = (hw >> 7) & 0x1        # extract N from bit 7
        n = (N << 3) | rn          # n = N:rn

        if n < 8 and rm < 8:
            raise DecodeFault("UNDEFINED")

        if n == 15 and rm == 15:
            raise DecodeFault("UNDEFINED")
     
        return INSTRUCTION(op = Op.CMP, setflags = True, rs1 = n, rs2 = rm)



    #CMP immediate 
    #CMP <Rn>,#<imm8>
    elif (hw & 0xF800) == 0x2800:
        imm8 = (hw >> 0) & 0x00FF     # extract imm8 from bits 7-0
        rn = (hw >> 8) & 0x0007       # extract rn from bits 10-8

        return INSTRUCTION(op = Op.CMP, setflags = True, isImm= True, rs1 = rn, imm32=imm8)
        

        
    # CMN register

    #CMN <Rn>,<Rm>
    elif (hw & 0xFFC0) == 0x42C0:

        rn = (hw >> 0) & 0x7        # extract rn from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 3-5

   
        
        return INSTRUCTION(op = Op.CMN, setflags = True,  rs1 = rn, rs2 = rm)
#__________________________
    # Extend and Reverse: 
#__________________________
    #SXTB 


    #SXTB <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xB240:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 3-5

        

        return INSTRUCTION(op = Op.SXTB,  rd = rd, rs1 = rm)


    #SXTH 


    #SXTH <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xB200:
        rd = (hw >> 0) & 0x7        # extract rd from bits 2-0
        rm = (hw >> 3) & 0x7        # extract rm from bits 3-5

        

        return INSTRUCTION(op = Op.SXTH,  rd = rd, rs1 = rm)

    
     # UXTH <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xB280:                  
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        return INSTRUCTION(op=Op.UXTH, rd=rd, rs1=rm, setflags=False)

    # UXTB <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xB2C0:                  
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        return INSTRUCTION(op=Op.UXTB, rd=rd, rs1=rm, setflags=False)


    # REV <Rd>,<Rm>
    elif (hw & 0xFFC0) == 0xBA00:                  
        rd = (hw >> 0) & 0x7
        rm = (hw >> 3) & 0x7
        return INSTRUCTION(op=Op.REV, rd=rd, rs1=rm, setflags=False)

#__________________________
    # Load and Store: 
#__________________________

    # register


    elif (hw & 0xF000) == 0x5000:

        # STR register # STR <Rt>,[<Rn>,<Rm>]
        if (hw & 0x0E00) == 0x0000:      
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

             
            
            return INSTRUCTION(op=Op.STR, rt=rt, rs1=rn, rs2=rm)

        
        # STRH register # STRH <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0200:    
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            
            
            return INSTRUCTION(op=Op.STRH, rt=rt, rs1=rn, rs2=rm)
            
        # STRB register # STRB <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0400:    
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            return INSTRUCTION(op=Op.STRB, rt=rt, rs1=rn, rs2=rm)


        # LDRSB register # LDRSB <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0600:    
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            return INSTRUCTION(op=Op.LDRSB, rt=rt, rs1=rn, rs2=rm)


             # LDR register # LDR <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0800:   
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            

            return INSTRUCTION(op=Op.LDR, rt=rt, rs1=rn, rs2=rm)

            # LDRH register # LDRH <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0A00:    
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            

            return INSTRUCTION(op=Op.LDRH, rt=rt, rs1=rn, rs2=rm)


            # LDRB register # LDRB <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0C00:    
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            return INSTRUCTION(op=Op.LDRB, rt=rt, rs1=rn, rs2=rm)


            # LDRSH register # LDRSH <Rt>,[<Rn>,<Rm>]
        elif (hw & 0x0E00) == 0x0E00:    
            rt = (hw >> 0) & 0x7        # extract rt from bits 2-0
            rn = (hw >> 3) & 0x7        # extract rn from bits 5-3
            rm = (hw >> 6) & 0x7        # extract rm from bits 8-6

            
            
            return INSTRUCTION(op=Op.LDRSH, rt=rt, rs1=rn, rs2=rm)


    #__________________________
    # Load and Store:  # immediate ---------------
#__________________________
   


    # STR immediate 

    # STR <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x6000:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        
        imm32 = imm5 << 2              # ZeroExtend(imm5:'00', 32)

        return INSTRUCTION(op=Op.STR, rt=rt, rs1=rn, imm32=imm32, isImm=True)

    
     # STR <Rt>,[SP,#<imm8>]
    elif (hw & 0xF800) == 0x9000:      
        imm8 = (hw >> 0) & 0xFF        # extract imm8 from bits 7-0
        rt = (hw >> 8) & 0x7           # extract rt from bits 10-8

                               # SP
        imm32 = imm8 << 2              # ZeroExtend(imm8:'00', 32)
        
        return INSTRUCTION(op=Op.STR, rt=rt, rs1=sp, imm32=imm32, isImm=True)

    # LDR immediate 

    # LDR <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x6800:     
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        
        imm32 = imm5 << 2              # ZeroExtend(imm5:'00', 32)

        return INSTRUCTION(op=Op.LDR, rt=rt, rs1=rn, imm32=imm32, isImm=True)

   
    # LDR <Rt>,[SP{,#<imm8>}]
    elif (hw & 0xF800) == 0x9800:     
        imm8 = (hw >> 0) & 0xFF        # extract imm8 from bits 7-0
        rt = (hw >> 8) & 0x7           # extract rt from bits 10-8

     
        imm32 = imm8 << 2              # ZeroExtend(imm8:'00', 32)

        return INSTRUCTION(op=Op.LDR, rt=rt, rs1=sp, imm32=imm32, isImm=True)



    # LDR <Rt>,[PC,#<imm8>] (literal pool load)
    elif (hw & 0xF800) == 0x4800:                  
        imm8 = (hw >> 0) & 0xFF
        rt = (hw >> 8) & 0x7
        imm32 = imm8 << 2

        return INSTRUCTION(op=Op.LDR, rt=rt, rs1=15, imm32= imm32, isImm=True, setflags=False)

    # STRB immediate 


    # STRB <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x7000:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        

        return INSTRUCTION(op=Op.STRB, rt=rt, rs1=rn, imm32=imm5, isImm=True)


    # LDRB immediate 


    # LDRB <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x7800:     
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        return INSTRUCTION(op=Op.LDRB, rt=rt, rs1=rn, imm32=imm5, isImm=True)

    # STRH immediate 


    # STRH <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x8000:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

       
        imm32 = imm5 << 1              # ZeroExtend(imm5:'0', 32)

        return INSTRUCTION(op=Op.STRH, rt=rt, rs1=rn, imm32=imm32, isImm=True)

    # LDRH immediate 


    # LDRH <Rt>,[<Rn>{,#<imm5>}]
    elif (hw & 0xF800) == 0x8800:      
        rt = (hw >> 0) & 0x7           # extract rt from bits 2-0
        rn = (hw >> 3) & 0x7           # extract rn from bits 5-3
        imm5 = (hw >> 6) & 0x1F        # extract imm5 from bits 10-6

        
        imm32 = imm5 << 1              # ZeroExtend(imm5:'0', 32)

        return INSTRUCTION(op=Op.LDRH, rt=rt, rs1=rn, imm32=imm32, isImm=True)


#--------------------------------
#  Multiple instructions: 
#--------------------------------


    # LDM 
     # LDM <Rn>{!},<registers>

    elif (hw & 0xF800) == 0xC800:     

        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        rn = (hw >> 8) & 0x7               # extract rn from bits 10-8

        
        registers = register_list          # '00000000':register_list
        wback = (( registers >> rn ) & 1 )== 0


        if  registers == 0: 
            raise DecodeFault ("UNDEFINED")

        return INSTRUCTION(op=Op.LDM, rs1=rn, registers=registers, write_back=wback)

    # STM 
    elif (hw & 0xF800) == 0xC000:      # STM <Rn>!,<registers>
        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        rn = (hw >> 8) & 0x7               # extract rn from bits 10-8

        
        registers = register_list          # '00000000':register_list
        
        # wback true 

        if registers == 0: 
            raise DecodeFault ("UNDEFINED")

        return INSTRUCTION(op=Op.STM, rs1=rn, registers=registers, write_back=True)

    # PUSH 
    elif (hw & 0xFE00) == 0xB400:      # PUSH <registers>
        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        M = (hw >> 8) & 0x1                # extract M (LR) from bit 8


        if M == 1:
            registers = 0x4000 | register_list   # include LR (bit 14)
        else:
            registers = register_list
         
        
        

        if registers == 0:
            raise DecodeFault("UNDEFINED")

        return INSTRUCTION(op=Op.PUSH, rs1=sp, registers=registers, write_back=True)

    # POP
    elif (hw & 0xFE00) == 0xBC00:      # POP <registers>
        register_list = (hw >> 0) & 0xFF   # extract register_list from bits 7-0
        P = (hw >> 8) & 0x1                # extract P (PC) from bit 8

        

        if P == 1:           # P:'0000000':register_list
            registers = 0x8000 | register_list
        else:
            registers = register_list

        
        #unalignedAllowed is false

        if registers == 0: 
            raise DecodeFault ("UNDEFINED")

        return INSTRUCTION(op=Op.POP, rs1=13, registers=registers, write_back=True)

    else:
        raise DecodeFault("UNDEFINED")


COND_NAMES = ("eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc", "hi", "ls", "ge", "lt", "gt", "le")

def register(r: int) -> str:
    if r == 13:
        return "sp"
    if r == 14:
        return "lr"
    if r == 15:
        return "pc"
    return f"r{r}"


def register_list(mask: int) -> str:
    regs = [register(i) for i in range(16) if (mask >> i) & 1]
    return "{" + ", ".join(regs) + "}"

def disasm(instr: INSTRUCTION, pc: int) -> str:
    op = instr.op
    s = "s" if instr.setflags else "" # adding suffix s for instruction that update flags 
    name = op.value.lower()

    # Moves
    if op == Op.MOV:
        if instr.isImm:
            return f"mov{s}\t{register(instr.rd)}, #{instr.imm32}"
 

        if not instr.setflags and instr.rd == instr.rs1 == 8:
            return "nop"
        return f"mov{s}\t{register(instr.rd)}, {register(instr.rs1)}"


    if op == Op.MVN:
        return f"mvns\t{register(instr.rd)}, {register(instr.rs1)}"

    # Shifts & Rotates
    if op in (Op.LSL, Op.LSR, Op.ASR, Op.ROR):
        if instr.isImm:
            return f"{name}{s}\t{register(instr.rd)}, {register(instr.rs1)}, #{instr.imm32}"
        return f"{name}{s}\t{register(instr.rd)}, {register(instr.rs2)}"

    # Add & Subtract
    # Add & Subtract
    if op in (Op.ADD, Op.SUB):
        if instr.isImm:
            # 2-operand form:
            if instr.rd == instr.rs1 and not instr.isImm3:
                return f"{name}{s}\t{register(instr.rd)}, #{instr.imm32}"
            # 3-operand form:
            return f"{name}{s}\t{register(instr.rd)}, {register(instr.rs1)}, #{instr.imm32}"

        if instr.setflags:   # ADDS/SUBS <Rd>,<Rn>,<Rm>, always 3 parameters
            return f"{name}{s}\t{register(instr.rd)}, {register(instr.rs1)}, {register(instr.rs2)}"
        # 2-operand register: ADD <Rdn>,<Rm> ( rdn is dest and first operand )or  ADD <Rdm>,SP,<Rdm> (rdm is destinatino and second operand)
        if instr.rd == instr.rs1:
            other = instr.rs2
        else:
            other = instr.rs1
        return f"{name}{s}\t{register(instr.rd)}, {register(other)}"

    # Other Arithmetic & Logic
    if op in (Op.ADC, Op.SBC, Op.AND, Op.ORR, Op.EOR, Op.BIC):
        return f"{name}s\t{register(instr.rd)}, {register(instr.rs2)}"

    if op == Op.RSB:
        return f"negs\t{register(instr.rd)}, {register(instr.rs1)}"

    if op == Op.MUL:
        return f"muls\t{register(instr.rd)}, {register(instr.rs1)}"

    # Compare & Test
    if op in (Op.CMP, Op.CMN, Op.TST):
        if instr.isImm:
            return f"{name}\t{register(instr.rs1)}, #{instr.imm32}"
        return f"{name}\t{register(instr.rs1)}, {register(instr.rs2)}"

    # Extend & Reverse
    if op in (Op.SXTB, Op.SXTH, Op.UXTB, Op.UXTH, Op.REV):
        return f"{name}\t{register(instr.rd)}, {register(instr.rs1)}"

    # PC-relative ADR
    if op == Op.ADR:
        target = ((pc + 4) & ~3) + instr.imm32
        return f"add\t{register(instr.rd)}, pc, #{instr.imm32}\t@ (adr {register(instr.rd)}, {target:x})" # ADD{<q>} <Rd>, PC, #<const>
    # Loads & Stores
    if op in (Op.LDR, Op.LDRB, Op.LDRH, Op.LDRSB, Op.LDRSH, Op.STR, Op.STRB, Op.STRH):
        if instr.isImm:
            if instr.rs1 == 15:
                target = ((pc + 4) & ~3) + instr.imm32
                return f"ldr\t{register(instr.rt)}, [pc, #{instr.imm32}]\t@ ({target:x})"
            
            return f"{name}\t{register(instr.rt)}, [{register(instr.rs1)}, #{instr.imm32}]"
        return f"{name}\t{register(instr.rt)}, [{register(instr.rs1)}, {register(instr.rs2)}]"

    # Multiple Register Transfers
    if op in (Op.PUSH, Op.POP):
        return f"{name}\t{register_list(instr.registers)}"

    if op == Op.LDM:
        wb = "!" if instr.write_back else ""
        return f"ldmia\t{register(instr.rs1)}{wb}, {register_list(instr.registers)}"

    if op == Op.STM:
        return f"stmia\t{register(instr.rs1)}!, {register_list(instr.registers)}"

    # Branches & System
    if op == Op.B:
        target = (pc + 4) + instr.imm32
        if instr.condition is not None:
            return f"b{COND_NAMES[instr.condition]}.n\t{target:x}"
        return f"b.n\t{target:x}"

    if op == Op.BL:
        target = (pc + 4) + instr.imm32
        return f"bl\t{target:x}"

    if op in (Op.BX, Op.BLX):
        return f"{name}\t{register(instr.rs1)}"

    if op == Op.SVC:
        return f"svc\t{instr.n}"

    if op == Op.NOP:
        return "nop"

    return f"<unknown {op}>"

