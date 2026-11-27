import alu
import decoder
from Memory import *
from instruction import INSTRUCTION, Op

class CPUExceptoin(Exception):
        pass

class CPU:
    def __init__(self):
        # Registers holder [R0 to R15]
        self.r = [0] * 16        # r[13] = sp, r[14] = lr, r[15] = pc
        # Flags
        self.N = False
        self.Z = False
        self.C = False
        self.V = False
        
        # Instruction retired counter
        self.instret = 0
        #cycles
        self.cycles = 0             #total accumulated cycles
        self.branchPenality = 2     #Cost of taking a branch, = 2 for M0 'default', 1 for M0+
        

    def reset(self):
        self.r[:] = [0] * 16
        self.N = self.Z = self.C = self.V = False
        self.instret = 0
        self.cycles = 0
        self.branchPenality = 2

        self.r[13] = read_mem(0, 4) & 0xFFFFFFFC # initial sp
        pc = read_mem(4, 4) # reset vector
        self.r[15] = pc # diagnostic uses the reset vector
        if not (pc & 1):
             raise CPUExceptoin("INVSTATE")
        self.r[15] = pc & ~1
        self.r[14] = 0xFFFFFFFF
    
    
    def instrCycles(self, instr: INSTRUCTION):
        cyl = 1 + instr.memory_accesses + (self.branchPenality if instr.branch_taken else 0) + ( 1 if instr.op=="BL" else 0) 
        return cyl
   
    
      
def execute ( instr: INSTRUCTION, cpu: CPU, nxt):
  
  #denitfy the instructin type
  match instr.op:
      case "ADD"  : nxt = alu.ADD(instr, cpu, nxt)
      case "ADR"  : alu.ADR(instr, cpu)
      case "SUB"  : alu.SUB(instr, cpu)
      case "SBC"  : alu.SBC(instr, cpu)
      case "RSB"  : alu.RSB(instr, cpu)
      case "ADC"  : alu.ADC(instr, cpu)
      case "CMP"  : alu.CMP(instr, cpu)
      case "CMN"  : alu.CMN(instr, cpu)
      case "MUL"  : alu.MUL(instr, cpu)
      case "AND"  : alu.AND(instr, cpu)
      case "ORR"  : alu.ORR(instr, cpu)
      case "EOR"  : alu.EOR(instr, cpu)
      case "BIC"  : alu.BIC(instr, cpu)
      case "TST"  : alu.TST(instr, cpu)
      case "LSL"  : alu.LSL(instr, cpu)
      case "LSR"  : alu.LSR(instr, cpu)
      case "ASR"  : alu.ASR(instr, cpu)
      case "ROR"  : alu.ROR(instr, cpu)
      case "B"    : nxt = alu.B(instr, cpu, nxt)
      case "BL"   : nxt = alu.BL(instr, cpu, nxt)
      case "BX"   : nxt = alu.BX(instr, cpu, nxt)
      case "BLX"  : nxt = alu.BLX(instr, cpu, nxt)
      case "MOV"  : nxt = alu.MOV(instr, cpu, nxt)
      case "MVN"  : alu.MVN(instr,cpu)
      case "SXTB" : alu.SXTB(instr, cpu)
      case "SXTH" : alu.SXTH(instr, cpu)
      case "UXTB" : alu.UXTB(instr, cpu)
      case "UXTH" : alu.UXTH(instr, cpu)
      case "REV"  : alu.REV(instr, cpu)

       #____ load, store, push, pop 

      case Op.LDR | Op.LDRH | Op.LDRB | Op.LDRSH | Op.LDRSB:
            load(instr, cpu)

      case Op.STR | Op.STRH | Op.STRB:
            store(instr, cpu)

      case Op.PUSH:
            exec_push(instr, cpu)

      case Op.POP:
            nxt = exec_pop(instr, cpu, nxt)

      case Op.LDM:
            loadMult(instr, cpu)

      case Op.STM:
            StorMult(instr, cpu) 

      case _:       raise alu.AlUExceptoin("UNDEFINED") #op is INVALID
      
  return nxt


