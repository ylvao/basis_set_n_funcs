functional = [
    ("lda_x",          "exchange"),
    ("gga_x_b88",      "exchange"),
    ("gga_x_pbe",      "exchange"),
    ("gga_c_pbe",      "correlation"),
    ("gga_x_N12",      "exchange"),
    ("gga_c_N12",      "correlation"),
    ("gga_x_pw91",     "exchange"),
    ("gga_c_pw91",     "correlation"),
    ("hyb_gga_xc_b97", "functional"),
    ("pbe",            "functional"),
    ("gga_x_pw91 gga_c_pw91", "functional"),
    ("gga_x_N12 gga_c_N12",   "functional"),
]

basis_set_fams_unformatted = {
    'cc':    ['cc-pVDZ', 'cc-pVTZ', 'cc-pVQZ'],
    'augcc': ['aug-cc-pVDZ', 'aug-cc-pVTZ', 'aug-cc-pVQZ'],
    'def2':  ['def2-SVP', 'def2-TZVP', 'def2-QZVP'],
    'pcseg': ["pcseg-0", "pcseg-2", "pcseg-4"],
    'pc':    ["pc-0", "pc-2", "pc-4"],
}

basis_set_unformatted = [item for fam in basis_set_fams_unformatted.values() for item in fam]

basis_set_fams = {}
for key in basis_set_fams_unformatted.keys():
    basis_set_fams[key] = [val.lower().replace("-", "") for val in basis_set_fams_unformatted[key]]

basis_set = [item for fam in basis_set_fams.values() for item in fam]

prec = ["T1", "T2"]

system = [
    "BF",      # s
    "BH",      # s
    "C4H6",    # s
    "CH3COOH", # s
    "H2O2",    # s
    "LiS",     # d
    "PO2",     # d
    "SiH2",    # t
    "PCl",     # t
]

need_tighter_prec =[
    "C4H6_gga_c_N12_T2_3e07", # Will get prec 1e-08
    "LiS_gga_c_N12_T1_1e06",
    "LiS_gga_c_N12_T2_1e07",
    "H2O2_gga_c_N12_T1_3e06",
    "PCl_gga_c_N12_T2_5e08",
    "CH3COOH_gga_c_N12_T2_2e07",
    "CH3COOH_gga_c_N12_T1_2e06",
    "C4H6_gga_c_N12_T2_3e08",
    "C4H6_gga_c_N12_T2_3e07",
    "PCl_gga_c_pbe_T2_5e08",
    "PCl_gga_c_pbe_T1_5e07",
    "C4H6_gga_c_pbe_T2_3e07",
    "PCl_gga_c_pw91_T2_5e08",
    "PCl_N12_T2_5e08",
    ]


mrchem_conv   = False  # True if mrchem has difficulty converging
force_new_inp = False  # Force creating new files, even if they already exist
force_new_run = False  # Force creating new files, even if they already exist
