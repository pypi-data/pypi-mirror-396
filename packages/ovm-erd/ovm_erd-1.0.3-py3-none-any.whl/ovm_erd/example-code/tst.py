# from ovm_erd.erd_sql import erd_sql

# erd_sql(path="C:/Temp/datavault-layer", ensemble="activity")


#from ovm_erd import erd_graphviz

#erd_graphviz(path=r"C:/Temp/datavault-layer", ensemble="activity")

# python -m ovm_erd sql --path C:/Temp/datavault-layer --ensemble activity
# python -m ovm_erd graphviz --path C:/Users/fouwe/Downloads/models/datavault-layer/raw_vault --ensemble distinct



#from ovm_erd.erd_drawio import generate_drawio_xml
#from ovm_erd.repository_reader import read_repository, build_metadata_dict

#files = read_repository("C:/Temp/datavault-layer")
#metadata = build_metadata_dict(files)

#generate_drawio_xml(metadata, output_file="ovm_erd/output/erd_core.drawio.xml")
#python -m ovm_erd graphviz --path C:/Temp/datavault-layer --ensemble activity
#python -m ovm_erd sql --ensemble ...
# python -m ovm_erd drawio --path C:/Temp/datavault-layer --ensemble activity

# python -m ovm_erd validate --path C:/Temp/datavault-layer

#python -m ovm_erd mermaid --path "C:/Temp/datavault-layer" --ensemble activity


from ovm_erd.repository_reader import read_repository
from ovm_erd.export import export_repository_json

files = read_repository("python -m ovm_erd graphviz --path C:/Users/fouwe/Downloads/models/datavault-layer/raw_vault --ensemble distinct")
export_repository_json(files)


