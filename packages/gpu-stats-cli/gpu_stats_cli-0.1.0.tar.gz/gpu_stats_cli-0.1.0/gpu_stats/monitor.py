#!/usr/bin/env python3
"""
Real-time GPU Monitor with NVIDIA GPU support
Requires: nvidia-smi and pynvml
"""
import time
import subprocess
import json
import sys
import termios
import tty
import select
from typing import Dict, List, Optional
from collections import deque
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.columns import Columns
from rich.align import Align
from .components import EnhancedGPUDisplay


class GPUMonitor:
    """Monitor NVIDIA GPUs using nvidia-smi"""

    def __init__(self, max_history: int = 30):
        self.max_history = max_history
        self.history: Dict[int, Dict[str, deque]] = {}

    def get_gpu_metrics(self) -> List[Dict]:
        """
        Get GPU metrics using nvidia-smi

        Returns:
            List of dictionaries with GPU metrics
        """
        try:
            result = subprocess.run(
                [
                    'nvidia-smi',
                    '--query-gpu=index,name,temperature.gpu,power.draw,power.limit,'
                    'memory.used,memory.total,utilization.gpu,utilization.memory',
                    '--format=csv,noheader,nounits'
                ],
                capture_output=True,
                text=True,
                check=True
            )

            gpus = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 9:
                    continue

                gpu = {
                    'index': int(parts[0]),
                    'name': parts[1],
                    'temperature': float(parts[2]),
                    'power_draw': float(parts[3]),
                    'power_limit': float(parts[4]),
                    'memory_used': float(parts[5]) / 1024,  # Convert to GB
                    'memory_total': float(parts[6]) / 1024,  # Convert to GB
                    'gpu_util': float(parts[7]),
                    'memory_util': float(parts[8])
                }

                gpus.append(gpu)

            return gpus

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to query GPU metrics: {e}")
        except FileNotFoundError:
            raise Exception("nvidia-smi not found. Make sure NVIDIA drivers are installed.")

    def update_history(self, gpu_index: int, memory_percent: float,
                      bandwidth_percent: float, compute_percent: float):
        """Update history for a GPU"""
        if gpu_index not in self.history:
            self.history[gpu_index] = {
                'memory': deque(maxlen=self.max_history),
                'bandwidth': deque(maxlen=self.max_history),
                'compute': deque(maxlen=self.max_history)
            }

        self.history[gpu_index]['memory'].append(memory_percent)
        self.history[gpu_index]['bandwidth'].append(bandwidth_percent)
        self.history[gpu_index]['compute'].append(compute_percent)

    def get_history(self, gpu_index: int) -> Dict[str, List[float]]:
        """Get history for a GPU"""
        if gpu_index not in self.history:
            return {
                'memory': [],
                'bandwidth': [],
                'compute': []
            }

        return {
            'memory': list(self.history[gpu_index]['memory']),
            'bandwidth': list(self.history[gpu_index]['bandwidth']),
            'compute': list(self.history[gpu_index]['compute'])
        }

    def analyze_boundedness(self, gpu: Dict) -> Dict:
        """
        Simple heuristic analysis for GPU boundedness

        Returns:
            Dictionary with analysis results
        """
        memory_util = gpu['memory_util']
        compute_util = gpu['gpu_util']

        # Simple heuristic: if memory util is significantly higher than compute
        is_memory_bound = memory_util > 60 and memory_util > compute_util * 2
        is_compute_bound = compute_util > 60 and compute_util > memory_util * 2

        result = {
            'is_memory_bound': is_memory_bound,
            'is_compute_bound': is_compute_bound,
            'memory_bandwidth_util': memory_util,
            'compute_util': compute_util
        }

        if is_memory_bound:
            result['cause'] = 'High memory utilization with low compute'
            result['suggestion'] = 'Consider optimizing data transfers or batch size'
        elif is_compute_bound:
            result['cause'] = 'High compute utilization with low memory usage'
            result['suggestion'] = 'Workload appears well-optimized'
        else:
            result['cause'] = 'Balanced or low utilization'
            result['suggestion'] = 'Monitor workload characteristics'

        return result


class KeyboardListener:
    """Non-blocking keyboard input handler"""

    def __init__(self):
        self.old_settings = None

    def __enter__(self):
        if sys.stdin.isatty():
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        if sys.stdin.isatty() and self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self, timeout=0):
        """Get a key press if available (non-blocking)"""
        if not sys.stdin.isatty():
            return None

        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            key = sys.stdin.read(1)
            # Handle arrow keys (escape sequences)
            if key == '\x1b':
                next_chars = sys.stdin.read(2)
                if next_chars == '[C':  # Right arrow
                    return 'right'
                elif next_chars == '[D':  # Left arrow
                    return 'left'
            return key
        return None


def render_gpu_data(console, monitor, display, gpus, current_gpu_index, show_grid, show_bottleneck_details):
    """Render GPU data for either single or grid view"""
    output_panels = []

    for gpu in gpus:
        # Calculate metrics
        memory_percent = (gpu['memory_used'] / gpu['memory_total']) * 100

        # Update history
        monitor.update_history(
            gpu['index'],
            memory_percent,
            gpu['memory_util'],
            gpu['gpu_util']
        )

        # Get history
        history = monitor.get_history(gpu['index'])

        # Analyze boundedness
        analysis = monitor.analyze_boundedness(gpu)

        # Mock calculations for bandwidth and compute
        bandwidth_max = 2.04  # TB/s for A100 (adjust for your GPU)
        compute_max = 312  # TFLOP/s for A100 (adjust for your GPU)

        bandwidth_current = (analysis['memory_bandwidth_util'] / 100) * bandwidth_max
        compute_current = int((analysis['compute_util'] / 100) * compute_max)

        # Render GPU display (compact mode for grid view will be set in grid rendering)
        main_panel, bottleneck_panel = display.render(
            gpu_index=gpu['index'],
            gpu_name=gpu['name'],
            temperature=int(gpu['temperature']),
            power_draw=int(gpu['power_draw']),
            memory_used_gb=gpu['memory_used'],
            memory_total_gb=gpu['memory_total'],
            memory_percent=memory_percent,
            memory_history=history['memory'],
            bandwidth_percent=analysis['memory_bandwidth_util'],
            bandwidth_current=bandwidth_current,
            bandwidth_max=bandwidth_max,
            bandwidth_history=history['bandwidth'],
            compute_percent=analysis['compute_util'],
            compute_current=compute_current,
            compute_max=compute_max,
            compute_history=history['compute'],
            is_memory_bound=analysis['is_memory_bound'],
            is_compute_bound=analysis['is_compute_bound'],
            bottleneck_cause=analysis['cause'],
            bottleneck_suggestion=analysis['suggestion'],
            compact=show_grid,  # Use compact mode when in grid view
            show_bottleneck_details=show_bottleneck_details if not show_grid else False
        )

        output_panels.append((gpu['index'], main_panel, bottleneck_panel))

    # Build the display
    renderables = []

    if show_grid:
        # Grid view - side by side
        # No header in grid view
        renderables.append("")

        # Create columns for side-by-side display (2 per row)
        # In grid view, bottleneck is embedded in panel (compact mode), so no separate bottleneck panel
        all_gpu_panels = []
        for idx, main_panel, bottleneck_panel in output_panels:
            all_gpu_panels.append(main_panel)

        # Create rows with 2 GPUs per row (quadrant layout)
        for i in range(0, len(all_gpu_panels), 2):
            row_panels = all_gpu_panels[i:i+2]
            renderables.append(Columns(row_panels, equal=True, expand=True))
            if i + 2 < len(all_gpu_panels):  # Add spacing between rows
                renderables.append("")
        renderables.append("")
        footer = Text("g: Single GPU View", style="dim", justify="center")
        renderables.append(footer)
    else:
        # Single GPU view - centered
        # No header, just GPU counter if multiple GPUs
        if len(gpus) > 1:
            header = Text(f"GPU {current_gpu_index + 1}/{len(gpus)}", style="dim")
            renderables.append(Align.center(header))
        renderables.append("")

        idx, main_panel, bottleneck_panel = output_panels[current_gpu_index]
        renderables.append(Align.center(main_panel))

        renderables.append("")
        if len(gpus) > 1:
            footer = Text("← / p: Previous GPU  |  → / n: Next GPU  |  g: Grid View  |  b: Toggle Details", style="dim", justify="center")
        else:
            footer = Text("g: Grid View  |  b: Toggle Details", style="dim", justify="center")
        renderables.append(footer)

    return Group(*renderables)


def main():
    """Main monitoring loop"""
    console = Console()
    monitor = GPUMonitor(max_history=30)
    display = EnhancedGPUDisplay(console)

    current_gpu_index = 0
    show_grid = False
    show_bottleneck_details = False

    try:
        with KeyboardListener() as kb:
            with Live(console=console, refresh_per_second=2) as live:
                while True:
                    try:
                        # Check for keyboard input
                        key = kb.get_key(timeout=0)
                        if key:
                            if key in ('q', '\x03'):  # q or Ctrl+C
                                break
                            elif key in ('n', 'right'):
                                # Next GPU
                                gpus = monitor.get_gpu_metrics()
                                if len(gpus) > 0:
                                    current_gpu_index = (current_gpu_index + 1) % len(gpus)
                            elif key in ('p', 'left'):
                                # Previous GPU
                                gpus = monitor.get_gpu_metrics()
                                if len(gpus) > 0:
                                    current_gpu_index = (current_gpu_index - 1) % len(gpus)
                            elif key == 'g':
                                # Toggle grid view
                                show_grid = not show_grid
                            elif key == 'b':
                                # Toggle bottleneck details
                                show_bottleneck_details = not show_bottleneck_details

                        # Get GPU metrics
                        gpus = monitor.get_gpu_metrics()

                        # Ensure current_gpu_index is valid
                        if current_gpu_index >= len(gpus):
                            current_gpu_index = 0

                        # Render the display
                        output = render_gpu_data(console, monitor, display, gpus, current_gpu_index, show_grid, show_bottleneck_details)
                        live.update(output)

                        # Wait before next update
                        time.sleep(2)

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                        break

    except KeyboardInterrupt:
        pass

    console.print("\n[yellow]Monitoring stopped by user[/yellow]")


if __name__ == "__main__":
    main()
