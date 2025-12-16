import argparse
from pipreqsafe.core import get_packages


def main():
    parser = argparse.ArgumentParser(
        description="Generate deployment-safe requirements.txt from pip list"
    )

    parser.add_argument(
        "--no-version",
        action="store_true",
        help="Write package names without versions",
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print requirements and do not write requirements.txt",
    )

    parser.add_argument(
        "--output",
        default="requirements.txt",
        help="Output file name (default: requirements.txt)",
    )

    args = parser.parse_args()

    pkgs = get_packages()

    # Terminal output
    if args.no_version:
        for name, _ in pkgs:
            print(name)
    else:
        print(f"{'Package':<15} Version")
        print(f"{'-'*15} {'-'*8}")
        for name, version in pkgs:
            print(f"{name:<15} {version}")

    # Only write to file if stdout is not set
    if not args.stdout:
        with open(args.output, "w") as f:
            for name, version in pkgs:
                if args.no_version:
                    f.write(f"{name}\n")
                else:
                    f.write(f"{name}=={version}\n")

        print(f"\n✔ Written {args.output}")


if __name__ == "__main__":
    main()
