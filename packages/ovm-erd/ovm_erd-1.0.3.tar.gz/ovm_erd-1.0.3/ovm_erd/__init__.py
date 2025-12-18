__version__ = "1.0.3"

from ovm_erd.repository_reader import (
    read_repository,
    build_metadata_dict,
    save_to_textfile
)
from ovm_erd.erd_graphviz import ERDGraphviz

def erd_graphviz(path, ensemble=None, output_prefix="ovm_erd/output/erd"):
    """
    One-line pipeline to read SQL files, extract metadata, and generate ERDs.

    :param path: Folder path with .sql files
    :param ensemble: Optional filter tag ('core', 'finance', 'distinct', etc.)
    :param output_prefix: Prefix for output filenames
    """
    files = read_repository(path)
    metadata = build_metadata_dict(files)

    if ensemble:
        if ensemble.lower() == "distinct":
            tags = set(tag for d in metadata.values() for tag in d.get("tags", []))
            for tag in tags:
                filtered = {fn: d for fn, d in metadata.items() if tag in d.get("tags", [])}
                if filtered:
                    ERDGraphviz(filtered).generate(f"{output_prefix}_{tag}")
        else:
            metadata = {fn: d for fn, d in metadata.items() if ensemble in d.get("tags", [])}
            if not metadata:
                print(f"⚠️ No metadata found for ensemble '{ensemble}'")
                return
            ERDGraphviz(metadata).generate(f"{output_prefix}_{ensemble}")
    else:
        ERDGraphviz(metadata).generate(f"{output_prefix}_all")

    # save_to_textfile(files, f"{output_prefix}_output.txt", metadata)
    print(f"✅ Generating complete for ensemble: {ensemble or 'ALL'}")
