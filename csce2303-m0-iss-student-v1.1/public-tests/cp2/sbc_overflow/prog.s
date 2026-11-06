@ Regression: sbc_overflow
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
  .hword 0x2000  @ movs r0, #0
  .hword 0x4907  @ ldr r1, [pc, #28]
  .hword 0x4288  @ cmp r0, r1; C=0
  .hword 0x4188  @ sbcs r0, r1; NZCV must be 1000
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
  .org 0x20
  .word 0x7fffffff
