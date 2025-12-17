import argparse
from fastfame import FastFameClient


def main():
    parser = argparse.ArgumentParser(description="FastFame TikTok Views Client")
    parser.add_argument("--username", required=True, help="FastFame username")
    parser.add_argument("--url", required=True, help="TikTok video URL")

    args = parser.parse_args()

    client = FastFameClient(username=args.username)
    result = client.send_views(args.url)

    print(result)


if __name__ == "__main__":
    main()
