#!/usr/bin/env python3
"""
Celery Queue Manager
--------------------
A command-line interface (CLI) tool to inspect, monitor, and clean up 
Celery queues stored in Redis.

Features:
- Scans all Redis databases (0-15) for active queues.
- Inspects JSON payloads of tasks.
- Supports purging entire queues.
- Supports selective deletion of tasks using wildcards (e.g., '*email*').

Created by: Machiel Broekman
"""
import sys
import redis
import json
import fnmatch  # Required for wildcard matching (*, ?)
import os

# --- CONFIGURATION ---
# Adjust the host/port if necessary.
# If running inside Docker, use the service name (e.g., 'redis') instead of 'localhost'.
BASE_REDIS_URL = os.getenv('CELERY_REDIS_URL', 'redis://localhost:6379')

def scan_all_databases():
    """Scans Redis databases 0 through 15 for Lists (Celery queues)."""
    all_found_queues = []
    print(f"\n--- Scanning databases 0-15 on {BASE_REDIS_URL} ---")

    for db_num in range(16):
        try:
            current_url = f"{BASE_REDIS_URL}/{db_num}"
            # Short timeout to skip unreachable DBs quickly
            r = redis.from_url(current_url, socket_timeout=0.5)
            
            # Optimization: Skip empty databases
            try:
                if r.dbsize() == 0: continue
            except: pass

            # Scan for keys
            for key in r.scan_iter("*"):
                try:
                    # Celery queues are stored as Redis Lists
                    if r.type(key).decode('utf-8') == 'list':
                        key_name = key.decode('utf-8')
                        length = r.llen(key_name)
                        
                        all_found_queues.append({
                            'db': db_num,
                            'name': key_name,
                            'count': length,
                            'connection': r
                        })
                except Exception:
                    pass
        except Exception:
            # Ignore connection errors for specific DBs
            pass

    return all_found_queues

def get_task_name(task_bytes):
    """Attempts to parse the task name from the raw bytes."""
    try:
        task_data = json.loads(task_bytes.decode('utf-8'))
        
        # Check headers (Protocol v2)
        headers = task_data.get('headers', {})
        name = headers.get('task')
        
        # Check body (Protocol v1 or fallback)
        if not name:
            name = task_data.get('task')
            
        return name if name else "Unknown_Task"
    except:
        return "Unreadable_Data"

def delete_tasks_by_pattern(r_conn, queue_name):
    """Deletes specific tasks based on a name pattern (wildcard)."""
    print(f"\n--- Selective Delete from '{queue_name}' ---")
    print("You can use wildcards. Examples: 'email*' or '*.validate_user'")
    
    pattern = input("Enter task name (or pattern) to delete: ")
    if not pattern:
        print("No pattern entered. Action cancelled.")
        return

    print("Analyzing queue content (this may take a moment)...")
    
    # Step 1: Fetch ALL items to inspect them
    # Warning: fast for <10k items, slower for massive queues
    all_items = r_conn.lrange(queue_name, 0, -1)
    to_delete = []
    
    # Step 2: Filter items locally
    for item in all_items:
        t_name = get_task_name(item)
        if fnmatch.fnmatch(t_name, pattern):
            to_delete.append((t_name, item))

    if not to_delete:
        print(f"❌ No tasks found matching pattern '{pattern}'.")
        return

    # Step 3: Confirmation
    print(f"\n⚠️  Found: {len(to_delete)} tasks matching '{pattern}'.")
    
    # Show preview
    print("Preview of matches:")
    for i, (name, _) in enumerate(to_delete[:3]):
        print(f"   - {name}")
    if len(to_delete) > 3: 
        print("   - ... and more")

    confirm = input(f"Are you sure you want to delete these {len(to_delete)} tasks? (yes/no): ")
    
    if confirm.lower() == 'yes':
        count = 0
        # Step 4: Perform deletion
        for t_name, raw_data in to_delete:
            # LREM removes items matching the value exactly
            removed = r_conn.lrem(queue_name, 0, raw_data)
            if removed > 0:
                count += 1
        print(f"✅ {count} tasks successfully removed.")
    else:
        print("Operation cancelled.")

def main():
    print("Starting Celery Queue Manager...")
    
    while True:
        queues = scan_all_databases()

        if not queues:
            print("\n❌ No queues found in any database (0-15).")
            print("Check your Redis connection URL.")
            break

        print("\n--- Found Queues ---")
        for i, q in enumerate(queues):
            print(f"{i + 1}. [DB {q['db']}] {q['name']:<30} (Items: {q['count']})")

        print("\nOptions:")
        print("Type the queue NUMBER to select it.")
        print("Type 'q' to quit.")
        print("Type 'r' to refresh/rescan.")

        choice = input("\nChoice: ").lower()

        if choice == 'q':
            print("Exiting. Goodbye!")
            sys.exit()
        elif choice == 'r':
            continue
        
        try:
            idx = int(choice)
            if 1 <= idx <= len(queues):
                target = queues[idx - 1]
                r_conn = target['connection']
                q_name = target['name']
                
                print(f"\nSelected Queue: '{q_name}' (DB {target['db']})")
                print("1. INSPECT CONTENT (Show top 5 tasks)")
                print("2. PURGE ENTIRE QUEUE (Delete everything)")
                print("3. DELETE SPECIFIC TASKS (Filter by name/wildcard)")
                print("4. Cancel / Back")
                
                sub_choice = input("Action: ")
                
                if sub_choice == '1':
                    # Inspect top 5
                    items = r_conn.lrange(q_name, 0, 4)
                    if not items:
                        print("Queue is empty.")
                    for raw in items:
                        print(f"- {get_task_name(raw)}")
                    input("\nPress Enter to continue...")
                    
                elif sub_choice == '2':
                    confirm = input(f"WARNING: Are you sure you want to delete ALL tasks in '{q_name}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        r_conn.delete(q_name)
                        print(f"✅ Queue '{q_name}' purged.")
                    else:
                        print("Cancelled.")
                        
                elif sub_choice == '3':
                    delete_tasks_by_pattern(r_conn, q_name)
                    
            else:
                print("Invalid number selected.")
        except ValueError:
            if choice not in ['r', 'q']:
                print("Invalid input.")

if __name__ == "__main__":
    main()