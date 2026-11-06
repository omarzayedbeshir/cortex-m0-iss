@ main(void) is not used: this image enters at _start.
@ calls: recursive Fibonacci with BL, PUSH, POP {pc} and BX lr
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
	movs r0, #15
	bl fib
	svc #0x12                @ 610
	ldr r0, =10
	svc #0x10
	movs r0, #6
	bl sq
	svc #0x12                @ 36
	ldr r0, =10
	svc #0x10
	movs r0, #0
	svc #0x00
	.thumb_func
fib:	push {r4, r5, lr}        @ r0 = n, returns fib(n)
	cmp r0, #2
	blt 1f
	movs r4, r0
	subs r0, #1
	bl fib
	movs r5, r0
	subs r0, r4, #2
	bl fib
	adds r0, r0, r5
1:	pop {r4, r5, pc}
	.thumb_func
sq:	muls r0, r0, r0          @ leaf function, returns with bx lr
	bx lr
	.ltorg
