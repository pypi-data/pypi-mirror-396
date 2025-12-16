import tests.http.configuration as cfg
from pytest import raises

from unrealircd_rpc_py.exceptions.rpc_exceptions import RpcProtocolError

def test_wrong_link():
    """## Wrong link
    """
    assert raises(Exception, cfg.start_requests_connection_with_invalid_readonly_credentials, match='Page not found. (404)')

def test_invalid_auth_requests():
    """## Authentication failed with requests
    """
    assert raises(Exception, cfg.start_requests_connection_with_invalid_readonly_credentials, match='Authentication required (401)')

def test_invalid_method():
    """## Invalid method
    """
    assert raises(RpcProtocolError, cfg.start_invalid_method_connection)
