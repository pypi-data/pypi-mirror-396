/* ANSI-C code produced by gperf version 3.1 */
/* Command-line: /usr/bin/gperf /home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf  */
/* Computed positions: -k'1-8' */

#if !((' ' == 32) && ('!' == 33) && ('"' == 34) && ('#' == 35) \
      && ('%' == 37) && ('&' == 38) && ('\'' == 39) && ('(' == 40) \
      && (')' == 41) && ('*' == 42) && ('+' == 43) && (',' == 44) \
      && ('-' == 45) && ('.' == 46) && ('/' == 47) && ('0' == 48) \
      && ('1' == 49) && ('2' == 50) && ('3' == 51) && ('4' == 52) \
      && ('5' == 53) && ('6' == 54) && ('7' == 55) && ('8' == 56) \
      && ('9' == 57) && (':' == 58) && (';' == 59) && ('<' == 60) \
      && ('=' == 61) && ('>' == 62) && ('?' == 63) && ('A' == 65) \
      && ('B' == 66) && ('C' == 67) && ('D' == 68) && ('E' == 69) \
      && ('F' == 70) && ('G' == 71) && ('H' == 72) && ('I' == 73) \
      && ('J' == 74) && ('K' == 75) && ('L' == 76) && ('M' == 77) \
      && ('N' == 78) && ('O' == 79) && ('P' == 80) && ('Q' == 81) \
      && ('R' == 82) && ('S' == 83) && ('T' == 84) && ('U' == 85) \
      && ('V' == 86) && ('W' == 87) && ('X' == 88) && ('Y' == 89) \
      && ('Z' == 90) && ('[' == 91) && ('\\' == 92) && (']' == 93) \
      && ('^' == 94) && ('_' == 95) && ('a' == 97) && ('b' == 98) \
      && ('c' == 99) && ('d' == 100) && ('e' == 101) && ('f' == 102) \
      && ('g' == 103) && ('h' == 104) && ('i' == 105) && ('j' == 106) \
      && ('k' == 107) && ('l' == 108) && ('m' == 109) && ('n' == 110) \
      && ('o' == 111) && ('p' == 112) && ('q' == 113) && ('r' == 114) \
      && ('s' == 115) && ('t' == 116) && ('u' == 117) && ('v' == 118) \
      && ('w' == 119) && ('x' == 120) && ('y' == 121) && ('z' == 122) \
      && ('{' == 123) && ('|' == 124) && ('}' == 125) && ('~' == 126))
/* The character set is not based on ISO-646.  */
#error "gperf generated tables don't work with this execution character set. Please report a bug to <bug-gperf@gnu.org>."
#endif

#line 5 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"

#include "../codegen/lookup.h"
#line 8 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
struct _LOOKUP;

#define ATOMTOTAL_KEYWORDS 806
#define ATOMMIN_WORD_LENGTH 3
#define ATOMMAX_WORD_LENGTH 8
#define ATOMMIN_HASH_VALUE 39
#define ATOMMAX_HASH_VALUE 4296
/* maximum key range = 4258, duplicates = 0 */

#ifdef __GNUC__
__inline
#else
#ifdef __cplusplus
inline
#endif
#endif
static unsigned int
_hash_atom (register const char *str, register size_t len)
{
  static unsigned short asso_values[] =
    {
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,   85,
        30, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,  915,
        25,  120,  948,  335,  814,  150,  540,  135, 4297, 4297,
      4297, 4297, 4297, 4297, 4297,   15, 1015,    5,    5, 1000,
      4297,   35,    0, 1005, 4297, 4297,  117,  210,  960,   45,
       220, 4297,  650,  495,  410,  400,  760, 4297,  655, 1309,
        30, 4297, 4297, 4297, 4297,    0, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297, 4297,
      4297, 4297, 4297, 4297, 4297, 4297, 4297
    };
  register unsigned int hval = len;

  switch (hval)
    {
      default:
        hval += asso_values[(unsigned char)str[7]+1];
      /*FALLTHROUGH*/
      case 7:
        hval += asso_values[(unsigned char)str[6]];
      /*FALLTHROUGH*/
      case 6:
        hval += asso_values[(unsigned char)str[5]];
      /*FALLTHROUGH*/
      case 5:
        hval += asso_values[(unsigned char)str[4]];
      /*FALLTHROUGH*/
      case 4:
        hval += asso_values[(unsigned char)str[3]];
      /*FALLTHROUGH*/
      case 3:
        hval += asso_values[(unsigned char)str[2]];
      /*FALLTHROUGH*/
      case 2:
        hval += asso_values[(unsigned char)str[1]];
      /*FALLTHROUGH*/
      case 1:
        hval += asso_values[(unsigned char)str[0]];
        break;
    }
  return hval;
}

struct _LOOKUP *
_lookup_atom (register const char *str, register size_t len)
{
  static struct _LOOKUP wordlist[] =
    {
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 62 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C2", 53},
      {""}, {""}, {""}, {""},
#line 47 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H2", 38},
#line 208 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C2", 199},
      {""}, {""}, {""},
#line 30 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C2", 21},
#line 194 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H2", 185},
#line 759 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C2", 750},
      {""}, {""}, {""},
#line 177 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C2", 168},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 104 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C2", 95},
      {""}, {""}, {""}, {""}, {""},
#line 249 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C2", 240},
#line 692 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HOH_H2", 683},
      {""}, {""},
#line 63 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O2", 54},
      {""}, {""}, {""}, {""}, {""},
#line 209 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_O2", 200},
      {""}, {""}, {""}, {""},
#line 122 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H22", 113},
#line 760 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O2", 751},
      {""}, {""}, {""},
#line 690 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HOH_O", 681},
#line 267 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H22", 258},
#line 744 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O2C", 735},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 76 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H2'", 67},
      {""}, {""}, {""}, {""},
#line 58 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C2'", 49},
#line 222 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H2'", 213},
      {""}, {""}, {""},
#line 40 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H2'", 31},
#line 205 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C2'", 196},
#line 773 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H2'", 764},
      {""}, {""},
#line 20 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C2'", 11},
#line 187 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H2'", 178},
#line 755 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C2'", 746},
      {""}, {""}, {""},
#line 168 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C2'", 159},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 115 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H2'", 106},
      {""},
#line 311 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_H", 302},
      {""}, {""},
#line 94 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C2'", 85},
#line 260 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H2'", 251},
#line 307 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_C", 298},
      {""}, {""}, {""},
#line 240 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C2'", 231},
      {""}, {""}, {""},
#line 59 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O2'", 50},
#line 77 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HO2'", 68},
      {""},
#line 314 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HA", 305},
      {""}, {""}, {""}, {""},
#line 306 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_CA", 297},
      {""},
#line 21 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O2'", 12},
#line 41 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HO2'", 32},
#line 756 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O2'", 747},
#line 312 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_H2", 303},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 766 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_HOC2", 757},
      {""},
#line 95 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O2'", 86},
#line 116 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HO2'", 107},
#line 308 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_O", 299},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 223 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H2''", 214},
      {""}, {""},
#line 74 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H3'", 65},
      {""}, {""}, {""}, {""},
#line 56 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C3'", 47},
#line 220 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H3'", 211},
#line 188 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H2''", 179},
      {""}, {""},
#line 38 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H3'", 29},
#line 203 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C3'", 194},
#line 772 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H3'", 763},
#line 49 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_P", 40},
      {""},
#line 18 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C3'", 9},
#line 185 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H3'", 176},
#line 753 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C3'", 744},
      {""},
#line 196 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_P", 187},
      {""},
#line 166 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C3'", 157},
      {""},
#line 11 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_P", 2},
      {""},
#line 745 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_P", 736},
      {""},
#line 261 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H2''", 252},
      {""},
#line 159 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_P", 150},
#line 113 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H3'", 104},
#line 742 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_PC", 733},
      {""}, {""}, {""},
#line 92 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C3'", 83},
#line 258 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H3'", 249},
      {""}, {""}, {""}, {""},
#line 238 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C3'", 229},
      {""},
#line 85 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_P", 76},
      {""},
#line 57 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O3'", 48},
#line 75 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HO3'", 66},
      {""}, {""},
#line 231 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_P", 222},
      {""},
#line 204 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_O3'", 195},
#line 221 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_HO3'", 212},
      {""}, {""},
#line 19 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O3'", 10},
#line 39 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HO3'", 30},
#line 754 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O3'", 745},
#line 313 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_H3", 304},
      {""}, {""},
#line 167 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_O3'", 158},
#line 186 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_HO3'", 177},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 93 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O3'", 84},
#line 114 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HO3'", 105},
      {""}, {""}, {""}, {""},
#line 239 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_O3'", 230},
#line 259 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_HO3'", 250},
      {""}, {""},
#line 51 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_OP2", 42},
#line 70 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HOP2", 61},
      {""}, {""}, {""}, {""},
#line 198 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_OP2", 189},
#line 216 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_HOP2", 207},
      {""}, {""},
#line 13 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_OP2", 4},
#line 34 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HOP2", 25},
#line 747 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_OP2", 738},
      {""}, {""}, {""},
#line 161 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_OP2", 152},
#line 181 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_HOP2", 172},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 87 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_OP2", 78},
#line 109 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HOP2", 100},
      {""}, {""}, {""}, {""},
#line 233 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_OP2", 224},
#line 254 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_HOP2", 245},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 82 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H5", 73},
      {""}, {""}, {""}, {""},
#line 67 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C5", 58},
#line 228 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H5", 219},
      {""}, {""}, {""}, {""},
#line 213 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C5", 204},
#line 777 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H5", 768},
      {""}, {""},
#line 26 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C5", 17},
      {""},
#line 764 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C5", 755},
      {""}, {""}, {""},
#line 173 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C5", 164},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 100 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C5", 91},
      {""}, {""}, {""}, {""}, {""},
#line 245 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C5", 236},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 48 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_OP3", 39},
#line 69 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HOP3", 60},
      {""}, {""}, {""}, {""},
#line 195 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_OP3", 186},
#line 215 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_HOP3", 206},
      {""}, {""},
#line 10 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_OP3", 1},
#line 33 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HOP3", 24},
#line 748 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_OP3", 739},
#line 767 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_HOP2", 758},
      {""}, {""},
#line 158 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_OP3", 149},
#line 180 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_HOP3", 171},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 84 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_OP3", 75},
#line 108 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HOP3", 99},
      {""}, {""}, {""},
#line 71 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H5'", 62},
#line 230 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_OP3", 221},
#line 253 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_HOP3", 244},
      {""},
#line 137 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C2", 128},
#line 53 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C5'", 44},
#line 217 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H5'", 208},
      {""}, {""}, {""},
#line 35 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H5'", 26},
#line 200 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C5'", 191},
#line 769 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H5'", 760},
      {""}, {""},
#line 15 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C5'", 6},
#line 182 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H5'", 173},
#line 750 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C5'", 741},
      {""}, {""},
#line 281 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C2", 272},
#line 163 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C5'", 154},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 111 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H5'", 102},
      {""}, {""}, {""}, {""},
#line 89 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C5'", 80},
#line 256 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H5'", 247},
      {""}, {""}, {""}, {""},
#line 235 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C5'", 226},
      {""},
#line 770 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H5''", 761},
#line 138 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O2", 129},
#line 52 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O5'", 43},
#line 78 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HO5'", 69},
      {""}, {""}, {""}, {""},
#line 199 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_O5'", 190},
#line 224 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_HO5'", 215},
      {""}, {""},
#line 14 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O5'", 5},
#line 42 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HO5'", 33},
#line 749 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O5'", 740},
      {""}, {""},
#line 282 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_O2", 273},
#line 162 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_O5'", 153},
#line 189 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_HO5'", 180},
      {""}, {""},
#line 693 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MG_MG", 684},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 88 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O5'", 79},
#line 117 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HO5'", 108},
      {""}, {""}, {""}, {""},
#line 234 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_O5'", 225},
#line 262 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_HO5'", 253},
      {""}, {""},
#line 151 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H2'", 142},
#line 72 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H5''", 63},
      {""}, {""}, {""},
#line 133 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C2'", 124},
      {""},
#line 218 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H5''", 209},
      {""},
#line 155 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H3", 146},
      {""},
#line 36 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H5''", 27},
      {""}, {""}, {""}, {""},
#line 296 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H2'", 287},
#line 183 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H5''", 174},
      {""}, {""}, {""},
#line 278 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C2'", 269},
      {""}, {""}, {""},
#line 300 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H3", 291},
      {""}, {""}, {""}, {""}, {""},
#line 110 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H5''", 101},
      {""}, {""}, {""}, {""}, {""},
#line 255 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H5''", 246},
      {""}, {""}, {""}, {""},
#line 357 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_H", 348},
      {""},
#line 44 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H8", 35},
#line 134 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O2'", 125},
#line 152 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HO2'", 143},
#line 349 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_C", 340},
      {""},
#line 24 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C8", 15},
#line 191 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H8", 182},
      {""}, {""},
#line 354 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CD", 345},
      {""},
#line 171 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C8", 162},
      {""}, {""},
#line 360 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HA", 351},
      {""},
#line 287 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C7", 278},
      {""}, {""},
#line 348 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CA", 339},
#line 119 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H8", 110},
      {""}, {""}, {""},
#line 358 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_H2", 349},
#line 98 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C8", 89},
#line 264 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H8", 255},
      {""}, {""}, {""}, {""},
#line 243 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C8", 234},
      {""}, {""}, {""}, {""}, {""},
#line 302 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H72", 293},
      {""},
#line 353 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CG", 344},
      {""}, {""}, {""},
#line 350 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_O", 341},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 149 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H3'", 140},
      {""}, {""}, {""}, {""},
#line 131 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C3'", 122},
      {""},
#line 297 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H2''", 288},
      {""},
#line 363 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HG2", 354},
      {""}, {""}, {""},
#line 124 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_P", 115},
      {""}, {""},
#line 294 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H3'", 285},
      {""}, {""}, {""}, {""},
#line 276 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C3'", 267},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 269 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_P", 260},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 132 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O3'", 123},
#line 150 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HO3'", 141},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 277 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_O3'", 268},
#line 295 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_HO3'", 286},
      {""}, {""}, {""}, {""}, {""},
#line 359 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_H3", 350},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 303 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H73", 294},
      {""}, {""}, {""},
#line 126 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_OP2", 117},
#line 145 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HOP2", 136},
      {""}, {""}, {""}, {""},
#line 723 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C2", 714},
      {""}, {""}, {""},
#line 574 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_H", 565},
      {""}, {""}, {""}, {""},
#line 564 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_C", 555},
#line 271 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_OP2", 262},
#line 290 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_HOP2", 281},
      {""},
#line 364 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HG3", 355},
      {""},
#line 569 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CD", 560},
      {""}, {""}, {""}, {""},
#line 577 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HA", 568},
#line 741 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H22", 732},
      {""}, {""}, {""},
#line 563 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CA", 554},
      {""}, {""}, {""}, {""},
#line 575 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_H2", 566},
      {""}, {""}, {""},
#line 341 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_H", 332},
      {""},
#line 582 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HD2", 573},
      {""},
#line 156 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H5", 147},
#line 334 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_C", 325},
#line 571 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CZ", 562},
      {""}, {""},
#line 142 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C5", 133},
      {""},
#line 568 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CG", 559},
      {""}, {""}, {""},
#line 565 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_O", 556},
#line 344 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_HA", 335},
      {""}, {""}, {""}, {""},
#line 333 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_CA", 324},
#line 706 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2A", 697},
#line 587 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH21", 578},
      {""},
#line 286 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C5", 277},
#line 342 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_H2", 333},
      {""}, {""}, {""}, {""}, {""},
#line 580 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HG2", 571},
      {""}, {""}, {""}, {""}, {""},
#line 736 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HO2'", 727},
      {""}, {""},
#line 338 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_CG", 329},
#line 697 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2G", 688},
      {""}, {""},
#line 335 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_O", 326},
      {""},
#line 735 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H2'", 726},
      {""}, {""}, {""}, {""},
#line 713 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C2'", 704},
      {""}, {""},
#line 123 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_OP3", 114},
#line 144 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HOP3", 135},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 268 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_OP3", 259},
#line 289 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_HOP3", 280},
      {""}, {""}, {""}, {""},
#line 340 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_OD2", 331},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 83 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H6", 74},
      {""},
#line 146 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H5'", 137},
#line 576 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_H3", 567},
#line 714 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2'", 705},
#line 68 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C6", 59},
#line 229 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H6", 220},
#line 128 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C5'", 119},
      {""},
#line 583 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HD3", 574},
      {""},
#line 214 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C6", 205},
#line 778 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H6", 769},
      {""}, {""},
#line 27 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C6", 18},
      {""},
#line 765 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C6", 756},
#line 291 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H5'", 282},
      {""}, {""},
#line 174 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C6", 165},
      {""},
#line 273 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C5'", 264},
      {""}, {""}, {""}, {""}, {""},
#line 703 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3A", 694},
#line 588 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH22", 579},
      {""}, {""},
#line 343 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_H3", 334},
      {""},
#line 101 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C6", 92},
#line 46 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H62", 37},
      {""}, {""},
#line 581 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HG3", 572},
      {""},
#line 246 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C6", 237},
#line 193 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H62", 184},
      {""}, {""},
#line 734 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HO3'", 725},
      {""},
#line 127 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O5'", 118},
#line 153 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HO5'", 144},
#line 698 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3G", 689},
#line 727 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HOG2", 718},
      {""}, {""}, {""},
#line 733 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H3'", 724},
      {""}, {""}, {""}, {""},
#line 711 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C3'", 702},
      {""}, {""}, {""},
#line 272 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_O5'", 263},
#line 298 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_HO5'", 289},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 628 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_H", 619},
#line 102 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O6", 93},
      {""}, {""}, {""},
#line 622 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_C", 613},
      {""},
#line 247 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_O6", 238},
      {""},
#line 704 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_PA", 695},
      {""}, {""}, {""}, {""},
#line 147 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H5''", 138},
      {""},
#line 631 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HA", 622},
      {""}, {""}, {""}, {""},
#line 621 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CA", 612},
      {""}, {""}, {""},
#line 712 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3'", 703},
#line 629 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_H2", 620},
      {""},
#line 527 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_C", 518},
#line 695 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_PG", 686},
#line 292 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H5''", 283},
      {""}, {""}, {""},
#line 532 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CD", 523},
      {""}, {""}, {""}, {""},
#line 535 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HA", 526},
      {""}, {""}, {""}, {""},
#line 526 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CA", 517},
#line 623 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_O", 614},
      {""}, {""}, {""},
#line 533 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_H2", 524},
      {""}, {""}, {""}, {""}, {""},
#line 540 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HD2", 531},
      {""},
#line 120 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H1", 111},
      {""}, {""}, {""}, {""}, {""},
#line 265 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H1", 256},
#line 531 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CG", 522},
#line 65 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C4", 56},
      {""},
#line 627 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CG2", 618},
#line 528 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_O", 519},
#line 691 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HOH_H1", 682},
      {""},
#line 211 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C4", 202},
      {""}, {""}, {""},
#line 32 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C4", 23},
      {""},
#line 762 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C4", 753},
      {""}, {""}, {""},
#line 179 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C4", 170},
      {""},
#line 121 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H21", 112},
      {""},
#line 538 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HG2", 529},
#line 81 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H42", 72},
      {""},
#line 636 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG21", 627},
#line 266 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H21", 257},
#line 743 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O1C", 734},
      {""},
#line 227 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H42", 218},
      {""}, {""},
#line 107 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C4", 98},
      {""}, {""},
#line 776 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H42", 767},
      {""}, {""},
#line 252 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C4", 243},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 694 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CS_CS", 685},
      {""}, {""}, {""}, {""},
#line 79 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H1'", 70},
#line 719 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C5", 710},
      {""}, {""}, {""},
#line 60 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C1'", 51},
#line 225 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H1'", 216},
      {""},
#line 630 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_H3", 621},
      {""},
#line 43 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H1'", 34},
#line 206 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C1'", 197},
#line 774 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H1'", 765},
      {""},
#line 105 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N2", 96},
#line 22 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C1'", 13},
#line 190 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H1'", 181},
#line 757 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C1'", 748},
      {""}, {""},
#line 250 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_N2", 241},
#line 169 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C1'", 160},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 118 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H1'", 109},
#line 534 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_H3", 525},
      {""},
#line 73 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H4'", 64},
      {""},
#line 96 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C1'", 87},
#line 263 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H1'", 254},
#line 541 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HD3", 532},
#line 54 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C4'", 45},
#line 219 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H4'", 210},
      {""},
#line 241 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C1'", 232},
      {""},
#line 37 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H4'", 28},
#line 201 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_C4'", 192},
#line 771 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H4'", 762},
      {""}, {""},
#line 16 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C4'", 7},
#line 184 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H4'", 175},
#line 751 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C4'", 742},
      {""}, {""}, {""},
#line 164 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_C4'", 155},
#line 611 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_H", 602},
#line 798 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C2", 789},
      {""}, {""}, {""},
#line 605 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_C", 596},
      {""}, {""},
#line 112 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H4'", 103},
      {""}, {""}, {""},
#line 539 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HG3", 530},
#line 90 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C4'", 81},
#line 257 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_H4'", 248},
#line 637 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG22", 628},
#line 614 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HA", 605},
      {""}, {""},
#line 236 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_C4'", 227},
      {""},
#line 604 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_CA", 595},
#line 815 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H22", 806},
#line 55 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O4'", 46},
#line 64 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_N3", 55},
      {""},
#line 612 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_H2", 603},
#line 730 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H5'", 721},
      {""},
#line 202 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_O4'", 193},
#line 210 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_N3", 201},
      {""},
#line 708 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C5'", 699},
#line 17 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O4'", 8},
#line 31 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N3", 22},
#line 752 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O4'", 743},
#line 761 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_N3", 752},
      {""}, {""},
#line 165 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_O4'", 156},
#line 178 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_N3", 169},
      {""}, {""}, {""}, {""},
#line 606 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_O", 597},
      {""},
#line 305 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_N", 296},
      {""},
#line 23 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N9", 14},
      {""}, {""},
#line 552 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_H", 543},
#line 91 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O4'", 82},
#line 106 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N3", 97},
#line 170 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_N9", 161},
      {""},
#line 544 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_C", 535},
#line 731 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H5''", 722},
#line 237 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_O4'", 228},
#line 251 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_N3", 242},
      {""}, {""},
#line 549 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CD", 540},
#line 25 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N7", 16},
      {""}, {""},
#line 610 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_CG2", 601},
#line 555 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HA", 546},
#line 97 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N9", 88},
#line 172 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_N7", 163},
      {""},
#line 707 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O5'", 698},
#line 543 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CA", 534},
      {""},
#line 242 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_N9", 233},
      {""}, {""},
#line 553 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_H2", 544},
      {""}, {""}, {""},
#line 809 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H2'", 800},
      {""},
#line 99 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N7", 90},
      {""}, {""},
#line 789 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C2'", 780},
#line 617 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG21", 608},
      {""},
#line 244 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_N7", 235},
      {""}, {""},
#line 548 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CG", 539},
      {""}, {""}, {""},
#line 545 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_O", 536},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 310 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_CB", 301},
      {""}, {""}, {""}, {""},
#line 810 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H2''", 801},
#line 558 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HG2", 549},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 613 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_H3", 604},
      {""}, {""}, {""},
#line 50 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_OP1", 41},
      {""}, {""}, {""},
#line 316 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HB2", 307},
      {""},
#line 197 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_OP1", 188},
      {""}, {""}, {""},
#line 12 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_OP1", 3},
      {""},
#line 746 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_OP1", 737},
      {""}, {""}, {""},
#line 160 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_OP1", 151},
      {""}, {""}, {""}, {""},
#line 738 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H8", 729},
      {""}, {""}, {""}, {""},
#line 717 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C8", 708},
      {""},
#line 157 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H6", 148},
      {""},
#line 86 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_OP1", 77},
      {""}, {""},
#line 143 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C6", 134},
      {""},
#line 377 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_H", 368},
#line 232 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_OP1", 223},
      {""}, {""}, {""},
#line 367 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_C", 358},
      {""}, {""},
#line 808 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_HO3'", 799},
#line 304 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H6", 295},
      {""},
#line 768 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_HOP3", 759},
      {""},
#line 554 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_H3", 545},
#line 288 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C6", 279},
      {""},
#line 380 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HA", 371},
#line 807 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H3'", 798},
      {""}, {""}, {""},
#line 366 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CA", 357},
#line 787 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C3'", 778},
#line 618 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG22", 609},
      {""}, {""},
#line 378 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_H2", 369},
      {""}, {""}, {""},
#line 779 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_P", 770},
#line 387 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HZ", 378},
#line 384 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HD2", 375},
      {""}, {""}, {""},
#line 376 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CZ", 367},
#line 373 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CD2", 364},
      {""},
#line 309 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_OXT", 300},
      {""},
#line 371 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CG", 362},
      {""}, {""}, {""},
#line 368 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_O", 359},
      {""}, {""}, {""},
#line 559 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HG3", 550},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 654 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_H", 645},
      {""},
#line 788 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O3'", 779},
      {""},
#line 317 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HB3", 308},
#line 641 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_C", 632},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 657 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HA", 648},
      {""}, {""}, {""}, {""},
#line 640 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CA", 631},
      {""}, {""}, {""}, {""},
#line 655 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_H2", 646},
#line 665 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HH2", 656},
      {""}, {""}, {""}, {""},
#line 653 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CH2", 644},
      {""}, {""}, {""}, {""},
#line 647 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CD2", 638},
      {""}, {""}, {""},
#line 645 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CG", 636},
#line 781 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_OP2", 772},
      {""}, {""},
#line 642 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_O", 633},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 663 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HZ2", 654},
      {""}, {""}, {""},
#line 379 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_H3", 370},
#line 651 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CZ2", 642},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 140 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C4", 131},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 284 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C4", 275},
      {""}, {""},
#line 794 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C5", 785},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 141 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O4", 132},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 154 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H1'", 145},
#line 656 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_H3", 647},
      {""}, {""}, {""},
#line 135 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C1'", 126},
      {""}, {""},
#line 285 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_O4", 276},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 299 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H1'", 290},
#line 782 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_OP3", 773},
#line 802 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_HOP2", 793},
      {""}, {""},
#line 279 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C1'", 270},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 664 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HZ3", 655},
#line 148 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H4'", 139},
      {""}, {""}, {""},
#line 652 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CZ3", 643},
#line 129 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C4'", 120},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 293 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H4'", 284},
      {""}, {""},
#line 804 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H5'", 795},
      {""},
#line 274 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_C4'", 265},
      {""}, {""},
#line 784 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C5'", 775},
      {""}, {""}, {""},
#line 393 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_H", 384},
      {""}, {""}, {""}, {""},
#line 390 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_C", 381},
      {""}, {""}, {""},
#line 517 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_H", 508},
      {""}, {""}, {""}, {""},
#line 510 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_C", 501},
      {""}, {""},
#line 130 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O4'", 121},
#line 139 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_N3", 130},
      {""},
#line 301 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_H71", 292},
#line 389 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_CA", 380},
#line 805 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H5''", 796},
      {""},
#line 720 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C6", 711},
#line 520 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HA", 511},
#line 394 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_H2", 385},
      {""}, {""}, {""},
#line 509 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_CA", 500},
      {""}, {""},
#line 275 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_O4'", 266},
#line 283 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_N3", 274},
#line 518 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_H2", 509},
#line 783 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O5'", 774},
      {""}, {""},
#line 409 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_H", 400},
      {""}, {""},
#line 396 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_HA2", 387},
      {""},
#line 400 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_C", 391},
#line 391 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_O", 382},
      {""}, {""}, {""}, {""},
#line 514 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_CG", 505},
#line 347 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_N", 338},
      {""}, {""},
#line 511 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_O", 502},
#line 412 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HA", 403},
#line 475 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_H", 466},
      {""}, {""}, {""},
#line 399 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CA", 390},
#line 468 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_C", 459},
      {""}, {""},
#line 721 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O6", 712},
#line 410 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_H2", 401},
      {""},
#line 523 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HD21", 514},
      {""}, {""}, {""},
#line 416 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HD2", 407},
#line 478 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HA", 469},
      {""}, {""}, {""},
#line 406 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CD2", 397},
#line 467 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CA", 458},
      {""}, {""},
#line 404 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CG", 395},
      {""},
#line 476 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_H2", 467},
      {""},
#line 401 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_O", 392},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 481 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HG", 472},
#line 474 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CD2", 465},
      {""}, {""}, {""},
#line 472 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CG", 463},
      {""}, {""}, {""},
#line 469 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_O", 460},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 812 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H8", 803},
      {""},
#line 352 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CB", 343},
      {""},
#line 485 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD21", 476},
#line 792 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C8", 783},
      {""}, {""}, {""},
#line 125 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_OP1", 116},
#line 739 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H1", 730},
#line 395 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_H3", 386},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 519 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_H3", 510},
      {""}, {""},
#line 361 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HB2", 352},
      {""},
#line 270 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_OP1", 261},
      {""},
#line 397 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_HA3", 388},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 740 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H21", 731},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 726 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C4", 717},
#line 497 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_H", 488},
#line 411 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_H3", 402},
      {""},
#line 524 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HD22", 515},
#line 356 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_OE2", 347},
#line 490 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_C", 481},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 500 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HA", 491},
      {""},
#line 477 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_H3", 468},
      {""}, {""},
#line 489 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CA", 480},
#line 705 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O1A", 696},
#line 585 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH11", 576},
      {""}, {""},
#line 498 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_H2", 489},
      {""}, {""}, {""}, {""},
#line 724 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N2", 715},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 562 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_N", 553},
#line 494 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CG", 485},
#line 696 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O1G", 687},
      {""},
#line 351 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_OXT", 342},
#line 491 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_O", 482},
      {""},
#line 737 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H1'", 728},
      {""}, {""},
#line 486 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD22", 477},
      {""},
#line 715 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C1'", 706},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 503 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HG2", 494},
      {""}, {""}, {""}, {""},
#line 573 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_NH2", 564},
      {""},
#line 362 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HB3", 353},
#line 332 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_N", 323},
      {""}, {""}, {""}, {""}, {""},
#line 728 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HOG3", 719},
#line 339 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_OD1", 330},
      {""}, {""},
#line 732 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H4'", 723},
#line 584 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HE", 575},
      {""}, {""}, {""},
#line 709 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C4'", 700},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 567 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CB", 558},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 586 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH12", 577},
      {""}, {""},
#line 499 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_H3", 490},
#line 578 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HB2", 569},
      {""},
#line 45 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H61", 36},
#line 710 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O4'", 701},
#line 725 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N3", 716},
      {""}, {""}, {""},
#line 192 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_H61", 183},
#line 337 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_CB", 328},
#line 702 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2B", 693},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 716 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N9", 707},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 345 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_HB2", 336},
      {""}, {""}, {""},
#line 718 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N7", 709},
#line 504 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HG3", 495},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 28 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N6", 19},
      {""}, {""}, {""}, {""}, {""},
#line 175 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_N6", 166},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 325 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_H", 316},
      {""}, {""},
#line 566 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_OXT", 557},
      {""},
#line 320 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_C", 311},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 328 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HA", 319},
      {""}, {""}, {""}, {""},
#line 319 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_CA", 310},
      {""}, {""}, {""}, {""},
#line 326 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_H2", 317},
      {""},
#line 579 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HB3", 570},
      {""}, {""}, {""}, {""},
#line 336 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_OXT", 327},
      {""}, {""},
#line 331 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HG", 322},
      {""},
#line 699 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3B", 690},
#line 729 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HOB2", 720},
#line 626 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CG1", 617},
#line 795 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C6", 786},
      {""},
#line 620 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_N", 611},
      {""},
#line 321 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_O", 312},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 346 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_HB3", 337},
#line 80 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H41", 71},
      {""},
#line 633 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG11", 624},
      {""}, {""}, {""},
#line 226 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_H41", 217},
#line 525 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_N", 516},
      {""}, {""}, {""},
#line 61 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_N1", 52},
#line 775 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H41", 766},
      {""}, {""}, {""}, {""},
#line 207 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_N1", 198},
      {""}, {""}, {""},
#line 29 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N1", 20},
#line 796 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O6", 787},
#line 758 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_N1", 749},
      {""}, {""}, {""},
#line 176 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DA_N1", 167},
      {""}, {""}, {""}, {""}, {""},
#line 700 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_PB", 691},
      {""},
#line 638 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG23", 629},
      {""}, {""}, {""}, {""},
#line 632 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HB", 623},
#line 103 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N1", 94},
      {""}, {""},
#line 66 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_N4", 57},
#line 625 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CB", 616},
      {""},
#line 248 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DG_N1", 239},
      {""}, {""},
#line 212 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DC_N4", 203},
      {""}, {""},
#line 451 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_H", 442},
      {""}, {""},
#line 763 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_N4", 754},
      {""},
#line 443 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_C", 434},
      {""}, {""}, {""},
#line 327 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_H3", 318},
      {""},
#line 448 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CD", 439},
      {""}, {""}, {""},
#line 530 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CB", 521},
#line 454 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HA", 445},
      {""}, {""}, {""}, {""},
#line 442 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CA", 433},
      {""}, {""}, {""},
#line 813 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H1", 804},
#line 452 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_H2", 443},
      {""}, {""}, {""}, {""}, {""},
#line 459 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HD2", 450},
      {""}, {""}, {""},
#line 536 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HB2", 527},
      {""}, {""}, {""}, {""},
#line 447 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CG", 438},
      {""}, {""},
#line 634 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG12", 625},
#line 444 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_O", 435},
      {""}, {""}, {""}, {""}, {""},
#line 814 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H21", 805},
      {""}, {""}, {""}, {""}, {""},
#line 464 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HZ2", 455},
      {""}, {""}, {""}, {""},
#line 457 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HG2", 448},
#line 801 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C4", 792},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 624 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_OXT", 615},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 616 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG1", 607},
      {""}, {""}, {""},
#line 799 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N2", 790},
      {""}, {""}, {""},
#line 603 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_N", 594},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 529 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_OXT", 520},
      {""}, {""}, {""}, {""},
#line 811 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H1'", 802},
      {""}, {""}, {""}, {""},
#line 790 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C1'", 781},
      {""}, {""}, {""}, {""},
#line 453 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_H3", 444},
      {""}, {""}, {""}, {""}, {""},
#line 460 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HD3", 451},
      {""}, {""}, {""},
#line 537 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HB3", 528},
      {""}, {""}, {""}, {""},
#line 609 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_OG1", 600},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 806 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H4'", 797},
      {""}, {""}, {""}, {""},
#line 785 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C4'", 776},
#line 619 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG23", 610},
#line 542 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_N", 533},
#line 465 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HZ3", 456},
      {""}, {""},
#line 615 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HB", 606},
      {""},
#line 458 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HG3", 449},
#line 315 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HB1", 306},
      {""},
#line 608 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_CB", 599},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 786 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O4'", 777},
#line 800 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N3", 791},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 495 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_SD", 486},
#line 428 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_H", 419},
      {""}, {""}, {""},
#line 791 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N9", 782},
#line 421 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_C", 412},
      {""}, {""}, {""}, {""}, {""},
#line 547 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CB", 538},
      {""}, {""}, {""}, {""},
#line 431 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HA", 422},
      {""}, {""},
#line 793 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N7", 784},
#line 383 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HD1", 374},
#line 420 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CA", 411},
      {""},
#line 596 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_H", 587},
      {""},
#line 372 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CD1", 363},
#line 429 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_H2", 420},
      {""},
#line 591 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_C", 582},
      {""}, {""}, {""},
#line 556 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HB2", 547},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 599 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HA", 590},
      {""}, {""}, {""},
#line 560 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HE21", 551},
#line 590 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_CA", 581},
#line 422 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_O", 413},
      {""}, {""}, {""},
#line 597 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_H2", 588},
#line 607 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_OXT", 598},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 365 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_N", 356},
#line 602 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HG", 593},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 426 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CG2", 417},
#line 592 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_O", 583},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 660 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HD1", 651},
      {""}, {""}, {""}, {""},
#line 646 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CD1", 637},
      {""}, {""},
#line 435 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG21", 426},
      {""},
#line 780 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_OP1", 771},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 546 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_OXT", 537},
      {""},
#line 595 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_OG", 586},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 639 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_N", 630},
#line 370 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CB", 361},
      {""},
#line 430 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_H3", 421},
      {""}, {""},
#line 803 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_HOP3", 794},
#line 386 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HE2", 377},
      {""},
#line 557 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HB3", 548},
      {""}, {""},
#line 375 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CE2", 366},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 561 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HE22", 552},
      {""},
#line 381 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HB2", 372},
      {""}, {""}, {""},
#line 598 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_H3", 589},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 136 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_N1", 127},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 280 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"DT_N1", 271},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 644 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CB", 635},
      {""}, {""}, {""},
#line 436 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG22", 427},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 649 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CE2", 640},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 658 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HB2", 649},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 369 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_OXT", 360},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 324 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_SG", 315},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 382 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HB3", 373},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 679 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_H", 670},
#line 689 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HH", 680},
      {""}, {""}, {""},
#line 668 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_C", 659},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 682 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HA", 673},
      {""}, {""}, {""}, {""},
#line 667 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CA", 658},
      {""},
#line 643 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_OXT", 634},
      {""}, {""},
#line 680 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_H2", 671},
      {""}, {""}, {""}, {""}, {""},
#line 686 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HD2", 677},
#line 662 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HE3", 653},
      {""}, {""},
#line 677 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CZ", 668},
#line 674 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CD2", 665},
#line 650 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CE3", 641},
      {""}, {""},
#line 672 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CG", 663},
      {""}, {""}, {""},
#line 669 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_O", 660},
#line 678 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_OH", 669},
      {""},
#line 659 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HB3", 650},
      {""}, {""}, {""},
#line 388 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_N", 379},
#line 415 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HD1", 406},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 508 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_N", 499},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 515 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_OD1", 506},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 473 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CD1", 464},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 398 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_N", 389},
      {""},
#line 516 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_ND2", 507},
      {""}, {""},
#line 482 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD11", 473},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 466 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_N", 457},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 681 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_H3", 672},
#line 513 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_CB", 504},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 487 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD23", 478},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 521 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HB2", 512},
      {""},
#line 355 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_OE1", 346},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 403 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CB", 394},
      {""}, {""}, {""}, {""}, {""},
#line 418 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HE2", 409},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 471 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CB", 462},
      {""}, {""},
#line 722 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N1", 713},
#line 413 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HB2", 404},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 479 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HB2", 470},
#line 483 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD12", 474},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 392 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_OXT", 383},
      {""}, {""}, {""},
#line 572 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_NH1", 563},
      {""}, {""},
#line 488 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_N", 479},
      {""},
#line 512 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_OXT", 503},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 522 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HB3", 513},
      {""}, {""}, {""}, {""},
#line 402 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_OXT", 393},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 496 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CE", 487},
      {""}, {""},
#line 470 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_OXT", 461},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 414 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HB3", 405},
      {""}, {""}, {""},
#line 493 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CB", 484},
#line 701 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O1B", 692},
      {""}, {""}, {""}, {""},
#line 506 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HE2", 497},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 480 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HB3", 471},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 570 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_NE", 561},
#line 501 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HB2", 492},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 492 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_OXT", 483},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 507 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HE3", 498},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 502 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HB3", 493},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 318 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_N", 309},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 635 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG13", 626},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 323 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_CB", 314},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 329 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HB2", 320},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 463 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HZ1", 454},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 441 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_N", 432},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 797 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N1", 788},
      {""}, {""}, {""}, {""}, {""},
#line 450 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_NZ", 441},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 322 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_OXT", 313},
      {""}, {""}, {""}, {""}, {""},
#line 449 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CE", 440},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 446 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CB", 437},
      {""}, {""}, {""},
#line 330 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HB3", 321},
      {""},
#line 461 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HE2", 452},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 455 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HB2", 446},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 445 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_OXT", 436},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 462 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HE3", 453},
      {""}, {""}, {""}, {""}, {""},
#line 427 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CD1", 418},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 456 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HB3", 447},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 438 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HD11", 429},
      {""}, {""}, {""},
#line 550 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_OE1", 541},
      {""}, {""}, {""}, {""},
#line 425 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CG1", 416},
      {""}, {""},
#line 419 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_N", 410},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 551 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_NE2", 542},
      {""}, {""}, {""}, {""}, {""},
#line 589 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_N", 580},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 437 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG23", 428},
      {""}, {""}, {""},
#line 385 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HE1", 376},
#line 432 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HB", 423},
      {""}, {""}, {""},
#line 374 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CE1", 365},
#line 424 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CB", 415},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 439 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HD12", 430},
#line 594 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_CB", 585},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 600 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HB2", 591},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 433 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG12", 424},
      {""},
#line 661 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HE1", 652},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 423 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_OXT", 414},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 593 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_OXT", 584},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 601 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HB3", 592},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 685 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HD1", 676},
      {""}, {""}, {""}, {""},
#line 673 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CD1", 664},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 666 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_N", 657},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 405 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_ND1", 396},
      {""}, {""}, {""}, {""}, {""},
#line 484 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD13", 475},
      {""},
#line 671 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CB", 662},
      {""}, {""}, {""}, {""}, {""},
#line 688 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HE2", 679},
      {""}, {""}, {""}, {""},
#line 676 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CE2", 667},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 683 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HB2", 674},
      {""}, {""}, {""}, {""}, {""},
#line 417 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HE1", 408},
      {""}, {""}, {""}, {""},
#line 407 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CE1", 398},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 670 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_OXT", 661},
      {""}, {""}, {""}, {""}, {""},
#line 408 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_NE2", 399},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 684 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HB3", 675},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 505 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HE1", 496},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 440 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HD13", 431},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 434 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG13", 425},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 648 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_NE1", 639},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 687 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HE1", 678},
      {""}, {""}, {""}, {""},
#line 675 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CE1", 666}
    };

  if (len <= ATOMMAX_WORD_LENGTH && len >= ATOMMIN_WORD_LENGTH)
    {
      register unsigned int key = _hash_atom (str, len);

      if (key <= ATOMMAX_HASH_VALUE)
        {
          register const char *s = wordlist[key].name;

          if (*str == *s && !strcmp (str + 1, s + 1))
            return &wordlist[key];
        }
    }
  return 0;
}
