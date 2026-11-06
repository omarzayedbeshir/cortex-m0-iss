@ main(void) is not used: this image enters at _start.
@ console: the console services with input (reads a name and three numbers)
	.syntax unified
	.cpu cortex-m0
	.thumb
	.section .vectors, "a"
	.word 0x20040000
	.word _start
	.text
	.thumb_func
	.global _start
_start:
	ldr r0, =prompt
	svc #0x11
	ldr r4, =0               @ read one line with GETCHAR, echo it back
1:	svc #0x14
	cmp r0, #10
	beq 2f
	svc #0x10
	adds r4, #1
	b 1b
2:	ldr r0, =10
	svc #0x10
	mov r0, r4
	svc #0x12                @ length of the name
	ldr r0, =10
	svc #0x10
	svc #0x15                @ three numbers with GETINT
	mov r5, r0
	svc #0x15
	adds r5, r5, r0
	svc #0x15
	adds r5, r5, r0
	mov r0, r5
	svc #0x12
	ldr r0, =32
	svc #0x10
	mov r0, r5
	svc #0x13
	ldr r0, =10
	svc #0x10
	svc #0x15                @ no more numbers: 0
	svc #0x12
	svc #0x14                @ end of file: -1
	svc #0x12
	ldr r0, =10
	svc #0x10
	movs r0, #0
	svc #0x00
	.ltorg
	.section .rodata
prompt:	.asciz "name: "
