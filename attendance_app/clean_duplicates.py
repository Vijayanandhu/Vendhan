#!/usr/bin/env python3

# Script to remove duplicate routes from app.py

import re

def clean_duplicates():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into lines
    lines = content.split('\n')
    
    # Track seen routes and their line numbers
    seen_routes = {}
    lines_to_remove = set()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a route decorator
        if line.startswith('@app.route('):
            route_match = re.search(r"@app\.route\('([^']+)'", line)
            if route_match:
                route_path = route_match.group(1)
                
                # If we've seen this route before, mark for removal
                if route_path in seen_routes:
                    print(f"Found duplicate route: {route_path} at line {i+1}")
                    
                    # Mark this route and its function for removal
                    start_line = i
                    
                    # Find the end of this route function
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        
                        # Stop at next route or end of file
                        if (next_line.startswith('@app.route(') or 
                            next_line.startswith('if __name__') or
                            j == len(lines) - 1):
                            break
                        j += 1
                    
                    # Mark lines for removal
                    for k in range(start_line, j):
                        lines_to_remove.add(k)
                    
                    i = j
                    continue
                else:
                    seen_routes[route_path] = i
        
        i += 1
    
    # Remove duplicate lines
    cleaned_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    
    # Write back to file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"Removed {len(lines_to_remove)} duplicate lines")

if __name__ == '__main__':
    clean_duplicates()