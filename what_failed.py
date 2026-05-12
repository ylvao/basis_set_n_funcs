import os

def check_orca_termination(file_path):
    target = "****ORCA TERMINATED NORMALLY****"

    with open(file_path, 'r') as f:
        for line in f:
            if target in line:
                return True
    return False

def check_mrchem_termination(file_path):
    target = "Exiting MRChem"

    with open(file_path, 'r') as f:
        for line in f:
            if target in line:
                return True
    return False

def inp_missing_out(file_name):
    folder_to_exclude = "out"    # The name of the folder to skip
    search_dir = "functionals"   # Start searching from the current directory
    name = file_name.replace(".inp", ".out")
    # print(name)
    for root, dirs, files in os.walk(search_dir):
        if folder_to_exclude in dirs:
            dirs.remove(folder_to_exclude)
            for file in files:
                if file.endswith(".out"):
                    # print(file)
                    if name == file:
                        return None
    return file_name


folder_to_exclude = "out"    # The name of the folder to skip
search_dir = "functionals"   # Start searching from the current directory

failed_jobs = []
nout = 0
ninp = 0
inp_without_out = []

for root, dirs, files in os.walk(search_dir):
    if folder_to_exclude in dirs:
        dirs.remove(folder_to_exclude)

    for file in files:
        if file.endswith(".out"):
            nout += 1
            file_path = os.path.join(root, file)
            if not check_mrchem_termination(file_path) and not check_orca_termination(file_path):
                failed_jobs.append(file_path)
        if file.endswith(".inp"):
            name_or_none = inp_missing_out(file)
            if name_or_none is not None:
                inp_without_out.append(name_or_none)
            ninp += 1

if not failed_jobs:
    print(f"All {nout} jobs completed successfully :) (out of {ninp} input files)")
else:
    print(f"Total jobs checked: {nout}")
    print("Failed jobs:\n")
    for job in failed_jobs:
        print(job)
    print(f"Total failed jobs: {len(failed_jobs)}")

if inp_without_out != []:
    print(f"\nInputs missing output: found {len(inp_without_out)}, expected {abs(nout - ninp)}\n")
    for inp in inp_without_out:
        print(inp)
