#!/usr/bin/env python3
"""
Auralis Cloud Worker CLI (Production)
Uses token-based authentication via API - no credentials needed.

Usage:
    auralis-worker --token <token> --job-id <id>
    auralis-worker --token <token>  # Poll mode
"""

import argparse
import asyncio
import logging
import os
import sys
import shutil
import zipfile
import tarfile
import subprocess
import aiohttp
import ssl
import certifi

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ASCII Banner
BANNER = r"""
 $$$$$$\                               $$\ $$\                  $$$$$$\  $$\                           $$\       
$$  __$$\                              $$ |\__|                $$  __$$\ $$ |                          $$ |      
$$ /  $$ |$$\   $$\  $$$$$$\  $$$$$$\  $$ |$$\  $$$$$$$\       $$ /  \__|$$ | $$$$$$\  $$\   $$\  $$$$$$$ |      
$$$$$$$$ |$$ |  $$ |$$  __$$\ \____$$\ $$ |$$ |$$  _____|      $$ |      $$ |$$  __$$\ $$ |  $$ |$$  __$$ |      
$$  __$$ |$$ |  $$ |$$ |  \__|$$$$$$$ |$$ |$$ |\$$$$$$\        $$ |      $$ |$$ /  $$ |$$ |  $$ |$$ /  $$ |      
$$ |  $$ |$$ |  $$ |$$ |     $$  __$$ |$$ |$$ | \____$$\       $$ |  $$\ $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |      
$$ |  $$ |\$$$$$$  |$$ |     \$$$$$$$ |$$ |$$ |$$$$$$$  |      \$$$$$$  |$$ |\$$$$$$  |\$$$$$$  |\$$$$$$$ |      
\__|  \__| \______/ \__|      \_______|\__|\__|\_______/        \______/ \__| \______/  \______/  \_______|      

                         Distributed AI Compute Platform — Worker Node v0.2.6
"""

DEFAULT_API_URL = "https://auraliscloud.xyz"


class AuralisWorker:
    """Production worker that uses token-based API authentication."""
    
    def __init__(self, token: str, api_url: str = None):
        self.token = token
        self.api_url = api_url or os.getenv("AURALIS_API_URL", DEFAULT_API_URL)
        self.headers = {"Authorization": f"Bearer {token}"}
        # Use home directory - Colima/Docker Desktop only share paths under ~
        # /tmp is NOT shared between Mac and Colima VM!
        default_work_dir = os.path.join(os.path.expanduser("~"), ".auralis-worker")
        self.work_dir = os.getenv("WORK_DIR", default_work_dir)
        os.makedirs(self.work_dir, exist_ok=True)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async def verify_token(self) -> bool:
        """Verify the worker token is valid."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.api_url}/api/worker/me",
                    headers=self.headers,
                    ssl=self.ssl_context
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"[OK] Authenticated as: {data.get('name', 'Worker')}")
                        return True
                    else:
                        logger.error(f"[ERROR] Authentication failed: {resp.status}")
                        return False
            except Exception as e:
                logger.error(f"[ERROR] Failed to verify token: {e}")
                return False
    
    async def get_available_jobs(self) -> list:
        """Get list of available jobs."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.api_url}/api/worker/jobs/available",
                    headers=self.headers,
                    ssl=self.ssl_context
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("jobs", [])
                    return []
            except Exception as e:
                logger.error(f"Error fetching jobs: {e}")
                return []
    
    async def claim_job(self, job_id: str) -> bool:
        """Claim a job."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/worker/job/{job_id}/claim",
                    headers=self.headers,
                    ssl=self.ssl_context
                ) as resp:
                    return resp.status == 200
            except Exception as e:
                logger.error(f"Error claiming job: {e}")
                return False
    
    async def get_job_info(self, job_id: str) -> dict:
        """Get job info with presigned URLs."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.api_url}/api/worker/job/{job_id}",
                    headers=self.headers,
                    ssl=self.ssl_context
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error = await resp.text()
                        logger.error(f"Failed to get job info: {error}")
                        return {}
            except Exception as e:
                logger.error(f"Error getting job info: {e}")
                return {}
    
    async def update_status(self, job_id: str, status: str, output_url: str = None):
        """Update job status."""
        async with aiohttp.ClientSession() as session:
            try:
                data = aiohttp.FormData()
                data.add_field("status", status)
                if output_url:
                    data.add_field("output_url", output_url)
                
                async with session.post(
                    f"{self.api_url}/api/worker/job/{job_id}/status",
                    headers=self.headers,
                    data=data,
                    ssl=self.ssl_context
                ) as resp:
                    return resp.status == 200
            except Exception as e:
                logger.error(f"Error updating status: {e}")
                return False
    
    async def append_log(self, job_id: str, content: str):
        """Append log entry."""
        async with aiohttp.ClientSession() as session:
            try:
                data = aiohttp.FormData()
                data.add_field("content", content)
                
                async with session.post(
                    f"{self.api_url}/api/worker/job/{job_id}/log",
                    headers=self.headers,
                    data=data,
                    ssl=self.ssl_context
                ) as resp:
                    return resp.status == 200
            except Exception as e:
                logger.error(f"Error appending log: {e}")
                return False
    
    async def download_input(self, download_url: str, job_dir: str) -> str:
        """Download input file from presigned URL."""
        local_path = os.path.join(job_dir, "input.zip")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url, ssl=self.ssl_context) as resp:
                if resp.status == 200:
                    with open(local_path, "wb") as f:
                        f.write(await resp.read())
                    logger.info(f"[DOWNLOAD] Downloaded {resp.content_length or 'unknown'} bytes")
                    return local_path
                else:
                    logger.error(f"Failed to download: {resp.status}")
                    return ""
    
    def extract_archive(self, archive_path: str, job_dir: str) -> str:
        """Extract archive and find Dockerfile."""
        extract_dir = os.path.join(job_dir, "project")
        os.makedirs(extract_dir, exist_ok=True)
        
        if archive_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(extract_dir)
        elif archive_path.endswith((".tar", ".tar.gz", ".tgz")):
            with tarfile.open(archive_path, "r:*") as tf:
                tf.extractall(extract_dir)
        
        # Find Dockerfile
        for root, dirs, files in os.walk(extract_dir):
            if "Dockerfile" in files:
                return root
        
        return ""
    
    async def build_docker_image(self, project_dir: str, image_name: str, job_id: str) -> bool:
        """Build Docker image."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "build", "-t", image_name, ".",
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            async for line in process.stdout:
                log_line = line.decode().strip()
                if log_line:
                    logger.info(f"[BUILD] {log_line}")
                    await self.append_log(job_id, f"[BUILD] {log_line}")
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Build error: {e}")
            return False
    
    async def run_container(
        self,
        image_name: str,
        output_dir: str,
        container_output_dir: str,
        timeout_hours: float,
        job_id: str
    ) -> bool:
        """Run Docker container."""
        try:
            timeout_seconds = timeout_hours * 3600
            
            # Normalize container output directory
            # Handle relative paths like ./output -> /app/output
            if container_output_dir.startswith("./"):
                container_output_dir = f"/app/{container_output_dir[2:]}"
            elif not container_output_dir.startswith("/"):
                container_output_dir = f"/app/{container_output_dir}"
            
            logger.info(f"[RUN] Mounting {output_dir} -> {container_output_dir}")
            
            process = await asyncio.create_subprocess_exec(
                "docker", "run", "--rm",
                "-v", f"{output_dir}:{container_output_dir}",
                image_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            start_time = asyncio.get_event_loop().time()
            
            async for line in process.stdout:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout_seconds:
                    process.kill()
                    await self.append_log(job_id, f"[TIMEOUT] Timed out after {timeout_hours}h")
                    return False
                
                log_line = line.decode().strip()
                if log_line:
                    logger.info(f"[RUN] {log_line}")
                    await self.append_log(job_id, f"[RUN] {log_line}")
            
            await process.wait()
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Container error: {e}")
            return False
    
    async def upload_outputs(self, output_dir: str, upload_url: str) -> bool:
        """Zip and upload outputs to presigned URL."""
        try:
            # Debug: list what's in the output directory
            logger.info(f"[DEBUG] Checking output directory: {output_dir}")
            if os.path.exists(output_dir):
                files = list(os.listdir(output_dir))
                logger.info(f"[DEBUG] Files in output: {files}")
            else:
                logger.info(f"[DEBUG] Output directory does not exist!")
                return True
            
            # Create zip of outputs
            zip_path = os.path.join(os.path.dirname(output_dir), "output.zip")
            
            files_exist = any(os.scandir(output_dir))
            if not files_exist:
                logger.info("No output files to upload")
                return True
            
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zf.write(file_path, arcname)
                        logger.info(f"[ZIP] Added: {arcname}")
            
            logger.info(f"[UPLOAD] Uploading {zip_path} ({os.path.getsize(zip_path)} bytes)")
            
            # Upload to presigned URL
            async with aiohttp.ClientSession() as session:
                with open(zip_path, "rb") as f:
                    async with session.put(
                        upload_url,
                        data=f.read(),
                        headers={"Content-Type": "application/zip"},
                        ssl=self.ssl_context
                    ) as resp:
                        if resp.status in (200, 201):
                            logger.info("[UPLOAD] Upload successful!")
                            return True
                        else:
                            logger.error(f"[UPLOAD] Failed: {resp.status}")
                            return False
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False
    
    async def execute_job(self, job_id: str) -> bool:
        """Execute a job end-to-end."""
        job_dir = os.path.join(self.work_dir, job_id)
        output_dir = os.path.join(job_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Get job info with presigned URLs
            job_info = await self.get_job_info(job_id)
            if not job_info:
                logger.error("Failed to get job info")
                return False
            
            download_url = job_info.get("input_download_url")
            upload_url = job_info.get("output_upload_url")
            timeout = job_info.get("timeout", 8)
            output_directory = job_info.get("output_directory", "/app/output")
            
            # Update status to RUNNING
            await self.update_status(job_id, "RUNNING")
            await self.append_log(job_id, "[START] Job started")
            
            # Download input
            logger.info("[DOWNLOAD] Downloading input...")
            await self.append_log(job_id, "[DOWNLOAD] Downloading input files...")
            input_file = await self.download_input(download_url, job_dir)
            if not input_file:
                await self.update_status(job_id, "FAILED")
                return False
            
            # Extract
            logger.info("[EXTRACT] Extracting...")
            await self.append_log(job_id, "[EXTRACT] Extracting project files...")
            project_dir = self.extract_archive(input_file, job_dir)
            if not project_dir:
                await self.append_log(job_id, "[ERROR] No Dockerfile found")
                await self.update_status(job_id, "FAILED")
                return False
            
            # Build Docker image
            image_name = f"auralis-job-{job_id[:8]}"
            logger.info(f"[BUILD] Building Docker image: {image_name}")
            await self.append_log(job_id, "[BUILD] Building Docker image...")
            
            if not await self.build_docker_image(project_dir, image_name, job_id):
                await self.append_log(job_id, "[ERROR] Docker build failed")
                await self.update_status(job_id, "FAILED")
                return False
            
            await self.append_log(job_id, "[OK] Docker image built")
            
            # Run container
            logger.info(f"[RUN] Running container ({timeout}h timeout)...")
            await self.append_log(job_id, f"[RUN] Running container...")
            
            if not await self.run_container(
                image_name, output_dir, output_directory, timeout, job_id
            ):
                await self.append_log(job_id, "[ERROR] Container execution failed")
                await self.update_status(job_id, "FAILED")
                return False
            
            await self.append_log(job_id, "[OK] Container finished")
            
            # Upload outputs
            logger.info("[UPLOAD] Uploading outputs...")
            await self.append_log(job_id, "[UPLOAD] Uploading output files...")
            uploaded = await self.upload_outputs(output_dir, upload_url)
            
            # Construct the S3 output URL (matches API pattern)
            # The API generates: outputs/{job_id}/output.zip
            bucket = os.getenv("S3_BUCKET_NAME", "auralis-job")
            output_s3_url = f"s3://{bucket}/outputs/{job_id}/output.zip" if uploaded else None
            
            # Mark complete with output URL
            await self.update_status(job_id, "COMPLETED", output_url=output_s3_url)
            await self.append_log(job_id, "[DONE] Job completed!")
            
            logger.info(f"[OK] Job {job_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing job: {e}")
            await self.append_log(job_id, f"[ERROR] Error: {str(e)}")
            await self.update_status(job_id, "FAILED")
            return False
        finally:
            # Cleanup
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir)
            subprocess.run(["docker", "rmi", f"auralis-job-{job_id[:8]}"], 
                          capture_output=True)
    
    async def run_polling_loop(self, poll_interval: int = 10):
        """Poll for and execute jobs."""
        logger.info(f"[POLL] Polling every {poll_interval}s...")
        
        while True:
            jobs = await self.get_available_jobs()
            
            if jobs:
                job = jobs[0]
                job_id = job["id"]
                logger.info(f"[JOB] Found job: {job_id}")
                
                if await self.claim_job(job_id):
                    logger.info(f"[CLAIMED] Claimed job: {job_id}")
                    await self.execute_job(job_id)
                else:
                    logger.info("Job claimed by another worker")
            
            await asyncio.sleep(poll_interval)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auralis-worker",
        description="Auralis Cloud Worker - Execute distributed compute jobs"
    )
    
    parser.add_argument(
        "--token", "-t",
        type=str,
        required=True,
        help="Your worker authentication token (from auralis.dev/provide)"
    )
    
    parser.add_argument(
        "--job-id", "-j",
        type=str,
        help="Run a specific job by ID"
    )
    
    parser.add_argument(
        "--api-url",
        type=str,
        default=os.getenv("AURALIS_API_URL", DEFAULT_API_URL),
        help="API URL (default: https://auralis.dev/api)"
    )
    
    parser.add_argument(
        "--poll-interval", "-p",
        type=int,
        default=10,
        help="Seconds between job polls (default: 10)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 0.2.6"
    )
    
    return parser


def check_docker() -> bool:
    """Check if Docker is running."""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
        return result.returncode == 0
    except:
        return False


async def run_worker(args):
    worker = AuralisWorker(args.token, args.api_url)
    
    # Verify token
    if not await worker.verify_token():
        logger.error("Invalid token. Get one at https://auralis.dev/provide")
        return 1
    
    if args.job_id:
        # Claim and run specific job
        if await worker.claim_job(args.job_id):
            success = await worker.execute_job(args.job_id)
            return 0 if success else 1
        else:
            logger.error("Failed to claim job")
            return 1
    else:
        # Poll mode
        await worker.run_polling_loop(args.poll_interval)
        return 0


def main() -> int:
    print(BANNER)
    
    parser = get_parser()
    args = parser.parse_args()
    
    if not check_docker():
        logger.error("[ERROR] Docker is not running")
        return 1
    
    try:
        return asyncio.run(run_worker(args))
    except KeyboardInterrupt:
        logger.info("\nWorker stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
