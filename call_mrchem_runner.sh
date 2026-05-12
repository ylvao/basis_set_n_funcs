#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Calc parameters
mol="BH"
func="gga_c_N12"
t="T2"
prec="2e06"
#

dir="functionals/$func/$mol"
name="${mol}_${func}_${t}_${prec}"

abs_dir="$script_dir/$dir"
cd "$script_dir/$dir/out" || exit 1
sbatch "$script_dir/mrchem_runner.sh" "$abs_dir" "$name"