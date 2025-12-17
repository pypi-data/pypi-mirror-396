#!/usr/bin/env python3
"""
Interactive JSON viewer for network logs.

Usage:
    python network-testing/tools/view_network_log.py network-testing/logs/network-log-noi.json
"""

import json
import sys
from pathlib import Path


def pretty_print_request(req, index):
    """Pretty print a single request/response."""
    request = req['request']
    response = req['response']
    
    print(f"\n{'─' * 80}")
    print(f"Request #{index}")
    print(f"{'─' * 80}")
    print(f"URL:      {request['url']}")
    print(f"Method:   {request['method']}")
    print(f"Type:     {request['resourceType']}")
    print(f"Time:     {request['timestamp']}ms")
    
    if request.get('postData'):
        print(f"\n📤 Request Body:")
        try:
            post_data = json.loads(request['postData'])
            print(json.dumps(post_data, indent=2)[:500])  # Limit output
            if len(request['postData']) > 500:
                print("... (truncated)")
        except:
            print(request['postData'][:500])
            if len(request['postData']) > 500:
                print("... (truncated)")
    
    if response:
        print(f"\n📥 Response:")
        print(f"Status:   {response['status']} {response.get('statusText', '')}")
        print(f"Time:     {response['timestamp']}ms")
        print(f"Duration: {response['timestamp'] - request['timestamp']}ms")
        print(f"Cached:   {response.get('fromCache', False)}")
        
        if response.get('body'):
            print(f"\nResponse Body:")
            body = response['body']
            if isinstance(body, dict) or isinstance(body, list):
                body_str = json.dumps(body, indent=2)
            else:
                body_str = str(body)
            
            # Show first 1000 chars
            print(body_str[:1000])
            if len(body_str) > 1000:
                print("... (truncated)")
    else:
        print(f"\n❌ No response captured")


def interactive_viewer(log_file):
    """Interactive log viewer."""
    with open(log_file) as f:
        data = json.load(f)
    
    metadata = data['metadata']
    requests = data['requests']
    
    print(f"\n{'='*80}")
    print(f"Network Log Viewer")
    print(f"{'='*80}")
    print(f"File:     {log_file}")
    print(f"Site:     {metadata['testSite']}")
    print(f"Time:     {metadata['timestamp']}")
    print(f"Requests: {metadata['totalRequests']}")
    print(f"Duration: {metadata['duration']}ms")
    print(f"{'='*80}")
    
    while True:
        print("\n\nCommands:")
        print("  [number]  - View request by index (0-{})".format(len(requests)-1))
        print("  list      - List all requests")
        print("  api       - List only API requests")
        print("  failed    - Show failed requests")
        print("  slow      - Show slow requests (>1s)")
        print("  search    - Search in URLs")
        print("  quit      - Exit")
        
        cmd = input("\n> ").strip().lower()
        
        if cmd == 'quit' or cmd == 'q' or cmd == 'exit':
            break
        
        elif cmd == 'list':
            print("\nAll Requests:")
            for i, req in enumerate(requests):
                url = req['request']['url']
                method = req['request']['method']
                status = req['response']['status'] if req['response'] else 'N/A'
                print(f"{i:4}: {method:6} {url[:70]:70} [{status}]")
        
        elif cmd == 'api':
            print("\nAPI Requests:")
            for i, req in enumerate(requests):
                if '/api/' in req['request']['url']:
                    url = req['request']['url']
                    method = req['request']['method']
                    status = req['response']['status'] if req['response'] else 'N/A'
                    print(f"{i:4}: {method:6} {url[:70]:70} [{status}]")
        
        elif cmd == 'failed':
            print("\nFailed Requests:")
            found = False
            for i, req in enumerate(requests):
                if req['response'] and req['response']['status'] >= 400:
                    found = True
                    url = req['request']['url']
                    method = req['request']['method']
                    status = req['response']['status']
                    print(f"{i:4}: {method:6} {url[:70]:70} [{status}]")
            if not found:
                print("No failed requests found!")
        
        elif cmd == 'slow':
            print("\nSlow Requests (>1000ms):")
            found = False
            for i, req in enumerate(requests):
                if req['response']:
                    duration = req['response']['timestamp'] - req['request']['timestamp']
                    if duration > 1000:
                        found = True
                        url = req['request']['url']
                        print(f"{i:4}: {duration:6}ms - {url}")
            if not found:
                print("No slow requests found!")
        
        elif cmd == 'search':
            pattern = input("Search pattern: ").strip()
            print(f"\nRequests matching '{pattern}':")
            found = False
            for i, req in enumerate(requests):
                if pattern.lower() in req['request']['url'].lower():
                    found = True
                    url = req['request']['url']
                    method = req['request']['method']
                    status = req['response']['status'] if req['response'] else 'N/A'
                    print(f"{i:4}: {method:6} {url[:70]:70} [{status}]")
            if not found:
                print("No matches found!")
        
        elif cmd.isdigit():
            index = int(cmd)
            if 0 <= index < len(requests):
                pretty_print_request(requests[index], index)
            else:
                print(f"Invalid index! Must be 0-{len(requests)-1}")
        
        else:
            print("Unknown command!")


def main():
    if len(sys.argv) != 2:
        print("Usage: python network-testing/tools/view_network_log.py <log-file.json>")
        print("\nExample:")
        print("  python network-testing/tools/view_network_log.py network-testing/logs/network-log-noi.json")
        sys.exit(1)
    
    log_file = Path(sys.argv[1])
    
    if not log_file.exists():
        print(f"Error: File not found: {log_file}")
        sys.exit(1)
    
    try:
        interactive_viewer(log_file)
    except KeyboardInterrupt:
        print("\n\nBye!")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
