/* CSCE 2303 comparison template: the same file is compiled for the M0 and for RV32I.
   Put only the functions you are measuring here; the readelf pane shows the size of .text. */
#include <stddef.h>

size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}
