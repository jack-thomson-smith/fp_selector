em_max = 480
usable_spec = set(range(400, 701))
protein_spec = set(range(em_max-50, em_max+50))
usable_spec -= protein_spec
