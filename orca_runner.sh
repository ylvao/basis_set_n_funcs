#!/bin/sh
#SBATCH --account=nn14654k
#SBATCH --partition=large
#SBATCH --output=%j.out
#SBATCH --error=%j.err


#SBATCH --job-name=orca_func_tester
#SBATCH --time=0-10:00:00
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=256
#SBATCH --cpus-per-task=1
export OMP_NUM_THREADS=1

#Modules
module --force purge --silent
module load NRIS/CPU
module load OpenMPI/5.0.9-GCC-14.3.0
export CMAKE_TLS_VERIFY=0

dir="$1"
name="$2"
cd "$dir/out" || exit 1

/cluster/projects/nn14654k/ylvaos/orca_6_1_1_linux_x86-64_shared_openmpi418/orca "$dir/inp/$name.inp" > "$dir/out/$name.out"

cp "$dir/inp/$name"* "$dir/out"
rm "$dir/inp/$name"*
cp "$dir/out/$name.inp" "$dir/inp"
cp "$dir/out/$name.out" "$dir"

exit 0



