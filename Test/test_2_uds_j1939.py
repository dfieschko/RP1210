"""Tests UDS services with J1939Messages."""

import pytest
from RP1210.J1939 import J1939Message
from RP1210.UDS import UDSMessage
from RP1210.UDS.Authentication import AuthenticationRequest, AuthenticationResponse
from RP1210.UDS.CommunicationControl import CommunicationControlRequest, CommunicationControlResponse
from RP1210.UDS.ControlDTCSetting import ControlDTCSettingRequest, ControlDTCSettingResponse
from RP1210.UDS.DiagnosticSessionControl import DiagnosticSessionControlRequest, DiagnosticSessionControlResponse
from RP1210.UDS.ECUReset import ECUResetRequest, ECUResetResponse
from RP1210.UDS.LinkControl import LinkControlRequest, LinkControlResponse
from RP1210.UDS.ReadDataByIdentifier import ReadDataByIdentifierRequest, ReadDataByIdentifierResponse
from RP1210.UDS.ReadMemoryByAddress import ReadMemoryByAddressRequest, ReadMemoryByAddressResponse
from RP1210.UDS.ReadScalingDataByIdentifier import ReadScalingDataByIdentifierRequest, ReadScalingDataByIdentifierResponse
from RP1210.UDS.RequestDownload import RequestDownloadRequest, RequestDownloadResponse
from RP1210.UDS.ResponseOnEvent import ResponseOnEventRequest, ResponseOnEventResponse
from RP1210.UDS.SecurityAccess import SecurityAccessRequest, SecurityAccessResponse
from RP1210.UDS.TesterPresent import TesterPresentRequest, TesterPresentResponse

UDSMESSAGE_CLASSES = [
    AuthenticationRequest, AuthenticationResponse, CommunicationControlRequest, CommunicationControlResponse,
    ControlDTCSettingResponse, ControlDTCSettingRequest, DiagnosticSessionControlRequest, DiagnosticSessionControlResponse,
    ECUResetRequest, ECUResetResponse, LinkControlRequest, LinkControlResponse, ReadDataByIdentifierRequest, ReadDataByIdentifierResponse,
    ReadMemoryByAddressRequest, ReadMemoryByAddressResponse, ReadScalingDataByIdentifierRequest, ReadScalingDataByIdentifierResponse,
    RequestDownloadRequest, RequestDownloadResponse, ResponseOnEventRequest, ResponseOnEventResponse,
    SecurityAccessRequest, SecurityAccessResponse, TesterPresentRequest, TesterPresentResponse
]

@pytest.mark.parametrize("cls", argvalues=UDSMESSAGE_CLASSES)
def test_UDSMessage_as_J1939Message_data(cls : type[UDSMessage]):
    uds = cls()
    msg = J1939Message()
    msg.data = uds
    assert msg.data == uds.raw
