#!/usr/bin/env python3
import sys
import os
import time
import random
import re
import argparse
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_log(msg):
    # Simulated Soong log format: [  0% 0/100] Message...
    # We will be dynamic with this in the build loop
    pass

def find_android_bp_files(root_dir):
    bp_files = []
    for root, dirs, files in os.walk(root_dir):
        if "Android.bp" in files:
            bp_files.append(os.path.join(root, "Android.bp"))
    return bp_files

def parse_bp_modules(bp_file):
    modules = []
    try:
        with open(bp_file, 'r') as f:
            content = f.read()
            # Very basic regex to find module names.
            # matches: cc_library { name: "foo", ... }
            matches = re.findall(r'([a-z_]+)\s*\{[^}]*name:\s*"([^"]+)"', content, re.MULTILINE | re.DOTALL)
            for m_type, m_name in matches:
                modules.append({'name': m_name, 'type': m_type, 'path': bp_file})
    except Exception as e:
        pass
    return modules

def get_module_out_path(root_dir, m_name, m_type):
    # Simulate output path based on type
    out_base = os.path.join(root_dir, "out", "target", "product", "generic")
    if "cc" in m_type:
        return os.path.join(out_base, "system", "lib64", f"{m_name}.fake")
    elif "java" in m_type or "android" in m_type:
        return os.path.join(out_base, "system", "framework", f"{m_name}.fake")
    else:
        return os.path.join(out_base, "system", "etc", f"{m_name}.fake")

def simulate_build(targets, modules_map, root_dir):
    print(f"{Colors.OKBLUE}Run Soong UI...{Colors.ENDC}")
    time.sleep(0.5)

    # Resolve targets
    # If target is a directory, find modules in that directory
    # If target is a module name, find that module
    # If target is empty, build everything (limit to some max in simulation)
    
    build_list = []
    
    if not targets:
        # Build "all" (just a random selection of known modules to keep it sane)
        build_list = list(modules_map.values())[:20] 
        print(f"{Colors.OKBLUE}Building all modules (simulated selection)...{Colors.ENDC}")
    else:
        for t in targets:
            # Check if t is a path
            path_match = False
            for m_name, m_info in modules_map.items():
                # Check if target is a path that contains this module
                rel_path = os.path.relpath(os.path.dirname(m_info['path']), root_dir)
                if t == rel_path or t == os.path.dirname(m_info['path']):
                    build_list.append(m_info)
                    path_match = True
            
            if not path_match:
                if t in modules_map:
                    build_list.append(modules_map[t])
                else:
                    print(f"{Colors.WARNING}Target {t} not found, assuming phony target.{Colors.ENDC}")
                    build_list.append({'name': t, 'type': 'phony', 'path': 'build/make/core'})

    # Remove duplicates
    unique_build_list = []
    seen = set()
    for b in build_list:
        if b['name'] not in seen:
            unique_build_list.append(b)
            seen.add(b['name'])
    build_list = unique_build_list

    total_steps = len(build_list) * 4 # 4 steps per module
    current_step = 0
    
    start_time = time.time()
    
    # Generate build.ninja simulation
    print(f"{Colors.OKBLUE}Generating build.ninja...{Colors.ENDC}")
    time.sleep(1)
    
    print(f"{Colors.OKBLUE}Starting build with {len(build_list)} modules...{Colors.ENDC}")
    
    for module in build_list:
        m_name = module['name']
        m_type = module['type']
        
        steps = [
            f" [ 10% {current_step}/{total_steps}] // {os.path.dirname(module['path'])}:{m_name} {m_type} stub",
            f" [ 40% {current_step+1}/{total_steps}] // {os.path.dirname(module['path'])}:{m_name} {m_type} header",
            f" [ 70% {current_step+2}/{total_steps}] // {os.path.dirname(module['path'])}:{m_name} {m_type} compile",
            f" [100% {current_step+3}/{total_steps}] // {os.path.dirname(module['path'])}:{m_name} {m_type} link"
        ]
        
        for step in steps:
            current_step += 1
            # Calculate percentage
            pct = int((current_step / total_steps) * 100)
            log_line = f"[{pct:>3}% {current_step}/{total_steps}] {step.split('] ')[1]}"
            print(log_line)
            
            # Simulate compilation delay
            time.sleep(random.uniform(0.05, 0.3))
            
        # Create a fake output file
        out_full_path = get_module_out_path(root_dir, m_name, m_type)
        out_dir = os.path.dirname(out_full_path)
        os.makedirs(out_dir, exist_ok=True)
        with open(out_full_path, "w") as f:
            f.write(f"Fake binary for {m_name}\nType: {m_type}\nTimestamp: {time.time()}\n")
            
    elapsed = time.time() - start_time
    print(f"{Colors.OKGREEN}#### build completed successfully ({int(elapsed/60)}:{int(elapsed%60):02}) ####{Colors.ENDC}")

import json

def generate_module_info(modules_map, root_dir):
    module_info = {}
    for name, m in modules_map.items():
        rel_path = os.path.relpath(m['path'], root_dir)
        out_path = get_module_out_path(root_dir, name, m['type'])
        
        # Map fake type to AOSP class
        m_class = ["UNKNOWN"]
        if "cc_" in m['type']:
            if "binary" in m['type']: m_class = ["EXECUTABLES"]
            elif "library" in m['type']: m_class = ["SHARED_LIBRARIES"]
        elif "java_" in m['type']:
            m_class = ["JAVA_LIBRARIES"]
        elif "android_app" in m['type']:
            m_class = ["APPS"]
            
        module_info[name] = {
            "class": m_class,
            "path": [os.path.dirname(rel_path)],
            "tags": ["optional"],
            "installed": [out_path],
            "module_name": name
        }
    
    out_dir = os.path.join(root_dir, "out", "target", "product", "generic")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "module-info.json")
    
    with open(json_path, "w") as f:
        json.dump(module_info, f, indent=2)
    
    return json_path

def main():
    root_dir = os.environ.get("ANDROID_BUILD_TOP")
    if not root_dir:
        root_dir = os.getcwd()

    # Scan for Android.bp files
    bp_files = find_android_bp_files(root_dir)
    modules_map = {}
    for bp in bp_files:
        mods = parse_bp_modules(bp)
        for m in mods:
            modules_map[m['name']] = m

    # Always generate module-info.json as it's a common artifact needed by tools
    json_path = generate_module_info(modules_map, root_dir)

    if "--list-modules" in sys.argv:
        # User requested specific list output, but hinted they want "actual AOSP display"
        # Since AOSP doesn't have a standard CLI list, we might just print the keys 
        # or maybe they just wanted the json file.
        # But if they ran `m module-info`, it would build the json.
        print(f"Generated module info at {json_path}")
        return

    if "--query-all" in sys.argv:
        json_path = os.path.join(root_dir, "out", "target", "product", "generic", "module-info.json")
        if not os.path.exists(json_path):
            print("Module info not found. Run 'refreshmod' first.")
            return
        with open(json_path, "r") as f:
            data = json.load(f)
            for name in sorted(data.keys()):
                print(name)
        return

    if "--query-path" in sys.argv:
        idx = sys.argv.index("--query-path")
        if idx + 1 >= len(sys.argv): return
        mod_name = sys.argv[idx+1]
        json_path = os.path.join(root_dir, "out", "target", "product", "generic", "module-info.json")
        if not os.path.exists(json_path): return
        with open(json_path, "r") as f:
            data = json.load(f)
            if mod_name in data:
                # path is a list, take first
                print(os.path.join(root_dir, data[mod_name]["path"][0]))
        return

    if "--query-out" in sys.argv:
        idx = sys.argv.index("--query-out")
        if idx + 1 >= len(sys.argv): return
        mod_name = sys.argv[idx+1]
        json_path = os.path.join(root_dir, "out", "target", "product", "generic", "module-info.json")
        if not os.path.exists(json_path): return
        with open(json_path, "r") as f:
            data = json.load(f)
            if mod_name in data:
                print(data[mod_name]["installed"][0])
        return

    if "--query-dir" in sys.argv:
        idx = sys.argv.index("--query-dir")
        if idx + 1 >= len(sys.argv): return
        target_dir = sys.argv[idx+1]
        # Normalize target dir to catch relative paths or missing trailing slashes
        # The json stores paths relative to root, e.g. "prebuilts/tools"
        # We need to handle if user passes absolute path or relative path
        if os.path.isabs(target_dir):
            target_dir = os.path.relpath(target_dir, root_dir)
        
        json_path = os.path.join(root_dir, "out", "target", "product", "generic", "module-info.json")
        if not os.path.exists(json_path):
             # Fallback to scanning if json missing? Or just return
             return

        with open(json_path, "r") as f:
            data = json.load(f)
            found = False
            for name, info in data.items():
                for p in info["path"]:
                    # Exact match or subdirectory? The requirement says "defined within a specific directory"
                    # Usually dirmods checks if the module path starts with the dir
                    if p == target_dir or p.startswith(target_dir + os.sep):
                        print(name)
                        found = True
            if not found:
                pass 
        return

    targets = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    
    # Handle "all_modules" or empty targets (if we want default behavior)
    if "all_modules" in targets:
        # Build everything
        targets = [] # simulate_build treats empty targets as "build selection of modules" or we can make it build ALL
        print(f"{Colors.OKBLUE}Building all detected modules (all_modules specified)...{Colors.ENDC}")
        # To actually build ALL in simulation, we pass all keys
        targets = list(modules_map.keys())

    simulate_build(targets, modules_map, root_dir)

if __name__ == "__main__":
    main()
