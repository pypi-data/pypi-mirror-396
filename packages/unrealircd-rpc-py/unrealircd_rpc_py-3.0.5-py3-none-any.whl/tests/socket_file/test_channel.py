import unrealircd_rpc_py.objects.Definition as Dfn
import tests.socket_file.configuration as cnf

rpc = cnf.start_valid_socket_admin_connection()

channel_name = "#welcome"
nickname = "adator_test"

def test_channel_list():
    """list all channels"""

    obj = rpc.Channel

    channels = obj.list_(4)
    assert isinstance(channels, list)

    for channel in channels:
        assert isinstance(channel, Dfn.Channel)
        assert isinstance(channel.error, Dfn.RPCErrorModel)

        for ban in channel.bans:
            assert isinstance(ban, Dfn.ChannelBans)
        for ban_exemption in channel.ban_exemptions:
            assert isinstance(ban_exemption, Dfn.ChannelBanExemptions)
        for member in channel.members:
            assert isinstance(member, Dfn.ChannelMembers)
        for invite_exception in channel.invite_exceptions:
            assert isinstance(invite_exception, Dfn.ChannelInviteExceptions)

def test_get_channel():
    """Get specific channel"""

    obj = rpc.Channel

    channel = obj.get(channel=channel_name, object_detail_level=5)

    assert isinstance(channel, Dfn.Channel)

    for member in channel.members:
        assert isinstance(member, Dfn.ChannelMembers)
        assert isinstance(member.user, Dfn.User)
        assert isinstance(member.tls, Dfn.Tls)
        assert isinstance(member.geoip, Dfn.Geoip)

    channel = obj.get(channel="wrongchannel", object_detail_level=5)

    assert isinstance(channel, Dfn.Channel)
    assert channel.error.message == "Channel not found"

def test_set_mode():
    """Set mode to a channel"""

    obj = rpc.Channel
    channel = obj.set_mode("#jsonrpc", "+be", "adator_test!rpc_test@jsonrpc.deb.biz.st")

    assert isinstance(channel, Dfn.RPCResult)
    assert channel.error.code == 0

    channel = obj.set_mode("#jsonrpc", "-be", "adator_test!rpc_test@jsonrpc.deb.biz.st")
    assert isinstance(channel, Dfn.RPCResult)
    assert channel.error.code == 0

    channel = obj.set_mode("#jsonrpc", "-ntl")
    assert isinstance(channel, Dfn.RPCResult)
    assert channel.error.code == 0

    channel = obj.set_mode("#jsonrpc", "+nt")
    assert isinstance(channel, Dfn.RPCResult)
    assert channel.error.code == 0

def test_set_topic():
    """Set topic to a channel"""

    obj = rpc.Channel

    channel =  obj.set_topic("#jsonrpc", "This topic has been written from jsonrpc", nickname, set_at="2025-10-10 23:52:00")
    assert isinstance(channel, Dfn.RPCResult)
    assert channel.error.code == 0
    assert channel.result == True

    # Test wrong channel
    channel = obj.set_topic("json-rpc", "This topic has been written from jsonrpc")
    assert channel.error.code == -1000 and channel.error.message == 'Channel not found'

def test_kick():
    """Kick nick on a channel"""

    obj_user = rpc.User
    obj = rpc.Channel

    channel = obj.kick("#jsonrpc", "adator_test", "Kicked from JSONRPC User")
    assert isinstance(channel, Dfn.RPCResult)
    assert channel.result == True

    # Test wrong channel
    channel = obj.kick("jsonrpc", "wrong_channel", "Kicked from JSONRPC User")
    assert channel.error.code == -1000 and channel.error.message == 'Channel not found'

    user = obj_user.join("adator_test", "#jsonrpc", '', True)
    assert isinstance(user, Dfn.RPCResult)
    assert user.result == True