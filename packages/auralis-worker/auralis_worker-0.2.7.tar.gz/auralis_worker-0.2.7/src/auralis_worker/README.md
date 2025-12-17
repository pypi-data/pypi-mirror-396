# Auralis Worker

[![PyPI version](https://badge.fury.io/py/auralis-worker.svg)](https://badge.fury.io/py/auralis-worker)

The official worker node for the Auralis distributed AI compute platform. Execute jobs from the global compute network on your machine.

## Installation

```bash
pip install auralis-worker
```

## Quick Start

1. **Set environment variables:**

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="auralis-job"
```

2. **Start the worker (polling mode):**

```bash
auralis-worker
```

3. **Run a specific job:**

```bash
auralis-worker --job-id <job-uuid>
```

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--job-id` | `-j` | Run a specific job by UUID |
| `--worker-id` | `-w` | Custom worker identifier |
| `--compute-type` | `-c` | cpu or gpu (default: cpu) |
| `--poll-interval` | `-p` | Seconds between polls (default: 10) |
| `--work-dir` | | Temp directory for jobs |
| `--version` | `-v` | Show version |

## Requirements

- Python 3.9+
- Docker (running)
- AWS S3 access
- Supabase project

## How It Works

1. Worker polls Supabase for pending jobs
2. Claims a job (atomic lock)
3. Downloads project.zip from S3
4. Builds Docker image from Dockerfile
5. Runs container with timeout
6. Streams logs to Supabase (real-time)
7. Uploads outputs to S3
8. Marks job complete

## Development

```bash
# Clone the repo
git clone https://github.com/auralis-dev/auralis
cd auralis/worker

# Install in editable mode
pip install -e .

# Run
auralis-worker
```

## License

MIT © Auralis Team
