from ovm_erd.repository_reader import read_repository, build_metadata_dict
from ovm_erd.erd_graphviz import ERDGraphviz
import os

# Stap 1: pad naar je SQL repository
# repository_path = "C:/Temp/datavault-layer"
repository_path = "C:/Users/fouwe/OneDrive - DATA-PROJECT BV/GitHub/OVM.Toolkit/ovm_erd/example-code/eneco-datavault-layer"

# Stap 2: metadata ophalen
files = read_repository(repository_path)
metadata = build_metadata_dict(files)

# Stap 3: unieke ensembles (tags) bepalen
ensembles = sorted({tag for d in metadata.values() for tag in d.get("tags", [])})

# Outputmap
output_dir = "ovm_erd/output"
os.makedirs(output_dir, exist_ok=True)

# Stap 4: per ensemble een ERD genereren
for ensemble in ensembles:
    filtered = {
        fn: d for fn, d in metadata.items()
        if ensemble in d.get("tags", [])
    }

    if not filtered:
        continue

    print(f"Generating Graphviz ERD for: {ensemble}")
    graph = ERDGraphviz(filtered)
    graph.generate(os.path.join(output_dir, f"erd_{ensemble}"))


