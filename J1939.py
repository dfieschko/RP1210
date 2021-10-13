class J1939ProtocolFormatter:
    """
    Generates fpchProtocol string that you can feed to ClientConnect or SendCommand in order to
    dictate J1939 transmission parameters (mainly baud rate).
    
    See Section 12.11: SETTING J1939 BAUD RATE ON RP1210_CLIENTCONNECT

    Instantiate this class, then call fpchProtocol() to generate a string with the given arguments.

    Frankly, you don't need to use this class. Just put in "J1939:Baud=Auto" (format 1), and if
    that's not supported use "J1939" (format 2). The only reason this class is in here is
    because I wanted the package to cover as many features of the RP1210 standard as possible.

    fpchProtocol =
    1. "J1939:Baud=X"
    2. "J1939"
    3. "J1939:Baud=X, SampleLocation=Y, SJW=Z"
    4. "J1939:Baud=X, PROP_SEG=A, PHASE_SEG1=B, PHASE_SEG2=C, SJW=Z"
    5. "J1939:Baud=X, TSEG1=D, TSEG2=E, SampleTimes=Y, SJW=Z"
    """

    def fpchProtocol(self, protocol = 1, Baud = 500, Channel = 1,
                            SampleLocation = 95, SJW = 1,
                            PROP_SEG = 1, PHASE_SEG1 = 2, PHASE_SEG2 = 1,
                            TSEG1 = 2, TSEG2 = 1, SampleTimes = 1) -> str:
        """
        Generates fpchProtocol string for a J1939 protocol format. The default values you see above
        were made up on the spot and shouldn't be used.

        Keyword arguments have the same names as below (e.g. Baud, SampleLocation, PHASE_SEG1).

        IDSize is automatically set to 29 whenever relevant because that is its only valid value.

        This function also accepts a Channel argument!

        Examples (assuming you've instantiated the class as j1939Format):
        - j1939Format.fpchProtocol(protocol = 1, Baud = "Auto")
        - j1939Format.fpchProtocol(protocol = 3, Baud = 500, SampleLocation = 75, SJW = 3, IDSize = 29)
        """
        if protocol == 1:
            return f"J1939:Baud={str(Baud)},Channel={str(Channel)}"
        elif protocol == 2:
            return f"J1939,Channel={str(Channel)}"
        elif protocol == 3:
            return f"J1939:Baud={str(Baud)},SampleLocation={str(SampleLocation)},SJW={str(SJW)},IDSize=29,Channel={str(Channel)}"
        elif protocol == 4:
            return f"J1939:Baud={str(Baud)},PROP_SEG={str(PROP_SEG)},PHASE_SEG1={str(PHASE_SEG1)},PHASE_SEG2={str(PHASE_SEG2)},SJW={str(SJW)},IDSize=29,Channel={str(Channel)}"
        elif protocol == 5:
            return f"J1939:Baud={str(Baud)},TSEG1={str(TSEG1)},TSEG2={str(TSEG2)},SampleTimes={str(SampleTimes)},SJW={str(SJW)},IDSize=29,Channel={str(Channel)}"
        else:
            return "J1939" # default to protocol format 2, default channel

    def getProtocolDescription(self, protocol : int) -> str:
        """Returns a description of the protocol selected with protocol arg."""
        if protocol == 1:
            return "Variable J1939 baud rate. Select 125, 250, 500, 1000, or Auto."
        elif protocol == 2:
            return "General default for J1939 baud rate (250k baud)."
        elif protocol == 3:
            return "Driver uses SampleLocation to calculate parameters."
        elif protocol == 4:
            return "Baud formula derived from BOSCH CAN specification."
        elif protocol == 5:
            return "Baud formula derived from Intel implementations."
        else:
            return "Invalid J1939 protocol format selected."
