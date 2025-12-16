import tests.http.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_http_admin_connection()

sb_obj = rpc.Server_ban

def test_server_ban_list():
    """Server Ban List"""
    response = sb_obj.list_()

    for sb in response:
        assert isinstance(sb, Dfn.ServerBan)
        assert sb.error.code == 0


def test_server_ban_get():
    """Server Ban List"""
    response = sb_obj.get('zline', '*@195.86.232.81')
    
    assert isinstance(response, Dfn.ServerBan)
    assert response.error.code == 0

    response = sb_obj.get('zline', 'impossible_to_find')
    assert response.error.code == -32602

    response = sb_obj.get('zline', '*@195.86.232.8151')
    
    assert isinstance(response, Dfn.ServerBan)
    assert response.error.code == -1000

def test_server_ban_add():
    """Server Ban List"""
    response = sb_obj.add('zline', '*@172.10.10.25', 'Test Jsonrpc server ban', 'Never', 'permanent', 'jsonrpc_user')
    assert isinstance(response, Dfn.RPCResult)
    assert response.error.code == 0

    response = sb_obj.add('zline', '*@172.10.10.35', 'Test Jsonrpc server ban', 'Never', '5s', 'jsonrpc_user')
    assert isinstance(response, Dfn.RPCResult)
    assert response.error.code == 0

def test_server_ban_del():
    """Server Ban List"""
    response = sb_obj.del_('zline', '*@172.10.10.25', 'jsonrpc_user')
    assert isinstance(response, Dfn.RPCResult)
    assert response.error.code == 0

    response = sb_obj.del_('zline', '*@172.10.10.35', 'jsonrpc_user')
    assert isinstance(response, Dfn.RPCResult)
    assert response.error.code == 0