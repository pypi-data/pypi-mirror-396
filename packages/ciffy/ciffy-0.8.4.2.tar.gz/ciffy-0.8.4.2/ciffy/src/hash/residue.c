/* ANSI-C code produced by gperf version 3.1 */
/* Command-line: /usr/bin/gperf /home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf  */
/* Computed positions: -k'1-3' */

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

#define RESIDUETOTAL_KEYWORDS 39
#define RESIDUEMIN_WORD_LENGTH 1
#define RESIDUEMAX_WORD_LENGTH 3
#define RESIDUEMIN_HASH_VALUE 1
#define RESIDUEMAX_HASH_VALUE 148
/* maximum key range = 148, duplicates = 0 */

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
  static unsigned char asso_values[] =
    {
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149,  10, 149,   0,   0,  15,
      149,   5,  25,  60, 149, 149,  20,   1,   1,  40,
       60, 149,  45,  45,  15,  20,   6, 149, 149,   5,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149, 149, 149, 149, 149,
      149, 149, 149, 149, 149, 149
    };
  register unsigned int hval = len;

  switch (hval)
    {
      default:
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
_lookup_residue (register const char *str, register size_t len)
{
  static struct _LOOKUP wordlist[] =
    {
      {""},
#line 11 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"C", 1},
#line 15 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DC", 5},
#line 43 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CCC", 32},
      {""}, {""},
#line 12 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"G", 2},
#line 16 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DG", 6},
#line 40 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MG", 29},
      {""}, {""},
#line 10 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"A", 0},
#line 14 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DA", 4},
      {""},
#line 44 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GNG", 33},
      {""},
#line 18 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"T", 7},
#line 17 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"DT", 7},
      {""}, {""}, {""},
#line 13 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"U", 3},
      {""},
#line 46 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CYT", 1},
      {""}, {""}, {""}, {""},
#line 45 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ADE", 0},
#line 32 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GLN", 21},
      {""}, {""}, {""},
#line 24 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GLY", 13},
#line 29 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"MET", 18},
      {""}, {""}, {""},
#line 47 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GUA", 2},
#line 36 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"VAL", 25},
      {""}, {""}, {""},
#line 19 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ALA", 8},
      {""}, {""}, {""},
#line 41 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CS", 30},
#line 22 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GLU", 11},
      {""}, {""}, {""}, {""},
#line 20 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"CYS", 9},
      {""}, {""}, {""}, {""},
#line 28 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"LEU", 17},
#line 30 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ASN", 19},
      {""}, {""}, {""},
#line 33 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ARG", 22},
      {""}, {""}, {""}, {""},
#line 38 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"TYR", 27},
      {""}, {""}, {""}, {""},
#line 27 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"LYS", 16},
      {""}, {""}, {""}, {""},
#line 48 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"URA", 3},
      {""}, {""}, {""}, {""},
#line 42 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"GTP", 31},
      {""}, {""}, {""}, {""},
#line 35 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"THR", 24},
      {""}, {""}, {""}, {""},
#line 39 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"HOH", 28},
      {""}, {""}, {""}, {""},
#line 26 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ILE", 15},
      {""}, {""}, {""}, {""},
#line 23 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"PHE", 12},
      {""}, {""}, {""}, {""},
#line 34 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"SER", 23},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 21 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"ASP", 10},
      {""}, {""}, {""}, {""},
#line 37 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"TRP", 26},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
#line 25 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"HIS", 14},
      {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""}, {""},
      {""}, {""}, {""}, {""}, {""},
#line 31 "/home/runner/work/ciffy/ciffy/ciffy/src/hash/residue.gperf"
      {"PRO", 20}
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
