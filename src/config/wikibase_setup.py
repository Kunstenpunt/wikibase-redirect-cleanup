from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_login import Login

# De nodige configuratie voor onze wikibase instantie
wbi_config["DEFAULT_LANGUAGE"] = "nl"
wbi_config["WIKIBASE_URL"] = "https://kg.kunsten.be"
wbi_config["MEDIAWIKI_API_URL"] = "https://kg.kunsten.be/w/api.php"
wbi_config["MEDIAWIKI_INDEX_URL"] = "https://kg.kunsten.be/w/index.php"
wbi_config["MEDIAWIKI_REST_URL"] = "https://kg.kunsten.be/w/rest.php"
wbi_config["SPARQL_ENDPOINT_URL"] = (
    "https://kg.kunsten.be/query/proxy/wdqs/bigdata/namespace/wdq/sparql"
)


def create_login(user: str, password: str) -> Login:
    """Create and return a logged-in session for the given credentials."""
    return Login(user=user, password=password)
