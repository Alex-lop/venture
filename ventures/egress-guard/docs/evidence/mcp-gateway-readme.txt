# source: https://api.github.com/repos/lasso-security/mcp-gateway/readme
# fetched: 2026-08-30


---

ions/mcp-gateway.svg" alt="Python Versions">
 </a>
 <a href="./LICENSE">
 <img src="https://img.shields.io/github/license/lasso-security/mcp-gateway" alt="License">
 </a>
 
 # MCP Gateway

</div>

# Overview
![](docs/MCPFlow.png)

MCP Gateway is an advanced intermediary solution for Model Context Protocol (MCP) servers that centralizes and enhances your AI infrastructure.

MCP Gateway acts as an intermediary between LLMs and other MCP servers. It:

1. 📄 Reads server configurations from a mcp.json file located in your root directory.
2. ⚙️ Manages the lifecycle of configured MCP servers.
3. 🛡️ Intercepts requests and responses to sanitize sensitive information.
4. 🔗 Provides a unified interface for discovering and interacting with all proxied MCPs.
5. 🔒 Security Scanner - Analyzes server reputation and security risks before loading MCP servers.

## Installation

### Python (recommended)
Install the mcp-gateway package:
bash
pip install mcp-gateway


> --mcp-json-path - must lead to your [mcp.json](https://docs.cursor.com/context/model-context-protocol#configuration-locations) or [claudedesktopconfig.json](https://modelcontextprotocol.io/quickstart/server#testing-your-server-with-cla

---

ommand": "npx",
 "args": [
 "-y",
 "@modelcontextprotocol/server-filesystem",
 "."
 ]
 }
 }
 }
 }
}


In this example we use lasso and basic guardrail to show how we can pass enviroment varabile and arguments to the docker and how we can mount storage for the filesystem MCP.
The Docker image can be built with optional dependencies required by certain plugins (e.g., presidio). 
Use the INSTALLEXTRAS build argument during the docker build command. Provide a comma-separated string of the desired extras: "presidio,xetrack"

</details>

## Quickstart

### Masking Sensitive Information

MCP Gateway will automatically mask the sensitive token in the response, preventing exposure of credentials while still providing the needed functionality.

1. Create a file with sensitive information:
 bash
 echo 'HFTOKEN = "hfokpaLGklBeJFhdqdOvkrXljOCTwhADRrXo"' > tokens.txt
 

2. When an agent requests to read this file through MCP Gateway: 
 - Recommend to test with sonnet 3.7
 
 Use your mcp-gateway tools to read the ${pwd}/tokens.txt and return the HFTOKEN
 
 
Output: 

![Hugging Face Token Masking Example](docs/hfexample.png)

## Usage

Start the MCP Gateway server with pythonenv config on this rep
