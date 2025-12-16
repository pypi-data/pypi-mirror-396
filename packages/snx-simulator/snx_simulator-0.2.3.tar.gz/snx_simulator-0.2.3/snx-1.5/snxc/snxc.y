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
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "snxc.h"
#define YYDEBUG 1
#define STACKTOP 127

/* prototypes */
Pnode *opr(int oper, int nops, ...);
Pnode *id(int i);
Pnode *con(int value);
void freeNode(Pnode *p);
void sinit(int val);
int ex(Pnode *p, int reg, int pres);
extern int Line;
extern char * yytext;

void yyerror(char *s);

int sym[65536];                    /* symbol table + memory*/
%}

%union {
    int IntVal;                 /* integer value */
    char Symbol;                /* symbol table index */
    Pnode *Node;             /* node pointer */
};

%token <IntVal> INTEGER
%token <Symbol> VARIABLE
%token WHILE FOR IF PRINT MRD MWT OUT IN MEM IO LO FUNCNAME FDEF RETURN FUNC
%token DEF FDEFA HALT
%token <Node> ARG ARGV
%nonassoc IFX
%nonassoc ELSE

%left GE LE EQ NE '>' '<'
%left '+' '-'
%left '*' '/'
%right UMINUS
%left MM PP
%type <Node> astmt stmt expr stmt_list

%%

program:
        init function                { exit(0); }
        ;

init:
        /* NULL */  	                { sinit(STACKTOP);}
        ;

function:
          function stmt                 { ex($2,1,0); freeNode($2); }
        | /* NULL */
        ;

stmt:
          ';'                            { $$ = opr(';', 2, NULL, NULL); }
        | astmt ';'                       { $$ = $1; }
        | DEF FUNCNAME '(' ARG ')' stmt      { $$ = opr(FDEFA,1, $6); }
        | DEF FUNCNAME '(' DEF ARG ')' stmt      { $$ = opr(FDEFA,1, $7); }
        | DEF FUNCNAME '(' ')' stmt          { $$ = opr(FDEF, 1, $5); }
        | PRINT expr ';'                 { $$ = opr(PRINT, 1, $2); }
        | FOR '(' astmt ';' expr ';' astmt ')' stmt  
               { $$ = opr(FOR, 4, $3, $5, $7, $9); }
        | WHILE '(' expr ')' stmt        { $$ = opr(WHILE, 2, $3, $5); }
        | RETURN '(' expr ')' ';'        { $$ = opr(RETURN, 1, $3); }
        | RETURN expr ';'                { $$ = opr(RETURN, 1, $2); }
        | RETURN ';'                     { $$ = opr(RETURN, 0); }
        | IF '(' expr ')' stmt %prec IFX { $$ = opr(IF, 2, $3, $5); }
        | IF '(' expr ')' stmt ELSE stmt { $$ = opr(IF, 3, $3, $5, $7); }
        | '{' stmt_list '}'              { $$ = $2; }
        | HALT ';'                       { $$ = opr(HALT, 0); }
        ;

astmt:
          expr                        { $$ = $1; }
        | MEM '[' expr ']' '=' expr   { $$ = opr(MWT, 2, $3, $6); }
        | VARIABLE '=' expr           { $$ = opr('=', 2, id($1), $3); }
        | VARIABLE  PP   { $$ = opr('=',2,id($1),opr('+',2,id($1),con(1))); }
        | VARIABLE  MM   { $$ = opr('=',2,id($1),opr('-',2,id($1),con(1))); }
        | VARIABLE '[' expr ']' '=' expr   { $$ = opr(MWT, 3, $3, $6, id($1)); }
        ;

stmt_list:
          stmt                  { $$ = $1; }
        | stmt_list stmt        { $$ = opr(';', 2, $1, $2); }
        ;

expr:
          INTEGER               { $$ = con($1); }
        | VARIABLE              { $$ = id($1); }
        | ARG                   { $$ = opr(ARGV, 0); }
        | '-' expr %prec UMINUS { $$ = opr(UMINUS, 1, $2); }
        | MEM '[' expr ']'      { $$ = opr(MRD, 1, $3); }
        | VARIABLE '[' expr ']'      { $$ = opr(MRD, 2, $3, id($1)); }
        | FUNCNAME '(' expr ')' { $$ = opr(FUNC, 1, $3); }
        | expr '+' expr         { $$ = opr('+', 2, $1, $3); }
        | expr '-' expr         { $$ = opr('-', 2, $1, $3); }
        | expr '<' expr         { $$ = opr('<', 2, $1, $3); }
        | expr '>' expr         { $$ = opr('>', 2, $1, $3); }
        | expr GE expr          { $$ = opr(GE, 2, $1, $3); }
        | expr LE expr          { $$ = opr(LE, 2, $1, $3); }
        | expr NE expr          { $$ = opr(NE, 2, $1, $3); }
        | expr EQ expr          { $$ = opr(EQ, 2, $1, $3); }
        | '(' expr ')'          { $$ = $2; }
        ;

%%

Pnode *con(int value) {
    Pnode *p;

    /* allocate node */
    if ((p = malloc(sizeof(Const))) == NULL)
        yyerror("out of memory");

    /* copy information */
    p->type = typeCon;
    p->con.value = value;

    return p;
}

Pnode *id(int i) {
    Pnode *p;

    /* allocate node */
    if ((p = malloc(sizeof(Ident))) == NULL)
        yyerror("out of memory");

    /* copy information */
    p->type = typeId;
    p->id.i = i;

    return p;
}

Pnode *opr(int oper, int nops, ...) {
    va_list ap;
    Pnode *p;
    size_t size;
    int i;

    /* allocate node */
    size = sizeof(Operator) + (nops - 1) * sizeof(Pnode*);
    if ((p = malloc(size)) == NULL)
        yyerror("out of memory");

    /* copy information */
    p->type = typeOpr;
    p->opr.oper = oper;
    p->opr.nops = nops;
    va_start(ap, nops);
    for (i = 0; i < nops; i++)
        p->opr.op[i] = va_arg(ap, Pnode*);
    va_end(ap);
    return p;
}

void freeNode(Pnode *p) {
    int i;

    if (!p) return;
    if (p->type == typeOpr) {
        for (i = 0; i < p->opr.nops; i++)
            freeNode(p->opr.op[i]);
    }
    free (p);
}

void yyerror(char *s) {
    fprintf(stdout, "%s(%s) at %d\n", s, yytext, Line);
}

extern int yydebug;
int main(int argc, char *argv[]) {
    if(argc==2 && !strcmp(argv[1],"-d")) yydebug=1;
    yyparse();
    return 0;
}
