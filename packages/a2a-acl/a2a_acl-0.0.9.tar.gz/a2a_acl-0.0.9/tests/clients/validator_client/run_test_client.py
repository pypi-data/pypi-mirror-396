import context

from a2a.types import (
    AgentCard,
)

from a2a_acl.protocol.send_acl_message import spawn_send_acl_message
from a2a_acl.a2a_utils.card_holder import download_card


from a2a_acl.utils.url import build_url

host = "127.0.0.1"


async def main() -> None:
    target_agent_url = build_url(host, context.port_validator)

    # Fetch Public Agent Card and Initialize Client
    target_agent_card: AgentCard | None = None

    try:
        target_agent_card = await download_card(target_agent_url)

    except Exception:
        print("Client failed to fetch the public agent card. Cannot continue.")
        exit(-1)

    spawn_send_acl_message(
        target_agent_card, "propose", "The function should return an integer.", "", "nl"
    )
    print("Message sent to validator agent.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
    input("Press Enter to exit.\n")
