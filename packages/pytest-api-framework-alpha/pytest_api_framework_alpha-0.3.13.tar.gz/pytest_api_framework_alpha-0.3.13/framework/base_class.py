import traceback
import importlib
from typing import Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse, urljoin

import pytest
from box import Box
from faker import Faker

from framework.db.redis_db import RedisDB
from framework.db.mysql_db import MysqlDB
from framework.utils.log_util import logger
from framework.render_data import RenderData
from framework.http_client import ResponseUtil
from framework.utils.date_util import DateUtil
from framework.utils.common import snake_to_pascal, SingletonFaker
from framework.global_attribute import GlobalAttribute, _FRAMEWORK_CONTEXT, CONTEXT
from framework.exceptions import ValidateException, RenderException, RequestException, GetAccountError, GetAppHttpError
from framework.utils.mock_util import get_customized_kytmock, set_customized_kytmock, PaymentType, RiskLevel, IsDelayed, \
    mock_mq

from handlers.extend_base_test_case_attr import ExtendBaseTestCase
from config.settings import UNAUTHORIZED_CODE, FAKER_LANGUAGE

module = importlib.import_module("test_case.conftest")


@dataclass
class Scenario:
    describe: str
    level: str
    data: Box
    expect: Box


class BaseTestCase(ExtendBaseTestCase):
    http = None
    data: Box = None
    belong_app = None
    scenario: Scenario = None
    response: ResponseUtil = None
    context: Union[GlobalAttribute, Box] = None
    config: Union[GlobalAttribute, Box] = None
    # faker方法文档 https://blog.csdn.net/m0_60052979/article/details/126368024
    faker: Faker = SingletonFaker(locale=FAKER_LANGUAGE).faker
    env = CONTEXT.get("env")
    logger: logger = logger

    date_util: DateUtil = DateUtil
    payment_type: PaymentType = PaymentType
    risk_level: RiskLevel = RiskLevel
    is_delayed: IsDelayed = IsDelayed

    def request(self, app=None, *, account, data, **kwargs) -> ResponseUtil:
        try:
            app = self.default_app(app)
            try:
                app_http = getattr(self.http, app)
            except AttributeError as e:
                raise GetAppHttpError(e)
            domain = self.context.get(app).get("domain")
            data = RenderData(data).render()
            data.request.url = self.replace_domain(data.request.url, domain)
            try:
                self.response = getattr(app_http, account).request(data=data, **kwargs)
            except AttributeError as e:
                raise GetAccountError(e)
            if self.response.status_code in UNAUTHORIZED_CODE:
                _http = _FRAMEWORK_CONTEXT.get(key="_http")
                setattr(_http, app, getattr(module, f"{snake_to_pascal(app)}Login")(app))
                token_expiry = self.context_get("token_expiry")
                expire_time = datetime.now() + timedelta(seconds=token_expiry)
                _FRAMEWORK_CONTEXT.set(app=app, key="expire_time", value=expire_time)
            return self.response

        except RenderException as e:
            logger.error(f"数据渲染异常: {e}")
            traceback.print_exc()
            pytest.fail(str(e))

        except GetAccountError as e:
            logger.error(f"获取账号{account}异常: {e}")
            traceback.print_exc()
            pytest.fail(str(e))

        except GetAppHttpError as e:
            logger.error(f"获取{app} http对象异常: {e}")
            traceback.print_exc()
            pytest.fail(str(e))

        except RequestException as e:
            logger.error(f"请求异常: {e}")
            traceback.print_exc()
            pytest.fail(str(e))

        except ValidateException as e:
            logger.error(f"断言异常: {e}")
            traceback.print_exc()
            pytest.fail(str(e))

        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            pytest.fail(str(e))

    def post(self, app, account, url, data=None, json=None, **kwargs) -> ResponseUtil:
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url), "data": data, "json": json}
        request.update({"method": "post", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def get(self, app, account, url, params=None, **kwargs) -> ResponseUtil:
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url), "params": params}
        request.update({"method": "get", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def put(self, app, account, url, data=None, json=None, **kwargs) -> ResponseUtil:
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url), "data": data, "json": json}
        request.update({"method": "put", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def delete(self, app, account, url, **kwargs) -> ResponseUtil:
        domain = self.context.get(app).get("domain")
        request = {"url": urljoin(domain, url)}
        request.update({"method": "delete", "headers": {}, **kwargs})
        return self.request(app=app, account=account, data=Box({"request": request}))

    def mysql_conn(self, db, app=None) -> MysqlDB:
        try:
            return _FRAMEWORK_CONTEXT.get(app=self.default_app(app), key="mysql").get(db)
        except AttributeError as e:
            logger.error(f"获取mysql连接异常: {e} {self.default_app(app)} {app} {db} ")
            traceback.print_exc()
            # pytest.exit(ExitCode.LOAD_DATABASE_INFO_ERROR)

    def redis_conn(self, db, index=0, app=None) -> RedisDB:
        try:
            return _FRAMEWORK_CONTEXT.get(app=self.default_app(app), key="redis").get(db)[index]
        except AttributeError as e:
            logger.error(f"获取redis连接异常: {e}")
            traceback.print_exc()
            # pytest.exit(ExitCode.LOAD_DATABASE_INFO_ERROR)

    def context_set(self, key, value):
        self.context.set(app=self.belong_app, key=key, value=value)

    def context_get(self, key):
        return self.context.get(app=self.belong_app, key=key)

    def default_app(self, app):
        return app or self.belong_app

    @staticmethod
    def replace_domain(url: str, new_base: str) -> str:
        """
        替换 URL 的 scheme 和 netloc（协议和域名）。
        :param url: 原始 URL
        :param new_base: 新的 base，如 'https://new.example.com'
        :return: 替换后的 URL
        """
        if url.startswith("http"):
            return url
        parsed_url = urlparse(url)
        new_base_parsed = urlparse(new_base)

        updated_url = parsed_url._replace(
            scheme=new_base_parsed.scheme,
            netloc=new_base_parsed.netloc
        )
        return urlunparse(updated_url)

    def get_customized_kytmock(self, request_id):
        return get_customized_kytmock(self.context.get("env"), request_id)

    def set_customized_kytmock(self, request_id, payment_type: PaymentType, risk_level: RiskLevel,
                               is_delayed: IsDelayed = IsDelayed.NO_DELAY):
        """
          参数:
            env: 环境名称（如
            "dev", "test"）
            request_id: 请求ID
            payment_type: 支付类型枚举
            risk_level: 风险等级枚举
            is_delayed: 是否延迟枚举，默认不延迟
            custom_url: 自定义URL（可选，用于临时测试特殊地址）

            返回:
            接口响应的JSON字典，失败则返回None

        """
        return set_customized_kytmock(self.context.get("env"), request_id, payment_type, risk_level, is_delayed)

    def mock_mq_message(self, target_exchange, exchange_type, message, routing_key: str = None):
        """
        target_exchange:目标交换机名称
        exchange_type：交换机类型，枚举：fanout，direct，topic，header
        message：消息体，json格式
        routing_key: 路由关键字，默认为null
        """
        return mock_mq(self.context.get("env"), target_exchange, exchange_type, message, routing_key)

    def regenerate_hot_wallet_for_psp(self, participant_code):
        """
        
        :param participant_code: partner或end-user的code
        :return: 
        """
        # 删除wallet_service中的钱包
        self.logger.info(f"重置{participant_code}热钱包")
        wallet_service = self.mysql_conn(db=self.db.DB_WALLET_SERVICE)
        wallet_service.execute(
            f"delete from tbl_wallet_coin where wallet_key in (select wallet_key from tbl_wallet where participant_code='{participant_code}');")
        wallet_service.execute(f"delete from tbl_wallet where  participant_code='{participant_code}';")
        # 删除blockchain_service中的钱包
        self.mysql_conn(self.db.DB_BLOCKCHAIN_SERVICE).execute(
            f"delete from hot_wallethsm where participant_code='{participant_code}';")
        # 删除crm中钱包
        crm = self.mysql_conn(db=self.db.DB_CAMP_CRM)
        crm.execute(
            f"delete from tbl_crypto_wallet where id in (select wallet_id from tbl_participant_crypto_wallet where participant_code='{participant_code}');")
        crm.execute(f"delete from tbl_participant_crypto_wallet where participant_code='{participant_code}';")

        # 重新生成新钱包
        self.post(
            app="camp_admin",
            account="admin",
            url="/prod-api/crm/participant/createHotWallet.do",
            json={"participantCode": participant_code}
        )
        assert self.response.code == 0

    def regenerate_hot_wallet_for_buyer(self, partner_account, merchant_participant_code, buyer_participant_code):
        """
        
        :param partner_account: partner账号
        :param merchant_participant_code: merchant code
        :param buyer_participant_code: buyer code
        :return: 
        """
        # 删除wallet_service中的钱包
        self.logger.info(f"重置{buyer_participant_code}热钱包")
        wallet_service = self.mysql_conn(db=self.db.DB_WALLET_SERVICE)
        wallet_service.execute(
            f"delete from tbl_wallet_coin where wallet_key in (select wallet_key from tbl_wallet where participant_code='{buyer_participant_code}');")
        wallet_service.execute(f"delete from tbl_wallet where  participant_code='{buyer_participant_code}';")
        # 删除blockchain_service中的钱包
        self.mysql_conn(self.db.DB_BLOCKCHAIN_SERVICE).execute(
            f"delete from hot_wallethsm where participant_code='{buyer_participant_code}';")
        # 删除crm中钱包
        crm = self.mysql_conn(db=self.db.DB_CAMP_CRM)
        crm.execute(
            f"delete from tbl_crypto_wallet where id in (select crypto_wallet_id from tbl_buyer_crypto_wallet where participant_code='{buyer_participant_code}');")
        crm.execute(f"delete from tbl_buyer_crypto_wallet where participant_code='{buyer_participant_code}';")

        # 重新生成新钱包
        self.post(
            app="psp_api",
            account=partner_account,
            url="/v1.0/crm/deposit/createWallet",
            json={
                "participantCode": merchant_participant_code,
                "buyerId": buyer_participant_code,
                "expiry": 0
            }
        )
        assert self.response.code == 200
