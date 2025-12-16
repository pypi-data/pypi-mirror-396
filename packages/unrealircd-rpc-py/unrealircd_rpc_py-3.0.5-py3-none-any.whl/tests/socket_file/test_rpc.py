import tests.socket_file.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

def test_rpc_info():
    """Test RPC Info
    """
    r = rpc.Rpc

    info = r.info()
    assert isinstance(info, list)

    # Test connection response
    if info:
        assert info[0].error.code == 0
        for i in info:
            assert isinstance(i, Dfn.RpcInfo)
            assert isinstance(i.error, Dfn.RPCErrorModel)


def test_rpc_set_issuer():
    """Test RPC set issuer
    """
    r = rpc.Rpc
    set_issuer = r.set_issuer('pytest')

    assert isinstance(set_issuer, Dfn.RPCResult)
    assert set_issuer.result == True
    assert isinstance(set_issuer.error, Dfn.RPCErrorModel)
    assert set_issuer.error.code == 0

def test_rpc_add_timer():
    # {"jsonrpc": "2.0", "method": "rpc.add_timer", "params": {"timer_id":"test","every_msec":1000,"request":{"jsonrpc": "2.0", "method": "stats.get", "params": {}, "id": 555}}, "id": 123}
    request = {"jsonrpc": "2.0", "method": "stats.get", "params": {}, "id": 555}
    add_timer = rpc.Rpc.add_timer('test_rpc_timer', 6000, request)
    assert isinstance(add_timer, Dfn.RPCResult)
    assert isinstance(add_timer.result, bool)
    assert add_timer.result

def test_rpc_del_timer():
    del_timer = rpc.Rpc.del_timer('test_rpc_timer')
    assert isinstance(del_timer, Dfn.RPCResult)
    assert del_timer.result is None