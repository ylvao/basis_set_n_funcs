import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import numpy as np
import subprocess
import sys


def plot_energy():
    # 1. Load Data
    with open('results/data.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(list(data.values()))

    # 2. Data Preparation
    df['Basis_or_Precision'] = df['Basis set'].fillna('') + df['Precision'].fillna('')
    
    # Define the exact order
    custom_order = ['T1', 'T2', 'ccpvdz', 'ccpvtz', 'ccpvqz']
    
    # Map the labels to numbers 0, 1, 2, 3
    order_map = {val: i for i, val in enumerate(custom_order)}
    df['sort_idx'] = df['Basis_or_Precision'].map(order_map)

    molecules = df['Molecule'].unique()
    functionals = sorted(df['Functional'].unique())
    
    cmap = plt.get_cmap('viridis')
    color_list = cmap(np.linspace(0, 0.9, len(functionals)))
    color_map = dict(zip(functionals, color_list))

    # 3. Create Plot
    fig, axes = plt.subplots(len(molecules), 1, figsize=(10, 6 * len(molecules)), constrained_layout=True)
    if len(molecules) == 1: axes = [axes]

    for i, mol in enumerate(molecules):
        # Filter for this molecule
        mol_df = df[df['Molecule'] == mol]
        
        for func in functionals:
            # Filter and sort by our numeric index
            func_df = mol_df[mol_df['Functional'] == func].sort_values('sort_idx')
            
            if not func_df.empty:
                # We plot against 'sort_idx' (the numbers 0-3) to ensure a straight line
                axes[i].plot(
                    func_df['sort_idx'], 
                    func_df['Total energy'], 
                    label=func,
                    marker='o',
                    linestyle=':',
                    linewidth=2,
                    color=color_map[func],
                    alpha=0.8
                )

        # Formatting - This is the critical fix for the x-axis order
        axes[i].set_title(f'Energy Comparison: {mol}', fontsize=14, fontweight='bold')
        axes[i].set_ylabel('Total Energy (Hartree)')
        axes[i].set_xlabel('Basis Set / Precision')
        
        # Manually force the x-axis ticks to match our order
        axes[i].set_xticks(range(len(custom_order)))
        axes[i].set_xticklabels(custom_order)
        # Prevent "extra" space or jumping if data is missing
        axes[i].set_xlim(-0.1, len(custom_order) - 0.9)
        
        axes[i].grid(True, linestyle=':', alpha=0.6)
        axes[i].legend(title="Functionals", bbox_to_anchor=(1.05, 1), loc='upper left')

    # 4. Save
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/energy_overlay_plots.png')
    plt.close()
    print("energy overlay plot saved successfully.")


def plot_dipole():
    # 1. Load Data
    with open('results/data.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(list(data.values()))

    # 2. Data Preparation
    df['Basis_or_Precision'] = df['Basis set'].fillna('') + df['Precision'].fillna('')
    
    # Define the exact order
    custom_order = ['T1', 'T2', 'ccpvdz', 'ccpvtz', 'ccpvqz']
    
    # Map the labels to numbers 0, 1, 2, 3
    order_map = {val: i for i, val in enumerate(custom_order)}
    df['sort_idx'] = df['Basis_or_Precision'].map(order_map)

    molecules = df['Molecule'].unique()
    functionals = sorted(df['Functional'].unique())
    
    cmap = plt.get_cmap('viridis')
    color_list = cmap(np.linspace(0, 0.9, len(functionals)))
    color_map = dict(zip(functionals, color_list))

    # 3. Create Plot
    fig, axes = plt.subplots(len(molecules), 1, figsize=(10, 6 * len(molecules)), constrained_layout=True)
    if len(molecules) == 1: axes = [axes]

    for i, mol in enumerate(molecules):
        # Filter for this molecule
        mol_df = df[df['Molecule'] == mol]
        
        for func in functionals:
            # Filter and sort by our numeric index
            func_df = mol_df[mol_df['Functional'] == func].sort_values('sort_idx')
            
            if not func_df.empty:
                # We plot against 'sort_idx' (the numbers 0-3) to ensure a straight line
                axes[i].plot(
                    func_df['sort_idx'], 
                    func_df['Total dipole moment'], 
                    label=func,
                    marker='o',
                    linestyle=':',
                    linewidth=2,
                    color=color_map[func],
                    alpha=0.8
                )

        # Formatting - This is the critical fix for the x-axis order
        axes[i].set_title(f'Dipole Comparison: {mol}', fontsize=14, fontweight='bold')
        axes[i].set_ylabel('Total dipole moment (a.u.)')
        axes[i].set_xlabel('Basis Set / Precision')
        
        # Manually force the x-axis ticks to match our order
        axes[i].set_xticks(range(len(custom_order)))
        axes[i].set_xticklabels(custom_order)
        # Prevent "extra" space or jumping if data is missing
        axes[i].set_xlim(-0.1, len(custom_order) - 0.9)
        
        axes[i].grid(True, linestyle=':', alpha=0.6)
        axes[i].legend(title="Functionals", bbox_to_anchor=(1.05, 1), loc='upper left')

    # 4. Save
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/dipole_overlay_plots.png')
    print("dipole overlay plot saved successfully.")


def plot_e_diff():
    # 1. Load Data
    with open('results/data.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(list(data.values()))

    # 2. Data Preparation
    df['Basis_or_Precision'] = df['Basis set'].fillna('') + df['Precision'].fillna('')
    custom_order = ['ccpvdz', 'ccpvtz', 'ccpvqz']
    order_map = {val: i for i, val in enumerate(custom_order)}
    
    molecules = df['Molecule'].unique()
    functionals = sorted(df['Functional'].unique())
    
    cmap = plt.get_cmap('viridis') # Changed color map for variety
    color_map = dict(zip(functionals, cmap(np.linspace(0, 1, len(functionals)))))
    
    Tn = "T1" # Reference

    # We loop twice: once for Absolute, once for Relative
    plot_types = [
        {"type": "absolute", "suffix": "abs", "label": r"$\Delta E$ (a.u.)"},
        {"type": "relative", "suffix": "rel", "label": r"Relative $\Delta E$ ($\Delta E / E_{ref}$)"}
    ]

    for p_info in plot_types:
        fig, axes = plt.subplots(len(molecules), 1, figsize=(10, 6 * len(molecules)), constrained_layout=True)
        if len(molecules) == 1: axes = [axes]

        for i, mol in enumerate(molecules):
            mol_df = df[df['Molecule'] == mol]
            
            for func in functionals:
                func_all = mol_df[mol_df['Functional'] == func]
                tn_match = func_all[func_all['Basis_or_Precision'].str.strip() == Tn]
                
                if not tn_match.empty:
                    tn_energy = tn_match['Total energy'].values[0]
                    
                    plot_df = func_all[func_all['Basis_or_Precision'].isin(custom_order)].copy()
                    plot_df['sort_idx'] = plot_df['Basis_or_Precision'].map(order_map)
                    plot_df = plot_df.sort_values('sort_idx')

                    if not plot_df.empty:
                        # Calculation logic based on current loop type
                        diff = plot_df['Total energy'] - tn_energy
                        y_values = diff if p_info["type"] == "absolute" else (diff / tn_energy)

                        axes[i].plot(
                            plot_df['sort_idx'], 
                            y_values, 
                            label=func,
                            marker='o' if p_info["type"] == "absolute" else 's',
                            color=color_map[func]
                        )

            # Formatting
            title_prefix = "Absolute" if p_info["type"] == "absolute" else "Relative"
            axes[i].set_title(f'{title_prefix} Energy: {mol}', fontsize=14, fontweight='bold')
            axes[i].set_ylabel(p_info["label"])
            axes[i].set_xticks(range(len(custom_order)))
            axes[i].set_xticklabels(custom_order)
            axes[i].axhline(0, color='black', linewidth=0.8, linestyle='--')
            axes[i].grid(True, linestyle=':', alpha=0.6)
            axes[i].legend(title="Functionals", bbox_to_anchor=(1.05, 1), loc='upper left')

        # 4. Save each type to its own file
        os.makedirs('results/plots', exist_ok=True)
        save_path = f"results/plots/energy_{p_info['suffix']}_plots_{Tn}.png"
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
        print(f"{p_info['type']} energy (to {Tn}) plot saved successfully")

def plot_dp_diff():
    # 1. Load Data
    with open('results/data.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(list(data.values()))

    # 2. Data Preparation
    df['Basis_or_Precision'] = df['Basis set'].fillna('') + df['Precision'].fillna('')
    custom_order = ['ccpvdz', 'ccpvtz', 'ccpvqz']
    order_map = {val: i for i, val in enumerate(custom_order)}
    
    molecules = df['Molecule'].unique()
    functionals = sorted(df['Functional'].unique())
    
    cmap = plt.get_cmap('viridis') # Changed color map for variety
    color_map = dict(zip(functionals, cmap(np.linspace(0, 1, len(functionals)))))
    
    Tn = "T1" # Reference

    # We loop twice: once for Absolute, once for Relative
    plot_types = [
        {"type": "absolute", "suffix": "abs", "label": r"$\Delta E$ (a.u.)"},
        {"type": "relative", "suffix": "rel", "label": r"Relative $\Delta E$ ($\Delta E / E_{ref}$)"}
    ]

    for p_info in plot_types:
        fig, axes = plt.subplots(len(molecules), 1, figsize=(10, 6 * len(molecules)), constrained_layout=True)
        if len(molecules) == 1: axes = [axes]

        for i, mol in enumerate(molecules):
            mol_df = df[df['Molecule'] == mol]
            
            for func in functionals:
                func_all = mol_df[mol_df['Functional'] == func]
                tn_match = func_all[func_all['Basis_or_Precision'].str.strip() == Tn]
                
                if not tn_match.empty:
                    tn_dp = tn_match['Total dipole moment'].values[0]
                    
                    plot_df = func_all[func_all['Basis_or_Precision'].isin(custom_order)].copy()
                    plot_df['sort_idx'] = plot_df['Basis_or_Precision'].map(order_map)
                    plot_df = plot_df.sort_values('sort_idx')

                    if not plot_df.empty:
                        # Calculation logic based on current loop type
                        diff = plot_df['Total dipole moment'] - tn_dp
                        if tn_dp > 0:
                            y_values = diff if p_info["type"] == "absolute" else (diff / tn_dp)

                            axes[i].plot(
                                plot_df['sort_idx'], 
                                y_values, 
                                label=func,
                                marker='o' if p_info["type"] == "absolute" else 's',
                                color=color_map[func]
                            )
                        else:
                            print("Relative dp not possible as MRCHem dipole moment is 0")

            # Formatting
            title_prefix = "Absolute" if p_info["type"] == "absolute" else "Relative"
            axes[i].set_title(f'{title_prefix} Dipole Moment: {mol}', fontsize=14, fontweight='bold')
            axes[i].set_ylabel(p_info["label"])
            axes[i].set_xticks(range(len(custom_order)))
            axes[i].set_xticklabels(custom_order)
            axes[i].axhline(0, color='black', linewidth=0.8, linestyle='--')
            axes[i].grid(True, linestyle=':', alpha=0.6)
            axes[i].legend(title="Functionals", bbox_to_anchor=(1.05, 1), loc='upper left')

        # 4. Save each type to its own file
        os.makedirs('results/plots', exist_ok=True)
        save_path = f"results/plots/dp_{p_info['suffix']}_plots_{Tn}.png"
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
        print(f"{p_info['type']} dipole moment (to {Tn}) plot saved successfully")

plot_energy()
plot_dipole()
plot_e_diff()
plot_dp_diff()