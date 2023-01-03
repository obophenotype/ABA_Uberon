import os
import re
import logging
import argparse
import csv
import urllib.request

from relation_validator import read_csv_to_dict
from structure_graph_utils import read_structure_graph
from abc import ABC, abstractmethod, ABCMeta
from os.path import isfile, join

MAPPING_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../robot_templates/mba_CCF_to_UBERON.tsv")
PATH_REPORT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../validation_report.txt")
STRUCTURE_GRAPH_URL = "http://api.brain-map.org/api/v2/structure_graph_download/"

SG_NAME_MAP = {"MBA": "1.json",
              "DMBA": "17.json",
              "HBA": "10.json",
              "DHBA": "16.json",
              "PBA": "8.json"}

log = logging.getLogger(__name__)


def save_report(report):
    f = open(PATH_REPORT, "w")
    for rep in report:
        f.write(rep+"\n")
    f.close()


class BaseChecker(ABC):

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def get_header(self):
        return "=== Default Checker :"


class StrictChecker(BaseChecker, metaclass=ABCMeta):
    """Failures of strict checks cause exceptions."""
    pass


class SoftChecker(BaseChecker, metaclass=ABCMeta):
    """Failures of soft checks cause warnings."""
    pass


class SingleMappingChecker(StrictChecker):
    """
    Only one of 'Equivalent' or 'Subclass part of' have value. If both has value, raises an error.
    """

    def __init__(self):
        self.reports = []

    def check(self):
        headers, records = read_csv_to_dict(MAPPING_FILE, delimiter="\t", generated_ids=True)
        for mapping in records:
            if records[mapping]["Equivalent"] and records[mapping]["Subclass part of"] \
                    and records[mapping]["ID"] != "ID":
                self.reports.append("{} has both Equivalent and SubClassOf".format(records[mapping]["ID"]))

    def get_header(self):
        return "=== Single Mapping Checks :"


class UniqueIdChecker(StrictChecker):
    """
    All IDs should be unique.
    """

    def __init__(self):
        self.reports = []

    def check(self):
        headers, records = read_csv_to_dict(MAPPING_FILE, delimiter="\t", generated_ids=True)
        id_mapping = dict()
        for line_number in records:
            mapped_id = records[line_number]["ID"]
            record = {
                "line": line_number + 1,
                "sc": records[line_number]["Subclass part of"],
                "ec": records[line_number]["Equivalent"]
            }
            if mapped_id in id_mapping:
                lines = id_mapping[mapped_id]
                lines.append(record)
                id_mapping[mapped_id] = lines
            else:
                id_mapping[mapped_id] = [record]

        for mapping_id in id_mapping:
            if len(id_mapping[mapping_id]) > 1:
                records = id_mapping[mapping_id]
                all_same = True
                base_record = None
                for record in records:
                    if not base_record:
                        base_record = record
                    else:
                        all_same &= (base_record["sc"] == record["sc"] and base_record["ec"] == record["ec"])

                if not all_same:
                    self.reports.append("{} exists in multiple lines: {} with different mappings."
                                        .format(mapping_id, ", ".join(str(record["line"]) for record in id_mapping[mapping_id])))

    def get_header(self):
        return "=== Unique Id Checks :"


class StructureGraphChecker(StrictChecker):
    """
    Compare mapping template with the original structure graph. All entities should exist in the structure graph
    and their label's should match.
    """

    def __init__(self):
        self.reports = []

    def check(self):
        mapping_file_name = MAPPING_FILE.rsplit('/', 1)[-1]
        # MBA, DMBA ...
        structure_graph_type = mapping_file_name.split("_")[0].upper()
        web_file_name = SG_NAME_MAP[structure_graph_type]
        urllib.request.urlretrieve(STRUCTURE_GRAPH_URL + web_file_name, web_file_name)

        structure_graph_list = read_structure_graph(web_file_name)
        structure_graph = dict()
        for item in structure_graph_list:
            structure_graph[item["id"]] = item

        headers, records = read_csv_to_dict(MAPPING_FILE, delimiter="\t", generated_ids=True)
        for line_number in records:
            mapped_id = str(records[line_number]["ID"]).strip()
            if mapped_id and mapped_id != "ID" and not str(mapped_id).endswith(structure_graph_type + "_ENTITY"):
                if mapped_id not in structure_graph:
                    self.reports.append("{} not exists in the structure graph.".format(mapped_id))

        for line_number in records:
            mapped_id = records[line_number]["ID"]
            if mapped_id in structure_graph:
                if str(structure_graph[mapped_id]["name"]).lower().strip() != \
                        str(records[line_number]["Label"]).lower().strip():
                    self.reports.append("{} label is '{}' in template, but '{}' in the structure graph.".
                                        format(mapped_id,
                                               records[line_number]["Label"],
                                               structure_graph[mapped_id]["name"]))

    def get_header(self):
        return "=== Structure Graph Compatibility :"


class MappingValidator(object):

    rules = [SingleMappingChecker(), UniqueIdChecker(), StructureGraphChecker()]
    errors = []
    warnings = []

    def validate(self):
        for checker in self.rules:
            checker.check()
            if checker.reports:
                if isinstance(checker, StrictChecker):
                    self.errors.append("\n"+checker.get_header())
                    self.errors.extend(checker.reports)
                else:
                    self.warnings.append("\n"+checker.get_header())
                    self.warnings.extend(checker.reports)


class ValidationError(Exception):

    def __init__(self, message, report):
        Exception.__init__(self)
        self.message = message
        self.report = report


def main(silent):
    log.info("Mapping validation started.")
    validator = MappingValidator()
    validator.validate()
    if not validator.errors and not validator.warnings:
        print("\nMarker validation successful.")
    elif not validator.errors:
        print("Warnings:")
        for rep in validator.warnings:
            print(rep)
        print("\nMarker validation completed with warnings.")
    else:
        print("\nErrors:")
        for rep in validator.errors:
            print(rep)
        if validator.warnings:
            print("\nWarnings:")
            for rep in validator.warnings:
                print(rep)
        print("\nMarker validation completed with errors.")
        if not silent:
            raise ValidationError("Marker validation completed with errors.", validator.errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args()
    main(args.silent)
