@ main(void) is not used: this image enters at _start.
@ debug_aids: RAND, DUMP_MEM, TRACE_ON and TRACE_OFF (run with --trace)
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
	ldr r6, =array
	movs r7, #0
1:	svc #0x32                @ fill 8 words with RAND
	lsrs r0, r0, #24
	str r0, [r6, r7]
	adds r7, #4
	cmp r7, #32
	bne 1b
	mov r0, r6
	movs r1, #32
	svc #0x41                @ DUMP_MEM before (stderr)
	svc #0x43                @ TRACE_OFF: the set-up above is traced, the sort below is not
	movs r4, #7
2:	mov r0, r6
	movs r5, #0
3:	ldr r1, [r0, #0]
	ldr r2, [r0, #4]
	cmp r1, r2
	bls 4f
	str r2, [r0, #0]
	str r1, [r0, #4]
4:	adds r0, #4
	adds r5, #1
	cmp r5, r4
	bne 3b
	subs r4, #1
	bne 2b
	svc #0x42                @ TRACE_ON
	mov r0, r6
	movs r1, #32
	svc #0x41                @ DUMP_MEM after (stderr)
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
	.data
	.balign 4
array:	.space 32
