#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Calc parameters
mol="C4H6"
func="gga_x_b88"
basis="ccpvqz"
#

dir="functionals/$func/$mol"
name="${mol}_${func}_${basis}"

abs_dir="$script_dir/$dir"
cd "$script_dir/$dir/out" || exit 1
sbatch "$script_dir/orca_runner.sh" "$abs_dir" "$name"