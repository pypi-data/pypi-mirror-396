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

#include <stdlib.h>
#include <setjmp.h>
#include "snxc.h"
#include "y.tab.h"
#define FUNMAX  127

static Pnode *foo;
static int sp=FUNMAX;
static jmp_buf funbuf[FUNMAX];
static int val, jv;

int sinit(int init) {return 0;}
int ex(Pnode *p) {
    if (!p) return 0;
    switch(p->type) {
    case typeCon:       return p->con.value;
    case typeId:        return sym[p->id.i + 1];
    case typeOpr:
        switch(p->opr.oper) {
        case FDEF:
        case FDEFA:     foo=p->opr.op[0];
                        p->opr.op[0] = NULL;
                        return 0;
        case ARGV:      
                        return sym[sp+1];
        case FUNC:      if(p->opr.nops>0) {
                        val = ex(p->opr.op[0]);
                        sp -=2;
                        sym[sp+1] = val;
                        jv = setjmp(funbuf[sp]);
                        if(jv == 0)
                                val=ex(foo);
                        sp +=2;
                        return val;
                        } else
                        {
                        jv = setjmp(funbuf[sp]);
                        if(jv == 0)
                             val = ex(foo);
                        return val;
                        }
        case RETURN:    if(p->opr.nops>0) {
                        val = ex(p->opr.op[0]);
                        } else
                        {
                        val = 0;
                        }
                        longjmp(funbuf[sp], -1);
        case FOR:       for(ex(p->opr.op[0]);
                            ex(p->opr.op[1]);
                            ex(p->opr.op[2])) ex(p->opr.op[3]); return 0;
        case WHILE:     while(ex(p->opr.op[0])) ex(p->opr.op[1]); return 0;
        case HALT:      exit(0);
        case IF:        if (ex(p->opr.op[0]))
                            ex(p->opr.op[1]);
                        else if (p->opr.nops > 2)
                            ex(p->opr.op[2]);
                        return 0;
        case PRINT:     printf("%d\n", ex(p->opr.op[0])); return 0;
        case ';':       ex(p->opr.op[0]); return ex(p->opr.op[1]);
        case '=':       return sym[p->opr.op[0]->id.i + 1] = ex(p->opr.op[1]);
        case OUT:       printf("Port[%d] <- %d\n",
				sym[ex(p->opr.op[0])] , ex(p->opr.op[1]));
			return 0;
        case MWT:       return sym[ex(p->opr.op[0])
                               +((p->opr.nops>2)?p->opr.op[2]->id.i+1:0)] =
                               ex(p->opr.op[1]);
        case MRD:       return sym[ex(p->opr.op[0])+
                                ((p->opr.nops>1)?p->opr.op[1]->id.i+1:0)];
        case IN:        printf("Enter value for Port[%d]: ", ex(p->opr.op[0]));
			return getchar();
        case UMINUS:    return -ex(p->opr.op[0]);
        case '+':       return ex(p->opr.op[0]) + ex(p->opr.op[1]);
        case '-':       return ex(p->opr.op[0]) - ex(p->opr.op[1]);
        case '*':       return ex(p->opr.op[0]) * ex(p->opr.op[1]);
        case '/':       return ex(p->opr.op[0]) / ex(p->opr.op[1]);
        case '<':       return ex(p->opr.op[0]) < ex(p->opr.op[1]);
        case '>':       return ex(p->opr.op[0]) > ex(p->opr.op[1]);
        case GE:        return ex(p->opr.op[0]) >= ex(p->opr.op[1]);
        case LE:        return ex(p->opr.op[0]) <= ex(p->opr.op[1]);
        case NE:        return ex(p->opr.op[0]) != ex(p->opr.op[1]);
        case EQ:        return ex(p->opr.op[0]) == ex(p->opr.op[1]);
        }
    }
 return 0;
}
