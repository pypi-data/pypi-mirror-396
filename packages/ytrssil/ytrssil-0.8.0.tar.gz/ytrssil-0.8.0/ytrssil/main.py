from sys import argv, exit, stderr

from ytrssil.cli import CLI
from ytrssil.client import Client
from ytrssil.config import load_config


def main() -> int:
    config = load_config()
    client = Client(config)
    cli = CLI(config, client)
    command: str
    try:
        command = argv[1]
    except IndexError:
        command = "watch"

    if command == "fetch":
        return cli.fetch()
    elif command == "subscribe":
        if len(argv) < 3:
            print(
                "Missing channel ID argument for subscribe command",
                file=stderr,
            )
            return 1

        return cli.subscribe_to_channel(channel_id=argv[2])
    elif command == "watch":
        return cli.watch_videos()
    elif command == "print":
        return cli.print_url()
    elif command == "history":
        return cli.watch_history()
    elif command == "mark":
        return cli.mark_as_watched()
    elif command == "unmark":
        return cli.mark_as_unwatched()
    else:
        print(f'Unknown command "{command}"', file=stderr)
        print(
            "Available commands: fetch, watch, print, history, mark, unmark",
            file=stderr,
        )
        return 1


if __name__ == "__main__":
    exit(main())
