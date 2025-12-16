import re

import allure
import pytest
from box import Box, BoxList
from jsonpath import jsonpath

from config.settings import RESPONSE_ATTR
from framework.utils.log_util import logger
from framework.render_data import RenderData
from framework.utils.common import an2cn, is_digit
from framework.exceptions import ValidateException


class Validate(object):
    def __init__(self, data, response):
        self.data = data
        self.response = response

        self.mapping = {
            "eq": "assert_equal",
            "not_eq": "assert_not_equal",
            "lt": "assert_less_than",
            "le": "assert_less_than_or_equals",
            "gt": "assert_greater_than",
            "ge": "assert_greater_than_or_equals",
            "len_eq": "assert_length_equals",
            "len_lt": "assert_length_less_than",
            "len_le": "assert_length_less_than_or_equals",
            "len_gt": "assert_length_greater_than",
            "len_ge": "assert_length_greater_than_or_equals",
            "contains": "assert_contains",
            "contained_by": "assert_contained_by",
            "startswith": "assert_startswith",
            "endswith": "assert_endswith",
            "is_null": "assert_is_null",
            "not_null": "assert_is_not_null",
        }

    def valid(self, validates):
        for valid_item in validates:
            key = list(valid_item.keys())[0]
            valid_list = [i.strip() for i in valid_item.get(key).split(",", 1)]
            expression = valid_list[0]
            try:
                expectant_result = valid_list[1]
            except IndexError:
                expectant_result = ""
            func = self.mapping.get(key)
            try:
                if func:
                    result = getattr(self, func)(expression, expectant_result.strip())
                    with allure.step(
                            f"断言({an2cn(validates.index(valid_item) + 1)}): 断言类型: {self.mapping.get(key)}, 断言内容: {valid_list}, 断言结果: {result}"):
                        logger.info(
                            f"断言({an2cn(validates.index(valid_item) + 1)}): 断言类型: {self.mapping.get(key)}, 断言内容: {valid_list}, 断言结果: {result}")
                else:
                    logger.error(f"不支持的断言方式: {key}")
            except Exception as e:
                allure.step(
                    f"断言({an2cn(validates.index(valid_item) + 1)}): 断言类型: {self.mapping.get(key)}, 断言内容: {valid_list}, 断言结果: 失败  失败原因: {str(e)}")
                raise ValidateException(
                    f"断言({an2cn(validates.index(valid_item) + 1)}): 断言类型: {self.mapping.get(key)}, 断言内容: {valid_list}, 断言结果: 失败  失败原因: {str(e)}")

    def parse_expectant_expression(self, expectant_expression):

        # jsonpath表达式取值
        if expectant_expression.lower().startswith("$."):
            return self.exec_jsonpath(expectant_expression)
        # 正则表达式取值
        elif expectant_expression.startswith("/") and expectant_expression.endswith("/"):
            return self.exec_reg(expectant_expression[1: -1])
        else:
            # box句点表达式
            return self.exec_box(expectant_expression)

    def exec_jsonpath(self, expression):
        try:
            return jsonpath(self.response.json(), expression)[0]
        except Exception as e:
            raise Exception(f"jsonpath表达式错误或非预期响应内容{e} 表达式: {expression};响应内容: {self.response}")

    def exec_reg(self, reg_expression):
        try:
            result = re.search(reg_expression, self.response.text, flags=re.S).group()
            if is_digit(result):
                return eval(result)
            else:
                return result
        except Exception as e:
            raise Exception(f"正则表达式或非预期响应内容{e} 表达式: {reg_expression}; 响应内容: {self.response.text}")

    def exec_box(self, expression):
        try:
            if expression in RESPONSE_ATTR:
                return getattr(self.response, expression)
            return self.get_nested_value(Box(self.response.json()), expression)
        except Exception as e:
            raise Exception(f"box表达式或响应内容异常{e} 表达式: {expression}; 响应内容: {self.response.text}")

    @staticmethod
    def get_nested_value(obj, attr_path):
        """通过字符串路径（如 'a.b[0].c'）获取嵌套属性值"""
        # 使用正则表达式分解路径，支持属性和索引的组合
        path_elements = re.findall(r'(\w+)|\[(\d+)]', attr_path)
        try:
            for attr, index in path_elements:
                if attr:  # 属性部分
                    obj = getattr(obj, attr)
                if index:  # 索引部分
                    obj = obj[int(index)]
            return obj
        except Exception:
            return None

    def assert_equal(self, expectant_expression, practical_result):
        expectant_result = self.parse_expectant_expression(expectant_expression)
        if isinstance(expectant_result, (int, float)) and isinstance(practical_result, str):
            if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith(
                    "}"):
                practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
            else:
                practical_result = eval(practical_result)
        assert practical_result == expectant_result, f'{expectant_result} == {practical_result}'
        return f'{expectant_result} == {practical_result}'

    def assert_not_equal(self, expectant_expression, practical_result):
        expectant_result = self.parse_expectant_expression(expectant_expression)
        if isinstance(expectant_result, (int, float)) and isinstance(practical_result, str):
            if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith(
                    "}"):
                practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
            else:
                practical_result = eval(practical_result)
        assert practical_result != expectant_result, f'{expectant_result} != {practical_result}'
        return f'{expectant_result} != {practical_result}'

    def assert_less_than(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_digit(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result < practical_result, f'{expectant_result} < {practical_result}'
        return f'{expectant_result} < {practical_result}'

    def assert_less_than_or_equals(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_digit(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result <= practical_result, f'{expectant_result} <= {practical_result}'
        return f'{expectant_result} <= {practical_result}'

    def assert_greater_than(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_digit(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result > practical_result, f'{expectant_result} > {practical_result}'
        return f'{expectant_result} > {practical_result}'

    def assert_greater_than_or_equals(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_digit(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result >= practical_result, f'{expectant_result} >= {practical_result}'
        return f'{expectant_result} >= {practical_result}'

    def assert_contains(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert practical_result in expectant_result, f'{practical_result} in {expectant_result}'
        return f'{practical_result} in {expectant_result}'

    def assert_contained_by(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result in practical_result, f'{expectant_result} in {practical_result}'
        return f'{expectant_result} in {practical_result}'

    def assert_startswith(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result.startswith(practical_result), f'{expectant_result} 以 {practical_result} 开头'
        return f'{expectant_result} 以 {practical_result} 开头'

    def assert_endswith(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert expectant_result.endswith(practical_result), f'{expectant_result} 以 {practical_result} 结尾'
        return f'{expectant_result} 以 {practical_result} 结尾'

    def assert_length_equals(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert len(expectant_result) == int(practical_result), f'{len(expectant_result)} == {practical_result}'
        return f'{len(expectant_result)} == {practical_result}'

    def assert_length_less_than(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert len(expectant_result) < int(practical_result), f'{len(expectant_result)} < {practical_result}'
        return f'{len(expectant_result)} < {practical_result}'

    def assert_length_less_than_or_equals(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert len(expectant_result) <= int(practical_result), f'{len(expectant_result)} <= {practical_result}'
        return f'{len(expectant_result)} <= {practical_result}'

    def assert_length_greater_than(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert len(expectant_result) > int(practical_result), f'{len(expectant_result)} > {practical_result}'
        return f'{len(expectant_result)} > {practical_result}'

    def assert_length_greater_than_or_equals(self, expectant_expression, practical_result):
        expectant_result, practical_result = self.__to_str(
            self.parse_expectant_expression(expectant_expression),
            practical_result
        )
        if isinstance(practical_result, str) and practical_result.startswith("${") and practical_result.endswith("}"):
            practical_result = RenderData(self.data).get_attribute(practical_result[2:-1])
        assert len(expectant_result) >= int(practical_result), f'{len(expectant_result)} >= {practical_result}'
        return f'{len(expectant_result)} >= {practical_result}'

    def assert_is_null(self, expectant_expression, practical_result):
        expectant_result = self.parse_expectant_expression(expectant_expression)
        assert expectant_result is None
        return expectant_result

    def assert_is_not_null(self, expectant_expression, practical_result):
        expectant_result = self.parse_expectant_expression(expectant_expression)
        assert expectant_result is not None
        return expectant_result

    def __to_str(self, expectant_expression, practical_result):
        if isinstance(expectant_expression, (int, float)):
            expectant_expression = str(expectant_expression)
        if isinstance(practical_result, (int, float)):
            practical_result = str(practical_result)
        return expectant_expression, practical_result

    def __to_digit(self, expectant_expression, practical_result):
        if isinstance(expectant_expression, str) and is_digit(expectant_expression):
            expectant_expression = eval(expectant_expression)
        if isinstance(practical_result, str) and is_digit(practical_result):
            practical_result = eval(practical_result)
        return expectant_expression, practical_result
