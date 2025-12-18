import os
from jinja2 import Template

def validate_metadata(metadata: dict, html_output="ovm_erd/output/validation_report.html"):
    """
    Validates metadata and generates an HTML report with detected issues.

    :param metadata: Dictionary containing all metadata entries
    :param html_output: Path to the output HTML file
    """
    issues = []
    all_pks = {d["pk"] for d in metadata.values() if d.get("pattern") == "hub"}

    for name, data in metadata.items():
        pattern = data.get("pattern", "")
        pk = data.get("pk", "")
        fk_list = data.get("fk", [])

        if not pattern:
            issues.append((name, "❌ No pattern detected (missing nk, fk, or hashdiff)"))

        if pattern == "sat":
            if not pk:
                issues.append((name, "❌ Satellite has no PK — cannot be linked to a hub"))
            elif pk not in all_pks:
                issues.append((name, f"❌ Satellite PK '{pk}' does not match any hub PKs"))

        if pattern == "link":
            if not fk_list:
                issues.append((name, "❌ Link has no FKs — cannot link to any hubs"))
            else:
                unmatched = [fk for fk in fk_list if fk not in all_pks]
                if unmatched:
                    issues.append((name, f"⚠️ Link FKs do not match any hub PKs: {', '.join(unmatched)}"))

    # HTML output with Jinja2
    template = Template("""
    <html>
    <head>
        <title>OVM ERD Validation Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2rem; }
            h1 { color: #333; }
            ul { line-height: 1.6; }
        </style>
    </head>
    <body>
        <h1>🔍 Validation Report</h1>
        {% if issues %}
            <ul>
            {% for name, msg in issues %}
                <li><strong>{{ name }}</strong>: {{ msg }}</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>✅ No issues found. All entities are correctly classified and linked.</p>
        {% endif %}
    </body>
    </html>
    """)
    html = template.render(issues=issues)
    os.makedirs(os.path.dirname(html_output), exist_ok=True)
    with open(html_output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Validation report saved: {html_output}")
