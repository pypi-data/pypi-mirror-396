"""
UI Components for GPU Monitor CLI
"""
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table


class Sparkline:
    """Sparkline component for displaying historical data trends"""

    # Use braille-like dots for htop-style rendering
    CHARS = ['⠀', '⣀', '⣄', '⣤', '⣦', '⣶', '⣷', '⣿']

    @staticmethod
    def render(data: List[float], width: int = 30, max_value: float = 100.0) -> str:
        """
        Render sparkline from data points using htop-style dots

        Args:
            data: List of values (0-100)
            width: Width of the sparkline
            max_value: Maximum value for normalization

        Returns:
            String with sparkline characters
        """
        if not data:
            return '⠀' * width

        # Normalize data to width
        normalized_data = data[-width:] if len(data) > width else data

        # Pad with zeros if needed
        while len(normalized_data) < width:
            normalized_data.insert(0, 0)

        # Convert to sparkline characters
        sparkline = ''
        for value in normalized_data:
            normalized = max(0, min(max_value, value))
            index = int((normalized / max_value) * (len(Sparkline.CHARS) - 1))
            sparkline += Sparkline.CHARS[index]

        return sparkline


class ProgressBar:
    """Progress bar component with percentage and label"""

    @staticmethod
    def render(percentage: float, width: int = 30, label: str = "") -> Text:
        """
        Render a progress bar

        Args:
            percentage: Percentage value (0-100)
            width: Width of the progress bar
            label: Optional label to show after percentage

        Returns:
            Rich Text object with the progress bar
        """
        filled = int((percentage / 100) * width)
        empty = width - filled

        bar = Text()
        bar.append('█' * filled, style="green")
        bar.append('░' * empty, style="dim")
        bar.append(f" {percentage:.1f}%")

        if label:
            bar.append(f" | {label}")

        return bar


class EnhancedGPUDisplay:
    """Enhanced GPU display component with nvtop-inspired design"""

    def __init__(self, console: Console = None):
        self.console = console or Console()

    def render(
        self,
        gpu_index: int,
        gpu_name: str,
        temperature: int,
        power_draw: int,
        memory_used_gb: float,
        memory_total_gb: float,
        memory_percent: float,
        memory_history: List[float],
        bandwidth_percent: float,
        bandwidth_current: float,
        bandwidth_max: float,
        bandwidth_history: List[float],
        compute_percent: float,
        compute_current: int,
        compute_max: int,
        compute_history: List[float],
        is_memory_bound: bool = False,
        is_compute_bound: bool = False,
        bottleneck_cause: str = "",
        bottleneck_suggestion: str = "",
        compact: bool = False,
        show_bottleneck_details: bool = False
    ) -> Panel:
        """
        Render the complete GPU display

        Returns:
            Rich Panel with the GPU information
        """
        content = Text()

        # Header (need to format this differently for proper alignment)
        content.append(f"GPU {gpu_index}", style="bold green")
        content.append(f"  {gpu_name}")
        # Calculate spaces needed to right-align the temperature/power
        spaces_needed = 76 - len(f"GPU {gpu_index}  {gpu_name}") - len(f"{temperature}°C  {power_draw}W")
        content.append(" " * max(1, spaces_needed))
        content.append(f"{temperature}°C  {power_draw}W")
        content.append("\n\n")

        # Memory Section
        content.append("MEMORY\n", style="bold")
        content.append("─" * 76, style="dim")
        content.append("\n\n")
        content.append("VRAM\n")
        content.append("\n")
        content.append(ProgressBar.render(
            memory_percent,
            width=30,
            label=f"{memory_used_gb:.1f}/{memory_total_gb:.0f} GB"
        ))
        if not compact:
            content.append("\n")
            sparkline = Sparkline.render(memory_history, width=30)
            content.append(sparkline, style="dim")
            content.append("\n")
            # Labels below the sparkline in very small dim text
            from rich.text import Text as RichText
            label_60s = RichText("60s")
            label_60s.stylize("dim", 0, 3)
            label_now = RichText("now")
            label_now.stylize("dim", 0, 3)
            content.append(label_60s)
            content.append(" " * 26)
            content.append(label_now)
        content.append("\n\n\n")

        # Throughput Section
        content.append("THROUGHPUT\n", style="bold")
        content.append("─" * 76, style="dim")
        content.append("\n\n")

        # Memory Bandwidth
        content.append("Memory Bandwidth\n")
        if not compact:
            content.append("Speed of data transfer between HBM and processors\n", style="dim")
        content.append("\n")
        content.append(ProgressBar.render(
            bandwidth_percent,
            width=30,
            label=f"{bandwidth_current:.2f}/{bandwidth_max:.2f} TB/s"
        ))
        if not compact:
            content.append("\n")
            sparkline = Sparkline.render(bandwidth_history, width=30)
            content.append(sparkline, style="dim")
            content.append("\n")
            # Labels below the sparkline in very small dim text
            from rich.text import Text as RichText
            label_60s = RichText("60s")
            label_60s.stylize("dim", 0, 3)
            label_now = RichText("now")
            label_now.stylize("dim", 0, 3)
            content.append(label_60s)
            content.append(" " * 26)
            content.append(label_now)
        content.append("\n\n")

        # Compute
        content.append("Compute\n")
        if not compact:
            content.append("Utilization of tensor cores and CUDA cores\n", style="dim")
        content.append("\n")
        content.append(ProgressBar.render(
            compute_percent,
            width=30,
            label=f"{compute_current}/{compute_max} TFLOP/s"
        ))
        if not compact:
            content.append("\n")
            sparkline = Sparkline.render(compute_history, width=30)
            content.append(sparkline, style="dim")
            content.append("\n")
            # Labels below the sparkline in very small dim text
            from rich.text import Text as RichText
            label_60s = RichText("60s")
            label_60s.stylize("dim", 0, 3)
            label_now = RichText("now")
            label_now.stylize("dim", 0, 3)
            content.append(label_60s)
            content.append(" " * 26)
            content.append(label_now)
        content.append("\n\n")

        # Bottleneck Analysis - Compact version embedded in panel
        bottleneck_panel = None
        if is_memory_bound or is_compute_bound:
            if compact:
                # Compact mode: show bottleneck inline
                if is_memory_bound:
                    content.append("● MEMORY BOUND ", style="bold red1")
                    content.append(f"({bandwidth_percent:.0f}% mem, {compute_percent:.0f}% compute)\n", style="red1")
                else:
                    content.append("● COMPUTE BOUND ", style="bold red1")
                    content.append(f"({compute_percent:.0f}% compute, {bandwidth_percent:.0f}% mem)\n", style="red1")
            else:
                # Full mode: show compact status, expand details if requested
                if is_memory_bound:
                    content.append("● MEMORY BOUND ", style="bold red1")
                    content.append(f"({bandwidth_percent:.0f}% mem, {compute_percent:.0f}% compute)", style="red1")
                else:
                    content.append("● COMPUTE BOUND ", style="bold red1")
                    content.append(f"({compute_percent:.0f}% compute, {bandwidth_percent:.0f}% mem)", style="red1")

                content.append("  ", style="dim")
                content.append("[Press 'b' for details]", style="dim")
                content.append("\n")

                # Show details if toggled on
                if show_bottleneck_details:
                    content.append("\n")
                    indent = "  "  # Two spaces for indentation
                    if is_memory_bound:
                        content.append(f"{indent}Memory bandwidth is at {bandwidth_percent:.1f}% while compute is at {compute_percent:.1f}%.\n", style="dim")
                        content.append(f"{indent}Tensor cores are waiting on data from HBM.\n", style="dim")
                    else:
                        content.append(f"{indent}Compute is at {compute_percent:.1f}% while memory bandwidth is at {bandwidth_percent:.1f}%.\n", style="dim")
                        content.append(f"{indent}Memory bandwidth is underutilized.\n", style="dim")

                    content.append("\n")
                    content.append(f"{indent}Cause    ", style="bold dim")
                    content.append(f"{bottleneck_cause}\n", style="dim")
                    content.append(f"{indent}Suggest  ", style="bold dim")
                    content.append(f"{bottleneck_suggestion}\n", style="dim")

        # Create main panel
        # In compact mode (grid view), expand to fill column
        # In full mode (single view), use fixed width for center alignment
        panel = Panel(
            content,
            border_style="dim",
            padding=(0, 1),
            expand=compact,
            width=80 if not compact else None
        )

        return panel, (bottleneck_panel if (is_memory_bound or is_compute_bound) else None)
