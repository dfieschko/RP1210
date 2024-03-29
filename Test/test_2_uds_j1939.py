"""Tests UDS services with J1939Messages."""

import pytest
from RP1210.J1939 import J1939Message
from RP1210.UDS import UDSMessage
from RP1210.UDS.Authentication import AuthenticationRequest, AuthenticationResponse
from RP1210.UDS.ClearDiagnosticInformation import ClearDiagnosticInformationRequest, ClearDiagnosticInformationResponse
from RP1210.UDS.CommunicationControl import CommunicationControlRequest, CommunicationControlResponse
from RP1210.UDS.ControlDTCSetting import ControlDTCSettingRequest, ControlDTCSettingResponse
from RP1210.UDS.DiagnosticSessionControl import DiagnosticSessionControlRequest, DiagnosticSessionControlResponse
from RP1210.UDS.ECUReset import ECUResetRequest, ECUResetResponse
from RP1210.UDS.InputOutputControlByIdentifier import InputOutputControlByIdentifierRequest, InputOutputControlByIdentifierResponse
from RP1210.UDS.LinkControl import LinkControlRequest, LinkControlResponse
from RP1210.UDS.ReadDataByIdentifier import ReadDataByIdentifierRequest, ReadDataByIdentifierResponse
from RP1210.UDS.ReadDTCInformation import ReadDTCInformationRequest, ReadDTCInformationResponse
from RP1210.UDS.ReadMemoryByAddress import ReadMemoryByAddressRequest, ReadMemoryByAddressResponse
from RP1210.UDS.ReadScalingDataByIdentifier import ReadScalingDataByIdentifierRequest, ReadScalingDataByIdentifierResponse
from RP1210.UDS.RequestDownload import RequestDownloadRequest, RequestDownloadResponse
from RP1210.UDS.RequestFileTransfer import RequestFileTransferRequest, RequestFileTransferResponse
from RP1210.UDS.RequestTransferExit import RequestTransferExitRequest, RequestTransferExitResponse
from RP1210.UDS.RequestUpload import RequestUploadRequest, RequestUploadResponse
from RP1210.UDS.ResponseOnEvent import ResponseOnEventRequest, ResponseOnEventResponse
from RP1210.UDS.RoutineControl import RoutineControlRequest, RoutineControlResponse
from RP1210.UDS.SecurityAccess import SecurityAccessRequest, SecurityAccessResponse
from RP1210.UDS.TesterPresent import TesterPresentRequest, TesterPresentResponse
from RP1210.UDS.TransferData import TransferDataRequest, TransferDataResponse
from RP1210.UDS.WriteDataByIdentifier import WriteDataByIdentifierRequest, WriteDataByIdentifierResponse
from RP1210.UDS.WriteMemoryByAddress import WriteMemoryByAddressRequest, WriteMemoryByAddressResponse

UDSMESSAGE_CLASSES = [
    AuthenticationRequest, AuthenticationResponse, CommunicationControlRequest, CommunicationControlResponse,
    ControlDTCSettingResponse, ControlDTCSettingRequest, DiagnosticSessionControlRequest, DiagnosticSessionControlResponse,
    ECUResetRequest, ECUResetResponse, LinkControlRequest, LinkControlResponse, ReadDataByIdentifierRequest, ReadDataByIdentifierResponse,
    ReadMemoryByAddressRequest, ReadMemoryByAddressResponse, ReadScalingDataByIdentifierRequest, ReadScalingDataByIdentifierResponse,
    RequestDownloadRequest, RequestDownloadResponse, ResponseOnEventRequest, ResponseOnEventResponse,
    SecurityAccessRequest, SecurityAccessResponse, TesterPresentRequest, TesterPresentResponse,
    WriteDataByIdentifierRequest, WriteDataByIdentifierResponse, ClearDiagnosticInformationRequest, ClearDiagnosticInformationResponse,
    InputOutputControlByIdentifierRequest, InputOutputControlByIdentifierResponse, ReadDTCInformationRequest, ReadDTCInformationResponse,
    RequestFileTransferRequest, RequestFileTransferResponse, RequestTransferExitRequest, RequestTransferExitResponse,
    RequestUploadRequest, RequestUploadResponse, RoutineControlRequest, RoutineControlResponse,
    TransferDataRequest, TransferDataResponse, WriteMemoryByAddressRequest, WriteMemoryByAddressResponse
]

@pytest.mark.parametrize("cls", argvalues=UDSMESSAGE_CLASSES)
def test_UDSMessage_as_J1939Message_data(cls : type[UDSMessage]):
    uds = cls()
    msg = J1939Message()
    msg.data = uds
    assert msg.data == uds.raw

def test_WriteDataByIdentifierRequest_J1939Message():
    request = WriteDataByIdentifierRequest()
    request.dataIdentifier = 0xBEEF
    request.dataRecord = b'\x12\x34\x56\x78'
    msg = J1939Message()
    msg.pgn = 0xDA00
    msg.sa = 0xF9
    msg.da = 0xBC
    msg.data = request
    assert msg.data == b'\x2E\xBE\xEF\x12\x34\x56\x78'
