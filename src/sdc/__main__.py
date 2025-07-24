import argparse
from pathlib import Path

from .database import open_db, Session, scan_to_db
from songripper.worker import approve_with_checks
from duplicate_finder import find_duplicates


def _cmd_scan(args: argparse.Namespace) -> None:
    engine = open_db()
    scan_to_db(Path(args.root), engine)


def _cmd_duplicates(args: argparse.Namespace) -> None:
    engine = open_db()
    with Session(engine) as session:
        groups = find_duplicates(session)
    for g in groups:
        print(f"# confidence: {g.score}")
        for p in g.files:
            print(p)
        print()


def _cmd_approve(args: argparse.Namespace) -> None:
    approve_with_checks()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="sdc")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_p = sub.add_parser("scan", help="Scan directory for audio files")
    scan_p.add_argument("root", help="Root directory to scan")
    scan_p.set_defaults(func=_cmd_scan)

    dup_p = sub.add_parser("duplicates", help="List duplicate tracks")
    dup_p.set_defaults(func=_cmd_duplicates)

    appr_p = sub.add_parser("approve", help="Approve staged tracks")
    appr_p.set_defaults(func=_cmd_approve)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
