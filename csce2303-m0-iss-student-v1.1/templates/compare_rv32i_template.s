# CSCE 2303 RV32I assembly for the comparison template: paste your RARS function here.
# Use only the code (no ecall-based main); the readelf pane shows the size of .text.
        .text
        .globl  my_strlen
my_strlen:                      # a0 = string, returns its length
        mv      t0, a0
1:      lbu     t1, 0(t0)
        beqz    t1, 2f
        addi    t0, t0, 1
        j       1b
2:      sub     a0, t0, a0
        ret
