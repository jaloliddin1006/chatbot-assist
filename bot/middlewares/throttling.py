import asyncio
import time
from typing import Any, Awaitable, Callable, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
import logging

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Async throttling middleware for aiogram 3.x.
    Prevents spam by limiting the rate of requests per user.
    """
    
    def __init__(self, slow_mode_delay: float = 0.5, cleanup_interval: int = 300):
        """
        Initialize throttling middleware.
        
        Args:
            slow_mode_delay: Minimum delay between requests in seconds
            cleanup_interval: Interval for cleaning old records in seconds
        """
        super().__init__()
        self._user_timeouts = {}
        self._slow_mode_delay = slow_mode_delay
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """
        Main middleware call method.
        """
        user_id = event.from_user.id
        current_time = time.time()
        
        # Periodic cleanup of old records
        await self._cleanup_old_records(current_time)
        
        # Check if user is being throttled
        if await self._is_user_throttled(user_id, current_time):
            await self._send_throttle_message(event)
            return  # Don't continue to handler
        
        # Update user's last request time
        self._user_timeouts[user_id] = current_time
        
        return await handler(event, data)
    
    async def _is_user_throttled(self, user_id: int, current_time: float) -> bool:
        """
        Check if user should be throttled.
        
        Args:
            user_id: Telegram user ID
            current_time: Current timestamp
            
        Returns:
            True if user should be throttled, False otherwise
        """
        last_request_time = self._user_timeouts.get(user_id, 0)
        time_since_last_request = current_time - last_request_time
        
        return time_since_last_request < self._slow_mode_delay
    
    async def _send_throttle_message(self, event: Union[Message, CallbackQuery]):
        """
        Send throttling message to user.
        
        Args:
            event: Message or CallbackQuery event
        """
        throttle_text = "🚫 Juda ko'p so'rov! Biroz kuting va qayta urinib ko'ring."
        
        try:
            if isinstance(event, CallbackQuery):
                await event.answer(throttle_text, show_alert=True)
            else:
                await event.reply(throttle_text)
                
        except Exception as e:
            logger.error(f"Failed to send throttle message: {e}")
    
    async def _cleanup_old_records(self, current_time: float):
        """
        Clean up old throttling records to prevent memory leaks.
        
        Args:
            current_time: Current timestamp
        """
        # Only cleanup periodically
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        try:
            # Remove records older than cleanup interval
            cutoff_time = current_time - self._cleanup_interval
            users_to_remove = [
                user_id for user_id, last_time in self._user_timeouts.items()
                if last_time < cutoff_time
            ]
            
            for user_id in users_to_remove:
                del self._user_timeouts[user_id]
            
            self._last_cleanup = current_time
            
            if users_to_remove:
                logger.debug(f"Cleaned up {len(users_to_remove)} old throttling records")
                
        except Exception as e:
            logger.error(f"Error during throttling cleanup: {e}")
    
    def get_user_timeout_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get timeout information for a specific user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with timeout info
        """
        current_time = time.time()
        last_request = self._user_timeouts.get(user_id, 0)
        time_since_last = current_time - last_request
        remaining_timeout = max(0, self._slow_mode_delay - time_since_last)
        
        return {
            'user_id': user_id,
            'last_request_time': last_request,
            'time_since_last_request': time_since_last,
            'remaining_timeout': remaining_timeout,
            'is_throttled': remaining_timeout > 0
        }
    
    def reset_user_timeout(self, user_id: int):
        """
        Reset timeout for a specific user (admin function).
        
        Args:
            user_id: Telegram user ID
        """
        self._user_timeouts.pop(user_id, None)
        logger.debug(f"Reset throttling timeout for user {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get throttling middleware statistics.
        
        Returns:
            Dictionary with statistics
        """
        current_time = time.time()
        active_users = len(self._user_timeouts)
        throttled_users = sum(
            1 for last_time in self._user_timeouts.values()
            if current_time - last_time < self._slow_mode_delay
        )
        
        return {
            'active_users': active_users,
            'throttled_users': throttled_users,
            'slow_mode_delay': self._slow_mode_delay,
            'cleanup_interval': self._cleanup_interval,
            'last_cleanup': self._last_cleanup
        }
