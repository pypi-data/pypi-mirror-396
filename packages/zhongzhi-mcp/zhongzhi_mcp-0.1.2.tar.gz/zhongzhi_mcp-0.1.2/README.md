# Zhongzhi MCP Server

An Model Context Protocol (MCP) server for the Zhongzhi (IPPH) API.

## Features

-   **Authentication**: Automatic login and token management with file-based persistence (Serverless friendly).
-   **Search**: Customized trademark/patent search.
-   **Details**: Retrieve detailed information using Registration Number.
-   **Pledge Info**: Query pledge information.
-   **Image Search**: Search by image URL.

## Installation

```bash
pip install zhongzhi-mcp
```

## Usage

### Running the Server

```bash
# Set up environment variables if needed (or rely on config.py defaults)
python -m zhongzhi_mcp.server
```

### Configuration

The server uses `config.py` for credentials. You can also use environment variables (support to be added).

## Tools

-   `shunjian_search_patents`
-   `shunjian_get_patent_detail`
-   `shunjian_get_pledge_info`
-   `shunjian_get_balance`
-   `shunjian_image_search`
-   `shunjian_image_search_aggregation`
-   `shunjian_check_sensitive_word`
