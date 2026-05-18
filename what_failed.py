import os
import re

def check_orca_termination(file_path):
    marker = '****ORCA TERMINATED NORMALLY****'
    with open(file_path, 'r', errors='ignore') as f:
        for line in f:
            if marker in line:
                return True
    return False

def check_mrchem_termination(file_path):
    found_exit = False
    found_scf = False
    with open(file_path, 'r', errors='ignore') as f:
        for line in f:
            if 'Exiting MRChem' in line:
                found_exit = True
            if 'SCF converged in ' in line:
                found_scf = True
            if found_exit and found_scf:
                return True
    return False


if __name__ == "__main__":
    def what_failed_general():
        folder_to_exclude = "out"    # The name of the folder to skip
        search_dir = "functionals"   # Start searching from the current directory

        failed_jobs = []
        inp_without_out = []
        out_files = set()
        inp_files = []

        for root, dirs, files in os.walk(search_dir):
            if folder_to_exclude in dirs:
                dirs.remove(folder_to_exclude)

            for file in files:
                if file.endswith(".out"):
                    out_files.add(file)
                    file_path = os.path.join(root, file)
                    if not check_mrchem_termination(file_path) and not check_orca_termination(file_path):
                        failed_jobs.append(file_path)
                elif file.endswith(".inp"):
                    inp_files.append(file)

        for inp_file in inp_files:
            expected_out = inp_file[:-4] + ".out"
            if expected_out not in out_files:
                inp_without_out.append(inp_file)

        nout = len(out_files)
        ninp = len(inp_files)

        if not failed_jobs:
            print(f"\nAll {nout} jobs completed successfully :) (out of {ninp} input files)")
        else:
            print(f"\nTotal jobs checked: {nout}")
            print("Failed jobs (did not converge):")
            for job in failed_jobs:
                print(job)
            print(f"Total failed jobs: {len(failed_jobs)}")

        if inp_without_out:
            print(f"\nInputs missing output: found {len(inp_without_out)}, expected {abs(nout - ninp)}")
            for inp in inp_without_out:
                print(inp)

    what_failed_general()
    # print(check_orca_termination("functionals/gga_c_N12/C4H6/C4H6_gga_c_N12_T2_3e07.out"))