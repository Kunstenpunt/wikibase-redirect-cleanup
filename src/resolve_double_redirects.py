from utils.csv_logger import Logger
from utils.utils import double_redirects_query_result_to_edit_list
from wikibaseintegrator.wbi_helpers import (
    execute_sparql_query,
    mediawiki_api_call_helper,
)


def run_resolve_double_redirects(login, output=print, error_log_path=None):
    """Resolve redirects that point to other redirects instead of the final entity.

    Args:
        login: A wikibaseintegrator Login object (from create_login in config.wikibase_setup).
        output: A callable for status/output messages (default: print).
        error_log_path: Optional path to a CSV file for logging errors.
    """
    query = """
    SELECT DISTINCT ?old ?new ?newer
    WHERE {
      ?old owl:sameAs ?new .
      ?new owl:sameAs ?newer .
    }
    """

    output(
        f"Executing query to obtain redirects that point to single redirects:\n{query}"
    )
    query_result = execute_sparql_query(query)
    edit_list = double_redirects_query_result_to_edit_list(query_result)
    total = len(edit_list)
    output(f"Query returned {total} redirects that need editing.")
    if total == 0:
        return

    if error_log_path:
        logger = Logger(error_log_path)
        logger.write_row(
            ["old_id", "new_id", "newer_id", "error_type", "error_message"]
        )
    else:
        logger = None

    for index, [old_id, new_id, newer_id] in enumerate(edit_list):
        output(
            f"Changing redirect {old_id} to point directly to {newer_id} instead of {new_id} ({index + 1}/{total})"
        )

        params = {
            "action": "wbcreateredirect",
            "from": old_id,
            "to": newer_id,
        }

        try:
            result = mediawiki_api_call_helper(data=params, login=login)
            output(result)
        except Exception as err:
            if logger is not None:
                logger.write_row([old_id, new_id, newer_id, type(err), err])
            output(f"Error while calling wbcreateredirect: {err}, {type(err)}")
