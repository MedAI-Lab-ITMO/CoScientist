import argparse
import asyncio
import json
import os
from dotenv import load_dotenv

from rag_tools import create_manager
from rag_tools.config.settings import get_settings
from rag_tools.retrieval import APIEmbedder, APIReranker, BM25Reranker, HybridReranker


# -----------------------
# INIT
# -----------------------
load_dotenv()


async def init_manager():
    settings = get_settings()

    embedder = APIEmbedder(settings.api_embedding)
    api_reranker = APIReranker(settings.api_reranker)
    bm25_reranker = BM25Reranker(settings.bm_reranker)
    reranker = HybridReranker([api_reranker, bm25_reranker], settings.hybrid_reranker)

    manager = await create_manager(settings, embedder, reranker)
    return manager


# -----------------------
# COMMANDS
# -----------------------

async def cmd_add(args):
    manager = await init_manager()

    server = await manager.add_server(
        protocol="http",
        url=args.url,
        name=args.name,
        description=args.description or "",
        headers={"Authorization": f"Bearer {args.token}"} if args.token else None,
        sync_tools=True
    )

    print(f"✅ Added server: {server.name}")
    print(f"   ID: {server.server_id}")

    await manager.close()


async def cmd_remove(args):
    manager = await init_manager()

    await manager.remove_server(args.server_id)

    print(f"🗑 Removed server: {args.server_id}")

    await manager.close()


async def cmd_sync(args):
    manager = await init_manager()

    result = await manager.sync_server(args.server_id)

    print(f"🔄 Synced server: {args.server_id}")
    print(result)

    await manager.close()


async def cmd_sync_all(args):
    manager = await init_manager()

    results = await manager.sync_all_servers()

    print("🔄 Sync results:")
    for r in results:
        print(f" - {r.server_id}: {r.status}")

    await manager.close()


async def cmd_load(args):
    manager = await init_manager()

    with open(args.file, "r") as f:
        servers = json.load(f)

    for s in servers:
        try:
            server = await manager.add_server(
                protocol="http",
                url=s["url"],
                name=s["name"],
                description=s.get("description", ""),
                headers={"Authorization": f"Bearer {s['token']}"} if s.get("token") else None,
                sync_tools=True
            )

            print(f"✅ Added: {server.name}")

        except Exception as e:
            print(f"❌ Failed: {s.get('name')} -> {e}")

    await manager.close()


async def cmd_list(args):
    manager = await init_manager()

    servers = await manager.postgres.list_servers()

    print("📦 Registered servers:\n")
    for s in servers:
        print(f"- {s.name}")
        print(f"  ID: {s.server_id}")
        print(f"  URL: {s.url}")
        print(f"  Description: {s.description}")
        print(f"  Status: {s.status}")
        print()

    await manager.close()


# -----------------------
# CLI
# -----------------------

def main():
    parser = argparse.ArgumentParser(
        description="RAG Tools MCP Server CLI"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add a server")
    p_add.add_argument("--url", required=True)
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--description", default="")
    p_add.add_argument("--token", default=None)
    p_add.set_defaults(func=cmd_add)

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a server")
    p_remove.add_argument("server_id")
    p_remove.set_defaults(func=cmd_remove)

    # sync
    p_sync = subparsers.add_parser("sync", help="Sync a server")
    p_sync.add_argument("server_id")
    p_sync.set_defaults(func=cmd_sync)

    # sync-all
    p_sync_all = subparsers.add_parser("sync-all", help="Sync all servers")
    p_sync_all.set_defaults(func=cmd_sync_all)

    # load
    p_load = subparsers.add_parser("load", help="Load servers from JSON")
    p_load.add_argument("file", help="Path to JSON file")
    p_load.set_defaults(func=cmd_load)

    # list
    p_list = subparsers.add_parser("list", help="List all servers")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()

    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()