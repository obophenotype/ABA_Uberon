import csv
import os
import pandas as pd


REL_REPORT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ontology/report/not_valid_relations.tsv")
REL_REPORT_LBL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ontology/report/not_valid_relations_lbl.tsv")

ALL_LABELS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../ontology/report/all_labels.csv")


def add_labels_to_report(report_path, labels_path, output_path):
    headers, records = read_csv_to_dict(report_path, delimiter="\t", generated_ids=True)
    labels = read_csv_to_dict(labels_path)[1]

    normalized_markers = []
    for row_num in records:
        normalized_data = {"o": records[row_num]["o"],
                           "s": records[row_num]["s"],
                           "olabel": records[row_num]["olabel"],
                           "slabel": records[row_num]["slabel"],
                           "user_oiri": records[row_num]["user_olabel"],
                           "user_olabel": labels[records[row_num]["user_olabel"]]["label"],
                           "user_siri": records[row_num]["user_slabel"],
                           "user_slabel": labels[records[row_num]["user_slabel"]]["label"]
                           }

        normalized_markers.append(normalized_data)

    class_robot_template = pd.DataFrame.from_records(normalized_markers)
    class_robot_template.to_csv(output_path, sep="\t", index=False)


def read_csv_to_dict(csv_path, id_column=0, id_column_name="", delimiter=",", id_to_lower=False, generated_ids=False):
    """
    Reads tsv file content into a dict. Key is the first column value and the value is dict representation of the
    row values (each header is a key and column value is the value).
    Args:
        csv_path: Path of the CSV file
        id_column: Id column becomes the keys of the dict. This column should be unique. Default is the first column.
        id_column_name: Alternative to the numeric id_column, id_column_name specifies id_column by its header string.
        delimiter: Value delimiter. Default is comma.
        id_to_lower: applies string lowercase operation to the key
        generated_ids: If 'True', uses row number as the key of the dict. Initial key is 0.

    Returns:
        Function provides two return values: first; headers of the table and second; the CSV content dict. Key of the
        content is the first column value and the values are dict of row values.
    """
    records = dict()

    headers = []
    with open(csv_path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        row_count = 0
        for row in rd:
            _id = row[id_column]
            if id_to_lower:
                _id = str(_id).lower()
            if generated_ids:
                _id = row_count

            if row_count == 0:
                headers = row
                if id_column_name and id_column_name in headers:
                    id_column = headers.index(id_column_name)
            else:
                row_object = dict()
                for column_num, column_value in enumerate(row):
                    row_object[headers[column_num]] = column_value
                records[_id] = row_object

            row_count += 1

    return headers, records


if __name__ == '__main__':
    add_labels_to_report(REL_REPORT_PATH, ALL_LABELS_PATH, REL_REPORT_LBL_PATH)
