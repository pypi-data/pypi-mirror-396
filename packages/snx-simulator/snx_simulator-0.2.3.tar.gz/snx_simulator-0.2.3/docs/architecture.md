# SN/X Architecture

This document provides a detailed technical reference for the SN/X processor architecture.

## Overview

SN/X (Simple 16-bit Non-Pipeline Processor) is a strictly 16-bit RISC processor designed for educational purposes.

**Designer:** Naohiko Shimizu

## Key Specifications

| Property | Value |
|----------|-------|
| Data Width | 16-bit |
| Address Space | 16-bit (2^16 words) for both IMEM and DMEM |
| Addressing | Word addressing (address increment of 1 = 16-bit move) |
| Registers | 4 General Purpose Registers (16-bit): `$0`, `$1`, `$2`, `$3` |
| Pipeline | Non-pipelined (sequential execution) |
| PC | 16-bit Program Counter (not directly accessible) |

> **Note:** `$0` can store values like any other register, but when used as a **base register** in memory addressing (e.g., `LD $1, 10($0)`), it is treated as constant `0`. This means `Imm($0)` becomes an absolute address.

## Instruction Formats

All instructions are 16-bit fixed length.

| Type | Assembly | Bit Layout (15→0) |
|------|----------|-------------------|
| **R** | `OP R1, R2, R3` | `OP(4) \| Src1(2) \| Src2(2) \| Dest(2) \| Unused(6)` |
| **R1** | `OP R1, R2` | `OP(4) \| Src(2) \| Unused(2) \| Dest(2) \| Unused(6)` |
| **R0** | `OP` | `OP(4) \| Unused(12)` |
| **I** | `OP R1, Imm(R2)` | `OP(4) \| Dest(2) \| Base(2) \| Imm(8)` |

## 8-bit Immediate Encoding

For I-type instructions (LD, ST, LDA, BAL with address operand), the immediate/offset field is **8 bits wide**. This implementation follows the original snxasm assembler behavior exactly:

- **Encoding:** The immediate value is masked to 8 bits (`imm & 0xFF`) during binary encoding.
- **Execution:** The 8-bit value is **sign-extended** to 16 bits before being added to the base register.
  - Values 0x00–0x7F (0–127) are interpreted as positive.
  - Values 0x80–0xFF (128–255) are interpreted as negative (-128 to -1).

This means the effective range for immediate values is **-128 to 127**. If a source value falls outside this range, it will be truncated and sign-extended, resulting in a different effective value. The static analyzer issues warning **I001** when this occurs.

**Example:**
```asm
LDA $1, 300($0)   ; Source value: 300
                  ; Encoded as: 300 & 0xFF = 0x2C (44)
                  ; Interpreted as: 44 (positive, since 0x2C < 0x80)
                  ; Warning I001: "Immediate value 300 will be encoded as 8-bit and interpreted as 44 (0x2C)"

LDA $1, -2($3)    ; Source value: -2
                  ; Encoded as: -2 & 0xFF = 0xFE (254)
                  ; Interpreted as: -2 (sign-extended, since 0xFE >= 0x80)
                  ; No warning (value unchanged after normalization)
```

## Full Instruction Set

| Opcode | Mnemonic | Type | Operation |
|:------:|:---------|:----:|:----------|
| `0x0` | **ADD** | R | `R1 = R2 + R3` |
| `0x1` | **AND** | R | `R1 = R2 & R3` |
| `0x2` | **SUB** | R | `R1 = R2 - R3` |
| `0x3` | **SLT** | R | `R1 = (R2 < R3) ? 1 : 0` |
| `0x4` | **NOT** | R1 | `R1 = ~R2` |
| `0x6` | **SR** | R1 | `R1 = R2 >> 1` |
| `0x7` | **HLT** | R0 | Halt processor |
| `0x8` | **LD** | I | `R1 = MEM[Base + Imm]` |
| `0x9` | **ST** | I | `MEM[Base + Imm] = R1` |
| `0xA` | **LDA** | I | `R1 = Base + Imm` (load address / immediate) |
| `0xC` | **IN** | I | `R1 = Input_Port` |
| `0xD` | **OUT** | I | `Output_Port = R1` |
| `0xE` | **BZ** | I | `if (R1 == 0) PC = Target` (branch if zero) |
| `0xF` | **BAL** | I | `R1 = PC + 1; PC = Target` (branch and link) |

### Branch Instructions

- **BZ:** Branches to target label if the condition register equals zero.
- **BAL:** Saves return address (`PC + 1`) into link register, then jumps to target. Used for function calls; return is typically `BAL $x, 0($link_reg)`.

## Branch Encoding and Program Length Limit

The original snxasm assembler encodes label-based branches (BZ, BAL) by directly adding the target label's PC value to the instruction word **without masking**. Since the opcode occupies bits 15–12 and the register field occupies bits 11–10, the target PC must fit within the lower 10 bits (bits 9–0) to avoid corrupting the instruction encoding.

This means:
- **Programs must be fewer than 1024 instructions** for branch encoding to work correctly.
- This Python implementation follows the same encoding scheme for compatibility with snxasm-generated binaries.

**Behavior for programs with 1024+ instructions:**

This implementation produces **identical binary output** to snxasm, even when branch targets exceed the 10-bit limit. When a branch target label has PC ≥ 1024:
- The encoding adds the full target PC to the instruction word, then masks to 16 bits.
- This causes the upper bits of the target PC to overflow into the opcode/register fields, corrupting the instruction—exactly as snxasm does.

The static analyzer issues warning **B001** when this occurs:
```
[B001] warning: Branch target 'label' has PC 1024, which exceeds the 10-bit branch field limit (0-1023);
       encoding will overflow into opcode/register bits (matching original snxasm behavior)
```

This warning alerts you to the encoding corruption while preserving full compatibility with legacy snxasm binaries.

## 16-bit Word Model

All register and memory values are strictly 16-bit words (0x0000–0xFFFF):
- Arithmetic operations wrap around on overflow/underflow.
- `SLT` compares values as signed 16-bit integers (two's complement).
- Effective addresses are computed as 16-bit values.

## I/O Model

The simulator supports `IN` and `OUT` instructions via callback functions:

```python
from snx import SNXSimulator

def my_input() -> int:
    return int(input("Enter value: "))

def my_output(value: int) -> None:
    print(f"Output: {value}")

sim = SNXSimulator.from_source(source, input_fn=my_input, output_fn=my_output)
sim.run()

print(sim.get_output_buffer())
```

- **IN:** Reads a 16-bit value from `input_fn()`. Returns 0 if no callback is set.
- **OUT:** Writes a 16-bit value via `output_fn()`. Values are also stored in an internal buffer accessible via `get_output_buffer()`.

## Memory Model

- **Architecture spec:** 2^16 words each for IMEM and DMEM.
- **Simulator default:** 2^16 words (65536) data memory, matching the full SN/X architecture.
- **Configurable:** Use `mem_size` parameter to reduce memory size for testing or constrained environments.

### Reduced Memory Mode

When `mem_size < 2^16`, the simulator operates in "reduced memory mode":

- **Static analysis:** For `LD`/`ST` with absolute addresses (`base == $0`) that exceed `mem_size`, an error is flagged at compile time (error code `M001`). Note: `LDA` is not checked since it only computes an address without accessing memory.
- **Runtime behavior:**
  - **LD:** Reading from an out-of-bounds address returns 0.
  - **ST:** Writing to an out-of-bounds address is silently ignored (no-op).

Example with reduced memory (static error):

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

### OOB Callback (Runtime Hook)

For dynamic addresses (where `base != $0`), out-of-bounds access cannot be detected at compile time. You can use the `oob_callback` parameter to receive notifications when OOB access occurs at runtime:

```python
from snx import SNXSimulator

def log_oob(kind, addr, pc, inst_text, mem_size):
    print(f"[OOB] {kind} at addr={addr} (pc={pc}): {inst_text}")

source = """
main:
    LDA $1, 200($0)   ; $1 = 200 (no OOB check for LDA)
    LD $2, 0($1)      ; Runtime OOB: addr=200 > mem_size=128
    HLT
"""

sim = SNXSimulator.from_source(
    source,
    mem_size=128,
    oob_callback=log_oob,
)
sim.run()
# Output: [OOB] load at addr=200 (pc=1): LD $2, 0($1)
```

**Callback signature:**
```python
def oob_callback(
    kind: str,      # "load" or "store"
    addr: int,      # Effective address (16-bit masked)
    pc: int,        # Program counter of the instruction
    inst_text: str, # Original assembly text
    mem_size: int,  # Current memory size
) -> None: ...
```

**Behavior:**
- If `oob_callback` is `None` (default), OOB access is handled silently (LD returns 0, ST is no-op).
- If `oob_callback` is set, it is called before the default behavior.
- If the callback raises an exception, the simulator stops immediately.

## Trace Output

Each simulation step outputs PC, instruction text, and register state in a table format.

## Related Documentation

- [Assembly Language](assembly-language.md) for syntax and grammar
- [Python API](python-api.md) for library usage
- [Static Analysis](static-analysis.md) for diagnostic codes
