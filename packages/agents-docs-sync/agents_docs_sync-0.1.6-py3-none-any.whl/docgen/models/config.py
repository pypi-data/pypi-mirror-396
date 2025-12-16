"""Configuration related Pydantic models."""

from __future__ import annotations

from pydantic import Field

from .agents import AgentsConfigSection
from .base import DocgenBaseModel


class LanguagesConfig(DocgenBaseModel):
    """Languages configuration model."""

    auto_detect: bool = True
    preferred: list[str] = Field(default_factory=list)


class OutputConfig(DocgenBaseModel):
    """Output configuration model."""

    api_doc: str = "docs/api.md"
    readme: str = "README.md"
    agents_doc: str = "AGENTS.md"


class GenerationConfig(DocgenBaseModel):
    """Generation configuration model."""

    update_readme: bool = True
    generate_api_doc: bool = True
    generate_agents_doc: bool = True
    preserve_manual_sections: bool = True


class ExcludeConfig(DocgenBaseModel):
    """Exclude configuration model."""

    directories: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)


class CacheConfig(DocgenBaseModel):
    """Cache configuration model."""

    enabled: bool = True


class BenchmarkConfig(DocgenBaseModel):
    """Benchmark configuration model."""

    enabled: bool = False


class DebugConfig(DocgenBaseModel):
    """Debug configuration model."""

    enabled: bool = False


class EmbeddingConfig(DocgenBaseModel):
    """Embedding configuration model."""

    model: str = "all-MiniLM-L6-v2"
    device: str = "cpu"


class IndexConfig(DocgenBaseModel):
    """Index configuration model."""

    type: str = "hnswlib"
    ef_construction: int = 200
    M: int = 16


class RetrievalConfig(DocgenBaseModel):
    """Retrieval configuration model."""

    top_k: int = 6
    score_threshold: float = 0.3


class ChunkingConfig(DocgenBaseModel):
    """Chunking configuration model."""

    max_chunk_size: int = 512
    overlap: int = 50


class RagExcludeConfig(DocgenBaseModel):
    patterns: list[str] = Field(
        default_factory=lambda: [
            r".*\.env$",
            r"secrets/.*",
            r".*_SECRET.*",
            r".*API_KEY.*",
        ]
    )
    files: list[str] = Field(default_factory=lambda: ["README.md", "AGENTS.md"])


class RagConfig(DocgenBaseModel):
    """RAG configuration model."""

    enabled: bool = True
    auto_build_index: bool = False
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    index: IndexConfig = Field(default_factory=IndexConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    exclude: RagExcludeConfig = Field(default_factory=RagExcludeConfig)


class ArchitecturePythonConfig(DocgenBaseModel):
    """Python architecture configuration."""

    max_nodes: int = 400
    collapse_packages: bool = True


class ArchitectureJavascriptConfig(DocgenBaseModel):
    """JavaScript architecture configuration."""

    ignore_patterns: list[str] = Field(default_factory=lambda: ["**/node_modules/**"])


class ArchitectureConfig(DocgenBaseModel):
    """Architecture diagram generation configuration."""

    enabled: bool = False
    output_dir: str = "docs/architecture"
    generator: str = "mermaid"
    image_formats: list[str] = Field(default_factory=lambda: ["png"])
    python: ArchitecturePythonConfig = Field(default_factory=ArchitecturePythonConfig)
    javascript: ArchitectureJavascriptConfig = Field(default_factory=ArchitectureJavascriptConfig)


class DocgenConfig(DocgenBaseModel):
    """Main configuration model for docgen."""

    languages: LanguagesConfig = Field(default_factory=LanguagesConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    agents: AgentsConfigSection = Field(default_factory=lambda: AgentsConfigSection())
    exclude: ExcludeConfig = Field(default_factory=ExcludeConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    benchmark: BenchmarkConfig = Field(default_factory=BenchmarkConfig)
    debug: DebugConfig = Field(default_factory=DebugConfig)
    rag: RagConfig = Field(default_factory=RagConfig)
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)
