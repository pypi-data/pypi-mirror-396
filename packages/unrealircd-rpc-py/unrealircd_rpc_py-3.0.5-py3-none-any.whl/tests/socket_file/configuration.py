'''
You must connect to unrealircd
    - You must connect a nickname on the ircd server
    - The nickname must be set to adator_test
    - Join a channel #jsonrpc
'''
from typing import TYPE_CHECKING, Literal
from unrealircd_rpc_py.ConnectionFactory import ConnectionFactory

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection

__debug_level: Literal[50] = 50

__valid_url = 'https://172.18.132.244:8600/api'
__valid_path_to_socket_file = '/home/adator/unrealircd/data/rpc.socket'

__valid_admin_username = 'admin-for-test'
__valid_admin_password = 'TUbFAFHF!$+*TnAnNVY#AasER)Wu5ZVw'

__valid_readonly_username = 'readonly-for-test'
__valid_readonly_password = 'TUbFAFHF!$+*TnAnNVY#AasER)Wu5ZVw'

def start_valid_socket_admin_connection() -> 'IConnection':
    # Connect To Factory
    conn = ConnectionFactory(debug_level=__debug_level).get('unixsocket')

    # Setup the connection
    conn.setup({'path_to_socket_file': __valid_path_to_socket_file})
    return conn

def start_socket_connection_with_wrong_link() -> 'IConnection':

    # Connect To Factory
    conn = ConnectionFactory(debug_level=__debug_level).get('unixsocket')

    # Setup the connection
    conn.setup({
        'path_to_socket_file': __valid_url + "__WRONG_LINK"
        })
    return conn

def start_valid_http_admin_connection() -> 'IConnection':

    # Connect To Factory
    conn = ConnectionFactory(debug_level=__debug_level).get('http')

    # Setup the connection
    conn.setup({
        'url': __valid_url, 
        'username': __valid_admin_username, 
        'password': __valid_admin_password
        })

    return conn

def start_requests_connection_with_invalid_readonly_credentials() -> 'IConnection':
    """## Authentication failed with requests
    """
    # Connect To Factory
    conn = ConnectionFactory(debug_level=__debug_level).get('http')

    # Setup the connection
    conn.setup({
        'url': __valid_url, 
        'username': '', 
        'password': ''
        })
    return conn

def start_requests_connection_with_wrong_link() -> 'IConnection':

    # Connect To Factory
    conn = ConnectionFactory(debug_level=__debug_level).get('http')

    # Setup the connection
    conn.setup({
        'url': __valid_url + "__WRONG_LINK",
        'username': __valid_readonly_username, 
        'password': __valid_readonly_password
        })
    return conn

def start_invalid_method_connection():
    """## Invalid method
    """
    # Connect To Factory
    conn = ConnectionFactory(debug_level=__debug_level).get('https')

    # Setup the connection
    conn.setup({
        'url': __valid_url + "__WRONG_LINK",
        'username': __valid_readonly_username, 
        'password': __valid_readonly_password
        })
    return conn

'''
def start_valid_socket_readonly_connection() -> Loader:

    return Loader(
        req_method='socket',
        url=__valid_url,
        username=__valid_readonly_username,
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_valid_requests_readonly_connection() -> Loader:

    return Loader(
        req_method='requests',
        url=__valid_url,
        username=__valid_readonly_username,
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_socket_readonly_connection_with_wrong_credentials() -> Loader:

    return Loader(
        req_method='socket',
        url=__valid_url,
        username=f'{__valid_readonly_username}-wrong-user',
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_socket_readonly_connection_with_wrong_link() -> Loader:

    return Loader(
        req_method='socket',
        url=f'{__valid_url}-wrong-link',
        username=__valid_readonly_username,
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_invalid_method_connection():
    """## Invalid method
    """
    return Loader(
                req_method='mynewmethod',
                url=__valid_url,
                username='',
                password='',
                debug_level=__debug_level
            )

'''