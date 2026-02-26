from fastmcp import FastMCP
from ChemCoScientist.download_papers.functions import download_papers as _download_papers

mcp = FastMCP("PapersSearch")

@mcp.tool()
def download_papers(task: str, session_id: str = "default", user_id: str = "default") -> dict:
    """
    Search for scientific papers in OpenAlex and download their PDFs.
    
    Args:
        task: Search query for papers (e.g., "find papers about CRISPR")
        session_id: Session identifier for organizing downloaded files
        user_id: User identifier for organizing downloaded files
    
    Returns:
        Dictionary with 'answer' and 'metadata' containing download results
    """
    result = _download_papers(
        task=task,
        session_id=session_id,
        user_id=user_id,
    )

    if isinstance(result, dict):
        return result

    return result


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=7331, path="/mcp")
