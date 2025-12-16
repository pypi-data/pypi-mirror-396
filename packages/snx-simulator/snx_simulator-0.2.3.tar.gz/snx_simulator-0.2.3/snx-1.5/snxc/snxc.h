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

typedef enum { typeCon, typeId, typeOpr } nodeType;

/* constants */
typedef struct {
    nodeType type;              /* type of node */
    int value;                  /* value of constant */
} Const;

/* identifiers */
typedef struct {
    nodeType type;              /* type of node */
    int i;                      /* subscript to ident array */
} Ident;

/* operators */
typedef struct {
    nodeType type;              /* type of node */
    int oper;                   /* operator */
    int nops;                   /* number of operands */
    union PnodeTag *op[1];   /* operands (expandable) */
} Operator;

typedef union PnodeTag {
    nodeType type;              /* type of node */
    Const con;            /* constants */
    Ident id;              /* identifiers */
    Operator opr;            /* operators */
} Pnode;

extern int sym[65536];
