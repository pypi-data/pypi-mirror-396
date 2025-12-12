# GPU Stats CLI

A beautiful, nvtop-inspired terminal UI for monitoring NVIDIA GPU metrics with intelligent bottleneck analysis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

- **Real-time GPU Monitoring** - Live metrics from `nvidia-smi`
- **Bottleneck Detection** - Automatically identifies memory-bound vs compute-bound workloads
- **Beautiful Terminal UI** - Clean, informative interface built with Rich
- **Multiple View Modes** - Single GPU or grid view for multiple GPUs
- **Historical Trends** - 60-second sparkline graphs for all metrics
- **Interactive Controls** - Keyboard navigation and togglable details
- **Demo Mode** - Test the interface with simulated GPU data

## Metrics Displayed

- **VRAM Usage** - Memory consumption with historical trend
- **Memory Bandwidth** - Data transfer speed (TB/s)
- **Compute Utilization** - Tensor/CUDA core usage (TFLOP/s)
- **Temperature & Power** - Real-time thermal and power draw
- **Bottleneck Analysis** - Identifies performance limitations with suggestions

## Installation

### From PyPI (once published)

```bash
pip install gpu-stats-cli
```

### From Source

```bash
git clone https://github.com/yourusername/gpu-stats-cli.git
cd gpu-stats-cli
pip install -e .
```

## Requirements

- Python 3.8 or higher
- NVIDIA GPU with drivers installed (for real monitoring)
- `nvidia-smi` in PATH (usually comes with NVIDIA drivers)

## Usage

### Monitor Real GPUs

```bash
gpu-stats
```

### Demo Mode (No GPU Required)

```bash
gpu-stats --demo
```

This runs a simulation with three GPUs showing different workload patterns:
- **GPU 0**: LLM inference (memory-bound with periodic spikes)
- **GPU 1**: Training workload (compute-bound, steady)
- **GPU 2**: Balanced workload

### Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit |
| `g` | Toggle grid/single view |
| `b` | Toggle bottleneck details |
| `←` or `p` | Previous GPU (single view) |
| `→` or `n` | Next GPU (single view) |

## Understanding Bottlenecks

### Memory-Bound
Your GPU's tensor cores are waiting for data from HBM (High Bandwidth Memory). Common in:
- LLM inference (autoregressive decoding)
- Small batch sizes
- Memory-intensive operations

**Suggestions:**
- Increase batch size
- Enable continuous batching
- Use KV cache optimization

### Compute-Bound
Your GPU's compute units are fully utilized. This typically means:
- Well-optimized workload
- Large batch sizes
- Compute-heavy operations (e.g., training)

## Example Output

### Single GPU View
```
                              GPU 1/3

╭──────────────────────────────────────────────────────────────────────────────╮
│ GPU 0  NVIDIA A100-SXM4-80GB                                   67°C  324W    │
│                                                                              │
│ MEMORY                                                                       │
│ ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│ VRAM                                                                         │
│                                                                              │
│ ████████████████████████░░░░░░░░ 78.0% | 62.4/80 GB                         │
│ ⣿⣿⣿⣶⣦⣤⣤⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀                                                 │
│ 60s                          now                                            │
│                                                                              │
│ THROUGHPUT                                                                   │
│ ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│ Memory Bandwidth                                                             │
│ Speed of data transfer between HBM and processors                           │
│                                                                              │
│ ████████████████████████░░░░░░░░ 78.0% | 1.59/2.04 TB/s                     │
│ ⣿⣿⣿⣿⣶⣦⣤⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀                                               │
│ 60s                          now                                            │
│                                                                              │
│ Compute                                                                      │
│ Utilization of tensor cores and CUDA cores                                  │
│                                                                              │
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░ 28.0% | 87/312 TFLOP/s                     │
│ ⣿⣿⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀                                               │
│ 60s                          now                                            │
│                                                                              │
│ ● MEMORY BOUND (78% mem, 28% compute)  [Press 'b' for details]             │
╰──────────────────────────────────────────────────────────────────────────────╯

        g: Grid View  |  b: Toggle Details  |  q: Quit
```

### Grid View
Shows all GPUs side-by-side in a compact layout, perfect for monitoring multiple GPUs simultaneously.

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/gpu-stats-cli.git
cd gpu-stats-cli
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black gpu_stats/
ruff check gpu_stats/
```

## Architecture

- `gpu_stats/components.py` - Reusable UI components (sparklines, progress bars, displays)
- `gpu_stats/monitor.py` - Real GPU monitoring using nvidia-smi
- `gpu_stats/demo.py` - Simulated GPU data for testing/demo
- `gpu_stats/cli.py` - Command-line interface and entry point

## License

MIT License - see LICENSE file for details

## Author

Shikhar Gupta

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Inspired by [nvtop](https://github.com/Syllo/nvtop) - an excellent ncurses-based GPU monitor.
