# Static Analysis

The SN/X toolchain performs several static checks before executing a program, similar in spirit to `go build` or `cargo check`.

## Overview

Static analysis is integrated into the compiler and runs by default when you call `compile_program()`. It catches errors and potential issues at compile time, before execution begins.

## Checks Performed

### Syntax and Basic Semantics

- Unknown instructions
- Invalid operand counts/types
- Register index bounds
- Undefined or duplicate labels

### Memory Bounds Checking

For `LD`/`ST` with absolute addresses (`base == $0`) that exceed `mem_size`, an error is flagged at compile time.

**Error code:** `M001`

```python
from snx import compile_program

source = """
main:
    LD $1, 1000($0)  ; Error: address 1000 exceeds mem_size=128
    HLT
"""

result = compile_program(source, mem_size=128)
print(result.format_diagnostics())  # Shows M001 error
```

> **Note:** `LDA` is not checked since it only computes an address without accessing memory.

### Control-Flow Analysis (CFG)

Builds a control-flow graph to identify:
- Unreachable code
- Obvious infinite loops (regions of code with no path to `HLT`)

### Dataflow Analysis

Tracks initialization state of registers/memory and return-address usage to detect:
- Reads from uninitialized or potentially uninitialized memory
- Return jumps that do not use a valid return address

## Diagnostic Codes

| Code | Severity | Description |
|------|----------|-------------|
| M001 | Error | Memory address exceeds configured `mem_size` |
| I001 | Warning | Immediate value truncated to 8 bits |
| B001 | Warning | Branch target exceeds 10-bit limit |

## Using Static Analysis

### From CLI

The CLI automatically runs static analysis and displays diagnostics:

```bash
snx program.s
```

The command will:
1. Parse and compile the assembly source
2. Run static analysis (errors and warnings)
3. If no errors, execute the program and display a trace table

### From Python

```python
from snx import compile_program

source = """
main:
    LDA $3, 64($0)
    LDA $1, 3($0)
    BAL $2, foo
    HLT
foo:
    HLT
"""

result = compile_program(source)

print(result.format_diagnostics())
if result.has_errors():
    raise SystemExit(1)
```

### Disabling Static Checks

If needed, you can disable static analysis:

```python
result = compile_program(source, run_static_checks=False)
```

When disabled, `cfg` and `dataflow` fields in `CompileResult` will be `None`.

## Related Documentation

- [Python API](python-api.md) for full API reference
- [Architecture](architecture.md) for memory model details
