import pytest

from buildgrid.server.app.settings.parser import validate_config


@pytest.mark.parametrize(
    "config_file",
    [
        "buildgrid/server/app/settings/reference.yml",
        "data/config/all-in-one.yml",
        "data/config/artifacts.yml",
        "data/config/bots-interface.yml",
        "data/config/cache.yml",
        "data/config/controller.yml",
        "data/config/default.yml",
        "data/config/monitoring-controller.yml",
        "data/config/multi-layer-storage.yml",
        "data/config/multi-level-cache/buildgrid.yml",
        "data/config/multi-level-cache/shared-lru.yml",
        "data/config/redis-cache.yml",
        "data/config/redis-index/action-cache.yml",
        "data/config/redis-index/cas.yml",
        "data/config/redis-index/execution.yml",
        "data/config/redis-sentinel/buildgrid.yml",
        "data/config/s3-cas/action-cache.yml",
        "data/config/s3-cas/cas.yml",
        "data/config/s3-cas/execution.yml",
        "data/config/s3-indexed-cas.yml",
        "data/config/storage-redis.yml",
        "data/config/storage-s3.yml",
        "data/config/storage.yml",
        "data/config/with-metering.yml",
        "data/config/with-pgbouncer.yml",
        "docs/source/data/basic-disk-cas.yml",
        "docs/source/data/bazel-example-server.yml",
        "docs/source/data/buildstream-example-server.yml",
        "docs/source/data/cas-and-ac.yml",
        "docs/source/data/cas-example-server.yml",
        "docs/source/data/execution-and-bots.yml",
    ],
)
def test_example_config(config_file):
    validate_config(config_file, strict=True, fail_deprecations=True)
