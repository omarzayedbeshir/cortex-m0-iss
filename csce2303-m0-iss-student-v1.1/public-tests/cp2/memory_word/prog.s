@ main(void) is not used: this image enters at _start.
@ memory_word: word loads and stores with every addressing form, bubble sort in RAM
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
	ldr r0, =array
	ldr r1, =init
	movs r2, #0
1:	ldr r3, [r1, r2]         @ copy the initial values from ROM to RAM
	str r3, [r0, r2]
	adds r2, #4
	cmp r2, #32
	bne 1b
	sub sp, #8               @ locals on the stack
	movs r3, #7
	str r3, [sp, #4]
	ldr r4, [sp, #4]         @ outer loop counter, from the stack
2:	ldr r0, =array
	movs r5, #0
3:	ldr r1, [r0, #0]
	ldr r2, [r0, #4]
	cmp r1, r2
	ble 4f
	str r2, [r0, #0]
	str r1, [r0, #4]
4:	adds r0, #4
	adds r5, #1
	cmp r5, r4
	bne 3b
	subs r4, #1
	bne 2b
	add sp, #8
	ldr r6, =array           @ print the sorted array
	movs r7, #0
5:	ldr r0, [r6, r7]
	svc #0x12
	ldr r0, =32
	svc #0x10
	adds r7, #4
	cmp r7, #32
	bne 5b
	ldr r0, =10
	svc #0x10
	movs r0, #0
	svc #0x00
	.ltorg
	.section .rodata
	.balign 4
init:	.word 42, -7, 1000, 3, 0, -500, 17, 8
	.data
	.balign 4
array:	.space 32
