# Use the SAME server from Claude Desktop

You already have a working MCP server: `server/mcp_server.py`. Your LangChain
agent spawns it as a subprocess. Claude Desktop can spawn the exact same file:
no code changes, just a config entry.

## 1. Find the config file

| OS      | Path                                                              |
|---------|-------------------------------------------------------------------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json`                     |
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux   | `~/.config/Claude/claude_desktop_config.json`                     |

The quickest way to open it is in Claude Desktop: **Settings → Developer → Edit Config**.
If the file doesn't exist yet, create it.

## 2. Add the server

```json
{
  "mcpServers": {
    "handbook": {
      "command": "python",
      "args": ["/absolute/path/to/project-mcp-langchain/server/mcp_server.py"],
      "env": {
        "INDEX_DIR": "/absolute/path/to/project-mcp-langchain/chroma_db"
      }
    }
  }
}
```

If the file already has an `"mcpServers"` block, add `"handbook": {...}` inside
it. Don't create a second `"mcpServers"` key.

**Use your venv's Python, not bare `python`.** Claude Desktop doesn't activate
your virtualenv, so `"python"` usually resolves to a system Python that doesn't
have `mcp` or `langchain-chroma` installed. Find the right path with the venv
active:

```bash
# macOS / Linux
which python
# Windows (PowerShell)
(Get-Command python).Source
```

A filled-in Windows example (note the doubled backslashes; forward slashes work too):

```json
{
  "mcpServers": {
    "handbook": {
      "command": "C:\\Users\\you\\itm-lecture-llm\\project-mcp-langchain\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\you\\itm-lecture-llm\\project-mcp-langchain\\server\\mcp_server.py"],
      "env": {
        "INDEX_DIR": "C:\\Users\\you\\itm-lecture-llm\\project-mcp-langchain\\chroma_db"
      }
    }
  }
}
```

The server doesn't need `GROQ_API_KEY`: the LLM is Claude this time. The server
only runs the retrieval.

## 3. Restart Claude Desktop, fully

Closing the window isn't enough, because Claude Desktop keeps running in the
background and only reads the config at startup.

- **Windows:** right-click the Claude icon in the system tray → **Quit**, then reopen.
- **macOS:** `Cmd+Q` (or Claude menu → Quit), then reopen.

## 4. Verify it connected

- In the chat box, click the tools / connectors icon at the bottom-left. `handbook`
  should be listed with its 3 tools: `search_handbook`, `search_by_page`,
  `list_sections`.
- **Settings → Developer** shows each server with a status (running / failed).
- Ask: *"Using the handbook, what's the attendance rule?"* Claude asks for permission
  to call `search_handbook`, and you'll see the tool call and its result in the chat.
- The `handbook://metadata` resource shows up in the attach (+) menu, where you can
  add it to the conversation as context. That's the difference between a resource
  and a tool: the host or user chooses resources, the model chooses tools.

## 5. Troubleshooting

**Where are the logs?**

| OS      | Folder                         |
|---------|--------------------------------|
| Windows | `%APPDATA%\Claude\logs\`       |
| macOS   | `~/Library/Logs/Claude/`       |

Look at `mcp-server-handbook.log` (your server's stderr) and `mcp.log`
(connection events). Every `log(...)` call in `mcp_server.py` lands in the first
one, including the `[handbook-rag] Loaded N chunks ...` startup line.

**stderr vs stdout, the #1 bug.** Over stdio, stdout *is* the protocol channel.
Claude Desktop reads stdout expecting only JSON-RPC messages. A single
`print("debug")` in your server, or a library banner, lands in that stream and
the client fails to parse it. Symptoms: "Server disconnected", tools never
appear, or calls hang. Fix: log with `print(..., file=sys.stderr)` (our `log()`
helper does this). stderr goes to the log file above.

**Common errors**

| Symptom in the log | Cause → fix |
|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | `command` is a Python without your packages → use the venv's python.exe path |
| `No index found at ...` | `INDEX_DIR` is wrong or you haven't run `01_build_index.py` → fix the path, rebuild |
| `can't open file '~/...'` | `~` and `$HOME` aren't expanded in this config → write the full absolute path |
| Server listed but "failed" right after restart | Run the exact `command` + `args` in a terminal yourself: the traceback prints right there |
| First tool call is slow | The embedding model loads on server startup (a few seconds); later calls are fast |

**Test outside Claude Desktop first.** The MCP Inspector is a browser UI that
connects to your server like a host would:

```bash
npx @modelcontextprotocol/inspector python server/mcp_server.py
```

If the tools work there, any remaining problem is in the Claude Desktop config,
not your code.
