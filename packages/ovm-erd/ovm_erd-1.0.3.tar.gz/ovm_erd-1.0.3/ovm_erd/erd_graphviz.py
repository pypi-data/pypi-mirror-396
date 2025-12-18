from graphviz import Digraph
import os


class ERDGraphviz:
    def __init__(self, metadata):
        self.metadata = metadata
        self.graph = Digraph(format='png')
        self.graph.attr(rankdir="TB", layout="dot", splines="polyline")
        self.graph.attr('node', shape='box', style='filled', fontname='Helvetica')
        self.hubs = []
        self.sats = []
        self.links = []

    def classify_entities(self):
        for data in self.metadata.values():
            pattern = data.get("pattern", "")
            table = data["table_name"]
            if pattern == "hub":
                self.hubs.append(table)
            elif pattern == "link":
                self.links.append(table)
            elif pattern == "sat":
                self.sats.append(table)

    def add_entities(self):
        self.classify_entities()
        color_map = {
            "hub": "lightblue",
            "sat": "lightyellow",
            "link": "red3",
        }

        # Sats bovenaan
        with self.graph.subgraph() as s:
            s.attr(rank='min')
            for name in self.sats:
                s.node(name, fillcolor=color_map["sat"])

        # Hubs op zelfde niveau
        with self.graph.subgraph() as s:
            s.attr(rank='same')
            for name in self.hubs:
                s.node(name, fillcolor=color_map["hub"])

        # Links eronder
        for name in self.links:
            self.graph.node(name, fillcolor=color_map["link"])

    def add_relationships(self):
        for data in self.metadata.values():
            source = data["table_name"]
            pattern = data.get("pattern", "")
            pk = data.get("pk", "")
            fk_list = data.get("fk", [])

            if pattern == "sat":
                # SAT/LSAT/MSAT: maximaal één relatie
                linked = False
                for target in self.metadata.values():
                    if linked:
                        break
                    target_pattern = target.get("pattern")
                    if pk and pk == target.get("pk"):
                        if target_pattern in ["hub", "link"]:
                            self.graph.edge(source, target["table_name"], dir="none", arrowhead="none")
                            linked = True

            elif pattern == "link":
                for fk in fk_list:
                    for target in self.metadata.values():
                        if target.get("pattern") == "hub" and fk == target.get("pk"):
                            self.graph.edge(target["table_name"], source, dir="none", arrowhead="none")

    def generate(self, output_filename="erd_diagram"):
        self.add_entities()
        self.add_relationships()
        self.graph.render(filename=output_filename, cleanup=True)
        print(f"✅ ERD generated and saved as: {output_filename}.png")
