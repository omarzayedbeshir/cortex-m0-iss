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

/* READ/WRITE return raw counts/errors, without errno or a C stream layer. */
static int read_line(char *s, int capacity) {
    int length = 0;
    unsigned char c;
    while (length + 1 < capacity && iss_read(0, &c, 1) == 1) {
        if (c == '\n') { s[length] = 0; return length; }
        s[length++] = (char)c;
    }
    s[length] = 0;
    return length ? length : -1;
}
int main(void) {
    char line[128], reversed[128];
    int length, count = 0;
    while ((length = read_line(line, sizeof line)) >= 0) {
        int vowels = 0;
        for (int i = 0; i < length; ++i) reversed[i] = line[length - 1 - i];
        for (int i = 0; i < length; ++i) {
            char c = line[i];
            if (c >= 'a' && c <= 'z') c -= 'a' - 'A';
            line[i] = c;
            if (c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') ++vowels;
        }
        iss_write(1, line, (unsigned)length); iss_puts(" | ");
        iss_write(1, reversed, (unsigned)length); iss_puts(" | ");
        iss_putint(vowels); iss_puts(" vowels | ");
        iss_putint(length); iss_puts(" chars\n"); ++count;
    }
    iss_putint(count); iss_puts(" lines\n");
    return count;
}
