import json
import ntpath


NAMESPACES = {"1.json": "http://purl.obolibrary.org/obo/MBA_",
              "17.json": "http://purl.obolibrary.org/obo/DMBA_",
              "10.json": "http://purl.obolibrary.org/obo/HBA_",
              "16.json": "http://purl.obolibrary.org/obo/DHBA_",
              "8.json": "http://purl.obolibrary.org/obo/PBA_"}


def read_structure_graph(graph_json):
    f = open(graph_json, 'r')
    j = json.loads(f.read())
    data_list = list()
    namespace = NAMESPACES[ntpath.basename(graph_json)]
    for root in j["msg"]:
        tree_recurse(root, data_list, namespace)
    f.close()
    return data_list


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
