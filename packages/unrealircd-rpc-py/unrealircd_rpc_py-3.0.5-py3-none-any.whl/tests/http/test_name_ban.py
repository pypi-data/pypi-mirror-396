import tests.http.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_http_admin_connection()

def test_name_ban_list():
    """Test Name ban
    """
    nobj = rpc.Name_ban

    name_ban = nobj.list_()
    assert isinstance(name_ban, list)

    # Test connection response
    if name_ban:
        assert name_ban[0].error.code == 0
        for i in name_ban:
            assert isinstance(i, Dfn.NameBan)
            assert isinstance(i.error, Dfn.RPCErrorModel)

def test_name_ban_get():
    """Test Name Ban get
    """
    obj = rpc.Name_ban

    get_name_ban = obj.get('*C*h*a*n*S*e*r*v*')
    assert isinstance(get_name_ban, Dfn.NameBan)
    assert isinstance(get_name_ban.error, Dfn.RPCErrorModel)
    assert get_name_ban.error.code == 0

    get_name_ban = obj.get('IMPOSSIBLE_TO_FIND_THIS_NAME')
    assert isinstance(get_name_ban, Dfn.NameBan)
    assert isinstance(get_name_ban.error, Dfn.RPCErrorModel)
    assert get_name_ban.error.code == -1000
    assert get_name_ban.error.message == 'Ban not found'

def test_name_ban_add():
    """Test Name Ban add
    """
    obj = rpc.Name_ban

    get_name_ban = obj.add('pytest_name_ban', 'reason of the name ban', 'pytest')
    assert isinstance(get_name_ban, Dfn.RPCResult)
    assert isinstance(get_name_ban.error, Dfn.RPCErrorModel)
    assert get_name_ban.error.code == 0

def test_name_ban_del():
    """Test name ban Del
    """
    obj = rpc.Name_ban

    get_name_ban = obj.del_('pytest_name_ban', 'pytest')
    assert isinstance(get_name_ban, Dfn.RPCResult)
    assert isinstance(get_name_ban.error, Dfn.RPCErrorModel)
    assert get_name_ban.error.code == 0

    get_name_ban = obj.del_('IMPOSSIBLE_TO_FIND_THIS_NAME', 'pytest')
    assert isinstance(get_name_ban, Dfn.RPCResult)
    assert isinstance(get_name_ban.error, Dfn.RPCErrorModel)
    assert get_name_ban.error.code == -1000
    assert get_name_ban.error.message == 'Ban not found'