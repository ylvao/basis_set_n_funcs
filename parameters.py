functional = [
    ("gga_x_pbe",      "exchange"),
    ("gga_c_pbe",      "correlation"),
    ("pbe",            "functional"),
    ("gga_x_b88",      "exchange"),
    ("lda_x",          "exchange"),
    ("gga_x_N12",      "exchange"),
    ("gga_c_N12",      "correlation"),
    ("gga_x_pw91",     "exchange"),
    ("gga_c_pw91",     "correlation"),
    ("hyb_gga_xc_b97", "functional"),
    ("gga_x_pw91 gga_c_pw91", "functional"),
]

basis_set_fams = {
    'cc':    ['ccpvdz', 'ccpvtz', 'ccpvqz'],
    'augcc': ['augccpvdz', 'augccpvtz', 'augccpvqz'],
    'def2':  ['def2svp', 'def2tzvp', 'def2qzvp'],
    'pcseg': ["pcseg0", "pcseg2", "pcseg4"],
    'pc':    ["pc0", "pc2", "pc4"],
}

basis_set = [item for fam in basis_set_fams.values() for item in fam]

prec = ["T1", "T2"]

system = [
    "BF",
    "BH",
    "C4H6",
]



mrchem_conv = False  # True if mrchem has difficulty converging
force_new = False    # Force creating new files, even if they already exist
