@ Regression: console_bytes
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
  .hword 0x2080  @ movs r0, #128
  .hword 0xdf10  @ svc PUTCHAR
  .hword 0x2007  @ movs r0, #7
  .hword 0xdf12  @ svc PUTINT
  .hword 0x20ff  @ movs r0, #255
  .hword 0xdf10  @ svc PUTCHAR
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
