import os
import re
import sys
import copy
import time
import platform
import threading
import importlib
import traceback
from pathlib import Path
from itertools import chain
from urllib.parse import urljoin
from collections import OrderedDict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import dill
import json
import retry
import allure
import pytest
from box import Box
import simplejson as json

import config.settings as settings
from framework.exit_code import ExitCode
from framework.db.mysql_db import MysqlDB
from framework.db.redis_db import RedisDB
from framework.utils.log_util import logger
from framework.utils.lark_util import LarkUtil
from framework.utils.yaml_util import CachedYamlLoader
from framework.exceptions import MysqlDBError, RedisDBError
from framework.global_attribute import CONTEXT, CONFIG, _FRAMEWORK_CONTEXT
from framework.utils.common import snake_to_pascal, get_apps, convert_numbers_to_decimal

all_app = get_apps()
module = importlib.import_module("test_case.conftest")
MARK_LIST = [item.lower() for sublist in settings.MARK_LIST.values() for item in sublist]


@pytest.fixture(autouse=True)
def response():
    response = None
    yield response


@pytest.fixture(autouse=True)
def data():
    data: dict = dict()
    yield data


@pytest.fixture(autouse=True)
def belong_app():
    app = None
    yield app


@pytest.fixture(autouse=True)
def config():
    config = None
    yield config


@pytest.fixture(autouse=True)
def context():
    context = None
    yield context


class Http(object): pass


@retry.retry(tries=3, delay=1)
@pytest.fixture(scope="function", autouse=True)
def http():
    yield _FRAMEWORK_CONTEXT.get("_http")


def pytest_configure(config):
    """
    初始化时被调用，可以用于设置全局状态或配置
    :param config:
    :return:
    """
    for app in all_app:
        # 将所有app对应环境的基础测试数据加到全局
        CONTEXT.set_from_yaml(f"config/{app}/context.yaml", CONTEXT.env, app)
        # 将所有app对应环境的中间件配置加到全局
        CONFIG.set_from_yaml(f"config/config.yaml", CONTEXT.env, app)

    CONTEXT.set(key="all_app", value=all_app)
    sys.path.append(settings.CASES_DIR)


def pytest_generate_tests(metafunc):
    """
    生成（多个）对测试函数的参数化调用
    :param metafunc:
    :return:
    """

    keyword_expr = metafunc.config.getoption("keyword")
    mark_expr = metafunc.config.getoption("markexpr")
    node_id = metafunc.definition.keywords.node.nodeid
    # 关键字标记
    keyword_flag = match_keyword(keyword_expr, node_id)
    # 如果只通过关键字过滤，没匹配上则直接返回
    if not keyword_flag and not mark_expr:
        return
    # 获取当前待执行用例的文件名
    module_name = metafunc.module.__name__.split('.')[-1]
    func_file_path = metafunc.module.__file__
    # 获取当前待执行用例的函数名
    func_name = metafunc.function.__name__
    # UPDATE: 为了支持Setup和Teardown的分组
    if func_name in ["test_setup", "test_teardown"]:
        return

    # 获取测试用例所属app
    belong_app = Path(func_file_path).relative_to(settings.CASES_DIR).parts[0]
    # 获取当前用例对应的测试数据路径
    data_path = find_data_path_by_case(belong_app, module_name)
    if not data_path:
        logger.error(f"测试数据文件: {func_file_path} 不存在")
        traceback.print_exc()
        pytest.exit(ExitCode.CASE_YAML_NOT_EXIST)
    # yml转json
    test_data = CachedYamlLoader(data_path).load_yml()

    # 测试用例公共数据
    case_common = test_data.get("case_common")
    # 忽略的用例直接跳过
    if case_common.get("ignore"):
        return
    # 获取mark标记
    marks = case_common.get("marks", [])
    # 将case_common中的moudel加到标签中
    marks.append(case_common.get("module", ""))
    # 将脚本中类中和定义的标签加到marks
    cls_pytestmark = getattr(metafunc.cls, "pytestmark", [])
    func_pytestmark = getattr(metafunc.definition, "own_markers")
    func_pytestmark.extend(cls_pytestmark)
    for mark_obj in func_pytestmark:
        if mark_obj.name not in ["skip", "skipif", "xfail", "usefixtures", "filterwarnings",
                                 "parametrize", "order", "timeout", "django_db", "asyncio"] and not mark_obj.args:
            marks.append(mark_obj.name)
    marks = [item.lower() for item in marks]
    # 校验标签
    is_subset, diff = subset_and_diff(set(marks), set(MARK_LIST))

    # 测试用例数据
    case_data = test_data.get(func_name) or dict()
    if not case_data:
        case_data["_scenario"] = {"data": {}}
        case_data["_belong_app"] = belong_app
        metafunc.parametrize("data", [case_data, ], ids=[f'{case_data.get("title", "")}#'], scope="function")
        return
    if case_data.get("request") is None:
        case_data["request"] = dict()
    if case_data.get("request").get("headers") is None:
        case_data["request"]["headers"] = dict()

    # 合并测试数据
    case_data.setdefault("module", case_common.get("module"))
    case_data.setdefault("describe", case_common.get("describe"))
    case_data["_belong_app"] = belong_app
    # 根据belong_app获取域名
    domain = CONTEXT.get(key="domain", app=belong_app)
    domain = domain if domain.startswith("http") else f"https://{domain}"
    # 获取request中的url
    url = case_data.get("request").get("url")
    # 判断url是否存在
    if not url:
        # 获取case_common中url
        case_common_url = case_common.get("url") or ""
        case_data["request"]["url"] = case_common_url if case_common_url.strip().startswith("${") else urljoin(
            domain, case_common_url)
        # # 判断case_common是否有url, 如果没有url给与提示
        # if not case_common_url:
        #     logger.warning(f"{func_name} request中缺少必要字段: url")

    else:
        case_data["request"]["url"] = url if url.strip().startswith("${") else urljoin(domain, url)
    # 获取method
    method = case_data.get("request").get("method")
    # 判断method是否存在
    if not method:
        # 获取case_common中method
        case_common_method = case_common.get("method", None)
        case_data["request"]["method"] = case_common_method
        # # 如果没有method给与提示
        # if not case_common_method:
        #     logger.warning(f"{func_name} request中缺少必要字段: method")

    # 获取用例title
    title = case_data.get("title")
    # 如果没有title给与提示
    if not title:
        logger.warning(f"{func_name} 缺少必要字段: title")

    scenarios = case_common.get("scenarios")
    if settings.ONLY_SUPPORT_SCENARIO and not scenarios:
        logger.error("当前仅支持使用scenario的方式执行用例")
        pytest.exit(ExitCode.NONSUPPORT_RUN_MODE)
    case_data_list = list()
    if scenarios:
        ids = list()
        for index, item in enumerate(scenarios):
            scenario = item.get("scenario")
            level = scenario.get("level", settings.DEFAULT_CASE_LEVEL).lower()
            case_data["level"] = level
            if scenario.get("ignore"):
                continue
            if func_name in scenario.get("exclude", list()):
                continue

            new_marks = marks.copy()
            new_marks.append(level)
            # mark标记
            mark_flag = match_mark(mark_expr, new_marks)
            # 用例路径匹配不到关键词,或者标签匹配不到用例，跳过该用例加载
            if not keyword_flag or not mark_flag:
                continue

            if not is_subset:
                logger.warning(f"{node_id} 使用非规范的用例标签:{list(diff)}")
                if settings.STRICT_MARKS:
                    return
            if level not in settings.CASE_LEVEL_LIST:
                logger.warning(f"{node_id} 使用非规范的用例级别 {level}")
                if settings.STRICT_MARKS:
                    continue
            try:
                deep_copied_case_data = copy.deepcopy(case_data)
                # 剔除标记disable的字段
                deep_copied_case_data = disable_field(scenario.get("data"), deep_copied_case_data)
                deep_copied_case_data["_scenario"] = item.get("scenario")
                deep_copied_case_data["_marks"] = new_marks
                deep_copied_case_data["_ignore_failed"] = case_common.get("ignore_failed",
                                                                          settings.GLOBAL_IGNORE_FAILED)
                case_data_list.append(deep_copied_case_data)
                ids.append(f'{case_data.get("title")} - {scenario.get("describe") or ""}#{index + 1}')
                logger.info(f"{node_id}::{case_data.get('title')} - {scenario.get('describe') or ''}#{index + 1}")

            except Exception as e:
                logger.error(f"scenario参数化格式不正确:{e}")
                traceback.print_exc()
                pytest.exit(ExitCode.SCENARIO_FORMAT_ERROR)
        if case_data_list:
            metafunc.parametrize("data", case_data_list, ids=ids, scope="function")

    else:
        case_data["_scenario"] = {"data": {}}
        case_data["_ignore_failed"] = case_common.get("ignore_failed", settings.GLOBAL_IGNORE_FAILED)
        level = case_data.get("level", settings.DEFAULT_CASE_LEVEL)
        case_data["level"] = level
        new_marks = marks.copy()
        new_marks.append(level)
        # 用例加mark标签
        case_data["_marks"] = new_marks
        # mark标记
        mark_flag = match_mark(mark_expr, new_marks)
        # 用例路径匹配不到关键词,或者标签匹配不到用例，跳过该用例加载
        if not keyword_flag or not mark_flag:
            return
        if not is_subset:
            logger.warning(f"{node_id} 使用非规范的用例标签:{list(diff)}")
            if settings.STRICT_MARKS:
                return
        if level not in settings.CASE_LEVEL_LIST:
            logger.warning(f"{node_id} 使用非规范的用例级别 {level}")
            if settings.STRICT_MARKS:
                return
        logger.info(f"{node_id}::{case_data.get('title')}#1")
        case_data_list = [case_data]
        # 进行参数化生成用例
        metafunc.parametrize("data", case_data_list, ids=[f'{case_data.get("title")}#1'], scope="function")


def pytest_collection_modifyitems(items):
    # 过滤掉不在收集范围的case
    items = [item for item in items if getattr(item, "callspec", None)]
    # 重新排序
    new_items = sort(items)
    items[:] = new_items
    for item in items:
        # 获取mark标记
        data = item.callspec.params["data"]
        if isinstance(data, dict):
            marks = data.get("_marks")
            for mark in marks:
                item.add_marker(mark)




def pytest_collection_finish(session):
    """获取最终排序后的 items 列表"""
    logger.info(f"共收集到 {len(session.items)} 个测试用例")
    if not session.items:
        pytest.exit("未收集到用例")
    # 过滤掉item名称是test_setup或test_teardown的
    session.items = [item for item in session.items if item.name not in ["test_setup", "test_teardown"]]

    # 1. 筛选出带井号 名称带'#' 的item，并记录原始索引
    hash_items_with_index = [(index, item) for index, item in enumerate(session.items) if "#" in item.name]

    # 2. 按照 'cls' 对带井号的元素进行分组
    grouped_by_cls = {}
    for index, item in hash_items_with_index:
        cls = item.cls.__module__ + item.parent.name
        if cls not in grouped_by_cls:
            grouped_by_cls[cls] = []
        grouped_by_cls[cls].append((index, item))  # 记录索引和元素

    # 3. 对每个 cls 分组内的带井号的元素进行排序
    for cls, group in grouped_by_cls.items():
        group_values = [x[1] for x in group]
        # 获取item#号后面的数字
        pattern = r"#(\d+)]"
        grouped_data = OrderedDict()
        # 按照#号后面的数字进行排序并分组
        for item in group_values:
            index = re.search(pattern, item.name).group(1)
            grouped_data.setdefault(index, []).append(item)
        # 标记每个分组的第一个和最后一个
        for group2 in grouped_data.values():
            group2[0].funcargs["first"] = True
            group2[-1].funcargs["last"] = True

        group_values = list(chain.from_iterable(grouped_data.values()))

        # 4. 将排序后的items放回原列表
        for (original_index, _), val in zip(group, group_values):
            session.items[original_index] = val  # 将反转后的元素替换回原位置


def pytest_runtestloop(session):
    # 统一登录账号
    _FRAMEWORK_CONTEXT.set(key="_http", value=login())

    # 执行前置脚本
    app = CONTEXT.get("app")
    app_handlers = getattr(settings, "APP_START_HANDLER_CLASSES", {})
    if app:
        handlers = app_handlers.get(app) or []
    else:
        handlers = [h for value in app_handlers.values() for h in value] or []
    global_handlers = getattr(settings, "GLOBAL_START_HANDLER_CLASSES", [])
    global_handlers.extend(handlers)
    handlers = global_handlers
    for handler in handlers:
        try:
            module_path, class_name = handler.rsplit(".", 1)
            cls = getattr(importlib.import_module(module_path), class_name)
            cls().run()
        except Exception as e:
            logger.error(str(e))
            traceback.print_exc()
            pytest.exit(ExitCode.GLOBAL_SCRIPT_ERROR)


def pytest_sessionfinish(session, exitstatus):
    app = CONTEXT.get("app")
    app_handlers = getattr(settings, "APP_FINISH_HANDLER_CLASSES", {})
    if app:
        handlers = app_handlers.get(app) or []
    else:
        handlers = [h for value in app_handlers.values() for h in value] or []
    global_handlers = getattr(settings, "GLOBAL_FINISH_HANDLER_CLASSES", [])
    handlers.extend(global_handlers)
    for handler in handlers:
        try:
            module_path, class_name = handler.rsplit(".", 1)
            cls = getattr(importlib.import_module(module_path), class_name)
            cls().run()
        except Exception as e:
            logger.error(str(e))
            traceback.print_exc()
            pytest.exit(ExitCode.GLOBAL_SCRIPT_ERROR)


def pytest_runtest_setup(item):
    allure.dynamic.sub_suite(item.allure_suite_mark)
    if item.funcargs.get("first"):
        test_object = item.instance
        test_object.context = CONTEXT
        test_object.config = CONFIG
        test_object.http = _FRAMEWORK_CONTEXT.get(key="_http")
        data = item.callspec.params.get("data")
        test_object.data = Box(data)
        test_object.scenario = Box(
            json.loads(json.dumps(convert_numbers_to_decimal(data.get("_scenario")))))
        test_object.belong_app = data.get("_belong_app")
        test_before_scenario = getattr(test_object, "test_setup", None)
        if test_before_scenario:
            try:
                test_before_scenario()
                item.funcargs["setup_success"] = True
            except Exception as e:
                item.funcargs["setup_success"] = False
                traceback.print_exc()
                logger.error(f"{item.name} test_setup方法执行异常: {e}")


def pytest_runtest_call(item):
    """
    模版渲染，运行用例
    :param item:
    :return:
    """
    origin_data = item.funcargs.get("data")
    ignore_failed = origin_data.get("_ignore_failed")
    if not ignore_failed:
        # setup方法执行失败，则主动标记用例执行失败，不会执行用例
        if item.funcargs.get("setup_success") is False:
            pytest.skip(f"test_setup execute error")
        # 判断上一个用例是否执行失败，如果上一个用例执行失败，则主动标记用例执行失败，不会执行用例（解决场景性用例，有一个失败则后续用例判为失败）
        index = item.session.items.index(item)
        pattern = re.compile(r'^(?P<prefix>.*)::[^:\[\]]+\[.*#(?P<index>\d+)\]$')
        current_match = pattern.match(item.nodeid)
        current_cls_name = current_match.group('prefix')
        current_index = current_match.group('index')
        prev_item = item.session.items[index - 1]
        prev_match = pattern.match(prev_item.nodeid)
        prev_cls_name = prev_match.group("prefix")
        prev_index = prev_match.group("index")
        # 确保是同一个类,并且索引相同
        if current_cls_name == prev_cls_name and current_index == prev_index:
            status = getattr(prev_item, "status", None)  # 访问 status 属性
            skip_reason = getattr(prev_item, "skip_reason", None)  # 访问 skip_reason 属性
            if status == "skipped" and skip_reason.strip() in [
                "the previous method execute skipped",
                "the previous method execute failed",
                "test_setup execute error"]:
                pytest.skip("the previous method execute skipped")
            elif status == "failed":
                pytest.skip("the previous method execute failed")

    # 获取原始测试数据
    origin_data = item.funcargs.get("data")
    logger.info(f"执行用例: {item.nodeid}")
    # 函数式测试用例添加参数data, belong_app
    http = item.funcargs.get("http")
    item.funcargs["data"] = item.instance.data = Box(origin_data)
    item.funcargs["scenario"] = item.instance.scenario = Box(json.loads(json.dumps(
        convert_numbers_to_decimal(origin_data.get("_scenario")))))
    _belong_app = origin_data.get("_belong_app")
    item.funcargs["belong_app"] = item.instance.belong_app = _belong_app
    item.funcargs["config"] = item.instance.config = CONFIG
    item.funcargs["context"] = item.instance.context = CONTEXT
    # 类式测试用例添加参数http，data, belong_app
    item.instance.http = http

    # 判断token是否过期，过期则重新登录
    expire_time = _FRAMEWORK_CONTEXT.get(app=_belong_app, key="expire_time")
    if expire_time:
        _http = _FRAMEWORK_CONTEXT.get("_http")
        if datetime.now() >= expire_time:
            # 重新登录
            setattr(_http, _belong_app, getattr(module, f"{snake_to_pascal(_belong_app)}Login")(_belong_app))
            # 更新记录的过期时间
            token_expiry = CONTEXT.get(_belong_app).get("token_expiry")
            expire_time = datetime.now() + timedelta(seconds=token_expiry)
            _FRAMEWORK_CONTEXT.set(app=_belong_app, key="expire_time", value=expire_time)


def pytest_runtest_teardown(item):
    if item.funcargs.get("last"):
        test_object = item.instance
        test_object.context = CONTEXT
        test_object.config = CONFIG
        test_object.http = _FRAMEWORK_CONTEXT.get(key="_http")
        data = item.callspec.params.get("data")
        test_object.data = Box(data)
        test_object.scenario = Box(
            json.loads(json.dumps(convert_numbers_to_decimal(data.get("_scenario")))))
        test_object.belong_app = data.get("_belong_app")
        test_after_scenario = getattr(test_object, "test_teardown", None)
        if test_after_scenario:
            try:
                test_after_scenario()
            except Exception as e:
                logger.error(f"{item.name} test_teardown方法执行异常: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """拦截 pytest 生成测试报告，移除特定用例的统计"""
    outcome = yield
    report = outcome.get_result()
    # 将测试结果存储到 item 对象的自定义属性 `_test_status`
    if report.when == "call":  # 只记录测试执行阶段的状态，不包括 setup/teardown
        longrepr = report.longrepr
        if longrepr:
            try:
                if ":" in longrepr[2]:
                    key, reason = longrepr[2].split(":")
                else:
                    key, reason = longrepr[2], ""
                if key == "Skipped":
                    item.skip_reason = reason
            except:
                pass
        item.status = report.outcome  # 'passed', 'failed', or 'skipped'


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """在 pytest 结束后修改统计数据或添加自定义报告"""
    stats = terminalreporter.stats
    # 统计各种测试结果
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    skipped = len(stats.get("skipped", []))
    total = passed + failed + skipped
    try:
        pass_rate = round(passed / (total - skipped) * 100, 2)
    except ZeroDivisionError:
        pass_rate = 0
    # 打印自定义统计信息
    terminalreporter.write("\n============ 执行结果统计 ============\n", blue=True, bold=True)
    terminalreporter.write(f"执行用例总数: {passed + failed}\n", bold=True)
    terminalreporter.write(f"通过用例数: {passed}\n", green=True, bold=True)
    terminalreporter.write(f"失败用例数: {failed}\n", red=True, bold=True)
    terminalreporter.write(f"跳过用例数: {skipped}\n", yellow=True, bold=True)
    terminalreporter.write(f"用例通过率: {pass_rate}%\n", green=True, bold=True)
    terminalreporter.write("====================================\n", blue=True, bold=True)
    if settings.ONLY_LINUX_NOTIFICATION:
        if "linux" not in platform.platform().lower():
            return
    for webhook in settings.LARK_WEBHOOKS.get(CONTEXT.get("env")):
        LarkUtil(webhook).send_test_report(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            report_url=os.environ.get("ALLURE_REPORT_URL"),
            job_name=os.environ.get("JOB_NAME"),
            env=CONTEXT.get("env")
        )

def pytest_exception_interact(node, call, report):
    """
    用例执行抛出异常时，将异常记录到日志
    :param node:
    :param call:
    :param report:
    :return:
    """
    if call.excinfo.type is AssertionError:
        logger.error(f"{node.nodeid} failed: {call.excinfo.value}\n")


def init_mysql():
    """初始化 MySQL 连接池"""
    try:
        mysql_config = CONFIG.get(app=all_app[0], key="mysql")
        mysql_conns = {item: MysqlDB(**mysql_config[item]) for item in mysql_config}
        for app in all_app:
            _FRAMEWORK_CONTEXT.set(app=app, key="mysql", value=mysql_conns)
    except Exception as e:
        raise MysqlDBError(e)


def init_redis():
    """初始化 Redis 连接池（16个db）"""
    try:
        redis_config = CONFIG.get(app=all_app[0], key="redis")
        redis_conns = {
            db: [RedisDB(**{**db_info, "db": i}) for i in range(16)]
            for db, db_info in redis_config.items()
        }
        for app in all_app:
            _FRAMEWORK_CONTEXT.set(app=app, key="redis", value=redis_conns)
    except Exception as e:
        raise RedisDBError(e)


def inner_login(app):
    """单个系统的登录和资源初始化"""

    login_cls = getattr(module, f"{snake_to_pascal(app)}Login")
    setattr(Http, app, login_cls(app))
    # Token 过期时间写入上下文
    token_expiry = CONTEXT.get(app).get("token_expiry")
    if token_expiry:
        expire_time = datetime.now() + timedelta(seconds=token_expiry)
        _FRAMEWORK_CONTEXT.set(app=app, key="expire_time", value=expire_time)


def login():
    def safe_call(func, name):
        try:
            logger.info(f"初始化{name}连接...")
            func()
            logger.info(f"{name}连接初始化成功")
        except (MysqlDBError, RedisDBError) as e:
            logger.error(f"{name}连接初始化异常: {e}")

    # 启动 MySQL 和 Redis 初始化线程
    threads = [
        threading.Thread(target=safe_call, args=(init_mysql, "MySQL")),
        threading.Thread(target=safe_call, args=(init_redis, "Redis"))
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    logger.info("登录账号".center(80, "*"))
    with ThreadPoolExecutor(max_workers=len(all_app)) as executor:
        futures = {executor.submit(inner_login, app): app for app in all_app}
        for future in as_completed(futures):
            future.result()

    logger.info("登录完成".center(80, "*"))
    return Http


def find_data_path_by_case(app, case_file_name):
    """
    基于case文件名称查找与之对应的yml文件路径
    :param app:
    :param case_file_name:
    :return:
    """
    env = CONTEXT.get("env")
    for file_path in Path(os.path.join(settings.DATA_DIR, env, app)).rglob(f"{case_file_name}.y*"):
        if file_path:
            return file_path


def subset_and_diff(small: set, big: set):
    """
    判断 small 是否为 big 的子集，并返回差集
    """
    return small.issubset(big), small - big


def disable_field(scenario, data):
    if not scenario:
        return data

    def _clean(obj):
        if isinstance(obj, dict):
            keys_to_delete = []
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    _clean(v)
                elif isinstance(v, str):
                    for ak, av in scenario.items():
                        if av == "disable" and v == f"${{{ak}}}":
                            keys_to_delete.append(k)
                            break
            # 统一删除，避免边遍历边删
            for k in keys_to_delete:
                del obj[k]

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    _clean(item)

    _clean(data)
    return data


def match_keyword(keyword_expr: str, target_str: str) -> bool:
    """
    按规则匹配字符串：
    - 空表达式：直接返回 True
    - 单个关键词：直接 in 判断
    - 多关键词：支持 and / or / not / 括号
    """
    if not keyword_expr.strip():
        return True  # 空关键字，默认匹配所有

    keyword_expr = keyword_expr.strip().lower()
    target_str = target_str.lower()

    # 单个关键词直接处理
    words = re.findall(r"[^\s()]+", keyword_expr)  # 提取非括号非空格的词
    if len(words) == 1:
        return words[0] in target_str

    # 带逻辑表达式
    # tokens 保留括号，分离 and/or/not/关键词
    tokens = re.findall(r"\(|\)|and|or|not|[^\s()]+", keyword_expr)

    expr_list = []
    for t in tokens:
        if t in {"and", "or", "not", "(", ")"}:
            expr_list.append(t)
        else:
            # 替换为 True/False
            expr_list.append(str(t in target_str))

    expr_str = " ".join(expr_list)
    try:
        return eval(expr_str)
    except Exception as e:
        logger.error(f"表达式解析错误: {e}, 表达式: {expr_str}")
        return False


def match_mark(keyword_expr: str, target_list: list[str]) -> bool:
    """
    按规则匹配目标列表：
    - 空表达式：直接返回 True
    - 单个关键词：精准匹配 target_list 中某个元素
    - 多个关键词：支持 and/or/not/括号
    """
    if not keyword_expr.strip():
        return True  # 空关键字，默认匹配所有

    keyword_expr = keyword_expr.strip().lower()
    target_list = [s.lower() for s in target_list]

    def contains(word: str) -> bool:
        """精准匹配：word 必须等于 target_list 的某个元素"""
        return word in target_list

    # tokens：保留括号，拆分 and/or/not/关键词
    tokens = re.findall(r"\(|\)|and|or|not|[^\s()]+", keyword_expr)

    expr_list = []
    for t in tokens:
        if t in {"and", "or", "not", "(", ")"}:
            expr_list.append(t)
        else:
            expr_list.append(str(contains(t)))

    expr_str = " ".join(expr_list)
    try:
        return eval(expr_str)
    except Exception as e:
        logger.error(f"表达式解析错误: {e}, 表达式: {expr_str}")
        return False


def init_allure(params):
    """设置allure中case的 title, description, level"""
    case_level_map = {
        "p0": allure.severity_level.BLOCKER,
        "p1": allure.severity_level.CRITICAL,
        "p2": allure.severity_level.NORMAL,
        "p3": allure.severity_level.MINOR,
        "p4": allure.severity_level.TRIVIAL,
    }
    allure.dynamic.title(params.get("title"))
    allure.dynamic.description(params.get("describe"))
    allure.dynamic.severity(case_level_map.get(params.get("level")))
    allure.dynamic.feature(params.get("module"))
    allure.dynamic.story(params.get("describe"))


# UPDATE 将用例 按类名进行分组的核心方法
def filtered_groupby(iterable, key_func):
    """生成器：过滤key_func返回None的元素，并按key_func分组"""
    current_key = None
    current_group = []

    for item in iterable:
        key = key_func(item)
        if key is None:
            continue  # 跳过key为None的元素

        # 处理分组逻辑（类似groupby）
        if key != current_key:
            if current_group:
                yield current_key, current_group
            current_key = key
            current_group = [item]
        else:
            current_group.append(item)

    # 输出最后一组
    if current_group:
        yield current_key, current_group


# UPDATE：按类的全路径 进行用例分组 同一个类的test方法分到一组
def __get_group_key__(item):
    return '::'.join(item.nodeid.split('::')[:2])


# UPDATE：改变pytest的原始排序规则
def sort(case_items):
    # 按测试类全路径分类,同一个类文件的用例归集到一起
    # 使用 groupby 函数进行分组
    item_group_list = [list(group) for _, group in filtered_groupby(case_items, __get_group_key__)]

    all_item_list = []
    clase_id = None
    for items in item_group_list:
        # 未被test_setup/test_teardown 标记的test方法
        non_custom_scope_items = [item for item in items if
                                  'test_setup' != item.originalname and 'test_teardown' != item.originalname]
        item_list = []
        # 用例的组数
        case_suite_num = 0
        # 生成每个组当前的索引
        ori_name_temp = None
        ori_name_list = []
        for item in non_custom_scope_items:
            clase_id = item.cls.__name__
            original_name = item.originalname
            if ori_name_temp is None or ori_name_temp == original_name:
                ori_name_temp = original_name
                case_suite_num += 1
                ori_name_list.append([original_name, item])
            else:
                break

        # 根据组数 创建各组的数组 并插入第一个case
        case_dict = dict()

        for i in range(case_suite_num):
            try:
                item = ori_name_list[i][1]
                id = item.callspec.id

                first_part = id.split('#', 1)[-1]
                index = first_part.split(']')[0]
                case_dict[index] = [item]
            except Exception as e:
                continue

        new_start_index = case_suite_num
        # 以new_start_index为起点 重新遍历items

        for i in range(new_start_index, len(non_custom_scope_items)):
            try:
                item = non_custom_scope_items[i]
                id = item.callspec.id
                first_part = id.split('#', 1)[-1]
                index = first_part.split(']')[0]
                case_dict.get(index).append(item)
            except Exception as e:
                continue

        index = 0
        for id in case_dict:
            index += 1
            case_item_list = case_dict.get(id)
            for item in case_item_list:
                allure_suite_mark = f'{clase_id}#{index}'
                setattr(item, 'allure_suite_mark', allure_suite_mark)
            item_list += case_item_list

        all_item_list += item_list

    return all_item_list
