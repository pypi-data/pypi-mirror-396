from .types import SDKConfiguration, SDKInitHook


class MoovVersionHook(SDKInitHook):

    def sdk_init(self, config: SDKConfiguration) -> SDKConfiguration:
        """Sets the X-Moov-Version global variable to the OpenAPI document version"""

        config.globals.x_moov_version = config.openapi_doc_version
        return config
