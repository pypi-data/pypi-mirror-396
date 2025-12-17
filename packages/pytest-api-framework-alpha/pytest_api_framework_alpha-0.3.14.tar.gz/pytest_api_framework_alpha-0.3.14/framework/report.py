import json
import argparse
import datetime
import traceback
from pathlib import Path
from framework.db.mysql_db import MysqlDB
from framework.utils.log_util import logger

from config.settings import DATABASE_HOST, DATABASE_PASSWORD, DATABASE_DB, DATABASE_USERNAME, DATABASE_PORT

if __name__ == '__main__':
    logger.info('调用report脚本')
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="演示如何使用 argparse 获取命令行参数")
    # 添加位置参数
    parser.add_argument('--task', help="输入任务的名字", required=True)
    # 添加可选参数
    parser.add_argument('--buildnum', type=int, help="输入构建次数", required=True)
    parser.add_argument('--allure_result', type=str, help="allure_result路径", required=True)

    # 解析命令行参数
    args = parser.parse_args()
    if not args.task:
        exit(400)
    logger.info(f"task, {args.task}!")
    taskName = args.task

    if not args.buildnum:
        exit(400)
    logger.info(f"buildnum, {args.buildnum}!")
    buildNum = args.buildnum

    if not args.allure_result:
        exit(400)
    logger.info(f"allure_result_path, {args.allure_result}!")
    allure_result_path = args.allure_result

    # 初始化数据库连接
    logger.info('初始化数据库连接')
    mysqlDB = MysqlDB(
        host=DATABASE_HOST,
        username=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT,
        db=DATABASE_DB
    )

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    task_id = mysqlDB.insert(
        f"INSERT INTO tbl_task (name,last_run_time,buildnum) VALUES ('{taskName}','{formatted_time}','{buildNum}')")
    logger.info(f'{task_id}')

    # 获取所有‘result.json‘结尾的文件
    logger.info('获取所有‘*result.json‘结尾的文件')
    folder = Path(allure_result_path)
    all = list(folder.rglob('*result.json'))
    logger.info(f'files count: {len(all)}')

    for file_path in all:
        try:
            # 打开 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as file:
                # 解析 JSON 文件内容
                data = json.load(file)
                # 示例：访问解析后的数据
                if 'fullName' in data:
                    logger.info(f"fullName: {data['fullName']}")
                if 'testCaseId' in data:
                    logger.info(f"testCaseId: {data['testCaseId']}")
                if 'start' in data:
                    logger.info(f"start: {data['start']}")
                if 'stop' in data:
                    logger.info(f"stop: {data['stop']}")
                if 'uuid' in data:
                    logger.info(f"uuid: {data['uuid']}")
                if 'status' in data:
                    logger.info(f"status: {data['status']}")

                if 'name' in data:
                    logger.info(f"name: {data['name']}")

                    if 'statusDetails' in data and data['statusDetails'] is not None:
                        mysqlDB.execute(
                            f"INSERT INTO tbl_test_case (test_case_id,status,name,starttime,stoptime,uuid,task_id,message) VALUES ('{data['testCaseId']}','{data['status']}','{data['name']}',{data['start']},{data['stop']},'{data['uuid']}',{task_id},'{str(data['statusDetails'])}')")
                    else:
                        mysqlDB.execute(
                            f"INSERT INTO tbl_test_case (test_case_id,status,name,starttime,stoptime,uuid,task_id) VALUES ('{data['testCaseId']}','{data['status']}','{data['name']}',{data['start']},{data['stop']},'{data['uuid']}',{task_id})")

        except FileNotFoundError:
            logger.info("错误: 文件未找到，请检查文件路径是否正确。")
        except json.JSONDecodeError:
            logger.info("错误: JSON 解析出错，请检查文件内容格式是否正确。")
        except Exception as e:
            logger.info(f"发生未知错误: {e}")
            traceback.print_exc()
