from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from src.moderation import ContentModerator
from src.llm import LLMClient
from src.tts import TTSClient
from src.config import Config, LLMConfig, TTSConfig

# Load environment variables
load_dotenv()

app = FastAPI(title="Convo AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
config = Config()
moderator = ContentModerator()
llm_client = LLMClient(config.llm)
tts_client = TTSClient(config.tts)

class Message(BaseModel):
    """Message model for chat interactions."""
    content: str
    role: str = "user"

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    text: str
    audio_url: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root() -> dict:
    """Root endpoint to verify API is running."""
    return {"status": "online", "message": "Convo AI is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: Message) -> ChatResponse:
    """
    Handle chat interactions.
    
    Args:
        message: The incoming message from the user
        
    Returns:
        ChatResponse: The AI's response with optional audio
    """
    try:
        # 1. Moderate the input
        moderation_result = await moderator.moderate(message.content)
        if not moderation_result.is_safe:
            return ChatResponse(
                text="I apologize, but I cannot process that content.",
                error="Content moderation failed"
            )
        
        # 2. Generate LLM response
        llm_response = await llm_client.generate(message.content)
        if llm_response.error:
            return ChatResponse(
                text="I apologize, but I encountered an error.",
                error=llm_response.error
            )
        
        # 3. Generate speech
        tts_response = await tts_client.generate_speech(llm_response.text)
        
        return ChatResponse(
            text=llm_response.text,
            audio_url=tts_response.audio_url,
            error=tts_response.error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 