def entity_id_from_uri(uri, prefix="https://kg.kunsten.be/entity/"):
    return uri.replace(prefix, "")


def statement_redirect_query_result_to_edit_list(query_result):
    edit_list = []
    for row in query_result["results"]["bindings"]:
        edit_row = []
        # Statement GUIDs are returned by query as
        # Q1334257-ABD96D2C-0021-4908-915B-E6BD1D3EEA9F
        # but wbgetclaims / wbsetclaim expects them of the form
        # Q1334257$ABD96D2C-0021-4908-915B-E6BD1D3EEA9F
        edit_row.append(
            entity_id_from_uri(
                row["subject"]["value"],
                prefix="https://kg.kunsten.be/entity/statement/",
            ).replace("-", "$", 1)
        )
        edit_row.append(entity_id_from_uri(row["old"]["value"]))
        edit_row.append(entity_id_from_uri(row["new"]["value"]))
        edit_list.append(edit_row)
    return edit_list


def double_redirects_query_result_to_edit_list(query_result):
    edit_list = []
    for row in query_result["results"]["bindings"]:
        edit_row = []
        edit_row.append(entity_id_from_uri(row["old"]["value"]))
        edit_row.append(entity_id_from_uri(row["new"]["value"]))
        edit_row.append(entity_id_from_uri(row["newer"]["value"]))
        edit_list.append(edit_row)
    return edit_list
