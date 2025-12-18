import os
import re
import json

# Default paths
example_path = './examples'
repository_path = r'C:\Temp\datavault-layer' #example_path # r'C:\Temp\datavault-layer' 
output_file = 'output/repository_output.txt'


def get_repository_path():
    """
    Bepaalt het juiste repository pad:
    - Als 'repository_path' niet bestaat of leeg is of niet bestaat als folder,
      wordt 'example_path' gebruikt als fallback.
    """
    try:
        if not repository_path or not os.path.exists(repository_path):
            print(f"⚠️ Ongeldig of leeg pad '{repository_path}'. Gebruik fallback: '{example_path}'")
            return example_path
        return repository_path
    except NameError:
        print(f"⚠️ Variabele 'repository_path' bestaat niet. Gebruik fallback: '{example_path}'")
        return example_path


def read_repository(repository_path):
    """
    Leest alle .sql-bestanden uit de folder (recursief) waarvan de inhoud
    de string 'set source_model =' bevat.
    """
    automateDV_files = {}

    for root, _, files in os.walk(repository_path):
        for file in files:
            if file.endswith(".sql"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "set source_model =" in content:
                        automateDV_files[file] = {"content": content}
                except UnicodeDecodeError:
                    print(f"⚠️ Kon bestand niet lezen: {full_path} — overgeslagen.")

    return automateDV_files


def build_metadata_dict(file_dict):
    """
    Maakt de metadata dictionary aan en vult table_name, tags, pk, fk, hashdiff,
    src_effective_date, nk en pattern op basis van de inhoud van elk .sql-bestand.
    """
    metadata = {}

    for filename, info in file_dict.items():
        table_name = filename[:-4] if filename.endswith(".sql") else filename
        content = info["content"]

        tag_match = re.search(r'tags\s*=\s*\[([^\]]*)\]', content, re.IGNORECASE)
        tags = [tag.strip().strip('"').strip("'") for tag in tag_match.group(1).split(',')] if tag_match else []

        pk_match = re.search(r'set\s+src_pk\s*=\s*"([^"]+)"', content, re.IGNORECASE)
        pk = pk_match.group(1) if pk_match else ""

        fk_match = re.search(r'set\s+src_fk\s*=\s*\[([^\]]*)\]', content, re.IGNORECASE)
        fk = [item.strip().strip('"').strip("'") for item in fk_match.group(1).split(',')] if fk_match else []

        hashdiff_match = re.search(r'set\s+src_hashdiff\s*=\s*"([^"]+)"', content, re.IGNORECASE)
        hashdiff = hashdiff_match.group(1) if hashdiff_match else ""

        eff_date_match = re.search(r'set\s+src_eff\s*=\s*"([^"]+)"', content, re.IGNORECASE)
        src_effective_date = eff_date_match.group(1) if eff_date_match else ""

        nk_match = re.search(r'set\s+src_nk\s*=\s*"([^"]+)"', content, re.IGNORECASE)
        nk = nk_match.group(1) if nk_match else ""

        if nk:
            pattern = "hub"
        elif fk:
            pattern = "link"
        elif hashdiff:
            pattern = "sat"
        else:
            pattern = ""

        metadata[filename] = {
            "table_name": table_name,
            "tags": tags,
            "pk": pk,
            "fk": fk,
            "hashdiff": hashdiff,
            "src_effective_date": src_effective_date,
            "nk": nk,
            "pattern": pattern
        }

    return metadata

def validate_metadata(metadata: dict):
    """
    Controleert welke entiteiten geen pattern hebben, of geen relaties kunnen leggen op basis van PK/FK.

    :param metadata: De volledige metadata dictionary.
    """
    print("\n🔍 Validatie-overzicht:\n")

    all_pks = {d["pk"] for d in metadata.values() if d.get("pattern") == "hub"}

    for name, data in metadata.items():
        pattern = data.get("pattern", "")
        pk = data.get("pk", "")
        fk_list = data.get("fk", [])

        if not pattern:
            print(f"⚠️  {name} heeft geen pattern (geen nk, fk of hashdiff gevonden)")

        if pattern == "sat":
            if not pk:
                print(f"⚠️  {name} (sat) heeft geen PK — kan niet linken aan hub")
            elif pk not in all_pks:
                print(f"⚠️  {name} (sat) PK '{pk}' komt niet overeen met een hub-PK")

        if pattern == "link":
            if not fk_list:
                print(f"⚠️  {name} (link) heeft geen FK's — kan geen relaties leggen")
            else:
                unmatched = [fk for fk in fk_list if fk not in all_pks]
                if unmatched:
                    print(f"⚠️  {name} (link) heeft FK's die niet matchen met hub-PK's: {unmatched}")

    print("\n✅ Validatie voltooid.")


def save_to_textfile(data, output_file, metadata=None):
    """
    Slaat de content dictionary op in een leesbaar tekstbestand
    en de metadata dictionary als JSON-bestand.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for filename, info in data.items():
            f.write(f"--- {filename} ---\n")
            f.write(info['content'])
            f.write("\n\n")

    if metadata is not None:
        metadata_file = output_file.replace('.txt', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as mf:
            json.dump(metadata, mf, indent=4)
        print(f"📝 Metadata opgeslagen als: {metadata_file}")
