/* ANSI-C code produced by gperf version 3.1 */
/* Command-line: /usr/bin/gperf /home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf  */
/* Computed positions: -k'1-2,$' */

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

#line 5 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"

#include "../codegen/lookup.h"
#line 8 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
struct _LOOKUP;

#define RESIDUETOTAL_KEYWORDS 77
#define RESIDUEMIN_WORD_LENGTH 1
#define RESIDUEMAX_WORD_LENGTH 4
#define RESIDUEMIN_HASH_VALUE 1
#define RESIDUEMAX_HASH_VALUE 278
/* maximum key range = 278, duplicates = 0 */

#ifdef __GNUC__
__inline
#else
#ifdef __cplusplus
inline
#endif
#endif
static unsigned int
_hash_residue (register const char *str, register size_t len)
{
  static unsigned short asso_values[] =
    {
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279,   2,
        7,  60,  85, 105,  60,  45, 105, 279, 279, 279,
      279, 279, 279, 279, 279,  10,   0,  15,  10, 105,
       50,   5,  15,  45,   2,   2, 105,  85,   0,   0,
       25,  50, 110,  60,  10,  35, 105, 279,   0,  90,
       40, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279, 279, 279, 279,
      279, 279, 279, 279, 279, 279, 279
    };
  register unsigned int hval = len;

  switch (hval)
    {
      default:
        hval += asso_values[(unsigned char)str[1]+1];
      /*FALLTHROUGH*/
      case 1:
        hval += asso_values[(unsigned char)str[0]];
        break;
    }
  return hval + asso_values[(unsigned char)str[len - 1]];
}

struct _LOOKUP *
_lookup_residue (register const char *str, register size_t len)
{
  static struct _LOOKUP wordlist[] =
    {
      {""},
#line 18 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"N", 8},
      {""}, {""}, {""},
#line 69 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"K", 59},
      {""}, {""},
#line 20 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"OMG", 10},
      {""},
#line 24 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"1MG", 14},
#line 13 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"G", 3},
#line 71 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"NA", 61},
#line 74 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GNG", 64},
      {""},
#line 26 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"2MG", 16},
#line 77 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X1MG", 14},
      {""},
#line 19 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"OMC", 9},
      {""},
#line 25 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"2MA", 15},
#line 10 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"A", 0},
#line 32 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DA", 22},
#line 38 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ASN", 28},
      {""}, {""}, {""}, {""},
#line 40 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CSO", 30},
      {""}, {""},
#line 11 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"C", 1},
#line 34 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DG", 24},
#line 73 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ACT", 63},
      {""}, {""}, {""},
#line 33 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DC", 23},
#line 21 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"OMU", 11},
      {""},
#line 64 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"UNK", 54},
      {""},
#line 72 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ZN", 62},
#line 12 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CCC", 2},
      {""}, {""}, {""}, {""},
#line 39 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ASP", 29},
      {""}, {""},
#line 86 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X6O1", 66},
      {""},
#line 31 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"7MG", 21},
      {""}, {""}, {""},
#line 35 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DT", 25},
#line 67 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"HOH", 57},
      {""}, {""}, {""}, {""},
#line 61 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"TPO", 51},
      {""}, {""}, {""}, {""},
#line 75 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GTP", 65},
#line 79 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X2MG", 16},
      {""},
#line 23 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"U", 13},
      {""},
#line 22 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"PSU", 12},
#line 78 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X2MA", 15},
      {""}, {""}, {""},
#line 37 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ARG", 27},
#line 81 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X5MC", 18},
#line 45 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"HIS", 35},
      {""}, {""},
#line 46 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"HYP", 36},
      {""}, {""}, {""},
#line 68 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CS", 58},
#line 56 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"PRO", 46},
#line 83 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X6MZ", 20},
#line 76 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"6O1", 66},
#line 16 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"I", 6},
      {""},
#line 42 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GLN", 32},
      {""}, {""}, {""}, {""},
#line 62 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"TRP", 52},
#line 82 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X5MU", 19},
      {""}, {""}, {""},
#line 30 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"6MZ", 20},
      {""}, {""}, {""},
#line 70 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MG", 60},
#line 36 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ALA", 26},
      {""}, {""}, {""}, {""},
#line 15 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"H2U", 5},
#line 84 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X7MG", 21},
      {""}, {""}, {""},
#line 41 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CYS", 31},
      {""}, {""}, {""}, {""},
#line 28 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"5MC", 18},
      {""}, {""}, {""}, {""},
#line 43 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GLU", 33},
      {""}, {""}, {""}, {""},
#line 27 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"4SU", 17},
      {""}, {""}, {""}, {""},
#line 58 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"SEP", 48},
      {""}, {""}, {""}, {""},
#line 29 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"5MU", 19},
#line 80 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X4SU", 17},
      {""}, {""}, {""},
#line 51 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MET", 41},
      {""}, {""}, {""}, {""},
#line 17 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"M2G", 7},
      {""}, {""}, {""}, {""},
#line 53 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MS6", 43},
      {""}, {""}, {""}, {""},
#line 63 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"TYR", 53},
      {""}, {""}, {""}, {""},
#line 60 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"THR", 50},
      {""}, {""}, {""}, {""},
#line 57 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"PTR", 47},
      {""}, {""}, {""}, {""},
#line 55 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"PHE", 45},
      {""}, {""}, {""}, {""},
#line 44 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GLY", 34},
      {""}, {""}, {""}, {""},
#line 50 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MEQ", 40},
      {""}, {""}, {""}, {""},
#line 48 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"LEU", 38},
#line 85 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"X4D4", 56},
      {""}, {""}, {""},
#line 14 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"G7M", 4},
      {""}, {""}, {""}, {""},
#line 54 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MSE", 44},
      {""}, {""}, {""}, {""},
#line 49 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"LYS", 39},
      {""}, {""}, {""}, {""},
#line 65 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"VAL", 55},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 59 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"SER", 49},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 47 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ILE", 37},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""}, {""},
#line 52 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MLY", 42},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 66 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"4D4", 56}
    };

  if (len <= RESIDUEMAX_WORD_LENGTH && len >= RESIDUEMIN_WORD_LENGTH)
    {
      register unsigned int key = _hash_residue (str, len);

      if (key <= RESIDUEMAX_HASH_VALUE)
        {
          register const char *s = wordlist[key].name;

          if (*str == *s && !strcmp (str + 1, s + 1))
            return &wordlist[key];
        }
    }
  return 0;
}
