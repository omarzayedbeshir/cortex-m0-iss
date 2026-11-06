@ Regression: sequential_branches_m0plus
@ main(void) is not used; entry is _start.
.syntax unified
.cpu cortex-m0
.thumb
.section .vectors, "a"
.word 0x20040000
.word _start
.text
.global _start
.thumb_func
_start:
  .hword 0xf000  @ BL first halfword
  .hword 0xf800  @ BL second halfword; target is next instruction
  .hword 0xe7ff  @ b to next instruction
  .hword 0x2200  @ movs r2, #0; Z=1
  .hword 0xd0ff  @ beq to next instruction; taken
  .hword 0xdf31  @ svc CYCLES; r0 must be 12 on m0 or 9 on m0plus
  .hword 0xdf12  @ svc PUTINT
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
