import tests.http.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()
__nickname__ = cfg.nickname_test
message = rpc.Message

def test_send_privmsg():
    """Test send_privmsg"""

    # Send the privmsg success
    send_privmsg = message.send_privmsg(__nickname__, 'Hello from JSONRPC')
    assert isinstance(send_privmsg, Dfn.RPCResult)
    assert send_privmsg.result

    # Send the privmsg with error
    send_privmsg = message.send_privmsg('nickname_not_found', 'FAIL Hello from JSONRPC')
    assert isinstance(send_privmsg, Dfn.RPCResult)
    assert send_privmsg.error.code != 0

def test_send_notice():
    """Test send_privmsg"""

    # Send the privmsg success
    send_notice = message.send_notice(__nickname__, 'Hello from JSONRPC notice')
    assert isinstance(send_notice, Dfn.RPCResult)
    assert send_notice.result

    # Send the privmsg with error
    send_notice = message.send_notice('nickname_not_found', 'FAIL Hello from JSONRPC')
    assert isinstance(send_notice, Dfn.RPCResult)
    assert send_notice.error.code != 0

def test_send_numeric():
    """Test send_numeric"""

    # Send the numeric success
    send_numeric = message.send_numeric(__nickname__, 5, 'Hello from JSONRPC send_numeric')
    assert isinstance(send_numeric, Dfn.RPCResult)
    assert send_numeric.result

    # Send the numeric with error
    send_numeric = message.send_numeric('nickname_not_found', 2, 'FAIL Hello from JSONRPC')
    assert isinstance(send_numeric, Dfn.RPCResult)
    assert send_numeric.error.code != 0