import tests.socket_file.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

whowas = rpc.Whowas

def test_whowas_get():
    """Get a user adator"""

    get_whowas = whowas.get("adator_test", None)
    assert isinstance(get_whowas, list)

    for whs in get_whowas:
        assert isinstance(whs, Dfn.Whowas)
        assert isinstance(whs.user, Dfn.WhowasUser)
        assert isinstance(whs.geoip, Dfn.Geoip)
  
    # Should be empty list
    get_whowas = whowas.get("for_sure_this_nick_is_not_available")
    assert isinstance(get_whowas, list)
