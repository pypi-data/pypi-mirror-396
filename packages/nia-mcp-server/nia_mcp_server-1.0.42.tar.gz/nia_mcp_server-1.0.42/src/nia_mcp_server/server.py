"""
Nia MCP Proxy Server - Lightweight server that communicates with Nia API
"""
import os
import logging
import json
import asyncio
import webbrowser
import textwrap
from typing import List, Optional, Dict, Any, Union, Tuple, Literal, Annotated
from pydantic import Field
from datetime import datetime
from urllib.parse import urlparse

from fastmcp import FastMCP
from fastmcp.server.auth import TokenVerifier, AccessToken
from fastmcp.server.dependencies import get_access_token
from mcp.types import TextContent, Resource
from .api_client import NIAApiClient, APIError
from .project_init import initialize_nia_project
from .profiles import get_supported_profiles
from dotenv import load_dotenv
import httpx
import json
import argparse
from contextvars import ContextVar
from starlette.requests import Request
from starlette.responses import JSONResponse

# Context variable to store current user's API key (for HTTP transport)
_current_api_key: ContextVar[Optional[str]] = ContextVar('api_key', default=None)

# Load .env from parent directory (nia-app/.env)
from pathlib import Path
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# =============================================================================
# AUTHENTICATION SETUP
# =============================================================================
# 
# For HTTP transport, users authenticate via Bearer token in Authorization header:
#   Authorization: Bearer <NIA_API_KEY>
#
# The API key is validated against the NIA backend and stored in context.
# For STDIO transport, the NIA_API_KEY environment variable is used.
#
# =============================================================================

class NIATokenVerifier(TokenVerifier):
    """
    Production-grade token verifier for NIA API keys.
    
    Validates API keys against the NIA backend with fail-closed security:
    - Only accepts tokens with valid nk_ prefix
    - Validates tokens against NIA backend API
    - Denies access on any validation failure (timeout, error, etc.)
    - Caches valid tokens for 2 minutes to reduce backend calls
    
    Users authenticate via Bearer token:
        Authorization: Bearer nk_xxxxx
    """
    
    # Class-level cache shared across instances
    _cache_lock = asyncio.Lock()
    _auth_cache: Dict[str, float] = {}  # token_hash -> expiry_timestamp
    _AUTH_CACHE_TTL = 120  # Cache valid keys for 2 minutes
    _AUTH_CACHE_MAX_SIZE = 1000  # Prevent unbounded growth
    
    def __init__(self):
        super().__init__(required_scopes=["api:access"])
        self.api_url = os.getenv("NIA_API_URL", "https://apigcp.trynia.ai").rstrip('/')
        self._http_client: Optional[httpx.AsyncClient] = None
    
    @staticmethod
    def _get_token_hash(token: str) -> str:
        """Hash token for cache key (don't store full token in memory)."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()[:16]
    
    @classmethod
    async def _is_token_cached(cls, token: str) -> bool:
        """Check if token is in cache and not expired."""
        import time
        token_hash = cls._get_token_hash(token)
        async with cls._cache_lock:
            if token_hash in cls._auth_cache:
                if time.time() < cls._auth_cache[token_hash]:
                    return True
                else:
                    del cls._auth_cache[token_hash]
        return False
    
    @classmethod
    async def _cache_valid_token(cls, token: str):
        """Cache a validated token."""
        import time
        async with cls._cache_lock:
            # Cleanup old entries if cache is too large
            if len(cls._auth_cache) >= cls._AUTH_CACHE_MAX_SIZE:
                now = time.time()
                expired = [k for k, v in cls._auth_cache.items() if v < now]
                for k in expired:
                    del cls._auth_cache[k]
                # If still too large, clear oldest half
                if len(cls._auth_cache) >= cls._AUTH_CACHE_MAX_SIZE:
                    sorted_keys = sorted(cls._auth_cache.keys(), key=lambda k: cls._auth_cache[k])
                    for k in sorted_keys[:len(sorted_keys)//2]:
                        del cls._auth_cache[k]
            
            token_hash = cls._get_token_hash(token)
            cls._auth_cache[token_hash] = time.time() + cls._AUTH_CACHE_TTL
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for validation requests."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=10.0)
        return self._http_client
    
    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify NIA API key against the backend.
        
        Args:
            token: The bearer token (NIA API key) to validate
            
        Returns:
            AccessToken with client_id and scopes if valid, None if invalid
        """
        # Basic format check
        if not token:
            logger.warning("Auth failed: empty token")
            return None
        
        if not token.startswith("nk_"):
            logger.warning("Auth failed: invalid token format (must start with nk_)")
            return None
        
        # Check cache first
        if await self._is_token_cached(token):
            _current_api_key.set(token)
            logger.debug("Auth: using cached validation")
            client_id = f"nia-user-{token[-8:]}"
            return AccessToken(
                client_id=client_id,
                scopes=["api:access"],
                token=token
            )
        
        # Validate against NIA backend
        try:
            client = await self._get_client()
            response = await client.get(
                f"{self.api_url}/v2/repositories",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": 1}  # Minimal request just to validate
            )
            
            if response.status_code == 401:
                logger.warning("Auth failed: invalid API key")
                return None
            
            if response.status_code != 200:
                logger.error(f"Auth validation request failed: {response.status_code}")
                # Fail closed on server errors for security
                logger.error("Auth validation failed: backend unavailable")
                return None
            
            # Cache the valid token
            await self._cache_valid_token(token)
            
            # Valid API key - store in context for tool use
            _current_api_key.set(token)
            logger.info("Auth success: API key validated and cached")
            
            # Return access token with the API key identifier
            # Using last 8 chars to avoid exposing the full key in logs
            client_id = f"nia-user-{token[-8:]}"
            return AccessToken(
                client_id=client_id,
                scopes=["api:access"],
                token=token
            )
            
        except httpx.TimeoutException:
            logger.error("Auth validation timeout - denying request")
            return None
        except Exception as e:
            logger.error(f"Auth validation error: {e} - denying request")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

# Create auth verifier for HTTP mode
auth_verifier = NIATokenVerifier()

# Create the MCP server with instructions for AI assistants
mcp = FastMCP(
    name="nia-knowledge-agent",
    instructions="""
    Nia Knowledge Agent provides tools for indexing and searching repositories and documentation.
    
    WORKFLOW: list available sources -> search using different methods (ls, grep, search, etc.)
    """,
    auth=auth_verifier  # Enable auth for HTTP transport
)

# =============================================================================
# HTTP SERVER SUPPORT
# =============================================================================
# 
# This server supports two transport modes:
#   1. STDIO (default) - For local clients like Claude Desktop, Cursor
#   2. HTTP - For remote/network access with multi-client support
#
# Usage:
#   STDIO:  python -m nia_mcp_server (or just run normally)
#   HTTP:   python -m nia_mcp_server --http [--port 8000] [--host 0.0.0.0]
#
# Production (ASGI):
#   uvicorn nia_mcp_server.server:http_app --host 0.0.0.0 --port 8000 --workers 4
#
# =============================================================================

# Default HTTP server settings
DEFAULT_HTTP_HOST = "0.0.0.0"
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_PATH = "/mcp"

# Custom HTTP routes for health checks and status
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for load balancers and monitoring."""
    return JSONResponse({
        "status": "healthy",
        "server": "nia-knowledge-agent",
        "transport": "http"
    })

@mcp.custom_route("/status", methods=["GET"])
async def server_status(request: Request) -> JSONResponse:
    """Server status endpoint with configuration info."""
    return JSONResponse({
        "server": "nia-knowledge-agent",
        "api_key_configured": bool(os.getenv("NIA_API_KEY")),
        "api_client_initialized": api_client is not None,
        "version": "1.0.0"
    })

def create_http_app(path: str = DEFAULT_HTTP_PATH):
    """
    Create ASGI application for production HTTP deployment.
    
    Usage:
        uvicorn nia_mcp_server.server:http_app --host 0.0.0.0 --port 8000
    
    Args:
        path: URL path for the MCP endpoint (default: /mcp)
    
    Returns:
        Starlette ASGI application
    """
    return mcp.http_app(path=path)

# NOTE: http_app is created AFTER all tool definitions (see end of file)
# This ensures all @mcp.tool() decorators have run before the ASGI app is created

# Global API client instance
api_client: Optional[NIAApiClient] = None

def get_api_key() -> str:
    """Get API key from environment."""
    api_key = os.getenv("NIA_API_KEY")
    if not api_key:
        raise ValueError(
            "NIA_API_KEY environment variable not set. "
            "Get your API key at https://trynia.ai/api-keys"
        )
    return api_key

async def ensure_api_client() -> NIAApiClient:
    """
    Ensure API client is initialized with appropriate API key.
    
    For HTTP transport: Uses API key from Bearer token (stored in context).
    For STDIO transport: Uses NIA_API_KEY environment variable.
    
    This enables multi-user support where each HTTP client uses their own API key.
    """
    global api_client
    
    # Check for user-provided API key from Bearer token (HTTP mode)
    user_api_key = _current_api_key.get()
    
    if user_api_key:
        # User provided their own API key via Bearer token
        # Create a fresh client for this request (don't use global cache)
        user_client = NIAApiClient(user_api_key)
        if not await user_client.validate_api_key():
            raise ValueError(
                "Invalid API key. Get your API key at https://trynia.ai/api-keys"
            )
        return user_client
    
    # No user API key - use the server's default (STDIO mode or fallback)
    if not api_client:
        api_key = get_api_key()  # From environment variable
        api_client = NIAApiClient(api_key)
        # Validate the API key
        if not await api_client.validate_api_key():
            raise ValueError("Failed to validate API key. Check logs for details.")
    return api_client

def _detect_resource_type(url: str) -> str:
    """Detect if URL is a GitHub repository or documentation.

    Args:
        url: The URL to analyze

    Returns:
        "repository" if GitHub URL or repository pattern, "documentation" otherwise
    """
    import re
    from urllib.parse import urlparse

    try:
        # First, check for repository-like patterns
        # Pattern 1: owner/repo format (simple case with single slash)
        if re.match(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$', url):
            return "repository"

        # Pattern 2: Git SSH format (git@github.com:owner/repo.git)
        if url.startswith('git@'):
            return "repository"

        # Pattern 3: Git protocol (git://...)
        if url.startswith('git://'):
            return "repository"

        # Pattern 4: Ends with .git
        if url.endswith('.git'):
            return "repository"

        # Pattern 5: owner/repo/tree/branch or owner/repo/tree/branch/... format
        if re.match(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+/tree/.+', url):
            return "repository"

        # Parse as URL for domain-based detection
        parsed = urlparse(url)
        # Only treat as repository if it's actually the github.com domain
        netloc = parsed.netloc.lower()
        if netloc == "github.com" or netloc == "www.github.com":
            return "repository"

        return "documentation"
    except Exception:
        # Fallback to documentation if parsing fails
        return "documentation"

# Tools

@mcp.tool()
async def index(
    url: Annotated[str, Field(description="GitHub repository URL or documentation site URL")],
    resource_type: Annotated[
        Literal["repository", "documentation"] | None,
        Field(description="Override auto-detection: 'repository' or 'documentation'")
    ] = None,
    branch: Annotated[Optional[str], Field(description="Branch to index (repo-specific, defaults to main)")] = None,
    url_patterns: Annotated[Optional[List[str]], Field(description="URL patterns to include in crawling (docs-specific)")] = None,
    exclude_patterns: Annotated[Optional[List[str]], Field(description="URL patterns to exclude from crawling (docs-specific)")] = None,
    max_age: Annotated[Optional[int], Field(description="Maximum age in seconds for cached content")] = None,
    only_main_content: Annotated[bool, Field(description="Extract only main content, excluding nav/footer")] = True,
    wait_for: Annotated[Optional[int], Field(description="Wait time in ms for dynamic content to load")] = None,
    include_screenshot: Annotated[Optional[bool], Field(description="Include screenshots of pages")] = None,
    check_llms_txt: Annotated[bool, Field(description="Check for llms.txt file on the domain")] = True,
    llms_txt_strategy: Annotated[
        Literal["prefer", "only", "ignore"],
        Field(description="How to handle llms.txt: 'prefer', 'only', or 'ignore'")
    ] = "prefer"
) -> List[TextContent]:
    """
    Universal indexing tool - intelligently indexes GitHub repositories or documentation.

    Auto-detects resource type from URL:
    - GitHub URLs (containing "github.com") → Repository indexing
    - All other URLs → Documentation indexing

    Args:
        url: GitHub repository URL or documentation site URL (required)
        resource_type: Optional override - "repository" or "documentation" (auto-detected if not provided)

        # Repo-specific params:
        branch: Branch to index (optional, defaults to main branch)

        # Documentation-specific params:
        url_patterns: Optional list of URL patterns to include in crawling
        exclude_patterns: Optional list of URL patterns to exclude from crawling
    Returns:
        Status of the indexing operation
    Important:
        - When indexing starts, use check_resource_status to monitor progress
        - Repository identifier format: owner/repo or owner/repo/tree/branch
    """
    try:
        client = await ensure_api_client()

        # Detect or validate resource type
        if resource_type:
            if resource_type not in ["repository", "documentation"]:
                return [TextContent(
                    type="text",
                    text=f"❌ Invalid resource_type: '{resource_type}'. Must be 'repository' or 'documentation'."
                )]
            detected_type = resource_type
        else:
            detected_type = _detect_resource_type(url)

        logger.info(f"Indexing {detected_type}: {url}")

        # Route to appropriate indexing method
        if detected_type == "repository":
            # Index repository
            result = await client.index_repository(url, branch)

            repository = result.get("repository", url)
            status = result.get("status", "unknown")

            if status == "completed":
                return [TextContent(
                    type="text",
                    text=f"✅ Repository already indexed: {repository}\n"
                         f"Branch: {result.get('branch', 'main')}\n"
                         f"You can now search this codebase!"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"⏳ Indexing started for: {repository}\n"
                         f"Branch: {branch or 'default'}\n"
                         f"Status: {status}\n\n"
                         f"Use `check_resource_status(\"repository\", \"{repository}\")` to monitor progress."
                )]

        else:  # documentation
            # Index documentation
            result = await client.create_data_source(
                url=url,
                url_patterns=url_patterns,
                exclude_patterns=exclude_patterns,
                max_age=max_age,
                only_main_content=only_main_content,
                wait_for=wait_for,
                include_screenshot=include_screenshot,
                check_llms_txt=check_llms_txt,
                llms_txt_strategy=llms_txt_strategy
            )

            source_id = result.get("id")
            status = result.get("status", "unknown")

            if status == "completed":
                return [TextContent(
                    type="text",
                    text=f"✅ Documentation already indexed: {url}\n"
                         f"Source ID: {source_id}\n"
                         f"You can now search this documentation!"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"⏳ Documentation indexing started: {url}\n"
                         f"Source ID: {source_id}\n"
                         f"Status: {status}\n\n"
                         f"Use `check_resource_status(\"documentation\", \"{source_id}\")` to monitor progress."
                )]

    except APIError as e:
        logger.error(f"API Error indexing {detected_type}: {e} (status_code={e.status_code}, detail={e.detail})")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text",
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for higher limits."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error indexing: {e}")
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error indexing: {error_msg}"
        )]

@mcp.tool()
async def search(
    query: Annotated[str, Field(description="Natural language search query")],
    repositories: Annotated[
        Optional[Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]],
        Field(description="Optional list of repositories (owner/repo format). If omitted, auto-detected from query")
    ] = None,
    data_sources: Annotated[
        Optional[Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]],
        Field(description="Optional list of documentation identifiers (UUID, name, or URL). If omitted, auto-detected")
    ] = None,
    search_mode: Annotated[
        Literal["unified", "repositories", "sources"],
        Field(description="Search scope: 'unified' (both), 'repositories', or 'sources'")
    ] = "unified",
    include_sources: Annotated[bool, Field(description="Include source snippets and metadata in results")] = True
) -> List[TextContent]:
    """
    Natural-language search across indexed repositories and documentation.
    
    **Auto-Routing:** If no repositories or data_sources are specified, Nia will use hybrid search across everything.

    Args:
        query: Natural language search query.
        repositories: Optional list of repositories (owner/repo or owner/repo/tree/branch/dir).
        data_sources: Optional list of documentation identifiers (UUID, display name, or URL).
        search_mode: "repositories", "sources", or "unified". Automatically set to "unified" when mixing targets.
        include_sources: Whether to include source snippets and metadata.
    """

    def _normalize_targets(
        targets: Optional[Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]]
    ) -> List[Union[str, Dict[str, Any]]]:
        if targets is None:
            return []
        if isinstance(targets, str):
            # Handle stringified JSON arrays (e.g., '["owner/repo"]' from MCP clients)
            stripped = targets.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass
            # Single string identifier
            return [targets]
        if isinstance(targets, dict):
            return [targets]
        return targets

    try:
        client = await ensure_api_client()

        repo_targets = _normalize_targets(repositories)
        source_targets = _normalize_targets(data_sources)

        # UNIVERSAL SEARCH: If no sources specified, search ALL indexed public sources
        if not repo_targets and not source_targets:
            logger.info(f"No sources specified - performing universal search across ALL public sources: {query[:80]}")
            
            try:
                # Determine which source types to include based on search_mode
                include_repos = search_mode in ("unified", "repositories")
                include_docs = search_mode in ("unified", "sources")
                
                # Call universal search endpoint with AI compression enabled
                result = await client.universal_search(
                    query=query,
                    top_k=20,
                    include_repos=include_repos,
                    include_docs=include_docs,
                    alpha=0.7,  # 70% vector, 30% BM25
                    compress_output=True  # Enable AI compression for token efficiency
                )
                
                # Format universal search results
                results = result.get("results", [])
                sources_searched = result.get("sources_searched", 0)
                query_time_ms = result.get("query_time_ms", 0)
                errors = result.get("errors", [])
                compressed_answer = result.get("answer")
                
                if not results:
                    no_results_msg = f"No results found for '{query}' across {sources_searched} indexed public sources.\n\n"
                    no_results_msg += "**Try:**\n"
                    no_results_msg += "- Refining your query with more specific terms\n"
                    no_results_msg += "- Using `manage_resource(action='list')` to see available indexed sources\n"
                    no_results_msg += "- Indexing new sources with `index('https://github.com/owner/repo')`\n"
                    
                    if errors:
                        no_results_msg += f"\n⚠️ Some sources had errors: {', '.join(errors[:3])}"
                    
                    return [TextContent(type="text", text=no_results_msg)]
                
                # If we have a compressed answer, use that as the primary response
                if compressed_answer:
                    response_text = f"# 🌐 Answer\n\n"
                    response_text += f"*Searched {sources_searched} public sources in {query_time_ms}ms*\n\n"
                    response_text += compressed_answer
                    response_text += "\n\n---\n\n## Sources\n\n"
                    
                    # Add compact source list
                    for i, result_item in enumerate(results[:5], 1):
                        source = result_item.get("source", {})
                        source_type = source.get("type", "unknown")
                        source_url = source.get("url", "")
                        file_path = source.get("file_path", "")
                        
                        icon = "📦" if source_type == "repository" else "📚"
                        location = f" → `{file_path}`" if file_path else ""
                        response_text += f"{i}. {icon} {source_url}{location}\n"
                    
                    response_text += "\n💡 Use `read_source_content` to get full file contents.\n"
                else:
                    # Fallback to full results when compression unavailable
                    response_text = f"# 🌐 Universal Search Results\n\n"
                    response_text += f"*Searched {sources_searched} public sources in {query_time_ms}ms*\n\n"
                    
                    for i, result_item in enumerate(results[:10], 1):
                        source = result_item.get("source", {})
                        content = result_item.get("content", "")
                        score = result_item.get("score", 0)
                        
                        response_text += f"## Result {i}\n"
                        response_text += f"**Relevance Score:** {score:.3f}\n"
                        
                        source_type = source.get("type", "unknown")
                        source_url = source.get("url", "")
                        
                        if source_type == "repository":
                            response_text += f"**📦 Repository:** {source_url}\n"
                        else:
                            response_text += f"**📚 Documentation:** {source_url}\n"
                        
                        # Include file path if available
                        file_path = source.get("file_path")
                        if file_path:
                            response_text += f"**File:** `{file_path}`\n"
                        
                        # Include content preview if requested
                        if content and include_sources:
                            preview = content[:500] + "..." if len(content) > 500 else content
                            response_text += f"```\n{preview}\n```\n\n"
                        else:
                            response_text += "\n"
                    
                    response_text += "\n---\n"
                    response_text += "💡 **Need full content?** Use `read_source_content` with the source URL.\n"
                    response_text += "🔍 **Want to search specific sources?** Provide `repositories` or `data_sources` parameters.\n"
                
                if errors:
                    response_text += f"\n⚠️ *Some sources had errors: {', '.join(errors[:3])}*\n"
                
                return [TextContent(type="text", text=response_text)]
                
            except APIError as e:
                # Log but fall through to standard query as fallback
                logger.warning(f"Universal search failed, falling back to auto-hint: {e}")
            except Exception as e:
                logger.error(f"Universal search error, falling back to auto-hint: {e}")
            
            # Fallback: Let backend's auto-hint system try to route
            logger.info(f"Falling back to auto-hint routing for query: {query[:80]}")

        allowed_modes = {"unified", "repositories", "sources"}
        normalized_mode = search_mode if search_mode in allowed_modes else "unified"
        if repo_targets and source_targets:
            normalized_mode = "unified"
        elif repo_targets and not source_targets and normalized_mode == "sources":
            normalized_mode = "repositories"
        elif source_targets and not repo_targets and normalized_mode == "repositories":
            normalized_mode = "sources"

        messages = [{"role": "user", "content": query}]

        logger.info(
            "Searching repositories=%d data_sources=%d mode=%s",
            len(repo_targets),
            len(source_targets),
            normalized_mode,
        )

        response_parts: List[str] = []
        sources_parts: List[Any] = []
        follow_up_questions: List[str] = []

        async for chunk in client.query_unified(
            messages=messages,
            repositories=repo_targets,
            data_sources=source_targets,
            search_mode=normalized_mode,
            stream=True,
            include_sources=include_sources
        ):
            try:
                data = json.loads(chunk)

                if "content" in data and data["content"] and data["content"] != "[DONE]":
                    response_parts.append(data["content"])

                if "sources" in data and data["sources"]:
                    sources_parts.extend(data["sources"])

                if "follow_up_questions" in data and data["follow_up_questions"]:
                    follow_up_questions = data["follow_up_questions"]
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON chunk: {chunk}, error: {e}")
                continue

        response_text = "".join(response_parts)

        if sources_parts and include_sources:
            response_text += "\n\n## Sources\n\n"
            for i, source in enumerate(sources_parts[:10], 1):
                response_text += f"### Source {i}\n"

                if isinstance(source, str):
                    response_text += f"**Reference:** {source}\n\n"
                    continue
                if not isinstance(source, dict):
                    response_text += f"**Source:** {str(source)}\n\n"
                    continue

                metadata = source.get("metadata", {})
                repository = source.get("repository") or metadata.get("repository") or metadata.get("source_name")
                if repository:
                    response_text += f"**Repository:** {repository}\n"

                url = source.get("url") or metadata.get("url") or metadata.get("source") or metadata.get("sourceURL")
                if url:
                    response_text += f"**URL:** {url}\n"

                file_path = (
                    source.get("file")
                    or source.get("file_path")
                    or metadata.get("file_path")
                    or metadata.get("document_name")
                )
                if file_path:
                    response_text += f"**File:** `{file_path}`\n"

                title = source.get("title") or metadata.get("title")
                if title:
                    response_text += f"**Title:** {title}\n"

                content = source.get("preview") or source.get("content")
                if content:
                    if len(content) > 500:
                        content = content[:500] + "..."
                    response_text += f"```\n{content}\n```\n\n"
                else:
                    response_text += "*Referenced source*\n\n"

            response_text += "\n💡 **Need more context?**\n\n"
            response_text += "Use `read_source_content` with the repository or documentation identifier shown above to retrieve the full content.\n"

        if follow_up_questions:
            response_text += "\n\n## 🔍 Suggested Follow-up Questions\n\n"
            for i, question in enumerate(follow_up_questions, 1):
                response_text += f"{i}. {question}\n"
            response_text += "\n*These suggestions are based on the retrieved sources and can deepen your investigation.*\n"

        return [TextContent(type="text", text=response_text)]

    except APIError as e:
        logger.error(f"API Error searching: {e} (status_code={e.status_code}, detail={e.detail})")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text",
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
                )]
            return [TextContent(
                type="text",
                text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for higher limits."
            )]

        return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error searching: {e}")
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
            )]
        return [TextContent(type="text", text=f"❌ Error running search: {error_msg}")]


@mcp.tool()
async def manage_resource(
    action: Annotated[
        Literal["list", "status", "rename", "delete"],
        Field(description="Action to perform on the resource")
    ],
    resource_type: Annotated[
        Literal["repository", "documentation"] | None,
        Field(description="Type of resource (required for status/rename/delete, optional for list)")
    ] = None,
    identifier: Annotated[
        Optional[str],
        Field(description="Resource identifier: owner/repo for repos, UUID/name/URL for docs (required for status/rename/delete)")
    ] = None,
    new_name: Annotated[
        Optional[str],
        Field(description="New display name, 1-100 chars (required for rename action)")
    ] = None
) -> List[TextContent]:
    """
    Unified resource management tool for repositories and documentation.

    """
    try:
        # Validate required parameters based on action
        if action in ["status", "rename", "delete"]:
            if not resource_type:
                return [TextContent(
                    type="text",
                    text=f"❌ resource_type is required for action '{action}'"
                )]
            if not identifier:
                return [TextContent(
                    type="text",
                    text=f"❌ identifier is required for action '{action}'"
                )]

        if action == "rename":
            if not new_name:
                return [TextContent(
                    type="text",
                    text="❌ new_name is required for rename action"
                )]
            # Validate name length
            if len(new_name) > 100:
                return [TextContent(
                    type="text",
                    text="❌ Display name must be between 1 and 100 characters."
                )]

        client = await ensure_api_client()

        # ===== LIST ACTION =====
        if action == "list":
            lines = []

            # Determine what to list
            list_repos = resource_type in [None, "repository"]
            list_docs = resource_type in [None, "documentation"]

            if list_repos:
                repositories = await client.list_repositories()

                if repositories:
                    lines.append("# Indexed Repositories\n")
                    for repo in repositories:
                        status_icon = "✅" if repo.get("status") == "completed" else "⏳"

                        # Show display name if available, otherwise show repository
                        display_name = repo.get("display_name")
                        repo_name = repo['repository']

                        if display_name:
                            lines.append(f"\n## {status_icon} {display_name}")
                            lines.append(f"- **Repository:** {repo_name}")
                        else:
                            lines.append(f"\n## {status_icon} {repo_name}")

                        lines.append(f"- **Branch:** {repo.get('branch', 'main')}")
                        lines.append(f"- **Status:** {repo.get('status', 'unknown')}")
                        if repo.get("indexed_at"):
                            lines.append(f"- **Indexed:** {repo['indexed_at']}")
                        if repo.get("error"):
                            lines.append(f"- **Error:** {repo['error']}")

                        # Add usage hint for completed repositories
                        if repo.get("status") == "completed":
                            lines.append(f"- **Usage:** `search(\"query\", repositories=[\"{repo_name}\"])`")
                elif resource_type == "repository":
                    lines.append("No indexed repositories found.\n\n")
                    lines.append("Get started by indexing a repository:\n")
                    lines.append("Use `index` with a GitHub URL.")

            if list_docs:
                sources = await client.list_data_sources()

                if sources:
                    if lines:  # Add separator if we already have repositories
                        lines.append("\n---\n")
                    lines.append("# Indexed Documentation\n")

                    for source in sources:
                        status_icon = "✅" if source.get("status") == "completed" else "⏳"

                        # Show display name if available, otherwise show URL
                        display_name = source.get("display_name")
                        url = source.get('url', 'Unknown URL')

                        if display_name:
                            lines.append(f"\n## {status_icon} {display_name}")
                            lines.append(f"- **URL:** {url}")
                        else:
                            lines.append(f"\n## {status_icon} {url}")

                        lines.append(f"- **ID:** {source['id']}")
                        lines.append(f"- **Status:** {source.get('status', 'unknown')}")
                        lines.append(f"- **Type:** {source.get('source_type', 'web')}")
                        if source.get("page_count", 0) > 0:
                            lines.append(f"- **Pages:** {source['page_count']}")
                        if source.get("created_at"):
                            lines.append(f"- **Created:** {source['created_at']}")
                elif resource_type == "documentation":
                    lines.append("No indexed documentation found.\n\n")
                    lines.append("Get started by indexing documentation:\n")
                    lines.append("Use `index` with a URL.")

            if not lines:
                lines.append("No indexed resources found.\n\n")
                lines.append("Get started by indexing:\n")
                lines.append("- Use `index` for GitHub repos or URLs\n")

            return [TextContent(type="text", text="\n".join(lines))]

        # ===== STATUS ACTION =====
        elif action == "status":
            if resource_type == "repository":
                status = await client.get_repository_status(identifier)
                if not status:
                    return [TextContent(
                        type="text",
                        text=f"❌ Repository '{identifier}' not found."
                    )]
                title = f"Repository Status: {identifier}"
                status_key = "status"
            else:  # documentation
                status = await client.get_data_source_status(identifier)
                if not status:
                    return [TextContent(
                        type="text",
                        text=f"❌ Documentation source '{identifier}' not found."
                    )]
                title = f"Documentation Status: {status.get('url', 'Unknown URL')}"
                status_key = "status"

            # Format status with appropriate icon
            status_text = status.get(status_key, "unknown")
            status_icon = {
                "completed": "✅",
                "indexing": "⏳",
                "processing": "⏳",
                "failed": "❌",
                "pending": "🔄",
                "error": "❌"
            }.get(status_text, "❓")

            lines = [
                f"# {title}\n",
                f"{status_icon} **Status:** {status_text}"
            ]

            # Add resource-specific fields
            if resource_type == "repository":
                lines.append(f"**Branch:** {status.get('branch', 'main')}")
                if status.get("progress"):
                    progress = status["progress"]
                    if isinstance(progress, dict):
                        lines.append(f"**Progress:** {progress.get('percentage', 0)}%")
                        if progress.get("stage"):
                            lines.append(f"**Stage:** {progress['stage']}")
            else:  # documentation
                lines.append(f"**Source ID:** {identifier}")
                if status.get("page_count", 0) > 0:
                    lines.append(f"**Pages Indexed:** {status['page_count']}")
                if status.get("details"):
                    details = status["details"]
                    if details.get("progress"):
                        lines.append(f"**Progress:** {details['progress']}%")
                    if details.get("stage"):
                        lines.append(f"**Stage:** {details['stage']}")

            # Common fields
            if status.get("indexed_at"):
                lines.append(f"**Indexed:** {status['indexed_at']}")
            elif status.get("created_at"):
                lines.append(f"**Created:** {status['created_at']}")

            if status.get("error"):
                lines.append(f"**Error:** {status['error']}")

            return [TextContent(type="text", text="\n".join(lines))]

        # ===== RENAME ACTION =====
        elif action == "rename":
            if resource_type == "repository":
                result = await client.rename_repository(identifier, new_name)
                resource_desc = f"repository '{identifier}'"
            else:  # documentation
                result = await client.rename_data_source(identifier, new_name)
                resource_desc = f"documentation source"

            if result.get("success"):
                return [TextContent(
                    type="text",
                    text=f"✅ Successfully renamed {resource_desc} to '{new_name}'"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to rename {resource_type}: {result.get('message', 'Unknown error')}"
                )]

        # ===== DELETE ACTION =====
        elif action == "delete":
            if resource_type == "repository":
                success = await client.delete_repository(identifier)
                resource_desc = f"repository: {identifier}"
            else:  # documentation
                success = await client.delete_data_source(identifier)
                resource_desc = f"documentation source: {identifier}"

            if success:
                return [TextContent(
                    type="text",
                    text=f"✅ Successfully deleted {resource_desc}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to delete {resource_desc}"
                )]

    except APIError as e:
        logger.error(f"API Error in manage_resource ({action}): {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 403 or "free tier limit" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                error_msg = f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
            else:
                error_msg += "\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for higher limits."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error in manage_resource ({action}): {e}")
        error_msg = str(e)
        if "indexing operations" in error_msg.lower() or "lifetime limit" in error_msg.lower():
            return [TextContent(
                type="text",
                text=f"❌ {error_msg}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
            )]
        return [TextContent(
            type="text",
            text=f"❌ Error in {action} operation: {error_msg}"
        )]

@mcp.tool()
async def get_github_file_tree(
    repository: Annotated[str, Field(description="Repository identifier (owner/repo format, e.g., 'facebook/react')")],
    branch: Annotated[Optional[str], Field(description="Branch name (defaults to repository's default branch)")] = None,
    include_paths: Annotated[Optional[List[str]], Field(description="Only show files in these paths (e.g., ['src/', 'lib/'])")] = None,
    exclude_paths: Annotated[Optional[List[str]], Field(description="Hide files in these paths (e.g., ['node_modules/', 'dist/'])")] = None,
    file_extensions: Annotated[Optional[List[str]], Field(description="Only show these file types (e.g., ['.py', '.js'])")] = None,
    exclude_extensions: Annotated[Optional[List[str]], Field(description="Hide these file types (e.g., ['.md', '.lock'])")] = None,
    show_full_paths: Annotated[bool, Field(description="Show full paths instead of tree structure")] = False
) -> List[TextContent]:
    """
    Get file and folder structure directly from GitHub API (no indexing required).
    """
    try:
        client = await ensure_api_client()

        # Require explicit repository specification
        if not repository:
            return [TextContent(
                type="text",
                text="🔍 **Please specify which repository to get file tree from:**\n\n"
                     "Usage: `get_github_file_tree(\"owner/repo\")`\n\n"
                     "**Examples:**\n"
                     "```\n"
                     "get_github_file_tree(\"facebook/react\")\n"
                     "get_github_file_tree(\"microsoft/vscode\", \"main\")\n"
                     "```"
            )]

        logger.info(f"Getting GitHub tree for repository: {repository}, branch: {branch or 'default'}, filters: {include_paths or exclude_paths or file_extensions or exclude_extensions}")

        # Call API with filters
        result = await client.get_github_tree(
            repository,
            branch=branch,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            file_extensions=file_extensions,
            exclude_extensions=exclude_extensions,
            show_full_paths=show_full_paths
        )

        # Format response
        response_text = f"# 📁 GitHub File Tree: {result.get('owner')}/{result.get('repo')}\n\n"
        response_text += f"**Branch:** `{result.get('branch')}`\n"
        response_text += f"**SHA:** `{result.get('sha')}`\n"
        response_text += f"**Retrieved:** {result.get('retrieved_at')}\n"
        response_text += f"**Source:** GitHub API (always current)\n"

        # Show active filters
        filters = result.get("filters_applied", {})
        active_filters = []
        if filters.get("include_paths"):
            active_filters.append(f"📂 Included paths: {', '.join(filters['include_paths'])}")
        if filters.get("exclude_paths"):
            active_filters.append(f"🚫 Excluded paths: {', '.join(filters['exclude_paths'])}")
        if filters.get("file_extensions"):
            active_filters.append(f"📄 File types: {', '.join(filters['file_extensions'])}")
        if filters.get("exclude_extensions"):
            active_filters.append(f"🚫 Excluded types: {', '.join(filters['exclude_extensions'])}")
        if filters.get("show_full_paths"):
            active_filters.append(f"📍 Showing full paths")

        if active_filters:
            response_text += f"**Filters:** {' | '.join(active_filters)}\n"

        response_text += "\n"

        # Add stats
        stats = result.get("stats", {})
        response_text += "## 📊 Statistics\n\n"
        response_text += f"- **Total Files:** {stats.get('total_files', 0)}\n"
        response_text += f"- **Total Directories:** {stats.get('total_directories', 0)}\n"
        response_text += f"- **Max Depth:** {stats.get('max_depth', 0)} levels\n"

        # File extensions breakdown
        file_extensions = stats.get("file_extensions", {})
        if file_extensions:
            response_text += f"\n**File Types:**\n"
            sorted_extensions = sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_extensions[:10]:  # Show top 10
                ext_name = ext if ext != "no_extension" else "(no extension)"
                response_text += f"  - `{ext_name}`: {count} files\n"

        # Tree structure (full)
        tree_text = result.get("tree_text", "")
        if tree_text:
            response_text += "\n## 🌳 Directory Structure\n\n"
            response_text += "```\n"
            response_text += tree_text
            response_text += "\n```\n"

        # Truncation warning
        if result.get("truncated"):
            response_text += "\n⚠️ **Note:** Repository is very large. Tree may be truncated by GitHub.\n"

        # Usage hints
        response_text += "\n---\n"
        response_text += "💡 **Next Steps:**\n"
        response_text += f"- Index this repository: `index(\"{repository}\")`\n"
        response_text += "- Refine with filters (examples below)\n"
        response_text += "- Use `manage_resource(\"status\", \"repository\", \"{}\")` to check indexing status\n\n".format(repository)

        # Show filter examples if no filters were used
        if not active_filters:
            response_text += "**Filter Examples:**\n"
            response_text += f"- Only Python files: `file_extensions=[\".py\"]`\n"
            response_text += f"- Exclude tests: `exclude_paths=[\"test/\", \"tests/\"]`\n"
            response_text += f"- Only src directory: `include_paths=[\"src/\"]`\n"
            response_text += f"- Full paths: `show_full_paths=True`\n"

        return [TextContent(type="text", text=response_text)]

    except APIError as e:
        logger.error(f"API Error getting GitHub tree: {e}")
        error_msg = f"❌ {str(e)}"
        if e.status_code == 404:
            error_msg = f"❌ Repository '{repository}' not found or not accessible.\n\n"
            error_msg += "**Possible reasons:**\n"
            error_msg += "- Repository doesn't exist\n"
            error_msg += "- Repository is private and GitHub App not installed\n"
            error_msg += "- Invalid owner/repo format\n\n"
            error_msg += "**Note:** You must have the repository indexed first, or have GitHub App installed."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Error getting GitHub tree: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error getting GitHub file tree: {str(e)}"
        )]

@mcp.tool()
async def nia_web_search(
    query: Annotated[str, Field(description="Natural language search query (e.g., 'best RAG implementations')")],
    num_results: Annotated[int, Field(description="Number of results to return (default: 5, max: 10)")] = 5,
    category: Annotated[
        Literal["github", "company", "research paper", "news", "tweet", "pdf"] | None,
        Field(description="Filter by category")
    ] = None,
    days_back: Annotated[Optional[int], Field(description="Only show results from the last N days")] = None,
    find_similar_to: Annotated[Optional[str], Field(description="URL to find similar content")] = None
) -> List[TextContent]:
    """
    Search repositories, documentation, and other content using web search.
    """
    try:
        client = await ensure_api_client()
        
        logger.info(f"Searching content for query: {query}")
        
        # Use the API client method instead of direct HTTP call
        result = await client.web_search(
            query=query,
            num_results=num_results,
            category=category,
            days_back=days_back,
            find_similar_to=find_similar_to
        )
        
        # Extract results
        github_repos = result.get("github_repos", [])
        documentation = result.get("documentation", [])
        other_content = result.get("other_content", [])
        
        # Format response to naturally guide next actions
        response_text = f"## 🔍 Nia Web Search Results for: \"{query}\"\n\n"
        
        if days_back:
            response_text += f"*Showing results from the last {days_back} days*\n\n"
        
        if find_similar_to:
            response_text += f"*Finding content similar to: {find_similar_to}*\n\n"
        
        # GitHub Repositories Section
        if github_repos:
            response_text += f"### 📦 GitHub Repositories ({len(github_repos)} found)\n\n"
            
            for i, repo in enumerate(github_repos[:num_results], 1):
                response_text += f"**{i}. {repo['title']}**\n"
                response_text += f"   📍 `{repo['url']}`\n"
                if repo.get('published_date'):
                    response_text += f"   📅 Updated: {repo['published_date']}\n"
                if repo['summary']:
                    response_text += f"   📝 {repo['summary']}...\n"
                if repo['highlights']:
                    response_text += f"   ✨ Key features: {', '.join(repo['highlights'])}\n"
                response_text += "\n"
            
            # Be more aggressive based on query specificity
            if len(github_repos) == 1 or any(specific_word in query.lower() for specific_word in ["specific", "exact", "particular", "find me", "looking for"]):
                response_text += "**🚀 RECOMMENDED ACTION - Index this repository with Nia:**\n"
                response_text += f"```\nIndex {github_repos[0]['owner_repo']}\n```\n"
                response_text += "✨ This will enable AI-powered code search, understanding, and analysis!\n\n"
            else:
                response_text += "**🚀 Make these repositories searchable with NIA's AI:**\n"
                response_text += f"- **Quick start:** Say \"Index {github_repos[0]['owner_repo']}\"\n"
                response_text += "- **Index multiple:** Say \"Index all repositories\"\n"
                response_text += "- **Benefits:** AI-powered code search, architecture understanding, implementation details\n\n"
        
        # Documentation Section
        if documentation:
            response_text += f"### 📚 Documentation ({len(documentation)} found)\n\n"
            
            for i, doc in enumerate(documentation[:num_results], 1):
                response_text += f"**{i}. {doc['title']}**\n"
                response_text += f"   📍 `{doc['url']}`\n"
                if doc['summary']:
                    response_text += f"   📝 {doc['summary']}...\n"
                if doc.get('highlights'):
                    response_text += f"   ✨ Key topics: {', '.join(doc['highlights'])}\n"
                response_text += "\n"
            
            # Be more aggressive for documentation too
            if len(documentation) == 1 or any(specific_word in query.lower() for specific_word in ["docs", "documentation", "guide", "tutorial", "reference"]):
                response_text += "**📖 RECOMMENDED ACTION - Index this documentation with NIA:**\n"
                response_text += f"```\nIndex documentation {documentation[0]['url']}\n```\n"
                response_text += "✨ NIA will make this fully searchable with AI-powered Q&A!\n\n"
            else:
                response_text += "**📖 Make this documentation AI-searchable with NIA:**\n"
                response_text += f"- **Quick start:** Say \"Index documentation {documentation[0]['url']}\"\n"
                response_text += "- **Index all:** Say \"Index all documentation\"\n"
                response_text += "- **Benefits:** Instant answers, smart search, code examples extraction\n\n"
        
        # Other Content Section
        if other_content and not github_repos and not documentation:
            response_text += f"### 🌐 Other Content ({len(other_content)} found)\n\n"
            
            for i, content in enumerate(other_content[:num_results], 1):
                response_text += f"**{i}. {content['title']}**\n"
                response_text += f"   📍 `{content['url']}`\n"
                if content['summary']:
                    response_text += f"   📝 {content['summary']}...\n"
                response_text += "\n"
        
        # No results found
        if not github_repos and not documentation and not other_content:
            response_text = f"No results found for '{query}'. Try:\n"
            response_text += "- Using different keywords\n"
            response_text += "- Being more specific (e.g., 'Python RAG implementation')\n"
            response_text += "- Including technology names (e.g., 'LangChain', 'TypeScript')\n"
        
        # Add prominent call-to-action if we found indexable content
        if github_repos or documentation:
            response_text += "\n## 🎯 **Ready to unlock nia's tools**\n"
        
        # Add search metadata
        response_text += f"\n---\n"
        response_text += f"*Searched {result.get('total_results', 0)} sources using NIA Web Search*"
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error in web search: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for higher limits."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error in NIA web search: {str(e)}")
        return [TextContent(
            type="text",
            text=f"❌ NIA Web Search error: {str(e)}\n\n"
                 "This might be due to:\n"
                 "- Network connectivity issues\n"
                 "- Service temporarily unavailable"
        )]

@mcp.tool()
async def nia_deep_research_agent(
    query: Annotated[str, Field(description="Research question (e.g., 'Compare top 3 RAG frameworks with pros/cons')")],
    output_format: Annotated[Optional[str], Field(description="Structure hint (e.g., 'comparison table', 'pros and cons list')")] = None
) -> List[TextContent]:
    """
    Perform deep, multi-step research on a topic using advanced AI research capabilities.
    """
    try:
        client = await ensure_api_client()
        
        logger.info(f"Starting deep research for: {query}")
        
        # Use the API client method with proper timeout handling
        try:
            result = await asyncio.wait_for(
                client.deep_research(query=query, output_format=output_format),
                timeout=720.0  # 12 minutes to allow for longer research tasks
            )
        except asyncio.TimeoutError:
            logger.error(f"Deep research timed out after 12 minutes for query: {query}")
            return [TextContent(
                type="text",
                text="❌ Research timed out. The query may be too complex. Try:\n"
                     "- Breaking it into smaller questions\n"  
                     "- Using more specific keywords\n"
                     "- Trying the nia_web_search tool for simpler queries"
            )]
        
        # Format the research results
        response_text = f"## 🔬 NIA Deep Research Agent Results\n\n"
        response_text += f"**Query:** {query}\n\n"
        
        if result.get("data"):
            response_text += "### 📊 Research Findings:\n\n"
            
            # Pretty print the JSON data
            
            formatted_data = json.dumps(result["data"], indent=2)
            response_text += f"```json\n{formatted_data}\n```\n\n"
            
            # Add citations if available
            if result.get("citations"):
                response_text += "### 📚 Sources & Citations:\n\n"
                citation_num = 1
                for field, citations in result["citations"].items():
                    if citations:
                        response_text += f"**{field}:**\n"
                        for citation in citations[:3]:  # Limit to 3 citations per field
                            response_text += f"{citation_num}. [{citation.get('title', 'Source')}]({citation.get('url', '#')})\n"
                            if citation.get('snippet'):
                                response_text += f"   > {citation['snippet'][:150]}...\n"
                            citation_num += 1
                        response_text += "\n"
            
            response_text += "### 💡 RECOMMENDED NEXT ACTIONS WITH NIA:\n\n"
            
            # Extract potential repos and docs from the research data
            repos_found = []
            docs_found = []
            
            # Helper function to extract URLs from nested data structures
            def extract_urls_from_data(data, urls_list=None):
                if urls_list is None:
                    urls_list = []
                
                if isinstance(data, dict):
                    for value in data.values():
                        extract_urls_from_data(value, urls_list)
                elif isinstance(data, list):
                    for item in data:
                        extract_urls_from_data(item, urls_list)
                elif isinstance(data, str):
                    # Check if this string is a URL
                    if data.startswith(('http://', 'https://')):
                        urls_list.append(data)
                
                return urls_list
            
            # Extract all URLs from the data
            all_urls = extract_urls_from_data(result["data"])
            
            # Filter for GitHub repos and documentation
            import re
            github_pattern = r'github\.com/([a-zA-Z0-9-]+/[a-zA-Z0-9-_.]+)'
            
            for url in all_urls:
                # Check for GitHub repos
                github_match = re.search(github_pattern, url)
                if github_match and '/tree/' not in url and '/blob/' not in url:
                    repos_found.append(github_match.group(1))
                # Check for documentation URLs
                elif any(doc_indicator in url.lower() for doc_indicator in ['docs', 'documentation', '.readthedocs.', '/guide', '/tutorial']):
                    docs_found.append(url)
            
            # Remove duplicates and limit results
            repos_found = list(set(repos_found))[:3]
            docs_found = list(set(docs_found))[:3]
            
            if repos_found:
                response_text += "**🚀 DISCOVERED REPOSITORIES - Index with NIA for deep analysis:**\n"
                for repo in repos_found:
                    response_text += f"```\nIndex {repo}\n```\n"
                response_text += "✨ Enable AI-powered code search and architecture understanding!\n\n"
            
            if docs_found:
                response_text += "**📖 DISCOVERED DOCUMENTATION - Index with NIA for smart search:**\n"
                for doc in docs_found[:2]:  # Limit to 2 for readability
                    response_text += f"```\nIndex documentation {doc}\n```\n"
                response_text += "✨ Make documentation instantly searchable with AI Q&A!\n\n"
            
            if not repos_found and not docs_found:
                response_text += "**🔍 Manual indexing options:**\n"
                response_text += "- If you see any GitHub repos mentioned: Say \"Index [owner/repo]\"\n"
                response_text += "- If you see any documentation sites: Say \"Index documentation [url]\"\n"
                response_text += "- These will unlock NIA's powerful AI search capabilities!\n\n"
            
            response_text += "**📊 Other actions:**\n"
            response_text += "- Ask follow-up questions about the research\n"
            response_text += "- Request a different analysis format\n"
            response_text += "- Search for more specific information\n"
        else:
            response_text += "No structured data returned. The research may need a more specific query."
        
        return [TextContent(type="text", text=response_text)]
        
    except APIError as e:
        logger.error(f"API Error in deep research: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower() or "indexing operations" in str(e).lower():
            if e.detail and "3 free indexing operations" in e.detail:
                return [TextContent(
                    type="text", 
                    text=f"❌ {e.detail}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for more indexing jobs."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ {str(e)}\n\n💡 Tip: You've reached the free tier limit. Upgrade to Pro for higher limits."
                )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error in deep research: {str(e)}")
        return [TextContent(
            type="text",
            text=f"❌ Research error: {str(e)}\n\n"
                 "Try simplifying your question or using the regular nia_web_search tool."
        )]

# TEMPORARILY COMMENTED OUT - Oracle agent under maintenance
# @mcp.tool()
# async def nia_oracle(
#     query: str,
#     output_format: Optional[str] = None,
#     repositories: Optional[str] = None,
#     data_sources: Optional[str] = None
# ) -> List[TextContent]:
#     """
#     Run the in-house Oracle research agent (Claude-powered) that orchestrates Nia tools.
#
#     Args:
#         query: Research objective (e.g., "Security review of internal auth flow")
#         output_format: Optional format hint ("briefing", "table", etc.)
#         repositories: Optional comma-separated list of repositories to emphasize
#         data_sources: Optional comma-separated list of documentation source IDs or URLs to search.
#                      If not provided, Oracle will auto-discover available indexed documentation.
#     """
#     try:
#         client = await ensure_api_client()
#
#         repo_list = None
#         if repositories:
#             repo_list = [repo.strip() for repo in repositories.split(",") if repo.strip()]
#
#         data_source_list = None
#         if data_sources:
#             data_source_list = [ds.strip() for ds in data_sources.split(",") if ds.strip()]
#
#         logger.info(f"Starting Oracle research for: {query}")
#         if data_source_list:
#             logger.info(f"Using {len(data_source_list)} data sources: {data_source_list[:3]}")
#         else:
#             logger.info("No data sources specified - Oracle will auto-discover indexed documentation")
#
#         result = await client.oracle_research(
#             query=query,
#             repositories=repo_list,
#             data_sources=data_source_list,
#             output_format=output_format
#         )
#
#         response_text = f"## 🔮 NIA Oracle Research Report\n\n**Query:** {query}\n\n"
#         summary = result.get("summary") or "No summary was returned."
#         response_text += f"{summary}\n\n"
#
#         citations = result.get("citations") or []
#         if citations:
#             response_text += "### 📚 Citations\n"
#             for idx, citation in enumerate(citations, start=1):
#                 label = citation.get("label") or citation.get("repository") or f"Source {idx}"
#                 url = citation.get("url")
#                 if url:
#                     response_text += f"{idx}. [{label}]({url})\n"
#                 else:
#                     response_text += f"{idx}. {label}\n"
#             response_text += "\n"
#
#         tool_calls = result.get("tool_calls") or []
#         if tool_calls:
#             response_text += "### 🛠️ Tool Decisions\n"
#             for call in tool_calls:
#                 name = call.get("name", "tool")
#                 error = call.get("error")
#                 if error:
#                     response_text += f"- {name}: ⚠️ {error}\n"
#                 else:
#                     response_text += f"- {name}: executed successfully\n"
#             response_text += "\n"
#
#         return [TextContent(type="text", text=response_text)]
#
#     except APIError as e:
#         logger.error(f"API error in Oracle research: {e}")
#         return [TextContent(type="text", text=f"❌ Oracle research error: {str(e)}")]
#     except Exception as e:
#         logger.error(f"Unexpected Oracle error: {e}", exc_info=True)
#         return [TextContent(type="text", text=f"❌ Oracle research error: {str(e)}")]

def _normalize_repo_source_identifier(
    source_identifier: str,
    metadata: Optional[Dict[str, Any]],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Ensure repository identifiers follow owner/repo:path/to/file format.

    Returns (normalized_identifier, repo_name, file_path).
    """
    identifier = (source_identifier or "").strip()
    meta = metadata or {}

    def _clean_repo(repo_value: Optional[str]) -> Optional[str]:
        if not repo_value:
            return None
        cleaned = repo_value.strip()
        if ":" in cleaned:
            cleaned = cleaned.split(":", 1)[0]
        return cleaned.strip().strip("/")

    if not identifier:
        return None, None, None

    if ":" in identifier:
        repo_part, path_part = identifier.split(":", 1)
        repo_part = _clean_repo(repo_part)
        path_part = path_part.lstrip("/")
        if repo_part and path_part:
            return f"{repo_part}:{path_part}", repo_part, path_part

    repo_hint = _clean_repo(
        meta.get("repository")
        or meta.get("repo")
        or meta.get("project")
        or meta.get("repo_name")
    )
    path_hint = meta.get("file_path") or meta.get("path")

    if repo_hint and path_hint and identifier == path_hint:
        normalized = f"{repo_hint}:{path_hint.lstrip('/')}"
        return normalized, repo_hint, path_hint.lstrip("/")

    if repo_hint and identifier.startswith(f"{repo_hint}/"):
        inferred_path = identifier[len(repo_hint) + 1 :].lstrip("/")
        if inferred_path:
            return f"{repo_hint}:{inferred_path}", repo_hint, inferred_path

    if repo_hint and identifier and identifier != repo_hint:
        inferred_path = identifier.lstrip("/")
        return f"{repo_hint}:{inferred_path}", repo_hint, inferred_path

    parts = identifier.split("/")
    if len(parts) >= 3:
        repo_candidate = "/".join(parts[:2]).strip()
        path_candidate = "/".join(parts[2:]).lstrip("/")
        if repo_candidate and path_candidate:
            return f"{repo_candidate}:{path_candidate}", repo_candidate, path_candidate

    if repo_hint and path_hint:
        normalized = f"{repo_hint}:{path_hint.lstrip('/')}"
        return normalized, repo_hint, path_hint.lstrip("/")

    return None, None, None


@mcp.tool()
async def read_source_content(
    source_type: Annotated[
        Literal["repository", "documentation"],
        Field(description="Type of source to read")
    ],
    source_identifier: Annotated[
        str,
        Field(description="For repo: 'owner/repo:path/to/file.py'. For docs: source URL or document ID")
    ],
    metadata: Annotated[
        Optional[Dict[str, Any]],
        Field(description="Optional metadata from search results to help locate the source")
    ] = None
) -> List[TextContent]:
    """
    Read the full content of a specific source file or document.
    """
    try:
        logger.info("Reading source content - type: %s, identifier: %s", source_type, source_identifier)

        normalized_identifier = source_identifier
        inferred_repo = None
        inferred_path = None
        if source_type == "repository":
            normalized_identifier, inferred_repo, inferred_path = _normalize_repo_source_identifier(
                source_identifier,
                metadata,
            )
            if not normalized_identifier:
                guidance = textwrap.dedent(
                    """
                    ❌ Unable to determine repository file reference.

                    Please specify sources in `owner/repo:path/to/file.ext` format.
                    Examples:
                      • astropy/astropy:astropy/cosmology/_src/core.py
                      • facebook/react:packages/react/src/ReactHooks.js

                    If you only have the file path, include `metadata.repository` when calling this tool.
                    """
                ).strip()
                return [TextContent(type="text", text=guidance)]
            if normalized_identifier != source_identifier:
                logger.info("Normalized repository source identifier: %s -> %s", source_identifier, normalized_identifier)

        client = await ensure_api_client()

        # Call the API to get source content
        result = await client.get_source_content(
            source_type=source_type,
            source_identifier=normalized_identifier,
            metadata=metadata or {}
        )
        
        if not result or not result.get("success"):
            error_msg = result.get("error", "Unknown error") if result else "Failed to fetch source content"
            return [TextContent(
                type="text",
                text=f"❌ Error reading source: {error_msg}"
            )]
        
        # Format the response
        content = result.get("content", "")
        source_metadata = result.get("metadata", {})
        
        # Build response with metadata header
        response_lines = []
        
        if source_type == "repository":
            repo_name = inferred_repo or source_metadata.get("repository", "Unknown")
            file_path = inferred_path or source_metadata.get(
                "file_path",
                normalized_identifier.split(":", 1)[-1] if ":" in normalized_identifier else "Unknown",
            )
            branch = source_metadata.get("branch", "main")
            
            response_lines.extend([
                f"# Source: {repo_name}",
                f"**File:** `{file_path}`",
                f"**Branch:** {branch}",
                ""
            ])
            
            if source_metadata.get("url"):
                response_lines.append(f"**GitHub URL:** {source_metadata['url']}")
                response_lines.append("")
            
            # Add file info if available
            if source_metadata.get("size"):
                response_lines.append(f"**Size:** {source_metadata['size']} bytes")
            if source_metadata.get("language"):
                response_lines.append(f"**Language:** {source_metadata['language']}")
                
            response_lines.extend(["", "## Content", ""])
            
            # Add code block with language hint
            language = source_metadata.get("language", "").lower() or "text"
            response_lines.append(f"```{language}")
            response_lines.append(content)
            response_lines.append("```")
            
        elif source_type == "documentation":
            url = source_metadata.get("url", source_identifier)
            title = source_metadata.get("title", "Documentation")
            
            response_lines.extend([
                f"# Documentation: {title}",
                f"**URL:** {url}",
                ""
            ])
            
            if source_metadata.get("last_updated"):
                response_lines.append(f"**Last Updated:** {source_metadata['last_updated']}")
                response_lines.append("")
                
            response_lines.extend(["## Content", "", content])
        
        else:
            # Generic format for unknown source types
            response_lines.extend([
                f"# Source Content",
                f"**Type:** {source_type}",
                f"**Identifier:** {source_identifier}",
                "",
                "## Content",
                "",
                content
            ])
        
        return [TextContent(type="text", text="\n".join(response_lines))]
        
    except APIError as e:
        logger.error(f"API Error reading source content: {e}")
        if e.status_code == 403 or "free tier limit" in str(e).lower():
            return [TextContent(
                type="text",
                text=f"❌ {str(e)}\n\n💡 Tip: Upgrade to Pro at https://trynia.ai/billing for higher limits."
            )]
        else:
            return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error reading source content: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error reading source content: {str(e)}"
        )]

# Documentation Virtual Filesystem Tools

@mcp.tool()
async def doc_tree(
    source_identifier: Annotated[str, Field(description="Documentation source (UUID, display name, or URL)")]
) -> List[TextContent]:
    """
    Get the filesystem-like tree structure of indexed documentation.
    
    Shows all indexed pages organized as a virtual file tree, making it easy
    to browse documentation structure without remembering URLs.
        
    Example:
        doc_tree("firecrawl-docs")
        doc_tree("https://docs.firecrawl.dev/")
        doc_tree("86c923b8-49a1-4b66-af5b-7f60e449687c")
    """
    try:
        client = await ensure_api_client()
        
        # Resolve identifier to source_id
        sources = await client.list_data_sources()
        source_id = None
        
        for source in sources:
            # Match by ID, URL, or display name
            if (source.get("id") == source_identifier or
                source.get("url") == source_identifier or
                source.get("display_name") == source_identifier):
                source_id = source.get("id")
                break
        
        if not source_id:
            # Try using identifier as-is (might be a valid ID)
            source_id = source_identifier
        
        # Get tree
        result = await client.get_doc_tree(source_id)
        
        if not result.get("success"):
            return [TextContent(
                type="text",
                text=f"❌ Failed to get documentation tree: {result.get('message', 'Unknown error')}"
            )]
        
        # Format response
        tree_string = result.get("tree_string", "")
        page_count = result.get("page_count", 0)
        base_url = result.get("base_url", "")
        
        response = f"# Documentation Tree: {base_url}\n\n"
        response += f"**Total Pages:** {page_count}\n\n"
        
        if tree_string:
            response += "```\n"
            response += tree_string
            response += "\n```\n\n"
            response += "**Usage:**\n"
            response += f"- Use `doc_ls('{source_identifier}', '/path')` to list a specific directory\n"
            response += f"- Use `doc_read('{source_identifier}', '/path/file.md')` to read a page\n"
            response += f"- Use `doc_grep('{source_identifier}', 'pattern')` to search content\n"
        else:
            response += "No pages indexed yet.\n"
        
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API Error getting doc tree: {e}")
        return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error getting doc tree: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]

@mcp.tool()
async def doc_ls(
    source_identifier: Annotated[str, Field(description="Documentation source (UUID, display name, or URL)")],
    path: Annotated[str, Field(description="Virtual path to list")] = "/"
) -> List[TextContent]:
    """
    List contents of a virtual directory in the documentation.
    
    Shows files (pages) and subdirectories at the specified path,
    similar to the Unix 'ls' command.
    """
    try:
        client = await ensure_api_client()
        
        # Resolve identifier to source_id
        sources = await client.list_data_sources()
        source_id = None
        
        for source in sources:
            if (source.get("id") == source_identifier or
                source.get("url") == source_identifier or
                source.get("display_name") == source_identifier):
                source_id = source.get("id")
                break
        
        if not source_id:
            source_id = source_identifier
        
        # List directory
        result = await client.get_doc_ls(source_id, path)
        
        if not result.get("success"):
            return [TextContent(
                type="text",
                text=f"❌ Failed to list directory: {result.get('message', 'Unknown error')}"
            )]
        
        # Format response
        directories = result.get("directories", [])
        files = result.get("files", [])
        total = result.get("total", 0)
        
        response = f"# Directory Listing: {path}\n\n"
        
        if directories:
            response += "## Directories\n\n"
            for dir_name in directories:
                response += f"- {dir_name}/\n"
            response += "\n"
        
        if files:
            response += "## Files\n\n"
            for file_name in files:
                response += f"- {file_name}\n"
            response += "\n"
        
        if total == 0:
            response += "Empty directory.\n"
        else:
            response += f"**Total:** {len(directories)} directories, {len(files)} files\n"
        
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API Error listing directory: {e}")
        return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]

@mcp.tool()
async def doc_read(
    source_identifier: Annotated[str, Field(description="Documentation source (UUID, display name, or URL)")],
    path: Annotated[str, Field(description="Virtual path to the page (e.g., /api/auth.md)")],
    line_start: Annotated[Optional[int], Field(description="Start line (1-based, inclusive)")] = None,
    line_end: Annotated[Optional[int], Field(description="End line (1-based, inclusive)")] = None,
    max_length: Annotated[Optional[int], Field(description="Max characters to return")] = None
) -> List[TextContent]:
    """
    Read content of a documentation page by its virtual filesystem path.
    
    More intuitive than remembering URLs - just use the path from doc_tree or doc_ls.
    Supports line range slicing and length truncation.
        
    Example:
        doc_read("firecrawl-docs", "/api/scrape.md")
        doc_read("nextjs-docs", "/app/building-your-application/routing.md", line_start=1, line_end=50)
    """
    try:
        client = await ensure_api_client()
        
        # Resolve identifier to source_id
        sources = await client.list_data_sources()
        source_id = None
        source_info = None
        
        for source in sources:
            if (source.get("id") == source_identifier or
                source.get("url") == source_identifier or
                source.get("display_name") == source_identifier):
                source_id = source.get("id")
                source_info = source
                break
        
        if not source_id:
            source_id = source_identifier
        
        # Read file
        result = await client.get_doc_read(
            source_id, 
            path,
            line_start=line_start,
            line_end=line_end,
            max_length=max_length
        )
        
        if not result.get("success"):
            error_msg = result.get("message", "Unknown error")
            return [TextContent(
                type="text",
                text=f"❌ Failed to read file: {error_msg}\n\n"
                     f"Try using `doc_tree('{source_identifier}')` to see available paths."
            )]
        
        # Format response
        content = result.get("content", "")
        url = result.get("url", "")
        metadata = result.get("metadata", {})
        total_lines = result.get("total_lines")
        returned_lines = result.get("returned_lines")
        truncated = result.get("truncated", False)
        
        response = f"# {path}\n\n"
        response += f"**URL:** {url}\n"
        
        if total_lines:
            response += f"**Total Lines:** {total_lines}\n"
        if returned_lines:
            response += f"**Returned Lines:** {returned_lines[0]}-{returned_lines[1]}\n"
        if truncated:
            response += "**Note:** Content was truncated\n"
        
        if metadata.get("title"):
            response += f"**Title:** {metadata['title']}\n"
        
        response += "\n---\n\n"
        response += content
        
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API Error reading file: {e}")
        return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]

@mcp.tool()
async def doc_grep(
    source_identifier: Annotated[str, Field(description="Documentation source (UUID, display name, or URL)")],
    pattern: Annotated[str, Field(description="Regex pattern to search for")],
    path: Annotated[str, Field(description="Limit search to this path prefix")] = "/",
    context_lines: Annotated[Optional[int], Field(description="Lines before AND after (shorthand for A/B)")] = None,
    A: Annotated[Optional[int], Field(description="Lines after each match (like grep -A)")] = None,
    B: Annotated[Optional[int], Field(description="Lines before each match (like grep -B)")] = None,
    case_sensitive: Annotated[bool, Field(description="Case-sensitive matching (default: insensitive)")] = False,
    whole_word: Annotated[bool, Field(description="Match whole words only")] = False,
    fixed_string: Annotated[bool, Field(description="Treat pattern as literal string, not regex")] = False,
    max_matches_per_file: Annotated[int, Field(description="Max matches per file")] = 10,
    max_total_matches: Annotated[int, Field(description="Max total matches")] = 100,
    output_mode: Annotated[Literal["content", "files_with_matches", "count"], Field(description="Output format")] = "content",
    highlight: Annotated[bool, Field(description="Add >>markers<< around matched text")] = False
) -> List[TextContent]:
    """
    Search documentation content with a regex pattern.
    
    Like the Unix 'grep' command, but for indexed documentation.
    Searches through all pages and returns matches with context.
    
    Supports asymmetric context lines (A for after, B for before),
    case sensitivity, whole word matching, and multiple output modes.
    """
    try:
        client = await ensure_api_client()
        
        # Resolve identifier to source_id
        sources = await client.list_data_sources()
        source_id = None
        
        for source in sources:
            if (source.get("id") == source_identifier or
                source.get("url") == source_identifier or
                source.get("display_name") == source_identifier):
                source_id = source.get("id")
                break
        
        if not source_id:
            source_id = source_identifier
        
        # Search with all parameters
        result = await client.post_doc_grep(
            source_id=source_id,
            pattern=pattern,
            path=path,
            context_lines=context_lines,
            A=A,
            B=B,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            fixed_string=fixed_string,
            max_matches_per_file=max_matches_per_file,
            max_total_matches=max_total_matches,
            output_mode=output_mode,
            highlight=highlight
        )
        
        if not result.get("success"):
            return [TextContent(
                type="text",
                text=f"❌ Failed to search: {result.get('message', 'Unknown error')}"
            )]
        
        # Format response
        total_matches = result.get("total_matches", 0)
        files_searched = result.get("files_searched", 0)
        files_with_matches_count = result.get("files_with_matches", 0)
        truncated = result.get("truncated", False)
        options = result.get("options", {})
        
        response = f"# Search Results: '{pattern}'\n\n"
        response += f"**Pattern:** `{pattern}`\n"
        response += f"**Path Filter:** {path}\n"
        response += f"**Total Matches:** {total_matches}\n"
        response += f"**Files with Matches:** {files_with_matches_count} of {files_searched} searched\n"
        
        if options.get("case_sensitive"):
            response += "**Case Sensitive:** Yes\n"
        if options.get("whole_word"):
            response += "**Whole Word:** Yes\n"
        if truncated:
            response += "**Note:** Results were truncated due to limits\n"
        
        response += "\n"
        
        if output_mode == "content":
            matches = result.get("matches", [])
            if not matches:
                response += "No matches found.\n"
            else:
                # Matches are now grouped by file from the API
                for file_group in matches:
                    file_path = file_group.get("path", "")
                    file_url = file_group.get("url", "")
                    file_matches = file_group.get("matches", [])
                    
                    response += f"## {file_path}\n\n"
                    response += f"**URL:** {file_url}\n"
                    response += f"**Matches in file:** {len(file_matches)}\n\n"
                
                    for match in file_matches:
                        line_num = match.get("line_number", "?")
                        line = match.get("line", "")
                        response += f"**Line {line_num}:**\n```\n{line}\n```\n\n"
        
        elif output_mode == "files_with_matches":
            files = result.get("files", [])
            if not files:
                response += "No files matched.\n"
            else:
                response += "**Matching Files:**\n"
                for f in files:
                    response += f"- {f}\n"
        
        elif output_mode == "count":
            counts = result.get("counts", {})
            if not counts:
                response += "No matches found.\n"
            else:
                response += "**Match Counts by File:**\n"
                for path_key, count in list(counts.items()):
                    response += f"- {path_key}: {count}\n"
        
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API Error searching documentation: {e}")
        return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


@mcp.tool()
async def code_grep(
    repository: Annotated[str, Field(description="Repository (owner/repo format)")],
    pattern: Annotated[str, Field(description="Regex pattern to search for")],
    path: Annotated[str, Field(description="Limit search to this file path prefix")] = "",
    context_lines: Annotated[Optional[int], Field(description="Lines before AND after (shorthand for A/B)")] = None,
    A: Annotated[Optional[int], Field(description="Lines after each match (like grep -A)")] = None,
    B: Annotated[Optional[int], Field(description="Lines before each match (like grep -B)")] = None,
    case_sensitive: Annotated[bool, Field(description="Case-sensitive matching (default: insensitive)")] = False,
    whole_word: Annotated[bool, Field(description="Match whole words only")] = False,
    fixed_string: Annotated[bool, Field(description="Treat pattern as literal string, not regex")] = False,
    max_matches_per_file: Annotated[int, Field(description="Max matches per file")] = 10,
    max_total_matches: Annotated[int, Field(description="Max total matches")] = 100,
    output_mode: Annotated[Literal["content", "files_with_matches", "count"], Field(description="Output format")] = "content",
    highlight: Annotated[bool, Field(description="Add >>markers<< around matched text")] = False,
    exhaustive: Annotated[bool, Field(description="Search ALL chunks for complete results (default: True). Set to False for faster but potentially incomplete BM25-based search.")] = True
) -> List[TextContent]:
    """
    Search repository code with a regex pattern.
    
    Like the Unix 'grep' command, but for indexed repository code.
    Searches through all code chunks and returns matches with context.
    
    Supports asymmetric context lines (A for after, B for before),
    case sensitivity, whole word matching, and multiple output modes.
    """
    try:
        client = await ensure_api_client()
        
        # Search with all parameters
        result = await client.post_code_grep(
            repository=repository,
            pattern=pattern,
            path=path,
            context_lines=context_lines,
            A=A,
            B=B,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            fixed_string=fixed_string,
            max_matches_per_file=max_matches_per_file,
            max_total_matches=max_total_matches,
            output_mode=output_mode,
            highlight=highlight,
            exhaustive=exhaustive
        )
        
        if not result.get("success"):
            return [TextContent(
                type="text",
                text=f"❌ Failed to search: {result.get('message', 'Unknown error')}"
            )]
        
        # Format response
        total_matches = result.get("total_matches", 0)
        files_searched = result.get("files_searched", 0)
        files_with_matches_count = result.get("files_with_matches", 0)
        truncated = result.get("truncated", False)
        options = result.get("options", {})
        
        response = f"# Code Search Results: '{pattern}'\n\n"
        response += f"**Repository:** {repository}\n"
        response += f"**Pattern:** `{pattern}`\n"
        response += f"**Path Filter:** {path or '/'}\n"
        response += f"**Total Matches:** {total_matches}\n"
        response += f"**Files with Matches:** {files_with_matches_count} of {files_searched} searched\n"
        
        if options.get("case_sensitive"):
            response += "**Case Sensitive:** Yes\n"
        if options.get("whole_word"):
            response += "**Whole Word:** Yes\n"
        if truncated:
            response += "**Note:** Results were truncated due to limits\n"
        
        response += "\n"
        
        if output_mode == "content":
            matches = result.get("matches", {})
            if not matches:
                response += "No matches found.\n"
            elif isinstance(matches, dict):
                # Grouped by file
                for file_path, file_matches in list(matches.items()):
                    response += f"## {file_path}\n\n"
                    response += f"**Matches in file:** {len(file_matches)}\n\n"
                    
                    for match in file_matches:
                        line_num = match.get("line_number", "?")
                        line = match.get("line", "")
                        response += f"**Line {line_num}:**\n```\n{line}\n```\n\n"
            else:
                # Flat list
                for match in matches:
                    file_path = match.get("path", "?")
                    line_num = match.get("line_number", "?")
                    line = match.get("line", "")
                    response += f"**{file_path}:{line_num}**\n```\n{line}\n```\n\n"
        
        elif output_mode == "files_with_matches":
            files = result.get("files", [])
            if not files:
                response += "No files matched.\n"
            else:
                response += "**Matching Files:**\n"
                for f in files:
                    response += f"- {f}\n"
        
        elif output_mode == "count":
            counts = result.get("counts", {})
            if not counts:
                response += "No matches found.\n"
            else:
                response += "**Match Counts by File:**\n"
                for path_key, count in list(counts.items()):
                    response += f"- {path_key}: {count}\n"
        
        return [TextContent(type="text", text=response)]
        
    except APIError as e:
        logger.error(f"API Error searching repository code: {e}")
        return [TextContent(type="text", text=f"❌ {str(e)}")]
    except Exception as e:
        logger.error(f"Error searching repository code: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


@mcp.tool()
async def nia_package_search_grep(
    registry: Annotated[
        Literal["crates_io", "golang_proxy", "npm", "py_pi", "ruby_gems"],
        Field(description="Package registry to search")
    ],
    package_name: Annotated[str, Field(description="Package name as it appears in the registry. For Go: org/repo format")],
    pattern: Annotated[str, Field(description="Regex pattern for text matching in the codebase")],
    version: Annotated[Optional[str], Field(description="Specific package version to search")] = None,
    language: Annotated[Optional[str], Field(description="Filter by programming language")] = None,
    filename_sha256: Annotated[Optional[str], Field(description="SHA256 hash of specific file to filter")] = None,
    a: Annotated[Optional[int], Field(description="Lines after each match to include")] = None,
    b: Annotated[Optional[int], Field(description="Lines before each match to include")] = None,
    c: Annotated[Optional[int], Field(description="Lines before and after each match to include")] = None,
    head_limit: Annotated[Optional[int], Field(description="Maximum number of results to return")] = None,
    output_mode: Annotated[
        Literal["content", "files_with_matches", "count"],
        Field(description="Output format: 'content' (snippets), 'files_with_matches' (file list), 'count' (match counts)")
    ] = "content"
) -> List[TextContent]:
    """
    Executes a grep over the source code of a public package. This tool is useful for deterministically
    finding code in a package using regex.

    Required Args: "registry", "package_name", "pattern" Optional Args: "version", "language",
    "filename_sha256", "a", "b", "c", "head_limit", "output_mode"

    Parameters:
        a: The number of lines after a grep match to include
        b: The number of lines before a grep match to include
        c: The number of lines before and after a grep match to include
        filename_sha256: The sha256 hash of the file to filter for
        head_limit: Limits number of results returned. If the number of results returned is less than the
            head limit, all results have been returned.
        language: The languages to filter for. If not provided, all languages will be searched.
        output_mode: Controls the shape of the grep output. Accepted values:
            "content" (default): return content snippets with line ranges
            "files_with_matches": return unique files (path and sha256) that match
            "count": return files with the count of matches per file
        package_name: The name of the requested package. Pass the name as it appears in the package
            manager. For Go packages, use the GitHub organization and repository name in the format
            {org}/{repo}
        pattern: The regex pattern for exact text matching in the codebase. Must be a valid regex.
            Example: "func\\s+\\(get_repository\\|getRepository\\)\\s*\\(.*?\\)\\s\\{"
        registry: The name of the registry containing the requested package. Must be one of:
            "crates_io", "golang_proxy", "npm", "py_pi", or "ruby_gems".
        version: Optional
    """
    try:
        # Use API client for backend routing
        client = await ensure_api_client()
        logger.info(f"Searching package {package_name} from {registry} with pattern: {pattern}")

        # Execute grep search through backend
        result = await client.package_search_grep(
            registry=registry,
            package_name=package_name,
            pattern=pattern,
            version=version,
            language=language,
            filename_sha256=filename_sha256,
            a=a,
            b=b,
            c=c,
            head_limit=head_limit,
            output_mode=output_mode
        )

        # Handle raw Chroma JSON response
        if not result or not isinstance(result, dict):
            return [TextContent(
                type="text",
                text=f"No response from Chroma for pattern '{pattern}' in {package_name} ({registry})"
            )]

        # Extract results and version from raw Chroma response
        results = result.get("results", [])
        version_used = result.get("version_used")

        if not results:
            return [TextContent(
                type="text",
                text=f"No matches found for pattern '{pattern}' in {package_name} ({registry})"
            )]

        response_lines = [
            f"# 🔍 Package Search Results: {package_name} ({registry})",
            f"**Pattern:** `{pattern}`",
            ""
        ]

        if version_used:
            response_lines.append(f"**Version:** {version_used}")
        elif version:
            response_lines.append(f"**Version:** {version}")

        response_lines.append(f"**Found {len(results)} matches**\n")

        # Handle grep result format: {output_mode: "content", result: {content, file_path, start_line, etc}}
        for i, item in enumerate(results, 1):
            response_lines.append(f"## Match {i}")

            # Extract data from Chroma grep format
            if "result" in item:
                result_data = item["result"]
                if result_data.get("file_path"):
                    response_lines.append(f"**File:** `{result_data['file_path']}`")

                # Show SHA256 for read_file tool usage
                if result_data.get("filename_sha256"):
                    response_lines.append(f"**SHA256:** `{result_data['filename_sha256']}`")

                if result_data.get("start_line") and result_data.get("end_line"):
                    response_lines.append(f"**Lines:** {result_data['start_line']}-{result_data['end_line']}")
                if result_data.get("language"):
                    response_lines.append(f"**Language:** {result_data['language']}")

                response_lines.append("```")
                response_lines.append(result_data.get("content", ""))
                response_lines.append("```\n")
            else:
                # Fallback for other formats
                response_lines.append("```")
                response_lines.append(str(item))
                response_lines.append("```\n")

        # Add truncation message if present
        if result.get("truncation_message"):
            response_lines.append(f"⚠️ **Note:** {result['truncation_message']}")

        # Add usage hint for read_file workflow (grep tool)
        response_lines.append("\n💡 **To read full file content:**")
        response_lines.append("Copy a SHA256 above and use: `nia_package_search_read_file(registry=..., package_name=..., filename_sha256=\"...\", start_line=1, end_line=100)`")

        return [TextContent(type="text", text="\n".join(response_lines))]

    except Exception as e:
        logger.error(f"Error in package search grep: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error searching package: {str(e)}\n\n"
                 f"Make sure:\n"
                 f"- The registry is one of: crates_io, golang_proxy, npm, py_pi\n"
                 f"- The package name is correct\n"
                 f"- The pattern is a valid regex"
        )]

@mcp.tool()
async def nia_package_search_hybrid(
    registry: Annotated[
        Literal["crates_io", "golang_proxy", "npm", "py_pi", "ruby_gems"],
        Field(description="Package registry to search")
    ],
    package_name: Annotated[str, Field(description="Package name as it appears in the registry. For Go: org/repo format")],
    semantic_queries: Annotated[
        List[str],
        Field(description="1-5 plain English questions about the codebase")
    ],
    version: Annotated[Optional[str], Field(description="Specific package version to search")] = None,
    filename_sha256: Annotated[Optional[str], Field(description="SHA256 hash of specific file to filter")] = None,
    pattern: Annotated[Optional[str], Field(description="Optional regex pattern for additional text matching")] = None,
    language: Annotated[Optional[str], Field(description="Filter by programming language")] = None
) -> List[TextContent]:
    """
    Searches package source code using semantic understanding AND optionally regex patterns.
    """
    try:
        # Use API client for backend routing
        client = await ensure_api_client()
        logger.info(f"Hybrid search in {package_name} from {registry} with queries: {semantic_queries}")

        # Execute hybrid search through backend
        result = await client.package_search_hybrid(
            registry=registry,
            package_name=package_name,
            semantic_queries=semantic_queries,
            version=version,
            filename_sha256=filename_sha256,
            pattern=pattern,
            language=language
        )

        # Handle raw Chroma JSON response
        if not result or not isinstance(result, dict):
            queries_str = "\n".join(f"- {q}" for q in semantic_queries)
            return [TextContent(
                type="text",
                text=f"No response from Chroma for queries:\n{queries_str}\n\nin {package_name} ({registry})"
            )]

        # Extract results and version from raw Chroma response
        results = result.get("results", [])
        version_used = result.get("version_used")

        if not results:
            queries_str = "\n".join(f"- {q}" for q in semantic_queries)
            return [TextContent(
                type="text",
                text=f"No relevant code found for queries:\n{queries_str}\n\nin {package_name} ({registry})"
            )]

        response_lines = [
            f"# 🔎 Package Semantic Search: {package_name} ({registry})",
            "**Queries:**"
        ]

        for query in semantic_queries:
            response_lines.append(f"- {query}")

        response_lines.append("")

        if version_used:
            response_lines.append(f"**Version:** {version_used}")
        elif version:
            response_lines.append(f"**Version:** {version}")
        if pattern:
            response_lines.append(f"**Pattern Filter:** `{pattern}`")

        response_lines.append(f"\n**Found {len(results)} relevant code sections**\n")

        # Handle hybrid result format: {id: "...", document: "content", metadata: {...}}
        for i, item in enumerate(results, 1):
            response_lines.append(f"## Result {i}")

            # Extract metadata if available
            metadata = item.get("metadata", {})
            if metadata.get("filename"):
                response_lines.append(f"**File:** `{metadata['filename']}`")

            # Show SHA256 for read_file tool usage (from metadata)
            if metadata.get("filename_sha256"):
                response_lines.append(f"**SHA256:** `{metadata['filename_sha256']}`")

            if metadata.get("start_line") and metadata.get("end_line"):
                response_lines.append(f"**Lines:** {metadata['start_line']}-{metadata['end_line']}")
            if metadata.get("language"):
                response_lines.append(f"**Language:** {metadata['language']}")

            # Get document content
            content = item.get("document", "")
            if content:
                response_lines.append("```")
                response_lines.append(content)
                response_lines.append("```\n")

        # Add truncation message if present
        if result.get("truncation_message"):
            response_lines.append(f"⚠️ **Note:** {result['truncation_message']}")

        # Add usage hint for read_file workflow (hybrid tool)
        response_lines.append("\n💡 **To read full file content:**")
        response_lines.append("Copy a SHA256 above and use: `nia_package_search_read_file(registry=..., package_name=..., filename_sha256=\"...\", start_line=1, end_line=100)`")

        return [TextContent(type="text", text="\n".join(response_lines))]

    except Exception as e:
        logger.error(f"Error in package search hybrid: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error in hybrid search: {str(e)}\n\n"
                 f"Make sure:\n"
                 f"- The registry is one of: crates_io, golang_proxy, npm, py_pi\n"
                 f"- The package name is correct\n"
                 f"- Semantic queries are provided (1-5 queries)"
        )]

@mcp.tool()
async def nia_package_search_read_file(
    registry: Annotated[
        Literal["crates_io", "golang_proxy", "npm", "py_pi", "ruby_gems"],
        Field(description="Package registry to search")
    ],
    package_name: Annotated[str, Field(description="Package name as it appears in the registry. For Go: org/repo format")],
    filename_sha256: Annotated[str, Field(description="SHA256 hash of the file to read")],
    start_line: Annotated[int, Field(description="1-based inclusive start line to read")],
    end_line: Annotated[int, Field(description="1-based inclusive end line to read (max 200 lines)")],
    version: Annotated[Optional[str], Field(description="Specific package version")] = None
) -> List[TextContent]:
    """
    Reads exact lines from a source file of a public package. Useful for fetching specific code regions by line range.
    """
    try:
        # Validate line range
        if end_line - start_line + 1 > 200:
            return [TextContent(
                type="text",
                text="❌ Error: Maximum 200 lines can be read at once. Please reduce the line range."
            )]

        if start_line < 1 or end_line < start_line:
            return [TextContent(
                type="text",
                text="❌ Error: Invalid line range. Start line must be >= 1 and end line must be >= start line."
            )]

        # Use API client for backend routing
        client = await ensure_api_client()
        logger.info(f"Reading file from {package_name} ({registry}): sha256={filename_sha256}, lines {start_line}-{end_line}")

        # Read file content through backend
        result = await client.package_search_read_file(
            registry=registry,
            package_name=package_name,
            filename_sha256=filename_sha256,
            start_line=start_line,
            end_line=end_line,
            version=version
        )

        # Handle raw Chroma response (read_file typically returns content directly)
        response_lines = [
            f"# 📄 Package File Content: {package_name} ({registry})",
            f"**File SHA256:** `{filename_sha256}`",
            f"**Lines:** {start_line}-{end_line}"
        ]

        if version:
            response_lines.append(f"**Version:** {version}")

        response_lines.append("\n```")
        # For read_file, Chroma typically returns the content directly as a string
        if isinstance(result, str):
            response_lines.append(result)
        elif isinstance(result, dict) and result.get("content"):
            response_lines.append(result["content"])
        else:
            response_lines.append(str(result))
        response_lines.append("```")

        return [TextContent(type="text", text="\n".join(response_lines))]

    except Exception as e:
        logger.error(f"Error reading package file: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error reading file: {str(e)}\n\n"
                 f"Make sure:\n"
                 f"- The registry is one of: crates_io, golang_proxy, npm, py_pi\n"
                 f"- The package name is correct\n"
                 f"- The filename_sha256 is valid\n"
                 f"- The line range is valid (1-based, max 200 lines)"
        )]

@mcp.tool()
async def nia_bug_report(
    description: Annotated[str, Field(description="Detailed description of the bug or feature request (10-5000 chars)")],
    bug_type: Annotated[
        Literal["bug", "feature-request", "improvement", "other"],
        Field(description="Type of report")
    ] = "bug",
    additional_context: Annotated[
        Optional[str],
        Field(description="Additional context, steps to reproduce, or related information")
    ] = None
) -> List[TextContent]:
    """
    Submit a bug report or feature request.
    """
    try:
        client = await ensure_api_client()

        # Validate input parameters
        if not description or len(description.strip()) < 10:
            return [
                TextContent(
                    type="text",
                    text="❌ Error: Bug description must be at least 10 characters long."
                )
            ]

        if len(description) > 5000:
            return [
                TextContent(
                    type="text",
                    text="❌ Error: Bug description must be 5000 characters or less."
                )
            ]

        if additional_context and len(additional_context) > 2000:
            return [
                TextContent(
                    type="text",
                    text="❌ Error: Additional context must be 2000 characters or less."
                )
            ]

        logger.info(f"Submitting bug report: type={bug_type}, description_length={len(description)}")

        # Submit bug report via API client
        result = await client.submit_bug_report(
            description=description.strip(),
            bug_type=bug_type,
            additional_context=additional_context.strip() if additional_context else None
        )

        if result.get("success"):
            return [
                TextContent(
                    type="text",
                    text=f"✅ Bug report submitted successfully!\n\n"
                         f"Thank you for your feedback. Your report has been sent to the development team "
                         f"and will be reviewed promptly.\n\n"
                         f"Reference ID: {result.get('message', '').split(': ')[-1] if ': ' in result.get('message', '') else 'N/A'}\n"
                         f"Type: {bug_type.title()}\n"
                         f"Status: The team will be notified immediately via email and Slack.\n\n"
                         f"You can also track issues and feature requests on our GitHub repository:\n"
                         f"https://github.com/nozomio-labs/nia/issues"
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Failed to submit bug report: {result.get('message', 'Unknown error')}\n\n"
                         f"Please try again or contact support directly at support@trynia.ai"
                )
            ]

    except Exception as e:
        logger.error(f"Error submitting bug report: {e}")
        return [
            TextContent(
                type="text",
                text=f"❌ Error submitting bug report: {str(e)}\n\n"
                     f"Please try again or contact support directly at support@trynia.ai"
            )
        ]

# Context Sharing Tools

@mcp.tool()
async def context(
    action: Annotated[
        Literal["save", "list", "retrieve", "search", "semantic-search", "keyword-search", "update", "delete"],
        Field(description="Action to perform on contexts")
    ],
    # For save action
    title: Annotated[Optional[str], Field(description="Descriptive title for the context (save/update)")] = None,
    summary: Annotated[Optional[str], Field(description="Brief summary, 10-1000 chars (save/update)")] = None,
    content: Annotated[Optional[str], Field(description="Full conversation context, min 50 chars (save/update)")] = None,
    agent_source: Annotated[Optional[str], Field(description="Agent creating this context, e.g. 'cursor', 'claude-code' (save)")] = None,
    tags: Annotated[Optional[List[str]], Field(description="Searchable tags (save/update)")] = None,
    metadata: Annotated[Optional[dict], Field(description="Additional metadata like file paths, repos discussed (save/update)")] = None,
    nia_references: Annotated[Optional[dict], Field(description="Structured data about NIA resources used (save)")] = None,
    edited_files: Annotated[Optional[List[dict]], Field(description="Files modified during conversation (save)")] = None,
    # New workspace-aware parameters
    workspace_override: Annotated[Optional[str], Field(description="Custom workspace name, overrides auto-detection (save)")] = None,
    # For list/search actions
    limit: Annotated[int, Field(description="Number of results to return, 1-100 (list/search)")] = 20,
    offset: Annotated[int, Field(description="Number of contexts to skip for pagination (list)")] = 0,
    scope: Annotated[
        Literal["auto", "all", "workspace", "directory"] | None,
        Field(description="Filter scope: 'auto' (smart), 'all', 'workspace', 'directory' (list)")
    ] = None,
    workspace: Annotated[Optional[str], Field(description="Filter by workspace/project name (list)")] = None,
    directory: Annotated[Optional[str], Field(description="Filter by directory path (list)")] = None,
    file_overlap: Annotated[Optional[List[str]], Field(description="Find contexts with overlapping files (list)")] = None,
    # For retrieve/update/delete actions
    context_id: Annotated[Optional[str], Field(description="Unique context ID (retrieve/update/delete)")] = None,
    # For search action
    query: Annotated[Optional[str], Field(description="Search query for title, summary, content, tags (search)")] = None
) -> List[TextContent]:
    """
    Unified context management tool for saving, listing, retrieving, searching, updating, and deleting conversation contexts.
    """
    try:
        client = await ensure_api_client()

        # ===== SAVE ACTION =====
        if action == "save":
            # Validate required parameters
            if not title or not title.strip():
                return [TextContent(type="text", text="❌ Error: title is required for save action")]
            if not summary:
                return [TextContent(type="text", text="❌ Error: summary is required for save action")]
            if not content:
                return [TextContent(type="text", text="❌ Error: content is required for save action")]
            if not agent_source or not agent_source.strip():
                return [TextContent(type="text", text="❌ Error: agent_source is required for save action")]

            # Validate field lengths
            if len(title) > 200:
                return [TextContent(type="text", text="❌ Error: Title must be 200 characters or less")]
            if len(summary) < 10 or len(summary) > 1000:
                return [TextContent(type="text", text="❌ Error: Summary must be 10-1000 characters")]
            if len(content) < 50:
                return [TextContent(type="text", text="❌ Error: Content must be at least 50 characters")]

            logger.info(f"Saving context: title='{title}', agent={agent_source}, content_length={len(content)}")

            # Auto-detect current working directory
            cwd = os.getcwd()

            result = await client.save_context(
                title=title.strip(),
                summary=summary.strip(),
                content=content,
                agent_source=agent_source.strip(),
                tags=tags or [],
                metadata=metadata or {},
                nia_references=nia_references,
                edited_files=edited_files or [],
                workspace_override=workspace_override,
                cwd=cwd
            )

            context_id_result = result.get("id")
            context_org = result.get("organization_id")

            org_line = f"👥 **Organization:** {context_org}\n" if context_org else ""

            return [TextContent(
                type="text",
                text=f"✅ **Context Saved Successfully!**\n\n"
                     f"🆔 **Context ID:** `{context_id_result}`\n"
                     f"📝 **Title:** {title}\n"
                     f"🤖 **Source Agent:** {agent_source}\n"
                     f"{org_line}"
                     f"📊 **Content Length:** {len(content):,} characters\n"
                     f"🏷️ **Tags:** {', '.join(tags) if tags else 'None'}\n\n"
                     f"**Next Steps:**\n"
                     f"• Other agents can now retrieve this context using the context ID\n"
                     f"• Use `context(action='search', query='...')` to find contexts\n"
                     f"• Use `context(action='list')` to see all your saved contexts\n\n"
                     f"🔗 **Share this context:** Provide the context ID `{context_id_result}` to other agents"
            )]

        # ===== LIST ACTION =====
        elif action == "list":
            # Validate parameters
            if limit < 1 or limit > 100:
                return [TextContent(type="text", text="❌ Error: Limit must be between 1 and 100")]
            if offset < 0:
                return [TextContent(type="text", text="❌ Error: Offset must be 0 or greater")]

            # Convert tags list to comma-separated string if provided
            tags_filter = ','.join(tags) if tags and isinstance(tags, list) else (tags if isinstance(tags, str) else None)

            # Convert file_overlap list to comma-separated string if provided
            file_overlap_str = ','.join(file_overlap) if file_overlap and isinstance(file_overlap, list) else None

            # Auto-detect current working directory if scope is "auto"
            cwd = os.getcwd() if scope == "auto" else None

            result = await client.list_contexts(
                limit=limit,
                offset=offset,
                tags=tags_filter,
                agent_source=agent_source,
                scope=scope,
                workspace=workspace,
                directory=directory,
                file_overlap=file_overlap_str,
                cwd=cwd
            )

            contexts = result.get("contexts", [])
            pagination = result.get("pagination", {})

            if not contexts:
                response = "📭 **No Contexts Found**\n\n"
                if tags or agent_source:
                    response += "No contexts match your filters.\n\n"
                else:
                    response += "You haven't saved any contexts yet.\n\n"

                response += "**Get started:**\n"
                response += "• Use `context(action='save', ...)` to save a conversation for cross-agent sharing\n"
                response += "• Perfect for handoffs between Cursor and Claude Code!"

                return [TextContent(type="text", text=response)]

            # Format the response
            response = f"📚 **Your Conversation Contexts** ({pagination.get('total', len(contexts))} total)\n\n"

            for i, ctx in enumerate(contexts, offset + 1):
                created_at = ctx.get('created_at', '')
                if created_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = 'Unknown'

                response += f"**{i}. {ctx['title']}**\n"
                response += f"   🆔 ID: `{ctx['id']}`\n"
                response += f"   🤖 Source: {ctx['agent_source']}\n"
                if ctx.get('organization_id'):
                    response += f"   👥 Organization: {ctx['organization_id']}\n"
                response += f"   📅 Created: {formatted_date}\n"
                response += f"   📝 Summary: {ctx['summary'][:100]}{'...' if len(ctx['summary']) > 100 else ''}\n"
                if ctx.get('tags'):
                    response += f"   🏷️ Tags: {', '.join(ctx['tags'])}\n"
                response += "\n"

            # Add pagination info
            if pagination.get('has_more'):
                next_offset = offset + limit
                response += f"📄 **Pagination:** Showing {offset + 1}-{offset + len(contexts)} of {pagination.get('total')}\n"
                response += f"   Use `context(action='list', offset={next_offset})` for next page\n"

            response += "\n**Actions:**\n"
            response += "• `context(action='retrieve', context_id='...')` - Get full context\n"
            response += "• `context(action='search', query='...')` - Search contexts\n"
            response += "• `context(action='delete', context_id='...')` - Remove context"

            return [TextContent(type="text", text=response)]

        # ===== RETRIEVE ACTION =====
        elif action == "retrieve":
            if not context_id or not context_id.strip():
                return [TextContent(type="text", text="❌ Error: context_id is required for retrieve action")]

            ctx = await client.get_context(context_id.strip())

            if not ctx:
                return [TextContent(
                    type="text",
                    text=f"❌ **Context Not Found**\n\n"
                         f"Context ID `{context_id}` was not found.\n\n"
                         f"**Possible reasons:**\n"
                         f"• The context ID is incorrect\n"
                         f"• The context belongs to a different user or organization\n"
                         f"• The context has been deleted\n\n"
                         f"Use `context(action='list')` to see your available contexts."
                )]

            # Format the context display
            created_at = ctx.get('created_at', '')
            if created_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                except:
                    formatted_date = created_at
            else:
                formatted_date = 'Unknown'

            updated_at = ctx.get('updated_at', '')
            formatted_updated = None
            if updated_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    formatted_updated = dt.strftime('%Y-%m-%d %H:%M UTC')
                except:
                    formatted_updated = updated_at

            response = f"📋 **Context: {ctx['title']}**\n\n"
            response += f"🆔 **ID:** `{ctx['id']}`\n"
            response += f"🤖 **Source Agent:** {ctx['agent_source']}\n"
            if ctx.get('organization_id'):
                response += f"👥 **Organization:** {ctx['organization_id']}\n"
            response += f"📅 **Created:** {formatted_date}\n"
            if formatted_updated:
                response += f"🔄 **Updated:** {formatted_updated}\n"

            if ctx.get('tags'):
                response += f"🏷️ **Tags:** {', '.join(ctx['tags'])}\n"

            response += f"\n📝 **Summary:**\n{ctx['summary']}\n\n"

            # Add NIA References
            nia_refs = ctx.get('nia_references') or {}
            if nia_refs:
                response += "🧠 **NIA RESOURCES USED - RECOMMENDED ACTIONS:**\n"

                indexed_resources = nia_refs.get('indexed_resources', [])
                if indexed_resources:
                    response += "**📦 Re-index these resources:**\n"
                    for resource in indexed_resources:
                        identifier = resource.get('identifier', 'Unknown')
                        resource_type = resource.get('resource_type', 'unknown')
                        purpose = resource.get('purpose', 'No purpose specified')

                        if resource_type == 'repository':
                            response += f"• `Index {identifier}` - {purpose}\n"
                        elif resource_type == 'documentation':
                            response += f"• `Index documentation {identifier}` - {purpose}\n"
                        else:
                            response += f"• `Index {identifier}` ({resource_type}) - {purpose}\n"
                    response += "\n"

                search_queries = nia_refs.get('search_queries', [])
                if search_queries:
                    response += "**🔍 Useful search queries to re-run:**\n"
                    for q in search_queries:
                        query_text = q.get('query', 'Unknown query')
                        query_type = q.get('query_type', 'search')
                        key_findings = q.get('key_findings', 'No findings specified')
                        resources_searched = q.get('resources_searched', [])

                        response += f"• **Query:** `{query_text}` ({query_type})\n"
                        if resources_searched:
                            response += f"  **Resources:** {', '.join(resources_searched)}\n"
                        response += f"  **Key Findings:** {key_findings}\n"
                    response += "\n"

                session_summary = nia_refs.get('session_summary')
                if session_summary:
                    response += f"**📋 NIA Session Summary:** {session_summary}\n\n"

            # Add Edited Files
            edited_files_list = ctx.get('edited_files') or []
            if edited_files_list:
                response += "📝 **FILES MODIFIED - READ THESE TO GET UP TO SPEED:**\n"
                for file_info in edited_files_list:
                    file_path = file_info.get('file_path', 'Unknown file')
                    operation = file_info.get('operation', 'modified')
                    changes_desc = file_info.get('changes_description', 'No description')
                    key_changes = file_info.get('key_changes', [])
                    language = file_info.get('language', '')

                    operation_emoji = {
                        'created': '🆕',
                        'modified': '✏️',
                        'deleted': '🗑️'
                    }.get(operation, '📄')

                    response += f"• {operation_emoji} **`{file_path}`** ({operation})\n"
                    response += f"  **Changes:** {changes_desc}\n"

                    if key_changes:
                        response += f"  **Key Changes:** {', '.join(key_changes)}\n"
                    if language:
                        response += f"  **Language:** {language}\n"

                    response += f"  **💡 Action:** Read this file with: `Read {file_path}`\n"
                response += "\n"

            # Add metadata if available
            metadata_dict = ctx.get('metadata') or {}
            if metadata_dict:
                response += f"📊 **Additional Metadata:**\n"
                for key, value in metadata_dict.items():
                    if isinstance(value, list):
                        response += f"• **{key}:** {', '.join(map(str, value))}\n"
                    else:
                        response += f"• **{key}:** {value}\n"
                response += "\n"

            response += f"📄 **Full Context:**\n\n{ctx['content']}\n\n"

            response += f"---\n"
            response += f"🚀 **NEXT STEPS FOR SEAMLESS HANDOFF:**\n"
            response += f"• This context was created by **{ctx['agent_source']}**\n"

            if nia_refs.get('search_queries'):
                response += f"• **RECOMMENDED:** Re-run the search queries to get the same insights\n"
            if edited_files_list:
                response += f"• **ESSENTIAL:** Read the modified files above to understand code changes\n"

            response += f"• Use the summary and full context to understand the strategic planning\n"

            return [TextContent(type="text", text=response)]

        # ===== SEARCH ACTION =====
        elif action == "search":
            # DEFAULT: Use semantic search for better results
            # For legacy keyword search, use action="keyword-search"
            if not query or not query.strip():
                return [TextContent(type="text", text="❌ Error: query is required for search action")]

            if limit < 1 or limit > 100:
                return [TextContent(type="text", text="❌ Error: Limit must be between 1 and 100")]

            try:
                result = await client.search_contexts_semantic(
                    query=query.strip(),
                    limit=limit,
                    cwd=workspace_override if workspace_override else None,
                    include_highlights=True,
                    workspace_filter=workspace if workspace else None
                )
            except Exception as e:
                return [TextContent(type="text", text=f"❌ Error performing semantic search: {str(e)}")]

            # Extract results from semantic search response
            contexts = result.get("results", [])

            if not contexts:
                response = f"🔍 **No Results Found**\n\n"
                response += f"No contexts match your search query: \"{query}\"\n\n"

                if tags or agent_source:
                    response += f"**Active filters:**\n"
                    if tags:
                        response += f"• Tags: {tags if isinstance(tags, str) else ', '.join(tags)}\n"
                    if agent_source:
                        response += f"• Agent: {agent_source}\n"
                    response += "\n"

                response += f"**Suggestions:**\n"
                response += f"• Try different keywords\n"
                response += f"• Remove filters to broaden search\n"
                response += f"• Use `context(action='list')` to see all contexts"

                return [TextContent(type="text", text=response)]

            # Format semantic search results
            response = f"🔍 **Semantic Search Results for \"{query}\"** ({len(contexts)} found)\n\n"

            for i, ctx in enumerate(contexts, 1):
                created_at = ctx.get('created_at', '')
                if created_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = 'Unknown'

                # Show relevance score if available
                relevance_score = ctx.get('relevance_score', 0.0)
                response += f"**{i}. {ctx['title']}** (Score: {relevance_score:.2f})\n"
                response += f"   🆔 ID: `{ctx['id']}`\n"
                response += f"   🤖 Source: {ctx['agent_source']}\n"
                response += f"   📅 Created: {formatted_date}\n"
                response += f"   📝 Summary: {ctx['summary'][:150]}{'...' if len(ctx['summary']) > 150 else ''}\n"

                if ctx.get('tags'):
                    response += f"   🏷️ Tags: {', '.join(ctx['tags'])}\n"

                # Show match highlights if available
                if ctx.get('match_highlights'):
                    highlights = ctx['match_highlights'][:2]  # Show first 2
                    if highlights:
                        response += f"   ✨ Highlights:\n"
                        for highlight in highlights:
                            response += f"      • {highlight[:100]}...\n"

                response += "\n"

            response += f"**Actions:**\n"
            response += f"• `context(action='retrieve', context_id='...')` - Get full context\n"
            response += f"• Results ranked by semantic relevance\n"
            response += f"• Use `action='keyword-search'` for exact keyword matching"

            return [TextContent(type="text", text=response)]

        # ===== SEMANTIC SEARCH ACTION =====
        elif action == "semantic-search":
            if not query or not query.strip():
                return [TextContent(type="text", text="❌ Error: query is required for semantic-search action")]

            if limit < 1 or limit > 100:
                return [TextContent(type="text", text="❌ Error: Limit must be between 1 and 100")]

            try:
                result = await client.search_contexts_semantic(
                    query=query.strip(),
                    limit=limit,
                    cwd=cwd,
                    workspace_override=workspace_override,
                    include_highlights=True,
                    workspace_filter=workspace if workspace else None
                )

                results = result.get("results", [])
                search_metadata = result.get("search_metadata", {})
                suggestions = result.get("suggestions", {})

                if not results:
                    response = f"🔍 **No Semantic Search Results Found**\n\n"
                    response += f"No contexts semantically match: \"{query}\"\n\n"

                    if suggestions:
                        response += f"**💡 Suggestions:**\n"
                        if suggestions.get("message"):
                            response += f"• {suggestions['message']}\n"
                        if suggestions.get("tips"):
                            for tip in suggestions["tips"]:
                                response += f"• {tip}\n"

                    return [TextContent(type="text", text=response)]

                # Format semantic search results with rich output
                response = f"🔍 **Semantic Search Results for \"{query}\"**\n\n"

                # Add search metadata
                response += f"**📊 Search Info:**\n"
                response += f"• Type: {search_metadata.get('search_type', 'semantic')}\n"
                response += f"• Results: {search_metadata.get('total_results', len(results))}\n"
                if search_metadata.get('current_workspace'):
                    response += f"• Current Workspace: {search_metadata['current_workspace']}\n"
                    response += f"• Workspace Matches: {search_metadata.get('workspace_matches', 0)}\n"
                response += "\n"

                # Display results
                for i, ctx in enumerate(results, 1):
                    relevance_score = ctx.get('relevance_score', 0)
                    response += f"**{i}. {ctx['title']}** (Score: {relevance_score:.2f})\n"
                    response += f"   🆔 ID: `{ctx['id']}`\n"
                    response += f"   🤖 Source: {ctx.get('agent_source', 'unknown')}\n"

                    # Show match highlights
                    if ctx.get('match_highlights'):
                        response += f"   ✨ Highlights:\n"
                        for highlight in ctx['match_highlights'][:2]:  # Show top 2 highlights
                            response += f"      • {highlight}\n"

                    # Show files edited
                    if ctx.get('files_edited'):
                        files_str = ', '.join(ctx['files_edited'][:3])
                        response += f"   📄 Files: {files_str}\n"

                    # Show tags
                    if ctx.get('tags'):
                        response += f"   🏷️ Tags: {', '.join(ctx['tags'][:5])}\n"

                    # Show workspace
                    if ctx.get('workspace_name'):
                        response += f"   💼 Workspace: {ctx['workspace_name']}\n"

                    response += "\n"

                # Add suggestions if available
                if suggestions:
                    response += f"**💡 Suggestions:**\n"
                    if suggestions.get('related_tags'):
                        response += f"• Related tags: {', '.join(suggestions['related_tags'][:5])}\n"
                    if suggestions.get('workspaces_found') and len(suggestions['workspaces_found']) > 1:
                        response += f"• Workspaces found: {', '.join(suggestions['workspaces_found'])}\n"
                    if suggestions.get('file_types'):
                        response += f"• File types: {', '.join(suggestions['file_types'][:5])}\n"
                    if suggestions.get('tip'):
                        response += f"• Tip: {suggestions['tip']}\n"
                    response += "\n"

                response += f"**Actions:**\n"
                response += f"• `context(action='retrieve', context_id='...')` - Get full context\n"
                response += f"• Try filtering by workspace for more relevant results\n"

                return [TextContent(type="text", text=response)]

            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
                return [TextContent(type="text", text=f"❌ Error performing semantic search: {str(e)}")]

        # ===== KEYWORD SEARCH ACTION (Legacy) =====
        elif action == "keyword-search":
            if not query or not query.strip():
                return [TextContent(type="text", text="❌ Error: query is required for keyword-search action")]

            if limit < 1 or limit > 100:
                return [TextContent(type="text", text="❌ Error: Limit must be between 1 and 100")]

            # Convert tags list to comma-separated string if provided
            tags_filter = ','.join(tags) if tags and isinstance(tags, list) else (tags if isinstance(tags, str) else None)

            result = await client.search_contexts(
                query=query.strip(),
                limit=limit,
                tags=tags_filter,
                agent_source=agent_source
            )

            contexts = result.get("contexts", [])

            if not contexts:
                response = f"🔍 **No Results Found**\n\n"
                response += f"No contexts match your keyword search: \"{query}\"\n\n"

                if tags or agent_source:
                    response += f"**Active filters:**\n"
                    if tags:
                        response += f"• Tags: {tags if isinstance(tags, str) else ', '.join(tags)}\n"
                    if agent_source:
                        response += f"• Agent: {agent_source}\n"
                    response += "\n"

                response += f"**Suggestions:**\n"
                response += f"• Try semantic search with `action='search'` for meaning-based results\n"
                response += f"• Use different keywords\n"
                response += f"• Remove filters to broaden search"

                return [TextContent(type="text", text=response)]

            # Format keyword search results
            response = f"🔍 **Keyword Search Results for \"{query}\"** ({len(contexts)} found)\n\n"

            for i, ctx in enumerate(contexts, 1):
                created_at = ctx.get('created_at', '')
                if created_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = 'Unknown'

                response += f"**{i}. {ctx['title']}**\n"
                response += f"   🆔 ID: `{ctx['id']}`\n"
                response += f"   🤖 Source: {ctx['agent_source']}\n"
                response += f"   📅 Created: {formatted_date}\n"
                response += f"   📝 Summary: {ctx['summary'][:150]}{'...' if len(ctx['summary']) > 150 else ''}\n"

                if ctx.get('tags'):
                    response += f"   🏷️ Tags: {', '.join(ctx['tags'])}\n"

                response += "\n"

            response += f"**Actions:**\n"
            response += f"• `context(action='retrieve', context_id='...')` - Get full context\n"
            response += f"• Try semantic search with `action='search'` for better results"

            return [TextContent(type="text", text=response)]

        # ===== UPDATE ACTION =====
        elif action == "update":
            if not context_id or not context_id.strip():
                return [TextContent(type="text", text="❌ Error: context_id is required for update action")]

            # Check that at least one field is being updated
            if not any([title, summary, content, tags is not None, metadata is not None]):
                return [TextContent(
                    type="text",
                    text="❌ Error: At least one field must be provided for update (title, summary, content, tags, or metadata)"
                )]

            # Validate fields if provided
            if title is not None and (not title.strip() or len(title) > 200):
                return [TextContent(type="text", text="❌ Error: Title must be 1-200 characters")]

            if summary is not None and (len(summary) < 10 or len(summary) > 1000):
                return [TextContent(type="text", text="❌ Error: Summary must be 10-1000 characters")]

            if content is not None and len(content) < 50:
                return [TextContent(type="text", text="❌ Error: Content must be at least 50 characters")]

            if tags is not None and len(tags) > 10:
                return [TextContent(type="text", text="❌ Error: Maximum 10 tags allowed")]

            result = await client.update_context(
                context_id=context_id.strip(),
                title=title.strip() if title else None,
                summary=summary.strip() if summary else None,
                content=content,
                tags=tags,
                metadata=metadata
            )

            if not result:
                return [TextContent(
                    type="text",
                    text=f"❌ Error: Context with ID `{context_id}` not found"
                )]

            # List updated fields
            updated_fields = []
            if title is not None:
                updated_fields.append("title")
            if summary is not None:
                updated_fields.append("summary")
            if content is not None:
                updated_fields.append("content")
            if tags is not None:
                updated_fields.append("tags")
            if metadata is not None:
                updated_fields.append("metadata")

            response = f"✅ **Context Updated Successfully!**\n\n"
            response += f"🆔 **Context ID:** `{context_id}`\n"
            response += f"📝 **Title:** {result['title']}\n"
            response += f"🔄 **Updated Fields:** {', '.join(updated_fields)}\n"
            response += f"🤖 **Source Agent:** {result['agent_source']}\n\n"

            response += f"**Current Status:**\n"
            response += f"• **Tags:** {', '.join(result['tags']) if result.get('tags') else 'None'}\n"
            response += f"• **Content Length:** {len(result['content']):,} characters\n\n"

            response += f"Use `context(action='retrieve', context_id='{context_id}')` to see the full updated context."

            return [TextContent(type="text", text=response)]

        # ===== DELETE ACTION =====
        elif action == "delete":
            if not context_id or not context_id.strip():
                return [TextContent(type="text", text="❌ Error: context_id is required for delete action")]

            success = await client.delete_context(context_id.strip())

            if success:
                return [TextContent(
                    type="text",
                    text=f"✅ **Context Deleted Successfully!**\n\n"
                         f"🆔 **Context ID:** `{context_id}`\n\n"
                         f"The context has been permanently removed from your account.\n"
                         f"This action cannot be undone.\n\n"
                         f"Use `context(action='list')` to see your remaining contexts."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ **Context Not Found**\n\n"
                         f"Context ID `{context_id}` was not found or has already been deleted.\n\n"
                         f"Use `context(action='list')` to see your available contexts."
                )]

    except APIError as e:
        logger.error(f"API Error in context ({action}): {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error in context ({action}): {e}")
        return [TextContent(type="text", text=f"❌ Error in {action} operation: {str(e)}")]

# DEPRECATED: Individual context tools below - use context() with action parameter instead

# @mcp.tool()
# async def save_context(
#     title: str,
#     summary: str,
#     content: str,
#     agent_source: str,
#     tags: Optional[List[str]] = None,
#     metadata: Optional[dict] = None,
#     nia_references: Optional[dict] = None,
#     edited_files: Optional[List[dict]] = None
# ) -> List[TextContent]:
    """
    Save a conversation context for cross-agent sharing.

    Args:
        title: A descriptive title for the context
        summary: Brief summary of the conversation
        content: Full conversation context - the agent should compact the conversation history but keep all important parts togethers, as well as code snippets. No excuses.
        agent_source: Which agent is creating this context (e.g., "cursor")
        tags: Optional list of searchable tags
        metadata: Optional metadata like file paths, repositories discussed, etc.
        nia_references: Structured data about NIA resources used during conversation
            Format: {
                "indexed_resources": [{"identifier": "owner/repo", "resource_type": "repository", "purpose": "Used for authentication patterns"}],
                "search_queries": [{"query": "JWT implementation", "query_type": "codebase", "resources_searched": ["owner/repo"], "key_findings": "Found JWT utils in auth folder"}],
                "session_summary": "Used NIA to explore authentication patterns and API design"
            }
        edited_files: List of files that were modified during conversation
            Format: [{"file_path": "src/auth.ts", "operation": "modified", "changes_description": "Added JWT validation", "key_changes": ["Added validate() function"]}]

    Returns:
        Confirmation of successful context save with context ID
    """
    try:
        # Validate input parameters
        if not title or not title.strip():
            return [TextContent(type="text", text="❌ Error: Title is required")]

        if len(title) > 200:
            return [TextContent(type="text", text="❌ Error: Title must be 200 characters or less")]

        if not summary or len(summary) < 10:
            return [TextContent(type="text", text="❌ Error: Summary must be at least 10 characters")]

        if len(summary) > 1000:
            return [TextContent(type="text", text="❌ Error: Summary must be 1000 characters or less")]

        if not content or len(content) < 50:
            return [TextContent(type="text", text="❌ Error: Content must be at least 50 characters")]

        if not agent_source or not agent_source.strip():
            return [TextContent(type="text", text="❌ Error: Agent source is required")]

        client = await ensure_api_client()

        logger.info(f"Saving context: title='{title}', agent={agent_source}, content_length={len(content)}")

        result = await client.save_context(
            title=title.strip(),
            summary=summary.strip(),
            content=content,
            agent_source=agent_source.strip(),
            tags=tags or [],
            metadata=metadata or {},
            nia_references=nia_references,
            edited_files=edited_files or []
        )

        context_id = result.get("id")

        return [TextContent(
            type="text",
            text=f"✅ **Context Saved Successfully!**\n\n"
                 f"🆔 **Context ID:** `{context_id}`\n"
                 f"📝 **Title:** {title}\n"
                 f"🤖 **Source Agent:** {agent_source}\n"
                 f"📊 **Content Length:** {len(content):,} characters\n"
                 f"🏷️ **Tags:** {', '.join(tags) if tags else 'None'}\n\n"
                 f"**Next Steps:**\n"
                 f"• Other agents can now retrieve this context using the context ID\n"
                 f"• Use `search_contexts` to find contexts by content or tags\n"
                 f"• Use `list_contexts` to see all your saved contexts\n\n"
                 f"🔗 **Share this context:** Provide the context ID `{context_id}` to other agents"
        )]

    except APIError as e:
        logger.error(f"API Error saving context: {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error saving context: {e}")
        return [TextContent(type="text", text=f"❌ Error saving context: {str(e)}")]

    """
    List saved conversation contexts with pagination and filtering.

    Args:
        limit: Number of contexts to return (1-100, default: 20)
        offset: Number of contexts to skip for pagination (default: 0)
        tags: Comma-separated tags to filter by (optional)
        agent_source: Filter by specific agent source (optional)

    Returns:
        List of conversation contexts with pagination info
    """
    try:
        # Validate parameters
        if limit < 1 or limit > 100:
            return [TextContent(type="text", text="❌ Error: Limit must be between 1 and 100")]

        if offset < 0:
            return [TextContent(type="text", text="❌ Error: Offset must be 0 or greater")]

        client = await ensure_api_client()

        result = await client.list_contexts(
            limit=limit,
            offset=offset,
            tags=tags,
            agent_source=agent_source
        )

        contexts = result.get("contexts", [])
        pagination = result.get("pagination", {})

        if not contexts:
            response = "📭 **No Contexts Found**\n\n"
            if tags or agent_source:
                response += "No contexts match your filters.\n\n"
            else:
                response += "You haven't saved any contexts yet.\n\n"

            response += "**Get started:**\n"
            response += "• Use `save_context` to save a conversation for cross-agent sharing\n"
            response += "• Perfect for handoffs between Cursor and Claude Code!"

            return [TextContent(type="text", text=response)]

        # Format the response
        response = f"📚 **Your Conversation Contexts** ({pagination.get('total', len(contexts))} total)\n\n"

        for i, context in enumerate(contexts, offset + 1):
            created_at = context.get('created_at', '')
            if created_at:
                # Format datetime for better readability
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                except:
                    formatted_date = created_at
            else:
                formatted_date = 'Unknown'

            response += f"**{i}. {context['title']}**\n"
            response += f"   🆔 ID: `{context['id']}`\n"
            response += f"   🤖 Source: {context['agent_source']}\n"
            response += f"   📅 Created: {formatted_date}\n"
            response += f"   📝 Summary: {context['summary'][:100]}{'...' if len(context['summary']) > 100 else ''}\n"
            if context.get('tags'):
                response += f"   🏷️ Tags: {', '.join(context['tags'])}\n"
            response += "\n"

        # Add pagination info
        if pagination.get('has_more'):
            next_offset = offset + limit
            response += f"📄 **Pagination:** Showing {offset + 1}-{offset + len(contexts)} of {pagination.get('total')}\n"
            response += f"   Use `list_contexts(offset={next_offset})` for next page\n"

        response += "\n**Actions:**\n"
        response += "• `retrieve_context(context_id)` - Get full context\n"
        response += "• `search_contexts(query)` - Search contexts\n"
        response += "• `delete_context(context_id)` - Remove context"

        return [TextContent(type="text", text=response)]

    except APIError as e:
        logger.error(f"API Error listing contexts: {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error listing contexts: {e}")
        return [TextContent(type="text", text=f"❌ Error listing contexts: {str(e)}")]

# DEPRECATED: Use context(action="retrieve") instead
# @mcp.tool()
# async def retrieve_context(context_id: str) -> List[TextContent]:
    """
    Retrieve a specific conversation context by ID.

    Use this tool to get the full conversation context that was saved by
    another agent. Perfect for getting strategic context from Cursor
    when working in Claude Code.

    Args:
        context_id: The unique ID of the context to retrieve

    Returns:
        Full conversation context with metadata

    Example:
        retrieve_context("550e8400-e29b-41d4-a716-446655440000")
    """
    try:
        if not context_id or not context_id.strip():
            return [TextContent(type="text", text="❌ Error: Context ID is required")]

        client = await ensure_api_client()

        context = await client.get_context(context_id.strip())

        if not context:
            return [TextContent(
                type="text",
                text=f"❌ **Context Not Found**\n\n"
                     f"Context ID `{context_id}` was not found.\n\n"
                     f"**Possible reasons:**\n"
                     f"• The context ID is incorrect\n"
                     f"• The context belongs to a different user\n"
                     f"• The context has been deleted\n\n"
                     f"Use `list_contexts()` to see your available contexts."
            )]

        # Format the context display
        created_at = context.get('created_at', '')
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
            except:
                formatted_date = created_at
        else:
            formatted_date = 'Unknown'

        updated_at = context.get('updated_at', '')
        if updated_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                formatted_updated = dt.strftime('%Y-%m-%d %H:%M UTC')
            except:
                formatted_updated = updated_at
        else:
            formatted_updated = None

        response = f"📋 **Context: {context['title']}**\n\n"
        response += f"🆔 **ID:** `{context['id']}`\n"
        response += f"🤖 **Source Agent:** {context['agent_source']}\n"
        response += f"📅 **Created:** {formatted_date}\n"
        if formatted_updated:
            response += f"🔄 **Updated:** {formatted_updated}\n"

        if context.get('tags'):
            response += f"🏷️ **Tags:** {', '.join(context['tags'])}\n"

        response += f"\n📝 **Summary:**\n{context['summary']}\n\n"

        # Add NIA References - CRITICAL for context handoffs
        # Use 'or {}' to handle cases where nia_references is None (not just missing)
        nia_references = context.get('nia_references') or {}
        if nia_references:
            response += "🧠 **NIA RESOURCES USED - RECOMMENDED ACTIONS:**\n"

            indexed_resources = nia_references.get('indexed_resources', [])
            if indexed_resources:
                response += "**📦 Re-index these resources:**\n"
                for resource in indexed_resources:
                    identifier = resource.get('identifier', 'Unknown')
                    resource_type = resource.get('resource_type', 'unknown')
                    purpose = resource.get('purpose', 'No purpose specified')

                    if resource_type == 'repository':
                        response += f"• `Index {identifier}` - {purpose}\n"
                    elif resource_type == 'documentation':
                        response += f"• `Index documentation {identifier}` - {purpose}\n"
                    else:
                        response += f"• `Index {identifier}` ({resource_type}) - {purpose}\n"
                response += "\n"

            search_queries = nia_references.get('search_queries', [])
            if search_queries:
                response += "**🔍 Useful search queries to re-run:**\n"
                for query in search_queries:
                    query_text = query.get('query', 'Unknown query')
                    query_type = query.get('query_type', 'search')
                    key_findings = query.get('key_findings', 'No findings specified')
                    resources_searched = query.get('resources_searched', [])

                    response += f"• **Query:** `{query_text}` ({query_type})\n"
                    if resources_searched:
                        response += f"  **Resources:** {', '.join(resources_searched)}\n"
                    response += f"  **Key Findings:** {key_findings}\n"
                response += "\n"

            session_summary = nia_references.get('session_summary')
            if session_summary:
                response += f"**📋 NIA Session Summary:** {session_summary}\n\n"

        # Add Edited Files - CRITICAL for code handoffs
        # Use 'or []' to handle cases where edited_files is None (not just missing)
        edited_files = context.get('edited_files') or []
        if edited_files:
            response += "📝 **FILES MODIFIED - READ THESE TO GET UP TO SPEED:**\n"
            for file_info in edited_files:
                file_path = file_info.get('file_path', 'Unknown file')
                operation = file_info.get('operation', 'modified')
                changes_desc = file_info.get('changes_description', 'No description')
                key_changes = file_info.get('key_changes', [])
                language = file_info.get('language', '')

                operation_emoji = {
                    'created': '🆕',
                    'modified': '✏️',
                    'deleted': '🗑️'
                }.get(operation, '📄')

                response += f"• {operation_emoji} **`{file_path}`** ({operation})\n"
                response += f"  **Changes:** {changes_desc}\n"

                if key_changes:
                    response += f"  **Key Changes:** {', '.join(key_changes)}\n"
                if language:
                    response += f"  **Language:** {language}\n"

                response += f"  **💡 Action:** Read this file with: `Read {file_path}`\n"
            response += "\n"

        # Add metadata if available
        # Use 'or {}' to handle cases where metadata is None (not just missing)
        metadata = context.get('metadata') or {}
        if metadata:
            response += f"📊 **Additional Metadata:**\n"
            for key, value in metadata.items():
                if isinstance(value, list):
                    response += f"• **{key}:** {', '.join(map(str, value))}\n"
                else:
                    response += f"• **{key}:** {value}\n"
            response += "\n"

        response += f"📄 **Full Context:**\n\n{context['content']}\n\n"

        response += f"---\n"
        response += f"🚀 **NEXT STEPS FOR SEAMLESS HANDOFF:**\n"
        response += f"• This context was created by **{context['agent_source']}**\n"

        if nia_references.get('search_queries'):
            response += f"• **RECOMMENDED:** Re-run the search queries to get the same insights\n"
        if edited_files:
            response += f"• **ESSENTIAL:** Read the modified files above to understand code changes\n"

        response += f"• Use the summary and full context to understand the strategic planning\n"

        return [TextContent(type="text", text=response)]

    except APIError as e:
        logger.error(f"API Error retrieving context: {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return [TextContent(type="text", text=f"❌ Error retrieving context: {str(e)}")]

    """
    Search conversation contexts by content, title, or summary.

    Args:
        query: Search query to match against title, summary, content, and tags
        limit: Maximum number of results to return (1-100, default: 20)
        tags: Comma-separated tags to filter by (optional)
        agent_source: Filter by specific agent source (optional)

    Returns:
        Search results with matching contexts
    """
    try:
        # Validate parameters
        if not query or not query.strip():
            return [TextContent(type="text", text="❌ Error: Search query is required")]

        if limit < 1 or limit > 100:
            return [TextContent(type="text", text="❌ Error: Limit must be between 1 and 100")]

        client = await ensure_api_client()

        result = await client.search_contexts(
            query=query.strip(),
            limit=limit,
            tags=tags,
            agent_source=agent_source
        )

        contexts = result.get("contexts", [])

        if not contexts:
            response = f"🔍 **No Results Found**\n\n"
            response += f"No contexts match your search query: \"{query}\"\n\n"

            if tags or agent_source:
                response += f"**Active filters:**\n"
                if tags:
                    response += f"• Tags: {tags}\n"
                if agent_source:
                    response += f"• Agent: {agent_source}\n"
                response += "\n"

            response += f"**Suggestions:**\n"
            response += f"• Try different keywords\n"
            response += f"• Remove filters to broaden search\n"
            response += f"• Use `list_contexts()` to see all contexts"

            return [TextContent(type="text", text=response)]

        # Format search results
        response = f"🔍 **Search Results for \"{query}\"** ({len(contexts)} found)\n\n"

        for i, context in enumerate(contexts, 1):
            created_at = context.get('created_at', '')
            if created_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                except:
                    formatted_date = created_at
            else:
                formatted_date = 'Unknown'

            response += f"**{i}. {context['title']}**\n"
            response += f"   🆔 ID: `{context['id']}`\n"
            response += f"   🤖 Source: {context['agent_source']}\n"
            response += f"   📅 Created: {formatted_date}\n"
            response += f"   📝 Summary: {context['summary'][:150]}{'...' if len(context['summary']) > 150 else ''}\n"

            if context.get('tags'):
                response += f"   🏷️ Tags: {', '.join(context['tags'])}\n"

            response += "\n"

        response += f"**Actions:**\n"
        response += f"• `retrieve_context(context_id)` - Get full context\n"
        response += f"• Refine search with different keywords\n"
        response += f"• Use tags or agent filters for better results"

        return [TextContent(type="text", text=response)]

    except APIError as e:
        logger.error(f"API Error searching contexts: {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error searching contexts: {e}")
        return [TextContent(type="text", text=f"❌ Error searching contexts: {str(e)}")]

    """
    Update an existing conversation context.

    Args:
        context_id: The unique ID of the context to update
        title: Updated title (optional)
        summary: Updated summary (optional)
        content: Updated content (optional)
        tags: Updated tags list (optional)
        metadata: Updated metadata (optional)

    Returns:
        Confirmation of successful update
    """
    try:
        if not context_id or not context_id.strip():
            return [TextContent(type="text", text="❌ Error: Context ID is required")]

        # Check that at least one field is being updated
        if not any([title, summary, content, tags is not None, metadata is not None]):
            return [TextContent(
                type="text",
                text="❌ Error: At least one field must be provided for update"
            )]

        # Validate fields if provided
        if title is not None and (not title.strip() or len(title) > 200):
            return [TextContent(
                type="text",
                text="❌ Error: Title must be 1-200 characters"
            )]

        if summary is not None and (len(summary) < 10 or len(summary) > 1000):
            return [TextContent(
                type="text",
                text="❌ Error: Summary must be 10-1000 characters"
            )]

        if content is not None and len(content) < 50:
            return [TextContent(
                type="text",
                text="❌ Error: Content must be at least 50 characters"
            )]

        if tags is not None and len(tags) > 10:
            return [TextContent(
                type="text",
                text="❌ Error: Maximum 10 tags allowed"
            )]

        client = await ensure_api_client()

        result = await client.update_context(
            context_id=context_id.strip(),
            title=title.strip() if title else None,
            summary=summary.strip() if summary else None,
            content=content,
            tags=tags,
            metadata=metadata
        )

        if not result:
            return [TextContent(
                type="text",
                text=f"❌ Error: Context with ID `{context_id}` not found"
            )]

        # List updated fields
        updated_fields = []
        if title is not None:
            updated_fields.append("title")
        if summary is not None:
            updated_fields.append("summary")
        if content is not None:
            updated_fields.append("content")
        if tags is not None:
            updated_fields.append("tags")
        if metadata is not None:
            updated_fields.append("metadata")

        response = f"✅ **Context Updated Successfully!**\n\n"
        response += f"🆔 **Context ID:** `{context_id}`\n"
        response += f"📝 **Title:** {result['title']}\n"
        response += f"🔄 **Updated Fields:** {', '.join(updated_fields)}\n"
        response += f"🤖 **Source Agent:** {result['agent_source']}\n\n"

        response += f"**Current Status:**\n"
        response += f"• **Tags:** {', '.join(result['tags']) if result.get('tags') else 'None'}\n"
        response += f"• **Content Length:** {len(result['content']):,} characters\n\n"

        response += f"Use `retrieve_context('{context_id}')` to see the full updated context."

        return [TextContent(type="text", text=response)]

    except APIError as e:
        logger.error(f"API Error updating context: {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error updating context: {e}")
        return [TextContent(type="text", text=f"❌ Error updating context: {str(e)}")]

    """
    Delete a conversation context.

    Args:
        context_id: The unique ID of the context to delete

    Returns:
        Confirmation of successful deletion

    Example:
        delete_context("550e8400-e29b-41d4-a716-446655440000")
    """
    try:
        if not context_id or not context_id.strip():
            return [TextContent(type="text", text="❌ Error: Context ID is required")]

        client = await ensure_api_client()

        success = await client.delete_context(context_id.strip())

        if success:
            return [TextContent(
                type="text",
                text=f"✅ **Context Deleted Successfully!**\n\n"
                     f"🆔 **Context ID:** `{context_id}`\n\n"
                     f"The context has been permanently removed from your account.\n"
                     f"This action cannot be undone.\n\n"
                     f"Use `list_contexts()` to see your remaining contexts."
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Context Not Found**\n\n"
                     f"Context ID `{context_id}` was not found or has already been deleted.\n\n"
                     f"Use `list_contexts()` to see your available contexts."
            )]

    except APIError as e:
        logger.error(f"API Error deleting context: {e}")
        return [TextContent(type="text", text=f"❌ API Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error deleting context: {e}")
        return [TextContent(type="text", text=f"❌ Error deleting context: {str(e)}")]


# =============================================================================
# ASGI APP EXPORT (must be after all @mcp.tool() decorators)
# =============================================================================
# Export ASGI app for production deployment with uvicorn/gunicorn
# Usage: uvicorn nia_mcp_server.server:http_app --host 0.0.0.0 --port 8000 --workers 4
#
# IMPORTANT: This MUST be defined after all tool definitions so that when Python
# imports this module, all @mcp.tool() decorators have already registered their
# tools with the MCP server before the ASGI app is created.
# =============================================================================
http_app = create_http_app()


async def cleanup():
    """Cleanup resources on shutdown."""
    global api_client, auth_verifier
    if api_client:
        await api_client.close()
        api_client = None
    if auth_verifier:
        await auth_verifier.close()
        auth_verifier = None

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="NIA MCP Server - Knowledge Agent for indexing and searching repositories/documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (default, for Claude Desktop/Cursor)
  python -m nia_mcp_server
  
  # Run with HTTP transport for remote access
  python -m nia_mcp_server --http
  python -m nia_mcp_server --http --port 9000 --host 127.0.0.1
  
  # Production deployment with uvicorn
  uvicorn nia_mcp_server.server:http_app --host 0.0.0.0 --port 8000 --workers 4
        """
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Use HTTP transport instead of stdio (enables remote/network access)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HTTP_HOST,
        help=f"Host to bind to when using HTTP transport (default: {DEFAULT_HTTP_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_HTTP_PORT,
        help=f"Port to bind to when using HTTP transport (default: {DEFAULT_HTTP_PORT})"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=DEFAULT_HTTP_PATH,
        help=f"URL path for MCP endpoint (default: {DEFAULT_HTTP_PATH})"
    )
    return parser.parse_args()


def run():
    """
    Run the MCP server.
    
    Supports two transport modes:
      - STDIO (default): For local clients like Claude Desktop, Cursor
      - HTTP (--http flag): For remote/network access with multi-client support
    
    Examples:
      # STDIO transport (default)
      python -m nia_mcp_server
      
      # HTTP transport
      python -m nia_mcp_server --http --port 8000
      
      # Production with uvicorn
      uvicorn nia_mcp_server.server:http_app --host 0.0.0.0 --port 8000
    """
    args = parse_args()
    
    try:
        # Check for API key early
        get_api_key()
        
        if args.http:
            # HTTP transport for remote/network access
            logger.info(f"Starting NIA MCP Server (HTTP) on {args.host}:{args.port}{args.path}")
            logger.info("Health check available at /health")
            logger.info("Server status available at /status")
            mcp.run(
                transport='http',
                host=args.host,
                port=args.port,
                path=args.path
            )
        else:
            # STDIO transport for local clients (Claude Desktop, Cursor)
            logger.info("Starting NIA MCP Server (STDIO)")
            mcp.run(transport='stdio')
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Run cleanup
        loop = asyncio.new_event_loop()
        loop.run_until_complete(cleanup())
        loop.close()