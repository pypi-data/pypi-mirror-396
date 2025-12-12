"""
MCP server for DocRAG Kit.

This module implements a Model Context Protocol (MCP) server that provides
semantic search capabilities over project documentation. It integrates with
Kiro AI to enable intelligent question-answering about project documentation.

The server provides two main tools:
1. search_docs: Semantic search with optional source file listing
2. list_indexed_docs: List all indexed documentation files

Requirements covered:
- 5.1-5.12: MCP server functionality
- 10.1-10.6: Error handling and user feedback

Usage:
    python -m docrag.mcp_server
    
    Or run via Kiro AI after configuration with `docrag mcp-config`
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from .config_manager import ConfigManager
from .vector_db import VectorDBManager


class MCPServer:
    """MCP server for DocRAG Kit integration with Kiro AI."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize MCP server.
        
        Args:
            config_path: Path to .docrag directory. Defaults to current directory.
        """
        # Determine project root
        if config_path:
            self.project_root = Path(config_path).parent if Path(config_path).name == ".docrag" else Path(config_path)
        else:
            self.project_root = Path.cwd()
        
        # Load environment variables
        load_dotenv(self.project_root / ".env")
        
        # Load configuration
        self.config_manager = ConfigManager(self.project_root)
        config_obj = self.config_manager.load_config()
        
        if not config_obj:
            raise ValueError(
                "❌ Configuration not found.\n"
                "   Run 'docrag init' to initialize DocRAG in this project."
            )
        
        self.config = config_obj.to_dict()
        
        # Initialize vector database manager
        self.vector_db = VectorDBManager(self.config, self.project_root)
        
        # QA chain will be lazily loaded
        self._qa_chain = None
        
        # Initialize MCP server
        self.server = Server("docrag-kit")
        
        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="search_docs",
                    description="Search project documentation using semantic search. "
                                "Поиск в документации проекта с использованием семантического поиска.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Question to search for in the documentation. "
                                              "Вопрос для поиска в документации."
                            },
                            "include_sources": {
                                "type": "boolean",
                                "description": "Include source file names in the response. "
                                              "Включить имена исходных файлов в ответ.",
                                "default": False
                            }
                        },
                        "required": ["question"]
                    }
                ),
                types.Tool(
                    name="list_indexed_docs",
                    description="List all indexed documents in the project. "
                                "Список всех проиндексированных документов в проекте.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_docs":
                    result = await self.handle_search_docs(
                        question=arguments.get("question", ""),
                        include_sources=arguments.get("include_sources", False)
                    )
                    return [types.TextContent(type="text", text=result)]
                
                elif name == "list_indexed_docs":
                    result = await self.handle_list_docs()
                    return [types.TextContent(type="text", text=result)]
                
                else:
                    error_msg = f"❌ Unknown tool: {name}"
                    return [types.TextContent(type="text", text=error_msg)]
            
            except Exception as e:
                error_msg = self._format_error(e)
                return [types.TextContent(type="text", text=error_msg)]

    def get_qa_chain(self):
        """
        Lazy load QA chain.
        
        Returns:
            Tuple of (chain, retriever) for executing queries.
        
        Raises:
            ValueError: If database doesn't exist or API key is missing.
        """
        if self._qa_chain is not None:
            return self._qa_chain
        
        # Get retriever
        try:
            retriever = self.vector_db.get_retriever()
        except ValueError as e:
            raise ValueError(str(e))
        
        # Initialize LLM based on provider
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider', 'openai')
        llm_model = llm_config.get('llm_model')
        temperature = llm_config.get('temperature', 0.3)
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "❌ OpenAI API key not found.\n"
                    "   Add OPENAI_API_KEY to your .env file.\n"
                    "   Get your API key from: https://platform.openai.com/api-keys"
                )
            
            llm = ChatOpenAI(
                model=llm_model or 'gpt-4o-mini',
                temperature=temperature,
                openai_api_key=api_key
            )
        
        elif provider == 'gemini':
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError(
                    "❌ Google API key not found.\n"
                    "   Add GOOGLE_API_KEY to your .env file.\n"
                    "   Get your API key from: https://makersuite.google.com/app/apikey"
                )
            
            llm = ChatGoogleGenerativeAI(
                model=llm_model or 'gemini-1.5-flash',
                temperature=temperature,
                google_api_key=api_key
            )
        
        else:
            raise ValueError(f"❌ Unsupported provider: {provider}")
        
        # Get prompt template
        prompt_config = self.config.get('prompt', {})
        prompt_template_str = prompt_config.get('template', '')
        
        # Create prompt template
        prompt = PromptTemplate(
            template=prompt_template_str,
            input_variables=["context", "question"]
        )
        
        # Helper function to format documents
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Create QA chain using LCEL (LangChain Expression Language)
        # This is the new LangChain 1.x pattern
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Store both chain and retriever for source document retrieval
        self._qa_chain = (chain, retriever)
        
        return self._qa_chain

    async def handle_search_docs(self, question: str, include_sources: bool = False) -> str:
        """
        Handle search_docs tool call.
        
        Args:
            question: Question to search for.
            include_sources: Whether to include source file names in response.
        
        Returns:
            Answer string, optionally with source files.
        
        Raises:
            ValueError: If question is empty or database/API errors occur.
        """
        if not question or not question.strip():
            raise ValueError("❌ Question cannot be empty")
        
        # Get QA chain and retriever
        chain, retriever = self.get_qa_chain()
        
        # Execute query
        try:
            # Invoke the chain with the question
            answer = chain.invoke(question)
            
            # Append sources if requested
            if include_sources:
                # Get source documents from retriever
                source_docs = retriever.invoke(question)
                if source_docs:
                    # Extract unique source files
                    source_files = set()
                    for doc in source_docs:
                        metadata = doc.metadata
                        if 'source_file' in metadata:
                            source_files.add(metadata['source_file'])
                        elif 'source' in metadata:
                            source_path = Path(metadata['source'])
                            source_files.add(source_path.name)
                    
                    if source_files:
                        sources_list = sorted(list(source_files))
                        answer += f"\n\nИсточники / Sources:\n" + "\n".join(f"- {s}" for s in sources_list)
            
            return answer
        
        except Exception as e:
            raise ValueError(f"❌ Query failed: {str(e)}")

    async def handle_list_docs(self) -> str:
        """
        Handle list_indexed_docs tool call.
        
        Returns:
            Formatted list of indexed documents.
        
        Raises:
            ValueError: If database doesn't exist.
        """
        try:
            documents = self.vector_db.list_documents()
            
            if not documents:
                return "📄 No documents indexed yet.\n   Run 'docrag index' to index your documentation."
            
            # Format document list
            doc_list = "\n".join(f"- {doc}" for doc in documents)
            return f"📚 Indexed Documents ({len(documents)}):\n\n{doc_list}"
        
        except ValueError as e:
            raise ValueError(str(e))

    def _format_error(self, error: Exception) -> str:
        """
        Format error message for user-friendly display.
        
        Args:
            error: Exception to format.
        
        Returns:
            Formatted error message.
        """
        error_msg = str(error)
        
        # If error already has emoji and formatting, return as-is
        if error_msg.startswith("❌"):
            return error_msg
        
        # Otherwise, format it
        return f"❌ Error: {error_msg}"

    async def run(self):
        """Run the MCP server with stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for MCP server."""
    try:
        # Determine project root from current directory
        server = MCPServer()
        await server.run()
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
