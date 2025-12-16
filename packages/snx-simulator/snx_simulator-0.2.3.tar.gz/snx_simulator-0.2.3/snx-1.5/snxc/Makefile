#
# Makefile for SNX Compiler
# Gnu C Version
# N. Shimizu 11 Jul 2001
#

CC = gcc
YACC = bison -y
LEX = flex

CFLAGS = -Wall -g

CLEANS = snxb1.o snxb2.o y.tab.o lex.yy.o y.tab.c lex.yy.c y.tab.h
OBJS = snxb1.o y.tab.o lex.yy.o
OBJI = snxb2.o y.tab.o lex.yy.o
SRCS = snxb2.c snxb1.c snxc.y snxc.l snxc.h

all: snxc snxi

snxi: $(OBJI)
	$(CC) $(CFLAGS) $(OBJI) -o snxi

snxc: $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o snxc

snxb1.o: snxb1.c snxc.h y.tab.c
	$(CC) $(CFLAGS) -c snxb1.c

snxb2.o: snxb2.c snxc.h y.tab.c
	$(CC) $(CFLAGS) -c snxb2.c

y.tab.o: y.tab.c snxc.y
	$(CC) $(CFLAGS) -c y.tab.c

lex.yy.o: lex.yy.c y.tab.h
	$(CC) $(CFLAGS) -c lex.yy.c

y.tab.c: snxc.y snxc.h
	$(YACC) -d snxc.y

lex.yy.c: snxc.l snxc.h
	$(LEX) snxc.l

clean:
	-rm $(CLEANS)

tar:
	tar cvf snxc.tar Makefile Readme.html $(SRCS)
