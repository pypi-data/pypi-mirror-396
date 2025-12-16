import argparse
import asyncio
import sys
from jsmon.core.engine import analyze_orchestrate
from jsmon.config.constants import DEFAULT_BATCH_SIZE

def build_parser():
    p = argparse.ArgumentParser(description="Production-ready JS Analyzer with batch processing and content deduplication.")
    p.add_argument("-i", "--input", required=True, help="Input file with base URLs.")
    p.add_argument("--redis-host", default="localhost", help="Redis server host.")
    p.add_argument("--redis-port", type=int, default=6379, help="Redis server port.")
    p.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Number of JS files to process per batch for checkpoint processing.")
    p.add_argument("--threads", type=int, default=3, help="Number of concurrent analyzer workers per batch.")
    p.add_argument("--continuous", action="store_true", help="Run the script in a continuous loop.")
    p.add_argument("--max-browser-concurrency", type=int, default=1, help="Maximum simultaneous browser fetches (1-2 recommended for stability).")
    p.add_argument("--delay", type=int, default=1, help="Delay in seconds between scans in continuous mode.")
    p.add_argument("-pc", "--notify-provider-config", help="Path to the notify provider-config file (optional).")
    p.add_argument("--log-diffs", help="Path to a file to log all detected code diffs (optional).")
    p.add_argument("--debug", action="store_true", help="Enable verbose debug logging and file output.")
    
    # Authenticated scanning options
    p.add_argument("--enable-auth-mode", action="store_true", 
                   help="Enable authenticated scanning (uses stored sessions)")
    p.add_argument("--spider-max-pages", type=int, default=20,
                   help="Max pages to visit in authenticated spider (default: 20)")
    p.add_argument("--spider-max-depth", type=int, default=3,
                   help="Max depth for spider crawling (default: 3)")
    p.add_argument("--session-health-check-interval", type=int, default=43200,
                   help="Session health check interval in seconds (default: 12 hours)")
    p.add_argument("--skip-session-health-check", action="store_true",
                   help="Disable automatic session health monitoring")
    
    # AI Analysis options
    p.add_argument("--ai-provider", choices=["gemini", "groq"], help="AI Provider for diff analysis.")
    p.add_argument("--ai-api-key", help="API Key for the AI provider.")
    p.add_argument("--ai-model", help="Specific model to use (optional).")
    p.add_argument("--skip-trivial-diffs", action="store_true", default=True,
                   help="Skip trivial diffs (formatting, renames) before AI analysis (default: enabled).")
    
    return p

def main():
    args = build_parser().parse_args()
    try: import lxml
    except ImportError: print("[!] 'lxml' not found. For better performance, run: pip install lxml")
    
    try: 
        asyncio.run(analyze_orchestrate(args))
    except KeyboardInterrupt: 
        print("\n[!] Analysis interrupted by user.", file=sys.stderr)
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
