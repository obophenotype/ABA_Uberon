"""
Mapping Report generator

This script reports the ABA terms that are mapped in the legacy file (OLD_MAPPING_FILE) but not in the new bridge
ontology (LATEST_BRIDGE). Differences are printed to the console.

Script uses FunOWL to read the ofn ontology format and this operation is pretty slow.
"""

import os
from rdflib import Graph
from funowl.converters.functional_converter import to_python
from relation_validator import read_csv_to_dict


SPARQL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../sparql/bridge_mappings_terms.sparql")
LATEST_BRIDGE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../aba_uberon.owl")
OLD_MAPPING_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../bridge/CCF_to_UBERON working list.tsv")


def query_mapped_entities(graph, query):
    """
    Runs given query in the
    Args:
        graph:
        query:

    Returns:

    """
    qres = graph.query(query)
    mapped_entities = set()
    index = 1
    for row in qres:
        print(str(index) + "- " + row.term)
        mapped_entities.add(str(row.term).strip())
        index += 1

    return mapped_entities


def read_ofn_file(ont_path):
    """
    Uses FunOWL to read ontology file in OWL functional syntax to rdflib graph.
    This function works very slow, but does the job.
    Args:
        ont_path: path of the ontology file in ofn format.

    Returns: rdflib graph object.
    """
    print("Converting functional syntax to rdf with FunOWL...")
    ont_doc = to_python(ont_path)
    graph = Graph()
    ont_doc.to_rdf(graph)
    print("RDF conversion completed!!!")

    return graph


def get_new_mapped_terms():
    """
    Gets ABA terms from the new bridge ontology.
    Returns: list of mapped ABA terms
    """
    global query
    graph = read_ofn_file(LATEST_BRIDGE)
    # read query from file
    with open(SPARQL_PATH, "r") as f:
        query = f.read()
    mapped_entities = query_mapped_entities(graph, query)

    return mapped_entities


def get_old_mapped_terms():
    """
    Gets ABA terms from the legacy mapping table.
    Returns: list of mapped ABA terms
    """
    headers, records = read_csv_to_dict(OLD_MAPPING_FILE, delimiter="\t", generated_ids=True)
    legacy_terms = set()
    for row_num in records:
        legacy_terms.add(str(records[row_num]["subclass_iri"]).strip().lstrip("<").rstrip(">"))
    return legacy_terms


if __name__ == '__main__':
    new_terms = get_new_mapped_terms()
    old_terms = get_old_mapped_terms()
    terms_not_in_new = old_terms.difference(new_terms)

    print("=======================================================")
    print("Terms that exist in the old mapping but not in the new one:")
    counter = 1
    for entity in terms_not_in_new:
        print(str(counter) + "- " + entity)
        counter += 1
