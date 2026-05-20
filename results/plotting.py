import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import numpy as np
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
from parameters import basis_set_fams, basis_set

def qupole_error(mol1, mol2):
    components = ('XX', 'XY', 'XZ', 'YY', 'YZ', 'ZZ')
    q1 = mol1['Quadrupole moment']
    q2 = mol2['Quadrupole moment']
    diff = np.array([q1.get(k) - q2.get(k) for k in components], dtype=float)
    return float(np.dot(diff, diff))

def quadrupole_magnitude(q):
    if not isinstance(q, dict):
        return np.nan
    vals = []
    for k in ('XX', 'XY', 'XZ', 'YY', 'YZ', 'ZZ'):
        v = q.get(k, 0.0)
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            vals.append(0.0)
    return float(np.linalg.norm(vals))


def load_and_prep_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(list(data.values()))
    df['Basis_or_Precision'] = df['Basis set'].fillna('') + df['Precision'].fillna('')
    df['Quadrupole magnitude'] = df['Quadrupole moment'].apply(quadrupole_magnitude)
    return df

def generate_plot(df, metric, title_prefix, ylabel, filename, 
                  custom_order=['T1', 'T2', 'ccpvdz', 'ccpvtz', 'ccpvqz', 'augccpvdz', 'augccpvtz', 'augccpvqz', 'def2svp', 'def2tzvp', 'def2qzvp'], 
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

    width = max(10, min(1 * len(custom_order), 24))
    fig, axes = plt.subplots(len(molecules), 1, figsize=(width, 6 * len(molecules)), constrained_layout=True)
    if len(molecules) == 1: axes = [axes]

    family_shading = True
    if family_shading:
        family_map = {member: fam for fam, members in basis_set_fams.items() for member in members}
        family_regions = []
        current_family = None
        region_start = 0
        for idx, entry in enumerate(custom_order):
            family = family_map.get(entry)
            if family != current_family:
                if current_family is not None:
                    family_regions.append((current_family, region_start, idx - 1))
                current_family = family
                region_start = idx
        if current_family is not None:
            family_regions.append((current_family, region_start, len(custom_order) - 1))
        colors = [plt.get_cmap('plasma')(x) for x in np.linspace(0.15, 0.85, len(family_regions))]
    else:
        family_regions = []

    for i, mol in enumerate(molecules):
        mol_df = df[df['Molecule'] == mol]

        if family_regions:
            for idx, (_, start, end) in enumerate(family_regions):
                axes[i].axvspan(start - 0.5, end + 0.5,
                                facecolor=colors[idx % len(colors)], alpha=.12,
                                linewidth=0, zorder=0)
            axes[i].set_xlim(-0.5, len(custom_order) - 0.5)
        
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
                if family_shading:
                    ts_group = {'T1', 'T2'}
                    family_seq = func_df['Basis_or_Precision'].map(
                        lambda x: family_map.get(x) if x not in ts_group else 'TS'
                    )
                    break_points = (func_df['sort_idx'].diff().fillna(1) != 1) | (family_seq != family_seq.shift(1))
                    group_id = break_points.cumsum()
                    first_seg = True
                    for _, segment in func_df.groupby(group_id):
                        axes[i].plot(
                            segment['sort_idx'], y_vals.loc[segment.index],
                            label=func if first_seg else '_nolegend_',
                            marker=markers[m % len(markers)], linestyle=':', linewidth=2,
                            color=color_map[func], alpha=0.8
                        )
                        first_seg = False
                else:
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


############ MAKING PLOTS ############


data_df = load_and_prep_data('results/data.json')
T = "T1"

# Standard Plots
generate_plot(data_df, 'Total energy', 'Energy Comparison', 'Energy (Hartree)', 
              'energy_overlay.png', custom_order=basis_set)
generate_plot(data_df, 'Total dipole moment', 'Dipole Comparison', 'Dipole (a.u.)', 
              'dipole_overlay.png', custom_order=basis_set)

# Energy Diffs
generate_plot(data_df, 'Total energy', 'Abs Energy Error', '$\Delta E$ (a.u.)', 
              'energy_abs_T1.png', custom_order=basis_set, ref_col=T)
generate_plot(data_df, 'Total energy', 'Rel Energy Error', 'Rel $\Delta E$', 
              'energy_rel_T1.png', custom_order=basis_set, ref_col=T, relative=True)

# Dipole Diffs
generate_plot(data_df, 'Total dipole moment', 'Abs Dipole Error', '$\Delta \mu$ (a.u.)',
              'dipole_abs_T1.png', custom_order=basis_set, ref_col=T)
generate_plot(data_df, 'Total dipole moment', 'Rel Dipole Error', 'Rel $\Delta \mu$',
              'dipole_rel_T1.png', custom_order=basis_set, ref_col=T, relative=True)

# Quadrupole Diffs
generate_plot(data_df, 'Quadrupole magnitude', 'Abs Quadrupole Error', '$\Delta Q$ (a.u.)',
              'qupole_abs_T1.png', custom_order=basis_set, ref_col=T)
generate_plot(data_df, 'Quadrupole magnitude', 'Rel Quadrupole Error', 'Rel $\Delta Q$',
              'qupole_rel_T1.png', custom_order=basis_set, ref_col=T, relative=True)

# # Make separate plot for all Functionals
# functionals = sorted(data_df['Functional'].unique())
# for func in functionals:
#     func_dir = f"functionals/{func}"
#     os.makedirs(f"results/plots/{func_dir}", exist_ok=True)
#     generate_plot(data_df, 'Total energy', 'Energy Comparison', 'Energy (Hartree)',
#                   f'{func_dir}/energy_overlay_{func}.png', func_names=[func])
#     generate_plot(data_df, 'Total dipole moment', 'Dipole Comparison', 'Dipole (a.u.)',
#                   f'{func_dir}/dipole_overlay_{func}.png', func_names=[func])

#     # Difference Plots (Relative to T1)
#     basis_set = ['ccpvdz', 'ccpvtz', 'ccpvqz', 'augccpvdz', 'augccpvtz', 'augccpvqz', 'def2svp', 'def2tzvp', 'def2qzvp']

#     generate_plot(data_df, 'Total energy', 'Abs Energy Error', '$\Delta E$ (a.u.)', 
#                 f'{func_dir}/energy_abs_T1_{func}.png', custom_order=basis_set, ref_col='T1', func_names=[func])
#     generate_plot(data_df, 'Total energy', 'Rel Energy Error', 'Rel $\Delta E$', 
#                 f'{func_dir}/energy_rel_T1_{func}.png', custom_order=basis_set, ref_col='T1', relative=True, func_names=[func])
#     generate_plot(data_df, 'Total dipole moment', 'Abs Dipole Error', '$\Delta \mu$ (a.u.)',
#                 f'{func_dir}/dipole_abs_T1_{func}.png', custom_order=basis_set, ref_col='T1', func_names=[func])
#     generate_plot(data_df, 'Total dipole moment', 'Rel Dipole Error', 'Rel $\Delta \mu$',
#                 f'{func_dir}/dipole_rel_T1_{func}.png', custom_order=basis_set, ref_col='T1', relative=True, func_names=[func])

# # Make separate plot for all basis set families
# for fam, basis_list in basis_set_fams.items():
#     basis_dir = f"basis/{fam}"
#     os.makedirs(f"results/plots/{basis_dir}", exist_ok=True)
#     generate_plot(data_df, 'Total energy', 'Energy Comparison', 'Energy (Hartree)',
#                 f'{basis_dir}/energy_overlay_{fam}.png', custom_order=basis_list)
#     generate_plot(data_df, 'Total dipole moment', 'Dipole Comparison', 'Dipole (a.u.)',
#                 f'{basis_dir}/dipole_overlay_{fam}.png', custom_order=basis_list)
#     generate_plot(data_df, 'Total energy', 'Abs Energy Error', '$\Delta E$ (a.u.)', 
#                 f'{basis_dir}/energy_abs_T1_{fam}.png', custom_order=basis_list, ref_col='T1')
#     generate_plot(data_df, 'Total energy', 'Rel Energy Error', 'Rel $\Delta E$', 
#                 f'{basis_dir}/energy_rel_T1_{fam}.png', custom_order=basis_list, ref_col='T1', relative=True)
#     generate_plot(data_df, 'Total dipole moment', 'Abs Dipole Error', '$\Delta \mu$ (a.u.)',
#                 f'{basis_dir}/dipole_abs_T1_{fam}.png', custom_order=basis_list, ref_col='T1')
#     generate_plot(data_df, 'Total dipole moment', 'Rel Dipole Error', 'Rel $\Delta \mu$',
#                 f'{basis_dir}/dipole_rel_T1_{fam}.png', custom_order=basis_list, ref_col='T1', relative=True)