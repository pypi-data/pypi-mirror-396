"""Main moderator service application."""

import asyncio
import json
import logging
import signal
import time
from pathlib import Path
from typing import Any

from kryten import (
    ChatMessageEvent,
    KrytenClient,
    UserJoinEvent,
    UserLeaveEvent,
)

from .metrics_server import MetricsServer
from .nats_handler import ModeratorCommandHandler


class ModeratorService:
    """Kryten Moderator Service.

    Provides chat moderation capabilities for CyTube channels:
    - Chat message monitoring
    - User join/leave tracking
    - Spam detection (future)
    - Word filtering (future)
    - Rate limiting (future)
    """

    def __init__(self, config_path: str):
        """Initialize the service.

        Args:
            config_path: Path to configuration JSON file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)

        # Components
        self.client: KrytenClient | None = None
        self.command_handler: ModeratorCommandHandler | None = None
        self.metrics_server: MetricsServer | None = None

        # State
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._start_time: float | None = None
        self._domain: str = "cytu.be"

        # Statistics counters
        self._events_processed = 0
        self._commands_processed = 0
        self._messages_checked = 0
        self._messages_flagged = 0
        self._users_tracked: set[str] = set()

        # Load configuration
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        with open(self.config_path) as f:
            self.config = json.load(f)

        # Override version from package to ensure it stays in sync
        from . import __version__
        if "service" not in self.config:
            self.config["service"] = {}
        self.config["service"]["version"] = __version__

        # Extract domain from first channel config
        channels = self.config.get("channels", [])
        if channels:
            self._domain = channels[0].get("domain", "cytu.be")

        self.logger.info(f"Configuration loaded from {self.config_path}")
        self.logger.info(f"Service version: {__version__}")

    async def start(self) -> None:
        """Start the service."""
        self.logger.info("Starting Kryten Moderator Service")

        # Initialize Kryten client
        self.client = KrytenClient(self.config)

        # Register event handlers
        self.logger.info("Registering event handlers...")

        @self.client.on("chatmsg")
        async def handle_chat(event: ChatMessageEvent):
            await self._handle_chat_message(event)

        @self.client.on("adduser")
        async def handle_user_join(event: UserJoinEvent):
            await self._handle_user_join(event)

        @self.client.on("userleave")
        async def handle_user_leave(event: UserLeaveEvent):
            await self._handle_user_leave(event)

        self.logger.info(f"Registered {len(self.client._handlers)} event types with handlers")

        # Connect to NATS (lifecycle events handled automatically via ServiceConfig)
        await self.client.connect()

        # Track start time for uptime
        self._start_time = time.time()

        # Lifecycle is now managed by KrytenClient - log confirmation
        if self.client.lifecycle:
            self.logger.info("Lifecycle publisher initialized via KrytenClient")

        # Subscribe to robot startup - re-announce when robot starts
        await self.client.subscribe("kryten.lifecycle.robot.startup", self._handle_robot_startup)
        self.logger.info("Subscribed to kryten.lifecycle.robot.startup")

        # Initialize command handler for NATS queries using existing KrytenClient
        self.command_handler = ModeratorCommandHandler(self, self.client)
        await self.command_handler.connect()

        # Initialize metrics server
        metrics_port = self.config.get("metrics", {}).get("port", 28284)
        self.metrics_server = MetricsServer(self, metrics_port)
        await self.metrics_server.start()

        # Start event processing
        self._running = True
        await self.client.run()

    async def stop(self) -> None:
        """Stop the service gracefully."""
        if not self._running:
            self.logger.debug("Service not running, skip stop")
            return

        self.logger.info("Stopping Kryten Moderator Service")
        self._running = False

        # Stop client event loop first
        if self.client:
            self.logger.debug("Stopping Kryten client...")
            await self.client.stop()

        # Stop command handler
        if self.command_handler:
            self.logger.debug("Disconnecting command handler...")
            await self.command_handler.disconnect()

        # Stop metrics server
        if self.metrics_server:
            self.logger.debug("Stopping metrics server...")
            await self.metrics_server.stop()

        # Disconnect from NATS
        if self.client:
            self.logger.debug("Disconnecting from NATS...")
            await self.client.disconnect()

        self.logger.info("Kryten Moderator Service stopped cleanly")

    async def _handle_robot_startup(self, event: Any) -> None:  # noqa: ARG002
        """Handle robot startup event to re-register with the ecosystem."""
        self._events_processed += 1
        self.logger.info("Received robot startup notification, re-announcing service...")

        # Re-announce via lifecycle if available
        if self.client and self.client.lifecycle:
            await self.client.lifecycle.publish_startup()
            self.logger.info("Re-announced service startup")

    async def _handle_chat_message(self, event: ChatMessageEvent) -> None:
        """Handle chat message event for moderation checks."""
        self._events_processed += 1
        self._messages_checked += 1

        try:
            # Safe message preview for logging
            msg_preview = (event.message or "")[:50] if event.message else "(no message)"
            self.logger.debug(f"Chat message from {event.username}: {msg_preview}")

            # Track user
            self._users_tracked.add(event.username.lower())

            # TODO: Add moderation checks here:
            # - Spam detection
            # - Banned word filtering
            # - Excessive caps detection
            # - URL filtering
            # - Rate limiting

            # Placeholder for future moderation logic
            # if self._check_spam(event):
            #     self._messages_flagged += 1
            #     await self._take_action(event, "spam")

        except Exception as e:
            self.logger.error(f"Error handling chat message: {e}", exc_info=True)

    async def _handle_user_join(self, event: UserJoinEvent) -> None:
        """Handle user join event."""
        self._events_processed += 1

        try:
            self.logger.debug(f"User joined: {event.username} in {event.channel}")

            # Track user
            self._users_tracked.add(event.username.lower())

            # TODO: Add join-based moderation:
            # - Check against ban lists
            # - Track join patterns (flood detection)
            # - Welcome message triggers

        except Exception as e:
            self.logger.error(f"Error handling user join: {e}", exc_info=True)

    async def _handle_user_leave(self, event: UserLeaveEvent) -> None:
        """Handle user leave event."""
        self._events_processed += 1

        try:
            self.logger.debug(f"User left: {event.username} from {event.channel}")

            # TODO: Add leave tracking:
            # - Log session duration
            # - Track leave patterns

        except Exception as e:
            self.logger.error(f"Error handling user leave: {e}", exc_info=True)

    def get_uptime_seconds(self) -> float:
        """Get service uptime in seconds."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time


async def main():
    """Main entry point."""
    import argparse
    import platform
    import sys

    # Parse arguments
    parser = argparse.ArgumentParser(description="Kryten Moderator Service for CyTube")
    parser.add_argument(
        "--config", help="Configuration file path (default: /etc/kryten/kryten-moderator/config.json or ./config.json)"
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    # Setup logging first so we can log errors during config validation
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()), 
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Determine config file path
    if args.config:
        config_path = Path(args.config)
    else:
        # Try default locations in order
        default_paths = [
            Path("/etc/kryten/kryten-moderator/config.json"), 
            Path("config.json")
        ]

        config_path = None
        for path in default_paths:
            if path.exists() and path.is_file():
                config_path = path
                break

        if not config_path:
            logger.error("No configuration file found.")
            logger.error("  Searched:")
            for path in default_paths:
                logger.error(f"    - {path}")
            logger.error("  Use --config to specify a custom path.")
            sys.exit(1)

    # Validate config file exists
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    if not config_path.is_file():
        logger.error(f"Configuration path is not a file: {config_path}")
        sys.exit(1)

    # Create service
    service = ModeratorService(str(config_path))

    # Setup signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        shutdown_event.set()

    # Register signal handlers (platform-specific)
    if platform.system() != "Windows":
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: signal_handler(s, None))
    else:
        # Windows uses traditional signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    # Run service
    try:
        # Start service in background task
        service_task = asyncio.create_task(service.start())

        # Wait for shutdown signal or KeyboardInterrupt
        try:
            await shutdown_event.wait()
        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt, initiating shutdown...")

        # Stop the service
        await service.stop()

        # Cancel and wait for service task
        service_task.cancel()
        try:
            await service_task
        except asyncio.CancelledError:
            pass

        logger.info("Shutdown complete")

    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt during startup, shutting down...")
        await service.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await service.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
