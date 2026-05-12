import os
import re
import json
from pathlib import Path

warnings = []

def extract_properties(name, file_path):

    json_file = Path("results/data.json")
    all_data = {}
    
    # Ensure directory exists
    json_file.parent.mkdir(parents=True, exist_ok=True)
    
    if json_file.exists():
        try:
            with open(json_file, 'r') as f:
                all_data = json.load(f)
        except json.JSONDecodeError:
            all_data = {}

    # Logic Change: Check if entry exists AND if it is complete
    if name in all_data:
        existing = all_data[name]
        # Overwrite if essential fields are missing/None
        if existing.get("Total energy") is not None and existing.get("Total dipole moment") is not None:
            # Entry is complete, skip processing
            return existing

    # If name is NOT in JSON, proceed with reading the file
    with open(file_path, 'r') as f:
        content = f.read()

    mrchem_dipole = r"Total\s+vector\s+:.*?\n\s+Magnitude\s+:\s+\(au\)\s+([\d\.\-]+)"
    mrchem_energy = r"Total energy\s+:\s+\(au\)\s+([\d\.\-\+eE]+)"
    
    orca_dipole = r"Magnitude \(a\.u\.\)\s+:\s+([\d\.\-]+)"
    orca_energy = r"FINAL SINGLE POINT ENERGY\s+([\d\.\-]+)"

    name_parts = name.split('_')
    molecule = name_parts[0] if len(name_parts) > 0 else "Unknown"

    t_index = next((i for i, s in enumerate(name_parts) if re.fullmatch(r'T[1-4]', s)), None)

    if t_index is not None:
        # If a T tier is found, everything between the molecule and the T tier is the functional
        functional = "_".join(name_parts[1:t_index])
    else:
        # Standard format: Molecule_Functional_Basis
        functional = "_".join(name_parts[1:-1])


    results = {
        "Software" : None,
        "Functional": functional,
        "Molecule": molecule,
        "Total dipole moment": None,
        "Total energy": None
        }

    m_en = re.search(mrchem_energy, content)
    o_en = re.search(orca_energy, content)
    m_dp = re.search(mrchem_dipole, content, re.DOTALL)
    o_dp = re.search(orca_dipole, content, re.DOTALL)
    if m_en:
        results["Total energy"] = float(m_en.group(1))
        results["Total dipole moment"] = float(m_dp.group(1)) if m_dp else None
        results["Precision"] = name_parts[-2]
        results["Software"] = "mrchem"
    elif o_en:
        results["Total energy"] = float(o_en.group(1))
        results["Total dipole moment"] = float(o_dp.group(1)) if o_dp else None
        results["Basis set"] = name_parts[-1]
        results["Software"] = "orca"
    else:
        warnings.append(f"Warning: No dipole magnitude or energyfound in {name}")

    # if Path(json_file).exists():
    try:
        with open(json_file, 'r') as f:
                all_data = json.load(f)
    except json.JSONDecodeError:
        all_data = {}

    all_data[name] = results

    with open(json_file, 'w') as f:
        json.dump(all_data, f, indent=4)

    print(f"Data extracted from {name}")

exclude = {"out"}

for root, dirs, files in os.walk("functionals"):
    dirs[:] = [d for d in dirs if d not in exclude]
    
    for file in files:
        if file.endswith(".out"):
            file_name = file.replace(".out", "")
            file_path = os.path.join(root, file)

            extract_properties(file_name, file_path)
for w in warnings:
    print(w)
