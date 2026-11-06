@ Regression: adc_overflow
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
  .hword 0x2100  @ movs r1, #0
  .hword 0x4289  @ cmp r1, r1; C=1
  .hword 0x4148  @ adcs r0, r1; NZCV must be 1001
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
  .org 0x20
  .word 0x7fffffff
