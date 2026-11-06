/* ===== CSCE 2303 bare-metal runtime: leave this block unchanged =====
 * No headers, standard library, libgcc, heap, or operating system.
 * ARM AAPCS passes arguments/results in r0-r3, matching the course SVC ABI.
 * Naked wrappers contain only basic assembly; the SVC preserves other registers.
 */
#define ISS_CALL __attribute__((naked, noinline, unused)) static
ISS_CALL void iss_putchar(int byte)                     { __asm volatile("svc #0x10\n bx lr"); }
ISS_CALL void iss_puts(const char *text)                 { __asm volatile("svc #0x11\n bx lr"); }
ISS_CALL void iss_putint(int value)                     { __asm volatile("svc #0x12\n bx lr"); }
ISS_CALL void iss_puthex(unsigned value)                { __asm volatile("svc #0x13\n bx lr"); }
ISS_CALL int iss_getchar(void)                          { __asm volatile("svc #0x14\n bx lr"); }
ISS_CALL int iss_getint(void)                           { __asm volatile("svc #0x15\n bx lr"); }
ISS_CALL int iss_read(int fd, void *buf, unsigned n)     { __asm volatile("svc #0x22\n bx lr"); }
ISS_CALL int iss_write(int fd, const void *buf, unsigned n) { __asm volatile("svc #0x23\n bx lr"); }
__attribute__((naked, noreturn)) static void iss_exit(int status) {
    __asm volatile("svc #0x00\n1: b 1b");
}
#undef ISS_CALL
extern unsigned char __bss_start__[], __bss_end__[];
int main(void);
__attribute__((noreturn)) void _start(void) {
    /* The dump loader places .data at its RAM address; clear .bss here. */
    for (unsigned char *p = __bss_start__; p < __bss_end__; ++p) *p = 0;
    iss_exit(main());
}
__attribute__((section(".vectors"), used))
static void *const vectors[2] = { (void *)0x20040000, (void *)_start };
/* ===== end of runtime block: write your program below ===== */
