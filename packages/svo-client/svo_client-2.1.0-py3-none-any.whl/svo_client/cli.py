"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

CLI for adapter-based ChunkerClient (queue-first).

Commands:
- health
- help
- chunk (one-shot: submit + wait)
- submit (enqueue only)
- status (single status fetch)
- logs (single logs fetch)
- wait (poll until completion)
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

from svo_client.chunker_client import ChunkerClient, SVOServerError


def _read_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    raise SystemExit("❌ Provide --text or --file")


def _client_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "host": args.host,
        "port": args.port,
        "token": args.token,
        "token_header": args.token_header,
        "cert": args.cert,
        "key": args.key,
        "ca": args.ca,
        "check_hostname": args.check_hostname,
        "timeout": args.timeout,
        "poll_interval": args.poll_interval,
    }


async def cmd_health(args: argparse.Namespace) -> None:
    async with ChunkerClient(**_client_kwargs(args)) as client:
        result = await client.health()
        print(json.dumps(result, indent=2))


async def cmd_help(args: argparse.Namespace) -> None:
    async with ChunkerClient(**_client_kwargs(args)) as client:
        result = await client.get_help(args.command)
        print(json.dumps(result, indent=2))


async def cmd_chunk(args: argparse.Namespace) -> None:
    text = _read_text(args)
    async with ChunkerClient(**_client_kwargs(args)) as client:
        try:
            chunks = await client.chunk_text(
                text, language=args.language, type=args.type
            )
            print(f"✅ chunks: {len(chunks)}")
            for idx, ch in enumerate(chunks[: args.max_print]):
                preview = ch.text[:120].replace("\n", " ")
                print(f"- #{idx} ({len(ch.text)} chars) {preview}")
        except SVOServerError as exc:
            print(f"❌ Server error {exc.code}: {exc.message}")
            if exc.chunk_error:
                print(json.dumps(exc.chunk_error, indent=2))


async def cmd_submit(args: argparse.Namespace) -> None:
    text = _read_text(args)
    async with ChunkerClient(**_client_kwargs(args)) as client:
        job_id = await client.submit_chunk_job(
            text,
            language=args.language,
            type=args.type,
            role=args.role,
        )
        print(json.dumps({"job_id": job_id, "status": "queued"}, indent=2))


async def cmd_status(args: argparse.Namespace) -> None:
    async with ChunkerClient(**_client_kwargs(args)) as client:
        status = await client.get_job_status(args.job_id)
        print(json.dumps(status, indent=2))


async def cmd_logs(args: argparse.Namespace) -> None:
    async with ChunkerClient(**_client_kwargs(args)) as client:
        logs = await client.get_job_logs(args.job_id)
        print(json.dumps(logs, indent=2))


async def cmd_wait(args: argparse.Namespace) -> None:
    async with ChunkerClient(**_client_kwargs(args)) as client:
        result = await client.wait_for_result(
            args.job_id,
            poll_interval=args.poll_interval,
            timeout=args.timeout,
        )
        print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adapter-based ChunkerClient CLI"
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8009)
    parser.add_argument("--token-header", default="X-API-Key")
    parser.add_argument("--token")
    parser.add_argument("--cert", help="Path to client certificate")
    parser.add_argument("--key", help="Path to client key")
    parser.add_argument("--ca", help="Path to CA certificate")
    parser.add_argument("--check-hostname", action="store_true")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--role", help="Optional role for chunk command")

    sub = parser.add_subparsers(dest="action", required=True)

    p_health = sub.add_parser("health", help="Health check")
    p_health.set_defaults(func=cmd_health)

    p_help = sub.add_parser("help", help="Get help info")
    p_help.add_argument("--command")
    p_help.set_defaults(func=cmd_help)

    p_chunk = sub.add_parser("chunk", help="Chunk text")
    p_chunk.add_argument("--text", help="Text to chunk")
    p_chunk.add_argument("--file", help="Path to file with text")
    p_chunk.add_argument("--language", default="en")
    p_chunk.add_argument("--type", default="Draft")
    p_chunk.add_argument(
        "--max-print", type=int, default=5, help="Preview first N chunks"
    )
    p_chunk.set_defaults(func=cmd_chunk)

    p_submit = sub.add_parser("submit", help="Enqueue chunk job")
    p_submit.add_argument("--text", help="Text to chunk")
    p_submit.add_argument("--file", help="Path to file with text")
    p_submit.add_argument("--language", default="en")
    p_submit.add_argument("--type", default="Draft")
    p_submit.set_defaults(func=cmd_submit)

    p_status = sub.add_parser("status", help="Get job status")
    p_status.add_argument("job_id", help="Job identifier")
    p_status.set_defaults(func=cmd_status)

    p_logs = sub.add_parser("logs", help="Get job logs")
    p_logs.add_argument("job_id", help="Job identifier")
    p_logs.set_defaults(func=cmd_logs)

    p_wait = sub.add_parser("wait", help="Wait until job completes")
    p_wait.add_argument("job_id", help="Job identifier")
    p_wait.set_defaults(func=cmd_wait)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
