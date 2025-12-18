from ovm_erd.repository_reader import read_repository
import json

# Pad naar je dbt-project of root van de repository
repository_path = "C:/Temp/datavault-layer"

# Metadata dictionary ophalen
metadata = read_repository(repository_path)

# Wegschrijven als JSON-bestand
output_path = "./metadata.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"Metadata succesvol weggeschreven naar: {output_path}")
