import pandas as pd
import json
import hashlib
from pathlib import Path
from datetime import datetime
import dspy

# Global variables to track processed calls
_processed_hashes = set()
_csv_path = "dspy_history.csv"
_include_full_prompts = False  # Set to True to log full prompts (increases CSV size)


def set_log_file(csv_path: str, include_full_prompts: bool = False):
    """Set the CSV file path for logging.
    
    Args:
        csv_path: Path to the CSV file for logging
        include_full_prompts: If True, log full system and user prompts (increases file size)
    """
    global _csv_path, _processed_hashes, _include_full_prompts
    _csv_path = csv_path
    _include_full_prompts = include_full_prompts

    # OPTIMIZATION: Do NOT load the entire CSV into memory.
    # We will only track hashes for the CURRENT session to avoid duplicates within a run.
    # If a run is restarted, we might log duplicates, but that's better than O(N) startup time.
    _processed_hashes = set()
    
    if not Path(csv_path).exists():
        print(f"New log file will be created: {csv_path}")
        if include_full_prompts:
            print("  ⚠️  Full prompts will be logged (large file size)")


def log_history(clear_memory: bool = True):
    """Log current DSPy history to CSV. Call this after running DSPy operations.
    
    Args:
        clear_memory: If True, clears the LM history after logging to free RAM.
    """
    global _processed_hashes, _csv_path

    # Get LM from dspy settings
    try:
        lm = dspy.settings.lm
    except:
        print("Error: No LM found in dspy.settings")
        return 0

    if not hasattr(lm, 'history') or not lm.history:
        # print("No history found in language model")
        return 0

    new_records = []

    for call_data in lm.history:
        # Generate unique hash
        hash_content = {
            'messages': call_data.get('messages', []),
            'timestamp': call_data.get('timestamp', ''),
            'uuid': call_data.get('uuid', ''),
        }
        call_hash = hashlib.md5(json.dumps(
            hash_content, sort_keys=True, default=str).encode()).hexdigest()

        # Skip if already processed IN THIS SESSION
        if call_hash in _processed_hashes:
            continue

        # Extract call info
        messages = call_data.get('messages', [])
        system_msg = next((m.get('content', '')
                          for m in messages if m.get('role') == 'system'), '')
        user_msg = next((m.get('content', '')
                        for m in messages if m.get('role') == 'user'), '')

        # Extract response
        response_obj = call_data.get('response', {})
        assistant_response = ""
        if hasattr(response_obj, 'choices') and response_obj.choices:
            assistant_response = response_obj.choices[0].message.content

        # Extract usage
        usage = call_data.get('usage', {})
        if isinstance(usage, dict):
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
        else:
            prompt_tokens = completion_tokens = total_tokens = 0

        record = {
            'call_hash': call_hash,
            'timestamp': call_data.get('timestamp', datetime.now().isoformat()),
            'uuid': call_data.get('uuid', ''),
            'model': call_data.get('model', ''),
            'cost': call_data.get('cost', 0.0),
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'system_msg_length': len(system_msg),
            'user_msg_preview': user_msg[:200] if user_msg else '',
            'response_preview': assistant_response[:200] if assistant_response else '',
            'cache_hit': getattr(response_obj, 'cache_hit', False) if response_obj else False,
            'logged_at': datetime.now().isoformat()
        }
        
        # Add full prompts if enabled
        if _include_full_prompts:
            record['full_system_prompt'] = system_msg
            record['full_user_prompt'] = user_msg
            record['full_response'] = assistant_response

        new_records.append(record)
        _processed_hashes.add(call_hash)

    if not new_records:
        if clear_memory:
            lm.history.clear()
        return 0

    # Save to CSV (Append mode)
    new_df = pd.DataFrame(new_records)

    if Path(_csv_path).exists():
        new_df.to_csv(_csv_path, mode='a', header=False, index=False)
    else:
        Path(_csv_path).parent.mkdir(parents=True, exist_ok=True)
        new_df.to_csv(_csv_path, index=False)
        
    # CRITICAL OPTIMIZATION: Clear memory after logging
    if clear_memory:
        lm.history.clear()

    return len(new_records)


def show_stats():
    """Show statistics from the logged history."""
    global _csv_path

    if not Path(_csv_path).exists():
        print("No history file found")
        return

    try:
        df = pd.read_csv(_csv_path)

        print(f"\nDSPy History Stats from {_csv_path}:")
        print("=" * 50)
        print(f"Total calls: {len(df)}")

        if 'model' in df.columns:
            print(f"Unique models: {df['model'].nunique()}")
            print("Model breakdown:")
            for model, count in df['model'].value_counts().head().items():
                print(f"  {model}: {count} calls")

        if 'cost' in df.columns:
            # If prompt_tokens == 0, set cost = 0 for those rows
            df.loc[df['prompt_tokens'] == 0, 'cost'] = 0

            # Recompute totals
            total_cost = df['cost'].sum()
            avg_cost = df['cost'].mean()

            print(f"Total cost: ${total_cost:.4f}")
            print(f"Average cost per call: ${avg_cost:.4f}")

        if 'total_tokens' in df.columns:
            total_tokens = df['total_tokens'].sum()
            avg_tokens = df['total_tokens'].mean()
            print(f"Total tokens: {total_tokens:,}")
            print(f"Average tokens per call: {avg_tokens:.1f}")

        if 'cache_hit' in df.columns:
            cache_rate = df['cache_hit'].mean() * 100
            print(f"Cache hit rate: {cache_rate:.1f}%")

        if 'timestamp' in df.columns:
            print(
                f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    except Exception as e:
        print(f"Error reading history: {e}")


def view_recent(n=5):
    """View the most recent n logged calls."""
    global _csv_path

    if not Path(_csv_path).exists():
        print("No history file found")
        return

    try:
        df = pd.read_csv(_csv_path)
        recent = df.tail(n)

        print(f"\nMost Recent {n} DSPy Calls:")
        print("=" * 60)

        for _, row in recent.iterrows():
            print(f"Time: {row['timestamp']}")
            print(f"Model: {row['model']}")
            print(f"Tokens: {row['total_tokens']} | Cost: ${row['cost']:.4f}")
            print(f"User: {row['user_msg_preview'][:100]}...")
            print(f"Response: {row['response_preview'][:100]}...")
            print("-" * 40)

    except Exception as e:
        print(f"Error reading history: {e}")


def clear_cache():
    """Clear the processed hashes cache (will reprocess all history next time)."""
    global _processed_hashes
    _processed_hashes.clear()
    print("Cleared processed hashes cache")


def export_full_history(output_file: str = "full_dspy_history.json"):
    """Export complete DSPy history with full messages to JSON."""
    try:
        lm = dspy.settings.lm
        if hasattr(lm, 'history') and lm.history:
            with open(output_file, 'w') as f:
                json.dump(lm.history, f, indent=2, default=str)
            print(f"Exported full history to {output_file}")
        else:
            print("No history found to export")
    except Exception as e:
        print(f"Error exporting history: {e}")


def log_execution_time(start_time: float, end_time: float, mode: str, source: str, target: str, schema: str):
    """Log execution time to CSV."""
    duration = end_time - start_time
    csv_path = "execution_times.csv"
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "duration_seconds": round(duration, 2),
        "source": source,
        "target": target,
        "schema": schema
    }
    
    df = pd.DataFrame([record])
    
    if Path(csv_path).exists():
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)
    
    print(f"\nExecution time logged: {duration:.2f}s")
