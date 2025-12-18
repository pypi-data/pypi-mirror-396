import xml.etree.ElementTree as ET
import uuid
import os

def generate_drawio_xml(metadata: dict, output_file="ovm_erd/output/erd.drawio.xml", diagram_title="ERD"):
    """
    Genereert een draw.io-compatible XML-bestand van het ERD op basis van de metadata.
    Tekenstijl: tabelstructuur per entiteit + lijnen met crow's feet. Layout is automatisch.
    """

    mxfile = ET.Element("mxfile", host="app.diagrams.net")
    diagram = ET.SubElement(mxfile, "diagram", name=diagram_title, autoLayout="1")
    graph_model = ET.SubElement(diagram, "mxGraphModel")
    root = ET.SubElement(graph_model, "root")

    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # Kleur per type
    colors = {
        "hub": "#D6EAF8",   # lichtblauw
        "sat": "#FFFACD",   # lichtgeel
        "link": "#F5B7B1"   # lichtrood
    }

    # Layout-instellingen
    x_start, y_start = 40, 40
    dx, dy = 250, 150
    cols = 4
    table_ids = {}

    # ENTITEITEN
    for idx, (filename, data) in enumerate(metadata.items()):
        table_name = data["table_name"]
        pattern = data.get("pattern", "hub")
        pk = data.get("pk", "")
        fk_list = data.get("fk", [])
        color = colors.get(pattern, "#FFFFFF")
        cell_id = f"id_{uuid.uuid4().hex[:8]}"
        table_ids[table_name] = cell_id

        # Attribuutinhoud
        lines = [f"<b>{table_name}</b>"]
        if pk:
            lines.append(f"pk: {pk}")
        for fk in fk_list:
            lines.append(f"fk: {fk}")
        value = "<br/>".join(lines)

        # XML blok
        cell = ET.SubElement(root, "mxCell", {
            "id": cell_id,
            "value": value,
            "style": f"shape=swimlane;html=1;whiteSpace=wrap;fillColor={color};strokeColor=#000000;",
            "vertex": "1",
            "parent": "1"
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x_start + (idx % cols) * dx),
            "y": str(y_start + (idx // cols) * dy),
            "width": "200",
            "height": "100",
            "as": "geometry"
        })

    # RELATIES (van hub naar sat/link)
    for data in metadata.values():
        src_type = data.get("pattern")
        src_table = data["table_name"]
        pk = data.get("pk", "")
        fk_list = data.get("fk", [])

        if src_type == "sat":
            for hub in metadata.values():
                if hub.get("pattern") == "hub" and hub.get("pk") == pk:
                    src_id = table_ids[hub["table_name"]]
                    dst_id = table_ids[src_table]
                    edge = ET.SubElement(root, "mxCell", {
                        "id": f"edge_{uuid.uuid4().hex[:8]}",
                        "style": "endArrow=open;endSize=16;startArrow=oval;edgeStyle=orthogonalEdgeStyle;rounded=0;",
                        "edge": "1",
                        "parent": "1",
                        "source": src_id,
                        "target": dst_id
                    })
                    ET.SubElement(edge, "mxGeometry", {
                        "relative": "1",
                        "as": "geometry"
                    })

        elif src_type == "link":
            for fk in fk_list:
                for hub in metadata.values():
                    if hub.get("pattern") == "hub" and hub.get("pk") == fk:
                        src_id = table_ids[hub["table_name"]]
                        dst_id = table_ids[src_table]
                        edge = ET.SubElement(root, "mxCell", {
                            "id": f"edge_{uuid.uuid4().hex[:8]}",
                            "style": "endArrow=open;endSize=16;startArrow=oval;edgeStyle=orthogonalEdgeStyle;rounded=0;",
                            "edge": "1",
                            "parent": "1",
                            "source": src_id,
                            "target": dst_id
                        })
                        ET.SubElement(edge, "mxGeometry", {
                            "relative": "1",
                            "as": "geometry"
                        })

    # Opslaan
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ draw.io diagram generated and saved: {output_file}")
