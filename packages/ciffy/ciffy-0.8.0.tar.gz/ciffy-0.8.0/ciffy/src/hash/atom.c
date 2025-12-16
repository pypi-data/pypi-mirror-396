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

#define ATOMTOTAL_KEYWORDS 654
#define ATOMMIN_WORD_LENGTH 3
#define ATOMMAX_WORD_LENGTH 8
#define ATOMMIN_HASH_VALUE 4
#define ATOMMAX_HASH_VALUE 5527
/* maximum key range = 5524, duplicates = 0 */

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
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,   30,
         0, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,  805,
         0,   45, 1299, 1714,  425,   75,   10,   40, 5528, 5528,
      5528, 5528, 5528, 5528, 5528,   15,  236,    0,  930,  860,
      5528,   35,    5,  720, 5528, 5528,  605,  890,  280,   55,
       140, 5528,  315,  380,    5, 1015,  555, 5528,   15,  425,
       870, 5528, 5528, 5528, 5528,    0, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528, 5528,
      5528, 5528, 5528, 5528, 5528, 5528, 5528
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
      {""}, {""}, {""}, {""},
#line 62 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C2", 53},
      {""},
#line 222 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C2", 213},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 30 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C2", 21},
      {""}, {""}, {""}, {""},
#line 47 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H2", 38},
      {""}, {""}, {""}, {""},
#line 24 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C8", 15},
      {""}, {""}, {""}, {""},
#line 44 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H8", 35},
#line 58 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C2'", 49},
      {""},
#line 218 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C2'", 209},
      {""},
#line 104 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C2", 95},
#line 76 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H2'", 67},
      {""},
#line 236 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H2'", 227},
      {""}, {""},
#line 122 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H22", 113},
      {""}, {""}, {""},
#line 98 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C8", 89},
#line 20 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C2'", 11},
      {""}, {""}, {""},
#line 119 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H8", 110},
#line 40 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H2'", 31},
      {""}, {""}, {""},
#line 63 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O2", 54},
      {""},
#line 223 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O2", 214},
#line 207 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O2C", 198},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 94 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C2'", 85},
      {""}, {""}, {""}, {""},
#line 115 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H2'", 106},
      {""}, {""}, {""}, {""},
#line 56 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C3'", 47},
      {""},
#line 216 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C3'", 207},
      {""}, {""},
#line 74 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H3'", 65},
      {""},
#line 235 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H3'", 226},
      {""}, {""},
#line 59 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O2'", 50},
      {""},
#line 219 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O2'", 210},
      {""}, {""},
#line 18 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C3'", 9},
#line 77 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HO2'", 68},
      {""}, {""}, {""},
#line 38 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H3'", 29},
      {""}, {""}, {""}, {""},
#line 21 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O2'", 12},
      {""}, {""}, {""}, {""}, {""},
#line 41 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HO2'", 32},
      {""},
#line 229 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_HOC2", 220},
      {""},
#line 92 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C3'", 83},
      {""}, {""}, {""}, {""},
#line 113 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H3'", 104},
      {""}, {""}, {""}, {""},
#line 95 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O2'", 86},
      {""}, {""}, {""}, {""}, {""},
#line 116 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HO2'", 107},
      {""}, {""}, {""},
#line 57 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O3'", 48},
      {""},
#line 217 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O3'", 208},
      {""}, {""}, {""},
#line 75 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HO3'", 66},
      {""},
#line 49 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_P", 40},
      {""},
#line 208 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_P", 199},
#line 205 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_PC", 196},
      {""}, {""}, {""},
#line 19 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O3'", 10},
      {""}, {""}, {""}, {""}, {""},
#line 39 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HO3'", 30},
      {""},
#line 11 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_P", 2},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 93 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O3'", 84},
      {""}, {""}, {""}, {""}, {""},
#line 114 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HO3'", 105},
      {""},
#line 85 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_P", 76},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 186 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C2", 177},
      {""}, {""}, {""}, {""}, {""},
#line 204 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H22", 195},
      {""}, {""}, {""},
#line 180 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C8", 171},
      {""}, {""}, {""},
#line 51 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_OP2", 42},
#line 201 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H8", 192},
#line 210 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_OP2", 201},
      {""}, {""}, {""},
#line 70 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HOP2", 61},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 13 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_OP2", 4},
      {""},
#line 176 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C2'", 167},
      {""}, {""}, {""},
#line 34 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HOP2", 25},
#line 198 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H2'", 189},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 87 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_OP2", 78},
      {""}, {""}, {""}, {""}, {""},
#line 109 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HOP2", 100},
      {""}, {""}, {""},
#line 48 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_OP3", 39},
      {""},
#line 211 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_OP3", 202},
#line 199 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HO2'", 190},
      {""}, {""},
#line 69 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HOP3", 60},
      {""},
#line 230 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_HOP2", 221},
      {""}, {""}, {""},
#line 169 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2A", 160},
      {""}, {""},
#line 10 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_OP3", 1},
      {""},
#line 174 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C3'", 165},
      {""}, {""}, {""},
#line 33 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HOP3", 24},
#line 196 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H3'", 187},
      {""}, {""}, {""}, {""},
#line 177 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2'", 168},
      {""}, {""}, {""}, {""},
#line 160 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2G", 151},
      {""}, {""},
#line 84 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_OP3", 75},
      {""}, {""}, {""}, {""}, {""},
#line 108 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HOP3", 99},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 197 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HO3'", 188},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 166 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3A", 157},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 175 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3'", 166},
      {""},
#line 105 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N2", 96},
      {""}, {""},
#line 161 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3G", 152},
      {""}, {""}, {""}, {""}, {""},
#line 190 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HOG2", 181},
#line 64 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_N3", 55},
#line 482 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_C", 473},
#line 224 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_N3", 215},
      {""}, {""}, {""},
#line 488 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_H", 479},
#line 489 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_H2", 480},
      {""}, {""},
#line 23 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N9", 14},
      {""},
#line 167 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_PA", 158},
      {""}, {""},
#line 31 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N3", 22},
      {""},
#line 481 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_CA", 472},
      {""}, {""}, {""}, {""},
#line 491 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HA", 482},
      {""}, {""}, {""}, {""},
#line 261 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C2", 252},
      {""}, {""},
#line 97 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N9", 88},
      {""},
#line 158 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_PG", 149},
#line 278 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H22", 269},
      {""},
#line 106 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N3", 97},
      {""},
#line 255 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C8", 246},
#line 487 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_CG2", 478},
      {""}, {""},
#line 594 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_C", 585},
#line 275 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H8", 266},
      {""},
#line 494 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG21", 485},
#line 25 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N7", 16},
#line 604 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_H", 595},
#line 605 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_H2", 596},
      {""}, {""}, {""}, {""},
#line 490 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_H3", 481},
      {""},
#line 617 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH21", 608},
      {""},
#line 483 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_O", 474},
#line 593 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CA", 584},
#line 252 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C2'", 243},
      {""}, {""}, {""},
#line 607 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HA", 598},
#line 272 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H2'", 263},
#line 273 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H2''", 264},
#line 99 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N7", 90},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 598 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CG", 589},
#line 484 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_OXT", 475},
      {""}, {""}, {""}, {""},
#line 610 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HG2", 601},
      {""}, {""}, {""}, {""}, {""},
#line 495 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG22", 486},
      {""}, {""},
#line 606 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_H3", 597},
      {""}, {""}, {""},
#line 595 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_O", 586},
      {""}, {""},
#line 618 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH22", 609},
#line 68 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C6", 59},
      {""},
#line 228 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C6", 219},
#line 250 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C3'", 241},
      {""},
#line 83 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H6", 74},
      {""},
#line 241 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H6", 232},
#line 270 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H3'", 261},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 27 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C6", 18},
      {""}, {""},
#line 596 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_OXT", 587},
      {""}, {""},
#line 46 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H62", 37},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 611 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HG3", 602},
      {""}, {""}, {""}, {""}, {""},
#line 271 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_HO3'", 262},
#line 101 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C6", 92},
#line 407 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_C", 398},
#line 187 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N2", 178},
      {""}, {""}, {""},
#line 420 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_H", 411},
#line 421 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_H2", 412},
#line 419 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CH2", 410},
      {""}, {""}, {""}, {""},
#line 431 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HH2", 422},
#line 165 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O2B", 156},
      {""}, {""},
#line 406 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CA", 397},
      {""}, {""}, {""}, {""},
#line 423 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HA", 414},
#line 251 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O3'", 242},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 242 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_P", 233},
      {""}, {""}, {""}, {""}, {""},
#line 411 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CG", 402},
      {""}, {""}, {""}, {""},
#line 179 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N9", 170},
      {""}, {""}, {""}, {""},
#line 188 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N3", 179},
      {""}, {""}, {""},
#line 367 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_C", 358},
#line 422 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_H3", 413},
      {""}, {""},
#line 102 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O6", 93},
#line 408 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_O", 399},
#line 373 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_H2", 364},
      {""},
#line 162 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O3B", 153},
      {""}, {""}, {""}, {""}, {""},
#line 192 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HOB2", 183},
      {""},
#line 366 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CA", 357},
      {""}, {""}, {""}, {""},
#line 375 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HA", 366},
      {""}, {""}, {""},
#line 536 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_C", 527},
#line 181 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N7", 172},
#line 409 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_OXT", 400},
      {""}, {""},
#line 543 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_H", 534},
#line 544 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_H2", 535},
      {""}, {""}, {""}, {""},
#line 371 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CG", 362},
#line 244 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_OP2", 235},
      {""}, {""}, {""},
#line 535 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_CA", 526},
#line 378 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HG2", 369},
      {""}, {""}, {""},
#line 546 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_HA", 537},
#line 163 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_PB", 154},
      {""}, {""}, {""},
#line 374 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_H3", 365},
#line 485 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_CB", 476},
      {""}, {""},
#line 368 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_O", 359},
      {""},
#line 492 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HB", 483},
      {""}, {""}, {""},
#line 540 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_CG", 531},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 545 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_H3", 536},
#line 369 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_OXT", 360},
      {""}, {""},
#line 537 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_O", 528},
      {""},
#line 245 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_OP3", 236},
      {""}, {""}, {""}, {""},
#line 379 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HG3", 370},
#line 265 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_HOP2", 256},
      {""}, {""}, {""},
#line 597 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CB", 588},
      {""}, {""},
#line 480 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_N", 471},
#line 183 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C6", 174},
      {""},
#line 608 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HB2", 599},
      {""}, {""}, {""},
#line 538 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_OXT", 529},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 262 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N2", 253},
      {""}, {""}, {""},
#line 291 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_C", 282},
      {""}, {""}, {""}, {""},
#line 295 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_H", 286},
#line 296 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_H2", 287},
      {""}, {""}, {""},
#line 592 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_N", 583},
      {""}, {""}, {""}, {""}, {""},
#line 290 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_CA", 281},
#line 603 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_NH2", 594},
#line 609 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HB3", 600},
      {""}, {""},
#line 298 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HA", 289},
      {""}, {""}, {""}, {""},
#line 184 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O6", 175},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 254 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N9", 245},
      {""}, {""}, {""},
#line 499 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_C", 490},
#line 263 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N3", 254},
      {""}, {""}, {""},
#line 506 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_H", 497},
#line 507 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_H2", 498},
      {""}, {""}, {""}, {""},
#line 297 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_H3", 288},
      {""}, {""}, {""},
#line 292 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_O", 283},
#line 498 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_CA", 489},
      {""}, {""}, {""}, {""},
#line 509 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HA", 500},
#line 410 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CB", 401},
      {""}, {""}, {""}, {""}, {""},
#line 424 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HB2", 415},
      {""}, {""},
#line 256 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N7", 247},
      {""}, {""}, {""}, {""},
#line 503 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_CG", 494},
#line 293 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_OXT", 284},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 28 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N6", 19},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 508 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_H3", 499},
      {""}, {""}, {""},
#line 500 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_O", 491},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 405 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_N", 396},
      {""}, {""}, {""}, {""},
#line 642 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_C", 633},
      {""},
#line 370 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CB", 361},
#line 425 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HB3", 416},
      {""},
#line 653 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_H", 644},
#line 654 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_H2", 645},
#line 501 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_OXT", 492},
#line 376 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HB2", 367},
      {""}, {""},
#line 663 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HH", 654},
      {""}, {""}, {""}, {""},
#line 641 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CA", 632},
      {""}, {""}, {""}, {""},
#line 656 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HA", 647},
      {""}, {""}, {""}, {""}, {""},
#line 539 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_CB", 530},
      {""}, {""}, {""},
#line 258 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C6", 249},
      {""},
#line 547 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_HB2", 538},
      {""}, {""},
#line 646 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CG", 637},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 365 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_N", 356},
      {""}, {""}, {""}, {""}, {""},
#line 655 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_H3", 646},
      {""},
#line 377 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HB3", 368},
      {""},
#line 643 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_O", 634},
      {""}, {""}, {""}, {""},
#line 454 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_C", 445},
#line 652 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_OH", 643},
      {""}, {""}, {""},
#line 459 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_H", 450},
#line 460 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_H2", 451},
      {""}, {""}, {""},
#line 534 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_N", 525},
      {""}, {""}, {""}, {""}, {""},
#line 453 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_CA", 444},
#line 644 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_OXT", 635},
#line 548 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_HB3", 539},
      {""}, {""},
#line 462 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HA", 453},
      {""}, {""}, {""}, {""},
#line 259 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O6", 250},
      {""}, {""}, {""},
#line 60 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C1'", 51},
      {""},
#line 220 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C1'", 211},
      {""}, {""},
#line 79 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H1'", 70},
      {""},
#line 237 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H1'", 228},
      {""},
#line 120 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H1", 111},
#line 121 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H21", 112},
#line 465 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HG", 456},
      {""}, {""}, {""},
#line 22 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C1'", 13},
      {""}, {""}, {""}, {""},
#line 43 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H1'", 34},
#line 461 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_H3", 452},
      {""}, {""}, {""},
#line 455 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_O", 446},
      {""},
#line 206 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O1C", 197},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 96 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C1'", 87},
      {""},
#line 294 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_CB", 285},
      {""}, {""},
#line 118 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H1'", 109},
      {""}, {""},
#line 300 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HB2", 291},
      {""}, {""}, {""},
#line 456 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_OXT", 447},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 502 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_CB", 493},
      {""}, {""},
#line 289 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_N", 280},
      {""}, {""},
#line 510 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HB2", 501},
      {""},
#line 516 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_C", 507},
      {""}, {""},
#line 301 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HB3", 292},
      {""},
#line 524 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_H", 515},
#line 525 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_H2", 516},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 515 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CA", 506},
      {""}, {""}, {""}, {""},
#line 527 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HA", 518},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 497 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_N", 488},
#line 520 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CG", 511},
      {""}, {""}, {""}, {""}, {""},
#line 530 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HG2", 521},
#line 511 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HB3", 502},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 526 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_H3", 517},
      {""}, {""}, {""},
#line 517 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_O", 508},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 645 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CB", 636},
      {""}, {""}, {""}, {""}, {""},
#line 657 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HB2", 648},
      {""}, {""},
#line 202 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H1", 193},
#line 203 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H21", 194},
      {""}, {""}, {""}, {""},
#line 518 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_OXT", 509},
      {""}, {""},
#line 50 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_OP1", 41},
      {""},
#line 209 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_OP1", 200},
      {""}, {""},
#line 384 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_C", 375},
      {""},
#line 531 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HG3", 522},
      {""}, {""},
#line 394 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_H", 385},
#line 395 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_H2", 386},
      {""}, {""},
#line 137 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C2", 128},
#line 12 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_OP1", 3},
      {""},
#line 178 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C1'", 169},
      {""}, {""}, {""},
#line 383 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CA", 374},
#line 200 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H1'", 191},
      {""}, {""},
#line 640 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_N", 631},
#line 397 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HA", 388},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 658 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HB3", 649},
      {""},
#line 86 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_OP1", 77},
      {""}, {""}, {""}, {""}, {""},
#line 388 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CG", 379},
#line 457 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_CB", 448},
      {""}, {""},
#line 133 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C2'", 124},
      {""}, {""},
#line 463 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HB2", 454},
      {""},
#line 151 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H2'", 142},
      {""}, {""}, {""}, {""}, {""},
#line 396 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_H3", 387},
#line 168 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O1A", 159},
      {""}, {""},
#line 385 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_O", 376},
      {""}, {""}, {""},
#line 155 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H3", 146},
#line 281 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_C", 272},
      {""}, {""}, {""},
#line 138 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O2", 129},
#line 284 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_H", 275},
#line 285 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_H2", 276},
      {""}, {""}, {""}, {""}, {""},
#line 159 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O1G", 150},
      {""}, {""}, {""},
#line 280 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_CA", 271},
#line 386 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_OXT", 377},
      {""},
#line 61 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_N1", 52},
#line 452 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_N", 443},
#line 221 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_N1", 212},
#line 287 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_HA2", 278},
      {""}, {""},
#line 131 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C3'", 122},
      {""}, {""},
#line 464 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_HB3", 455},
      {""},
#line 149 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H3'", 140},
      {""}, {""}, {""},
#line 29 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_N1", 20},
#line 134 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O2'", 125},
      {""}, {""}, {""}, {""},
#line 621 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_C", 612},
#line 152 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HO2'", 143},
      {""}, {""}, {""},
#line 630 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_H", 621},
#line 631 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_H2", 622},
      {""}, {""}, {""}, {""},
#line 286 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_H3", 277},
      {""}, {""},
#line 103 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_N1", 94},
#line 282 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_O", 273},
#line 620 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CA", 611},
      {""}, {""}, {""}, {""},
#line 633 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HA", 624},
      {""}, {""}, {""}, {""}, {""},
#line 288 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_HA3", 279},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 625 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CG", 616},
#line 283 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_OXT", 274},
      {""}, {""},
#line 132 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O3'", 123},
      {""}, {""}, {""}, {""}, {""},
#line 150 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HO3'", 141},
      {""},
#line 124 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_P", 115},
      {""}, {""},
#line 632 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_H3", 623},
#line 519 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CB", 510},
      {""}, {""},
#line 622 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_O", 613},
#line 276 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H1", 267},
#line 277 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H21", 268},
#line 528 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HB2", 519},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 493 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG1", 484},
      {""}, {""},
#line 304 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_C", 295},
      {""}, {""}, {""}, {""},
#line 310 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_H", 301},
#line 311 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_H2", 302},
#line 623 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_OXT", 614},
#line 615 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH11", 606},
      {""}, {""}, {""},
#line 253 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C1'", 244},
      {""}, {""}, {""},
#line 303 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CA", 294},
#line 274 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H1'", 265},
      {""}, {""}, {""},
#line 313 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HA", 304},
      {""}, {""}, {""},
#line 514 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_N", 505},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 529 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HB3", 520},
      {""},
#line 126 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_OP2", 117},
      {""},
#line 309 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CG2", 300},
      {""}, {""}, {""},
#line 145 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HOP2", 136},
      {""},
#line 318 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG21", 309},
      {""}, {""},
#line 458 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CYS_SG", 449},
#line 486 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_OG1", 477},
      {""}, {""}, {""},
#line 312 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_H3", 303},
      {""},
#line 616 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HH12", 607},
      {""},
#line 305 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_O", 296},
#line 614 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HE", 605},
      {""}, {""}, {""}, {""},
#line 601 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CZ", 592},
      {""}, {""}, {""}, {""}, {""},
#line 387 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CB", 378},
      {""}, {""}, {""}, {""}, {""},
#line 398 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HB2", 389},
      {""},
#line 45 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H61", 36},
      {""},
#line 306 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_OXT", 297},
      {""}, {""},
#line 123 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_OP3", 114},
      {""}, {""}, {""}, {""}, {""},
#line 144 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HOP3", 135},
      {""},
#line 319 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG22", 310},
      {""}, {""},
#line 185 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_N1", 176},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 164 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O1B", 155},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 382 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_N", 373},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 399 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HB3", 390},
      {""}, {""},
#line 599 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_CD", 590},
      {""},
#line 65 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C4", 56},
      {""},
#line 225 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C4", 216},
      {""},
#line 612 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HD2", 603},
      {""},
#line 81 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H42", 72},
      {""},
#line 239 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H42", 230},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 32 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C4", 23},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 415 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CE2", 406},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 54 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C4'", 45},
      {""},
#line 214 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C4'", 205},
#line 417 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CZ2", 408},
#line 107 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C4", 98},
#line 73 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H4'", 64},
      {""},
#line 234 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H4'", 225},
#line 429 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HZ2", 420},
      {""},
#line 139 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_N3", 130},
      {""}, {""},
#line 624 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CB", 615},
      {""},
#line 16 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C4'", 7},
#line 279 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLY_N", 270},
      {""},
#line 613 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_HD3", 604},
#line 634 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HB2", 625},
#line 37 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H4'", 28},
      {""}, {""},
#line 243 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_OP1", 234},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 90 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C4'", 81},
      {""}, {""},
#line 416 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CE3", 407},
      {""},
#line 112 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H4'", 103},
      {""}, {""},
#line 428 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HE3", 419},
      {""}, {""}, {""}, {""},
#line 418 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CZ3", 409},
      {""}, {""}, {""}, {""},
#line 430 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HZ3", 421},
      {""},
#line 55 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O4'", 46},
#line 619 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_N", 610},
#line 215 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O4'", 206},
      {""}, {""}, {""}, {""}, {""},
#line 413 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CD2", 404},
#line 635 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HB3", 626},
      {""}, {""}, {""}, {""}, {""},
#line 17 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O4'", 8},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 569 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_C", 560},
      {""},
#line 307 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CB", 298},
      {""}, {""},
#line 577 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_H", 568},
#line 578 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_H2", 569},
#line 314 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HB", 305},
      {""},
#line 91 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O4'", 82},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 568 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CA", 559},
      {""}, {""}, {""}, {""},
#line 580 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HA", 571},
      {""}, {""}, {""}, {""},
#line 260 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_N1", 251},
      {""}, {""},
#line 143 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C6", 134},
      {""},
#line 372 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_CD", 363},
      {""}, {""},
#line 157 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H6", 148},
      {""},
#line 573 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CG", 564},
#line 380 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HD2", 371},
      {""}, {""}, {""}, {""},
#line 583 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HG2", 574},
      {""}, {""},
#line 302 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_N", 293},
      {""},
#line 602 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_NH1", 593},
      {""}, {""}, {""},
#line 579 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_H3", 570},
      {""}, {""}, {""},
#line 570 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_O", 561},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 189 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C4", 180},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 571 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_OXT", 562},
      {""}, {""}, {""}, {""},
#line 381 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PRO_HD3", 372},
      {""}, {""}, {""}, {""},
#line 584 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HG3", 575},
      {""}, {""}, {""}, {""},
#line 231 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_HOP3", 222},
      {""}, {""}, {""},
#line 600 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ARG_NE", 591},
      {""}, {""}, {""}, {""},
#line 172 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C4'", 163},
      {""}, {""}, {""}, {""},
#line 195 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H4'", 186},
      {""}, {""}, {""}, {""}, {""},
#line 542 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_OD2", 533},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 468 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_C", 459},
      {""}, {""}, {""}, {""},
#line 473 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_H", 464},
#line 474 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_H2", 465},
      {""}, {""}, {""}, {""},
#line 173 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O4'", 164},
      {""}, {""}, {""}, {""},
#line 467 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_CA", 458},
      {""}, {""}, {""}, {""},
#line 476 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HA", 467},
#line 191 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_HOG3", 182},
#line 66 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_N4", 57},
      {""},
#line 226 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_N4", 217},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 479 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HG", 470},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 475 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_H3", 466},
#line 650 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CE2", 641},
      {""}, {""},
#line 469 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_O", 460},
      {""},
#line 662 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HE2", 653},
#line 512 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HD21", 503},
      {""}, {""},
#line 651 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CZ", 642},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 470 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_OXT", 461},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 472 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_OG", 463},
#line 572 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CB", 563},
      {""}, {""},
#line 264 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C4", 255},
      {""}, {""},
#line 581 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HB2", 572},
      {""},
#line 551 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_C", 542},
      {""}, {""},
#line 513 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_HD22", 504},
      {""},
#line 559 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_H", 550},
#line 560 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_H2", 551},
      {""}, {""}, {""}, {""}, {""},
#line 496 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"THR_HG23", 487},
      {""}, {""}, {""},
#line 550 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CA", 541},
      {""}, {""}, {""}, {""},
#line 562 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HA", 553},
#line 648 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CD2", 639},
      {""}, {""}, {""},
#line 248 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C4'", 239},
#line 660 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HD2", 651},
#line 299 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ALA_HB1", 290},
      {""}, {""},
#line 269 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H4'", 260},
      {""}, {""}, {""},
#line 567 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_N", 558},
#line 555 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CG", 546},
      {""}, {""}, {""}, {""}, {""},
#line 565 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HG2", 556},
#line 582 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HB3", 573},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 561 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_H3", 552},
      {""}, {""}, {""},
#line 552 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_O", 543},
      {""}, {""},
#line 67 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C5", 58},
      {""},
#line 227 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C5", 218},
      {""}, {""},
#line 82 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H5", 73},
      {""},
#line 240 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H5", 231},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 26 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C5", 17},
      {""}, {""}, {""},
#line 553 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_OXT", 544},
      {""}, {""}, {""},
#line 249 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O4'", 240},
      {""}, {""}, {""}, {""}, {""},
#line 566 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HG3", 557},
      {""},
#line 53 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_C5'", 44},
      {""},
#line 213 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_C5'", 204},
      {""},
#line 100 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C5", 91},
#line 71 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H5'", 62},
      {""},
#line 232 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H5'", 223},
#line 233 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H5''", 224},
      {""}, {""},
#line 434 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_C", 425},
      {""}, {""}, {""},
#line 15 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_C5'", 6},
#line 441 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_H", 432},
#line 442 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_H2", 433},
      {""}, {""},
#line 35 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H5'", 26},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 433 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CA", 424},
      {""}, {""}, {""}, {""},
#line 444 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HA", 435},
      {""}, {""},
#line 89 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_C5'", 80},
#line 72 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H5''", 63},
      {""}, {""}, {""},
#line 111 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H5'", 102},
      {""}, {""}, {""},
#line 532 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HE21", 523},
      {""}, {""},
#line 438 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CG", 429},
#line 471 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_CB", 462},
      {""}, {""},
#line 36 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_H5''", 27},
      {""},
#line 447 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HG2", 438},
#line 477 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HB2", 468},
#line 52 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_O5'", 43},
      {""},
#line 212 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_O5'", 203},
      {""}, {""}, {""},
#line 78 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_HO5'", 69},
#line 443 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_H3", 434},
      {""}, {""}, {""},
#line 435 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_O", 426},
      {""}, {""}, {""},
#line 14 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_O5'", 5},
#line 110 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_H5''", 101},
      {""}, {""}, {""}, {""},
#line 42 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"A_HO5'", 33},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 436 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_OXT", 427},
#line 533 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_HE22", 524},
#line 88 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_O5'", 79},
#line 466 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_N", 457},
      {""}, {""}, {""}, {""},
#line 117 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"G_HO5'", 108},
      {""},
#line 448 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HG3", 439},
#line 478 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"SER_HB3", 469},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 135 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C1'", 126},
#line 521 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_CD", 512},
#line 266 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_HOP3", 257},
      {""}, {""},
#line 154 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H1'", 145},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 392 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CE2", 383},
      {""}, {""}, {""}, {""},
#line 403 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HE2", 394},
      {""}, {""}, {""},
#line 393 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CZ", 384},
      {""}, {""}, {""}, {""},
#line 404 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HZ", 395},
      {""}, {""}, {""}, {""}, {""},
#line 505 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_ND2", 496},
      {""}, {""}, {""}, {""},
#line 554 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CB", 545},
      {""}, {""},
#line 182 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C5", 173},
      {""}, {""},
#line 563 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HB2", 554},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 171 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_C5'", 162},
      {""}, {""}, {""}, {""},
#line 193 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H5'", 184},
#line 194 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_H5''", 185},
      {""}, {""},
#line 549 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_N", 540},
      {""},
#line 390 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CD2", 381},
      {""}, {""}, {""}, {""},
#line 401 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HD2", 392},
#line 564 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_HB3", 555},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 639 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HE2", 630},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 170 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GTP_O5'", 161},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 437 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CB", 428},
      {""}, {""}, {""}, {""}, {""},
#line 445 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HB2", 436},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 125 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_OP1", 116},
      {""},
#line 308 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_CG1", 299},
      {""}, {""}, {""}, {""}, {""},
#line 315 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG11", 306},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 432 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_N", 423},
      {""},
#line 627 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CD2", 618},
      {""}, {""}, {""}, {""},
#line 637 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HD2", 628},
#line 446 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HB3", 437},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 523 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_NE2", 514},
      {""}, {""},
#line 257 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C5", 248},
      {""}, {""},
#line 316 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG12", 307},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 247 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_C5'", 238},
      {""}, {""},
#line 136 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_N1", 127},
      {""},
#line 267 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H5'", 258},
#line 268 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_H5''", 259},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 80 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"C_H41", 71},
      {""},
#line 238 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"CCC_H41", 229},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 427 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HE1", 418},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 246 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GNG_O5'", 237},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 345 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_C", 336},
      {""}, {""}, {""}, {""},
#line 352 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_H", 343},
#line 353 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_H2", 344},
      {""}, {""}, {""}, {""}, {""},
#line 412 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_CD1", 403},
      {""}, {""}, {""},
#line 344 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CA", 335},
#line 426 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_HD1", 417},
      {""}, {""}, {""},
#line 355 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HA", 346},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 350 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CG2", 341},
      {""}, {""}, {""}, {""}, {""},
#line 359 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG21", 350},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 354 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_H3", 345},
      {""}, {""}, {""},
#line 346 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_O", 337},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 629 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_NE2", 620},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 347 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_OXT", 338},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 575 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CE", 566},
      {""},
#line 360 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG22", 351},
      {""}, {""}, {""},
#line 587 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HE2", 578},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 590 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HZ2", 581},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 140 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C4", 131},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 588 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HE3", 579},
      {""}, {""}, {""}, {""},
#line 541 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASP_OD1", 532},
      {""}, {""}, {""}, {""},
#line 591 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HZ3", 582},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 574 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_CD", 565},
      {""}, {""},
#line 129 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C4'", 120},
      {""}, {""},
#line 585 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HD2", 576},
      {""},
#line 148 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H4'", 139},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 141 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O4", 132},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 586 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HD3", 577},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 130 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O4'", 121},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 414 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TRP_NE1", 405},
      {""}, {""}, {""}, {""},
#line 649 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CE1", 640},
      {""}, {""}, {""}, {""},
#line 661 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HE1", 652},
      {""}, {""}, {""}, {""},
#line 348 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CB", 339},
      {""}, {""}, {""}, {""},
#line 356 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HB", 347},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 343 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_N", 334},
      {""},
#line 504 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ASN_OD1", 495},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 323 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_C", 314},
      {""},
#line 647 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_CD1", 638},
      {""}, {""},
#line 330 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_H", 321},
#line 331 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_H2", 322},
#line 659 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"TYR_HD1", 650},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 322 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CA", 313},
      {""}, {""}, {""}, {""},
#line 333 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HA", 324},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 327 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CG", 318},
#line 320 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG23", 311},
      {""}, {""}, {""},
#line 336 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HG", 327},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 332 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_H3", 323},
      {""}, {""}, {""},
#line 324 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_O", 315},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 325 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_OXT", 316},
      {""}, {""}, {""},
#line 576 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_NZ", 567},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 558 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_OE2", 549},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 556 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_CD", 547},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 440 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_CE", 431},
      {""}, {""}, {""}, {""}, {""},
#line 450 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HE2", 441},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""},
#line 522 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLN_OE1", 513},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 451 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HE3", 442},
      {""}, {""}, {""}, {""},
#line 391 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CE1", 382},
      {""}, {""}, {""}, {""},
#line 402 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HE1", 393},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""},
#line 326 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CB", 317},
      {""}, {""}, {""}, {""}, {""},
#line 334 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HB2", 325},
      {""}, {""}, {""}, {""},
#line 142 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C5", 133},
      {""}, {""}, {""}, {""},
#line 156 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H5", 147},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 389 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_CD1", 380},
      {""}, {""}, {""}, {""},
#line 400 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"PHE_HD1", 391},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 128 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_C5'", 119},
#line 321 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_N", 312},
      {""}, {""}, {""},
#line 146 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H5'", 137},
      {""}, {""}, {""},
#line 335 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HB3", 326},
      {""}, {""}, {""},
#line 628 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_CE1", 619},
      {""}, {""}, {""}, {""},
#line 638 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HE1", 629},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 147 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_H5''", 138},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 127 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_O5'", 118},
      {""}, {""}, {""}, {""}, {""},
#line 153 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"U_HO5'", 144},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 636 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_HD1", 627},
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
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 349 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CG1", 340},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 439 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_SD", 430},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 357 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG12", 348},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""},
#line 589 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LYS_HZ1", 580},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""},
#line 626 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"HIS_ND1", 617},
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
      {""},
#line 317 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"VAL_HG13", 308},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 557 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"GLU_OE1", 548},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 329 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CD2", 320},
      {""}, {""}, {""}, {""}, {""},
#line 340 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD21", 331},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 449 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"MET_HE1", 440},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 341 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD22", 332},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 361 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG23", 352},
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
      {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 351 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_CD1", 342},
      {""}, {""}, {""}, {""}, {""},
#line 362 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HD11", 353},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 363 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HD12", 354},
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
#line 328 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_CD1", 319},
      {""}, {""}, {""}, {""}, {""},
#line 337 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD11", 328},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 338 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD12", 329},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 358 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HG13", 349},
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
      {""}, {""}, {""}, {""}, {""}, {""},
#line 342 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD23", 333},
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
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 364 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"ILE_HD13", 355},
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
      {""}, {""}, {""}, {""}, {""}, {""},
#line 339 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/atom.gperf"
      {"LEU_HD13", 330}
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
