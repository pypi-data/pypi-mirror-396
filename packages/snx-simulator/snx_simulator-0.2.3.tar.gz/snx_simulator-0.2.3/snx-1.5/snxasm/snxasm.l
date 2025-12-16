/******************************************

  Simple 16bit Non-Pipeline Processor (SN/X) V1.1
  Assembler source code.

  (C)Copyright by Naohiko Shimizu, 2001, 2002.
  All rights are reserved.

  Contact information:
  Dr. Naohiko Shimizu

  IP Architecture Laboratory
  Email: nshimizu@ip-arch.jp
  URL: http://www.ip-arch.jp/

  
  Update informations:

    04-Aug-2002: modified for PARTHENON lecture
******************************************/

%{
#include <stdlib.h>
#include "snxasm.h"
#include "y.tab.h"
void yyerror(char *s);
extern int Line;
%}

%%

L[0-9]+  { 
                yylval.iValue = atoi(yytext+1)+2;
                return LABEL;
            }
"foo"      {
                yylval.iValue = 0;
                return LABEL;
            }
"fooexit"      {
                yylval.iValue = 1;
                return LABEL;
            }

[0-9]+      {
                yylval.iValue = atoi(yytext);
                return INTEGER;
            }
"-"[0-9]+      {
                yylval.iValue = atoi(yytext);
                return INTEGER;
            }
"$"[0-3]    {
                yylval.iValue = atoi(yytext+1);
                return REG;
            }


[,():] {
                return *yytext;
             }

[\n] {
                Line++; return *yytext;
             }

"ld"|"LD"            {
                yylval.iValue = 8;
                return ITYPE;
             }
"st"|"ST"            {
                yylval.iValue = 9;
                return ITYPE;
             }
"lda"|"LDA"           {
                yylval.iValue = 10;
                return ITYPE;
             }
"bz"|"BZ"            {
                yylval.iValue = 14;
                return ITYPE;
             }
"bal"|"BAL"           {
                yylval.iValue = 15;
                return ITYPE;
             }
"in"|"IN"            {
                yylval.iValue = 12;
                return ITYPE;
             }
"out"|"OUT"           {
                yylval.iValue = 13;
                return ITYPE;
             }
"add"|"ADD"           {
                yylval.iValue = 0;
                return RTYPE;
             }
"sub"|"SUB"           {
                yylval.iValue = 2;
                return RTYPE;
             }
"and"|"AND"           {
                yylval.iValue = 1;
                return RTYPE;
             }
"slt"|"SLT"           {
                yylval.iValue = 3;
                return RTYPE;
             }
"not"|"NOT"           {
                yylval.iValue = 4;
                return RTYPE1;
             }
"sr"|"SR"            {
                yylval.iValue = 6;
                return RTYPE1;
             }
"hlt"|"HLT"            {
                yylval.iValue = 7;
                return RTYPE0;
             }

[ \t]+        ;       /* ignore whitespace */
";"*"\n"      ;       /* ignore comments */

.               yyerror("Unknown character");
%%
int yywrap(void) {
    return 1;
}
