"""
Pile Foundation Design under Eccentric Loading
According to Thai Standard มยผ.1106-64 (Conceptual Implementation)

Author: Structural Engineer + Python Developer

Assumptions:
- Linear elastic load distribution
- No pile cap rigidity issues
- Suitable for preliminary design
"""

import numpy as np


# -------------------------------
# FUNCTION: Calculate Centroid
# -------------------------------
def calculate_centroid(piles):
    """
    piles: list of tuples [(x1,y1), (x2,y2), ...]
    return: (x_bar, y_bar)
    """
    x_coords = [p[0] for p in piles]
    y_coords = [p[1] for p in piles]

    x_bar = sum(x_coords) / len(piles)
    y_bar = sum(y_coords) / len(piles)

    return x_bar, y_bar


# -------------------------------
# FUNCTION: Calculate Eccentricity
# -------------------------------
def calculate_eccentricity(Mx, My, P):
    """
    ex = My / P
    ey = Mx / P
    """
    if P == 0:
        raise ValueError("Axial load P cannot be zero")

    ex = My / P
    ey = Mx / P

    return ex, ey


# -------------------------------
# FUNCTION: Calculate Pile Loads
# -------------------------------
def calculate_pile_loads(piles, P, Mx, My):
    """
    Calculate load on each pile:
    P_i = (P/n) + (Mx*y_i / Σy^2) + (My*x_i / Σx^2)
    """

    n = len(piles)

    # Convert to centroid-based coordinates
    x_bar, y_bar = calculate_centroid(piles)

    shifted = [(x - x_bar, y - y_bar) for x, y in piles]

    x_vals = np.array([p[0] for p in shifted])
    y_vals = np.array([p[1] for p in shifted])

    sum_x2 = np.sum(x_vals ** 2)
    sum_y2 = np.sum(y_vals ** 2)

    loads = []

    for i in range(n):
        xi = x_vals[i]
        yi = y_vals[i]

        axial_part = P / n

        moment_x_part = 0 if sum_y2 == 0 else (Mx * yi) / sum_y2
        moment_y_part = 0 if sum_x2 == 0 else (My * xi) / sum_x2

        Pi = axial_part + moment_x_part + moment_y_part

        loads.append(Pi)

    return loads, shifted


# -------------------------------
# FUNCTION: Safety Check
# -------------------------------
def check_safety(loads, Qa, FS, allow_tension=False):
    """
    Check:
    - Max load <= Qa/FS
    - No tension if not allowed
    """

    allowable = Qa / FS
    max_load = max(loads)
    min_load = min(loads)

    status = "PASS"
    warnings = []

    # Check compression capacity
    if max_load > allowable:
        status = "FAIL"
        warnings.append("Pile load exceeds allowable capacity")

    # Check tension
    if not allow_tension and min_load < 0:
        status = "FAIL"
        warnings.append("Tension detected in pile")

    utilization = max_load / allowable

    return {
        "status": status,
        "max_load": max_load,
        "min_load": min_load,
        "utilization": utilization,
        "allowable": allowable,
        "warnings": warnings
    }


# -------------------------------
# FUNCTION: Print Results
# -------------------------------
def print_results(piles, loads, safety, shifted):
    print("\n========== PILE LOAD RESULTS ==========\n")

    for i, ((x, y), load) in enumerate(zip(shifted, loads)):
        print(f"Pile {i+1}:")
        print(f"  Position (relative): x = {x:.3f}, y = {y:.3f}")
        print(f"  Load = {load:.2f} kN\n")

    print("========== SUMMARY ==========")
    print(f"Max Load     : {safety['max_load']:.2f} kN")
    print(f"Min Load     : {safety['min_load']:.2f} kN")
    print(f"Allowable    : {safety['allowable']:.2f} kN")
    print(f"Utilization  : {safety['utilization']:.2f}")
    print(f"Status       : {safety['status']}")

    if safety["warnings"]:
        print("\n⚠ WARNINGS:")
        for w in safety["warnings"]:
            print(f"- {w}")


# -------------------------------
# MAIN PROGRAM
# -------------------------------
def run_example():
    """
    Example:
    4 piles in square layout (2m x 2m)
    """

    print("\n=== EXAMPLE: 4-PILE GROUP WITH ECCENTRIC LOAD ===")

    # Pile layout (meters)
    piles = [
        (-1, -1),
        (1, -1),
        (1, 1),
        (-1, 1)
    ]

    # Loads
    P = 1000   # kN
    Mx = 200   # kN-m
    My = 150   # kN-m

    # Capacity
    Qa = 400   # kN
    FS = 2.5

    print("\n--- INPUT ---")
    print(f"P  = {P} kN")
    print(f"Mx = {Mx} kN-m")
    print(f"My = {My} kN-m")
    print(f"Qa = {Qa} kN")
    print(f"FS = {FS}")

    # Step 1: Centroid
    x_bar, y_bar = calculate_centroid(piles)
    print("\n--- STEP 1: CENTROID ---")
    print(f"x_bar = {x_bar:.3f}, y_bar = {y_bar:.3f}")

    # Step 2: Eccentricity
    ex, ey = calculate_eccentricity(Mx, My, P)
    print("\n--- STEP 2: ECCENTRICITY ---")
    print(f"ex = {ex:.3f} m")
    print(f"ey = {ey:.3f} m")

    # Step 3: Load distribution
    loads, shifted = calculate_pile_loads(piles, P, Mx, My)

    print("\n--- STEP 3: LOAD DISTRIBUTION ---")
    print("Formula:")
    print("P_i = (P/n) + (Mx*y_i / Σy²) + (My*x_i / Σx²)")

    # Step 4: Safety
    safety = check_safety(loads, Qa, FS)

    # Step 5: Output
    print_results(piles, loads, safety, shifted)


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    run_example()
