"""Configuration models for PromptSentry."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_CONFIG_DIR = Path.home() / ".promptsentry"
DEFAULT_DB_PATH = DEFAULT_CONFIG_DIR / "issues.db"
DEFAULT_VECTOR_DB_PATH = DEFAULT_CONFIG_DIR / "chroma_db"
DEFAULT_MODEL_CACHE = DEFAULT_CONFIG_DIR / "models"


class ScanConfig(BaseModel):
    """Configuration for scanning behavior."""

    threshold: int = Field(
        80, ge=0, le=100,
        description="Minimum security score required (0-100). Score below this blocks commit."
    )
    min_confidence: float = Field(
        0.6, ge=0.0, le=1.0,
        description="Minimum confidence for prompt detection"
    )
    file_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go"],
        description="File extensions to scan"
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["**/node_modules/**", "**/.git/**", "**/venv/**", "**/__pycache__/**"],
        description="Glob patterns to exclude from scanning"
    )
    max_file_size: int = Field(
        1_000_000,  # 1MB
        description="Maximum file size to scan (bytes)"
    )


class LLMConfig(BaseModel):
    """Configuration for LLM via Ollama."""

    model_config = ConfigDict(protected_namespaces=())

    # Ollama settings (recommended - works locally without auth)
    provider: str = Field(
        "ollama",
        description="LLM provider: 'ollama' (recommended) or 'transformers'"
    )
    model_name: str = Field(
        "deepseek-r1:1.5b",
        description="Model name (Ollama: deepseek-r1:1.5b, qwen3:4b, llama3.2:3b, etc.)"
    )
    ollama_base_url: str = Field(
        "http://localhost:11434",
        description="Ollama API base URL"
    )

    # Generation settings
    max_tokens: int = Field(
        4096,
        description="Maximum tokens for generation"
    )
    temperature: float = Field(
        0.1, ge=0.0, le=2.0,
        description="Temperature for generation (lower = more consistent)"
    )

    # Legacy HuggingFace settings (for transformers provider)
    device: str = Field(
        "auto",
        description="Device for transformers (auto, cpu, cuda, mps)"
    )
    use_gpu: bool = Field(
        True,
        description="Whether to use GPU if available"
    )
    load_in_4bit: bool = Field(
        False,
        description="Whether to use 4-bit quantization"
    )


class VectorDBConfig(BaseModel):
    """Configuration for vector database."""

    db_path: Path = Field(
        default_factory=lambda: DEFAULT_VECTOR_DB_PATH,
        description="Path to ChromaDB database"
    )
    embedding_model: str = Field(
        "all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )
    similarity_threshold: float = Field(
        0.65, ge=0.0, le=1.0,
        description="Minimum similarity for matches"
    )
    top_k: int = Field(
        5, ge=1,
        description="Number of similar matches to return"
    )


class HookConfig(BaseModel):
    """Configuration for git hook."""

    enabled: bool = Field(True, description="Whether hook is enabled")
    block_on_issues: bool = Field(True, description="Whether to block commits with issues")
    allow_bypass: bool = Field(True, description="Allow --no-verify bypass")
    show_fixes: bool = Field(True, description="Show fix suggestions")
    verbose: bool = Field(False, description="Verbose output")


class PromptSentryConfig(BaseModel):
    """Main configuration for PromptSentry."""

    config_dir: Path = Field(
        default_factory=lambda: DEFAULT_CONFIG_DIR,
        description="Configuration directory"
    )
    scan: ScanConfig = Field(default_factory=ScanConfig, description="Scan configuration")
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    vectordb: VectorDBConfig = Field(default_factory=VectorDBConfig, description="Vector DB configuration")
    hook: HookConfig = Field(default_factory=HookConfig, description="Git hook configuration")

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "PromptSentryConfig":
        """Load configuration from file or create default."""
        import yaml

        if config_path is None:
            config_path = DEFAULT_CONFIG_DIR / "config.yaml"

        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
            return cls(**data)

        return cls()

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file."""
        import yaml

        if config_path is None:
            config_path = self.config_dir / "config.yaml"

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(mode="json"), f, default_flow_style=False)

    @property
    def db_path(self) -> Path:
        """Path to issue database."""
        return self.config_dir / "issues.db"

    @property
    def vector_db_path(self) -> Path:
        """Path to vector database."""
        return self.config_dir / "chroma_db"

    @property
    def model_cache_path(self) -> Path:
        """Path to model cache."""
        return self.config_dir / "models"
