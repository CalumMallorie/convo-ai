import asyncio
from llm import LLMClient

async def test_llm():
    """Test the LLM client with a simple prompt."""
    client = LLMClient()
    client.set_model("phi")
    
    prompt = """Please help me understand the following:
    1. What is Python?
    2. What are its main features?
    Please provide a concise answer."""
    
    print("Sending prompt:", prompt)
    print("-" * 50)
    
    response = await client.generate(prompt)
    print("Response:", response.text)
    if response.error:
        print("Error:", response.error)

if __name__ == "__main__":
    asyncio.run(test_llm()) 