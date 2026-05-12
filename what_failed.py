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


folder_to_exclude = "out"    # The name of the folder to skip
search_dir = "functionals"   # Start searching from the current directory

failed_jobs = []
total_jobs = 0  # 1. Initialize outside the loops

for root, dirs, files in os.walk(search_dir):
    if folder_to_exclude in dirs:
        dirs.remove(folder_to_exclude)

    for file in files:
        if file.endswith(".out"):
            total_jobs += 1
            file_path = os.path.join(root, file)
            if not check_mrchem_termination(file_path) and not check_orca_termination(file_path):
                failed_jobs.append(file_path)

if not failed_jobs:
    print(f"All {total_jobs} jobs completed successfully :)")
else:
    print(f"Total jobs checked: {total_jobs}")
    print("Failed jobs:\n")
    for job in failed_jobs:
        print(job)
    print(f"Total failed jobs: {len(failed_jobs)}")