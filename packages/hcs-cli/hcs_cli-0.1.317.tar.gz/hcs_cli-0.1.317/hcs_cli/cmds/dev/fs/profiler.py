import json
import os
from time import sleep, time

import click

from hcs_cli.support.exec_util import exec


@click.command()
def profiler():
    """Profile IO"""

    print("Starting profiler...")
    _enable_mongo_profiler()

    redis_stat_start = _get_redis_stat()
    start_time = time()

    print("Profiler started.")
    print()
    print("---------------------------------")
    print("Press CTRL+C to stop...")
    print("---------------------------------")

    elapsed = 0

    def _snapshot():
        nonlocal elapsed
        elapsed = int(time() - start_time)
        mong_stat_current = _get_mongo_stat()
        redis_stat_current = _get_redis_stat()

        total_ops = sum(mong_stat_current.values())
        opm = int((total_ops / elapsed if elapsed > 0 else 0) / 60)
        print(f"Mongo:   {mong_stat_current}, {opm}/m")
        redis_commands = int(redis_stat_current["stats"]["total_commands_processed"]) - int(
            redis_stat_start["stats"]["total_commands_processed"]
        )
        cpm = int((redis_commands / elapsed if elapsed > 0 else 0) / 60)
        print(f"Redis:   {redis_commands}, {cpm}/m")
        print(f"Elapsed: {elapsed} seconds")
        print()

    try:
        while True:
            _snapshot()
            sleep(10)
    except KeyboardInterrupt:
        pass

    _snapshot()

    print("Stopping profiler...")
    _disable_mongo_profiler()
    print("Done")


def _run_mongo_commands(command: str):
    kubectl_cmd = ["kubectl", "exec", "-i", "mongodb-standalone-0", "--", "/bin/bash", "-c", "mongo -u mongoadmin -p mongosecret --quiet"]
    cp = exec(kubectl_cmd, input=command, show_command=False, env=os.environ.copy())
    stdout = cp.stdout.strip()
    # print("STDOUT:", stdout)
    return stdout


def _enable_mongo_profiler():

    mongo_commands = """
use app
db.setProfilingLevel(0)
db.system.profile.drop()
db.setProfilingLevel(2)
"""
    return _run_mongo_commands(mongo_commands)


def _get_mongo_stat():
    #     mongo_commands = """
    # use app
    # db.system.profile.aggregate([{$group:{_id:'$op',count:{$sum:1}}}])
    # """
    mongo_commands = """
use app
print('---STAT---')
db.system.profile.aggregate([{$group:{_id:"$op",count:{$sum:1}}},{$group:{_id:null,asMap:{$push:{k:"$_id",v:"$count"}}}},{$replaceRoot:{newRoot:{$arrayToObject:"$asMap"}}}])
"""
    ret = _run_mongo_commands(mongo_commands)

    # get the content after '---STAT---'
    stat_start = ret.find("---STAT---")
    if stat_start == -1:
        print(ret)
        raise Exception("No '---STAT---' found in MongoDB profiler output")
    stat_content = ret[stat_start + len("---STAT---") :].strip()
    if not stat_content:
        return {}
    return json.loads(stat_content)


def _disable_mongo_profiler():
    mongo_commands = """
use app
db.setProfilingLevel(0)
db.system.profile.drop()
"""
    return _run_mongo_commands(mongo_commands)


def _parse_redis_info(text):
    ret = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        ret[key.strip()] = value.strip()
    return ret


def _get_redis_stat():
    env = os.environ.copy()
    cp = exec("kubectl exec -it redis-standalone-0 -- redis-cli info stats", show_command=False, env=env)
    stats = _parse_redis_info(cp.stdout)

    cp = exec("kubectl exec -it redis-standalone-0 -- redis-cli info memory", show_command=False, env=env)
    memory = _parse_redis_info(cp.stdout)

    return {"stats": stats, "memory": memory}
