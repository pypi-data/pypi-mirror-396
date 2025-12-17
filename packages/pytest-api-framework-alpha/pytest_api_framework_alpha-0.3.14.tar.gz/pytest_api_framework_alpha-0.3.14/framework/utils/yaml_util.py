import os
import hashlib

import yaml
import json
from box import Box

from config.settings import ROOT_DIR, YML_CACHE_DIR


class YamlUtil(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def load_yml(self, key=None, is_box=False):
        """

        @param key:
        @param is_box:
        @return:
        """
        with open(os.path.join(ROOT_DIR, self.file_path), mode="r", encoding="utf-8") as f:
            result = yaml.safe_load(stream=f) or dict()
            if key:
                result = result.get(key)
            if is_box:
                result = Box(result) if isinstance(result, dict) else result
            return result


class CachedYamlLoader(object):
    """
    YAML 加载器，带缓存机制：
    - 文件没改动，直接读取 JSON 缓存
    - 文件改动后自动重新解析 YAML 并更新缓存
    """

    def __init__(self, file_path):
        self.file_path = os.path.join(ROOT_DIR, file_path)
        self.cache_dir = YML_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_file(self):
        """根据文件修改时间 + 文件大小生成唯一缓存文件名"""
        stat = os.stat(self.file_path)
        key = f"{self.file_path}-{stat.st_mtime}-{stat.st_size}"
        hash_key = hashlib.md5(key.encode()).hexdigest()
        hash_path = hashlib.md5(self.file_path.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_path}_{hash_key}.json")

    def load_yml(self, key=None, is_box=False):
        """
        加载 YAML 文件并使用缓存
        :param key: 指定获取 YAML 中某个 key 的值
        :param is_box: 是否转换成 Box 对象
        :return: dict / Box / value
        """
        cache_file = self._get_cache_file()

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    result = json.load(f)
            except Exception:
                result = self._parse_and_cache(cache_file)
        else:
            result = self._parse_and_cache(cache_file)

        if key:
            result = result.get(key)

        if is_box:
            result = Box(result) if isinstance(result, dict) else result

        return result

    def _parse_and_cache(self, cache_file):
        """解析 YAML 并写入缓存，同时删除旧缓存"""
        # 删除旧缓存文件
        file_hash = hashlib.md5(self.file_path.encode()).hexdigest()
        for f in os.listdir(self.cache_dir):
            f_path = os.path.join(self.cache_dir, f)
            if os.path.isfile(f_path) and f.startswith(file_hash):
                try:
                    os.remove(f_path)
                except Exception as e:
                    print(f"删除旧缓存失败: {e}")

        # 解析 YAML
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            result = yaml.safe_load(f) or {}

        # 写入新缓存
        with open(cache_file, "w", encoding="utf-8") as cf:
            json.dump(result, cf, ensure_ascii=False)
        return result