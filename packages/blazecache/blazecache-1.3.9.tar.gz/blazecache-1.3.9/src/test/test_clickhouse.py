import os
from blazecache import blazecache
from pathlib import Path
import subprocess
from base.log import log_util
from business import compilecachesubmit_plugin

def build_clickhouse(repo_dir: str):
    return True
    

if __name__ == "__main__":
    clickhouse_local_repo_dir = "/Users/bytedance/Desktop/clickhouse-build/ClickHouse"
    clickhouse_git_url = "git@code.byted.org:dp/ClickHouse.git"
    # 初始化 BlazeCache 的参数
    product_name = "clickhouse"
    build_dir = clickhouse_local_repo_dir
    local_repo_dir = {
        "clickhouse": clickhouse_local_repo_dir
    }
    current_branch = "cnch-dev"
    current_commit_id = "5f141c8ae32b7ce8924483089c88f9aa391ac536"
    os_type = "linux"
    task_type = "cache_generator_task"
    branch_type = current_branch
    # 本次做缓存的机器 id, 暂时用1234测试
    machine_id = "1234"
    print(f"machine_id: {machine_id}")
    feature_branch = {
        "clickhouse": current_commit_id
    }
    p4_client = f"clickhouse-{machine_id}"
    fallback_branch = None
    product_tos_url = "https://tosv.byted.org/obj/blazecache-cn/product_config/clickhouse/product_config.json"

    p4_submit_label = f'clickhouse_{current_branch}_{current_commit_id}'
    print(f"p4_label: {p4_submit_label}")
    
    modify_timestamp_flag = False
    
    bzcache = blazecache.BlazeCache(product_name=product_name, build_dir=build_dir, local_repo_dir=local_repo_dir,
                                    os_type=os_type, task_type=task_type, branch_type=branch_type,
                                    machine_id=machine_id, mr_target_branch=current_branch,
                                    feature_branch=feature_branch, p4_client=p4_client, fallback_branch=fallback_branch,
                                    product_tos_url=product_tos_url)
    
    result = bzcache.run_compile_cache_submit_plugin(build_executor=lambda: build_clickhouse(repo_dir=clickhouse_local_repo_dir),
                                            p4_ignore_url="https://tosv.byted.org/obj/blazecache-cn/p4_ignore/clickhouse/p4_ignore.txt",
                                            p4_submit_label=p4_submit_label, mr_target_branch=feature_branch, modify_timestamp=modify_timestamp_flag)
    