from ovm_erd.repository_reader import read_repository, build_metadata_dict


def generate_sql_query(metadata: dict, ensemble: str) -> str:
    """
    Generates a SQL query based on metadata for a specific ensemble/tag.
    Connects hubs with sats and links using INNER JOINs.

    :param metadata: Full (filtered) metadata dictionary
    :param ensemble: The tag for which the SQL query is generated
    :return: SQL query string
    """
    filtered = {
        fn: d for fn, d in metadata.items()
        if ensemble in d.get("tags", [])
    }

    if not filtered:
        return f"-- ⚠️ No tables found for ensemble: {ensemble}"

    from_clause = []
    joins = []
    added = set()

    for data in filtered.values():
        name = data["table_name"]
        pattern = data.get("pattern", "")
        pk = data.get("pk", "")
        fk_list = data.get("fk", [])

        if pattern == "hub":
            from_clause.append(name)
            added.add(name)

            # Join sats
            for sat_data in filtered.values():
                if sat_data.get("pattern") == "sat" and sat_data.get("pk") == pk:
                    sat = sat_data["table_name"]
                    joins.append(f"INNER JOIN {sat} ON {sat}.{pk} = {name}.{pk}")
                    added.add(sat)

            # Join links (with all hubs matching any FK)
            for link_data in filtered.values():
                if link_data.get("pattern") == "link":
                    link = link_data["table_name"]
                    for fk in link_data.get("fk", []):
                        if fk == pk:
                            join_line = f"INNER JOIN {link} ON {link}.{fk} = {name}.{pk}"
                            if join_line not in joins:
                                joins.append(join_line)
                                added.add(link)

    tables_used = from_clause + [j.split()[2] for j in joins]
    select_clause = ",\n    ".join([f"{t}.*" for t in tables_used])

    query = f"SELECT\n    {select_clause}\nFROM\n    {from_clause[0]}\n"
    if joins:
        query += "\n" + "\n".join(joins)

    return query


def erd_sql(path: str = "./examples", ensemble: str = "all"):
    """
    Entry point for the SQL generator CLI.
    Reads repository and metadata, generates query for given ensemble.
    """
    files = read_repository(path)
    metadata = build_metadata_dict(files)

    sql = generate_sql_query(metadata, ensemble)

    output_path = f"ovm_erd/output/query_{ensemble}.sql"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql)

    print(f"✅ SQL query generated and saved: {output_path}")
