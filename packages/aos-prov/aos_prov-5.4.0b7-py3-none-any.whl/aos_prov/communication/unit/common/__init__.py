#
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#

import grpc
from contextlib import contextmanager
from aos_prov.utils.errors import UnitError, GrpcUnimplemented

_UNIT_DEFAULT_PORT = 8089
_MAX_PORT = 65535

def unit_address_parser(address: str) -> str:
    if not address:
        address = 'localhost:8089'

    parts = address.split(':')

    if len(parts) == 2:
        try:
            port = int(parts[1])
            if port not in range(1, _MAX_PORT):
                raise UnitError('Unit port is invalid')
        except ValueError as exc:
            raise UnitError('Unit port is invalid') from exc
    else:
        address = address + ':' + str(_UNIT_DEFAULT_PORT)

    return address


@contextmanager
def unit_communication_channel(address, service_func, catch_inactive=False, wait_for_close=False):
    try:
        with grpc.insecure_channel(address) as channel:
            stub = service_func(channel)
            if wait_for_close:
                def _stop_wait(state):  # noqa: WPS430
                    if state is grpc.ChannelConnectivity.SHUTDOWN:
                        channel.unsubscribe(_stop_wait)
                        return
                channel.subscribe(_stop_wait, try_to_connect=False)
            yield stub

    except grpc.RpcError as exc:
        e_code = exc.code()
        e_detail = exc.details()
        if catch_inactive and not (e_code == grpc.StatusCode.UNAVAILABLE.value and e_detail == 'Socket closed'):
            return
        if wait_for_close and (e_code == grpc.StatusCode.UNKNOWN.value and e_detail == 'Stream removed'):
            return
        raise UnitError(f'FAILED! Error occurred: \n{e_code}: {e_detail}') from exc


@contextmanager
def unit_communication_version_channel(address, service_func):
    try:
        with grpc.insecure_channel(address) as channel:
            stub = service_func(channel)
            yield stub

    except grpc.RpcError as exc:
        e_code = exc.code()
        e_detail = exc.details()
        if e_code.value == grpc.StatusCode.UNIMPLEMENTED.value:
            raise GrpcUnimplemented(f'Provisioning protocol 6 is not supported: \n{e_code}: {e_detail}') from exc
        raise UnitError(f'FAILED! Error occurred: \n{e_code}: {e_detail}') from exc


