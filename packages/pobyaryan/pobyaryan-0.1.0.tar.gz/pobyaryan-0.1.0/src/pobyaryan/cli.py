# src/po_by/cli.py
import argparse
import os
from .agent import repl_loop, make_client

def main():
    parser = argparse.ArgumentParser(prog="po", description="Run the PO agent REPL")
    parser.add_argument("--api-key", help="GenAI API key (or set PO_GENAI_API_KEY env var)") # Prefer env wale varaibles n also prefer shell commands only 
    args = parser.parse_args()
    client = make_client(args.api_key)
    repl_loop(client)

if __name__ == "__main__":
    main()
