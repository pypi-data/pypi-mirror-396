from .server import serve


def main():
    """MCP SSP(Social Security Planner) Server"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to a person's age and cbxx"
    )
    parser.add_argument("--ip", type=str, help="ip")

    args = parser.parse_args()
    asyncio.run(serve(args.ip))


if __name__ == "__main__":
    main()
