import os
import re
from pathlib import Path

def parse_tree(raw_text, root_base=None):
    """
    Parses the ASCII/Unicode tree structure.
    Returns a list of actions: {'type': 'dir'|'file', 'path': Path object}
    """
    if root_base is None:
        root_base = Path.cwd()
    else:
        root_base = Path(root_base)

    lines = raw_text.split('\n')
    stack = [] 
    actions = []
    
    # Regex to capture the prefix (tree characters + indentation)
    prefix_pattern = re.compile(r'^[\s│├└─\|\+\`]*')

    for line in lines:
        if not line.strip(): continue
        # Skip headers often output by AI
        if "directory structure" in line.lower(): continue
        
        # 1. Clean comments
        clean_line = line.split(" #")[0].split(" ←")[0].strip()
        if not clean_line: continue

        # 2. Calculate depth based on prefix length
        match = prefix_pattern.match(line)
        prefix_len = len(match.group(0)) if match else 0
        
        # 3. Extract name
        item_name = line[prefix_len:].strip()
        item_name = item_name.split("  ")[0].strip() # remove inline spaces/comments
        
        if not item_name: continue
        if item_name == "│": continue 

        # 4. Determine type
        is_dir = item_name.endswith("/") or item_name.endswith("\\")
        clean_name = item_name.rstrip("/\\")

        # 5. Stack logic for nesting
        if not stack:
            # If stack empty, we are at the root of the snippet
            current_path = root_base / clean_name
            is_dir = True # Root of a tree snippet is usually a container dir
            stack.append({'indent': prefix_len, 'path': current_path})
            actions.append({'type': 'dir', 'path': current_path})
            continue

        # Pop stack until we find the parent (parent indent < current indent)
        while stack and prefix_len <= stack[-1]['indent']:
            stack.pop()
        
        parent_path = stack[-1]['path'] if stack else root_base
        current_path = parent_path / clean_name
        
        if is_dir:
            actions.append({'type': 'dir', 'path': current_path})
            stack.append({'indent': prefix_len, 'path': current_path})
        else:
            actions.append({'type': 'file', 'path': current_path})

    return actions

def execute_actions(actions, dry_run=False):
    """
    Executes the list of actions (creating dirs/files).
    Yields status strings for logging.
    """
    stats = {'dirs': 0, 'files': 0, 'skipped': 0}
    
    for action in actions:
        path = action['path']
        type_ = action['type']
        
        if dry_run:
            yield f"[PREVIEW] {type_.upper()}: {path}"
            continue

        try:
            if type_ == 'dir':
                if not path.exists():
                    os.makedirs(path)
                    stats['dirs'] += 1
                    yield f"CREATED DIR: {path}"
                else:
                    stats['skipped'] += 1
                    yield f"EXISTS:      {path}"
            
            elif type_ == 'file':
                # Ensure parent dir exists (failsafe)
                if not path.parent.exists():
                    os.makedirs(path.parent)
                
                if not path.exists():
                    path.touch() # Creates empty file
                    stats['files'] += 1
                    yield f"CREATED FILE:{path}"
                else:
                    stats['skipped'] += 1
                    yield f"EXISTS:      {path}"
                    
        except Exception as e:
            yield f"ERROR on {path}: {str(e)}"

    if not dry_run:
        yield f"--- SUMMARY: {stats['dirs']} dirs, {stats['files']} files created, {stats['skipped']} skipped. ---"