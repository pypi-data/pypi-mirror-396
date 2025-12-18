from ovm_erd.repository_reader import read_repository, build_metadata_dict
from ovm_erd.erd_graphviz import ERDGraphviz
import os

# Pad naar je repository
repository_path = "C:/Temp/models"
ensemble = "customer"

# Metadata ophalen
files = read_repository(repository_path)
metadata = build_metadata_dict(files)

# Filter op ensemble/tag
filtered_metadata = {
    fn: d for fn, d in metadata.items()
    if ensemble in d.get("tags", [])
}

# Outputpad maken
output_path = f"ovm_erd/output/erd_{ensemble}"
os.makedirs("ovm_erd/output", exist_ok=True)

# ERD genereren
graph = ERDGraphviz(filtered_metadata)
graph.generate(output_path)
