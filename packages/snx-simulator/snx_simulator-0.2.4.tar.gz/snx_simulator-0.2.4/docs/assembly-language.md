# SN/X Assembly Language

This document defines the syntax of the SN/X assembly language.

## Informal Overview

An SN/X assembly program consists of lines. Each line may contain:
- An optional **label definition** (an identifier followed by `:`)
- An optional **instruction** (a mnemonic followed by operands)
- An optional **comment** (starting with `;` and extending to the end of the line)

Empty lines and comment-only lines are allowed.

## Lexical Grammar

The lexer splits the input into the following token kinds:

| Token Kind | Description                                      | Examples            |
|------------|--------------------------------------------------|---------------------|
| IDENT      | Identifiers for labels and mnemonics             | `main`, `LDA`, `foo`|
| NUMBER     | Signed decimal integers                          | `42`, `-3`, `+10`   |
| REGISTER   | Register names (`$` followed by digits)          | `$0`, `$2`, `$3`    |
| COMMA      | `,`                                              |                     |
| COLON      | `:`                                              |                     |
| LPAREN     | `(`                                              |                     |
| RPAREN     | `)`                                              |                     |
| EOL        | End-of-line marker (produced for each newline)   |                     |
| EOF        | End-of-file marker                               |                     |

Comments start with `;` and continue to the end of the line. They are discarded by the lexer.

In EBNF notation:

```ebnf
identifier  = letter , { letter | digit | "_" } ;
number      = [ "+" | "-" ] , digit , { digit } ;
register    = "$" , digit , { digit } ;

letter      = "A".."Z" | "a".."z" ;
digit       = "0".."9" ;
```

Identifiers and mnemonics are case-insensitive; they are normalized to uppercase internally.

## Concrete Syntax Grammar (BNF / CFG)

The following context-free grammar (CFG), written in BNF, defines the concrete syntax of the SN/X assembly language:

```bnf
<program>           ::= <line>* <eof>

<line>              ::= [<label-def>] [<instruction>] <eol>

<label-def>         ::= <identifier> ":"

<instruction>       ::= <mnemonic> [<operand-list>]

<mnemonic>          ::= <identifier>

<operand-list>      ::= <operand> ("," <operand>)*

<operand>           ::= <register-operand>
                      | <address-operand>
                      | <label-ref-operand>

<register-operand>  ::= REGISTER

<address-operand>   ::= NUMBER "(" REGISTER ")"
                      | NUMBER

<label-ref-operand> ::= <identifier>

<eol>               ::= EOL | <eof>
<eof>               ::= EOF
```

**Notes:**
- When `<address-operand>` is written as just `NUMBER` (without parentheses), the base register defaults to `$0`.
- `<mnemonic>` is matched against the supported opcodes (`ADD`, `AND`, `SUB`, `SLT`, `NOT`, `SR`, `HLT`, `LD`, `ST`, `LDA`, `IN`, `OUT`, `BZ`, `BAL`). Unknown mnemonics produce a diagnostic error.
- Labels and mnemonics are case-insensitive.

## Operand Types by Instruction

| Instruction | Operand 1       | Operand 2                  | Operand 3       |
|-------------|-----------------|----------------------------|-----------------|
| ADD         | Register        | Register                   | Register        |
| AND         | Register        | Register                   | Register        |
| SUB         | Register        | Register                   | Register        |
| SLT         | Register        | Register                   | Register        |
| NOT         | Register        | Register                   |                 |
| SR          | Register        | Register                   |                 |
| HLT         |                 |                            |                 |
| LD          | Register        | Address                    |                 |
| ST          | Register        | Address                    |                 |
| LDA         | Register        | Address                    |                 |
| IN          | Register        |                            |                 |
| OUT         | Register        |                            |                 |
| BZ          | Register        | Label                      |                 |
| BAL         | Register        | Label or Address           |                 |

## Related Documentation

- [Architecture](architecture.md) for instruction encoding and ISA details
- [Static Analysis](static-analysis.md) for diagnostic codes
