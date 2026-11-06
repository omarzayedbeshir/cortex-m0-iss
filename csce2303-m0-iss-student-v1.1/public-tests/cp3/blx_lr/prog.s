@ Regression: blx_lr
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
  .hword 0x4807  @ ldr r0, [pc, #28]
  .hword 0x4686  @ mov lr, r0
  .hword 0x47f0  @ blx lr; must branch to 0x10a using OLD lr
  .hword 0x2063  @ movs r0, #99; failure
  .hword 0xdf00  @ svc EXIT
  .hword 0x2000  @ movs r0, #0; success
  .hword 0xdf00  @ svc EXIT
  .org 0x20
  .word 0x0000010b
