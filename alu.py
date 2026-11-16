from instruction import INSTRUCTION, Op
from cpu import CPU
from Memory import *

                #-------------------------------------------------------------------------#
                #This ALU is done by @BawahabYousefOmar For CSCE Assymbly course in AUC   |
                #Assume CPU registers always contain unsigned 32-bit values               |
                #                                                                         |
                #-------------------------------------------------------------------------#   
    
def execute ( instr: INSTRUCTION, cpu: CPU):
  
  #denitfy the instructin type
  match instr.op:
      case "ADD"  : ADD(instr, cpu)
      case "ADC"  : ADC(instr, cpu)
      case "SUB"  : SUB(instr, cpu)
      case "RSB"  : RSB(instr, cpu)
      case "MUL"  : MUL(instr, cpu)
      case "AND"  : AND(instr, cpu)
      case "ORR"  : ORR(instr, cpu)
      case "EOR"  : EOR(instr, cpu)

      #____ load, store, push, pop 

      case Op.LDR | Op.LDRH | Op.LDRB | Op.LDRSH | Op.LDRSB:
            load(cpu, instr, read_mem)

      case Op.STR | Op.STRH | Op.STRB:
            store(cpu, instr, write_mem)

      case Op.PUSH:
            exec_push(cpu, instr, write_mem)

      case Op.POP:
            nxt = exec_pop(cpu, instr, nxt, read_mem, fault)

      case Op.LDM:
            loadMult(cpu, instr, read_mem)

      case Op.STM:
            StorMult(cpu, instr, write_mem)

  return 


def ADD( instr: INSTRUCTION, cpu: CPU):
     input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
     #check if second register is just an imm
     if(instr.isImm): 
         input_2 = mask32(instr.imm)
     else:
         input_2 = mask32(cpu.r[instr.rs2])
      
     #count sum
     res = (input_1 + input_2)
     cpu.r[instr.rd] = mask32(res)
     #if flags should changed in case ADDS
     if( instr.set_flags):
        handleFlags_ADD(cpu, input_1, input_2, carry_in=int(cpu.C))
     
     return 
def ADC( instr: INSTRUCTION, cpu: CPU):
     input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
     #rs2
     input_2 = mask32(cpu.r[instr.rs2])
      
     #count sum
     res = input_1 + input_2 + cpu.C # rs1, rs2, carry
     
     cpu.r[instr.rd] = mask32(res)
     #if flags should changed in case ADDS
     if(instr.set_flags):
        handleFlags_ADD(cpu, input_1, input_2, carry_in=int(cpu.C)) 
     
     return 

def SUB( instr: INSTRUCTION, cpu: CPU):
        input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
        #check if second register is just an imm
        if(instr.isImm): 
            input_2 = mask32(instr.imm)
        else:
            input_2 = mask32(cpu.r[instr.rs2])
            
        diff = input_1 - input_2    #get difference
        cpu.r[instr.rd] = mask32(diff)
        
        if(instr.set_flags):
            handleFlags_SUB(cpu, input_1, input_2)
            
        return 
 #SBCS r0, r1     no immdiate   
def SBC( instr: INSTRUCTION, cpu: CPU):
        input_1 =  mask32(cpu.r[instr.rs1])  #rs1 have the index of value
        #not immdiate
        input_2 = mask32(cpu.r[instr.rs2])
           
        borrow = 1 - int(cpu.C)     #if C_pre is 0, means borrow occurs, so considerate 
        diff = input_1 - input_2  - borrow  #get difference
        cpu.r[instr.rd] = mask32(diff)
        
        if(instr.set_flags):
            handleFlags_SUB(cpu, input_1, input_2, borrow )
            
        return     
 
 #RSBS R0, R1, #0  no immdiate other than 0 supported, always set flags
def RSB(instr: INSTRUCTION, cpu: CPU):
     input_1 = cpu.r[instr.rs1]  
     res = 0 - input_1         #negate
     
     cpu.r[instr.rd] = mask32(res)  
     
     handleFlags_SUB(cpu, 0, input_1)
         
     return 
 #            

#MULS r0, r1
def MUL(instr: INSTRUCTION, cpu: CPU):
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
    
#--------------------------- BITWISE ---------------------------------#
#ANDS r0, r1    no immdiate expected
def AND(instr: INSTRUCTION, cpu: CPU):
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
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 ^ input_2
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
#bit Clear : BICS r0, r1
def BIC(instr: INSTRUCTION, cpu: CPU):
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 &(~input_2)   # r0 & (not r1)
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

#TST r0, r1, like AND, no store 
def TST(instr: INSTRUCTION, cpu: CPU):
    input_1 = cpu.r[instr.rs1]
    input_2 = cpu.r[instr.rs2]
    res = input_1 & input_2
    res = mask32(res)
    
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


#----------------------------- LOGICAL -----------------------------

#LSLS r0, r1, #2 or LSLS r0, r1
def LSL(instr: INSTRUCTION, cpu: CPU):
    

    input_1 = cpu.r[instr.rs1]
    
    if(instr.isImm):
        shiftby = instr.imm 
    else:
        shiftby = (cpu.r[instr.rs2] & 0x0FF)    #lower 8 bits
    
    res = (input_1 << shiftby)
    
    cpu.r[instr.rd]  = mask32(res)
    
    if(instr.set_flags):
        handleFlags_LS(cpu, res, input_1, shiftby)
   
    return 

def LSR(instr: INSTRUCTION, cpu: CPU):
    
    input_1 = cpu.r[instr.rs1]
    
    if(instr.isImm):
        shiftby = instr.imm         #imm have the decoded shift amount like LSR r0, r1, #32
    else:
        shiftby = (cpu.r[instr.rs2] & 0x0FF)    #lower 8 bits
    
    res = (input_1 >> shiftby)
    
    cpu.r[instr.rd]  = mask32(res)
    
    if(instr.set_flags):
        handleFlags_LS(cpu, res, input_1, shiftby, shiftLeft=False)
   
    return

def ASR(instr: INSTRUCTION, cpu: CPU):
    input_1 = cpu.r[instr.rs1]  #assuming input_1 stored as unsigned integer 
    
    if(instr.isImm):
        shiftby = instr.imm       
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
    if(instr.set_flags):
        cpu.N = bool(res & 0x80000000)     #is negative? 1:0
        cpu.Z = (res==0)             #is Zero
        if(0<shiftby<32):                  
            cpu.C = bool((input_1>>(shiftby-1)) & 1)
        elif(shiftby>=32):
            cpu.C =  bool(input_1& 0x8000_0000)
        
    return

#RORS R0, R1, no immdiate expected
def ROR(instr: INSTRUCTION, cpu: CPU):
    
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
     
    if(instr.set_flags):
       cpu.N = bool(res & 0x8000_0000)  #if MSB is 1
       cpu.Z = bool(res == 0) 
       cpu.C = bool (res & 0x8000_0000) if (not shiftby==0) else cpu.C #change only when shift not zero
    
    return

    



#_______________________________________________________

#helper functino
def mask32(val):
    return (val & 0xFFFFFFFF) #return only first 32 bits

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
    #overflow when num1 and num2 differs in signs and num1 and diff too
    cpu.V = ((num1 & 0x8000_0000) != (num2 & 0x8000_0000)) and ((diff & 0x8000_0000) != (num1 & 0x8000_0000))
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
    

def toSigned32(val):
    val = val & 0xFFFF_FFFF     #lower 32 bits
    if(val & 0x8000_0000): #is bit 31  negative
        val = val - 0x1_0000_0000 #make it negative)
    return val
        
        
        



        
