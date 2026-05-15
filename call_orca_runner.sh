#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Calc parameters
mol="BF"
func="gga_c_N12"
basis="ccpvtz"
#

dir="functionals/$func/$mol"
name="${mol}_${func}_${basis}"

abs_dir="$script_dir/$dir"
cd "$script_dir/$dir/out" || exit 1
sbatch "$script_dir/orca_runner.sh" "$abs_dir" "$name"