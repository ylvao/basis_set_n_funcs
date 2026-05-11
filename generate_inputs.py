import re
import os
from get_xyz import extract_geometry
from mw_settings import calculate_energy_metrics

def create_mrchem_runner(molecule_name, functional, e_rel, Tn):
    filename = f"runners/{molecule_name}_{functional}_{Tn}_{e_rel}.sh"
    if os.path.exists(filename):
        return print(f"Runner file already exists for: {molecule_name}_{functional}_{Tn}_{e_rel}")
    template_str = """#!/bin/bash

cd ..

# Calc parameters
mol="param_mol"
func="param_func"
t="param_t"
prec="param_prec"

abs="/cluster/projects/nn14654k/ylvaos/basis_set_n_funcs"
dir="functionals/$func/$mol"
name="${mol}_${func}_${t}_${prec}"

abs_dir="$abs/$dir"
cd "$abs_dir/out" || exit 1
sbatch "$abs/mrchem_runner.sh" "$abs_dir" "$name"

"""

    # Fill the template
    file_content = template_str.replace("param_mol", molecule_name)
    file_content = file_content.replace("param_func", functional)
    file_content = file_content.replace("param_prec", e_rel)
    file_content = file_content.replace("param_t", Tn)

    with open(filename, 'w') as f:
        f.write(file_content)

def create_mrchem_input(geometry, molecule_name, functional, Tn, e_rel, order, e_conv, e_orb):
    """
    Parses an XYZ file and creates individual simulation input files
    for each molecule using a provided template.
    """
    
    # Create output directory and file
    input_dir = f"functionals/{functional}/{molecule_name}/inp"
    filename_prec = str(e_rel).replace("-", "")
    output_file = f"{input_dir}/{molecule_name}_{functional}_{Tn}_{filename_prec}.inp"

    create_mrchem_runner(molecule_name, functional, filename_prec, Tn)
    if os.path.exists(f"functionals/{functional}/{molecule_name}/inp/{molecule_name}_{functional}_{Tn}_{filename_prec}.inp"):
        return print(f"Input  file already exists for: {molecule_name}_{functional}_{Tn}_{e_rel}")

    template_str = """# vim:syntax=sh:

world_prec = param_prec               # Overall relative precision
world_unit = angstrom

MPI {
  numerically_exact = true        # Guarantee identical results in MPI
  omp_threads = 16
}

Molecule {
  charge = 0
  multiplicity = param_m
$coords
param_xyz
$end
}

Basis {
  order = param_order
}

WaveFunction {
  method = DFT                   # Wave function method (HF or DFT)
  restricted = param_spin
}

DFT {
  functionals = param_func
  xc_library = libxc
}

Properties {
  dipole_moment = true
}

SCF {
    energy_thrs = param_econv
    orbital_thrs = param_eorb
}

"""
    xyz_file_path = geometry
    with open(xyz_file_path, 'r') as f:
        # Read Number of Atoms
        num_atoms_line = f.readline().strip()
        try:
            num_atoms = int(num_atoms_line)
        except ValueError:
            raise ValueError("Invalid number of atoms in XYZ file")

        # Read Metadata line and extract mol_code and multiplicity
        metadata = f.readline().strip()

        # Extract mol_name and multiplicity
        mol_match = re.search(r'=\s+(\w+)_(\w).xyz\s+=', metadata)
        if mol_match:
            mol_name = mol_match.group(1)
            m = mol_match.group(2)
        else:
            mol_name = "unknown"
            m = "s"  # default

        # Determine parameters
        m_value = {"s": 1, "d": 2, "t": 3}.get(m, 1)
        s_value = (m_value - 1) / 2
        spin_bool = "true" if s_value == 0 else "false"

        # Read atom coordinates
        coords_block = ""
        for _ in range(num_atoms):
            coords_block += f.readline()

        # Fill the template
        file_content = template_str.replace("param_xyz", coords_block.strip())
        file_content = file_content.replace("param_spin", spin_bool)
        file_content = file_content.replace("param_m", str(m_value))
        file_content = file_content.replace("param_func", functional)
        file_content = file_content.replace("param_prec", str(e_rel))
        file_content = file_content.replace("param_order", str(order))
        file_content = file_content.replace("param_econv", str(e_conv))
        file_content = file_content.replace("param_eorb", str(e_orb))

        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(f"functionals/{functional}/{molecule_name}/out", exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(file_content)

    print(f"\nNew!\nMRChem input file created for: {molecule_name}_{functional}_{Tn}_{e_rel}\n")

def create_orca_runner(molecule_name, functional, basis_set):
    filename = f"runners/{molecule_name}_{functional}_{basis_set}.sh"

    if os.path.exists(filename):
        return print(f"Runner file already exists for: {molecule_name}_{functional}_{basis_set}")

    template_str = """#!/bin/bash

cd ..

# Calc parameters
mol="param_mol"
func="param_func"
t="param_t"
prec="param_prec"

abs="/cluster/projects/nn14654k/ylvaos/basis_set_n_funcs"
dir="functionals/$func/$mol"
name="${mol}_${func}_${basis}"

abs_dir="$abs/$dir"
cd "$abs_dir/out" || exit 1
sbatch "$abs/mrchem_runner.sh" "$abs_dir" "$name"

"""
    # Fill the template
    file_content = template_str.replace("param_basis", basis_set)
    file_content = file_content.replace("param_func", functional)
    file_content = file_content.replace("param_mol", molecule_name)

    with open(filename, 'w') as f:
        f.write(file_content)


def create_orca_input(geometry, molecule_name, functional, basis_set, xc_type):
    """
    Parses an XYZ file and creates an ORCA input file
    for the molecule using a provided template.
    """

    input_dir = f"functionals/{functional}/{molecule_name}/inp"
    basis_set_format = basis_set.lower().replace("-", "")
    output_file = f"{input_dir}/{molecule_name}_{functional}_{basis_set_format}.inp"

    create_orca_runner(molecule_name, functional, basis_set_format)
    if os.path.exists(f"functionals/{functional}/{molecule_name}/inp/{molecule_name}_{functional}_{basis_set_format}.inp"):
        return print(f"Input  file already exists for: {molecule_name}_{molecule_name}_{functional}_{basis_set_format}")

    template_str = """! dft param_basis TightSCF
%pal nprocs 8 end

%loc
  LocMet NewBoys
  Occ true
end

%method
  param_xctype param_func
end

%elprop
  Dipole true
end

* xyz param_q param_m
param_xyz
*

"""
    xyz_file_path = geometry
    with open(xyz_file_path, 'r') as f:
        # Read Number of Atoms
        num_atoms_line = f.readline().strip()
        try:
            num_atoms = int(num_atoms_line)
        except ValueError:
            raise ValueError("Invalid number of atoms in XYZ file")

        # Read Metadata line and extract multiplicity
        metadata = f.readline().strip()

        # Extract multiplicity
        mol_match = re.search(r'=\s+(\w+)_(\w).xyz\s+=', metadata)
        if mol_match:
            m = mol_match.group(2)
        else:
            m = "s"  # default

        # Determine multiplicity value
        m_value = {"s": 1, "d": 2, "t": 3}.get(m, 1)

        # Assume charge 0
        q_value = 0

        # Read atom coordinates
        coords_block = ""
        for _ in range(num_atoms):
            coords_block += f.readline()

        # Fill the template
        file_content = template_str.replace("param_xyz", coords_block.strip())
        file_content = file_content.replace("param_q", str(q_value))
        file_content = file_content.replace("param_m", str(m_value))
        file_content = file_content.replace("param_basis", basis_set)
        file_content = file_content.replace("param_func", functional)
        file_content = file_content.replace("param_xctype", xc_type)

        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(f"functionals/{functional}/{molecule_name}/out", exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(file_content)

    print(f"\nNEW!\nOrca input file created for: {molecule_name}_{functional}_{basis_set_format}\n")


def find_xyz_file(system):
    # Find the geometry file for the requested system in the geometries directory.
    base_dir = os.path.abspath(os.path.dirname(__file__))
    geometries_dir = os.path.join(base_dir, "geometries")
    matching_files = [
        f for f in os.listdir(geometries_dir)
        if f.startswith(f"{system}_") and f.endswith(".xyz")
    ]
    if not matching_files:
        extract_geometry(system)
        matching_files = [
            f for f in os.listdir(geometries_dir)
            if f.startswith(f"{system}_") and f.endswith(".xyz")
        ]
    if not matching_files:
        raise FileNotFoundError(f"No XYZ file found for system '{system}' in {geometries_dir}")
    return os.path.join(geometries_dir, matching_files[0])


# Global
functional = ["gga_c_N12"]
system     = ["BF", "BH", "C4H6"]
geom_file  = [find_xyz_file(sys) for sys in system]

# MRChem
prec = "T2"
mw_params = [calculate_energy_metrics(sys, prec) for sys in system]
e_abs, e_rel, order, e_conv, e_orb = zip(*mw_params)

# Orca
basis_set  = "cc-pVDZ"
xc_type = "correlation" # functional, exchange or correlation

for func in functional:
    for sys in range(len(system)):
        create_mrchem_input(geom_file[sys], system[sys], func, prec, e_rel[sys], order[sys], e_conv[sys], e_orb[sys])
        create_orca_input(geom_file[sys], system[sys], func, basis_set, xc_type)