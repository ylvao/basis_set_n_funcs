import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import numpy as np
import sys
from pathlib import Path
import re

from plotting import load_and_prep_data, quadrupole_magnitude

def calculate_errors_to_json(df, index):
    name = df["Name"][index]
    lacks_t1_ref = False
    lacks_t2_ref = False
    if "_T" in name:
        return name, (lacks_t1_ref, lacks_t2_ref)
    name_parts = name.split("_")
    name_core = "_".join(name_parts[0:-1])
    json_file = "results/data_error.json"

    all_data = {}

    # json_file.parent.mkdir(parents=True, exist_ok=True)

    with open(json_file, 'r') as f:
        all_data = json.load(f)

    # if name in all_data:
    #     existing = all_data[name]
    #     if existing.get("Quadrupole error to T2 (abs)") is not "Null":
    #         return name_core, (lacks_t1_ref, lacks_t2_ref)

    data = {
        "Energy error to T1 (abs)"     : None,
        "Energy error to T1 (rel)"     : None,
        "Dipole error to T1 (abs)"     : None,
        "Dipole error to T1 (rel)"     : None,
        "Quadrupole error to T1 (abs)" : None,
        "Quadrupole error to T1 (rel)" : None,
        "Energy error to T2 (abs)"     : None,
        "Energy error to T2 (rel)"     : None,
        "Dipole error to T2 (abs)"     : None,
        "Dipole error to T2 (rel)"     : None,
        "Quadrupole error to T2 (abs)" : None,
        "Quadrupole error to T2 (rel)" : None,
        }

    for T in ["T1", "T2"]:
        t_re = fr"{re.escape(name_core)}_{re.escape(T)}"
        if t_re in df:
            print("Match!")

        # matches = df[df["Name"].str.match(t_re)]
        # # print(matches)
        # if not matches.empty:
        #     # print("matches not empty")
        #     ref_index = matches.index[0]
            
        #     etot   = df["Total energy"][index]
        #     dipole = df["Total dipole moment"][index]
        #     qupole = df["Quadrupole magnitude"][index]
        #     ref_etot   = df["Total energy"][ref_index]
        #     ref_dipole = df["Total dipole moment"][ref_index]
        #     ref_qupole = df["Quadrupole magnitude"][ref_index]

        #     name = df["Name"][index]
        #     data[f"Energy error to {T} (abs)"]     = etot - ref_etot
        #     data[f"Energy error to {T} (rel)"]     = (etot - ref_etot) / ref_etot if ref_etot != 0.0 else None
        #     data[f"Dipole error to {T} (abs)"]     = dipole - ref_dipole
        #     data[f"Dipole error to {T} (rel)"]     = (dipole - ref_dipole) / ref_dipole if ref_dipole != 0.0 else None
        #     data[f"Quadrupole error to {T} (abs)"] = qupole - ref_qupole
        #     data[f"Quadrupole error to {T} (rel)"] = (qupole - ref_qupole) / ref_qupole if ref_qupole != 0.0 else None
        # else:
        #     if T == "T1":
        #         lacks_t1_ref = True
        #     elif T == "T2":
        #         lacks_t2_ref = True

    all_data[name] = data

    with open(json_file, 'w') as f:
        json.dump(all_data, f, indent=4)

    if data[f"Quadrupole error to {T} (abs)"] != None:
        print(f"New data extracted from {name}")
    return name_core, (lacks_t1_ref, lacks_t2_ref)


data_df = load_and_prep_data('results/data.json')

lacks_all_t_refs = []
lacks_t1_refs = []
lacks_t2_refs = []
for i in range(len(data_df)):
    name, lacks_ref = calculate_errors_to_json(data_df, i)
    # print(name)
    if lacks_ref[0] and lacks_ref[1]:
        lacks_all_t_refs.append(name)
    elif lacks_ref[0]:
        lacks_t1_refs.append(name)
    elif lacks_ref[1]:
        lacks_t2_refs.append(name)

print(f"\nLacks T1 MRchem references:")
for n in set(lacks_t1_refs):
    print(n)
print(f"\nLacks T2 MRchem references:")
for n in set(lacks_t2_refs):
    print(n)
print(f"\nLacks all MRchem references:")
for n in set(lacks_all_t_refs):
    print(n)