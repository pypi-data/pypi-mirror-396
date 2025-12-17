import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CalibrationValues(_message.Message):
    __slots__ = ("calibration_date", "dac_voffs", "dac_vgain", "dac_coffs", "dac_cgain", "adc_vout_offs", "adc_vout_gain", "adc_vsense_offs", "adc_vsense_gain", "adc_coffs", "adc_cgain")
    CALIBRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    DAC_VOFFS_FIELD_NUMBER: _ClassVar[int]
    DAC_VGAIN_FIELD_NUMBER: _ClassVar[int]
    DAC_COFFS_FIELD_NUMBER: _ClassVar[int]
    DAC_CGAIN_FIELD_NUMBER: _ClassVar[int]
    ADC_VOUT_OFFS_FIELD_NUMBER: _ClassVar[int]
    ADC_VOUT_GAIN_FIELD_NUMBER: _ClassVar[int]
    ADC_VSENSE_OFFS_FIELD_NUMBER: _ClassVar[int]
    ADC_VSENSE_GAIN_FIELD_NUMBER: _ClassVar[int]
    ADC_COFFS_FIELD_NUMBER: _ClassVar[int]
    ADC_CGAIN_FIELD_NUMBER: _ClassVar[int]
    calibration_date: _timestamp_pb2.Timestamp
    dac_voffs: float
    dac_vgain: float
    dac_coffs: float
    dac_cgain: float
    adc_vout_offs: float
    adc_vout_gain: float
    adc_vsense_offs: float
    adc_vsense_gain: float
    adc_coffs: float
    adc_cgain: float
    def __init__(self, calibration_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., dac_voffs: _Optional[float] = ..., dac_vgain: _Optional[float] = ..., dac_coffs: _Optional[float] = ..., dac_cgain: _Optional[float] = ..., adc_vout_offs: _Optional[float] = ..., adc_vout_gain: _Optional[float] = ..., adc_vsense_offs: _Optional[float] = ..., adc_vsense_gain: _Optional[float] = ..., adc_coffs: _Optional[float] = ..., adc_cgain: _Optional[float] = ...) -> None: ...

class ConfigurationSet(_message.Message):
    __slots__ = ("calibration_values", "auto_recover")
    CALIBRATION_VALUES_FIELD_NUMBER: _ClassVar[int]
    AUTO_RECOVER_FIELD_NUMBER: _ClassVar[int]
    calibration_values: CalibrationValues
    auto_recover: bool
    def __init__(self, calibration_values: _Optional[_Union[CalibrationValues, _Mapping]] = ..., auto_recover: _Optional[bool] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("calibration_values", "auto_recover")
    CALIBRATION_VALUES_FIELD_NUMBER: _ClassVar[int]
    AUTO_RECOVER_FIELD_NUMBER: _ClassVar[int]
    calibration_values: CalibrationValues
    auto_recover: bool
    def __init__(self, calibration_values: _Optional[_Union[CalibrationValues, _Mapping]] = ..., auto_recover: _Optional[bool] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ("max_voltage", "max_current", "max_power")
    MAX_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_CURRENT_FIELD_NUMBER: _ClassVar[int]
    MAX_POWER_FIELD_NUMBER: _ClassVar[int]
    max_voltage: float
    max_current: float
    max_power: float
    def __init__(self, max_voltage: _Optional[float] = ..., max_current: _Optional[float] = ..., max_power: _Optional[float] = ...) -> None: ...

class SetDefaults(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetVoltageLevel(_message.Message):
    __slots__ = ("level",)
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    level: float
    def __init__(self, level: _Optional[float] = ...) -> None: ...

class SetOutputEnabled(_message.Message):
    __slots__ = ("enabled",)
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    def __init__(self, enabled: _Optional[bool] = ...) -> None: ...

class SetCurrentLimit(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: float
    def __init__(self, limit: _Optional[float] = ...) -> None: ...

class Recover(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("setDefaults", "setVoltageLevel", "setOutputEnabled", "setCurrentLimit", "recover")
    SETDEFAULTS_FIELD_NUMBER: _ClassVar[int]
    SETVOLTAGELEVEL_FIELD_NUMBER: _ClassVar[int]
    SETOUTPUTENABLED_FIELD_NUMBER: _ClassVar[int]
    SETCURRENTLIMIT_FIELD_NUMBER: _ClassVar[int]
    RECOVER_FIELD_NUMBER: _ClassVar[int]
    setDefaults: SetDefaults
    setVoltageLevel: SetVoltageLevel
    setOutputEnabled: SetOutputEnabled
    setCurrentLimit: SetCurrentLimit
    recover: Recover
    def __init__(self, setDefaults: _Optional[_Union[SetDefaults, _Mapping]] = ..., setVoltageLevel: _Optional[_Union[SetVoltageLevel, _Mapping]] = ..., setOutputEnabled: _Optional[_Union[SetOutputEnabled, _Mapping]] = ..., setCurrentLimit: _Optional[_Union[SetCurrentLimit, _Mapping]] = ..., recover: _Optional[_Union[Recover, _Mapping]] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("desired_voltage", "measured_sense_voltage", "measured_output_voltage", "current_limit", "measured_current", "diag_flags", "output_state", "temperature")
    class DiagFlags(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        none: _ClassVar[FunctionControlGetResponse.DiagFlags]
        internal_error: _ClassVar[FunctionControlGetResponse.DiagFlags]
        input_under_voltage: _ClassVar[FunctionControlGetResponse.DiagFlags]
        input_over_voltage: _ClassVar[FunctionControlGetResponse.DiagFlags]
        current_limit_active: _ClassVar[FunctionControlGetResponse.DiagFlags]
        sense_line_error: _ClassVar[FunctionControlGetResponse.DiagFlags]
    none: FunctionControlGetResponse.DiagFlags
    internal_error: FunctionControlGetResponse.DiagFlags
    input_under_voltage: FunctionControlGetResponse.DiagFlags
    input_over_voltage: FunctionControlGetResponse.DiagFlags
    current_limit_active: FunctionControlGetResponse.DiagFlags
    sense_line_error: FunctionControlGetResponse.DiagFlags
    class OutputState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        off: _ClassVar[FunctionControlGetResponse.OutputState]
        on: _ClassVar[FunctionControlGetResponse.OutputState]
        shutdown: _ClassVar[FunctionControlGetResponse.OutputState]
    off: FunctionControlGetResponse.OutputState
    on: FunctionControlGetResponse.OutputState
    shutdown: FunctionControlGetResponse.OutputState
    DESIRED_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    MEASURED_SENSE_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    MEASURED_OUTPUT_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LIMIT_FIELD_NUMBER: _ClassVar[int]
    MEASURED_CURRENT_FIELD_NUMBER: _ClassVar[int]
    DIAG_FLAGS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_STATE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    desired_voltage: float
    measured_sense_voltage: float
    measured_output_voltage: float
    current_limit: float
    measured_current: float
    diag_flags: int
    output_state: FunctionControlGetResponse.OutputState
    temperature: float
    def __init__(self, desired_voltage: _Optional[float] = ..., measured_sense_voltage: _Optional[float] = ..., measured_output_voltage: _Optional[float] = ..., current_limit: _Optional[float] = ..., measured_current: _Optional[float] = ..., diag_flags: _Optional[int] = ..., output_state: _Optional[_Union[FunctionControlGetResponse.OutputState, str]] = ..., temperature: _Optional[float] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Sample(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamData(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
