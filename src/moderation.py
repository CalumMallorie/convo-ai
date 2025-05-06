from typing import Dict, Any
import os
from openai import OpenAI
from pydantic import BaseModel

class ModerationResult(BaseModel):
    """Result of content moderation."""
    is_safe: bool
    flagged_categories: Dict[str, float]
    error: str | None = None

class ContentModerator:
    """Handles content moderation using OpenAI's moderation API."""
    
    def __init__(self) -> None:
        """Initialize the moderator with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    async def moderate(self, text: str) -> ModerationResult:
        """
        Moderate the given text content.
        
        Args:
            text: The text content to moderate
            
        Returns:
            ModerationResult: The moderation result with safety status
        """
        try:
            response = await self.client.moderations.create(input=text)
            result = response.results[0]
            
            return ModerationResult(
                is_safe=not result.flagged,
                flagged_categories=result.category_scores.model_dump()
            )
        except Exception as e:
            return ModerationResult(
                is_safe=False,
                flagged_categories={},
                error=str(e)
            ) 