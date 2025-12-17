"""
PyX AI Integration
LLM and AI helpers with Zen Mode access.
"""
import json
from typing import Optional, List, Dict, Any, Union, AsyncIterator
from dataclasses import dataclass


@dataclass
class AIMessage:
    """Represents a chat message"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass 
class AIResponse:
    """AI response wrapper"""
    content: str
    model: str
    usage: Dict[str, int] = None
    
    def __str__(self):
        return self.content


class AIProvider:
    """Base class for AI providers"""
    
    async def chat(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        raise NotImplementedError
    
    async def stream(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        raise NotImplementedError
    
    async def embed(self, text: str) -> List[float]:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI/ChatGPT provider"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = None
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        self._client = None
    
    @property
    def client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
            
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    async def chat(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        """Send chat completion request"""
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )
    
    async def stream(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        """Stream chat completion"""
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000),
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def embed(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Get text embeddings"""
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding


class AnthropicProvider(AIProvider):
    """Anthropic/Claude provider"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def client(self):
        """Lazy load Anthropic client"""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
            except ImportError:
                raise ImportError("anthropic not installed. Run: pip install anthropic")
            
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client
    
    async def chat(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        """Send chat request to Claude"""
        # Separate system message
        system = None
        chat_messages = []
        
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        
        response = await self.client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", 1000),
            system=system,
            messages=chat_messages
        )
        
        return AIResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        )
    
    async def stream(self, messages: List[AIMessage], **kwargs) -> AsyncIterator[str]:
        """Stream chat response"""
        system = None
        chat_messages = []
        
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        
        async with self.client.messages.stream(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", 1000),
            system=system,
            messages=chat_messages
        ) as stream:
            async for text in stream.text_stream:
                yield text


class GeminiProvider(AIProvider):
    """Google Gemini provider"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp"
    ):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def client(self):
        """Lazy load Gemini client"""
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
            
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client
    
    async def chat(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        """Send chat request to Gemini"""
        # Build conversation history
        history = []
        user_message = None
        
        for m in messages:
            if m.role == "user":
                user_message = m.content
            elif m.role == "assistant":
                history.append({
                    "role": "model",
                    "parts": [m.content]
                })
        
        chat = self._client.start_chat(history=history)
        response = await chat.send_message_async(user_message)
        
        return AIResponse(
            content=response.text,
            model=self.model
        )
    
    async def embed(self, text: str) -> List[float]:
        """Get text embeddings"""
        import google.generativeai as genai
        result = genai.embed_content(
            model="models/embedding-001",
            content=text
        )
        return result["embedding"]


class ZenAI:
    """
    Zen Mode AI - Simple AI/LLM integration.
    
    Usage:
        from pyx import ai
        
        # Configure (choose provider)
        ai.use_openai(api_key="sk-...")
        ai.use_anthropic(api_key="sk-...")
        ai.use_gemini(api_key="...")
        
        # Simple chat
        response = await ai.chat("Explain quantum physics simply")
        print(response)
        
        # With system prompt
        response = await ai.chat(
            "Write a poem about Python",
            system="You are a creative poet"
        )
        
        # Multi-turn conversation
        messages = [
            ai.system("You are a helpful assistant"),
            ai.user("What is Python?"),
            ai.assistant("Python is a programming language..."),
            ai.user("Give me an example")
        ]
        response = await ai.complete(messages)
        
        # Streaming
        async for chunk in ai.stream("Tell me a story"):
            print(chunk, end="")
        
        # Embeddings
        vector = await ai.embed("search query")
    """
    
    def __init__(self):
        self._provider: Optional[AIProvider] = None
    
    # ====================
    # Configuration
    # ====================
    
    def use_openai(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = None
    ):
        """Configure OpenAI/ChatGPT provider"""
        self._provider = OpenAIProvider(
            api_key=api_key,
            model=model,
            base_url=base_url
        )
        return self
    
    def use_anthropic(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """Configure Anthropic/Claude provider"""
        self._provider = AnthropicProvider(
            api_key=api_key,
            model=model
        )
        return self
    
    def use_gemini(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp"
    ):
        """Configure Google Gemini provider"""
        self._provider = GeminiProvider(
            api_key=api_key,
            model=model
        )
        return self
    
    def _check_provider(self):
        """Ensure provider is configured"""
        if self._provider is None:
            raise RuntimeError(
                "AI provider not configured. Use ai.use_openai(), "
                "ai.use_anthropic(), or ai.use_gemini() first."
            )
    
    # ====================
    # Message Helpers
    # ====================
    
    @staticmethod
    def system(content: str) -> AIMessage:
        """Create system message"""
        return AIMessage(role="system", content=content)
    
    @staticmethod
    def user(content: str) -> AIMessage:
        """Create user message"""
        return AIMessage(role="user", content=content)
    
    @staticmethod
    def assistant(content: str) -> AIMessage:
        """Create assistant message"""
        return AIMessage(role="assistant", content=content)
    
    # ====================
    # Core Methods
    # ====================
    
    async def chat(
        self,
        message: str,
        system: str = None,
        **kwargs
    ) -> str:
        """
        Simple chat completion.
        
        Args:
            message: User message
            system: Optional system prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            AI response text
        """
        self._check_provider()
        
        messages = []
        if system:
            messages.append(AIMessage(role="system", content=system))
        messages.append(AIMessage(role="user", content=message))
        
        response = await self._provider.chat(messages, **kwargs)
        return response.content
    
    async def complete(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> AIResponse:
        """
        Full chat completion with message history.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Returns:
            AIResponse object
        """
        self._check_provider()
        return await self._provider.chat(messages, **kwargs)
    
    async def stream(
        self,
        message: str,
        system: str = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream chat completion.
        
        Usage:
            async for chunk in ai.stream("Tell me a story"):
                print(chunk, end="", flush=True)
        """
        self._check_provider()
        
        messages = []
        if system:
            messages.append(AIMessage(role="system", content=system))
        messages.append(AIMessage(role="user", content=message))
        
        async for chunk in self._provider.stream(messages, **kwargs):
            yield chunk
    
    async def embed(self, text: str) -> List[float]:
        """
        Get text embeddings for semantic search.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        self._check_provider()
        return await self._provider.embed(text)
    
    # ====================
    # Utility Methods
    # ====================
    
    async def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text"""
        return await self.chat(
            f"Summarize this in {max_length} words or less:\n\n{text}",
            system="You are a concise summarizer. Only output the summary, nothing else."
        )
    
    async def translate(self, text: str, to_language: str) -> str:
        """Translate text to target language"""
        return await self.chat(
            f"Translate to {to_language}:\n\n{text}",
            system=f"You are a translator. Only output the translation to {to_language}, nothing else."
        )
    
    async def classify(self, text: str, categories: List[str]) -> str:
        """Classify text into one of the categories"""
        categories_str = ", ".join(categories)
        return await self.chat(
            f"Classify this text into one of these categories: {categories_str}\n\nText: {text}",
            system=f"You are a text classifier. Only output one of these categories: {categories_str}. Nothing else."
        )
    
    async def extract(self, text: str, fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract structured data from text.
        
        Args:
            text: Text to extract from
            fields: Dict of field_name -> description
            
        Returns:
            Extracted data as dict
        """
        fields_str = "\n".join([f"- {k}: {v}" for k, v in fields.items()])
        
        response = await self.chat(
            f"Extract the following information from this text:\n{fields_str}\n\nText: {text}",
            system="You are a data extractor. Output valid JSON only, with the requested fields."
        )
        
        try:
            return json.loads(response)
        except:
            return {"raw": response}
    
    async def sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        response = await self.chat(
            f"Analyze the sentiment of this text:\n\n{text}",
            system='You are a sentiment analyzer. Output JSON with fields: "sentiment" (positive/negative/neutral), "confidence" (0-1), "explanation" (brief)'
        )
        
        try:
            return json.loads(response)
        except:
            return {"sentiment": "unknown", "raw": response}


# Zen Mode instance
ai = ZenAI()


__all__ = [
    'ai', 'ZenAI',
    'AIMessage', 'AIResponse',
    'OpenAIProvider', 'AnthropicProvider', 'GeminiProvider'
]
