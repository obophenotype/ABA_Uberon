import argparse
import os
import pandas as pd
from relation_validator import read_csv_to_dict


def generate_mapping_source_template(old_mapping_path:str, new_mapping_path:str, output_path:str):
    old_headers, old_records = read_csv_to_dict(old_mapping_path, delimiter="\t")
    new_headers, new_records = read_csv_to_dict(new_mapping_path, delimiter="\t")

    robot_template_seed = {'ID': 'ID',
                           'Source': '>A oboInOwl:source'
                           }
    dl = [robot_template_seed]

    for new_id in new_records:
        if new_id in old_records:
            if new_records[new_id]["Equivalent"] and \
                    new_records[new_id]["Equivalent"] == old_records[new_id]["?equivalent"]:
                d = dict()
                d["ID"] = new_id
                d["Source"] = "https://orcid.org/0000-0002-6601-2165"
                dl.append(d)
            if new_records[new_id]["Subclass part of"] and \
                    new_records[new_id]["Subclass part of"] == old_records[new_id]["?parent"]:
                d = dict()
                d["ID"] = new_id
                d["Source"] = "https://orcid.org/0000-0002-6601-2165"
                dl.append(d)

    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_path, sep="\t", index=False)


parser = argparse.ArgumentParser(description='Process old and new mapping files and decide source of the mapping.')
parser.add_argument('-i1', '--input1', help="Path to old mapping TSV file")
parser.add_argument('-i2', '--input2', help="Path to new mapping TSV file")
parser.add_argument('-o', '--output', help="Path to output TSV file")

args = parser.parse_args()

generate_mapping_source_template(args.input1, args.input2, args.output)
