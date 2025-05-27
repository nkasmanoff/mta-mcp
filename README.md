# MTA MCP Server

This is a simple MCP server that provides information about the next train arrival at a given station and direction.

## Next steps:

-   Integrate location?
-   More testing with different lines and spelling issues

## How to run

To get started I followed the instructions in the [MCP documentation](https://github.com/modelcontextprotocol/python-sdk).

```bash
uv run subway.py
```

Next add this to your .cursor/mcp.json file:

```json
{
    "mcpServers": {
        "mta_subway_tracker": {
            "command": "uv",
            "args": ["--directory", "<path to your project>", "run", "subway.py"]
        }
    }
}
```

Example questions:

```
When is the next express south train arriving at 14th street?
```

Answer:

```
Okay, I can help you with that. I'll check for the next southbound train at 14th St-Union Sq using the feed for lines 1, 2, 3, 4, 5, and 6.


Ran tool
The next express southbound trains arriving at 14th St-Union Sq are:
- 4 train at 15:52:41
- 5 train at 15:56:24

There are also local 6 trains arriving, the next one is at 15:46:27.
```

Created by [Jonathan Allen](https://github.com/jonathanallen44) and [Noah Kasmanoff](https://github.com/nkamanoff)
