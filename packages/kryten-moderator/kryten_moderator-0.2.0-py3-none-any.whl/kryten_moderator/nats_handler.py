"""NATS command handler for moderator service.

This module handles command queries on the kryten.moderator.command subject.
It uses KrytenClient instead of direct NATS access, following the architectural
rule that all NATS operations must go through kryten-py.
"""

import logging
from typing import Any

from kryten import KrytenClient


class ModeratorCommandHandler:
    """Handles command queries on NATS subjects owned by moderator service."""

    def __init__(self, app_reference, client: KrytenClient):
        """Initialize command handler using existing KrytenClient.

        Args:
            app_reference: Reference to ModeratorService for accessing state
            client: KrytenClient instance (already connected)
        """
        self.app = app_reference
        self.client = client
        self.logger = logging.getLogger(__name__)

        self._subscriptions: list[Any] = []

    async def connect(self) -> None:
        """Subscribe to unified command subject using KrytenClient.

        Single subject: kryten.moderator.command
        Commands are routed via 'command' field in message payload.
        """
        try:
            subject = "kryten.moderator.command"
            await self._subscribe(subject, self._handle_command)

            self.logger.info(f"Subscribed to {subject}")

        except Exception as e:
            self.logger.error(f"Failed to subscribe to command subjects: {e}", exc_info=True)
            raise

    async def disconnect(self) -> None:
        """Disconnect is handled by KrytenClient.

        No need to manually unsubscribe - KrytenClient manages all subscriptions.
        """
        self.logger.info("Command handler cleanup (managed by KrytenClient)")
        self._subscriptions.clear()

    async def _subscribe(self, subject: str, handler) -> None:
        """Subscribe to a command subject using KrytenClient's request-reply mechanism."""
        sub = await self.client.subscribe_request_reply(subject, handler)
        self._subscriptions.append(sub)
        self.logger.debug(f"Subscribed to {subject}")

    async def _handle_command(self, request: dict) -> dict:
        """Dispatch commands based on 'command' field in request.

        Request format:
            {
                "command": "system.health" | "system.stats" | etc,
                "service": "moderator",  # For routing/filtering (optional)
                ... command-specific parameters ...
            }

        Response format:
            {
                "service": "moderator",
                "command": "system.health",
                "success": true,
                "data": { ... } | "error": "message"
            }
        """
        # Increment commands counter
        self.app._commands_processed += 1

        command = request.get("command")

        if not command:
            return {"service": "moderator", "success": False, "error": "Missing 'command' field"}

        # Check service field for routing (other services can ignore)
        service = request.get("service")
        if service and service != "moderator":
            return {
                "service": "moderator",
                "success": False,
                "error": f"Command intended for '{service}', not 'moderator'",
            }

        # Dispatch to handler
        handler_map = {
            "system.health": self._handle_system_health,
            "system.stats": self._handle_system_stats,
            # Future commands:
            # "filter.add": self._handle_filter_add,
            # "filter.remove": self._handle_filter_remove,
            # "filter.list": self._handle_filter_list,
            # "user.warn": self._handle_user_warn,
            # "user.mute": self._handle_user_mute,
        }

        handler = handler_map.get(command)
        if not handler:
            return {
                "service": "moderator",
                "command": command,
                "success": False,
                "error": f"Unknown command: {command}",
            }

        try:
            result = await handler(request)
            return {"service": "moderator", "command": command, "success": True, "data": result}
        except Exception as e:  # noqa: BLE001
            self.logger.error(f"Error executing command '{command}': {e}", exc_info=True)
            return {"service": "moderator", "command": command, "success": False, "error": str(e)}

    async def _handle_system_health(self, request: dict) -> dict:
        """Handle system.health query - Get service health status."""
        from . import __version__

        return {
            "service": "moderator",
            "status": "healthy" if self.app._running else "starting",
            "version": __version__,
            "uptime_seconds": self.app.get_uptime_seconds(),
        }

    async def _handle_system_stats(self, request: dict) -> dict:
        """Handle system.stats query - Get service statistics."""
        from . import __version__

        return {
            "service": "moderator",
            "version": __version__,
            "uptime_seconds": self.app.get_uptime_seconds(),
            "events_processed": self.app._events_processed,
            "commands_processed": self.app._commands_processed,
            "messages_checked": self.app._messages_checked,
            "messages_flagged": self.app._messages_flagged,
            "users_tracked": len(self.app._users_tracked),
        }
