from framework.base_class import BaseTestCase
from framework.global_attribute import CONTEXT, _FRAMEWORK_CONTEXT, CONFIG


class __BaseScript(BaseTestCase):
    BaseTestCase.context = CONTEXT
    BaseTestCase.config = CONFIG
    BaseTestCase.http = _FRAMEWORK_CONTEXT.get("_http")


class BaseScript(__BaseScript):
    app = None

    def run(self):
        raise NotImplementedError

    def default_app(self, app):
        return app or self.app

    def context_set(self, key, value):
        self.context.set(app=self.app, key=key, value=value)

    def context_get(self, key):
        return self.context.get(app=self.app, key=key)