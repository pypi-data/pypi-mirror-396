"""
PrimeLLM CLI

Command-line interface for PrimeLLM SDK.

Usage:
    primellm chat "Your message here" --model gpt-5.1
    primellm credits
    primellm models
"""

import argparse
import os
import sys
import json


def main():
    parser = argparse.ArgumentParser(
        prog="primellm",
        description="PrimeLLM CLI - Interact with PrimeLLM AI API",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", help="Message to send")
    chat_parser.add_argument("--model", default="gpt-5.1", help="Model to use (default: gpt-5.1)")
    chat_parser.add_argument("--stream", action="store_true", help="Stream the response")
    
    # Credits command
    subparsers.add_parser("credits", help="Get credit balance")
    
    # Models command
    subparsers.add_parser("models", help="List available models")
    
    # Keys command
    keys_parser = subparsers.add_parser("keys", help="Manage API keys")
    keys_parser.add_argument("--list", action="store_true", help="List keys")
    keys_parser.add_argument("--create", type=str, metavar="LABEL", help="Create new key with label")
    keys_parser.add_argument("--revoke", type=int, metavar="ID", help="Revoke key by ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Import here to avoid slow startup
    from primellm import PrimeLLM
    
    api_key = os.getenv("PRIMELLM_API_KEY")
    if not api_key:
        print("Error: Set PRIMELLM_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)
    
    try:
        client = PrimeLLM(api_key=api_key)
        
        if args.command == "chat":
            if args.stream:
                for chunk in client.chat.stream(
                    model=args.model,
                    messages=[{"role": "user", "content": args.message}],
                ):
                    delta = chunk.get("delta", {})
                    content = delta.get("content", "")
                    print(content, end="", flush=True)
                print()
            else:
                response = client.chat.create(
                    model=args.model,
                    messages=[{"role": "user", "content": args.message}],
                )
                print(response["choices"][0]["message"]["content"])
        
        elif args.command == "credits":
            response = client.credits.get()
            print(f"Credits: {response['credits']}")
        
        elif args.command == "models":
            response = client.models.list()
            for model in response.get("data", []):
                print(f"  - {model['id']}: {model.get('description', '')}")
        
        elif args.command == "keys":
            if args.create:
                response = client.keys.create(args.create)
                print(f"Created key: {response['key']}")
            elif args.revoke:
                response = client.keys.revoke(args.revoke)
                print(f"Revoked key {args.revoke}")
            else:
                response = client.keys.list()
                for key in response.get("data", []):
                    status = "active" if key.get("active") else "revoked"
                    print(f"  - {key['id']}: {key.get('key_prefix', '?')}... ({status})")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
