#!/usr/bin/env python3
import os
import sys
import re

def main():
    root = "."
    audit_file = "project_audit.md"
    
    # 1. Ground Truth - File System
    ground_truth_files = set()
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, root)
            if not os.path.isfile(full_path): continue 
            # Skip the output file itself
            if os.path.abspath(full_path) == os.path.abspath(audit_file):
                continue
            # Note: We expect audit_project.py and verify_audit_completeness.py to be in the audit if they are in root
            
            ground_truth_files.add(rel_path)

    # 2. Parse Audit File
    if not os.path.exists(audit_file):
        print("FAIL: audit file not found")
        sys.exit(1)
        
    with open(audit_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract File Index Section
    # Regex for table rows: | `path` | size | ...
    # Be more strict to avoid matching headers or text
    indexed_files = set()
    # Look for lines that start with | ` and have | numbers | ...
    # This should avoid "Supported Encoding" unless it's formatted exactly like a file row
    # My audit script output: | `path` | size | Type | Modified |
    for match in re.finditer(r"^\|\s*`([^`]+)`\s*\|\s*\d+\s*\|", content, re.MULTILINE):
        indexed_files.add(match.group(1))

    # 3. Compare Index vs Ground Truth
    missing_in_audit = ground_truth_files - indexed_files
    extra_in_audit = indexed_files - ground_truth_files
    
    print(f"Total Ground Truth Files: {len(ground_truth_files)}")
    print(f"Total Indexed Files: {len(indexed_files)}")
    
    # 4. Content Block Verification (Optimized)
    # Scan content ONCE for all headers
    found_headers = set()
    for match in re.finditer(r"^### File: `(.+?)`$", content, re.MULTILINE):
        found_headers.add(match.group(1))
        
    missing_content = indexed_files - found_headers
    
    # 5. Reporting
    fail = False
    
    if missing_in_audit:
        print("FAIL: Missing files in audit index:")
        for f in sorted(missing_in_audit):
            print(f" - {f}")
        fail = True
    
    if extra_in_audit:
        print("FAIL: Extra files in audit index (ghosts?):")
        for f in sorted(extra_in_audit):
            print(f" - {f}")
        fail = True
        
    if missing_content:
        print("FAIL: Indexed files missing content blocks:")
        for f in sorted(missing_content):
            print(f" - {f}")
        fail = True

    # Check for "TRUNCATED" marker
    truncated_count = len(re.findall(r"\[TRUNCATED\]", content))
    
    # Check for binary marker
    binary_count = len(re.findall(r"Binary file content not embedded", content))

    # Check for local links
    if "file:///Users" in content:
        print("FAIL: Found local file links!")
        fail = True
    
    if not fail:
        print("PASS: Completeness Verification Successful")
        print(f"Files: {len(indexed_files)}")
        print(f"Binaries: {binary_count}")
        print(f"Truncated: {truncated_count}")
    else:
        print("FAIL: Verification Failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
