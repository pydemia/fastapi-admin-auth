from opensearchpy import OpenSearch
from ..core.config import OpensearchConfig
import ssl


# host = 'localhost'
# port = 9200
# auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
# ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.
# client_cert_path = None
# client_key_path = None

def get_https_client(config: OpensearchConfig) -> OpenSearch:
    
    context = ssl.SSLContext()
    context.load_verify_locations(cadata=config.cacert)

    if config.verify_certs:
        client = OpenSearch(
            hosts = [{'host': config.host, 'port': config.port}],
            # hosts = [{'host': "opensearch.corus-ai.net", 'port': 9200}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (config.username, config.password),
            ssl_context=context,
            # ca_cert_data=config.cacert,
            # client_cert_data=config.cert,
            # client_key_data=config.certkey,
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl = config.use_ssl,
            verify_certs = config.verify_certs,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
            # ca_certs = ca_certs_path
        )
    else:
        ## HTTP
        # Create the client with SSL/TLS and hostname verification disabled.
        client = OpenSearch(
            hosts = [{'host': config.host, 'port': config.port}],
            http_compress = True, # enables gzip compression for request bodies
            use_ssl = True,
            http_auth = (config.username, config.password),
            verify_certs = config.verify_certs,
            ssl_assert_hostname = False,
            ssl_show_warn = False
        )

    return client