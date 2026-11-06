@ Regression: adr
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
  .hword 0xa007  @ adr r0, 0x120
  .hword 0xdf11  @ svc PUTS
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
  .org 0x20
  .word 0x000a4b4f
