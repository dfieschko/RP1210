from . import UDSMessage


class AuthenticationRequest(UDSMessage):
    """
    Authentication (Request)
    - `sid` = 0x29
    - `subfn` = authenticationTask 
    """

    _sid = 0x29
    _isResponse = False

    # sub-function IDs, for convenience:
    deAuthenticate = 0x00
    authenticationConfiguration = 0x08
    # only if authentication with PKI Certificate Exchange (APCE) is used
    verifyCertificateUnidirectional = 0x01
    verifyCertificateBidirectional = 0x02
    proofOfOwnership = 0x03
    transmitCertificate = 0x04
    # only if authentication with Challenge-Response (ACR) is used
    requestChallengeForAuthentication = 0x05
    verifyProofOfOwnershipUnidirectional = 0x06
    verifyProofOfOwnershupBidirectional = 0x07
    authenticationConfiguration = 0x08

    def __init__(self, subfn: int = authenticationConfiguration):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False

        self.subfn = subfn


class AuthenticationResponse(UDSMessage):
    """
    Authentication (Response)
    - `sid` = 0x69
    - `subfn` = authenticationTask
    - `data` = authenticationReturnParameter + other parameters depends on subfn
    """

    _sid = 0x69
    _isResponse = True

    # sub-function IDs, for convenience:
    deAuthenticate = 0x00
    authenticationConfiguration = 0x08
    # only if authentication with PKI Certificate Exchange (APCE) is used
    verifyCertificateUnidirectional = 0x01
    verifyCertificateBidirectional = 0x02
    proofOfOwnership = 0x03
    transmitCertificate = 0x04
    # only if authentication with Challenge-Response (ACR) is used
    requestChallengeForAuthentication = 0x05
    verifyProofOfOwnershipUnidirectional = 0x06
    verifyProofOfOwnershupBidirectional = 0x07
    authenticationConfiguration = 0x08

    def __init__(self, subfn: int = authenticationConfiguration, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.subfn = subfn
        self.data = data
