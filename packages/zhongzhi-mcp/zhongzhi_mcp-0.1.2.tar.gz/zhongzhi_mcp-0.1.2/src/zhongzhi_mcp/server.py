from mcp.server.fastmcp import FastMCP
from .auth import TokenManager
from .client import ZhongzhiClient
import logging
import json

# Initialize FastMCP
mcp = FastMCP("zhongzhi-mcp")

# Global instances
token_manager = TokenManager()
client = ZhongzhiClient(token_manager)

@mcp.resource("config://status")
def get_status() -> str:
    """Returns the status of the connection."""
    if token_manager.token:
        return "Connected"
    return "Disconnected"

@mcp.tool()
def shunjian_search_patents(tm_name: str = None, reg_num: str = None, page: int = 1, page_size: int = 10) -> str:
    """
    Search for trademarks/patents using the Zhongzhi API.
    You must provide at least one search criterion (tm_name or reg_num).
    """
    try:
        result = client.search_patents(tm_name=tm_name, reg_num=reg_num, page=page, page_size=page_size)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_get_patent_detail(tid: str, detail_type: str = "0") -> str:
    """
    Get details of a specific trademark/patent.
    
    Args:
        tid: The trademark ID (usually the Registration Number / regNum).
        detail_type: The type of detail to retrieve (default "0").
    """
    try:
        result = client.get_patent_detail(tid, detail_type)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_get_pledge_info(reg_num: str, int_cls: str, page: int = 1, page_size: int = 10) -> str:
    """
    Get pledge information for a trademark.
    
    Args:
        reg_num: Registration Number.
        int_cls: International Classification.
    """
    try:
        result = client.get_pledge_info(reg_num, int_cls, page, page_size)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_get_balance() -> str:
    """
    Get the interface balance.
    """
    try:
        result = client.get_balance()
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_image_search(image_url: str) -> str:
    """
    Search for trademarks by image URL.
    """
    try:
        result = client.image_search(image_url)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_image_search_aggregation(image_url: str) -> str:
    """
    Search for trademarks by image URL (Aggregation).
    """
    try:
        result = client.image_search_aggregation(image_url)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_check_sensitive_word(word: str) -> str:
    """
    Check if a word is sensitive.
    """
    try:
        result = client.check_sensitive_word(word)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize authentication on startup
try:
    token_manager.start_scheduler()
except Exception as e:
    logging.error(f"Failed to start token manager: {e}")

def main():
    mcp.run()

if __name__ == "__main__":
    main()
