import requests
from enum import Enum, unique
from typing import Dict, Optional

from config.settings import AVAILABLE_ENVS, ENV_CONFIG


@unique
class PaymentType(Enum):
    """支付类型枚举"""
    DEPOSIT = 0  # 入金
    WALLET_SCANNING = 1  # 出金
    CHECKOUT = 2  # 结账


@unique
class RiskLevel(Enum):
    """风险等级枚举"""
    DISABLE_MOCK = 0  # 禁用模拟
    LOW = 1  # 低风险
    MEDIUM_LOW = 2  # 中低风险
    MEDIUM_HIGH = 3  # 中高风险
    HIGH = 4  # 高风险
    SEVERE = 5  # 严重风险
    PENDING_KYT = 6  # 严重风险


@unique
class IsDelayed(Enum):
    """是否延迟枚举"""
    NO_DELAY = 0  # 不延迟
    DELAY = 1  # 延迟


def get_environment_config(env: str) -> Dict:
    """
    获取指定环境的完整配置

    参数:
        env: 环境名称（如"dev", "test"等）

    返回:
        对应环境的配置字典

    异常:
        ValueError: 当环境名称不存在时抛出
    """
    if env not in AVAILABLE_ENVS:
        raise ValueError(f"不支持的环境: {env}，可用环境: {AVAILABLE_ENVS}")
    return ENV_CONFIG[env]


def get_full_api_url(env,method):
    """拼接完整的API URL"""
    config = get_environment_config(env)
    return f"{config['base_url']}{config[method]}"


def set_customized_kytmock(env: str,request_id: str, payment_type: PaymentType,risk_level: RiskLevel,is_delayed: IsDelayed = IsDelayed.NO_DELAY):
    """
    调用指定环境的HTTP接口

    参数:
        env: 环境名称（如"dev", "test"）
        request_id: 请求ID
        payment_type: 支付类型枚举
        risk_level: 风险等级枚举
        is_delayed: 是否延迟枚举，默认不延迟
        custom_url: 自定义URL（可选，用于临时测试特殊地址）

    返回:
        接口响应的JSON字典，失败则返回None
    """
    # 获取环境配置
    env_config = get_environment_config(env)
    method = "set_mock"
    url = get_full_api_url(env,method)

    # 参数验证
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("request_id必须是非空字符串")

    for param, name in [
        (payment_type, "payment_type"),
        (risk_level, "risk_level"),
        (is_delayed, "is_delayed")
    ]:
        if not isinstance(param, (PaymentType, RiskLevel, IsDelayed)):
            raise ValueError(f"{name}必须是对应的枚举类型")

    # 构建请求参数
    payload = {
        "request_id": request_id,
        "payment_type": payment_type.value,
        "risk_level": risk_level.value,
        "is_delayed": is_delayed.value
    }

    try:
        # 使用环境配置中的超时时间
        response = requests.post(
            url,
            json=payload,
            timeout=env_config["timeout"]
        )
        response.raise_for_status()

        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误 [{env}]: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常 [{env}]: {e}")
    except ValueError:
        print(f"响应解析失败 [{env}]")

    return None


def get_customized_kytmock(env,request_id):
    # 获取环境配置
    env_config = get_environment_config(env)

    # 参数验证
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("request_id必须是非空字符串")
    method = f"get_mock"
    url = f"{get_full_api_url(env, method)}{request_id}"
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误 [{env}]: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常 [{env}]: {e}")
    except ValueError:
        print(f"响应解析失败 [{env}]")

    return None

def mock_mq(env,target_exchange,exchange_type,message,routing_key):
    # 获取环境配置
    env_config = get_environment_config(env)
    method = "mock_mq"
    url = get_full_api_url(env,method)
    # 参数验证
    if not isinstance(target_exchange, str) or not target_exchange:
        raise ValueError("target_exchange必须是非空字符串")
    if not isinstance(exchange_type,str ) or not exchange_type:
        raise ValueError("exchange_type 必须是非空字符串")
    if not isinstance(message,str ) or not message:
        raise ValueError("message 必须是非空字符串")
    # 构建请求参数
    payload = {
            "targetExchange": target_exchange,
            "targetExchangeType": exchange_type,
            "message": message,
            "targetRoutingKey": routing_key
        }

    try:
        # 使用环境配置中的超时时间
        response = requests.post(
            url,
            json=payload,
            timeout=env_config["timeout"]
        )
        response.raise_for_status()

        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误 [{env}]: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常 [{env}]: {e}")
    except ValueError:
        print(f"响应解析失败 [{env}]")

    return None

if __name__ == "__main__":
    # # 1. 调用测试环境的入金接口
    # test_deposit = set_customized_kytmock(
    #     env="dev",
    #     request_id="A0101585",
    #     payment_type=PaymentType.DEPOSIT,
    #     risk_level=RiskLevel.LOW
    # )
    # print(f"测试环境入金响应: {test_deposit}")
    #
    # # 2. 调用测试环境的出金接口
    # dev_withdrawal = set_customized_kytmock(
    #     env="dev",
    #     request_id="0xf3C3e95597544cD0525393CE49B685994b8e50A7",
    #     payment_type=PaymentType.WITHDRAWAL,
    #     risk_level=RiskLevel.LOW
    # )
    # print(f"开发环境出金响应: {dev_withdrawal}")

    # get_content = get_customized_kytmock("dev","A0101585")
    # print(f"查询结果：{get_content}")
    exchange_name = "camp.gateway.backbone.mock.ex.order-status"
    exchange_type = "fanout"
    message = "{ \"avgFillPrice\": 440.23, \"filled\": 11.0000000000000000, \"orderId\": 409, \"remaining\": 0.0000000000000000, \"status\": \"Filled\" }"
    result = mock_mq("dev",exchange_name,exchange_type,message)
    print(result)

