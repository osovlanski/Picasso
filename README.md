# Picasso Tower – Python Home Assignment

## Overview

This solution calculates the number of valid assignments of **animals and colors** to five distinct floors, given a list of logic hints. Each floor must have **one unique animal and one unique color**. The problem involves interpreting and satisfying three types of logical hints:

- `AbsoluteHint`: Enforces that two attributes are assigned to the same floor.
- `RelativeHint`: Enforces a fixed floor difference between two attributes.
- `NeighborHint`: Enforces that two attributes are placed on adjacent floors.

## Problem Space

- Total number of possible assignments (without constraints): **5! × 5! = 14,400**
- The goal is to filter and count only the assignments that satisfy all given hints.

## Algorithmic Strategy

This solution combines **constraint propagation** and **filtered permutation evaluation** for optimal performance:

### 1. Constraint Propagation

- Each `Hint` implements a `propagate()` method.
- During propagation, possible floor assignments are narrowed down for each color and animal.
- If any constraint reduces an attribute to a single valid floor, it is assigned immediately.
- Propagation continues until no more domains change (fixpoint).

### 2. Permutation-Based Assignment Validation

- After propagation, if any unassigned floors remain, permutations of remaining colors and animals are generated.
- For each permutation, the full assignment is tested using `satisfies()` from each `Hint` subclass.
- This stage ensures correctness while avoiding unnecessary evaluation paths eliminated during propagation.

## Design Principles

- Clean **object-oriented design** using:
  - `Picasso` for domain tracking and assignments.
  - `Hint` subclasses for encapsulating logic and validation.
  - `FloorsAssignment` to abstract read-only, complete state for validation.
- All constraint logic is polymorphic (no `if isinstance()` checks).
- Early detection of conflicting hints using `is_consistent()`.

## How to Run

Run the script directly using:

```bash
python count_assignments.py

## Output

If successful, the script will print:

```
Success!
```

## Requirements

- Python 3.x
- No external dependencies (only standard library)
