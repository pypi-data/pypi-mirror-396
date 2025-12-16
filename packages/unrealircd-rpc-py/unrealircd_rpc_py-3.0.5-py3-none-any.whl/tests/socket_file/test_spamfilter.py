import tests.socket_file.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

obj = rpc.Spamfilter

def test_spamfilter_list():
    """Server Ban List"""
    sfilters = obj.list_()
    assert isinstance(sfilters, list)

    for spam in sfilters:
        assert isinstance(spam, Dfn.Spamfilter)
        assert spam.error.code == 0

def test_spamfilter_get():
    """Server Ban List"""
    
    sfilter = obj.get(
        name="*Hey*come watch me on my webcam*",
        match_type="simple",
        spamfilter_targets="cp",
        ban_action="kill"
    )
    assert isinstance(sfilter, Dfn.Spamfilter)
    assert sfilter.error.code == 0

    sfilter = obj.get(
        name="impossible_to_find_this_name",
        match_type="simple____",
        spamfilter_targets="cp____",
        ban_action="gline_____"
    )
    assert isinstance(sfilter, Dfn.Spamfilter)
    assert isinstance(sfilter.error, Dfn.RPCErrorModel)
    assert sfilter.error.code != 0

def test_spamfilter_add():
    """Server Ban List"""
    sfilter = obj.add(
        name="jsonrpc_add_spam",
        match_type="simple",
        ban_action="kill",
        ban_duration=1,
        spamfilter_targets="cp",
        reason="Coming from jsonrpc",
        set_by="json_user"
    )
    assert isinstance(sfilter, Dfn.RPCResult)
    assert isinstance(sfilter.error, Dfn.RPCErrorModel)
    assert sfilter.error.code == 0

    sfilter = obj.add(
        name="jsonrpc_add_spam",
        match_type="simple",
        ban_action="kill",
        ban_duration=1,
        spamfilter_targets="cp",
        reason="Coming from jsonrpc",
        set_by="json_user"
    )
    assert isinstance(sfilter, Dfn.RPCResult)
    assert isinstance(sfilter.error, Dfn.RPCErrorModel)
    assert sfilter.error.code == -1001 and sfilter.error.message == "A spamfilter with that regex+action+target already exists"

def test_spamfilter_del():
    """Server Ban List"""
    sfilter = obj.del_(
        name="jsonrpc_add_spam",
        match_type="simple",
        ban_action="kill",
        spamfilter_targets="cp",
        _set_by="json_user"
    )
    assert isinstance(sfilter, Dfn.RPCResult)
    assert isinstance(sfilter.error, Dfn.RPCErrorModel)
    assert sfilter.error.code == 0