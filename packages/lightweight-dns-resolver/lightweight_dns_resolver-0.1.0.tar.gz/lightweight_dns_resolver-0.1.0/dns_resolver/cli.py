import argparse
from .core import resolve

def main():
    parser = argparse.ArgumentParser(description="DNS Resolver Tool")
    parser.add_argument("domain", help="Domain or IP to resolve")
    parser.add_argument("type", help="Record type (A, MX, TXT, etc.)")
    parser.add_argument("--server", "-s", help="Custom DNS Server", default=None)
    
    args = parser.parse_args()
    
    print(f"Querying {args.type.upper()} for {args.domain}...")
    resolve(args.domain, args.type, args.server)

if __name__ == "__main__":
    main()
