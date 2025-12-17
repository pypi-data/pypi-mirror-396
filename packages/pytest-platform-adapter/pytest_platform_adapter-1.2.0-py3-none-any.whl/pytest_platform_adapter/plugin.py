import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import requests
from allure_pytest.utils import allure_label, allure_title
import logging
import pytest
from _pytest.stash import StashKey

logger = logging.getLogger('pytest-platform-adapter')
logger.setLevel(logging.INFO)

# 全局变量用于统计测试用例状态
test_stats = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'current': 0  # 当前已执行的用例数
}
milestone_counter = 10  # 里程碑计数器
failed_cases = set()  # 记录已标记为失败的用例
skipped_cases = set()  # 记录已标记为跳过的用例
cases_ids = set()  # 存放所有用例ID，用来检查是否有重复的
scan_enable = False  # 记录是否扫描模式，默认为False非扫描模式，True为扫描模式
platform_ip = None
platform_port = None
platform_path = None
pipeline_name = None
build_number = None
platform_use_https = False
ENV_SETTINGS_KEY: StashKey["EnvCheckSettings"] = StashKey()
ENV_RUNTIME_KEY: StashKey["EnvCheckRuntime"] = StashKey()
ITEM_KIND_KEY: StashKey[str] = StashKey()
BEHAVIOR_KEY: StashKey[Optional[str]] = StashKey()
ENV_XFAIL_REASON_KEY: StashKey[Optional[str]] = StashKey()
FORCED_ITEMS_KEY: StashKey[List[pytest.Item]] = StashKey()
STASH_SENTINEL = object()


@dataclass
class EnvCheckSettings:
    mode: str = 'all'
    behavior_scope: str = 'feature'
    fail_action: str = 'skip'
    collect_mode: str = 'force'  # force(强制)/auto(自动)
    global_nodeids: List[str] = field(default_factory=list)
    behavior_nodeids: List[str] = field(default_factory=list)

    def enable_global(self) -> bool:
        return self.mode in {'global', 'all'} and bool(self.global_nodeids)

    def enable_behavior(self) -> bool:
        return self.mode in {'behavior', 'all'} and bool(self.behavior_nodeids)

    def enabled(self) -> bool:
        if self.mode == 'off':
            return False
        return self.enable_global() or self.enable_behavior()


@dataclass
class EnvCheckRuntime:
    global_failures: Dict[str, str] = field(default_factory=dict)
    behavior_failures: Dict[str, str] = field(default_factory=dict)

    def first_global_failure(self) -> Optional[str]:
        if not self.global_failures:
            return None
        return next(iter(self.global_failures.values()))


def pytest_addoption(parser):
    group = parser.getgroup('platform-adapter', '自动化平台插件')
    group.addoption(
        '--case_ids',
        action='store',
        default=None,
        help='要执行的测试用例ID列表，使用逗号分隔，例如：19936,19930'
    )
    group.addoption(
        '--case_ids_file',
        action='store',
        default=None,
        help='包含测试用例ID的文件路径，文件中每行一个ID'
    )
    group.addoption(
        '--scan',
        action='store_true',
        default=False,
        help='扫描模式：快速生成 Allure 报告而不实际执行测试'
    )
    group.addoption(
        '--env-check-mode',
        action='store',
        default='all',
        choices=['off', 'global', 'behavior', 'all'],
        help='环境检查模式：off(禁用)/global(仅全局)/behavior(仅行为)/all(全部)'
    )
    group.addoption(
        '--env-check-scope',
        action='store',
        default=None,
        help='特性级检查所使用的 Allure 标签层级：epic/feature/story'
    )
    group.addoption(
        '--env-check-collect-mode',
        action='store',
        default=None,
        choices=['force', 'auto'],
        help='环境检查收集模式覆盖：force(强制收集并执行)/auto(仅执行已收集到的检查用例)'
    )
    parser.addini(
        'platform_ip',
        help='自动化平台API IP',
        default=None
    )
    parser.addini(
        'platform_port',
        help='自动化平台API端口',
        default=None
    )
    parser.addini(
        'platform_path',
        help='自动化平台API Path',
        default='/api/autoplatform/task/refresh_data_count'
    )
    parser.addini(
        'platform_use_https',
        help='上报自动化平台时启用HTTPS，默认不启用',
        default=False
    )
    parser.addini(
        'platform_env_global_checks',
        type='linelist',
        help='全局环境检查用例的绝对NodeID列表',
        default=[]
    )
    parser.addini(
        'platform_env_behavior_checks',
        type='linelist',
        help='特性级环境检查用例的绝对NodeID列表',
        default=[]
    )
    parser.addini(
        'platform_env_behavior_scope',
        help='特性级检查的Allure层级（epic/feature/story）',
        default='feature'
    )
    parser.addini(
        'platform_env_fail_action',
        help='环境检查失败后对业务用例的处理方式（skip/xfail/none）',
        default='skip'
    )
    parser.addini(
        'platform_env_collect_mode',
        help='环境检查收集模式：force(强制收集并执行)/auto(仅执行已收集到的检查用例)',
        default='force'
    )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_collection_modifyitems(config, items):
    """
    hook收集用例的过程，给--case_ids和--case_ids_file提供支持
    修改测试用例集合，根据提供的测试用例ID过滤测试用例
    """
    settings = get_env_settings(config)
    forced_nodeids = _collect_forced_nodeids(settings)
    # 预先快照强制环境检查用例，供后续无视 -m / -k 过滤使用。
    if env_checks_enabled(settings) and settings.collect_mode == 'force':
        forced_items: List[pytest.Item] = []
        seen: Set[str] = set()
        for item in items:
            if _is_forced_item(item.nodeid, forced_nodeids) and item.nodeid not in seen:
                forced_items.append(item)
                seen.add(item.nodeid)
        config.stash[FORCED_ITEMS_KEY] = forced_items
    yield
    # 缺失检查告警：force 模式下使用 pre-deselect 的快照判断，避免被 -m/-k 误判。
    if env_checks_enabled(settings) and settings.collect_mode == 'force':
        forced_items_snapshot = config.stash.get(FORCED_ITEMS_KEY, [])
        available_ids = {item.nodeid for item in forced_items_snapshot}
    else:
        available_ids = {item.nodeid for item in items}
    missing_forced: List[str] = []
    for prefix in forced_nodeids:
        if not any(n == prefix or n.startswith(prefix + "::") for n in available_ids):
            missing_forced.append(prefix)
    for missing in sorted(missing_forced):
        logger.warning(f"配置的环境检查用例 {missing} 未被收集，检查 NodeID 是否正确")

    target_ids = get_target_test_ids(config)
    selected = []
    deselected = []
    for item in items:
        nodeid = item.nodeid
        should_force_run = _is_forced_item(nodeid, forced_nodeids)
        title = allure_title(item)
        test_id = get_test_id_from_title(title)
        if not target_ids or should_force_run or test_id in target_ids:
            selected.append(item)
        else:
            deselected.append(item)
        # 检测 ID 是否有重复，只是单纯的检查一下，不影响执行。用例 id 为 1 的是环境检查脚本
        if test_id in cases_ids and test_id != "0":
            # 为 None 在这里就不用打印log了，因为在 get_test_id_from_title 里面就会报错一次
            if test_id is None:
                continue
            logger.warning(f"测试用例ID {test_id} 重复")
        else:
            cases_ids.add(test_id)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected

    # force 模式下无视 -m / -k 的 deselect：把缓存的环境检查重新插回来
    if env_checks_enabled(settings) and settings.collect_mode == 'force':
        forced_items = config.stash.get(FORCED_ITEMS_KEY, [])
        current_ids = {item.nodeid for item in items}
        for forced_item in forced_items:
            if forced_item.nodeid not in current_ids:
                items.append(forced_item)
                current_ids.add(forced_item.nodeid)

    selected_ids = [get_test_id_from_title(allure_title(item)) for item in items]
    test_stats['total'] = len(items)  # 更新总用例数
    if target_ids:
        logger.info("目标测试用例ID (%d个): %s", len(target_ids), target_ids)
        logger.info("实际执行用例ID (%d个): %s", len(selected_ids), selected_ids)
    if env_checks_enabled(settings):
        _apply_env_check_collection_logic(config, settings, items)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    if item.config.getoption('--scan'):
        # logger.info(f"扫描模式：跳过执行测试用例 {allure_title(item)}")
        pytest.skip("扫描模式已启动，跳过执行测试用例")
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    if item.config.getoption('--scan'):
        # logger.info(f"扫描模式：跳过测试用例 {allure_title(item)}前置")
        pytest.skip("扫描模式已启动，跳过测试用例前置")
    settings = get_env_settings(item.config)
    if env_checks_enabled(settings):
        runtime = get_env_runtime(item.config)
        kind = _get_item_kind(item)
        global_reason = runtime.first_global_failure()
        if global_reason and kind != 'global_check':
                _apply_env_failure_action(settings, item, global_reason)
        elif kind == 'business':
            behavior = _ensure_behavior_stashed(item, settings.behavior_scope)
            behavior_reason = runtime.behavior_failures.get(behavior) if behavior else None
            if behavior_reason:
                _apply_env_failure_action(settings, item, behavior_reason)
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item):
    if item.config.getoption('--scan'):
        # logger.info(f"扫描模式：跳过测试用例 {allure_title(item)}后置")
        pytest.skip("扫描模式已启动，跳过测试用例后置")
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    settings = get_env_settings(item.config)
    if not env_checks_enabled(settings):
        return
    if report.when != 'call':
        return
    kind = _get_item_kind(item)
    if kind not in {'global_check', 'behavior_check'}:
        return
    runtime = get_env_runtime(item.config)
    if report.failed:
        reason = _format_env_failure_message(kind, item, report)
        if kind == 'global_check':
            runtime.global_failures[item.nodeid] = reason
        else:
            behavior = _ensure_behavior_stashed(item, settings.behavior_scope)
            if behavior:
                runtime.behavior_failures[behavior] = reason
            else:
                logger.warning("特性级环境检查 %s 缺少 %s 标签，无法绑定到具体行为", item.nodeid,
                               settings.behavior_scope)
    else:
        if kind == 'global_check':
            runtime.global_failures.pop(item.nodeid, None)
        else:
            behavior = _ensure_behavior_stashed(item, settings.behavior_scope)
            if behavior:
                runtime.behavior_failures.pop(behavior, None)


@pytest.hookimpl
def pytest_runtest_logreport(report):
    """
    hook测试用例执行结果的输出过程
    """
    global milestone_counter, scan_enable, platform_ip, platform_port, platform_path, platform_use_https
    global pipeline_name, build_number
    # config = pytest.Config
    # my_option = config.getini("my_option")
    # 使用 report.nodeid 作为唯一标识
    nodeid = report.nodeid

    if report.when in ['setup', 'call', 'teardown']:
        # 记录失败状态，如果该用例任意阶段失败，则添加到 failed_cases
        if report.failed:
            failed_cases.add(nodeid)

        # 记录跳过状态，仅在 setup 阶段处理
        if report.skipped and report.when == 'setup':
            skipped_cases.add(nodeid)
            test_stats['skipped'] += 1

        # 仅在 teardown 阶段完成统计更新
        if report.when == 'teardown':
            test_stats['current'] += 1
            # 检查用例是否为失败、跳过或通过
            if nodeid in failed_cases:
                # TODO Xfail 应该计算为失败，但是不太对
                test_stats['failed'] += 1
            elif nodeid in skipped_cases:
                # 如果用例已跳过，不计为通过
                pass
            else:
                test_stats['passed'] += 1

            # 打印进度和统计信息
            progress = (test_stats['current'] / test_stats['total']) * 100 if test_stats['total'] != 0 else 0
            pass_rate = (test_stats['passed'] / (test_stats['total'] - test_stats['skipped'])) * 100 if (
                    (test_stats['total'] - test_stats['skipped']) != 0) else 0
            logger.info(
                f"pipeline_name:{pipeline_name}, build_number: {build_number}"
                f"用例进度: 总数 {test_stats['total']}, 跳过 {test_stats['skipped']}, 已执行 {test_stats['current']}, "
                f"失败 {test_stats['failed']}, 通过 {test_stats['passed']}, 进度 {progress:.2f}%, 通过率 {pass_rate:.2f}%"
            )

            # 当没有启用扫描模式、同时配置了平台的IP和端口的时候才回报给自动化平台
            if not scan_enable and platform_ip and platform_port:
                # 在执行前10个用例的时候，进度立即回报给平台进度。之后就是每隔10个用例再回报一次
                if test_stats['current'] <= 10 or test_stats['current'] % 10 == 0:
                    json_data = None
                    url = f"http://{platform_ip}:{platform_port}{platform_path}" if not platform_use_https \
                        else f"https://{platform_ip}:{platform_port}{platform_path}"
                    try:
                        json_data = {
                            'pipeline': pipeline_name,
                            'build_number': build_number,
                            'passed_case_count': test_stats['passed'],
                            'skipped_case_count': test_stats['skipped'],
                            'failed_case_count': test_stats['failed'],
                            'selected_case': test_stats['total'] }
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(url, data=json.dumps(json_data), headers=headers, timeout=3)
                        logger.info(f"已将数据回报给 {url}，"
                                    f"平台返回状态码：{response.status_code}，"
                                    f"响应体：{response.text}，请求体：{json_data}")
                    except Exception as e:
                        logger.info(f"将请求发送到 {url}"
                                    f"，请求体：{json_data} 错误信息：{e}")


def pytest_configure(config):
    global scan_enable, platform_ip, platform_port, platform_path
    global pipeline_name, build_number
    scan_enable, platform_ip, platform_port, platform_path, platform_use_https = config.getoption(
        '--scan'), config.getini('platform_ip'), config.getini('platform_port'), config.getini(
        'platform_path'), config.getini('platform_use_https')
    settings = build_env_check_settings(config)
    config.stash[ENV_SETTINGS_KEY] = settings
    config.stash[ENV_RUNTIME_KEY] = EnvCheckRuntime()
    # 在强制模式下，将声明的环境检查 NodeID 注入到 pytest 收集参数中，
    # 以保证即使用户只选择了业务目录也能收集到检查用例。
    if env_checks_enabled(settings) and settings.collect_mode == 'force':
        try:
            from pathlib import Path

            existing_args = set(config.args or [])
            rootpath = getattr(config, "rootpath", Path.cwd())
            forced_args: List[str] = []
            for nodeid in _collect_forced_nodeids(settings):
                if nodeid in existing_args:
                    continue
                # 仅对文件路径存在的 NodeID 进行注入，避免明显的 not found。
                path_part = nodeid.split("::", 1)[0]
                p = Path(path_part)
                if not p.is_absolute():
                    p = rootpath / p
                if p.exists():
                    forced_args.append(nodeid)
                else:
                    logger.warning("强制收集环境检查失败：文件不存在 %s", nodeid)
            if forced_args:
                config.args.extend(forced_args)
                logger.debug("已强制注入环境检查收集参数: %s", forced_args)
        except Exception as e:
            logger.warning("强制收集环境检查参数注入异常：%s", e)
    pipeline_name = os.environ.get("JOB_NAME")
    build_number = os.environ.get("BUILD_NUMBER")
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('自动化平台插件 - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    config.addinivalue_line(
        "markers",
        "allure_title: 使用allure标题标记测试用例"
    )
    config.addinivalue_line(
        "markers",
        "environment_check: 标记环境检查用例"
    )


def get_test_ids_from_file(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def get_test_ids_from_option(ids_string: str) -> List[str]:
    case_id = []
    for id_ in ids_string.strip(',').split(','):
        id_strip = id_.strip()
        if not id_strip.isdigit():
            logger.error(f'存在无效的测试用例ID：{id_}')
            continue
        else:
            case_id.append(id_strip)
    return case_id


def get_target_test_ids(config) -> Optional[List[str]]:
    case_ids = config.getoption('--case_ids')
    case_ids_file = config.getoption('--case_ids_file')
    if case_ids:
        logger.info(f"接收到case_ids入参为：'{case_ids}'")
        return get_test_ids_from_option(case_ids)
    elif case_ids_file:
        logger.info(f"接收到case_ids_file入参为：'{case_ids_file}'")
        return get_test_ids_from_file(case_ids_file)
    return None


def get_test_id_from_title(title: Optional[str]) -> Optional[str]:
    if not title:
        return None
    match = title.split('-', 1)
    if len(match) != 2:
        logger.error(f'存在无法解析用例ID的用例，用例标题为：{title}')
        return None
    if match[0].isdigit():
        return match[0]
    else:
        logger.error(f'存在无法解析用例ID的用例，用例标题为：{title}')
        return None


def build_env_check_settings(config) -> EnvCheckSettings:
    mode = config.getoption('--env-check-mode') or 'all'
    scope_opt = config.getoption('--env-check-scope')
    scope_ini = config.getini('platform_env_behavior_scope') or 'feature'
    scope = (scope_opt or scope_ini or 'feature').strip().lower()
    if scope not in {'epic', 'feature', 'story'}:
        logger.warning("未识别的行为层级 %s，回退到 feature", scope)
        scope = 'feature'
    fail_action_raw = config.getini('platform_env_fail_action')
    fail_action = (fail_action_raw or 'skip').strip().lower()
    if fail_action not in {'skip', 'xfail', 'none'}:
        logger.warning("platform_env_fail_action=%s 不受支持，改用 skip", fail_action_raw)
        fail_action = 'skip'
    collect_mode_opt = config.getoption('--env-check-collect-mode')
    collect_mode_raw = collect_mode_opt or config.getini('platform_env_collect_mode')
    collect_mode = (collect_mode_raw or 'force').strip().lower()
    if collect_mode in {'强制'}:
        collect_mode = 'force'
    elif collect_mode in {'自动'}:
        collect_mode = 'auto'
    if collect_mode not in {'force', 'auto'}:
        logger.warning("platform_env_collect_mode=%s 不受支持，改用 force", collect_mode_raw)
        collect_mode = 'force'
    global_nodes = _normalize_nodeids(config.getini('platform_env_global_checks'))
    behavior_nodes = _normalize_nodeids(config.getini('platform_env_behavior_checks'))
    if mode not in {'off', 'global', 'behavior', 'all'}:
        logger.warning("未识别的 env-check-mode %s，回退到 all", mode)
        mode = 'all'
    return EnvCheckSettings(
        mode=mode,
        behavior_scope=scope,
        fail_action=fail_action,
        collect_mode=collect_mode,
        global_nodeids=global_nodes,
        behavior_nodeids=behavior_nodes,
    )


def env_checks_enabled(settings: Optional[EnvCheckSettings]) -> bool:
    return bool(settings and settings.enabled())


def _normalize_nodeids(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    normalized = []
    for nodeid in values:
        if not nodeid:
            continue
        value = nodeid.strip()
        if value:
            normalized.append(value)
    return normalized


def get_env_settings(config) -> EnvCheckSettings:
    return config.stash.get(ENV_SETTINGS_KEY, EnvCheckSettings())


def get_env_runtime(config) -> EnvCheckRuntime:
    return config.stash.get(ENV_RUNTIME_KEY, EnvCheckRuntime())


def _collect_forced_nodeids(settings: Optional[EnvCheckSettings]) -> Set[str]:
    if not env_checks_enabled(settings):
        return set()
    forced = set()
    if settings.enable_global():
        forced.update(settings.global_nodeids)
    if settings.enable_behavior():
        forced.update(settings.behavior_nodeids)
    return forced


def _is_forced_item(nodeid: str, forced_nodeids: Set[str]) -> bool:
    """支持用父级 NodeID（如模块/类）声明的强制收集。"""
    if nodeid in forced_nodeids:
        return True
    for forced in forced_nodeids:
        if nodeid.startswith(forced + "::"):
            return True
    return False


def _apply_env_check_collection_logic(config, settings: EnvCheckSettings, items: List[pytest.Item]) -> None:
    ordered: List[pytest.Item] = []
    consumed: Set[str] = set()
    missing_behaviors: List[str] = []

    # 1) 全局检查：支持使用模块/类 NodeID 作为前缀声明。
    for prefix in settings.global_nodeids:
        for item in items:
            if item.nodeid in consumed:
                continue
            if item.nodeid == prefix or item.nodeid.startswith(prefix + "::"):
                ordered.append(item)
                consumed.add(item.nodeid)
                item.stash[ITEM_KIND_KEY] = 'global_check'
                item.stash[BEHAVIOR_KEY] = None

    # 2) 特性级检查：同样支持前缀声明，按行为（epic/feature/story）绑定。
    behavior_checks: Dict[str, pytest.Item] = {}
    for prefix in settings.behavior_nodeids:
        for item in items:
            if item.nodeid in consumed:
                continue
            if item.nodeid != prefix and not item.nodeid.startswith(prefix + "::"):
                continue
            behavior = _ensure_behavior_stashed(item, settings.behavior_scope)
            if not behavior:
                missing_behaviors.append(item.nodeid)
                continue
            if behavior in behavior_checks:
                logger.warning(
                    "特性级检查 %s 重复定义，沿用首次声明的用例 %s",
                    behavior,
                    behavior_checks[behavior].nodeid,
                )
                continue
            behavior_checks[behavior] = item
            consumed.add(item.nodeid)
            item.stash[ITEM_KIND_KEY] = 'behavior_check'

    if missing_behaviors:
        logger.warning(
            "下列特性级检查缺少 %s 标签：%s",
            settings.behavior_scope,
            missing_behaviors,
        )

    # 3) 按业务用例的行为插入对应检查。
    behavior_inserted: Set[str] = set()
    for item in items:
        if item.nodeid in consumed:
            continue
        if item.stash.get(ITEM_KIND_KEY, STASH_SENTINEL) is STASH_SENTINEL:
            item.stash[ITEM_KIND_KEY] = 'business'
        behavior = _ensure_behavior_stashed(item, settings.behavior_scope)
        if behavior and behavior in behavior_checks and behavior not in behavior_inserted:
            ordered.append(behavior_checks[behavior])
            behavior_inserted.add(behavior)
        ordered.append(item)

    # 4) 未匹配到业务用例的特性级检查：force 模式下不执行；auto 模式保持原行为（放到末尾执行）。
    if settings.collect_mode != 'force':
        for behavior, check_item in behavior_checks.items():
            if behavior not in behavior_inserted:
                ordered.append(check_item)
                behavior_inserted.add(behavior)

    if ordered:
        items[:] = ordered
    logger.debug(
        "最终的环境检查执行顺序: %s",
        [item.nodeid for item in items],
    )


def _ensure_behavior_stashed(item: pytest.Item, scope: str) -> Optional[str]:
    behavior = item.stash.get(BEHAVIOR_KEY, STASH_SENTINEL)
    if behavior is not STASH_SENTINEL:
        return behavior
    labels = allure_label(item, scope) or []
    value = labels[0] if labels else None
    item.stash[BEHAVIOR_KEY] = value
    return value


def _get_item_kind(item: pytest.Item) -> Optional[str]:
    return item.stash.get(ITEM_KIND_KEY, None)


def _apply_env_failure_action(settings: EnvCheckSettings, item: pytest.Item, reason: str) -> None:
    if settings.fail_action == 'none':
        return
    if settings.fail_action == 'xfail':
        _mark_item_expected_failure(item, reason)
        return
    pytest.skip(reason)


def _mark_item_expected_failure(item: pytest.Item, reason: str) -> None:
    existing = item.stash.get(ENV_XFAIL_REASON_KEY, None)
    if existing:
        return
    item.add_marker(pytest.mark.xfail(reason=reason, run=True, strict=False))
    item.stash[ENV_XFAIL_REASON_KEY] = reason


def _format_env_failure_message(kind: str, item: pytest.Item, report: pytest.TestReport) -> str:
    prefix = "全局" if kind == 'global_check' else "特性级"
    detail = ""
    longrepr = getattr(report, "longreprtext", "")
    if longrepr:
        first_line = longrepr.strip().splitlines()[0]
        if first_line:
            detail = f": {first_line}"
    return f"{prefix}环境检查失败（{item.nodeid}）{detail}"
