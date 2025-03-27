from math import comb

probabilities = [0.2, 0.18, 0.15, 0.13, 0.12, 0.1, 0.07, 0.045, 0.005]
multipliers = [1.3, 2.25, 3.00, 5.00, 10.0, 25.0, 50.0, 125.0, 5000]

# Expected value for a single line
E_line = sum(p**3 * m for p, m in zip(probabilities, multipliers))

# Expected value for two intersecting lines (e.g., row + column)
E_overlapping_pair = sum(p**5 * m for p, m in zip(probabilities, multipliers))

# Expected value for two separate lines (e.g., row + column)
E_separate_pair = sum(p**6 * m for p, m in zip(probabilities, multipliers))

# Expected value for three intersecting lines (e.g., row + column + diagonal)
E_triple = sum(p**7 * m for p, m in zip(probabilities, multipliers))

# Expected value for all values in grid the same
E_full = sum(p**9 * m for p, m in zip(probabilities, multipliers))

# Total expected return (inclusion-exclusion)
E_total = (8 * E_line) + (12 * E_overlapping_pair) + (6 * E_separate_pair) + (9 * E_triple) + (1 * E_full)

# House edge
house_edge = 1 - E_total

print(f"Exact Expected Return: {E_total*100:.12f}%")
print(f"Exact House Edge: {house_edge*100:.12f}%")