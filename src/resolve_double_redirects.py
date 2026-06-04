import argparse
import threading
from typing import Callable

from wikibaseintegrator import wbi_login
from wikibaseintegrator.wbi_helpers import (
    execute_sparql_query,
    mediawiki_api_call_helper,
)

import config.wikibase_setup as wb_config
from utils.csv_logger import Logger
from utils.utils import double_redirects_query_result_to_edit_list


def run_resolve_double_redirects(
    login: wbi_login.Login | None,
    output: Callable[[str], None] = print,
    error_log_path: str | None = None,
    cancel_event: threading.Event | None = None,
) -> None:
    """Resolve redirects that point to other redirects instead of the final entity.

    Args:
        login: A wikibaseintegrator Login object (from create_login in config.wikibase_setup).
        output: A callable for status/output messages (default: print).
        error_log_path: Optional path to a CSV file for logging errors.
        cancel_event: An optional threading.Event. When set, the function will
            stop processing further redirects as soon as possible.
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
        if cancel_event is not None and cancel_event.is_set():
            output("Cancellation requested — stopping resolve_double_redirects.")
            return

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
            output(str(result))
        except Exception as err:
            if logger is not None:
                logger.write_row([old_id, new_id, newer_id, str(type(err)), str(err)])
            output(f"Error while calling wbcreateredirect: {err}, {type(err)}")


if __name__ == "__main__":
    config = wb_config.sanitize(wb_config.load())
    wb_config.save(config)
    wb_config.apply(config)

    parser = argparse.ArgumentParser(
        description="Resolve double redirects in wikibase instance, using given username and botpassword. Make sure correct config info is present in adjacent config.json file."
    )
    parser.add_argument("username", help="Username for authentication")
    parser.add_argument("botpassword", help="Bot password for authentication")
    args = parser.parse_args()

    run_resolve_double_redirects(
        wb_config.create_login(args.username, args.botpassword)
    )
