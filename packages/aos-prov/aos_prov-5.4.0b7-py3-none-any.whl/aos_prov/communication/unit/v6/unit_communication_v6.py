#
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
from contextlib import contextmanager

import grpc

from aos_prov.communication.unit.common import (
    unit_address_parser,
    unit_communication_channel,
    unit_communication_version_channel
)
from aos_prov.communication.unit.v6.generated import iamanager_pb2 as iam_manager
from aos_prov.communication.unit.v6.generated import (
    iamanager_pb2_grpc as iam_manager_grpc,
)
from aos_prov.communication.unit.version.generated import version_pb2_grpc
from aos_prov.utils.common import print_done, print_left, print_success
from aos_prov.utils.errors import UnitError
from aos_prov.utils.unit_certificate import UnitCertificate
from google.protobuf import empty_pb2

UNIT_DEFAULT_PORT = 8089
_MAX_PORT = 65535


class UnitCommunicationV6:
    def __init__(self, address: str = 'localhost:8089'):
        self._unit_address = unit_address_parser(address)

    def is_node_main(self, node_id: str) -> bool:
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMPublicNodesServiceStub) as stub:
            node_info = stub.GetNodeInfo(iam_manager.GetNodeInfoRequest(node_id=node_id))
            for node_item in node_info.attrs:
                if node_item.name == 'MainNode':
                    return True

            return False

    def get_node_info(self, node_id: str) -> iam_manager.NodeInfo:
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMPublicNodesServiceStub) as stub:
            return stub.GetNodeInfo(iam_manager.GetNodeInfoRequest(node_id=node_id))

    def get_protocol_version(self) -> int:
        with unit_communication_version_channel(self._unit_address, version_pb2_grpc.IAMVersionServiceStub) as stub:
            print_left('Communicating with unit using provisioning protocol version 6...')
            response = stub.GetAPIVersion(empty_pb2.Empty())
            print(response.version)
            return response.version
            print_done()
            return int(response.version)

    def get_system_info(self) -> (str, str):
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMPublicIdentityServiceStub) as stub:
            print_left('Getting System Info...')
            response = stub.GetSystemInfo(empty_pb2.Empty())
            print(response)
            print_done()
            print_left('System ID:')
            print_success(response.system_id)
            print_left('Unit model:')
            print_success(response.unit_model)
            return response.system_id, response.unit_model

    def get_all_node_ids(self) -> [str]:
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMPublicNodesServiceStub) as stub:
            print_left('Getting Node IDs...')
            response = stub.GetAllNodeIDs(empty_pb2.Empty())
            print(response)
            print_success(response.ids)
            return response.ids

    def get_cert_types(self, node_id: str = '') -> [str]:
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMProvisioningServiceStub) as stub:
            print_left(f'Getting certificate types to renew on node {node_id}...')
            response = stub.GetCertTypes(iam_manager.GetCertTypesRequest(node_id=node_id))
            print_success(response.types)
            return response.types

    def create_keys(self, cert_type: str, password: str, node_id: str = '') -> UnitCertificate:
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMCertificateServiceStub) as stub:
            print_left(f'Generating key type: {cert_type} on Node: {node_id}...')
            response = stub.CreateKey(iam_manager.CreateKeyRequest(type=cert_type, password=password, node_id=node_id))
            if response.error.message:
                raise UnitError(
                    f'FAILED! Received error from the unit: \n aos_code: {response.error.aos_code}\n'  # noqa: WPS237
                    f'exit_code: {response.error.exit_code}\n message: {response.error.message}',
                )
            user_creds = UnitCertificate()
            user_creds.cert_type = response.type
            user_creds.node_id = response.node_id
            user_creds.csr = response.csr
            print_done()
            return user_creds

    def apply_certificate(self, unit_cert: UnitCertificate):
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMCertificateServiceStub) as stub:
            node_id = ''
            if unit_cert.node_id:
                node_id = str(unit_cert.node_id)
            print_left(f'Applying certificate type: {unit_cert.cert_type} Node ID: {node_id}...')
            response = stub.ApplyCert(iam_manager.ApplyCertRequest(
                type=unit_cert.cert_type,
                cert=unit_cert.certificate,
                node_id=node_id,
            ))
            if response.error.message:
                raise UnitError(
                    f'FAILED! Received error from the unit: \n aos_code: {response.error.aos_code}\n'  # noqa: WPS237
                    f'exit_code: {response.error.exit_code}\n message: {response.error.message}',
                )
            print_done()

    def start_provisioning(self, node_id: str, password: str) -> None:
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMProvisioningServiceStub, True) as stub:
            print_left('Starting provisioning...')
            response = stub.StartProvisioning(iam_manager.StartProvisioningRequest(node_id=node_id, password=password))
            if response.error.message:
                raise UnitError(
                    f'FAILED! Received error from the unit: \n aos_code: {response.error.aos_code}\n'  # noqa: WPS237
                    f'exit_code: {response.error.exit_code}\n message: {response.error.message}',
                )
            print_done()

    def finish_provisioning(self, node_id: str = None, password: str = None):
        with unit_communication_channel(self._unit_address, iam_manager_grpc.IAMProvisioningServiceStub, True) as stub:
            print_left(f'Finishing provisioning... Node ID: {node_id}')
            response = stub.FinishProvisioning(
                iam_manager.FinishProvisioningRequest(node_id=node_id, password=password),
            )
            if response.error.message:
                raise UnitError(
                    f'FAILED! Received error from the unit: \n aos_code: {response.error.aos_code}\n'  # noqa: WPS237
                    f'exit_code: {response.error.exit_code}\n message: {response.error.message}',
                )
            print_done()
