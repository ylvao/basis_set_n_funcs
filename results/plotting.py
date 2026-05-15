import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import numpy as np

def qupole_error(mol1, mol2):
    components = ('XX', 'XY', 'XZ', 'YY', 'YZ', 'ZZ')
    q1 = mol1['Quadrupole moment']
    q2 = mol2['Quadrupole moment']
    diff = np.array([q1.get(k) - q2.get(k) for k in components], dtype=float)
    return float(np.dot(diff, diff))

def load_and_prep_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(list(data.values()))
    df['Basis_or_Precision'] = df['Basis set'].fillna('') + df['Precision'].fillna('')
    return df

def generate_plot(df, metric, title_prefix, ylabel, filename, 
                  custom_order=['T1', 'T2', 'ccpvdz', 'ccpvtz', 'ccpvqz', 'augccpvdz', 'augccpvtz', 'augccpvqz', 'def2svp', 'def2tzvp', 'def2tzvp'], 
                  ref_col=None, relative=False, func_names=None):
    """Generic engine to plot absolute values or differences."""
    
    molecules = df['Molecule'].unique()
    if func_names == None:
        functionals = sorted(df['Functional'].unique())
    else:
        functionals = func_names
    order_map = {val: i for i, val in enumerate(custom_order)}
    
    cmap = plt.get_cmap('viridis')
    color_map = dict(zip(functionals, cmap(np.linspace(0, 0.9, len(functionals)))))
    markers = ['o', '^', 's', 'D', '>', 'p', '*', '<', 'o', '^', 's', 'D', '>', 'p', '*', '<']

    fig, axes = plt.subplots(len(molecules), 1, figsize=(10, 6 * len(molecules)), constrained_layout=True)
    if len(molecules) == 1: axes = [axes]

    for i, mol in enumerate(molecules):
        mol_df = df[df['Molecule'] == mol]
        
        for m, func in enumerate(functionals):
            func_df = mol_df[mol_df['Functional'] == func].copy()
            
            # If we are doing a difference plot (e.g., relative to T1)
            if ref_col:
                ref_match = func_df[func_df['Basis_or_Precision'].str.strip() == ref_col]
                if ref_match.empty: continue
                ref_val = ref_match[metric].values[0]
                
                # Filter func_df to only include the comparison sets
                func_df = func_df[func_df['Basis_or_Precision'].isin(custom_order)]
                y_vals = func_df[metric] - ref_val
                if relative:
                    if ref_val == 0: continue
                    y_vals = y_vals / ref_val
            else:
                y_vals = func_df[metric]

            func_df['sort_idx'] = func_df['Basis_or_Precision'].map(order_map)
            func_df = func_df.dropna(subset=['sort_idx']).sort_values('sort_idx')

            if not func_df.empty:
                axes[i].plot(
                    func_df['sort_idx'], y_vals.loc[func_df.index], 
                    label=func, marker=markers[m % len(markers)], linestyle=':', linewidth=2, 
                    color=color_map[func], alpha=0.8
                )

        # Axis Formatting
        axes[i].set_title(f'{title_prefix}: {mol}', fontsize=14, fontweight='bold')
        axes[i].set_ylabel(ylabel)
        axes[i].set_xticks(range(len(custom_order)))
        axes[i].set_xticklabels(custom_order)
        if ref_col: axes[i].axhline(0, color='black', linewidth=0.8, linestyle='--')
        
        axes[i].grid(True, linestyle=':', alpha=0.6)
        axes[i].legend(title="Functionals", bbox_to_anchor=(1.05, 1), loc='upper left')

    os.makedirs('results/plots', exist_ok=True)
    plt.savefig(f'results/plots/{filename}', dpi=300)
    plt.close()
    print(f"Saved: {filename}")


data_df = load_and_prep_data('results/data.json')

# Standard Plots
generate_plot(data_df, 'Total energy', 'Energy Comparison', 'Energy (Hartree)', 'energy_overlay.png')
generate_plot(data_df, 'Total dipole moment', 'Dipole Comparison', 'Dipole (a.u.)', 'dipole_overlay.png')

# Difference Plots (Relative to MRChem)
diff_sets = ['ccpvdz', 'ccpvtz', 'ccpvqz', 'augccpvdz', 'augccpvtz', 'augccpvqz', 'def2svp', 'def2tzvp', 'def2tzvp']

# Energy Diffs
generate_plot(data_df, 'Total energy', 'Abs Energy Error', '$\Delta E$ (a.u.)', 
              'energy_abs_T1.png', custom_order=diff_sets, ref_col='T1')
generate_plot(data_df, 'Total energy', 'Rel Energy Error', 'Rel $\Delta E$', 
              'energy_rel_T1.png', custom_order=diff_sets, ref_col='T1', relative=True)

# Dipole Diffs
generate_plot(data_df, 'Total dipole moment', 'Abs Dipole Error', '$\Delta \mu$ (a.u.)',
              'dipole_abs_T1.png', custom_order=diff_sets, ref_col='T1')
generate_plot(data_df, 'Total dipole moment', 'Rel Dipole Error', 'Rel $\Delta \mu$',
              'dipole_rel_T1.png', custom_order=diff_sets, ref_col='T1', relative=True)


# Make separate plot for all Functionals
functionals = sorted(data_df['Functional'].unique())
for func in functionals:
    func_dir = f"functionals/{func}"
    os.makedirs(f"results/plots/{func_dir}", exist_ok=True)
    generate_plot(data_df, 'Total energy', 'Energy Comparison', 'Energy (Hartree)',
                  f'{func_dir}/energy_overlay_{func}.png', func_names=[func])
    generate_plot(data_df, 'Total dipole moment', 'Dipole Comparison', 'Dipole (a.u.)',
                  f'{func_dir}/dipole_overlay_{func}.png', func_names=[func])

    # Difference Plots (Relative to T1)
    diff_sets = ['ccpvdz', 'ccpvtz', 'ccpvqz', 'augccpvdz', 'augccpvtz', 'augccpvqz', 'def2svp', 'def2tzvp', 'def2tzvp']

    generate_plot(data_df, 'Total energy', 'Abs Energy Error', '$\Delta E$ (a.u.)', 
                f'{func_dir}/energy_abs_T1_{func}.png', custom_order=diff_sets, ref_col='T1', func_names=[func])
    generate_plot(data_df, 'Total energy', 'Rel Energy Error', 'Rel $\Delta E$', 
                f'{func_dir}/energy_rel_T1_{func}.png', custom_order=diff_sets, ref_col='T1', relative=True, func_names=[func])
    generate_plot(data_df, 'Total dipole moment', 'Abs Dipole Error', '$\Delta \mu$ (a.u.)',
                f'{func_dir}/dipole_abs_T1_{func}.png', custom_order=diff_sets, ref_col='T1', func_names=[func])
    generate_plot(data_df, 'Total dipole moment', 'Rel Dipole Error', 'Rel $\Delta \mu$',
                f'{func_dir}/dipole_rel_T1_{func}.png', custom_order=diff_sets, ref_col='T1', relative=True, func_names=[func])

# Make separate plot for all basis set families
basis_set_fams = {
    'cc':    ['ccpvdz', 'ccpvtz', 'ccpvqz'],
    'augcc': ['augccpvdz', 'augccpvtz', 'augccpvqz'],
    'def2':  ['def2svp', 'def2tzvp', 'def2tzvp'],
    'pcseg': ["pcseg0", "pcseg2", "pcseg4"],
    'pc':    ["pc0", "pc2", "pc4"],
}

for fam, list in basis_set_fams.items():
    basis_dir = f"basis/{fam}"
    os.makedirs(f"results/plots/{basis_dir}", exist_ok=True)
    generate_plot(data_df, 'Total energy', 'Energy Comparison', 'Energy (Hartree)',
                f'{basis_dir}/energy_overlay_{fam}.png', custom_order=list)
    generate_plot(data_df, 'Total dipole moment', 'Dipole Comparison', 'Dipole (a.u.)',
                f'{basis_dir}/dipole_overlay_{fam}.png', custom_order=list)
    generate_plot(data_df, 'Total energy', 'Abs Energy Error', '$\Delta E$ (a.u.)', 
                f'{basis_dir}/energy_abs_T1_{fam}.png', custom_order=list, ref_col='T1')
    generate_plot(data_df, 'Total energy', 'Rel Energy Error', 'Rel $\Delta E$', 
                f'{basis_dir}/energy_rel_T1_{fam}.png', custom_order=list, ref_col='T1', relative=True)
    generate_plot(data_df, 'Total dipole moment', 'Abs Dipole Error', '$\Delta \mu$ (a.u.)',
                f'{basis_dir}/dipole_abs_T1_{fam}.png', custom_order=list, ref_col='T1')
    generate_plot(data_df, 'Total dipole moment', 'Rel Dipole Error', 'Rel $\Delta \mu$',
                f'{basis_dir}/dipole_rel_T1_{fam}.png', custom_order=list, ref_col='T1', relative=True)