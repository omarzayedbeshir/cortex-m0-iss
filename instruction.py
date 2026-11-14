

class INSTRUCTION:
    def __init__(self, type, rd, rs1, rs2, imm, isImm, set_flags, address, size):
        self.type = type                 #type of instruction, add, sub, BEQ, etc, if ADDS, set_flags to True, and same for others
        self.rd   = rd                   #DESTINATION REGISTER
        self.rs1  = rs1                  #first REGISTER SOURCES 
        self.rs2  = rs2                  #second register source
        self.imm  = imm                  #immediate value
        self.isImm= isImm                #instruction have imm
        self.set_flags = set_flags       #update flags
        self.address = address           #current address of instruciton
        self.size = size                 #instruction size = 2 bytes by default
        