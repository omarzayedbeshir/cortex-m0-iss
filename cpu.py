
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


