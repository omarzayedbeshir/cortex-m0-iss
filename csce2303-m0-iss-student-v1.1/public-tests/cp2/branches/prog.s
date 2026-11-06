@ main(void) is not used: this image enters at _start.
@ branches: every condition code taken and not taken, plus loops
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
	movs r4, #0              @ count taken branches in r4
	movs r0, #5
	cmp r0, #5
	bne 1f
	adds r4, #1              @ eq
1:	cmp r0, #4
	beq 2f
	adds r4, #1              @ ne
2:	cmp r0, #3
	bcc 3f
	adds r4, #1              @ cs
3:	cmp r0, #9
	bcs 4f
	adds r4, #1              @ cc
4:	ldr r1, =0x80000000
	cmp r1, #0
	bpl 5f
	adds r4, #1              @ mi
5:	cmp r0, #0
	bmi 6f
	adds r4, #1              @ pl
6:	ldr r1, =0x7FFFFFFF
	adds r1, #1
	bvc 7f
	adds r4, #1              @ vs
7:	cmp r0, #0
	bvs 8f
	adds r4, #1              @ vc
8:	cmp r0, #2
	bls 9f
	adds r4, #1              @ hi
9:	cmp r0, #5
	bhi 10f
	adds r4, #1              @ ls
10:	ldr r1, =-3
	cmp r1, r0
	bge 11f
	adds r4, #1              @ lt (signed)
11:	cmp r0, r1
	blt 12f
	adds r4, #1              @ ge (signed)
12:	cmp r0, r1
	ble 13f
	adds r4, #1              @ gt
13:	cmp r0, r0
	bgt 14f
	adds r4, #1              @ le
14:	mov r0, r4
	svc #0x12                @ expect 14
	ldr r0, =10
	svc #0x10
	movs r0, #0              @ sum 1..100 with a backward branch
	movs r1, #100
15:	adds r0, r0, r1
	subs r1, #1
	bne 15b
	svc #0x12
	ldr r0, =10
	svc #0x10
	movs r0, #0              @ count down with b and an exit test at the top
	movs r1, #7
16:	cmp r1, #0
	beq 17f
	adds r0, #3
	subs r1, #1
	b 16b
17:	svc #0x12
	ldr r0, =10
	svc #0x10
	mov r0, r4
	svc #0x00                @ exit status 14
	.ltorg
