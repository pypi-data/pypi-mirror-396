import unrealircd_rpc_py.objects.Definition as Dfn
import tests.http.configuration as cfg

rpc =cfg.start_valid_http_admin_connection()

nickname = cfg.nickname_test
nickname_new = 'rpc_test'
username = 'rpc_test'

nickname_not_available = 'xxxxxxx'


def test_get_user():
    """Get a user adator"""

    user_obj = rpc.User

    client = user_obj.get(nickname)
    assert client.name == nickname
    assert isinstance(client, Dfn.Client)
    assert isinstance(client.geoip, Dfn.Geoip)
    assert isinstance(client.tls, Dfn.Tls)
    assert isinstance(client.user, Dfn.User)
    for channel in client.user.channels:
        assert isinstance(channel, Dfn.UserChannel)

    get_user = user_obj.get('nickname_not_available_for_sure')
    assert isinstance(get_user, Dfn.Client)
    assert get_user.error.message == 'Nickname not found'

def test_list_users():
    """Get a user adator"""

    user_obj = rpc.User

    for i in range(1, 4):
        list_user = user_obj.list_(i)
        assert isinstance(list_user, list)

    list_user = user_obj.list_(4)
    for client in list_user:
        assert isinstance(client, Dfn.Client)
        assert isinstance(client.geoip, Dfn.Geoip)
        assert isinstance(client.tls, Dfn.Tls)
        assert isinstance(client.user, Dfn.User)
        for channel in client.user.channels:
            assert isinstance(channel, Dfn.UserChannel)

    # Error level 3 doesnt exist
    list_client = user_obj.list_(3)
    assert list_client[0].error.code == -32602

def test_set_nick():
    """Get a user adator"""

    user_obj = rpc.User
    set_nick = user_obj.set_nick(nickname, nickname_new, True)
    assert isinstance(set_nick, Dfn.RPCResult)
    assert set_nick.error.code == 0

    # Set nick on non available nickname
    set_nick = user_obj.set_nick(nickname_not_available, 'adator_test', True)
    assert isinstance(set_nick, Dfn.RPCResult)
    assert set_nick.error.code == -1000
    assert set_nick.error.message == 'Nickname not found'

    # Re Init the nickname
    set_nick = user_obj.set_nick(nickname_new, nickname, True)
    assert isinstance(set_nick, Dfn.RPCResult)
    assert set_nick.result == True

def test_set_username():
    """Get a user adator"""

    user_obj = rpc.User

    set_username = user_obj.set_username(nickname, username)
    assert isinstance(set_username, Dfn.RPCResult)

    # New username
    if set_username.error.code == 0:
        assert set_username.result == True
    # Old and new user name are identical (-1001)
    else: 
        assert set_username.error.code == -1001

    set_username = user_obj.set_username(nickname_not_available, 'adator_test')
    assert isinstance(set_username, Dfn.RPCResult)
    assert set_username.error.code == -1000

def test_set_realname():
    """Set realname"""

    user_obj = rpc.User

    set_real = user_obj.set_realname('adator_test', 'jrpc_test')
    assert isinstance(set_real, Dfn.RPCResult)
    assert set_real.result == True

    set_real = user_obj.set_realname('adator_test', 'jrpc_original')
    assert isinstance(set_real, Dfn.RPCResult)
    assert set_real.result == True
    assert set_real.error.code == 0

    set_real = user_obj.set_realname('xxxxxx', 'adator_test')
    assert isinstance(set_real, Dfn.RPCResult)
    assert set_real.error.code == -1000
    assert set_real.error.message == 'Nickname not found'

def test_set_vhost():
    """Set realname"""

    user_obj = rpc.User

    set_vhost = user_obj.set_vhost('adator_test', 'jsonrpc.deb.biz.st')
    assert isinstance(set_vhost, Dfn.RPCResult)
    assert set_vhost.result == True

    set_vhost = user_obj.set_vhost('adator_test', 'jsonrpc_original.deb.biz.st')
    assert isinstance(set_vhost, Dfn.RPCResult)
    assert set_vhost.error.code == 0

    set_vhost = user_obj.set_vhost('xxxxxx', 'jsonrpc.deb.biz.st')
    assert isinstance(set_vhost, Dfn.RPCResult)
    assert set_vhost.error.code != 0

def test_set_mode():
    """Set realname"""

    user_obj = rpc.User

    set_mode = user_obj.set_mode('adator_test', '-o')
    assert isinstance(set_mode, Dfn.RPCResult)
    assert set_mode.error.code == 0

    set_mode = user_obj.set_mode('adator_test', '+t')
    assert isinstance(set_mode, Dfn.RPCResult)
    assert set_mode.error.code == 0

    set_mode = user_obj.set_mode('adator_test', '-t')
    assert isinstance(set_mode, Dfn.RPCResult)
    assert set_mode.error.code == 0

    set_mode = user_obj.set_mode('xxxxxx', 'jsonrpc.deb.biz.st')
    assert isinstance(set_mode, Dfn.RPCResult)
    assert set_mode.error.code != 0

def test_set_snomask():
    """Set snomask"""

    user_obj = rpc.User

    set_snomask =  user_obj.set_snomask(nickname, '+s')
    assert isinstance(set_snomask, Dfn.RPCResult)
    assert set_snomask.error.code == 0
    
    set_snomask = user_obj.set_snomask(nickname, '-s')
    assert isinstance(set_snomask, Dfn.RPCResult)
    assert set_snomask.error.code == 0

    set_snomask = user_obj.set_snomask(nickname_not_available, '-x')
    assert isinstance(set_snomask, Dfn.RPCResult)
    assert set_snomask.error.code != 0


def test_set_oper():
    """Set oper"""

    user_obj = rpc.User

    set_oper = user_obj.set_oper(nickname, 'adator', 'adator')
    assert isinstance(set_oper, Dfn.RPCResult)
    assert set_oper.error.code == 0
