import asyncio
from typing import Any, Awaitable, Callable, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
import logging

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    Middleware to handle user registration and update user data.
    """
    
    def __init__(self):
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """
        Main middleware call method.
        """
        try:
            # Get user from event
            user = event.from_user
            if not user:
                return await handler(event, data)
            
            # Register or update user
            telegram_user = await self.user_service.get_or_create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code
            )
              # Add user to data for handlers
            data['user'] = telegram_user
            # Add user language to data for handlers
            data['user_lang'] = telegram_user.language_code or 'en'
            
        except Exception as e:
            logger.error(f"Error in UserMiddleware: {e}")
            # Continue even if user registration fails
        
        return await handler(event, data)
