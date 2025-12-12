#!/usr/bin/env python3
"""
Demo script for GPU Monitor CLI - Python Version
Shows the enhanced nvtop-style design with mock data
"""
import random
import sys
import termios
import tty
import select
import time
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.columns import Columns
from rich.align import Align
from .components import EnhancedGPUDisplay


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


class DynamicGPUSimulator:
    """Simulates realistic GPU behavior with fluctuating metrics"""

    def __init__(self):
        # Base configurations for different GPUs
        self.gpu_configs = [
            {
                'index': 0,
                'name': 'NVIDIA A100-SXM4-80GB',
                'memory_total_gb': 80.0,
                'bandwidth_max': 2.04,
                'compute_max': 312,
                'base_memory_percent': 78.0,
                'base_bandwidth_percent': 78.0,
                'base_compute_percent': 28.0,
                'base_temperature': 67,
                'base_power': 324,
                'scenario': 'inference'  # LLM inference pattern
            },
            {
                'index': 1,
                'name': 'NVIDIA A100-SXM4-80GB',
                'memory_total_gb': 80.0,
                'bandwidth_max': 2.04,
                'compute_max': 312,
                'base_memory_percent': 56.5,
                'base_bandwidth_percent': 42.0,
                'base_compute_percent': 92.0,
                'base_temperature': 72,
                'base_power': 298,
                'scenario': 'training'  # Training pattern
            },
            {
                'index': 2,
                'name': 'NVIDIA A100-SXM4-80GB',
                'memory_total_gb': 80.0,
                'bandwidth_max': 2.04,
                'compute_max': 312,
                'base_memory_percent': 48.4,
                'base_bandwidth_percent': 55.0,
                'base_compute_percent': 54.0,
                'base_temperature': 65,
                'base_power': 245,
                'scenario': 'balanced'  # Balanced workload
            }
        ]
        self.iteration = 0

    def _add_variance(self, base_value, variance_pct, min_val=0, max_val=100):
        """Add random variance to a base value"""
        variance = base_value * variance_pct * (random.random() - 0.5) * 2
        return max(min_val, min(max_val, base_value + variance))

    def _simulate_inference_pattern(self, base_compute, iteration):
        """Simulate LLM inference: periodic spikes when processing requests"""
        # Create request bursts every ~10 iterations
        if iteration % 10 < 3:  # Processing request
            spike = random.uniform(15, 35)  # Spike during token generation
        else:  # Idle or prefill
            spike = random.uniform(-5, 10)
        return max(5, min(100, base_compute + spike))

    def _simulate_training_pattern(self, base_compute, iteration):
        """Simulate training: steady high compute with small fluctuations"""
        variance = random.uniform(-5, 5)
        return max(80, min(100, base_compute + variance))

    def get_current_state(self):
        """Get current GPU states with realistic fluctuations"""
        gpus = []

        for config in self.gpu_configs:
            # Simulate different patterns based on scenario
            if config['scenario'] == 'inference':
                compute_percent = self._simulate_inference_pattern(
                    config['base_compute_percent'], self.iteration
                )
                # Memory bandwidth spikes with compute during inference
                bandwidth_percent = self._add_variance(
                    config['base_bandwidth_percent'], 0.30
                )
                memory_percent = self._add_variance(
                    config['base_memory_percent'], 0.15  # More visible VRAM changes
                )
            elif config['scenario'] == 'training':
                compute_percent = self._simulate_training_pattern(
                    config['base_compute_percent'], self.iteration
                )
                # Training has more stable bandwidth
                bandwidth_percent = self._add_variance(
                    config['base_bandwidth_percent'], 0.25
                )
                memory_percent = self._add_variance(
                    config['base_memory_percent'], 0.20
                )
            else:  # balanced
                compute_percent = self._add_variance(
                    config['base_compute_percent'], 0.30
                )
                bandwidth_percent = self._add_variance(
                    config['base_bandwidth_percent'], 0.30
                )
                memory_percent = self._add_variance(
                    config['base_memory_percent'], 0.25
                )

            # Temperature and power correlate with compute
            temp_variance = (compute_percent - config['base_compute_percent']) * 0.1
            temperature = int(config['base_temperature'] + temp_variance + random.uniform(-2, 2))

            power_variance = (compute_percent - config['base_compute_percent']) * 2
            power_draw = int(config['base_power'] + power_variance + random.uniform(-10, 10))

            # Calculate derived values
            memory_used_gb = (memory_percent / 100) * config['memory_total_gb']
            bandwidth_current = (bandwidth_percent / 100) * config['bandwidth_max']
            compute_current = int((compute_percent / 100) * config['compute_max'])

            # Determine bottleneck
            is_memory_bound = bandwidth_percent > 60 and bandwidth_percent > compute_percent * 1.5
            is_compute_bound = compute_percent > 60 and compute_percent > bandwidth_percent * 1.5

            if is_memory_bound:
                bottleneck_cause = 'Likely autoregressive decoding or small batch size'
                bottleneck_suggestion = 'Increase batch size or enable continuous batching'
            elif is_compute_bound:
                bottleneck_cause = 'High compute utilization with low memory usage'
                bottleneck_suggestion = 'Workload appears well-optimized'
            else:
                bottleneck_cause = 'Balanced or low utilization'
                bottleneck_suggestion = 'Monitor workload characteristics'

            gpu = {
                'index': config['index'],
                'name': config['name'],
                'temperature': temperature,
                'power_draw': power_draw,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': config['memory_total_gb'],
                'memory_percent': memory_percent,
                'bandwidth_percent': bandwidth_percent,
                'bandwidth_current': bandwidth_current,
                'bandwidth_max': config['bandwidth_max'],
                'compute_percent': compute_percent,
                'compute_current': compute_current,
                'compute_max': config['compute_max'],
                'is_memory_bound': is_memory_bound,
                'is_compute_bound': is_compute_bound,
                'bottleneck_cause': bottleneck_cause,
                'bottleneck_suggestion': bottleneck_suggestion
            }
            gpus.append(gpu)

        self.iteration += 1
        return gpus


def render_display(console, display, gpus, current_gpu_index, show_grid, histories, show_bottleneck_details):
    """Render the display for single or grid view"""
    renderables = []

    if show_grid:
        # Grid view - side by side
        # No header in grid view
        renderables.append("")

        # Render all GPU panels in compact mode
        all_gpu_panels = []
        for i, gpu in enumerate(gpus):
            main_panel, bottleneck_panel = display.render(
                gpu_index=gpu['index'],
                gpu_name=gpu['name'],
                temperature=gpu['temperature'],
                power_draw=gpu['power_draw'],
                memory_used_gb=gpu['memory_used_gb'],
                memory_total_gb=gpu['memory_total_gb'],
                memory_percent=gpu['memory_percent'],
                memory_history=histories[i]['memory'],
                bandwidth_percent=gpu['bandwidth_percent'],
                bandwidth_current=gpu['bandwidth_current'],
                bandwidth_max=gpu['bandwidth_max'],
                bandwidth_history=histories[i]['bandwidth'],
                compute_percent=gpu['compute_percent'],
                compute_current=gpu['compute_current'],
                compute_max=gpu['compute_max'],
                compute_history=histories[i]['compute'],
                is_memory_bound=gpu['is_memory_bound'],
                is_compute_bound=gpu['is_compute_bound'],
                bottleneck_cause=gpu['bottleneck_cause'],
                bottleneck_suggestion=gpu['bottleneck_suggestion'],
                compact=True,  # Use compact mode for grid view
                show_bottleneck_details=False  # No details in grid view
            )
            # In compact mode, bottleneck is embedded, so no separate panel
            all_gpu_panels.append(main_panel)

        # Create rows with 2 GPUs per row (quadrant layout)
        for i in range(0, len(all_gpu_panels), 2):
            row_panels = all_gpu_panels[i:i+2]
            renderables.append(Columns(row_panels, equal=True, expand=True))
            if i + 2 < len(all_gpu_panels):  # Add spacing between rows
                renderables.append("")
        renderables.append("")
        footer = Text("g: Single GPU View  |  q: Quit", style="dim", justify="center")
        renderables.append(footer)
    else:
        # Single GPU view - centered
        # No header, just GPU counter if multiple GPUs
        if len(gpus) > 1:
            header = Text(f"GPU {current_gpu_index + 1}/{len(gpus)}", style="dim")
            renderables.append(Align.center(header))
        renderables.append("")

        gpu = gpus[current_gpu_index]
        main_panel, bottleneck_panel = display.render(
            gpu_index=gpu['index'],
            gpu_name=gpu['name'],
            temperature=gpu['temperature'],
            power_draw=gpu['power_draw'],
            memory_used_gb=gpu['memory_used_gb'],
            memory_total_gb=gpu['memory_total_gb'],
            memory_percent=gpu['memory_percent'],
            memory_history=histories[current_gpu_index]['memory'],
            bandwidth_percent=gpu['bandwidth_percent'],
            bandwidth_current=gpu['bandwidth_current'],
            bandwidth_max=gpu['bandwidth_max'],
            bandwidth_history=histories[current_gpu_index]['bandwidth'],
            compute_percent=gpu['compute_percent'],
            compute_current=gpu['compute_current'],
            compute_max=gpu['compute_max'],
            compute_history=histories[current_gpu_index]['compute'],
            is_memory_bound=gpu['is_memory_bound'],
            is_compute_bound=gpu['is_compute_bound'],
            bottleneck_cause=gpu['bottleneck_cause'],
            bottleneck_suggestion=gpu['bottleneck_suggestion'],
            show_bottleneck_details=show_bottleneck_details
        )
        renderables.append(Align.center(main_panel))

        renderables.append("")
        if len(gpus) > 1:
            footer = Text("← / p: Previous GPU  |  → / n: Next GPU  |  g: Grid View  |  b: Toggle Details  |  q: Quit", style="dim", justify="center")
        else:
            footer = Text("g: Grid View  |  b: Toggle Details  |  q: Quit", style="dim", justify="center")
        renderables.append(footer)

    return Group(*renderables)


def main():
    console = Console()
    display = EnhancedGPUDisplay(console)

    # Create dynamic GPU simulator
    simulator = DynamicGPUSimulator()
    gpus = simulator.get_current_state()

    # Create history data structures for each GPU
    histories = [
        {
            'memory': [],
            'bandwidth': [],
            'compute': []
        }
        for gpu in gpus
    ]

    current_gpu_index = 0
    show_grid = False
    show_bottleneck_details = False

    try:
        with KeyboardListener() as kb:
            with Live(console=console, refresh_per_second=4) as live:
                while True:
                    # Check for keyboard input
                    key = kb.get_key(timeout=0)
                    if key:
                        if key in ('q', '\x03'):  # q or Ctrl+C
                            break
                        elif key in ('n', 'right'):
                            # Next GPU
                            current_gpu_index = (current_gpu_index + 1) % len(gpus)
                        elif key in ('p', 'left'):
                            # Previous GPU
                            current_gpu_index = (current_gpu_index - 1) % len(gpus)
                        elif key == 'g':
                            # Toggle grid view
                            show_grid = not show_grid
                        elif key == 'b':
                            # Toggle bottleneck details
                            show_bottleneck_details = not show_bottleneck_details

                    # Get updated GPU state from simulator
                    gpus = simulator.get_current_state()

                    # Update histories
                    for i, gpu in enumerate(gpus):
                        histories[i]['memory'].append(gpu['memory_percent'])
                        histories[i]['bandwidth'].append(gpu['bandwidth_percent'])
                        histories[i]['compute'].append(gpu['compute_percent'])

                        # Keep only last 30 data points
                        for key in ['memory', 'bandwidth', 'compute']:
                            if len(histories[i][key]) > 30:
                                histories[i][key] = histories[i][key][-30:]

                    # Render the display
                    output = render_display(console, display, gpus, current_gpu_index, show_grid, histories, show_bottleneck_details)
                    live.update(output)

                    # Small delay (500ms to see fluctuations)
                    time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    console.print("\n[yellow]Demo stopped[/yellow]")


if __name__ == "__main__":
    main()
