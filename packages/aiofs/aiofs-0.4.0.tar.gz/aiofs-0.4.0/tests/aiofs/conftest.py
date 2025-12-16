from dataclasses import dataclass
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from aiofs.redis import RedisConfig
from aiofs.azure import AzureContainerConfig


@pytest.fixture(scope="session")
def redis_container():
    """Start Redis container for the test session."""
    container = DockerContainer("redis:5.0.3-alpine")
    container.with_exposed_ports(6379)
    with container:
        strategy = LogMessageWaitStrategy("Ready to accept connections")
        strategy.with_startup_timeout(30)
        container.waiting_for(strategy)
        yield container


@pytest.fixture(scope="session")
def azurite_container():
    """Start Azurite container for the test session."""
    container = DockerContainer("mcr.microsoft.com/azure-storage/azurite:latest")
    container.with_exposed_ports(10000)
    container.with_command(
        "azurite --blobHost 0.0.0.0 --blobPort 10000 --skipApiVersionCheck"
    )
    with container:
        strategy = LogMessageWaitStrategy(
            "Azurite Blob service is successfully listening"
        )
        strategy.with_startup_timeout(30)
        container.waiting_for(strategy)
        yield container


@pytest.fixture(scope="session")
def redis_connection_params(redis_container):
    """Get Redis connection parameters."""
    return {
        "host": redis_container.get_container_host_ip(),
        "port": redis_container.get_exposed_port(6379),
    }


class AzuriteConfig(AzureContainerConfig):

    def __init__(self, container_name, host, port):
        self._host = host
        self._port = port
        super().__init__("", "", container_name)

    @property
    def connection_string(self) -> str:
        return (
            "AccountName=devstoreaccount1;"
            "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
            "K1SZFPTOtr/KBHBeksoGMGw==;"
            "DefaultEndpointsProtocol=http;"
            f"BlobEndpoint=http://{self._host}:{self._port}/devstoreaccount1;"
        )


@pytest.fixture(scope="session")
def azure_config(azurite_container):
    host = azurite_container.get_container_host_ip()
    port = azurite_container.get_exposed_port(10000)
    return AzuriteConfig("aiofs-cnt", host, port)


@pytest.fixture(scope="session")
def redis_config(redis_container):
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)

    return RedisConfig(host=host, port=port)
