# 🌌 Auralis Worker Node

The worker node polls for pending jobs, executes them in Docker containers, and streams logs back to the dashboard.

## Prerequisites

- **Python 3.10+**
- **Docker** installed and running
- AWS credentials configured
- Supabase credentials configured

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file in the worker directory:
   ```env
   # Supabase
   SUPABASE_URL=your-supabase-url
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

   # AWS S3
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=auralis-job

   # Worker Config
   WORKER_ID=my-local-worker
   COMPUTE_TYPE=cpu
   POLL_INTERVAL=10
   WORK_DIR=/tmp/auralis-worker
   ```

## Usage

### Auto-Poll Mode (Default)
Continuously polls for pending jobs and executes them:
```bash
python main.py
```

### Run Specific Job
Execute a specific job by ID:
```bash
python main.py --job-id abc123-def456
```

### Options
```
-j, --job-id    Run a specific job by ID
-w, --worker-id Unique worker identifier (default: worker-<pid>)
```

## How It Works

1. **Poll**: Worker checks Supabase for `PENDING` jobs
2. **Claim**: Worker atomically claims a job (`PENDING` → `CLAIMED`)
3. **Download**: Downloads project zip from S3
4. **Build**: Builds Docker image from Dockerfile
5. **Run**: Executes container with output volume mounted
6. **Stream**: Logs are streamed to Supabase in real-time
7. **Upload**: Output files are uploaded to S3
8. **Complete**: Job marked as `COMPLETED` or `FAILED`

## Architecture

```
worker/
├── main.py           # Entry point, polling loop
├── job_runner.py     # Docker build & run logic
├── supabase_client.py # Job queries & log streaming
├── s3_client.py      # File upload/download
└── requirements.txt  # Dependencies
```
