"""Worker entry point."""

import argparse
import logging
import sys

from workers.base import Worker, WorkerConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for worker."""
    parser = argparse.ArgumentParser(description="AgentVine Worker")
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Worker name",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="Backend API URL",
    )
    parser.add_argument(
        "--redis-url",
        type=str,
        default="redis://localhost:6379/0",
        help="Redis URL",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Poll interval in seconds",
    )
    parser.add_argument(
        "--heartbeat-interval",
        type=int,
        default=30,
        help="Heartbeat interval in seconds",
    )

    args = parser.parse_args()

    # Create worker config
    config = WorkerConfig(
        name=args.name,
        api_url=args.api_url,
        redis_url=args.redis_url,
        poll_interval=args.poll_interval,
        heartbeat_interval=args.heartbeat_interval,
    )

    # Create and run worker
    worker = Worker(config)

    try:
        logger.info(f"Starting worker: {args.name}")
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
