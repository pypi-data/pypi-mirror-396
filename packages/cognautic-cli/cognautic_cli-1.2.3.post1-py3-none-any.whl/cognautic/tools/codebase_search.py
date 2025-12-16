"""
Codebase Search Tool - Search indexed codebase for symbols, files, and imports
"""

from typing import Dict, Any, List
from ..codebase_indexer import CodebaseIndexer


class CodebaseSearchTool:
    """Tool for searching indexed codebase"""
    
    name = "codebase_search"
    description = """Search the indexed codebase for symbols, files, imports, and more.
    
Use this tool when you need to:
- Find where a function or class is defined
- Locate files by name or path
- Find all usages of an import
- Get codebase statistics
- Understand project structure

The codebase is automatically indexed on startup for fast searching."""
    
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["search", "stats", "list_files", "get_file_info"],
                "description": "Action to perform: search for query, get stats, list files, or get file info"
            },
            "query": {
                "type": "string",
                "description": "Search query (for 'search' action) - can be symbol name, file name, import, etc."
            },
            "file_path": {
                "type": "string",
                "description": "File path (for 'get_file_info' action)"
            },
            "language": {
                "type": "string",
                "description": "Filter by language (optional, for 'list_files' action)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 50)",
                "default": 50
            }
        },
        "required": ["action"]
    }
    
    def __init__(self, project_path: str = None):
        """Initialize tool
        
        Args:
            project_path: Path to project root
        """
        self.project_path = project_path
        self.indexer = None
        if project_path:
            self.indexer = CodebaseIndexer(project_path)
    
    def execute(self, action: str, query: str = None, file_path: str = None, 
                language: str = None, limit: int = 50, **kwargs) -> Dict[str, Any]:
        """Execute codebase search
        
        Args:
            action: Action to perform
            query: Search query
            file_path: File path for get_file_info
            language: Language filter
            limit: Maximum results
        
        Returns:
            Search results or stats
        """
        if not self.indexer:
            return {
                "success": False,
                "error": "No project path set. Use /workspace command to set working directory."
            }
        
        try:
            # Load index
            index = self.indexer.load_index()
            if not index:
                return {
                    "success": False,
                    "error": "Codebase not indexed. Index will be created automatically on next startup."
                }
            
            # Execute action
            if action == "search":
                if not query:
                    return {"success": False, "error": "Query required for search action"}
                
                results = self.indexer.search(query, index)
                return {
                    "success": True,
                    "action": "search",
                    "query": query,
                    "total_results": len(results),
                    "results": results[:limit]
                }
            
            elif action == "stats":
                stats = self.indexer.get_stats(index)
                return {
                    "success": True,
                    "action": "stats",
                    "stats": stats
                }
            
            elif action == "list_files":
                files = []
                for file_index in index.files.values():
                    if language and file_index.language != language:
                        continue
                    files.append({
                        "path": file_index.relative_path,
                        "language": file_index.language,
                        "lines": file_index.lines_of_code,
                        "size": file_index.size
                    })
                
                return {
                    "success": True,
                    "action": "list_files",
                    "language_filter": language,
                    "total_files": len(files),
                    "files": files[:limit]
                }
            
            elif action == "get_file_info":
                if not file_path:
                    return {"success": False, "error": "file_path required for get_file_info action"}
                
                file_index = index.files.get(file_path)
                if not file_index:
                    return {"success": False, "error": f"File not found in index: {file_path}"}
                
                return {
                    "success": True,
                    "action": "get_file_info",
                    "file": {
                        "path": file_index.relative_path,
                        "language": file_index.language,
                        "lines": file_index.lines_of_code,
                        "size": file_index.size,
                        "symbols": file_index.symbols,
                        "imports": file_index.imports,
                        "docstrings": file_index.docstrings
                    }
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing codebase search: {str(e)}"
            }
