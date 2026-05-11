import sys
import os
import re

def extract_geometry(geom_name):
    with open('geometries/geometries.txt', 'r') as f:
        lines = f.readlines()
    
    pattern = re.compile(rf'=====================  ({re.escape(geom_name)}_[sdt])\.xyz  ======================')
    start = None
    full_name = None
    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            full_name = match.group(1)
            start = i + 2  # skip header and "Atom x y z"
            break
    
    if start is None:
        print(f"Geometry {geom_name} not found")
        return
    
    atoms = []
    for line in lines[start:]:
        line = line.strip()
        if line == '':
            break
        parts = line.split()
        if len(parts) == 4:
            atoms.append(line)
    
    num_atoms = len(atoms)
    
    with open(f'geometries/{full_name}.xyz', 'w') as f:
        f.write(f'{num_atoms}\n')
        f.write(f'=====================  {full_name}.xyz  ======================\n')
        for atom in atoms:
            f.write(f'{atom}\n')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python get_xyz.py <geometry_name>")
        sys.exit(1)
    geom_name = sys.argv[1]
    extract_geometry(geom_name)