import re
import os
from get_xyz import extract_geometry
from mw_settings import calculate_energy_metrics
from what_failed import check_orca_termination, check_mrchem_termination

force_new = False

def create_mrchem_runner(molecule_name, functional, e_rel, Tn):
    file_name = f"{molecule_name}_{functional}_{Tn}_{e_rel}"
    input_file = f"functionals/{functional}/{molecule_name}/inp/{file_name}.inp"
    output_file = f"functionals/{functional}/{molecule_name}/{file_name}.out"
    
    runner_path = f"runners/{file_name}.sh"

    if force_new == False:
        if os.path.exists(output_file):
            if check_mrchem_termination(output_file) != False:
                # print(f"Outfile already exists for: {file_name}, but failed. Making new...")
                return None
        if os.path.exists(runner_path):
            return None

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

    with open(runner_path, 'w') as f:
        f.write(file_content)
    return file_name



def create_orca_runner(molecule_name, functional, basis_set):

    file_name = f"{molecule_name}_{functional}_{basis_set}"
    input_file = f"functionals/{functional}/{molecule_name}/inp/{file_name}.inp"
    output_file = f"functionals/{functional}/{molecule_name}/{file_name}.out"
    
    runner_path = f"runners/{file_name}.sh"

    if force_new == False:
        if os.path.exists(output_file):
            if check_orca_termination(output_file) != False:
                return None
        if os.path.exists(runner_path):
            return None
            # return print(f"Runner file already exists for: {file_name}")

    template_str = """#!/bin/bash

script_dir=$(pwd)

# Calc parameters
mol="param_mol"
func="param_func"
basis="param_basis"

dir="functionals/$func/$mol"
name="${mol}_${func}_${basis}"

abs_dir="$script_dir/$dir"
cd "$script_dir/$dir/out" || exit 1
sbatch "$script_dir/orca_runner.sh" "$abs_dir" "$name"

"""
    # Fill the template
    file_content = template_str.replace("param_basis", basis_set)
    file_content = file_content.replace("param_func", functional)
    file_content = file_content.replace("param_mol", molecule_name)

    with open(runner_path, 'w') as f:
        f.write(file_content)
    return file_name




def create_mrchem_input(geometry, molecule_name, functional, Tn, e_rel, order, e_conv, e_orb, do_not_want_to_converge=False):
    """
    Parses an XYZ file and creates individual simulation input files
    for each molecule using a provided template.
    """
    if " " in functional:
        functional_name = functional.split("_")[-1].strip()
        more_funcs = True
    else:
        functional_name = functional
        more_funcs = False
        
    # Create output directory and file
    input_dir = f"functionals/{functional_name}/{molecule_name}/inp"
    output_dir = f"functionals/{functional_name}/{molecule_name}/out"

    filename_prec = str(e_rel).replace("-", "")
    name_core = f"{molecule_name}_{functional_name}_{Tn}_{filename_prec}"
    input_file = f"{input_dir}/{name_core}.inp"
    output_file = f"{output_dir}/{name_core}.out"

    if force_new == False:
        if os.path.exists(input_file):
            if os.path.exists(output_file):
                if check_mrchem_termination(output_file):
                    return
    new_runner = create_mrchem_runner(molecule_name, functional_name, filename_prec, Tn)

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
$functionals
param_func
$end
  xc_library = libxc
}

Properties {
  dipole_moment = true
  quadrupole_moment = true
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
        if more_funcs == True:
            file_content = file_content.replace("param_func", functional.replace(" ", "\n"))
        else:
            file_content = file_content.replace("param_func", functional)
        file_content = file_content.replace("param_prec", str(e_rel))
        if do_not_want_to_converge:
            file_content = file_content.replace("param_prec", str(e_rel / 10))
        file_content = file_content.replace("param_order", str(order))
        file_content = file_content.replace("param_econv", str(e_conv))
        file_content = file_content.replace("param_eorb", str(e_orb))

        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        with open(input_file, 'w') as f:
            f.write(file_content)
    return name_core, new_runner
    # print(f"\nNew!\nMRChem input file created for: {name_core}\nSaved in {input_dir}\n")


def create_orca_input(geometry, molecule_name, functional, basis_set, xc_type):
    """
    Parses an XYZ file and creates an ORCA input file
    for the molecule using a provided template.
    """

    if " " in functional:
        functional_name = functional.split("_")[-1].strip()
        exch_func = functional.split(" ")[0].strip()
        corr_func = functional.split(" ")[1].strip()
        more_funcs = True
    else:
        functional_name = functional
        more_funcs = False
    
    # Create output directory and file
    input_dir = f"functionals/{functional_name}/{molecule_name}/inp"
    output_dir = f"functionals/{functional_name}/{molecule_name}/out"

    basis_set_format = basis_set.lower().replace("-", "")
    name_core = f"{molecule_name}_{functional_name}_{basis_set_format}"
    input_file = f"{input_dir}/{name_core}.inp"
    output_file = f"{output_dir}/{name_core}.out"

    if force_new == False:
        if os.path.exists(input_file):
            if os.path.exists(output_file):
                if check_orca_termination(output_file):
                    return None
                # return print(f"Successful output already exists for: {name_core}")
    new_runner = create_orca_runner(molecule_name, functional_name, basis_set_format)

    template_str = """! dft param_basis TightSCF
%pal nprocs 8 end

%loc
  LocMet NewBoys
  Occ true
end

%method
  exchange param_exch
  correlation param_corr
end

%elprop
  Dipole true
  Quadrupole true
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

        if more_funcs == True:
            file_content = file_content.replace("param_exch", exch_func)
            file_content = file_content.replace("param_corr", corr_func)
        else:
            if xc_type == "functional":
                file_content = file_content.replace("exchange param_exch", "")
                file_content = file_content.replace("correlation", "functional")
                file_content = file_content.replace("param_corr", functional)
            if xc_type == "exchange":
                file_content = file_content.replace("param_exch", functional)
                file_content = file_content.replace("param_corr", "None")
            if xc_type == "correlation":
                file_content = file_content.replace("param_exch", "None")
                file_content = file_content.replace("param_corr", functional)

        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        with open(input_file, 'w') as f:
            f.write(file_content)
    return name_core, new_runner


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
functional = [
    ("gga_x_pbe",      "exchange"),
    ("gga_c_pbe",      "correlation"),
    ("pbe",            "functional"),
    ("gga_x_b88",      "exchange"),
    ("lda_x",          "exchange"),
    ("gga_x_N12",      "exchange"),
    ("gga_c_N12",      "correlation"),
    ("gga_x_pw91",     "exchange"),
    ("gga_c_pw91",     "correlation"),
    ("hyb_gga_xc_b97", "functional"),
    ("gga_x_pw91 gga_c_pw91", "functional"),
    ]

system     = [
    "BF",
    "BH",
    "C4H6",
    ]
geom_file  = [find_xyz_file(sys) for sys in system]

# MRChem
prec = "T2"
mw_params = [calculate_energy_metrics(sys, prec) for sys in system]
e_abs, e_rel, order, e_conv, e_orb = zip(*mw_params)

# Orca
basis_set  = [
    "def2-SVP", "def2-TZVP", "def2-QZVP",
    "cc-pVDZ", "cc-pVTZ", "cc-pVQZ",
    "aug-cc-pVDZ", "aug-cc-pVTZ", "aug-cc-pVQZ",
    "pcseg-0", "pcseg-2", "pcseg-4",
    "pc-0", "pc-2", "pc-4",
    ]

new_mrchem_input = []
new_mrchem_runners = []
new_orca_input = []
new_orca_runners = []
for func in functional:
    for sys in range(len(system)):
        mrchem_result = create_mrchem_input(
            geom_file[sys], system[sys], func[0], prec,
            e_rel[sys], order[sys], e_conv[sys], e_orb[sys],
            do_not_want_to_converge=True,
        )
        if mrchem_result is not None:
            nmi, nwr = mrchem_result
            if nmi is not None:
                new_mrchem_input.append(nmi)
            if nwr is not None:
                new_mrchem_runners.append(nwr)

        for basis in basis_set:
            orca_result = create_orca_input(
                geom_file[sys], system[sys], func[0], basis, func[1]
            )
            if orca_result is not None:
                noi, nor = orca_result
                if noi is not None:
                    new_orca_input.append(noi)
                if nor is not None:
                    new_orca_runners.append(nor)

print(f"\nNew MRChem input file created for:")
for inp in new_mrchem_input:
    print(inp)
print(f"\nNew MRChem runner file created for:")
for runner in new_mrchem_runners:
    print(runner)
print(f"\nNew Orca input file created for:")
for inp in new_orca_input:
    print(inp)
print(f"\nNew Orca runner file created for:")
for runner in new_orca_runners:
    print(runner)