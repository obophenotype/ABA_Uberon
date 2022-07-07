import os
import pandas as pd
from relation_validator import read_csv_to_dict


CCF_TO_UBERON_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     "../bridge/CCF_to_UBERON working list.csv")
CCF_TO_UBERON_TEMPLATE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../robot_templates/CCF_to_UBERON.tsv")

ALLOWED_NS = ["http://purl.obolibrary.org/obo/MBA_", "http://purl.obolibrary.org/obo/DMBA_"]


def generate_robot_template(mapping_path: str, output_filepath: str):
    headers, records = read_csv_to_dict(mapping_path, delimiter="\t", generated_ids=True)

    robot_template_seed = {'ID': 'ID',
                           'Label': 'A IAO:0000589',
                           'Subclass part of': 'SC part_of some %',
                           'Equivalent': 'EC %',
                           'SuperClass Label': '>A rdfs:label',
                           'Status': 'A oboInOwl:status',
                           'Approved by': '>A oboInOwl:source'
                           }
    dl = [robot_template_seed]

    for mapping in records:
        if records[mapping]["Analysis"] == "OK" and any(ns in records[mapping]["subclass_iri"] for ns in ALLOWED_NS):
            d = dict()
            d["ID"] = str(records[mapping]["subclass_iri"]).replace("<", "").replace(">", "")
            d["Label"] = records[mapping]["subclass_name"]
            d["Subclass part of"] = str(records[mapping]["superclass_iri"]).replace("<", "").replace(">", "")
            d["Equivalent"] = ''
            d["SuperClass Label"] = records[mapping]["superclass_name_linked"]
            d["Status"] = ''
            d["Approved by"] = ''
            dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


generate_robot_template(CCF_TO_UBERON_MAPPING, CCF_TO_UBERON_TEMPLATE)
