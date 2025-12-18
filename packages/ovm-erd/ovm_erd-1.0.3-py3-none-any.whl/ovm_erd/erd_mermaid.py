import os

def generate_mermaid_erd(metadata: dict, ensemble: str, output_dir: str = "ovm_erd/output"):
    """
    Generate Mermaid ERD diagrams based on metadata for one ensemble or all distinct ensembles.
    Output is saved as Markdown (.md) files containing Mermaid 'erDiagram' syntax.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Distinct ensemble mode → produce one ERD per tag
    if ensemble == "distinct":
        all_tags = {tag for d in metadata.values() for tag in d.get("tags", [])}
        for tag in sorted(all_tags):
            subset = {k: v for k, v in metadata.items() if tag in v.get("tags", [])}
            if subset:
                export_mermaid_markdown(subset, tag, output_dir)
        return

    # Single ensemble mode
    subset = {k: v for k, v in metadata.items() if ensemble in v.get("tags", [])}
    if not subset:
        print(f"⚠️ No tables found for ensemble: {ensemble}")
        return

    export_mermaid_markdown(subset, ensemble, output_dir)


def sanitize(name: str) -> str:
    """Make names Mermaid-compatible (no spaces, no hyphens)."""
    return name.replace("-", "_").replace(" ", "_")


def export_mermaid_markdown(metadata: dict, ensemble: str, output_dir: str):
    """
    Create a Mermaid ERD diagram (.md output) for a single ensemble.
    Uses Data Vault cardinality conventions:
    - Hub (1) → Sat (many)
    - Hub (1) → Link (many)
    - Link (1) → LSAT/MSAT (many)
    """
    lines = ["```mermaid", "erDiagram"]

    # ----------------------------------------------------------
    # 1. ENTITIES
    # ----------------------------------------------------------
    for _, data in metadata.items():
        table = sanitize(data["table_name"])
        lines.append(f"    {table} {{")

        # Only pk and fk attributes
        if data.get("pk"):
            lines.append(f"        string {sanitize(data['pk'])} PK")

        for fk in data.get("fk", []):
            lines.append(f"        string {sanitize(fk)} FK")

        lines.append("    }")

    # ----------------------------------------------------------
    # 2. RELATIONSHIPS
    # ----------------------------------------------------------
    for _, data in metadata.items():
        src = sanitize(data["table_name"])
        pattern = data.get("pattern", "")
        pk = data.get("pk")
        fk_list = data.get("fk", [])

        # ------------------------------
        # SAT → HUB (1:N)
        # Hub ||--o{ Sat
        # ------------------------------
        if pattern == "sat":
            for tgt in metadata.values():
                if tgt.get("pattern") == "hub" and pk == tgt.get("pk"):
                    hub = sanitize(tgt["table_name"])
                    lines.append(f"    {hub} ||--o{{ {src} : {pk}")

        # ------------------------------
        # LINK → HUB (1:N per FK)
        # Hub ||--o{ Link
        # ------------------------------
        elif pattern == "link":
            for fk in fk_list:
                for tgt in metadata.values():
                    if tgt.get("pattern") == "hub" and fk == tgt.get("pk"):
                        hub = sanitize(tgt["table_name"])
                        lines.append(f"    {hub} ||--o{{ {src} : {pk}")

        # ------------------------------
        # MSAT → LINK or HUB (first match)
        # Target ||--o{ MSAT
        # ------------------------------
        elif pattern == "msat":
            for tgt in metadata.values():
                if pk == tgt.get("pk") and tgt.get("pattern") in ["link", "hub"]:
                    target = sanitize(tgt["table_name"])
                    lines.append(f"    {target} ||--o{{ {src} : {pk}")
                    break

        # ------------------------------
        # LSAT → LINK
        # Link ||--o{ LSAT
        # ------------------------------
        elif pattern == "lsat":
            for tgt in metadata.values():
                if pk == tgt.get("pk") and tgt.get("pattern") == "link":
                    link = sanitize(tgt["table_name"])
                    lines.append(f"    {link} ||--o{{ {src} : {pk}")

    lines.append("```")

    # ----------------------------------------------------------
    # 3. SAVE OUTPUT
    # ----------------------------------------------------------
    filename = f"{output_dir}/erd_mermaid_{ensemble}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Mermaid ERD saved to: {filename}")
