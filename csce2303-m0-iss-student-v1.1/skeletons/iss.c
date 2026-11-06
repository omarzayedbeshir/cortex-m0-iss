/* iss.c -- CSCE 2303 Cortex-M0 simulator skeleton.
   Build: gcc -O2 -Wall -o iss iss.c      Run: ./iss prog.dump */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define ROM_BASE  0x00000000u
#define ROM_SIZE  (1u << 20)              /* 1 MB   */
#define RAM_BASE  0x20000000u
#define RAM_SIZE  (256u << 10)            /* 256 KB */
#define MAX_INSTR 100000000ull

uint8_t  rom[ROM_SIZE], ram[RAM_SIZE];
uint32_t r[16];                    /* r[13] = sp, r[14] = lr, r[15] = pc */
int      N, Z, C, V;               /* the APSR flags */
uint64_t instret;

void fault(const char *kind)
{
    fprintf(stderr, "FAULT %s at pc=0x%08x\n", kind, r[15]);
    exit(255);
}

/* Pointer to the byte at addr, or NULL if addr is unmapped. */
uint8_t *mem_ptr(uint32_t addr)
{
    if (addr - ROM_BASE < ROM_SIZE) return &rom[addr - ROM_BASE];
    if (addr - RAM_BASE < RAM_SIZE) return &ram[addr - RAM_BASE];
    return NULL;
}

uint32_t read_mem(uint32_t addr, int size)       /* size = 1, 2 or 4 */
{
    if (addr % size) fault("UNALIGNED");
    uint8_t *p = mem_ptr(addr);
    if (!p) fault("BUS");
    uint32_t v = 0;
    for (int i = size - 1; i >= 0; i--)                  /* little-endian */
        v = (v << 8) | p[i];
    return v;
}

void write_mem(uint32_t addr, uint32_t v, int size)
{
    if (addr % size) fault("UNALIGNED");
    if (addr - RAM_BASE >= RAM_SIZE) fault("BUS");       /* only RAM is writable */
    for (int i = 0; i < size; i++)
        ram[addr - RAM_BASE + i] = (uint8_t)(v >> (8 * i));
}

/* Load a `readelf -x` dump. A data line looks like
     "  0x00000100 094811df 0a2000f0 03f812df 002000df .H... ......"
   The 35 characters after the address hold up to 16 bytes; the rest is ASCII. */
void load_dump(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(253); }
    char line[256];
    while (fgets(line, sizeof line, f)) {
        char *s = line;
        while (*s == ' ') s++;
        if (strncmp(s, "0x", 2) != 0) continue;          /* headers, blank lines */
        uint32_t addr = (uint32_t)strtoul(s, &s, 16);
        s++;                                             /* the space after the address */
        for (int i = 0; i + 1 < 35 && s[i] && s[i] != '\n'; ) {
            if (s[i] == ' ') { i++; continue; }
            unsigned byte;
            if (sscanf(s + i, "%2x", &byte) != 1) break;
            uint8_t *p = mem_ptr(addr++);
            if (!p) { fprintf(stderr, "load error\n"); exit(253); }
            *p = (uint8_t)byte;
            i += 2;
        }
    }
    fclose(f);
}

void reset(void)
{
    r[13] = read_mem(0, 4);                  /* initial sp   */
    uint32_t pc = read_mem(4, 4);            /* reset vector */
    r[15] = pc;                            /* diagnostic uses the reset vector */
    if (!(pc & 1)) fault("INVSTATE");
    r[15] = pc & ~1u;
    r[14] = 0xFFFFFFFFu;
}

void set_nz(uint32_t x) { N = x >> 31; Z = (x == 0); }

void svc(int n)
{
    switch (n) {
    case 0x00: exit(r[0] & 0xFF);                                    /* EXIT    */
    case 0x10: putchar(r[0] & 0xFF); break;                          /* PUTCHAR */
    case 0x11: for (uint32_t a = r[0]; read_mem(a, 1); a++)          /* PUTS    */
                   putchar(read_mem(a, 1));
               break;
    case 0x12: printf("%d", (int32_t)r[0]); break;                   /* PUTINT  */
    /* TODO: the other services in section 5 of the handout */
    default:   fault("UNDEFINED");
    }
}

/* Execute one instruction. r[15] holds the address of the current
   instruction; an instruction that reads pc must see r[15] + 4. */
void step(void)
{
    uint32_t pc = r[15];
    uint32_t hw = read_mem(pc, 2);
    uint32_t next = pc + 2;

    if ((hw >> 11) >= 0x1D) {                     /* 11101, 11110, 11111: 32-bit */
        uint32_t hw2 = read_mem(pc + 2, 2);
        (void)hw2;
        next = pc + 4;
        fault("UNDEFINED");                       /* TODO: BL, from hw and hw2 */
    }
    else if ((hw & 0xF800) == 0x2000) {           /* MOVS Rd, #imm8 */
        int rd = (hw >> 8) & 7;
        r[rd] = hw & 0xFF;
        set_nz(r[rd]);
    }
    else if ((hw & 0xF800) == 0xE000) {           /* B label (unconditional) */
        int32_t off = hw & 0x7FF;
        if (off & 0x400) off -= 0x800;            /* sign-extend 11 bits */
        next = pc + 4 + off * 2;
    }
    else if ((hw & 0xFF00) == 0xDF00) {           /* SVC #imm8 */
        svc(hw & 0xFF);
    }
    /* TODO: the other instructions in section 4 of the handout */
    else {
        fault("UNDEFINED");
    }

    r[15] = next;
    instret++;
    /* TODO: write a trace line here when --trace is given (section 6) */
}

int main(int argc, char **argv)
{
    /* TODO: parse the options in section 6 */
    if (argc != 2) { fprintf(stderr, "usage: %s PROGRAM\n", argv[0]); return 2; }
    load_dump(argv[1]);
    reset();
    for (;;) {
        if (instret >= MAX_INSTR) {
            fprintf(stderr, "LIMIT at pc=0x%08x\n", r[15]);
            exit(254);
        }
        step();
    }
}
