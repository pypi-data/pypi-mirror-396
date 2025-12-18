from loguru import logger
from pushikoo_interface import (
    Processer,
    Struct,
    TerminateFlowException,
    ProcesserConfig,  # noqa: F401
    ProcesserInstanceConfig,  # noqa: F401
)
from pushikoo_adapter_testprocesser.config import AdapterConfig, InstanceConfig


class TestProcesser(
    Processer[
        AdapterConfig,  # If you don't have any configuration, you can just use ProcesserConfig
        InstanceConfig,  # If you don't have any configuration, you can just use ProcesserInstanceConfig
    ]
):
    # This is your Adapter main implementation.
    # If a fatal error occurs (cannot be recovered properly), do not capture it.
    # Exceptions should be raised directly, with the framework responsible for final error handling and logging.

    def __init__(self) -> None:
        self.config  # Access to adapter configuration
        self.instance_config  # Access to instance configuration
        self.adapter_name  # Adapter name
        self.identifier  # Adapter instance identifier
        self.ctx  # Framework context

        self.ctx.get_proxies  # Framework provides proxies via ctx
        # {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

        logger.debug(
            f"{self.adapter_name}.{self.identifier} initialized"
        )  # We recommend to use loguru for logging

    def process(self, content: Struct) -> Struct:
        if len(content.content) > 0 and "DONOT" in content.content[0].text:
            raise TerminateFlowException("DONOT received")
        if len(content.content) > 0:
            content.content[0].text = content.content[0].text.replace("A", "B")
        return content
