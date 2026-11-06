@ Regression: trace_resume
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
  .hword 0xdf43  @ svc TRACE_OFF; omitted
  .hword 0xdf42  @ svc TRACE_ON; included
  .hword 0x2000  @ movs r0, #0
  .hword 0xdf00  @ svc EXIT
