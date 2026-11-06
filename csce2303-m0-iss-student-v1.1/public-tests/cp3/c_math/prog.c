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

/* Integer arithmetic only. No division, floating point, or compiler helpers. */
static unsigned crc32(const unsigned char *p, unsigned n) {
    unsigned crc = ~0u;
    for (unsigned i = 0; i < n; ++i) {
        crc ^= p[i];
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ ((0u - (crc & 1u)) & 0xedb88320u);
    }
    return ~crc;
}
static unsigned rotate_left(unsigned value, unsigned amount) {
    amount &= 31u;
    return (value << amount) | (value >> ((0u - amount) & 31u));
}
static volatile unsigned rotate_value = 0x80000001u;
static volatile unsigned rotate_amount = 4u;
static volatile unsigned long long values[3] = {
    0x00000001ffffffffull, 0x0000000200000001ull, 0xfffffff000000000ull
};
int main(void) {
    iss_puts("crc32 = "); iss_puthex(crc32((const unsigned char *)"123456789", 9));
    iss_puts("\nrotate = "); iss_puthex(rotate_left(rotate_value, rotate_amount));
    unsigned long long total = 0;
    for (unsigned i = 0; i < 3; ++i) total += values[i];
    iss_puts("\nsum high = "); iss_puthex((unsigned)(total >> 32));
    iss_puts(", low = "); iss_puthex((unsigned)total); iss_putchar('\n');
    return 0;
}
