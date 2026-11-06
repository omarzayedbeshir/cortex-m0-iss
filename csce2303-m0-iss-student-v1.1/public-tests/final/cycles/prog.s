@ main(void) is not used: this image enters at _start.
@ cycles: CYCLES around loops, loads and calls; run once for each core
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
	svc #0x31
	mov r4, r0
	ldr r1, =1000            @ a counted loop
	movs r0, #0
1:	adds r0, #1
	subs r1, #1
	bne 1b
	svc #0x31
	subs r0, r0, r4
	svc #0x12
	ldr r0, =10
	svc #0x10
	svc #0x31
	mov r4, r0
	ldr r5, =0x20000000      @ loads, stores and multiple
	movs r6, #100
2:	str r6, [r5, #0]
	ldr r1, [r5, #0]
	push {r1, r2, r3}
	pop {r1, r2, r3}
	subs r6, #1
	bne 2b
	svc #0x31
	subs r0, r0, r4
	svc #0x12
	ldr r0, =10
	svc #0x10
	svc #0x31
	mov r4, r0
	movs r6, #100            @ calls and returns
3:	bl leaf
	subs r6, #1
	bne 3b
	svc #0x31
	subs r0, r0, r4
	svc #0x12
	ldr r0, =10
	svc #0x10
	movs r0, #0
	svc #0x00
	.thumb_func
leaf:	push {r4, lr}
	pop {r4, pc}
	.ltorg
