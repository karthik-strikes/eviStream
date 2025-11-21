import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from schemas.registry import get_schema

def verify():
    print("Verifying 'index_test' schema...")
    
    # 1. Check registry
    try:
        schema = get_schema("index_test")
        print("PASS: Schema found in registry.")
    except Exception as e:
        print(f"FAIL: Schema not found in registry: {e}")
        return
    
    # 2. Check attributes
    print(f"Schema Name: {schema.name}")
    print(f"Output Field: {schema.output_field_name}")
    print(f"Cache File: {schema.field_cache_file}")
    
    # 3. Instantiate pipeline
    try:
        pipeline = schema.pipeline_factory()
        print(f"PASS: Pipeline instantiated: {type(pipeline)}")
    except Exception as e:
        print(f"FAIL: Pipeline instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("Verification successful!")

if __name__ == "__main__":
    verify()
