# Copyright (C) 2025 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import grpc

from buildgrid._protos.build.buildgrid.quota_pb2 import (
    DeleteInstanceQuotaRequest,
    GetInstanceQuotaRequest,
    InstanceQuota,
    PutInstanceQuotaRequest,
)
from buildgrid._protos.build.buildgrid.quota_pb2_grpc import QuotaStub
from buildgrid.server.exceptions import NotFoundError
from buildgrid.server.logging import buildgrid_logger

LOGGER = buildgrid_logger(__name__)


class QuotaInterface:
    """Interface for calls to the Quota Service."""

    def __init__(self, channel: grpc.Channel) -> None:
        """Initialises an instance of the quota service.

        Args:
            channel (grpc.Channel): A gRPC channel to the Quota endpoint.
        """
        self._stub = QuotaStub(channel)

    def get_instance_quota(self, instance_name: str, bot_cohort: str) -> InstanceQuota:
        """Returns the quota configuration for a specific instance and bot cohort.

        Args:
            instance_name (str): The name of the REAPI instance.
            bot_cohort (str): The name of the bot cohort.

        Returns:
            InstanceQuota: The quota configuration.

        Raises:
            NotFoundError: When the quota doesn't exist.
            ConnectionError: When there's a connection issue.
        """
        request = GetInstanceQuotaRequest(instance_name=instance_name, bot_cohort=bot_cohort)
        try:
            response = self._stub.GetInstanceQuota(request)
            return response.instance_quota

        except grpc.RpcError as e:
            LOGGER.exception(e)
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(f"Instance quota not found. instance={instance_name} bot_cohort={bot_cohort}")
            raise ConnectionError(e.details())

    def put_instance_quota(self, instance_name: str, bot_cohort: str, min_quota: int, max_quota: int) -> None:
        """Sets or updates the quota configuration for a specific instance and bot cohort.

        Args:
            instance_name (str): The name of the REAPI instance.
            bot_cohort (str): The name of the bot cohort.
            min_quota (int): Minimum quota limit for the instance.
            max_quota (int): Maximum quota limit for the instance.

        Raises:
            ConnectionError: When there's a connection issue.
        """
        request = PutInstanceQuotaRequest(
            instance_name=instance_name, bot_cohort=bot_cohort, min_quota=min_quota, max_quota=max_quota
        )
        try:
            self._stub.PutInstanceQuota(request)

        except grpc.RpcError as e:
            LOGGER.exception(e)
            raise ConnectionError(e.details())

    def delete_instance_quota(self, instance_name: str, bot_cohort: str) -> None:
        """Deletes the quota configuration for a specific instance and bot cohort.

        Args:
            instance_name (str): The name of the REAPI instance.
            bot_cohort (str): The name of the bot cohort.

        Raises:
            NotFoundError: When the quota doesn't exist.
            ConnectionError: When there's a connection issue.
        """
        request = DeleteInstanceQuotaRequest(instance_name=instance_name, bot_cohort=bot_cohort)
        try:
            self._stub.DeleteInstanceQuota(request)

        except grpc.RpcError as e:
            LOGGER.exception(e)
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(f"Instance quota not found. instance={instance_name} bot_cohort={bot_cohort}")
            raise ConnectionError(e.details())
