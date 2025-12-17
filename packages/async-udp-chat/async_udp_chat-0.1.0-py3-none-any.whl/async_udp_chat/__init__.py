# Andrea Diamantini
# UDP async CHAT

import argparse
import asyncio
import sys
from importlib.metadata import version

# local import
from async_udp_chat import udp_client, udp_server

# server
server_port = 22222

# ---------------------------------------------------------------------------------------------------------


def main():
    """
    async udp chat, server and client app.
    Implemented for educational purposes.
    """

    parser = argparse.ArgumentParser(
        prog="async_udp_chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"{main.__doc__}",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="show package version and exit",
        action="version",
        version=version("async_udp_chat"),
    )

    parser.add_argument("--server", help="run in server mode", action="store_true")
    parser.add_argument("--client", help="run in client mode", action="store_true")
    parser.add_argument("--gui", help="run in GUI client mode", action="store_true")

    args = parser.parse_args()

    try:
        if args.server:
            print("[INFO] server mode")
            asyncio.run(udp_server.runServer(server_port))
            sys.exit(0)

        if args.client:
            print("[INFO] client mode")
            asyncio.run(udp_client.runClient(server_port))
            sys.exit(0)

        if args.gui:
            print("[INFO] GUI client mode")
            # included here cause of the OPTIONAL wx deps
            from async_udp_chat import udp_gui_client

            asyncio.run(udp_gui_client.runGuiClient(server_port))
            sys.exit(0)

        # if no arguments, print help
        parser.print_help()

    except KeyboardInterrupt:
        print("[INFO] Closing NOW!!!")


# ---------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
