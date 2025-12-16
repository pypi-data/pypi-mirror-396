import context
from a2a_acl.agent.server_utils import run_server
from sample_agents.human_validation.validator import (
    ValidatorAgentExecutor,
    my_card,
)
from a2a_acl.utils.url import build_url


the_host = "127.0.0.1"
my_url = build_url(the_host, context.validator_port)


async def main() -> None:
    run_server(
        ValidatorAgentExecutor(my_card, build_url(the_host, context.validator_port)),
        the_host,
        context.validator_port,
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
