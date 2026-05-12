#!/bin/sh
#SBATCH --account=nn14654k
#SBATCH --partition=large
#SBATCH --output=%j.out
#SBATCH --error=%j.err


#SBATCH --job-name=mrchem_func_tester
#SBATCH --time=0-10:00:00
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=256
#SBATCH --cpus-per-task=1
export OMP_NUM_THREADS=1

#Modules
module --force purge --silent
module load NRIS/CPU
module load GCC/14.2.0
module load Python/3.13.1-GCCcore-14.2.0
module load OpenMPI/5.0.7-GCC-14.2.0
module load CMake/3.31.3-GCCcore-14.2.0
export CMAKE_TLS_VERIFY=0

dir="$1"
name="$2"
cd "$dir/out" || exit 1

/cluster/projects/nn14654k/ylvaos/mrchem/install/bin/mrchem --launcher='srun --distribution=cyclic:cyclic' "$dir/inp/$name.inp"

rm -rf checkpoint
rm -rf orbitals
rm -rf plots
cp "$dir/out/$name.out" "$dir"

exit 0



