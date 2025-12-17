from colorLED.v1alpha1 import colorLED_pb2 as _colorLED_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RebootMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOFT: _ClassVar[RebootMethod]
    HARD: _ClassVar[RebootMethod]

class WatchdogStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PC: _ClassVar[WatchdogStrategy]
    SD: _ClassVar[WatchdogStrategy]
    RE: _ClassVar[WatchdogStrategy]

class SystemState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OFF: _ClassVar[SystemState]
    LED_TEST: _ClassVar[SystemState]
    START_INH: _ClassVar[SystemState]
    UP_DELAYED: _ClassVar[SystemState]
    BOOT_UP: _ClassVar[SystemState]
    ON: _ClassVar[SystemState]
    DOWN_DELAYED: _ClassVar[SystemState]
    SHUTDOWN: _ClassVar[SystemState]
    STANDBY: _ClassVar[SystemState]
    ERROR: _ClassVar[SystemState]
    POWERCUT: _ClassVar[SystemState]

class StateCommandResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATE_OK: _ClassVar[StateCommandResponseType]
    INVALID_STATE_ERROR: _ClassVar[StateCommandResponseType]
    UNKNOWN_STATE_ERROR: _ClassVar[StateCommandResponseType]

class HostCommandResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CMD_OK: _ClassVar[HostCommandResponseType]
    INVALID_CMD_STATE_ERROR: _ClassVar[HostCommandResponseType]
    CMD_FAILED_ERROR: _ClassVar[HostCommandResponseType]
    UNKNOWN_CMD_ERROR: _ClassVar[HostCommandResponseType]
SOFT: RebootMethod
HARD: RebootMethod
PC: WatchdogStrategy
SD: WatchdogStrategy
RE: WatchdogStrategy
OFF: SystemState
LED_TEST: SystemState
START_INH: SystemState
UP_DELAYED: SystemState
BOOT_UP: SystemState
ON: SystemState
DOWN_DELAYED: SystemState
SHUTDOWN: SystemState
STANDBY: SystemState
ERROR: SystemState
POWERCUT: SystemState
STATE_OK: StateCommandResponseType
INVALID_STATE_ERROR: StateCommandResponseType
UNKNOWN_STATE_ERROR: StateCommandResponseType
CMD_OK: HostCommandResponseType
INVALID_CMD_STATE_ERROR: HostCommandResponseType
CMD_FAILED_ERROR: HostCommandResponseType
UNKNOWN_CMD_ERROR: HostCommandResponseType

class ConfigurationSet(_message.Message):
    __slots__ = ("pon_min_temp", "pon_max_temp", "standby_mode", "boot_delay", "wd_tout", "wd_reboot_threshold", "wd_reboot_window", "wd_boot_delay", "wd_strategy", "pwrcycle_time", "shutdown_timeout", "error_timeout", "delay_up", "delay_down", "uv_detection", "uv_in_threshold", "uv_out_threshold", "start_color", "on_color", "up_color", "down_color", "shutdown_color", "standby_color", "powercut_color", "error_color", "boot_color", "reboot_method", "power_lp_func", "power_lp_time_min", "power_sp_func", "power_sp_time_min", "reboot_func", "ign_func", "sys_led")
    PON_MIN_TEMP_FIELD_NUMBER: _ClassVar[int]
    PON_MAX_TEMP_FIELD_NUMBER: _ClassVar[int]
    STANDBY_MODE_FIELD_NUMBER: _ClassVar[int]
    BOOT_DELAY_FIELD_NUMBER: _ClassVar[int]
    WD_TOUT_FIELD_NUMBER: _ClassVar[int]
    WD_REBOOT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    WD_REBOOT_WINDOW_FIELD_NUMBER: _ClassVar[int]
    WD_BOOT_DELAY_FIELD_NUMBER: _ClassVar[int]
    WD_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    PWRCYCLE_TIME_FIELD_NUMBER: _ClassVar[int]
    SHUTDOWN_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ERROR_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DELAY_UP_FIELD_NUMBER: _ClassVar[int]
    DELAY_DOWN_FIELD_NUMBER: _ClassVar[int]
    UV_DETECTION_FIELD_NUMBER: _ClassVar[int]
    UV_IN_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    UV_OUT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    START_COLOR_FIELD_NUMBER: _ClassVar[int]
    ON_COLOR_FIELD_NUMBER: _ClassVar[int]
    UP_COLOR_FIELD_NUMBER: _ClassVar[int]
    DOWN_COLOR_FIELD_NUMBER: _ClassVar[int]
    SHUTDOWN_COLOR_FIELD_NUMBER: _ClassVar[int]
    STANDBY_COLOR_FIELD_NUMBER: _ClassVar[int]
    POWERCUT_COLOR_FIELD_NUMBER: _ClassVar[int]
    ERROR_COLOR_FIELD_NUMBER: _ClassVar[int]
    BOOT_COLOR_FIELD_NUMBER: _ClassVar[int]
    REBOOT_METHOD_FIELD_NUMBER: _ClassVar[int]
    POWER_LP_FUNC_FIELD_NUMBER: _ClassVar[int]
    POWER_LP_TIME_MIN_FIELD_NUMBER: _ClassVar[int]
    POWER_SP_FUNC_FIELD_NUMBER: _ClassVar[int]
    POWER_SP_TIME_MIN_FIELD_NUMBER: _ClassVar[int]
    REBOOT_FUNC_FIELD_NUMBER: _ClassVar[int]
    IGN_FUNC_FIELD_NUMBER: _ClassVar[int]
    SYS_LED_FIELD_NUMBER: _ClassVar[int]
    pon_min_temp: int
    pon_max_temp: int
    standby_mode: bool
    boot_delay: int
    wd_tout: int
    wd_reboot_threshold: int
    wd_reboot_window: int
    wd_boot_delay: int
    wd_strategy: WatchdogStrategy
    pwrcycle_time: int
    shutdown_timeout: int
    error_timeout: int
    delay_up: int
    delay_down: int
    uv_detection: bool
    uv_in_threshold: int
    uv_out_threshold: int
    start_color: _colorLED_pb2.Color
    on_color: _colorLED_pb2.Color
    up_color: _colorLED_pb2.Color
    down_color: _colorLED_pb2.Color
    shutdown_color: _colorLED_pb2.Color
    standby_color: _colorLED_pb2.Color
    powercut_color: _colorLED_pb2.Color
    error_color: _colorLED_pb2.Color
    boot_color: _colorLED_pb2.Color
    reboot_method: RebootMethod
    power_lp_func: str
    power_lp_time_min: int
    power_sp_func: str
    power_sp_time_min: int
    reboot_func: str
    ign_func: str
    sys_led: int
    def __init__(self, pon_min_temp: _Optional[int] = ..., pon_max_temp: _Optional[int] = ..., standby_mode: _Optional[bool] = ..., boot_delay: _Optional[int] = ..., wd_tout: _Optional[int] = ..., wd_reboot_threshold: _Optional[int] = ..., wd_reboot_window: _Optional[int] = ..., wd_boot_delay: _Optional[int] = ..., wd_strategy: _Optional[_Union[WatchdogStrategy, str]] = ..., pwrcycle_time: _Optional[int] = ..., shutdown_timeout: _Optional[int] = ..., error_timeout: _Optional[int] = ..., delay_up: _Optional[int] = ..., delay_down: _Optional[int] = ..., uv_detection: _Optional[bool] = ..., uv_in_threshold: _Optional[int] = ..., uv_out_threshold: _Optional[int] = ..., start_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., on_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., up_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., down_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., shutdown_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., standby_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., powercut_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., error_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., boot_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., reboot_method: _Optional[_Union[RebootMethod, str]] = ..., power_lp_func: _Optional[str] = ..., power_lp_time_min: _Optional[int] = ..., power_sp_func: _Optional[str] = ..., power_sp_time_min: _Optional[int] = ..., reboot_func: _Optional[str] = ..., ign_func: _Optional[str] = ..., sys_led: _Optional[int] = ...) -> None: ...

class ConfigurationSetResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationGetResponse(_message.Message):
    __slots__ = ("pon_min_temp", "pon_max_temp", "standby_mode", "boot_delay", "wd_tout", "wd_reboot_threshold", "wd_reboot_window", "wd_boot_delay", "wd_strategy", "pwrcycle_time", "shutdown_timeout", "error_timeout", "delay_up", "delay_down", "uv_detection", "uv_in_threshold", "uv_out_threshold", "start_color", "on_color", "up_color", "down_color", "shutdown_color", "standby_color", "powercut_color", "error_color", "boot_color", "reboot_method", "power_lp_func", "power_lp_time_min", "power_sp_func", "power_sp_time_min", "reboot_func", "ign_func", "sys_led")
    PON_MIN_TEMP_FIELD_NUMBER: _ClassVar[int]
    PON_MAX_TEMP_FIELD_NUMBER: _ClassVar[int]
    STANDBY_MODE_FIELD_NUMBER: _ClassVar[int]
    BOOT_DELAY_FIELD_NUMBER: _ClassVar[int]
    WD_TOUT_FIELD_NUMBER: _ClassVar[int]
    WD_REBOOT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    WD_REBOOT_WINDOW_FIELD_NUMBER: _ClassVar[int]
    WD_BOOT_DELAY_FIELD_NUMBER: _ClassVar[int]
    WD_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    PWRCYCLE_TIME_FIELD_NUMBER: _ClassVar[int]
    SHUTDOWN_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    ERROR_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DELAY_UP_FIELD_NUMBER: _ClassVar[int]
    DELAY_DOWN_FIELD_NUMBER: _ClassVar[int]
    UV_DETECTION_FIELD_NUMBER: _ClassVar[int]
    UV_IN_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    UV_OUT_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    START_COLOR_FIELD_NUMBER: _ClassVar[int]
    ON_COLOR_FIELD_NUMBER: _ClassVar[int]
    UP_COLOR_FIELD_NUMBER: _ClassVar[int]
    DOWN_COLOR_FIELD_NUMBER: _ClassVar[int]
    SHUTDOWN_COLOR_FIELD_NUMBER: _ClassVar[int]
    STANDBY_COLOR_FIELD_NUMBER: _ClassVar[int]
    POWERCUT_COLOR_FIELD_NUMBER: _ClassVar[int]
    ERROR_COLOR_FIELD_NUMBER: _ClassVar[int]
    BOOT_COLOR_FIELD_NUMBER: _ClassVar[int]
    REBOOT_METHOD_FIELD_NUMBER: _ClassVar[int]
    POWER_LP_FUNC_FIELD_NUMBER: _ClassVar[int]
    POWER_LP_TIME_MIN_FIELD_NUMBER: _ClassVar[int]
    POWER_SP_FUNC_FIELD_NUMBER: _ClassVar[int]
    POWER_SP_TIME_MIN_FIELD_NUMBER: _ClassVar[int]
    REBOOT_FUNC_FIELD_NUMBER: _ClassVar[int]
    IGN_FUNC_FIELD_NUMBER: _ClassVar[int]
    SYS_LED_FIELD_NUMBER: _ClassVar[int]
    pon_min_temp: int
    pon_max_temp: int
    standby_mode: bool
    boot_delay: int
    wd_tout: int
    wd_reboot_threshold: int
    wd_reboot_window: int
    wd_boot_delay: int
    wd_strategy: WatchdogStrategy
    pwrcycle_time: int
    shutdown_timeout: int
    error_timeout: int
    delay_up: int
    delay_down: int
    uv_detection: bool
    uv_in_threshold: int
    uv_out_threshold: int
    start_color: _colorLED_pb2.Color
    on_color: _colorLED_pb2.Color
    up_color: _colorLED_pb2.Color
    down_color: _colorLED_pb2.Color
    shutdown_color: _colorLED_pb2.Color
    standby_color: _colorLED_pb2.Color
    powercut_color: _colorLED_pb2.Color
    error_color: _colorLED_pb2.Color
    boot_color: _colorLED_pb2.Color
    reboot_method: RebootMethod
    power_lp_func: str
    power_lp_time_min: int
    power_sp_func: str
    power_sp_time_min: int
    reboot_func: str
    ign_func: str
    sys_led: int
    def __init__(self, pon_min_temp: _Optional[int] = ..., pon_max_temp: _Optional[int] = ..., standby_mode: _Optional[bool] = ..., boot_delay: _Optional[int] = ..., wd_tout: _Optional[int] = ..., wd_reboot_threshold: _Optional[int] = ..., wd_reboot_window: _Optional[int] = ..., wd_boot_delay: _Optional[int] = ..., wd_strategy: _Optional[_Union[WatchdogStrategy, str]] = ..., pwrcycle_time: _Optional[int] = ..., shutdown_timeout: _Optional[int] = ..., error_timeout: _Optional[int] = ..., delay_up: _Optional[int] = ..., delay_down: _Optional[int] = ..., uv_detection: _Optional[bool] = ..., uv_in_threshold: _Optional[int] = ..., uv_out_threshold: _Optional[int] = ..., start_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., on_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., up_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., down_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., shutdown_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., standby_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., powercut_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., error_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., boot_color: _Optional[_Union[_colorLED_pb2.Color, str]] = ..., reboot_method: _Optional[_Union[RebootMethod, str]] = ..., power_lp_func: _Optional[str] = ..., power_lp_time_min: _Optional[int] = ..., power_sp_func: _Optional[str] = ..., power_sp_time_min: _Optional[int] = ..., reboot_func: _Optional[str] = ..., ign_func: _Optional[str] = ..., sys_led: _Optional[int] = ...) -> None: ...

class ConfigurationDescribe(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationDescribeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConfigurationResponse(_message.Message):
    __slots__ = ("get", "set", "describe")
    GET_FIELD_NUMBER: _ClassVar[int]
    SET_FIELD_NUMBER: _ClassVar[int]
    DESCRIBE_FIELD_NUMBER: _ClassVar[int]
    get: ConfigurationGetResponse
    set: ConfigurationSetResponse
    describe: ConfigurationDescribeResponse
    def __init__(self, get: _Optional[_Union[ConfigurationGetResponse, _Mapping]] = ..., set: _Optional[_Union[ConfigurationSetResponse, _Mapping]] = ..., describe: _Optional[_Union[ConfigurationDescribeResponse, _Mapping]] = ...) -> None: ...

class StateCommandResponse(_message.Message):
    __slots__ = ("response", "message")
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    response: StateCommandResponseType
    message: str
    def __init__(self, response: _Optional[_Union[StateCommandResponseType, str]] = ..., message: _Optional[str] = ...) -> None: ...

class HostCommandResponse(_message.Message):
    __slots__ = ("response", "message")
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    response: HostCommandResponseType
    message: str
    def __init__(self, response: _Optional[_Union[HostCommandResponseType, str]] = ..., message: _Optional[str] = ...) -> None: ...

class FunctionControlGet(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FunctionControlSet(_message.Message):
    __slots__ = ("kick", "error", "resolve", "fatal", "shutdown", "on", "reboot")
    KICK_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESOLVE_FIELD_NUMBER: _ClassVar[int]
    FATAL_FIELD_NUMBER: _ClassVar[int]
    SHUTDOWN_FIELD_NUMBER: _ClassVar[int]
    ON_FIELD_NUMBER: _ClassVar[int]
    REBOOT_FIELD_NUMBER: _ClassVar[int]
    kick: bool
    error: str
    resolve: str
    fatal: str
    shutdown: bool
    on: bool
    reboot: bool
    def __init__(self, kick: _Optional[bool] = ..., error: _Optional[str] = ..., resolve: _Optional[str] = ..., fatal: _Optional[str] = ..., shutdown: _Optional[bool] = ..., on: _Optional[bool] = ..., reboot: _Optional[bool] = ...) -> None: ...

class FunctionControlGetResponse(_message.Message):
    __slots__ = ("state",)
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: SystemState
    def __init__(self, state: _Optional[_Union[SystemState, str]] = ...) -> None: ...

class FunctionControlSetResponse(_message.Message):
    __slots__ = ("state_error", "host_error")
    STATE_ERROR_FIELD_NUMBER: _ClassVar[int]
    HOST_ERROR_FIELD_NUMBER: _ClassVar[int]
    state_error: StateCommandResponse
    host_error: HostCommandResponse
    def __init__(self, state_error: _Optional[_Union[StateCommandResponse, _Mapping]] = ..., host_error: _Optional[_Union[HostCommandResponse, _Mapping]] = ...) -> None: ...

class StreamControlStart(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StreamData(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
