# clserve

CLI tool for serving LLM models on Alps with sglang.

## Installation

```bash
pip install clserve
```

Or install from source:

```bash
git clone https://github.com/nathanrchn/clserve
cd clserve
pip install -e .
```

## Features

- **Predefined model configurations** - Serve popular models with optimized settings
- **Multi-node distributed serving** - Scale across multiple nodes with tensor parallelism
- **Load balancing** - Built-in router support for distributing requests across workers
- **Real-time status monitoring** - Track worker loading stages from initialization to ready
- **Flexible deployment** - Single-node, multi-node, or multiple instances per node
- **Model management** - Download models from HuggingFace Hub
- **Log management** - Easy access to job logs for debugging
- **User configuration** - Persistent configuration for account, partition, and environment defaults

## Quick Start

```bash
# Configure your account and defaults (optional but recommended)
clserve config

# Download a model (optional - models can be auto-downloaded on first serve)
clserve download deepseek-v3

# Serve a model using predefined config
clserve serve deepseek-v3

# Check status of all clserve jobs (shows worker loading stages)
clserve status

# Get the endpoint URL by model name
clserve url deepseek-v3

# View logs
clserve logs deepseek-v3

# Stop the serving job by model name
clserve stop deepseek-v3
```

## Commands

### `clserve config`

Configure clserve defaults. Configuration is stored in `~/.clserve/config.yaml`.

```bash
# Show current configuration
clserve config --show

# Set cluster account
clserve config --account myproject

# Set multiple values
clserve config --partition normal --time-limit 08:00:00

# Interactive configuration (prompts for each value)
clserve config
```

**Options:**
- `--show, -s`: Show current configuration
- `--account, -a`: Set cluster account
- `--partition, -p`: Set default SLURM partition
- `--environment, -e`: Set default container environment
- `--router-environment`: Set router container environment
- `--time-limit, -t`: Set default time limit (HH:MM:SS)

**Configuration file format (`~/.clserve/config.yaml`):**

```yaml
account: myproject
partition: normal
environment: sglang_gb200
router_environment: sglang_router
time_limit: "04:00:00"
```

### `clserve serve`

Start serving a model.

```bash
# Serve with predefined configuration
clserve serve deepseek-v3
clserve serve llama-405b
clserve serve qwen3-235b

# Serve with multiple workers
clserve serve deepseek-v3 --workers 2 --use-router

# Serve a custom model
clserve serve my-org/my-model --tp-size 4 --nodes-per-worker 1

# Serve a small model with 4 instances per node
clserve serve llama-8b --num-gpus-per-worker 1 --use-router
```

**Options:**
- `--workers, -w`: Number of workers (default: 1)
- `--nodes-per-worker, -n`: Nodes per worker (default: 1)
- `--partition, -p`: SLURM partition (default: normal)
- `--environment, -e`: Container environment (default: sglang_gb200)
- `--tp-size`: Tensor parallel size (default: 1)
- `--dp-size`: Data parallel size (default: 1)
- `--ep-size`: Expert parallel size (default: 1)
- `--num-gpus-per-worker`: GPUs per worker process (1, 2, or 4)
- `--cuda-graph-max-bs`: Max batch size for CUDA graphs (default: 256)
- `--grammar-backend`: Grammar backend (default: llguidance)
- `--reasoning-parser`: Reasoning parser module (for reasoning models)
- `--use-router/--no-router`: Enable load balancer router
- `--router-policy`: Router policy (cache_aware, random, round_robin)
- `--router-environment`: Router container environment (default: sglang_router)
- `--time-limit, -t`: Job time limit in HH:MM:SS (default: 04:00:00)

### `clserve status`

Show status of serving jobs with detailed worker loading information.

```bash
# Show all running jobs
clserve status

# Show status for a specific job
clserve status 12345

# Show status for jobs serving a model
clserve status deepseek-v3
```

The status command displays:
- Job state (RUNNING, PENDING, etc.)
- Worker loading stages (INITIALIZING → LOADING WEIGHTS → CAPTURING CUDA GRAPH → READY)
- Model information and endpoint URLs
- Router status (when enabled)

### `clserve url`

Get the endpoint URL for a serving job by model name.
If multiple jobs are serving the same model, you'll be prompted to select one.

```bash
# Get URL by model name
clserve url deepseek-v3

# Get URL by full model path
clserve url deepseek-ai/DeepSeek-V3.1
```

### `clserve stop`

Stop serving jobs by model name.
If multiple jobs are serving the same model, you'll be prompted to select one.

```bash
# Stop by model name (selector if multiple)
clserve stop deepseek-v3

# Stop all jobs for a model
clserve stop deepseek-v3 --all

# Stop all running jobs
clserve stop --all
```

### `clserve models`

List available predefined model configurations.

```bash
clserve models
```

### `clserve logs`

Get the log file path for a job by model name.
If multiple jobs are serving the same model, you'll be prompted to select one.
Logs are stored in `~/.clserve/logs/<job_id>/`.

```bash
clserve logs deepseek-v3
tail -f $(clserve logs deepseek-v3)/log.out
```

### `clserve download`

Download a model from HuggingFace Hub to the cluster.

```bash
# Download using alias
clserve download deepseek-v3

# Download using full model path
clserve download meta-llama/Llama-3.1-70B-Instruct

# Download specific revision
clserve download deepseek-v3 --revision main
```

**Options:**
- `--revision, -r`: Specific model revision/branch to download

## Predefined Model Configurations

The following models have optimized configurations:

| Alias | Model | TP Size | Nodes/Worker | Description |
|-------|-------|---------|--------------|-------------|
| deepseek-v3 | deepseek-ai/DeepSeek-V3.1 | 16 | 4 | DeepSeek V3.1 MoE (FP8) |
| deepseek-v3.2 | deepseek-ai/DeepSeek-V3.2 | 16 | 4 | DeepSeek V3.2 - 4 workers, 4 nodes each |
| deepseek-r1 | deepseek-ai/DeepSeek-R1 | 16 | 4 | DeepSeek R1 reasoning model |
| llama-405b | meta-llama/Llama-3.1-405B-Instruct | 16 | 4 | Llama 3.1 405B |
| llama-70b | meta-llama/Llama-3.1-70B-Instruct | 4 | 1 | Llama 3.1 70B |
| llama-8b | meta-llama/Llama-3.1-8B-Instruct | 1 | 1 | Llama 3.1 8B (4x per node) |
| qwen3-235b | Qwen/Qwen3-235B-A22B-Instruct-2507 | 8 | 2 | Qwen3 235B MoE |
| qwen3-coder-480b | Qwen/Qwen3-Coder-480B-A35B-Instruct | 16 | 4 | Qwen3 Coder 480B MoE |
| qwen3-32b | Qwen/Qwen3-32B | 2 | 1 | Qwen3 32B (2x per node) |
| qwen3-8b | Qwen/Qwen3-8B | 1 | 1 | Qwen3 8B (4x per node) |
| qwen3-embedding-4b | Qwen/Qwen3-Embedding-4B | 1 | 1 | Qwen3 Embedding 4B (4x per node) |
| apertus-8b | swiss-ai/Apertus-8B-Instruct-2509 | 1 | 1 | Apertus 8B (4x per node) |
| gpt-oss-120b | openai/gpt-oss-120b | 4 | 1 | OpenAI GPT-OSS 120B - 4 workers |
| minimax-m2 | MiniMaxAI/MiniMax-M2 | 8 | 2 | MiniMax M2 - 4 workers, 2 nodes each |
| kimi-k2 | moonshotai/Kimi-K2-Instruct-0905 | 16 | 4 | Kimi K2 Instruct - 4 workers |

## Examples

### Serve DeepSeek V3 with default config

```bash
clserve serve deepseek-v3
```

This will:
- Use 4 nodes with TP=16
- Start the model on the cluster
- Print the job ID and endpoint URL instructions

### Serve with multiple workers and router

```bash
clserve serve deepseek-v3 --workers 2 --use-router
```

This doubles capacity with load balancing.

### Serve a small model efficiently

```bash
clserve serve llama-8b
```

Predefined config runs 4 instances per node with a router for high throughput.

### Full workflow example

```bash
# Start serving
clserve serve deepseek-v3
# Output: Job ID: 12345

# Wait for startup, then get URL
clserve url 12345
# Output: http://10.0.0.1:30000

# Use the API
curl http://10.0.0.1:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-ai/DeepSeek-V3.1", "messages": [{"role": "user", "content": "Hello!"}]}'

# When done, stop the job
clserve stop 12345
```

## Architecture

clserve unifies single-node and multi-node deployments into a single template:

- **Single node, full GPU**: `--nodes-per-worker 1 --num-gpus-per-worker 4`
- **Multi-node distributed**: `--nodes-per-worker 4 --tp-size 16`
- **Multiple instances per node**: `--num-gpus-per-worker 1 --use-router`

The router is automatically configured when needed for load balancing across multiple worker processes.
