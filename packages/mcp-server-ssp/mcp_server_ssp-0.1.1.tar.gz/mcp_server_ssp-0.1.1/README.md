# SSP(Social Security Planner) MCP Server

### Available Tools

- `queryPerAgeAndCbxx` - 获取一个人的年龄和社保参保信息。
  - Required arguments:
    - `sfzhm` (string): 身份证号 (e.g., '37010119760201001X')
    - `rsxtid` (string): 参保地区编号 (e.g., '3751')

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-ssp*.