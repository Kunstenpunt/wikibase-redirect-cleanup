import json

from utils.csv_logger import Logger
from utils.utils import statement_redirect_query_result_to_edit_list
from wikibaseintegrator.wbi_helpers import (
    execute_sparql_query,
    mediawiki_api_call_helper,
)


def run_fix_statement_redirects(login, output=print, error_log_path=None):
    """Fix statements that point to redirected entities.

    Args:
        login: A wikibaseintegrator Login object (from create_login in config.wikibase_setup).
        output: A callable for status/output messages (default: print).
        error_log_path: Optional path to a CSV file for logging errors.
    """
    query = """
    SELECT DISTINCT ?subject ?old ?new
    WHERE {
      ?old owl:sameAs ?new .
      ?subject ?predicate ?old .
      ?subject wikibase:rank [] .
    }
    """

    output(f"Executing query to obtain statements that point to redirects:\n{query}")
    query_result = execute_sparql_query(query)
    edit_list = statement_redirect_query_result_to_edit_list(query_result)
    total = len(edit_list)
    output(f"Query returned {total} statements that need editing.")
    if total == 0:
        return

    if error_log_path:
        logger = Logger(error_log_path)
        logger.write_row(
            ["statement_id", "old_id", "new_id", "error_type", "error_message"]
        )
    else:
        logger = None

    for index, [statement_id, old_id, new_id] in enumerate(edit_list):
        output(
            f"Changing statement {statement_id} to accomodate redirect: {old_id} -> {new_id} ({index + 1}/{total})"
        )

        params = {
            "action": "wbgetclaims",
            "claim": statement_id,
        }
        result = mediawiki_api_call_helper(data=params, login=login, is_bot=True)
        result_json = json.dumps(list(result["claims"].values())[0][0])
        # Het lijkt alsof enkel de numeric-id aanpassen ook voldoende is,
        # maar voor het zeker toch beide nog doen
        updated_json = result_json.replace(f'"{old_id}"', f'"{new_id}"')
        updated_json = updated_json.replace(
            f'"numeric-id": {old_id[1:]}', f'"numeric-id": {new_id[1:]}'
        )

        params = {
            "action": "wbsetclaim",
            "claim": updated_json,
            "summary": "update value to accomodate redirect",
        }
        try:
            mediawiki_api_call_helper(data=params, login=login, is_bot=True)
        except Exception as err:
            if logger is not None:
                logger.write_row([statement_id, old_id, new_id, type(err), err])
            output(err)
