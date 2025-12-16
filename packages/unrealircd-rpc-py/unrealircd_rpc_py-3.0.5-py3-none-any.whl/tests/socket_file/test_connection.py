import tests.socket_file.configuration as cfg
from pytest import raises

def test_wrong_link():
    """## Wrong link
    """
    assert raises(Exception, cfg.start_requests_connection_with_invalid_readonly_credentials, match='Page not found. (404)')
    assert raises(Exception, cfg.start_socket_connection_with_wrong_link)

def test_invalid_auth_requests():
    """## Authentication failed with requests
    """
    assert raises(Exception, cfg.start_requests_connection_with_invalid_readonly_credentials, match='Authentication required (401)')

def test_invalid_method():
    """## Invalid method
    """
    assert raises(Exception, cfg.start_invalid_method_connection, match='Invalid method!')
