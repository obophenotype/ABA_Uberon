import argparse
import json
import pandas as pd
import csv
import ntpath


NAMESPACES = {"1.json": "http://purl.obolibrary.org/obo/MBA_",
              "17.json": "http://purl.obolibrary.org/obo/DMBA_",
              "10.json": "http://purl.obolibrary.org/obo/HBA_",
              "16.json": "http://purl.obolibrary.org/obo/DHBA_",
              "8.json": "http://purl.obolibrary.org/obo/PBA_"}


def generate_template(graph_json, output):
    f = open(graph_json, 'r')
    j = json.loads(f.read())
    data_list = list()
    namespace = NAMESPACES[ntpath.basename(graph_json)]

    for root in j["msg"]:
        tree_recurse(root, data_list, namespace)

    data_template = pd.DataFrame.from_records(data_list)
    data_template.to_csv(output, sep="\t", index=False, quoting=csv.QUOTE_NONE)
    f.close()


def tree_recurse(node, dl, namespace):
    d = dict()
    d["id"] = namespace + str(node["id"])
    d["name"] = str(node["name"])
    d["acronym"] = node["acronym"]
    if node["parent_structure_id"]:
        d["parent_structure_id"] = namespace + str(node["parent_structure_id"])
    d["subclass_of"] = "UBERON:0002616"
    dl.append(d)

    for child in node["children"]:
        tree_recurse(child, dl, namespace)


parser = argparse.ArgumentParser(description='Cli interface structure graph linkml template generation.')

parser.add_argument('-i', '--input', help="Path to input JSON file")
parser.add_argument('-o', '--output', help="Path to output TSV file")

args = parser.parse_args()

generate_template(args.input, args.output)
