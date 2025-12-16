import sys, os
from . import extractors as ex
from argparse import ArgumentParser
from innertube.clients import InnerTube


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='')
    _ = parser.add_argument('query', type=str, help='query to make')
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    innertube_client = InnerTube('WEB_REMIX')
    response = innertube_client.search(args.query)
    try:
        channel_id = ex.get_channel_id(response)
    except (KeyError, IndexError):
        print(f'no results\n')
        sys.exit(1)

    response = innertube_client.browse(f"MPAD{channel_id}")
    playlists = ex.get_playlists(response)

    try:
        for p in playlists:
            print(f"{p.title} {p.album_type} {p.release_year} {p.playlist_id}")
    except BrokenPipeError:
        # Python flushes standard streams on exit;
        # redirect remaining output to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        _ = os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE


if __name__ == '__main__':
  main()

