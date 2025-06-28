import sys
import os
from flow import create_text_to_sql_flow
from populate_db import populate_database, DB_FILE

def run_text_to_sql(natural_query, db_path=DB_FILE, max_debug_retries=3):
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        print(f"Database at {db_path} missing or empty. Populating...")
        populate_database(db_path)

    shared = {
        "db_path": db_path,
        "natural_query": natural_query,
        "max_debug_attempts": max_debug_retries,
        "debug_attempts": 0,
        "final_result": None,
        "final_error": None
    }

    print(f"\n=== Starting Text-to-SQL Workflow ===")
    print(f"Query: '{natural_query}'")
    print(f"Database: {db_path}")
    print(f"Max Debug Retries on SQL Error: {max_debug_retries}")
    print("=" * 45)

    flow = create_text_to_sql_flow()
    flow.run(shared) # 让流程逻辑处理循环内的错误

    # 根据共享数据检查最终状态
    if shared.get("final_error"):
            print("\n=== Workflow Completed with Error ===")
            print(f"Error: {shared['final_error']}")
    elif shared.get("final_result") is not None:
            print("\n=== Workflow Completed Successfully ===")
            # 结果已经由ExecuteSQL节点打印
    else:
            # 如果流程逻辑正确且覆盖所有结束状态，这种情况不应该发生
            print("\n=== Workflow Completed (Unknown State) ===")

    print("=" * 36)
    return shared

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "total products per category"

    run_text_to_sql(query) 