import os
import re
from typing import Any, Dict, List, Sequence, Tuple
import math


def parse_formula(formula: str) -> List[str]:
    """
    Parse a molecular formula into a list of atom symbols.

    Parameters:
        formula: Molecular formula, e.g., "CH4", "H2O".

    Returns:
        List of atom symbols, e.g., ["C", "H", "H", "H", "H"].
    """
    atoms = []
    for match in re.finditer(r'([A-Z][a-z]?)(\d*)', formula):
        element = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1
        atoms.extend([element] * count)
    return atoms

def round_sig_fig(x):
    if x == 0:
        return 0
    # Determine the power of 10
    power = math.floor(math.log10(abs(x)))
    # Round the leading digit and put it back in the original scale
    return round(x, -power)

def calculate_energy_metrics(formula: str, TN: str) -> Dict[str, Any]:
    """
    Calculate energy metrics for a given molecular formula and TN level, based on the Excel formulas.

    Parameters:
        formula: Molecular formula, e.g., "CH4".
        TN: TN level, one of "T1", "T2", "T3", "T4".

    Returns:
        A dictionary with keys: e_abs, e_rel, order, e_conv, e_orb.
    """
    atoms = parse_formula(formula)
    
    # Atomic numbers for common elements
    atomic_numbers = {
        'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
        'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20,
        'Br': 35, 'I': 53
    }
    
    # Compute atomic numbers of the atoms
    atomic_number_list = [atomic_numbers.get(atom.strip(), 0) for atom in atoms]
    atomic_number_energy = [z**(5/2) for z in atomic_number_list]
    atomic_number_sum = sum(atomic_number_energy)

    if TN == "T1":
        T = 1.00e-3
    elif TN == "T2":
        T = 1.00e-4
    elif TN == "T3":
        T = 1.00e-5
    elif TN == "T4":
        T = 1.00e-6
    else:
        raise ValueError(f"Invalid TN: {TN}. Must be one of T1, T2, T3, T4.")

    # Calculate the metrics using the formulas
    e_abs = T
    e_rel = T / atomic_number_sum if atomic_number_sum != 0 else 0
    order = -1.5 * math.log10(e_rel) if e_rel > 0 else 0
    e_conv = e_rel / 10
    e_orb = math.sqrt(e_conv) if e_conv >= 0 else 0

    return round_sig_fig(e_abs), round_sig_fig(e_rel), int(round(order)), round_sig_fig(e_conv), round_sig_fig(e_orb)


# e_abs, e_rel, order, e_conv, e_orb = calculate_energy_metrics("Be4C", "T4")
# print(e_abs, e_rel, order, e_conv, e_orb)