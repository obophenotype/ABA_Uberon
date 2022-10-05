"""
Mapping Report generator. Provides following reports:

- report_old_vs_new_bridge: Reports the ABA terms that are mapped in the legacy file (OLD_MAPPING_FILE) but not in the
new bridge ontology (LATEST_BRIDGE). Differences are printed to the console.
- report_json_vs_new_bridge: Reports the ABA terms that are defined in the json
(such as http://api.brain-map.org/api/v2/structure_graph_download/1.json, but we will use src/ontology/sources/1.ofn
since json is already processed and ontology generated) but not in the new bridge ontology
(MBA_BRIDGE). Differences are printed to the console with their Uberon parents.

Script uses FunOWL to read the ofn ontology format and this operation is pretty slow.
"""

import os
from rdflib import Graph
from funowl.converters.functional_converter import to_python
from relation_validator import read_csv_to_dict


SPARQL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../sparql/bridge_mappings_terms.sparql")
LATEST_BRIDGE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../aba_uberon.owl")
MBA_BRIDGE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ontology/new-bridges/new-uberon-bridge-to-mba.owl")
UBERON_WITH_BRIDGE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ontology/uberon_with_bridge.owl")
OLD_MAPPING_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../bridge/CCF_to_UBERON working list.tsv")
JSON_ONT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ontology/sources/1.ofn")


def query_mapped_entities(graph, query):
    """
    Runs given query in the given graph
    Args:
        graph: ontology graph
        query: query to run

    Returns: set of entity names
    """
    qres = graph.query(query)
    mapped_entities = set()
    index = 1
    for row in qres:
        print(str(index) + "- " + row.term)
        mapped_entities.add(str(row.term).strip())
        index += 1

    return mapped_entities


def read_ontology(ontology_path):
    """
    Reads ontology file in any format from the given path.

    Params:
        ontology_path: file path to the ontology
    Return: ontology graph
    """
    try:
        graph = Graph()
        print("reading ontology file...")
        graph.parse(ontology_path)
        print("ontology file read")
    except:
        graph = read_ofn_file(ontology_path)
    return graph


def read_ofn_file(ont_path):
    """
    Uses FunOWL to read ontology file in OWL functional syntax to rdflib graph.
    This function works very slow, but does the job.
    Params:
        ont_path: path of the ontology file in ofn format.

    Returns: rdflib graph object.
    """
    print("Converting functional syntax to rdf with FunOWL...")
    ont_doc = to_python(ont_path)
    graph = Graph()
    ont_doc.to_rdf(graph)
    print("RDF conversion completed!!!")

    return graph


def get_new_mapped_terms(ontology_path):
    """
    Gets ABA terms from the new bridge ontology.

    Params:
        ontology_path: ontology file path
    Returns: list of mapped ABA terms
    """
    try:
        graph = Graph()
        graph.parse(ontology_path)
    except:
        graph = read_ofn_file(ontology_path)
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


def get_ont_terms(ontology_path):
    """
    Gets ABA terms from the new bridge ontology.

    Params:
        ontology_path: ontology file path
    Returns: list of mapped ABA terms
    """
    graph = read_ontology(ontology_path)

    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX MBA: <http://purl.obolibrary.org/obo/MBA_>
    
    SELECT DISTINCT (str(?class) as ?term)
    WHERE {
      ?class a owl:Class .
      FILTER(strstarts(str(?class),str(MBA:)) )
    }
    """
    mapped_entities = query_mapped_entities(graph, query)

    return mapped_entities


def query_label(graph, entity):
    """
    Retrieves label of the given entity.

    Params:
        graph: ontology to query
        entity: ontology term to search
    Returns: labels joined with &
    """
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX MBA: <http://purl.obolibrary.org/obo/MBA_>

    SELECT DISTINCT (str(?class) as ?term) ?label
    WHERE {
      <entity_iri> rdfs:label ?label .
    }
    """.replace("entity_iri", entity)

    qres = graph.query(query)
    labels = set()
    for row in qres:
        labels.add(str(row.label).strip())

    return " & ".join(labels)


def query_parent(graph, entity):
    """
    Materialization didn't worked due to unsats so dynamically generating a complex query.

    Params:
        graph: ontology to query
        entity: MBA term to search
    Returns: most specific UBERON parents as string
    """
    query_start = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX UBERON: <http://purl.obolibrary.org/obo/UBERON_>
                PREFIX MBA: <http://purl.obolibrary.org/obo/MBA_>
        
                SELECT DISTINCT (str(?related_uberon) as ?term) (?uberon_lanel as ?label)
                WHERE {
                    <entity_name> a owl:Class.  
                """

    query_end = """
                     ?parentClass  owl:equivalentClass/
                                    owl:intersectionOf/
                                    rdf:rest*/rdf:first ?related_uberon.
                     FILTER( strstarts(str(?related_uberon),str(UBERON:)) )
                     ?related_uberon rdfs:label ?uberon_lanel . 
                    }
                """

    for i in range(7):
        query_mid = generate_path_query(i)

        query = (query_start + query_mid + query_end).replace("entity_name", entity)
        # print(query)
        qres = graph.query(query)
        parents = set()
        labels = set()
        for row in qres:
            parents.add(str(row.term).strip())
            labels.add(str(row.label).strip())
        if parents:
            return " & ".join(parents) + " (" + " & ".join(labels) + ")"

    return ""


def generate_path_query(i):
    """
    Dynamically generating fixed length super class queries such as:
        <entity_name> rdfs: subClassOf / owl:someValuesFrom ?p1.
        FILTER(strstarts(str(?p1), str(MBA:)) )
        ?p1 rdfs: subClassOf / owl:someValuesFrom ?parentClass.
        FILTER(strstarts(str(?parentClass), str(MBA:)) )

    Params:
        i: depth of Uberon parent to search
    Returns: fixed length parent query section.
    """
    query_mid = ""
    for j in range(i + 1):
        s_name = "?p" + str(j)
        o_name = "?p" + str(j + 1)

        if j == 0:
            s_name = "<entity_name>"
        if j == i:
            o_name = "?parentClass"

        query_mid += """
                    {} rdfs:subClassOf/owl:someValuesFrom {} .
                    FILTER( strstarts(str({}),str(MBA:)) )
                    """.format(s_name, o_name, o_name)
    return query_mid


def report_old_vs_new_bridge():
    """
    Reports the ABA terms that are mapped in the legacy file (OLD_MAPPING_FILE) but not in the new bridge ontology
    (LATEST_BRIDGE). Differences are printed to the console.
    """
    new_terms = get_new_mapped_terms(LATEST_BRIDGE)
    old_terms = get_old_mapped_terms()
    terms_not_in_new = old_terms.difference(new_terms)
    print("=======================================================")
    print("Terms that exist in the old mapping but not in the new one:")
    counter = 1
    for entity in terms_not_in_new:
        print(str(counter) + "- " + entity)
        counter += 1


def report_json_vs_new_bridge():
    """
    Reports the ABA terms that are defined in the json
    (such as http://api.brain-map.org/api/v2/structure_graph_download/1.json, but we will use src/ontology/sources/1.ofn
    since json is already processed and ontology generated) but not in the new bridge ontology
    (MBA_BRIDGE). Differences are printed to the console with their Uberon parents.
    """
    new_terms = get_ont_terms(MBA_BRIDGE)
    json_terms = get_ont_terms(JSON_ONT)
    terms_not_in_new = json_terms.difference(new_terms)
    print("=======================================================")
    print("Bridge term count: " + str(len(new_terms)))
    print("Json term count: " + str(len(json_terms)))
    print("Terms that exist in the json but not in the mba bridge")
    counter = 1

    g = read_ontology(UBERON_WITH_BRIDGE)
    for entity in terms_not_in_new:
        print(str(counter) + "- " + entity + " (" + query_label(g, entity) + ")" + " - " + query_parent(g, entity))
        counter += 1


if __name__ == '__main__':
    # report_old_vs_new_bridge()
    report_json_vs_new_bridge()
