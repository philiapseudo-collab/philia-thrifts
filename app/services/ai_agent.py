"""
AI Agent for conversational intelligence (Simplified MVP).

Stateless conversation with OpenAI GPT-4o function calling for inventory search.
"""
import json
import logging
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.services.inventory import search_available_items
from app.clients.tiktok import TikTokClient

logger = logging.getLogger(__name__)


class AIAgent:
    """
    Simplified AI agent for Philia Thrifts.
    
    Features:
    - OpenAI GPT-4o with function calling
    - Inventory search integration
    - Stateless (no conversation history for MVP)
    - TikTok message sending
    """
    
    def __init__(self, tiktok_client: TikTokClient):
        """
        Initialize AI agent.
        
        Args:
            tiktok_client: TikTok API client for sending messages
        """
        self.tiktok = tiktok_client
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.system_prompt = """
        You are Philia, a helpful, trendy assistant for Philia Thrifts.
        You sell one-of-a-kind vintage clothes.
        
        RULES:
        - NEVER invent inventory. ALWAYS use the 'search_inventory' tool.
        - If the tool returns no results, say "I couldn't find that right now."
        - If a user asks for size, give specific measurements (pit-to-pit), not just "Large".
        - Keep messages short (under 200 chars preferred) and conversational.
        - Use emojis sparingly (✨, 🧥, 🤎).
        """

    async def handle_conversation(
        self, 
        user_id: str, 
        user_text: str, 
        session: AsyncSession
    ):
        """
        Handle conversation with user.
        
        Flow:
        1. Call OpenAI with tools
        2. If tool requested, execute search_inventory
        3. Get final response from OpenAI
        4. Send via TikTok
        
        Args:
            user_id: TikTok user OpenID
            user_text: User's message
            session: Database session
        """
        # 1. Define Tools
        tools = [{
            "type": "function",
            "function": {
                "name": "search_inventory",
                "description": "Search for available clothes by name or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string", 
                            "description": "Search term e.g. 'vintage nike'"
                        }
                    },
                    "required": ["query"]
                }
            }
        }]

        # 2. Prepare Messages (Stateless - no history)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_text}
        ]

        # 3. Call OpenAI (Step 1)
        logger.info(f"Calling OpenAI for user {user_id}: '{user_text[:50]}...'")
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_msg = response.choices[0].message
        final_text = response_msg.content  # Default if no tool used

        # 4. Handle Tool Call
        if response_msg.tool_calls:
            logger.info(f"OpenAI requested {len(response_msg.tool_calls)} tool calls")
            messages.append(response_msg)
            
            for tool_call in response_msg.tool_calls:
                if tool_call.function.name == "search_inventory":
                    args = json.loads(tool_call.function.arguments)
                    query = args.get("query", "")
                    
                    logger.info(f"Executing search_inventory('{query}')")
                    
                    # Search database
                    items = await search_available_items(query, session)
                    
                    # Format results for OpenAI
                    items_str = json.dumps([{
                        "name": i.name, 
                        "price": str(i.price), 
                        "size": i.size_label,
                        "measurements": i.measurements
                    } for i in items])
                    
                    logger.info(f"Found {len(items)} items for query '{query}'")
                    
                    # Append tool result
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": items_str
                    })

            # 5. Call OpenAI (Step 2 - Final Answer)
            logger.info("Getting final response from OpenAI...")
            final_response = await self.openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_text = final_response.choices[0].message.content

        logger.info(f"AI response: '{final_text[:100]}...'")

        # 6. Send Reply via TikTok
        await self.tiktok.send_message(user_id, final_text)
