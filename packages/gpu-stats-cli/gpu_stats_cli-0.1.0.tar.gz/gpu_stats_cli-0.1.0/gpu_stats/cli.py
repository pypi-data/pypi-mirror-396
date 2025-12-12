#!/usr/bin/env python3
"""
Command-line interface for GPU Stats
"""
import sys
import argparse


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GPU Stats - Beautiful terminal UI for NVIDIA GPU monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gpu-stats              # Monitor real GPUs
  gpu-stats --demo       # Run demo with simulated data
  gpu-stats --help       # Show this help message

Controls:
  q              Quit
  g              Toggle grid/single view
  b              Toggle bottleneck details
  ← / p          Previous GPU (single view)
  → / n          Next GPU (single view)
        """
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with simulated GPU data'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )

    args = parser.parse_args()

    if args.demo:
        from gpu_stats.demo import main as demo_main
        demo_main()
    else:
        from gpu_stats.monitor import main as monitor_main
        try:
            monitor_main()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            print("\nTip: Run 'gpu-stats --demo' to try the demo mode", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
