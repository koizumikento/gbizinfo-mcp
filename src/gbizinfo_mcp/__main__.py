from __future__ import annotations

import argparse
import asyncio
import json
import sys

from pydantic import ConfigDict, ValidationError, validate_call

from .server import create_server, create_toolset
from .tool_specs import TOOL_SPECS


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args == ["serve"]:
        create_server().run(transport="stdio")
        return 0

    parser = argparse.ArgumentParser(description="Query gBizINFO, or use serve to start MCP.")
    parser.add_argument("operation", choices=[spec.name for spec in TOOL_SPECS])
    parser.add_argument("--args", default="{}", help="Tool arguments as a JSON object")
    options = parser.parse_args(args)
    try:
        params = json.loads(options.args)
        if not isinstance(params, dict):
            raise ValueError("--args must be a JSON object")
    except ValueError as exc:
        parser.error(str(exc))

    try:
        operation = getattr(create_toolset(), options.operation)
        call = validate_call(config=ConfigDict(strict=True))(operation)
        result = asyncio.run(call(**params))
    except ValidationError as exc:
        print(exc.json(include_input=False, include_url=False), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
