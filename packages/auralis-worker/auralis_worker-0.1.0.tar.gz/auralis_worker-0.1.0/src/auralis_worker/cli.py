#!/usr/bin/env python3
"""
Auralis Worker CLI
Global command-line interface for running Auralis worker nodes.

Usage:
    auralis-worker                    # Start polling for jobs
    auralis-worker --job-id <id>      # Run a specific job
    auralis-worker --help             # Show help
"""

import argparse
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ASCII Banner
BANNER = """
    ╔═══════════════════════════════════════╗
    ║     🌌 AURALIS WORKER NODE 🌌         ║
    ║   The Distributed AI Computer         ║
    ╚═══════════════════════════════════════╝
"""


def get_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="auralis-worker",
        description="Auralis Worker Node - Execute distributed AI compute jobs",
        epilog="Visit https://auralis.dev for more information."
    )
    
    parser.add_argument(
        "--job-id", "-j",
        type=str,
        help="Run a specific job by ID instead of polling"
    )
    
    parser.add_argument(
        "--worker-id", "-w",
        type=str,
        default=os.getenv("WORKER_ID", f"worker-{os.getpid()}"),
        help="Unique identifier for this worker (default: auto-generated)"
    )
    
    parser.add_argument(
        "--compute-type", "-c",
        type=str,
        choices=["cpu", "gpu"],
        default=os.getenv("COMPUTE_TYPE", "cpu"),
        help="Type of compute this worker provides (default: cpu)"
    )
    
    parser.add_argument(
        "--poll-interval", "-p",
        type=int,
        default=int(os.getenv("POLL_INTERVAL", "10")),
        help="Seconds between job polls (default: 10)"
    )
    
    parser.add_argument(
        "--work-dir",
        type=str,
        default=os.getenv("WORK_DIR", "/tmp/auralis-worker"),
        help="Directory for temporary job files (default: /tmp/auralis-worker)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser


def check_environment() -> bool:
    """Check required environment variables."""
    required = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Set these in your environment or .env file:")
        for var in missing:
            logger.error(f"  export {var}=<your-value>")
        return False
    
    return True


def check_docker() -> bool:
    """Check if Docker is available."""
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


async def run_worker(args: argparse.Namespace) -> int:
    """Run the worker with given arguments."""
    from .worker import AuralisWorker
    
    worker = AuralisWorker(
        worker_id=args.worker_id,
        compute_type=args.compute_type,
        poll_interval=args.poll_interval
    )
    
    if args.job_id:
        logger.info(f"🚀 Running specific job: {args.job_id}")
        success = await worker.run_single_job(args.job_id)
        return 0 if success else 1
    else:
        logger.info(f"🔄 Starting polling loop (interval: {args.poll_interval}s)")
        await worker.run_polling_loop()
        return 0


def main() -> int:
    """Main entry point for the CLI."""
    print(BANNER)
    
    parser = get_parser()
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Check Docker
    if not check_docker():
        logger.error("❌ Docker is not running or not installed")
        logger.error("Please start Docker and try again")
        return 1
    
    # Run the worker
    try:
        return asyncio.run(run_worker(args))
    except KeyboardInterrupt:
        logger.info("\n👋 Worker stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Worker error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
