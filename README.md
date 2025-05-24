# Picasso Tower – Python Home Assignment

## Overview

This solution computes the number of valid assignments of animals and colors to five floors based on a list of logic hints. Each floor has one unique color and one unique animal. The logic supports three types of constraints: `AbsoluteHint`, `RelativeHint`, and `NeighborHint`.

- Total search space: **5! × 5! = 14,400** combinations.
- The program checks all combinations and filters those that satisfy the hints.
- Polymorphic methods (`satisfies()` and `is_consistent()`) are defined on each `Hint` subclass for clean logic separation.

## Design Decisions

- Used **brute-force with filtering** due to the small problem space (as allowed by the instructions).
- Refactored logic to use **OOP and polymorphism** instead of `if isinstance(...)` checks or dispatch tables.
- Hints with contradictory or invalid structure are filtered early using `is_consistent()`.

## How to Run

Run the Python script directly:

```bash
python picasso_tower.py
```

## Output

If successful, the script will print:

```
Success!
```

## Requirements

- Python 3.x
- No external dependencies (only standard library)
