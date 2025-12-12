from __future__ import annotations

import random
from typing import List, Optional,Any


def generate_random_numbers(count: int, lower_bound: int, upper_bound: int) -> list[int]:
    return [random.randint(lower_bound, upper_bound) for _ in range(count)]

def generate_number_sequence(start: int, end: int, step: int) -> list[int]:
    return list(range(start, end + 1, step))

def generate_even_odd_numbers(lower_bound: int, upper_bound: int, even: bool = True) -> list[int]:
    if even:
        return [num for num in range(lower_bound, upper_bound + 1) if num % 2 == 0]
    else:
        return [num for num in range(lower_bound, upper_bound + 1) if num % 2 != 0]



def generate_random_table(
    rows: int,
    cols: int,
    min_count: int,
    max_count: int,
    category_prefix: str,
    header_first_row: bool,
    header_first_col: bool = False,
    row_prefix: Optional[str] = None,
) -> List[List[Any]]:
    """
    Generate a 2D list of cells. If header_first_row/col are True,
    first row/col will contain headers / labels instead of numbers.
    """

    # Example sketch – adjust to your actual implementation
    cells: List[List[Any]] = []

    # Build column headers if needed
    if header_first_row:
        header_row = []
        if header_first_col:
            header_row.append("")  # top-left empty or category label
        for j in range(cols if not header_first_col else cols - 1):
            header_row.append(f"{category_prefix} {j+1}")
        cells.append(header_row)

    # Build the rest of the rows
    data_rows = rows if not header_first_row else rows - 1
    for i in range(data_rows):
        row = []
        # Row label if header_first_col and row_prefix present
        if header_first_col:
            if row_prefix:
                row_label = f"{row_prefix} {i+1}"
            else:
                row_label = f"Row {i+1}"
            row.append(row_label)

        # Numeric cells
        num_data_cols = cols if not header_first_col else cols - 1
        for _ in range(num_data_cols):
            value = random.randint(min_count, max_count)
            row.append(value)

        cells.append(row)

    return cells

def build_number_sets():
    """Build number pairs for each operation using your utility functions."""

    add_a = generate_random_numbers(100, 1, 50)
    add_b = generate_random_numbers(100, 1, 50)
    addition_pairs = list(zip(add_a, add_b))

    seq = generate_number_sequence(20, 40, 2)  
    sub_a = seq[:3]
    sub_b = [n // 2 for n in sub_a]          
    subtraction_pairs = list(zip(sub_a, sub_b))

    evens = generate_even_odd_numbers(2, 20, even=True)
    mul_a = evens[:2]             
    mul_b = generate_random_numbers(2, 1, 10) 
    multiplication_pairs = list(zip(mul_a, mul_b))  # 2 pairs

    extra_add_a = generate_random_numbers(2, 1, 30)
    extra_add_b = generate_random_numbers(2, 1, 30)
    extra_add_pairs = list(zip(extra_add_a, extra_add_b))
    addition_pairs.extend(extra_add_pairs)  # now total 5 addition pairs

    return {
        "addition": addition_pairs,       # 5 pairs
        "subtraction": subtraction_pairs, # 3 pairs
        "multiplication": multiplication_pairs,  # 2 pairs
    }




def build_stat_prob_context(
    num_data_sets: int = 30,
    num_probability_sets: int = 30,
) -> dict:
    """
    Build numeric context for:
    - data handling questions (mean, range, interpreting tables/graphs)
    - probability questions (likelihood, evens, more/less likely)

    This version is designed to scale to 100s/1000s of questions by
    generating more varied and numerous contexts.
    """

    # ----------------------------
    # DATA SETS (for statistics)
    # ----------------------------
    data_sets = []

    # Different "profiles" of data: small values, test scores, temperatures, etc.
    data_profiles = [
        # (min, max, typical_length)
        (0, 10, 5),    # counts (e.g. number of books, goals, etc.)
        (1, 20, 6),    # small whole numbers
        (5, 50, 7),    # medium range (e.g. scores out of 50)
        (10, 100, 8),  # larger range (e.g. heights or points)
    ]

    for _ in range(num_data_sets):
        low, high, base_len = random.choice(data_profiles)
        length = base_len + random.choice([-1, 0, 1])  # tiny variation in length
        length = max(3, length)  # at least 3 values
        values = generate_random_numbers(length, low, high)
        data_sets.append(values)

    # ----------------------------
    # PROBABILITY CONTEXTS
    # ----------------------------
    probability_sets = []

    for _ in range(num_probability_sets):
        # Randomly choose a pattern: coloured objects or success/total
        pattern = random.choice(["colours_2", "colours_3", "success_total"])

        if pattern == "colours_2":
            # e.g. red/blue balls in a bag
            total = random.randint(5, 20)
            red = random.randint(0, total)
            blue = total - red
            probability_sets.append({"type": "bag_2_colours", "red": red, "blue": blue})

        elif pattern == "colours_3":
            # e.g. red/blue/green balls in a bag
            total = random.randint(6, 30)
            red = random.randint(0, total)
            remaining = total - red
            blue = random.randint(0, remaining)
            green = remaining - blue
            probability_sets.append(
                {"type": "bag_3_colours", "red": red, "blue": blue, "green": green}
            )

        else:  # "success_total"
            # e.g. success out of total (coin/dice/spinner style)
            total = random.choice([2, 4, 6, 8, 10, 12])  # small discrete sample spaces
            success = random.randint(0, total)
            probability_sets.append(
                {"type": "success_total", "success": success, "total": total}
            )

    return {
        "data_sets": data_sets,
        "probability_sets": probability_sets,
    }

