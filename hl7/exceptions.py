class HL7Exception(Exception):
    pass


class MalformedSegmentException(HL7Exception):
    pass


class MalformedBatchException(HL7Exception):
    pass


class MalformedFileException(HL7Exception):
    pass


class ParseException(HL7Exception):
    pass


class MLLPException(HL7Exception):
    pass


class CLIException(HL7Exception):
    """ An exception to propagate expected exit code from cli script"""
    def __init__(self, exit_code):
        self.exit_code = exit_code