import argparse
import os
from ovm_erd.repository_reader import read_repository, build_metadata_dict
from ovm_erd.erd_graphviz import ERDGraphviz
from ovm_erd.erd_sql import generate_sql_query
from ovm_erd.erd_mermaid import generate_mermaid_erd
from ovm_erd.validator import validate_metadata

OUTPUT_DIR = "ovm_erd/output"

def main():
    parser = argparse.ArgumentParser(description="OVM-ERD: Generate ERDs and SQL from AutomateDV metadata")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # graphviz
    graphviz_parser = subparsers.add_parser("graphviz", help="Generate a Graphviz ERD")
    graphviz_parser.add_argument("--path", required=True, help="Path to the repository")
    graphviz_parser.add_argument("--ensemble", required=True, help="Ensemble name or 'distinct'")

    # sql
    sql_parser = subparsers.add_parser("sql", help="Generate SQL from metadata")
    sql_parser.add_argument("--path", required=True, help="Path to the repository")
    sql_parser.add_argument("--ensemble", required=True, help="Ensemble/tag to use")

    # mermaid
    mermaid_parser = subparsers.add_parser("mermaid", help="Generate a Mermaid ERD in Markdown format")
    mermaid_parser.add_argument("--path", required=True, help="Path to the repository")
    mermaid_parser.add_argument("--ensemble", required=True, help="Ensemble name or 'distinct'")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate the metadata and generate HTML report")
    validate_parser.add_argument("--path", required=True, help="Path to the repository")
    validate_parser.add_argument("--ensemble", required=True, help="Ensemble name or 'distinct'")

    args = parser.parse_args()

    # Metadata ophalen
    files = read_repository(args.path)
    metadata = build_metadata_dict(files)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.command == "graphviz":
        if args.ensemble == "distinct":
            all_tags = {tag for d in metadata.values() for tag in d.get("tags", [])}
            for tag in sorted(all_tags):
                subset = {
                    k: v for k, v in metadata.items() if tag in v.get("tags", [])
                }
                output_path = os.path.join(OUTPUT_DIR, f"erd_{tag}")
                graph = ERDGraphviz(subset)
                graph.generate(output_path)
        else:
            subset = {
                k: v for k, v in metadata.items() if args.ensemble in v.get("tags", [])
            }
            output_path = os.path.join(OUTPUT_DIR, f"erd_{args.ensemble}")
            graph = ERDGraphviz(subset)
            graph.generate(output_path)

    elif args.command == "sql":
        query = generate_sql_query(metadata, args.ensemble)
        output_path = os.path.join(OUTPUT_DIR, f"query_{args.ensemble}.sql")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(query)
        print(f"✅ SQL saved to: {output_path}")

    elif args.command == "mermaid":
        generate_mermaid_erd(metadata, args.ensemble)

    elif args.command == "validate":
        from ovm_erd.validator import validate_metadata
        validate_metadata(metadata, args.ensemble)

if __name__ == "__main__":
    main()
