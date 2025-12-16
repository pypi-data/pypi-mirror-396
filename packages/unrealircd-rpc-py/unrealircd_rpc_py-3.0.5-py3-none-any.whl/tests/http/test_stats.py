import tests.http.configuration as cfg
import unrealircd_rpc_py.objects.Definition as Dfn

rpc = cfg.start_valid_http_admin_connection()

stats_obj = rpc.Stats

def test_stats_get():
    """Get a user adator"""

    get_stat = stats_obj.get()

    assert isinstance(get_stat, Dfn.Stats)
    assert isinstance(get_stat.server, Dfn.StatsServer)
    assert isinstance(get_stat.server_ban, Dfn.StatsServerBan)
    assert isinstance(get_stat.channel, Dfn.StatsChannel)
    assert isinstance(get_stat.user, Dfn.StatsUser)
    assert isinstance(get_stat.error, Dfn.RPCErrorModel)
    for country in get_stat.user.countries:
        assert isinstance(country, Dfn.StatsUserCountries)
