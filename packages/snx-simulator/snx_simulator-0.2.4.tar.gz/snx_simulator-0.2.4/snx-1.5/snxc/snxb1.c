/***********************************
  -- snxb1.c --
  Compiler source code for
  Simple 16bit Processor SN/X

  (C)Copyright by Naohiko Shimizu,
   2001, 2002.
    All rights are reserved.

  Contact information:
  Dr. Naohiko Shimizu

    IP Architecture Laboratory
    Email: nshimizu@ip-arch.jp
    URL: http://www.ip-arch.jp/
***********************************/
#include <stdio.h>
#include "snxc.h"
#include "y.tab.h"

static int lbl;
static int frametop = 0;

void rinst (char *op,int r1,
		int r2,int r3) {
  printf("\t%s\t$%d,\t$%d,\t$%d\n",
         op,r1,r2,r3);
}
void rinst2 (char *op,int r1,
		int r2) {
  printf("\t%s\t$%d,\t$%d\n",
         op,r1,r2);
}
void iinst (char *op, int r1,
		int i,int r2) {
  printf("\t%s\t$%d,\t%d($%d)\n",
           op,r1,i,r2);
}
void sinit(int val) {
  iinst("lda",3,val,0);
  return;
  }
int ex(Pnode *p,int reg,int pres) {
    int lbl1, lbl2, regx,
        value, i, j, top;

 regx = 3 - reg;
 if (!p) return 0;
 switch(p->type) {
  case typeCon:       
  value = p->con.value;
  top = 0;
  for(i=2; i > 0; i--) {
   if((p->con.value >> i*7) != 0) {
    value=(p->con.value>>i*7)&127;
    if(top == 0 || value != 0)
     iinst("lda", reg, value, top); 
    for(j=0; j<7; j++)
     rinst("add",reg,reg,reg);
    top = reg;
    }
   }
  value = p->con.value  & 127;
  if(value || top == 0)
   iinst("lda",
      reg, p->con.value & 127, top);
   break;
  case typeId:        
  iinst("ld", reg, p->id.i + 1, 0);
  break;
  case typeOpr:
  switch(p->opr.oper) {
   case FDEFA:
   printf("\tbal\t$0,\tL%03d\n",
           lbl1=lbl++);
   printf("foo:\n");
   iinst("lda",3,-2,3);
   iinst("st",2,0,3);
   iinst("st",1,1,3);
   ex(p->opr.op[0], 1, 0);
   printf("fooexit:\n");
   iinst("ld",2,0,3);
   iinst("lda",3,2,3);
   iinst("bal",0,0,2);
   printf("L%03d:\n", lbl1);
   break;
   case FDEF:
   printf("\tbal\t$0,\tL%03d\n",
          lbl1=lbl++);
   printf("foo:\n");
   iinst("lda",3,-1,3);
   iinst("st",2,0,3);
   ex(p->opr.op[0], 1, 0);
   printf("fooexit:\n");
   iinst("ld",2,0,3);
   iinst("lda",3,1,3);
   iinst("bal",0,0,2);
   printf("L%03d:\n", lbl1);
   break;
   case RETURN:
   if (p->opr.nops > 0) {
    ex(p->opr.op[0], 1, 0);
    }
   printf("\tbal\t$0,\tfooexit\n");
   break;
   case FOR:
   ex(p->opr.op[0], reg,pres);
   printf("L%03d:\n", lbl1 = lbl++);
   ex(p->opr.op[1], reg,pres);
   printf("\tbz\t$%d,\tL%03d\n",
           reg, lbl2 = lbl++);
   ex(p->opr.op[3], reg,pres);
   ex(p->opr.op[2], reg,pres);
   printf("\tbal\t$0,\tL%03d\n",
          lbl1);
   printf("L%03d:\n", lbl2);
   break;
   case WHILE:
   printf("L%03d:\n", lbl1 = lbl++);
   ex(p->opr.op[0], reg, pres);
   printf("\tbz\t$%d,\tL%03d\n",
           reg, lbl2 = lbl++);
   ex(p->opr.op[1], reg, pres);
   printf("\tbal\t$0,\tL%03d\n",
           lbl1);
   printf("L%03d:\n", lbl2);
   break;
   case HALT:
   printf("\thlt\n");
   break;
   case IF:
   ex(p->opr.op[0], reg, pres);
   if (p->opr.nops > 2) {
                /* if else */
    printf("\tbz\t$%d,\tL%03d\n",
           reg, lbl1 = lbl++);
    ex(p->opr.op[1], reg, pres);
    printf("\tbal\t$0,\tL%03d\n",
           lbl2 = lbl++);
    printf("L%03d:\n", lbl1);
    ex(p->opr.op[2], reg, pres);
    printf("L%03d:\n", lbl2);
    } else {
    /* if */
    printf("\tbz\t$%d,\tL%03d\n",
           reg, lbl1 = lbl++);
    ex(p->opr.op[1],reg, pres);
    printf("L%03d:\n", lbl1);
    }
   break;
   case PRINT:     
   ex(p->opr.op[0],reg, pres);
   iinst("st",reg,0,0);
   break;
   case OUT:     
   ex(p->opr.op[0],reg, pres);
   ex(p->opr.op[1],regx, 1);
   iinst("out",regx,0,reg);
   break;
   case MWT:     
   ex(p->opr.op[0],reg, pres);
   ex(p->opr.op[1],regx, 1);
   iinst("st", regx,(p->opr.nops>2)?
            p->opr.op[2]->id.i+1: 0,
	    reg);
   break;
   case '=':       
   ex(p->opr.op[1],reg, pres);
   iinst("st", reg,
         p->opr.op[0]->id.i+1,0);
   break;
   case UMINUS:    
   ex(p->opr.op[0],reg, pres);
   rinst2("not", reg,reg);
   iinst("lda",reg,1,reg);
   break;
   case IN:    
   ex(p->opr.op[0],reg, pres);
   iinst("in",reg,0,reg);
   break;
   case MRD:    
   ex(p->opr.op[0],reg, pres);
   iinst("ld",
          reg,(p->opr.nops>1)?
          p->opr.op[1]->id.i+1:
          0,reg);
   break;
   case ARGV:    
   iinst("ld" ,reg,frametop+1,3);
   break;
   case FUNC:    
   if(pres) {
    iinst("lda",3,-1,3);
    iinst("st",regx,0,3);
    frametop += 1;
    }
   ex(p->opr.op[0],1, 0);
   printf("\tbal\t$2,\tfoo\n");
   if(reg!=1) {
    iinst("lda",reg,0,1);
    }
   if(pres) {
    iinst("ld",regx,0,3);
    iinst("lda",3,1,3);
    frametop -= 1;
    }
   break;
   default:
   ex(p->opr.op[0], reg, pres);
   if(pres) {
    iinst("lda",3,-1,3);
    iinst("st",regx,0,3);
    frametop += 1;
    }
   ex(p->opr.op[1], regx, 1);
   switch(p->opr.oper) {
    case '+':
    rinst("add",reg,reg,regx);
    break;
    case '-':
    rinst2("not", regx,regx);
    iinst("lda",regx,1,regx);
    rinst("add",reg,reg,regx);
    break;
    case '<':
    rinst("slt",reg,reg,regx);
    break;
    case '>':
    rinst("slt",reg,regx,reg);
    break;
    case GE:
    rinst("slt",reg,regx,reg);
    rinst2("not", reg,reg);
    iinst("lda",reg,1,reg);
    iinst("lda",regx,1,0);
    rinst("add",reg,reg,regx);
    break;
    case LE:
    rinst("slt",reg,reg,regx);
    rinst2("not", reg,reg);
    iinst("lda",reg,1,reg);
    iinst("lda",regx,1,0);
    rinst("add",reg,reg,regx);
    break;
    case NE:    {
    rinst2("not", reg,reg);
    iinst("lda",reg,1,reg);
    rinst("add",reg,reg,regx);
    printf("\tbz\t$%d,\tL%03d\n",
            reg, lbl1 = lbl++);
    iinst("lda",reg,1,0);
    printf("L%03d:\n", lbl1);
    break;}
    case EQ:    {
    rinst2("not", reg,reg);
    iinst("lda",reg,1,reg);
    rinst("add",reg,reg,regx);
    printf("\tbz\t$%d,\tL%03d\n",
           reg,  lbl1 = lbl++);
    iinst("lda",reg,0,0);
    printf("\tbal\t$0,\tL%03d\n",
           lbl2 = lbl++);
    printf("L%03d:\n", lbl1);
    iinst("lda",reg,1,0);
    printf("L%03d:\n", lbl2);
    break;}
    }
   if(pres) {
    iinst("ld",regx,0,3);
    iinst("lda",3,1,3);
    frametop -= 1;
    }
   }
  }
 return 0;
}
