"""Detection models for PromptSentry."""

from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field


class PromptLocation(BaseModel):
    """Location of a detected prompt in source code."""
    
    file_path: str = Field(..., description="Path to the file containing the prompt")
    start_line: int = Field(..., ge=1, description="Starting line number (1-indexed)")
    end_line: int = Field(..., ge=1, description="Ending line number (1-indexed)")
    start_col: Optional[int] = Field(None, ge=0, description="Starting column (0-indexed)")
    end_col: Optional[int] = Field(None, ge=0, description="Ending column (0-indexed)")
    
    @property
    def line_range(self) -> str:
        """Human-readable line range."""
        if self.start_line == self.end_line:
            return f"line {self.start_line}"
        return f"lines {self.start_line}-{self.end_line}"


class DetectedPrompt(BaseModel):
    """A detected AI prompt in source code."""
    
    content: str = Field(..., description="The prompt content")
    location: PromptLocation = Field(..., description="Location in source code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence (0-1)")
    prompt_type: str = Field(
        default="unknown",
        description="Type of prompt (system, user, template, etc.)"
    )
    context: Optional[str] = Field(
        None, 
        description="Surrounding code context"
    )
    variable_name: Optional[str] = Field(
        None,
        description="Variable name containing the prompt"
    )
    
    @property
    def short_content(self) -> str:
        """Truncated content for display."""
        if len(self.content) <= 80:
            return self.content
        return self.content[:77] + "..."
    
    @property
    def location_str(self) -> str:
        """Human-readable location string."""
        return f"{self.location.file_path}:{self.location.start_line}"


class DetectionSignals(BaseModel):
    """Signals used for prompt detection."""
    
    llm_keywords: int = Field(0, ge=0, description="Count of LLM-related keywords")
    instruction_verbs: int = Field(0, ge=0, description="Count of instruction verbs")
    few_shot_patterns: int = Field(0, ge=0, description="Count of few-shot patterns")
    api_calls: int = Field(0, ge=0, description="Count of LLM API calls detected")
    role_patterns: int = Field(0, ge=0, description="Count of role-based patterns")
    template_markers: int = Field(0, ge=0, description="Count of template markers")
    length_score: float = Field(0.0, ge=0.0, le=1.0, description="Length-based score")
    
    @property
    def total_score(self) -> float:
        """Calculate weighted confidence score."""
        # More lenient scoring - a single strong signal should push toward detection
        score = 0.0
        
        # LLM keywords are strong indicators
        if self.llm_keywords >= 1:
            score += 0.4
        if self.llm_keywords >= 2:
            score += 0.2
        
        # Instruction verbs are good indicators
        if self.instruction_verbs >= 1:
            score += 0.2
        if self.instruction_verbs >= 2:
            score += 0.1
        
        # Few-shot patterns are very strong
        if self.few_shot_patterns >= 1:
            score += 0.3
        
        # API calls are definitive
        if self.api_calls >= 1:
            score += 0.5
        
        # Role patterns are strong
        if self.role_patterns >= 1:
            score += 0.3
        
        # Template markers are decent indicators
        if self.template_markers >= 1:
            score += 0.15
        if self.template_markers >= 3:
            score += 0.1
        
        # Length score provides a small boost
        score += self.length_score * 0.1
        
        return min(score, 1.0)
