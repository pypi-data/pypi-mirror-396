from apppy.env import DictEnv
from apppy.sb.auth import SupabaseAuthSettings

_env = DictEnv(
    prefix="SUPABASE_AUTH",
    name="test_client_options_with_storage",
    d={
        "api_anon_key": "api_anon_key",
        "api_key": "api_key",
        "api_url": "api_url",
    },
)


async def test_client_options_with_storage():
    settings = SupabaseAuthSettings(env=_env)
    client_options = settings.client_options_with_storage(
        session={"my_session_key": "my_session_value"}
    )

    # Assert that we can read the session back using the
    # default supabase storage key
    session = await client_options.storage.get_item("supabase.auth.token")
    assert session is not None
    assert session["my_session_key"] == "my_session_value"


async def test_client_options_without_storage():
    settings = SupabaseAuthSettings(env=_env)
    client_options = settings.client_options_without_storage()

    # Assert that we cannot read the session back using the
    # default supabase storage key
    session = await client_options.storage.get_item("supabase.auth.token")
    assert session is None
