import os

from dotenv import load_dotenv

from hcs_cli.cmds.dev.util import log


def validate(list_of_required_fields):
    load_dotenv()
    missing = [var for var in list_of_required_fields if not os.getenv(var)]
    if missing:
        log.fail(f"Missing required environment variables: {', '.join(missing)}")
    return {var: os.getenv(var) for var in list_of_required_fields}
