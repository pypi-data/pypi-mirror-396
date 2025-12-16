/******************************************

  Simple 16bit Non-Pipeline Processor (SN/X) V1.1
  Compiler source code.

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
#include "snxc.h"
#include "y.tab.h"
void yyerror(char *s);
int Line = 1;
%}

%%

[a-z]       { 
                yylval.Symbol = *yytext - 'a';
                return VARIABLE;
            }

[0-9]+      {
                yylval.IntVal = atoi(yytext);
                return INTEGER;
            }

[-()<>=+*/;{}.\[\]] {
                return *yytext;
             }

"++"            return PP;
"--"            return MM;
">="            return GE;
"<="            return LE;
"=="            return EQ;
"!="            return NE;
"for"           return FOR;
"while"         return WHILE;
"if"            return IF;
"else"          return ELSE;
"return"        return RETURN;
"print"         return PRINT;
"mem"           return MEM;
"io"            return IO;
"arg"           return ARG;
"lo"            return LO;
"void"          return DEF;
"int"           return DEF;
"foo"           return FUNCNAME;
"halt"          return HALT;

[ \t]+        ;       /* ignore whitespace */
[\n]		Line++;

.               yyerror("Unknown character");
%%
int yywrap(void) {
    return 1;
}
