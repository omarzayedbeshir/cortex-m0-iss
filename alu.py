from __future__ import annotations
from instruction import INSTRUCTION, Op



#-------------------------------------------------------------------------#
      #This ALU is done by @BawahabYousefOmar For CSCE Assymbly course in AUC 
      #  
      #Assume CPU registers always contain unsigned 32-bit values 
      #              
      #Sign depends on the operation, and each instruction updates only 
      #the flags when specified by ARM   
      #
      #immediate LSR and ASR encode a shift of 32 using a zero immediate 
      #field.Decoder should give 32, not zero
      #
      #The offset must  be sign-extended and scaled appropriately by 
      #the decoder.                                                             |
      #-------------------------------------------------------------------------#   
    
#temporary class exceptoin

class AlUExceptoin(Exception):
        pass

     


def ADD( instr: INSTRUCTION, cpu: CPU, nxt):
     #ADDS <Rd>,<rs1>,#<imm3>
     #ADDS <Rds>,#<imm8>
     #ADD SP,<rs2>
     #ADD <Rdm>, SP, <Rdm>
     #ADDS <Rd>,<rs1>,<rs2>
     #ADD <Rds>,<rs2>
     #ADD <Rd>,SP,#<imm8>
     #ADD SP,SP,#<imm7>
     if(instr.rs1 != 15 ):
         input_1 = mask32(cpu.r[instr.rs1])  
     else:#the rs1 is PC
         input_1 = mask32(cpu.r[instr.rs1] + 4)
     #check if second register is just an imm32
     if(instr.isImm): 
         input_2 = mask32(instr.imm32)
     else:
         if(instr.rs2 != 15 ):
             input_2 = mask32(cpu.r[instr.rs2])  
         else:#the rs2 is PC
             input_2 = mask32(cpu.r[instr.rs2] + 4) 
      
     #count sum
     res = (input_1 + input_2)
     
     if(instr.rd!=15):#Not PC, write to destination
        value = mask32(res)
        if instr.rd == 13:
            value &= 0xFFFFFFFC
        cpu.r[instr.rd] = value
     else:#nxt = PC + 4 + operand, bit_0 clear
         nxt = mask32((res) & 0xFFFF_FFFE) 
         instr.branch_taken = True;          #branch taken
     
     #if flags should changed in case ADDS
     if(instr.setflags):
        handleFlags_ADD(cpu, input_1, input_2)
     
     return nxt
def ADC( instr: INSTRUCTION, cpu: CPU):
     # ADCS <Rds>,<rs2>
     input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
     #rs2
     input_2 = mask32(cpu.r[instr.rs2])
      
     #count sum
     res = input_1 + input_2 + cpu.C # rs1, rs2, carry
     
     cpu.r[instr.rd] = mask32(res)
     #if flags should changed in case ADDS
     if(instr.setflags):
        handleFlags_ADD(cpu, input_1, input_2, carry_in=int(cpu.C)) 
     
     return 
def SUB( instr: INSTRUCTION, cpu: CPU):
        #SUBS <Rd>,<rs1>,#<imm3>
        #SUBS <Rds>,#<imm8>
        #SUBS <Rd>,<rs1>,<rs2> 
        #SUB SP,SP,#<imm7>
        input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
        #check if second register is just an imm32
        if(instr.isImm): 
            input_2 = mask32(instr.imm32)
        else:
            input_2 = mask32(cpu.r[instr.rs2])
            
        diff = input_1 - input_2    #get difference
        cpu.r[instr.rd] = mask32(diff)
        
        if(instr.setflags):
            handleFlags_SUB(cpu, input_1, input_2)
            
        return 
 #SBCS r0, r1     no immdiate   
#SBCS r0, r1     no immdiate 
def SBC( instr: INSTRUCTION, cpu: CPU):
        #SBCS <Rds>,<rs2>
        input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
        #not immdiate
        input_2 = mask32(cpu.r[instr.rs2])
           
        borrow = 1 - int(cpu.C)     #if C_pre is 0, means borrow occurs, so considerate 
        diff = input_1 - input_2  - borrow  #get difference
        cpu.r[instr.rd] = mask32(diff)
        
        if(instr.setflags):
            handleFlags_SUB(cpu, input_1, input_2, borrow )
            
        return     
 
 #RSBS R0, R1, #0  no immdiate other than 0 supported, always set flags
def RSB(instr: INSTRUCTION, cpu: CPU):
     #RSBS <Rd>,<rs1>,#0
     input_1 = cpu.r[instr.rs1]  
     res = 0 - input_1         #negate
     
     cpu.r[instr.rd] = mask32(res)  
     
     #update flag always
     handleFlags_SUB(cpu, 0, input_1)
         
     return 
 #            
#CMP R0, R1
def CMP( instr: INSTRUCTION, cpu: CPU):
        #CMP <rs1>,<rs2>
        #CMP <rs1>,#<imm8>
        input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
        #check if second register is just an imm32
        if(instr.isImm): 
            input_2 = mask32(instr.imm32)
        else:
            input_2 = mask32(cpu.r[instr.rs2])
        #Update flags     
        handleFlags_SUB(cpu, input_1, input_2)
            
        return 
#CMN R0, R1, no immdiate expected
def CMN( instr: INSTRUCTION, cpu: CPU):
     #CMN <rs1>,<rs2>
     input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
     #check if second register is just an imm32
     input_2 = mask32(cpu.r[instr.rs2])
     #update flag always
     handleFlags_ADD(cpu, input_1, input_2)
     
     return   
#MULS r0, r1
def MUL(instr: INSTRUCTION, cpu: CPU):
    #MULS <Rdm>,<rs1>,<Rdm>
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    
    res = input_1 * input_2 
    res = mask32(res)
    cpu.r[instr.rd] = res
    
    #in-palce flag update
    if((res & 0x8000_0000)):#check negative flag
        cpu.N = True
    else:
         cpu.N = False   
    if(res == 0): #check zero
        cpu.Z = True 
    else: 
        cpu.Z = False
        

    return
def MOV(instr: INSTRUCTION, cpu: CPU, nxt):
    # MOVS Rd, #imm8
    # MOV <Rd>,<rs2> (high/all registers)
    # MOVS <Rd>,<rs2> ( low registers, updates N and Z)
    if(instr.isImm):
        val = instr.imm32
    else:
        if(instr.rs1!=15):#NOT CP
          val = cpu.r[instr.rs1]    
        else:
          val = cpu.r[instr.rs1]+4
     
    res = mask32(val)
    
    if(instr.rd != 15):#if rd is not PC, store it in rd
       cpu.r[instr.rd] = res & 0xFFFFFFFC if instr.rd == 13 else res
    else:#if rd is PC
        nxt = mask32((res) & 0xFFFF_FFFE)      #update nxt with bit_0 cleared  
        instr.branch_taken = True              #branch taken
    
    
    if(instr.setflags): #low registers, updates N and Z
        cpu.N = bool(res & 0x8000_0000)
        cpu.Z = bool(res == 0)
    
    return nxt

def ADR(instr: INSTRUCTION, cpu: CPU):
    #ADR <Rd>,<label>
    val = ((cpu.r[15] + 4) & 0xFFFF_FFFC) + instr.imm32 # rd = (PC + 4)& 1100 + imm32
    cpu.r[instr.rd] = mask32(val)
    
    return 
#--------------------------- BITWISE ---------------------------------#
#ANDS r0, r1    no immdiate expected
def AND(instr: INSTRUCTION, cpu: CPU):
    # ANDS <Rds>,<rs2>
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 & input_2
    cpu.r[instr.rd] = mask32(res) 
    
    #in-palce flag update
    if((res & 0x8000_0000)):#check negative flag
        cpu.N = True
    else:
         cpu.N = False   
    if(res == 0): #check zero
        cpu.Z = True 
    else: 
        cpu.Z = False
    
    return

def ORR(instr: INSTRUCTION, cpu: CPU):
    # ORRS <Rds>,<rs2>
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 | input_2
    cpu.r[instr.rd] = mask32(res)
    
    #in-palce flag update
    if((res & 0x8000_0000)):#check negative flag
        cpu.N = True
    else:
         cpu.N = False   
    if(res == 0): #check zero
        cpu.Z = True 
    else: 
        cpu.Z = False
    
    return

def EOR(instr: INSTRUCTION, cpu: CPU):
     #EORS <Rds>,<rs2>
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 ^ input_2
    cpu.r[instr.rd] = mask32(res)
    
    #in-palce flag update
    cpu.N = bool(res & 0x8000_0000)
    cpu.Z = bool(res == 0)
    
    return
#bit Clear : BICS r0, r1
def BIC(instr: INSTRUCTION, cpu: CPU):
     #BICS <Rds>,<rs2>
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 &(~input_2)   # r0 & (not r1)
    cpu.r[instr.rd] = mask32(res)
    
    #in-palce flag update
    cpu.N = bool(res & 0x8000_0000)
    cpu.Z = bool(res == 0)
    
    return
#TST r0, r1, like AND, no store 
def TST(instr: INSTRUCTION, cpu: CPU):
    #TST <rs1>,<rs2>
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 & input_2
    res = mask32(res)
    
    #in-palce flag update
    cpu.N = bool(res & 0x8000_0000)
    cpu.Z = bool(res == 0)
    
    return
 
def MVN(instr: INSTRUCTION, cpu: CPU): #BITWISE NOT
    #no immediate expected
    # MVNS <Rd>,<rs2>
    val = cpu.r[instr.rs1]
        
    res = mask32(~val)
    
    cpu.r[instr.rd] = res
    
    if(instr.setflags):
        cpu.N = bool(res & 0x8000_0000)
        cpu.Z = bool(res == 0)
        


#----------------------------- LOGICAL -----------------------------

#LSLS r0, r1, #2 or LSLS r0, r1
def LSL(instr: INSTRUCTION, cpu: CPU):
    #LSLS <Rds>,<rs2>
    ## LSLS <Rd>,<rs2>,#<imm5>
    input_1 = cpu.r[instr.rs1]
    
    if(instr.isImm):
        shiftby = instr.imm32 
    else:
        shiftby = (cpu.r[instr.rs2] & 0x0FF)    #lower 8 bits
    
    res = (input_1 << shiftby)
    
    cpu.r[instr.rd]  = mask32(res)
    
    if(instr.setflags):
        handleFlags_LS(cpu, res, input_1, shiftby)
   
    return 

def LSR(instr: INSTRUCTION, cpu: CPU):
    #LSRS <Rds>,<rs2>
    # LSRS <Rd>,<rs2>,#<imm5>
    input_1 = cpu.r[instr.rs1]
    
    if(instr.isImm):
        shiftby = instr.imm32         #imm32 have the decoded shift amount like LSR r0, r1, #32
    else:
        shiftby = (cpu.r[instr.rs2] & 0x0FF)    #lower 8 bits
    
    res = (input_1 >> shiftby)
    
    cpu.r[instr.rd]  = mask32(res)
    
    if(instr.setflags):
        handleFlags_LS(cpu, res, input_1, shiftby, shiftLeft=False)
   
    return

def ASR(instr: INSTRUCTION, cpu: CPU):
    #ASRS <Rds>,<rs2>
    # ASRS <Rd>,<rs2>,#<imm5>
    input_1 = cpu.r[instr.rs1]  #assuming input_1 stored as unsigned integer 
    
    if(instr.isImm):
        shiftby = instr.imm32       
    else:
        shiftby = (cpu.r[instr.rs2] & 0x0FF)    #lower 8 bits
    
    #sign before shifting nad leave it to python 
    input_1 = toSigned32(input_1)
        
    res = mask32((input_1 >> shiftby))
    
    #check sign -ultranative way
    # if(input_1 & 0x8000_0000):
    #     if(shiftby>=32):
    #         res = 0xFFFF_FFFF
    #     else:
    #         mask =  ((pow(2, shiftby))-1) << (32 - shiftby) 
    #         res = res | mask         
         
    cpu.r[instr.rd] = res 
    
    #inplace handling flags
    if(instr.setflags):
        cpu.N = bool(res & 0x80000000)     #is negative? 1:0
        cpu.Z = (res==0)             #is Zero
        if(0<shiftby<32):                  
            cpu.C = bool((input_1>>(shiftby-1)) & 1)
        elif(shiftby>=32):
            cpu.C =  bool(input_1& 0x8000_0000)
        
    return

#RORS R0, R1, no immdiate expected
def ROR(instr: INSTRUCTION, cpu: CPU):
    #RORS <Rds>,<rs2>
    input_1 = cpu.r[instr.rs1]
    shiftby = (cpu.r[instr.rs2] & 0x0FF)    #lower 8 bits
    res = input_1
    for i in range(shiftby):
        
        bit_0 = res & 0x0000_0001 #get bit 0
        res = res >> 1            #shift R one bit
        if(bit_0 == 1):
            res = res | 0x8000_0000 # set MST to 1
        #if bit_0 is zero, no need to handle it's already done by pythone

    cpu.r[instr.rd]  = mask32(res)
     
    if(instr.setflags):
       cpu.N = bool(res & 0x8000_0000)  #if MSB is 1
       cpu.Z = bool(res == 0) 
       cpu.C = bool (res & 0x8000_0000) if (not shiftby==0) else cpu.C #change only when shift not zero
    
    return


#----------------------------------- BRANCH ------------------------------------
def B(instr: INSTRUCTION, cpu: CPU, nxt):
    #cpu.r[15] have the current address
    #B<c> <label>
    jump = False
    if(instr.condition==0b0000): #BEQ : Equal?
        if(cpu.Z==True):
            jump = True;
    elif(instr.condition==0b0001): #BNE : not equal
        if(cpu.Z==False):
            jump = True
    elif(instr.condition==0b0010): #BCS/BHS : Carry set / Unsigned >=
        if(cpu.C==True):
            jump = True
    elif(instr.condition==0b0011): #BCC/BLO : Carry clear / Unsigned <
        if(cpu.C==False):
            jump = True
    elif(instr.condition==0b0100): #BMI :  Negative
        if(cpu.N==True):
            jump = True
    elif(instr.condition==0b0101): #BPL : Positive or zero
        if(cpu.N==False):
            jump = True       
    elif(instr.condition==0b0110): #BVS : Overflow set
        if(cpu.V==True):
            jump = True       
    elif(instr.condition==0b0111): #BVC : Overflow clear
        if(cpu.V==False):
            jump = True
    elif(instr.condition==0b1000): #BHI: unsigned >
        if(cpu.C and not cpu.Z):
            jump = True
    elif(instr.condition==0b1001): #BLS: unsigned <=
        if(not cpu.C or cpu.Z):
            jump = True
    elif(instr.condition==0b1010): #BGE: signed >=
        if(cpu.N == cpu.V):
            jump = True
    elif(instr.condition==0b1011): #BLT: signed <
        if(cpu.N != cpu.V):
            jump = True
    elif(instr.condition==0b1100): #BGT: signed >
        if((cpu.V == cpu.N) and not cpu.Z):
            jump = True
    elif(instr.condition==0b1101): #BLE: signed <=
        if((cpu.V != cpu.N) or  cpu.Z):
            jump = True
    elif(instr.condition is None):
        jump = True     #uncoditional B
    else:  #ERROR CONDITION NOT FOUND    
        raise AlUExceptoin("UNDEFINED")
    if(jump):
        nxt =mask32(cpu.r[15]+ instr.imm32 + 4)     #nxt PC
        instr.branch_taken = True                   #branch taken
    #if branch not taken, no change

        
    return nxt

def BL(instr: INSTRUCTION, cpu: CPU, nxt):
    
    #set the return address, bit0 is set, convention and indicator of thumb state
    #LR ar cpu.r[14] = (current Address(PC) + 4) | 1
    cpu.r[14] = mask32((cpu.r[15]+ 4) | 1)
    
    #nxt
    nxt = mask32(cpu.r[15] + 4 + instr.imm32) #next instruction address
    #branch always taken
    instr.branch_taken = True
    
    return nxt
   
def BX(instr: INSTRUCTION, cpu: CPU, nxt):
    # BX <rs1>
    addrs = cpu.r[instr.rs1]
    if(addrs & 0x0000_0001):#LSB is 1, state Thumb
        nxt = mask32(addrs &0xFFFF_FFFE)    #set bit_0 to 0
        instr.branch_taken = True          #branch taken
    else: #ERROR, LR indicates different state, not handled
         raise AlUExceptoin("INVSTATE")  
    
    return nxt
    
def BLX(instr: INSTRUCTION, cpu: CPU, nxt):
    # BLX <rs1>
    addrs = cpu.r[instr.rs1]    #address of next instruction
    if(addrs & 0x0000_0001):#LSB is 1, state Thumb
        nxt = mask32(addrs &0xFFFF_FFFE)    #set bit_0 to 0
        instr.branch_taken = True           #branch taken
    else:#EXCEPTION
        raise AlUExceptoin("INVSTATE")
    #LR at cpu.r[14] = (current Address(PC) + 2) | 1
    cpu.r[14] = mask32((cpu.r[15]+ 2) | 1)  #return address
    
    return nxt

#------------------------------------- Sign Extention ---------------------------
def SXTB(instr: INSTRUCTION, cpu: CPU):
    #SXTB <rd>,<rs1>
    val = cpu.r[instr.rs1]
    
    #is signed at bit 7
    if((val>>7)&1):#negative
        val = (val | 0xFFFF_FF00)   #sign negative extneded the upper 24 bits 
    else:
        val = (val & 0x0000_00FF)   #sign positive extneded the upper 24 bits
    
    cpu.r[instr.rd] = mask32(val)
    return 
def SXTH(instr: INSTRUCTION, cpu: CPU):
    #SXTh <rd>,<rs1>
    val = cpu.r[instr.rs1]
    
    #is signed at bit 15
    if((val>>15)&1):#negative
        val = (val | 0xFFFF_0000)   #sign negative extneded the upper 16 bits 
    else:
        val = (val & 0x0000_FFFF)   #sign positive extneded the upper 16 bits
    
    cpu.r[instr.rd] = mask32(val)
   
    return 

def UXTB(instr: INSTRUCTION, cpu: CPU):
    #UXTB <rd>,<rs1>
    cpu.r[instr.rd] = mask32((cpu.r[instr.rs1] & 0x0000_00FF))  #Zero extneded the upper 24 bits
   
    return 
def UXTH(instr: INSTRUCTION, cpu: CPU):
    #UXTH <rd>,<rs1>
    cpu.r[instr.rd] = mask32((cpu.r[instr.rs1] & 0x0000_FFFF))  #Zero extneded the upper 24 bits
   
    return

#-------------------------------------     reverse    ---------------------------------------
def REV(instr: INSTRUCTION, cpu: CPU):
    # REV <rd>,<rs1>
    val = mask32(cpu.r[instr.rs1])
    res = 0x0000_0000
    for i in range(4):
        res = res << 8
        res = ((val& 0x0000_00FF)  | res )
        val = val >> 8
        
    cpu.r[instr.rd] = mask32(res)
    
    return 
 
    
#helper functino
def mask32(val):
    return (val & 0xFFFFFFFF) #return only first 32 bits
def toSigned32(val):
    val = val & 0xFFFF_FFFF     #lower 32 bits
    if(val & 0x8000_0000): #is bit 31  negative
        val = val - 0x1_0000_0000 #make it negative)
    return val
def handleFlags_ADD(cpu: CPU, num1, num2, carry_in=0):
    res = num1 + num2 + carry_in #full result
    cpu.C = (res>0xFFFFFFFF)     #unsigned overflow, num out of range
    res = mask32(res)
    cpu.N = bool(res & 0x80000000)     #is negative? 1:0
    cpu.Z = (res==0)             #is Zero
    # overflow when both same signs and res is different sign
    cpu.V = ((num1 & 0x80000000)==(num2 & 0x80000000)) and ((res & 0x80000000)!=(num1 & 0x80000000))
    return
def handleFlags_SUB(cpu: CPU, num1, num2, borrow=0):
    diff = num1 - num2 - borrow
    cpu.C = bool(num1 >= (num2 + borrow)) #no borrow = 1, borrow = 0
    diff = mask32(diff)
    cpu.N = bool(diff & 0x8000_0000)
    cpu.Z = (diff == 0)
    #unsign to signed
    signed_diff = toSigned32(num1) - toSigned32(num2) - borrow
    cpu.V = (signed_diff < -0x8000_0000) or (signed_diff > 0x7FFF_FFFF)
    
 #handle floag for LSL, LSR    
def handleFlags_LS(cpu: CPU, res, num, shift, shiftLeft=1):
    res = mask32(res)
    cpu.N = bool(res & 0x80000000)     #is negative? 1:0
    cpu.Z = (res==0)             #is Zero
   
   #handling C flag
   #shift to left
    if(shiftLeft):
        if(0<shift<32):
            cpu.C = bool((num>>(32-shift)) & 1) 
        elif(shift==32):
            cpu.C = bool(num&0x01)
        elif(shift > 32):
            cpu.C = False;
    #shifting to Right
    else:
        if(0<shift<32):
            cpu.C = bool((num>>(shift-1)) & 1)
        elif(shift==32):
            cpu.C =  bool(num & 0x8000_0000)
        elif(shift > 32):
            cpu.C = False
    #no change when shift =0. cpu.V no need to update

 
# def REV16(instr: INSTRUCTION, cpu: CPU):
#     #reverse lower 2 bytes and upper 2 bytes 
#     val = mask32(cpu.r[instr.rs1])
#     res = 0x0000_0000
#     #lower 16 bits
#     res = res | ((val & 0x0000_FF00) >> 8) #take upper 8 bits to the lower 8 bits in res
#     res = res | ((val & 0x0000_00FF) << 8)   #take 8 lower bits to upper 8 bits in res
#     #upper 16 bits
#     res = res | ((val & 0x00FF_0000) << 8)  
#     res = res | ((val & 0xFF00_0000) >> 8)    
    
#     cpu.r[instr.rd] = mask32(res)
    
#     return 
# def REVSH(instr: INSTRUCTION, cpu: CPU):
#     #reverse lower 2 bytes and upper 2 bytes 
#     val = mask32(cpu.r[instr.rs1])
#     res = 0x0000_0000
#     #lower 16 bits
#     res = res | ((val & 0x0000_FF00) >> 8) #take upper 8 bits to the lower 8 bits in res
#     res = res | ((val & 0x0000_00FF) << 8)   #take 8 lower bits to upper 8 bits in res
    
#     #sign extention
#     if((res>>15)&1):
#         res = res | (0xFFFF_0000)
#     else:
#         res = res & (0x0000_FFFF)  
        
#     cpu.r[instr.rd] = mask32(res)
    
#     return            


# ## enum to determine the type of operation will be performed in execution. 
# class Op(str, Enum):

#     MOV = "MOV"         # MOVS #imm8, MOV reg, MOVS reg (LSLS #0)
#     MVN = "MVN"         # MVNS Rd, rs2

#     # Arithmetic
#     ADD = "ADD"         # ADDS imm3/imm8/reg, ADD high/SP+reg/SP+imm7/SP+imm8
#     ADR = "ADR"         # ADR Rd, label (Align(PC + 4, 4) + imm32)
#     ADC = "ADC"         # ADCS Rds, rs2
#     SUB = "SUB"         # SUBS imm3/imm8/reg, SUB SP-imm7
#     SBC = "SBC"         # SBCS Rds, rs2
#     RSB = "RSB"         # RSBS Rd, rs1, #0
#     MUL = "MUL"         # MULS Rdm, rs1, Rdm

#     # Logic & Shifts
#     AND = "AND"         # ANDS Rds, rs2
#     ORR = "ORR"         # ORRS Rds, rs2
#     EOR = "EOR"         # EORS Rds, rs2
#     BIC = "BIC"         # BICS Rds, rs2
#     TST = "TST"         # TST rs1, rs2
#     LSL = "LSL"         # LSLS imm5, LSLS reg
#     LSR = "LSR"         # LSRS imm5, LSRS reg
#     ASR = "ASR"         # ASRS imm5, ASRS reg
#     ROR = "ROR"         # RORS Rds, rs2

#     # Compare
#     CMP = "CMP"         # CMP #imm8, CMP reg (low & high)
#     CMN = "CMN"         # CMN rs1, rs2

#     # Extend & Reverse
#     SXTB = "SXTB"       # SXTB Rd, rs2
#     SXTH = "SXTH"       # SXTH Rd, rs2
#     UXTB = "UXTB"       # UXTB Rd, rs2
#     UXTH = "UXTH"       # UXTH Rd, rs2
#     REV = "REV"         # REV Rd, rs2

#     # Load & Store
#     LDR = "LDR"         # LDR imm5, LDR [SP, #imm8], LDR reg, LDR literal [PC, #imm8]
#     LDRB = "LDRB"       # LDRB imm5, LDRB reg
#     LDRH = "LDRH"       # LDRH imm5, LDRH reg
#     LDRSB = "LDRSB"     # LDRSB reg
#     LDRSH = "LDRSH"     # LDRSH reg
#     STR = "STR"         # STR imm5, STR [SP, #imm8], STR reg
#     STRB = "STRB"       # STRB imm5, STRB reg
#     STRH = "STRH"       # STRH imm5, STRH reg

#     # Multiple
#     LDM = "LDM"         # LDM rs1{!}, <registers>
#     STM = "STM"         # STM rs1!, <registers>
#     PUSH = "PUSH"       # PUSH <registers>
#     POP = "POP"         # POP <registers>

#     # Control & System
#     B = "B"             # B label (condition=None) and B<c> label (condition=0..13)
#     BL = "BL"           # BL label (32-bit, size=4)
#     BX = "BX"           # BX rs2
#     BLX = "BLX"         # BLX rs2
#     SVC = "SVC"         # SVC #imm8

#             # NOP
#     NOP = "NOP"
        
        



        
