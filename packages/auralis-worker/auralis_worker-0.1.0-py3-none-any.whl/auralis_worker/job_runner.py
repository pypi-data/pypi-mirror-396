"""
Job Runner
Handles the full lifecycle of executing a job:
1. Download input from S3
2. Build Docker image
3. Run container with timeout
4. Stream logs in real-time
5. Upload outputs to S3
"""

import os
import shutil
import logging
import asyncio
import zipfile
import tarfile
import subprocess
from typing import Optional

from .s3_client import download_from_s3, upload_directory_to_s3
from .supabase_client import get_job, update_job_status, append_log, batch_append_logs

logger = logging.getLogger(__name__)


class JobRunner:
    """Executes jobs by building and running Docker containers."""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.work_dir = os.getenv("WORK_DIR", "/tmp/auralis-worker")
        os.makedirs(self.work_dir, exist_ok=True)
    
    async def execute_job(self, job_id: str) -> bool:
        """
        Execute a job end-to-end.
        
        Returns True if successful, False otherwise.
        """
        job_dir = os.path.join(self.work_dir, job_id)
        output_dir = os.path.join(job_dir, "output")
        
        try:
            # Create job directory
            os.makedirs(job_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)
            
            # Get job details
            job = await get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            input_url = job.get("input_url", "")
            timeout_hours = job.get("timeout", 8)
            output_directory = job.get("output_directory", "/app/output")
            
            # Update status to RUNNING
            await update_job_status(job_id, "RUNNING")
            await append_log(job_id, f"🚀 Job started by worker {self.worker_id}")
            
            # Step 1: Download input from S3
            logger.info(f"📥 Downloading input from {input_url}")
            await append_log(job_id, f"📥 Downloading input files...")
            
            input_file = await self._download_input(input_url, job_dir)
            if not input_file:
                await append_log(job_id, "❌ Failed to download input")
                await update_job_status(job_id, "FAILED")
                return False
            
            # Step 2: Extract the archive
            logger.info(f"📦 Extracting {input_file}")
            await append_log(job_id, "📦 Extracting project files...")
            
            project_dir = await self._extract_archive(input_file, job_dir)
            if not project_dir:
                await append_log(job_id, "❌ Failed to extract archive")
                await update_job_status(job_id, "FAILED")
                return False
            
            # Step 3: Build Docker image
            image_name = f"auralis-job-{job_id[:8]}"
            logger.info(f"🔨 Building Docker image: {image_name}")
            await append_log(job_id, f"🔨 Building Docker image...")
            
            build_success = await self._build_docker_image(project_dir, image_name, job_id)
            if not build_success:
                await append_log(job_id, "❌ Docker build failed")
                await update_job_status(job_id, "FAILED")
                return False
            
            await append_log(job_id, "✅ Docker image built successfully")
            
            # Step 4: Run container
            logger.info(f"▶️ Running container with {timeout_hours}h timeout")
            await append_log(job_id, f"▶️ Running container...")
            
            run_success = await self._run_container(
                image_name=image_name,
                output_dir=output_dir,
                container_output_dir=output_directory,
                timeout_hours=timeout_hours,
                job_id=job_id
            )
            
            if not run_success:
                await append_log(job_id, "❌ Container execution failed")
                await update_job_status(job_id, "FAILED")
                return False
            
            await append_log(job_id, "✅ Container finished successfully")
            
            # Step 5: Upload outputs to S3
            logger.info(f"📤 Uploading outputs to S3")
            await append_log(job_id, "📤 Uploading output files...")
            
            output_url = await self._upload_outputs(output_dir, job_id)
            
            # Step 6: Mark as completed
            await update_job_status(job_id, "COMPLETED", output_url=output_url)
            await append_log(job_id, f"🎉 Job completed! Output: {output_url}")
            
            logger.info(f"✅ Job {job_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing job {job_id}: {e}")
            await append_log(job_id, f"❌ Error: {str(e)}")
            await update_job_status(job_id, "FAILED")
            return False
            
        finally:
            # Cleanup
            await self._cleanup(job_dir, f"auralis-job-{job_id[:8]}")
    
    async def _download_input(self, input_url: str, job_dir: str) -> Optional[str]:
        """Download input file from S3."""
        try:
            # Parse S3 URL: s3://bucket/key
            if input_url.startswith("s3://"):
                parts = input_url[5:].split("/", 1)
                if len(parts) == 2:
                    bucket, key = parts
                    
                    # Determine file extension
                    ext = ".zip"
                    if key.endswith(".tar"):
                        ext = ".tar"
                    elif key.endswith(".tar.gz"):
                        ext = ".tar.gz"
                    
                    local_path = os.path.join(job_dir, f"input{ext}")
                    await download_from_s3(bucket, key, local_path)
                    return local_path
            
            logger.error(f"Invalid S3 URL: {input_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading input: {e}")
            return None
    
    async def _extract_archive(self, archive_path: str, job_dir: str) -> Optional[str]:
        """Extract archive and return project directory."""
        try:
            extract_dir = os.path.join(job_dir, "project")
            os.makedirs(extract_dir, exist_ok=True)
            
            if archive_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zf:
                    zf.extractall(extract_dir)
            elif archive_path.endswith((".tar", ".tar.gz", ".tgz")):
                with tarfile.open(archive_path, "r:*") as tf:
                    tf.extractall(extract_dir)
            else:
                logger.error(f"Unknown archive format: {archive_path}")
                return None
            
            # Find Dockerfile - might be in a subdirectory
            dockerfile_path = self._find_dockerfile(extract_dir)
            if dockerfile_path:
                return os.path.dirname(dockerfile_path)
            
            logger.error("No Dockerfile found in archive")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting archive: {e}")
            return None
    
    def _find_dockerfile(self, search_dir: str) -> Optional[str]:
        """Find Dockerfile in directory tree."""
        for root, dirs, files in os.walk(search_dir):
            if "Dockerfile" in files:
                return os.path.join(root, "Dockerfile")
        return None
    
    async def _build_docker_image(
        self,
        project_dir: str,
        image_name: str,
        job_id: str
    ) -> bool:
        """Build Docker image from project directory."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "build", "-t", image_name, ".",
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            log_buffer = []
            async for line in process.stdout:
                log_line = line.decode().strip()
                if log_line:
                    logger.info(f"[BUILD] {log_line}")
                    log_buffer.append(f"[BUILD] {log_line}")
                    
                    # Batch send logs every 10 lines
                    if len(log_buffer) >= 10:
                        await batch_append_logs(job_id, log_buffer)
                        log_buffer = []
            
            # Send remaining logs
            if log_buffer:
                await batch_append_logs(job_id, log_buffer)
            
            await process.wait()
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Error building Docker image: {e}")
            return False
    
    async def _run_container(
        self,
        image_name: str,
        output_dir: str,
        container_output_dir: str,
        timeout_hours: float,
        job_id: str
    ) -> bool:
        """Run Docker container with timeout and log streaming."""
        try:
            timeout_seconds = timeout_hours * 3600
            
            # Ensure container output dir is absolute (Docker requirement)
            if not container_output_dir or not container_output_dir.startswith("/"):
                container_output_dir = "/app/output"
                logger.info(f"Using default container output directory: {container_output_dir}")
            
            # Run container with output volume mount
            process = await asyncio.create_subprocess_exec(
                "docker", "run", "--rm",
                "-v", f"{output_dir}:{container_output_dir}",
                image_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            log_buffer = []
            start_time = asyncio.get_event_loop().time()
            
            try:
                async for line in process.stdout:
                    # Check timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > timeout_seconds:
                        logger.warning(f"Job timed out after {timeout_hours}h")
                        process.kill()
                        await append_log(job_id, f"⏰ Job timed out after {timeout_hours} hours")
                        return False
                    
                    log_line = line.decode().strip()
                    if log_line:
                        logger.info(f"[RUN] {log_line}")
                        log_buffer.append(f"[RUN] {log_line}")
                        
                        # Stream logs in batches
                        if len(log_buffer) >= 5:
                            await batch_append_logs(job_id, log_buffer)
                            log_buffer = []
                
                # Send remaining logs
                if log_buffer:
                    await batch_append_logs(job_id, log_buffer)
                
                await process.wait()
                return process.returncode == 0
                
            except asyncio.TimeoutError:
                process.kill()
                await append_log(job_id, f"⏰ Job timed out after {timeout_hours} hours")
                return False
                
        except Exception as e:
            logger.error(f"Error running container: {e}")
            return False
    
    async def _upload_outputs(self, output_dir: str, job_id: str) -> str:
        """Upload output directory to S3."""
        try:
            output_key = f"outputs/{job_id}"
            bucket = os.getenv("S3_BUCKET_NAME", "auralis-job")
            
            # Check if there are any files to upload
            files = list(os.walk(output_dir))
            if not files or not any(f[2] for f in files):
                logger.info("No output files to upload")
                return f"s3://{bucket}/{output_key}/"
            
            # Upload the entire output directory
            await upload_directory_to_s3(output_dir, bucket, output_key)
            
            return f"s3://{bucket}/{output_key}/"
            
        except Exception as e:
            logger.error(f"Error uploading outputs: {e}")
            return ""
    
    async def _cleanup(self, job_dir: str, image_name: str):
        """Clean up job directory and Docker resources."""
        try:
            # Remove job directory
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir)
                logger.info(f"Cleaned up job directory: {job_dir}")
            
            # Remove Docker image
            try:
                subprocess.run(
                    ["docker", "rmi", image_name],
                    capture_output=True,
                    timeout=30
                )
                logger.info(f"Removed Docker image: {image_name}")
            except Exception:
                pass  # Image might not exist or be in use
                
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
