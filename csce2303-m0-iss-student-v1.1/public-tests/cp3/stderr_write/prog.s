@ Regression: stderr_write
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
  .hword 0x4907  @ ldr r1, [pc, #28]
  .hword 0x2002  @ movs r0, #2
  .hword 0x2203  @ movs r2, #3
  .hword 0xdf23  @ svc WRITE
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
  .org 0x20
  .word 0x00000140
  .org 0x40
  .word 0x000a4b4f
