from .env import HOST, PORT
from .mcp import mcp


def main():
    mcp.run(
        transport="http",
        port=PORT,
        host=HOST,
    )
