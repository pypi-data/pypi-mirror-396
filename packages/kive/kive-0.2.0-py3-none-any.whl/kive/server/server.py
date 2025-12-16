"""Kive Memory Gateway Server"""
from typing import Dict
import warnings
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

import kive
from kive.providers.base import BaseProvider
from kive.server.schemas import (
    AddMemoryRequest,
    UpdateMemoryRequest,
    QueryMemoryRequest,
    MemoryResponse,
)


class Server:
    """Memory Gateway Server
    
    Host multiple memory providers and expose unified REST API.
    
    Example:
        >>> from kive.providers.local import Mem0Local
        >>> from kive.providers.cloud import Mem0Cloud
        >>> from kive.server import Server
        >>> 
        >>> mem0_local = Mem0Local(llm_provider="openai", llm_api_key="xxx")
        >>> mem0_cloud = Mem0Cloud(api_key="m0-xxx")
        >>> 
        >>> server = Server(providers={
        ...     "local/mem0": mem0_local,
        ...     "cloud/mem0": mem0_cloud
        ... })
        >>> server.run()
    """
    
    def __init__(
        self,
        providers: Dict[str, BaseProvider],
        host: str = "0.0.0.0",
        port: int = 12123
    ):
        """Initialize Memory Gateway Server
        
        Args:
            providers: Dict mapping route paths to provider instances
                      e.g. {"local/mem0": Mem0Local(), "cloud/mem0": Mem0Cloud()}
            host: Host to bind (default: 0.0.0.0)
            port: Port to bind (default: 12123)
        """
        self.app = FastAPI(
            title="Kive Memory Gateway",
            description="Unified REST API for multiple memory providers",
            version=kive.__version__
        )
        self.providers = providers
        self.host = host
        self.port = port
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes for all providers"""
        # Health check
        @self.app.get("/health")
        async def health():
            return {"status": "ok", "providers": list(self.providers.keys())}
        
        # Create router for each provider
        for provider_key, provider in self.providers.items():
            router = self._create_provider_router(provider_key, provider)
            self.app.include_router(router, prefix=f"/memory/{provider_key}")
    
    def _create_provider_router(self, provider_key: str, provider: BaseProvider) -> APIRouter:
        """Create REST API router for a provider
        
        Args:
            provider_key: Provider route key (e.g. "local/mem0")
            provider: Provider instance
            
        Returns:
            Configured APIRouter
        """
        router = APIRouter(tags=[provider_key])
        
        @router.post("/add", response_model=MemoryResponse)
        async def add_memory(request: AddMemoryRequest):
            """Add memory"""
            try:
                result = await provider.aadd(
                    content=request.content,
                    user_id=request.user_id,
                    metadata=request.metadata
                )
                return MemoryResponse(
                    success=result.status == "completed",
                    message=result.message or f"Memory added with status: {result.status}",
                    data={"id": result.id, "status": result.status},
                    provider=provider_key
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/get/{memory_id}", response_model=MemoryResponse)
        async def get_memory(memory_id: str):
            """Get memory by ID"""
            try:
                result = await provider.aget(memory_id)
                if result is None:
                    raise HTTPException(status_code=404, detail="Memory not found")
                return MemoryResponse(
                    success=True,
                    message="Memory retrieved successfully",
                    data=result.result.dict(),
                    provider=provider_key
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.put("/update/{memory_id}", response_model=MemoryResponse)
        async def update_memory(memory_id: str, request: UpdateMemoryRequest):
            """Update memory"""
            try:
                result = await provider.aupdate(
                    memory_id=memory_id,
                    content=request.content,
                    metadata=request.metadata
                )
                if result is None:
                    raise HTTPException(status_code=404, detail="Memory not found")
                return MemoryResponse(
                    success=True,
                    message="Memory updated successfully",
                    data=result.result.dict(),
                    provider=provider_key
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.delete("/delete/{memory_id}", response_model=MemoryResponse)
        async def delete_memory(memory_id: str):
            """Delete memory"""
            try:
                result = await provider.adelete(memory_id)
                return MemoryResponse(
                    success=result.success,
                    message=result.message,
                    data=None,
                    provider=provider_key
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/search", response_model=MemoryResponse)
        async def search_memory(query: str, user_id: str = None, limit: int = 10):
            """Search memories"""
            try:
                result = await provider.asearch(query=query, user_id=user_id, limit=limit)
                return MemoryResponse(
                    success=True,
                    message=f"Found {len(result.results)} memories",
                    data=[memo.dict() for memo in result.results],
                    provider=provider_key
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.post("/query", response_model=MemoryResponse)
        async def query_memory(request: QueryMemoryRequest):
            """Query memories with filters"""
            try:
                result = await provider.aquery(
                    user_id=request.user_id,
                    filters=request.filters,
                    limit=request.limit
                )
                return MemoryResponse(
                    success=True,
                    message=f"Found {len(result.results)} memories",
                    data=[memo.dict() for memo in result.results],
                    provider=provider_key
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        return router
    
    def run(self, **kwargs):
        """Start the server
        
        Args:
            **kwargs: Additional uvicorn configuration
        """
        # Suppress websockets deprecation warnings from uvicorn
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.*")
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.*")
        
        self._print_startup_banner()
        uvicorn.run(self.app, host=self.host, port=self.port, **kwargs)
    
    def _print_startup_banner(self):
        """Print server startup banner"""
        console = Console()
        
        # ASCII Logo
        logo = """[bold cyan]
██╗  ██╗██╗██╗   ██╗███████╗
██║ ██╔╝██║██║   ██║██╔════╝
█████╔╝ ██║██║   ██║█████╗  
██╔═██╗ ██║╚██╗ ██╔╝██╔══╝  
██║  ██╗██║ ╚████╔╝ ███████╗
╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝[/bold cyan]
[dim]Memory Gateway Server[/dim]
"""
        console.print(logo)
        
        # Version and GitHub info
        version = self.app.version
        console.print(f"[bold]Version:[/bold] {version}")
        console.print(f"[bold]GitHub:[/bold] [link=https://github.com/zhixiangxue/kive-ai]https://github.com/zhixiangxue/kive-ai[/link]\n")
        
        # Convert 0.0.0.0 to accessible URLs
        if self.host == "0.0.0.0":
            url = f"http://localhost:{self.port}"
        else:
            url = f"http://{self.host}:{self.port}"
        
        # Server URLs
        console.print(f"\n[bold green]Server:[/bold green] [link={url}]{url}[/link]")
        console.print(f"[bold green]Docs:[/bold green]   [link={url}/docs]{url}/docs[/link]")
        
        # Providers
        if self.providers:
            console.print("\n[bold yellow]Memory Providers:[/bold yellow]")
            for route, provider in self.providers.items():
                provider_name = provider.__class__.__name__
                console.print(f"  • [cyan]{route}[/cyan] → [green]{provider_name}[/green]")
        
        # Endpoints example
        console.print("\n[bold]API Endpoints:[/bold]")
        if self.providers:
            first_route = list(self.providers.keys())[0]
            console.print(f"  [dim]POST[/dim]   /memory/{first_route}/add")
            console.print(f"  [dim]GET[/dim]    /memory/{first_route}/get/{{id}}")
            console.print(f"  [dim]PUT[/dim]    /memory/{first_route}/update/{{id}}")
            console.print(f"  [dim]DELETE[/dim] /memory/{first_route}/delete/{{id}}")
            console.print(f"  [dim]GET[/dim]    /memory/{first_route}/search?query=...")
            console.print(f"  [dim]POST[/dim]   /memory/{first_route}/query")
            if len(self.providers) > 1:
                console.print(f"  [dim]... (same for other {len(self.providers)-1} providers)[/dim]")
        
        console.print("\n[bold cyan]🚀 Server starting...[/bold cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
