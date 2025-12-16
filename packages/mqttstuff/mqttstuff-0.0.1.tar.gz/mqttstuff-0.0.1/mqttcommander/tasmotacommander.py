import difflib
import json
import os
import textwrap
import threading

from datetime import timedelta, date, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Literal, Set, Optional, List, Dict, Annotated, ClassVar
from uuid import UUID

from pydantic import BaseModel, Field, AliasPath, field_validator, AliasChoices

import config

from mqttstuff.mosquittomqttwrapper import MWMqttMessage, MosquittoClientWrapper, MQTTLastDataReader

from loguru import logger

logger.debug(f"{__name__} DEBUG")
logger.info(f"{__name__} INFO")

# from rich import print as rprint

from pydantic.networks import IPv4Address
from pydantic_extra_types.mac_address import MacAddress

# MacAddress.validate_mac_address("80646FA760E6".encode())
# MacAddress.validate_mac_address("80:64:6F:A7:60:E6".encode())
# maca: MacAddress = MacAddress("80:64:6F:A7:60:E6")

# print(maca.model_dump())
# exit(1)

class TasmotaTimerConfig(BaseModel):
    # Enable	0 = disarm or disable timer
    # 1 = arm or enable timer
    enable: Optional[Annotated[int, Field(ge=0, le=1)]] = Field(None, validation_alias=AliasChoices("Enable", "enable"))

    # Mode	0 = use clock time
    # 1 = Use local sunrise time using Longitude, Latitude and Time offset
    # 2 = use local sunset time using Longitude, Latitude and Time offset
    mode: Optional[Annotated[int, Field(ge=0, le=2)]] = Field(None, validation_alias=AliasChoices("Mode", "mode"))

    # Time	When Mode 0 is active
    # > hh:mm = set time in hours 0 .. 23 and minutes 0 .. 59
    # When Mode 1 or Mode 2 is active
    # > +hh:mm or -hh:mm = set offset in hours 0 .. 11 and minutes 0 .. 59 from the time defined by sunrise/sunset.
    time: Optional[str] = Field(None, validation_alias=AliasChoices("Time", "time"))

    # Window	0..15 = add or subtract a random number of minutes to Time
    window: Optional[Annotated[int, Field(ge=0, le=15)]] = Field(None, validation_alias=AliasChoices("Window", "window"))

    # Days	SMTWTFS = set day of weeks mask where 0 or - = OFF and any different character = ON
    days: Optional[Annotated[str, Field(pattern="[1|0|-]{7}")]] = Field(None, validation_alias=AliasChoices("Days", "days"))

    # Repeat	0 = allow timer only once
    # 1 = repeat timer execution
    repeat: Optional[Annotated[int, Field(ge=0, le=1)]] = Field(None, validation_alias=AliasChoices("Repeat", "repeat"))

    # Output	1..16 = select an output to be used if no rule is enabled
    output: Optional[Annotated[int, Field(ge=1, le=16)]] = Field(None, validation_alias=AliasChoices("Output", "output"))

    # Action	0 = turn output OFF
    # 1 = turn output ON
    # 2 = TOGGLE output
    # 3 = RULE/BLINK
    # If the Tasmota Rules feature has been activated by compiling the code (activated by default in all pre-compiled Tasmota binaries), a rule with Clock#Timer=<timer> will be triggered if written and turned on by the user.
    # If Rules are not compiled, BLINK output using BlinkCount parameters.
    action: Optional[Annotated[int, Field(ge=1, le=16)]] = Field(None, validation_alias=AliasChoices("Action", "action"))

    # {"Timer1":{"Enable":1,"Mode":0,"Time":"22:00","Window":0,"Days":"1111111","Repeat":1,"Output":1,"Action":0}}





class TasmotaTimeZoneDSTSTD(BaseModel):
    hemisphere: Optional[int] = Field(None, validation_alias=AliasChoices("Hemisphere", "hemisphere"))
    week: Optional[int] = Field(None, validation_alias=AliasChoices("Week", "week"))
    month: Optional[int] = Field(None, validation_alias=AliasChoices("Month", "month"))
    day: Optional[int] = Field(None, validation_alias=AliasChoices("Day", "day"))
    hour: Optional[int] = Field(None, validation_alias=AliasChoices("Hour", "hour"))
    offset: Optional[int] = Field(None, validation_alias=AliasChoices("Offset", "offset"))

class TasmotaTimezoneConfig(BaseModel):
    latitude: Optional[float] = Field(None, validation_alias=AliasChoices("Latitude", "latitude"))
    longitude: Optional[float] = Field(None, validation_alias=AliasChoices("Longitude", "longitude"))
    timedst: Optional[TasmotaTimeZoneDSTSTD] = Field(None, validation_alias=AliasChoices("TimeDst", "timedst"))
    timestd: Optional[TasmotaTimeZoneDSTSTD] = Field(None, validation_alias=AliasChoices("TimeStd", "timestd"))
    timezone: Optional[int|str] = Field(None, validation_alias=AliasChoices("Timezone", "timezone"))  # 99 | +01:00

class TasmotaDeviceConfig(BaseModel):
    friendly_name: Optional[str] = Field(None, validation_alias=AliasChoices("friendly_name", AliasPath('fn', 0)))  # friendly name -> first element of list of strings?
    device_name: Optional[str] = Field(None, validation_alias=AliasChoices("dn", "device_name"))
    hostname: Optional[str]  = Field(None, validation_alias=AliasChoices("hn", "hostname")) # host name
    manufacturer_description: Optional[str] = Field(None, validation_alias=AliasChoices("md", "manufacturer_description")) # manufacturer description ?!
    ip: Optional[IPv4Address] = None
    mac: Optional[MacAddress] = None
    offline_msg: Optional[str] = Field(None, validation_alias=AliasChoices("ofln", "offline_msg"))
    online_msg: Optional[str] = Field(None, validation_alias=AliasChoices("onln", "online_msg"))
    state: Optional[List[str]] = None
    #t: str = Field(alias="topic", validation_alias='t')
    topic: Optional[str] = Field(None, validation_alias=AliasChoices("t", "topic"))
    tp: Optional[List[str]] = Field(None)
    software_version: Optional[str] = Field(None, validation_alias=AliasChoices('sw', "software_version"))
    timezoneconfig: Optional[TasmotaTimezoneConfig] = None
    teleperiod: Optional[int] = Field(None, validation_alias=AliasChoices("TelePeriod", "teleperiod"))
    powerdelta1: Optional[int] = Field(None, validation_alias=AliasChoices("PowerDelta1", "powerdelta1"))
    setoption4: Optional[Literal['ON', 'OFF']] = Field(None, validation_alias=AliasChoices("SetOption4", "setoption4"))
    timer1: Optional[TasmotaTimerConfig] = Field(None, validation_alias=AliasChoices("Timer1", "timer1"))
    timer2: Optional[TasmotaTimerConfig] = Field(None, validation_alias=AliasChoices("Timer2", "timer2"))
    timer3: Optional[TasmotaTimerConfig] = Field(None, validation_alias=AliasChoices("Timer2", "timer3"))
    timer4: Optional[TasmotaTimerConfig] = Field(None, validation_alias=AliasChoices("Timer4", "timer4"))


    # SSID1
    # SSID2
    # powerdelta
    # ampres
    # voltres
    # setoption4
    # SetOption53 1; SetOption56 0; SetOption57 0;

    @field_validator('mac', mode="before")
    @classmethod
    def validate_mac(cls, v: Any) -> Optional[str]:
        # logger.debug(f"VALIDATE MAC: {v}")
        if not v:
            return None

        return cls.mac_no_colon_to_colon(v)

    @staticmethod
    def mac_no_colon_to_colon(mac: str) -> str:
        if mac.find(":") == 2:
            return mac

        ret: StringIO = StringIO()
        for ch2i in range(0, len(mac), 2):
            if ret.tell() > 0:
                ret.write(":")
            ret.write(mac[ch2i:ch2i + 2])

        return ret.getvalue()


class TasmotaRule(BaseModel):
    state: Optional[Literal['ON','OFF']] = Field(None, validation_alias=AliasChoices("State", "state"))
    once: Optional[Literal['ON','OFF']] = Field(None, validation_alias=AliasChoices("Once", "once"))
    stoponerror: Optional[Literal['ON','OFF']] = Field(None, validation_alias=AliasChoices("StopOnError", "stoponerror"))
    length: Optional[int] = Field(None, validation_alias=AliasChoices("Length", "length"))
    rules: Optional[str] = Field(None, validation_alias=AliasChoices("Rules", "rules"))

class TasmotaDeviceSensors(BaseModel):
    # tasmota/discovery/x/sensors
    # sn: dict
    time: datetime = Field(..., validation_alias=AliasChoices("time", "Time",AliasPath('sn', "Time")))

    # {"sn": {"Time": "2024-07-04T13:09:25", "ANALOG": {"A0": 169},
    #        "SHT3X": {"Temperature": 26.1, "Humidity": 44.5, "DewPoint": 13.1}, "TempUnit": "C"}, "ver": 1}

class TasmotaDevice(BaseModel):
    # tasmota/discovery/x/config
    tasmota_config: Optional[TasmotaDeviceConfig] = None
    tasmota_sensors: Optional[TasmotaDeviceSensors] = None
    tasmota_rule1: Optional[TasmotaRule] = None
    tasmota_rule2: Optional[TasmotaRule] = None
    tasmota_rule3: Optional[TasmotaRule] = None

    lwt_current_value: Optional[Literal['Online', 'Offline']] = None

    def is_online(self, lwt_online_default_value: str = "Online") -> bool:
        if self.tasmota_config and self.tasmota_config.online_msg:
            return self.lwt_current_value == self.tasmota_config.online_msg

        return self.lwt_current_value == lwt_online_default_value

    # 2024-09-15T12:13:31.007101+0200 | DEBUG | None:main:255 - [051] tasmota/discovery/441793221AF4/config	[type(msg.value)=<class 'str'>] {
    # "ip":"192.168.102.156","dn":"azenvy5","fn":["azenvy5FN",null,null,null,null,null,null,null],"hn":"azenvy5","mac":"441793221AF4","md":"AZ Envy","
    # ty":0,"if":0,"ofln":"Offline","onln":"Online","state":["OFF","ON","TOGGLE","HOLD"],"sw":"14.1.0","t":"tasmota_221AF4","
    # ft":"%prefix%/%topic%/","tp":["cmnd","stat","tele"],"rl":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    # 0,0,0],"swc":[-1,-1,-1,-1,-1,-1,-1,-1,-1,-
    # 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    # -1,-1,-1,-1,-1,-1],"swn":[null,null,null,
    # null,null,null,null,null,null,null,null,
    # null,null,null,null,null,null,null,null,null
    # ,null,null,null,null,null,null,null,
    # null],"btn":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    # 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    # ,0,0],"so":{"4":0,"11":0,"13":0,"17":0,"20":0,"30":0,"68":0,"73":0,"82":0,"114":0,"117":0},"lk":0,"lt_st":0,"bat":0,"dslp":0,"sho":[],"sht":[],"ver":1}
    # 2024-09-15T12:13:31.007111+0200 | DEBUG | None:main:255 - [052] tasmota/discovery/441793221AF4/sensors	[type(msg.value)=<class 'str'>]
    # {"sn":{"Time":"2024-07-04T13:09:25","ANALOG":{"A0":169},"SHT3X":{"Temperature":26.1,"Humidity":44.5,"DewPoint":13.1},"TempUnit":"C"},"ver":1}

# class TasmotaDeviceList(BaseModel):
#     tasmotas: List[TasmotaDevice]

def print_pretty_dict_json(data: Any, indent: int = 4) -> None:
    print(json.dumps(data, indent=indent, sort_keys=True, cls=ComplexEncoder, default=str))


def get_pretty_dict_json(data: Any, indent: int = 4) -> str:
    return json.dumps(data, indent=indent, sort_keys=True, cls=ComplexEncoder, default=str)


def get_pretty_dict_json_no_sort(data: Any, indent: int = 4) -> str:
    return json.dumps(data, indent=indent, sort_keys=False, cls=ComplexEncoder, default=str)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if hasattr(obj, "repr_json"):
            return obj.repr_json()
        elif hasattr(obj, "as_string"):
            return obj.as_string()
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()  # strftime("%Y-%m-%d %H:%M:%S %Z")
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, dict) or isinstance(obj, list):
            robj: str = get_pretty_dict_json_no_sort(obj)
            return robj
        else:
            return json.JSONEncoder.default(self, obj)


class MqttCommander:
    logger: ClassVar = logger.bind(classname=__qualname__)
    _msg_topicname_startwith_drop_filter_defaultset: ClassVar[Set[str]] = {"tele/rtl_433"}

    # TODO ADD RECEIVE_TRIGGERS

    def __init__(self,
                 topics: list[str],
                 msg_topicname_startwith_drop_filter: Set|None=_msg_topicname_startwith_drop_filter_defaultset  # type: ignore
                 ):
        self.msg_topicname_startwith_drop_filter = msg_topicname_startwith_drop_filter
        if msg_topicname_startwith_drop_filter is self.__class__._msg_topicname_startwith_drop_filter_defaultset:
            self.__class__.logger.debug("DEFAULT SET REPLACED!")
            self.msg_topicname_startwith_drop_filter: Set[str] = set()  # type: ignore
            self.msg_topicname_startwith_drop_filter.update(msg_topicname_startwith_drop_filter)
            
        self.mqttclient: MosquittoClientWrapper = MosquittoClientWrapper(
            host=config.settings.mqtt.host,
            port=config.settings.mqtt.port,
            username=config.settings.mqtt.username,
            password=config.settings.mqtt.password
        )
        self.topics = topics
        self.mqttclient.set_topics(topics)
        self.cmdsent: bool = False


    def apply_topic_filter(self, msgs: list[MWMqttMessage] | None) -> list[MWMqttMessage] | None:
        if self.msg_topicname_startwith_drop_filter is None or msgs is None:
            return msgs

        ret: list[MWMqttMessage] = []
        for msg in msgs:
            for sw in self.msg_topicname_startwith_drop_filter:
                if not msg.topic.startswith(sw):
                    ret.append(msg)

        if len(ret) == 0:
            return None

        return ret

    def get_all_retained(self, topics: list[str]|None = None, retained_msgs_receive_grace_ms: int = 2_000, noisy: bool = False,
                         rettype: Literal["json", "str", "int", "float", "valuemsg", "str_raw"] = "str_raw",
                         fallback_rettype: Literal["json", "str", "int", "float", "valuemsg", "str_raw"] = "str_raw") -> list[MWMqttMessage]|None:

        if topics is None:
            topics = self.topics

        msgs: list[MWMqttMessage] | None = MQTTLastDataReader.get_most_recent_data_with_timeout(
            host=config.settings.mqtt.host,
            port=config.settings.mqtt.port,
            username=config.settings.mqtt.username,
            password=config.settings.mqtt.password,
            topics=topics,
            noisy=noisy,
            timeout_msgreceived_seconds=retained_msgs_receive_grace_ms / 1000.0,
            retained="only",
            max_received_msgs=-1,
            rettype=rettype,
            fallback_rettype=fallback_rettype
        )

        msgs = self.apply_topic_filter(msgs)

        return msgs


    def start_loop_forever(self, rettype: Literal["json", "str", "int", "float", "valuemsg", "str_raw"] = "str_raw") -> None:
        #self.mqttclient.add_message_callback("tele/tasmota_183BC5/LWT", self.on_msg_received)
        self.mqttclient.set_on_msg_callback(self.on_msg_received, rettype=rettype)
        self.mqttclient.connect_and_start_loop_forever(topics=self.topics)

    def on_msg_received(self, msg: MWMqttMessage, userdata: Any) -> None:
        if self.msg_topicname_startwith_drop_filter is not None:
            for sw in self.msg_topicname_startwith_drop_filter:
                if msg.topic.startswith(sw):
                    return

        self.__class__.logger.debug(
            get_pretty_dict_json_no_sort(msg.model_dump(by_alias=True))
        )




def get_all_tasmota_devices_from_retained(topics: List[str]|None = None, noisy: bool = False, noisy_lowerlevel: bool = False) -> list[TasmotaDevice]:
    topics = topics or ["tasmota/discovery/#", "tele/+/LWT"]
    ret: list[TasmotaDevice] = []

    mqtc: MqttCommander = MqttCommander(topics=topics)

    msgs: list[MWMqttMessage] | None = mqtc.get_all_retained(
        retained_msgs_receive_grace_ms=2_000,
        rettype="json",
        noisy=noisy_lowerlevel,
        topics=topics,
        fallback_rettype="str_raw"
    )

    tdlookup: dict[str, TasmotaDevice] = {}
    td: TasmotaDevice | None

    if msgs:
        # first run for discovery...
        for num, msg in enumerate(msgs, start=1):
            if noisy:
                logger.debug(f"DIS [{num:03}] {msg.topic}\t[{type(msg.value)=}] {msg.value}")

            if msg.topic.startswith("tasmota/discovery"):
                maclookupkey: str = msg.topic[0:msg.topic.rfind("/")]
                maclookupkey = maclookupkey[maclookupkey.rfind("/")+1:]

                td = tdlookup.get(maclookupkey)
                if noisy:
                    logger.debug(f"LOOKUP [{msg.topic}] for {maclookupkey} GOT: {td=}")
                if td is None:
                    td = TasmotaDevice()
                    tdlookup[maclookupkey] = td
                    ret.append(td)

                if msg.topic.endswith("config"):
                    assert isinstance(msg.value, dict)
                    td.tasmota_config=TasmotaDeviceConfig(**msg.value)
                    if noisy:
                        logger.debug(
                            get_pretty_dict_json_no_sort(
                                td.model_dump(mode="python", exclude_none=False, exclude_defaults=False, by_alias=False)
                            )
                        )

                    assert td.tasmota_config.topic
                    tdlookup[td.tasmota_config.topic] = td
                elif msg.topic.endswith("sensors"):
                    assert isinstance(msg.value, dict)
                    td.tasmota_sensors=TasmotaDeviceSensors(**msg.value)
                    if noisy:
                        logger.debug(
                            get_pretty_dict_json_no_sort(
                                td.model_dump(mode="python", exclude_none=False, exclude_defaults=False, by_alias=False)
                            )
                        )


        # second run for LWT status
        for num, msg in enumerate(msgs, start=1):
            if noisy:
                logger.debug(f"LWT [{num:03}] {msg.topic}\t[{type(msg.value)=}] {msg.value}")

            if msg.topic.startswith("tele/") and msg.topic.endswith("LWT"):
                mytopic: str = msg.topic.split("/")[1]

                td = tdlookup.get(mytopic)
                if noisy:
                    logger.debug(f"LOOKUP [{msg.topic}] for {mytopic} GOT: {td=}")

                if td is None:
                    td = TasmotaDevice()
                    td.tasmota_config = TasmotaDeviceConfig()  # type: ignore
                    td.tasmota_config.topic = mytopic

                    tdlookup[mytopic] = td
                    ret.append(td)

                td.lwt_current_value = msg.value  # type: ignore

    return ret

def write_tasmota_devices_file(tasmotas: List[TasmotaDevice], fp: Path|None = None, noisy: bool = False) -> Path:
    if fp is None:
        fp = Path(__file__)
        fp = Path(fp.parent.resolve(), "tasmotas")
        if not fp.exists():
            fp.mkdir()

        now: datetime = datetime.now(tz=config.TZBERLIN)
        fp = Path(fp, f"tasmota_devices_{now:%d-%m-%Y_%H%M%S}.json")


    with open(fp, "w") as fout:
        fout.write("[\n")

        for num, tasmota in enumerate(tasmotas, start=1):
            if num > 1:
                fout.write(",\n")

            outs: str = get_pretty_dict_json_no_sort(
                tasmota.model_dump(
                    mode="python",
                    exclude_none=False,
                    exclude_defaults=False,
                    by_alias=False
                )
            )

            if noisy:
                logger.debug(
                    f"[{num}]\n{outs}")

            fout.write(outs)

        fout.write("\n]\n")
        fout.flush()

    logger.debug(f"TASMOTA DEVICES WRITTEN TO: {fp.resolve()}")

    return fp

def update_online_tasmotas(tasmotas: List[TasmotaDevice]) -> List[TasmotaDevice]:
    tasmota_online: List[TasmotaDevice] = []

    for tdo in tasmotas:
        if not tdo.is_online():
            continue

    for num, tdo in enumerate(tasmotas, start=1):
        assert tdo.tasmota_config is not None

        if not tdo.is_online():
            logger.debug(f"[{num}]*OFFLINE* {tdo.tasmota_config.topic} -> {tdo.tasmota_config.topic} -> LWT={tdo.lwt_current_value}")
        else:
            logger.debug(f"[{num}]*ONLINE* {tdo.tasmota_config.device_name} -> {tdo.tasmota_config.topic} -> LWT={tdo.lwt_current_value}")
            tasmota_online.append(tdo)

    tasmota_online = send_cmds_to_online_tasmotas(
        tasmotas=tasmota_online,
        to_be_used_commands=None,  # nimmt dann die default status-commands...
        values_to_send=None  # sendet dann empty command -> returned nur den status
    )

    return tasmota_online


def send_cmds_to_online_tasmotas(tasmotas: List[TasmotaDevice], to_be_used_commands: List[str]|None = None, values_to_send: List[List[str|float|dict|int]|None]|None = None) -> List[TasmotaDevice]:
    to_be_used_commands = to_be_used_commands or [
        "RULE1",
        "RULE2",
        "RULE3",
        "TIMEZONE",
        "LATITUDE",
        "LONGITUDE",
        "TIMEDST",
        "TIMESTD",
        "TELEPERIOD",
        "POWERDELTA1",
        "SETOPTION4",
        "TIMER1",
        "TIMER2",
        "TIMER3",
        "TIMER4"
    ]

    values_to_send = values_to_send or [None for _ in tasmotas]

    assert len(values_to_send) == len(tasmotas),  f"{len(values_to_send)=} =! {len(tasmotas)=}"

    tasmota_online: List[TasmotaDevice] = []
    values_to_send_online: List[List[str|float|dict|int]|None] = []

    for num, (tdo, vt) in enumerate(zip(tasmotas, values_to_send), start=1):
        assert tdo.tasmota_config is not None

        if not tdo.is_online():
            logger.debug(f"[{num}]*OFFLINE* {tdo.tasmota_config.topic} -> {tdo.tasmota_config.topic} -> LWT={tdo.lwt_current_value}")
        else:
            logger.debug(f"[{num}]*ONLINE* {tdo.tasmota_config.device_name} -> {tdo.tasmota_config.topic} -> LWT={tdo.lwt_current_value}")
            logger.debug(f"\t{vt=}")
            tasmota_online.append(tdo)
            values_to_send_online.append(vt)

            if vt:
                assert len(vt) == len(to_be_used_commands), f"{len(vt)=} != {len(to_be_used_commands)=}"

    topics: List[str] = ["stat/+/RESULT", "stat/+/STATUS"]
    cmd_to_topic_map: Dict[str, str] = {}

    # cmnd/tasmota_06888F/SetOption4 1 => enables mqtt result to stat/tasmota_06888F/[CMDNAME]
    for cmd in to_be_used_commands:
        if cmd[-1].isdigit():
            cmd_to_topic_map[cmd] = cmd[0:-1]
        else:
            cmd_to_topic_map[cmd] = cmd

    for v in set(cmd_to_topic_map.values()):
        topics.append(f"stat/+/{v}")

    logger.debug("cmd_to_topic_map:")
    logger.debug(cmd_to_topic_map)

    logger.debug("TOPICS:")
    logger.debug(topics)

    # logger.debug("Sleeping 10s")
    # time.sleep(10)


    mq: MosquittoClientWrapper = MosquittoClientWrapper(
        host=config.settings.mqtt.host,
        port=config.settings.mqtt.port,
        username=config.settings.mqtt.username,
        password=config.settings.mqtt.password,
        # topics=[f"stat/{td.tasmota_config.topic}/#"],
        topics=topics,
        timeout_connect_seconds=5
    )

    # mq.add_message_callback("f"stat/{td.tasmota_config.topic}/")
    mq.wait_for_connect_and_start_loop()

    for num, (td, vt) in enumerate(zip(tasmota_online, values_to_send_online), start=1):
        assert td.tasmota_config is not None

        logger.debug(f"{num}: {td.tasmota_config.topic} -> {vt=}")

        tzconfig: Dict = td.tasmota_config.timezoneconfig.model_dump() if td.tasmota_config.timezoneconfig else {}

        for index, cmd in enumerate(to_be_used_commands):
            to_send_value: None|str|float|dict = None
            if vt:
                to_send_value = vt[index]

            cmd_topic: str = f"cmnd/{td.tasmota_config.topic}/{cmd}"

            logger.debug(f"\t{cmd_topic=} -> {to_send_value=}")

            cmd_res: str = cmd_to_topic_map[cmd]

            result_topic: str = f"stat/{td.tasmota_config.topic}/RESULT"
            cmd_res_topic: str = f"stat/{td.tasmota_config.topic}/{cmd_res}"

            msg_received_cond: threading.Condition = threading.Condition()
            # msg_received_bool: bool = False
            resp_data: Dict[str, MWMqttMessage] = {}

            def msg_received(msg: MWMqttMessage, userdata: Any) -> None:
                logger.debug(f"MSG Received :: {msg=} {userdata=}")

                with msg_received_cond:
                    msg_received_cond.notify_all()
                    # msg_received_bool = True
                    resp_data[msg.topic] = msg


            # mq.set_on_msg_callback(msg_received, rettype="str")  # rettype="str" macht ein auto-try auf json-decode...
            mq.add_message_callback(sub=result_topic, callback=msg_received, rettype="str")
            mq.add_message_callback(sub=cmd_res_topic, callback=msg_received, rettype="str")

            # td.tasmota_config.tp[0] -> cmnd
            # td.tasmota_config.tp[1] ->stat
            # td.tasmota_config.tp[1] ->tele

            published_success: bool = mq.publish_one(topic=cmd_topic, value=to_send_value, timeout=5)
            logger.debug(f"{cmd_topic} [{td.tasmota_config.device_name}] -> published {to_send_value=} -> {published_success=}")

            if not published_success:
                logger.debug("SKIPPING since not properly published...")
                continue

            with msg_received_cond:
                wait_success: bool = msg_received_cond.wait(timeout=10)
                logger.debug(f"MSG[{result_topic}] -> WaitingSuccess {wait_success=}")
                if not wait_success:
                    logger.debug("SKIPPING since no msg received properly...")
                    continue


                wait2: bool = msg_received_cond.wait_for(lambda: result_topic in resp_data or cmd_res_topic in resp_data, timeout=10)
                logger.debug(f"Waiting for {result_topic}|{cmd_res_topic} [{td.tasmota_config.device_name}] to be in resp_data: {wait2=}")
                if not wait2:
                    logger.debug("SKIPPING since response not received properly...")
                    continue

            msg_me: MWMqttMessage|None = resp_data.get(result_topic, resp_data.get(cmd_res_topic, None))
            logger.debug(f"{msg_me=}")

            assert msg_me is not None and msg_me.value is not None and isinstance(msg_me.value, dict)

            # {"Command":"Unknown"
            if "Command" in msg_me.value and msg_me.value["Command"] == "Unknown":
                logger.debug("SKIPPING since command is not known to this DEVICE...")

                if result_topic in resp_data:
                    del resp_data[result_topic]
                if cmd_res_topic in resp_data:
                    del resp_data[cmd_res_topic]

                continue

            match cmd:
                case "RULE1":
                    td.tasmota_rule1 = TasmotaRule(**msg_me.value["Rule1"])
                case "RULE2":
                    td.tasmota_rule2 = TasmotaRule(**msg_me.value["Rule2"])
                case "RULE3":
                    td.tasmota_rule3 = TasmotaRule(**msg_me.value["Rule3"])
                case "TIMEZONE" | "LATITUDE" | "LATITUDE" | "LONGITUDE" | "TIMEDST" | "TIMESTD":
                    tzconfig.update(**msg_me.value)
                case "TELEPERIOD":
                    td.tasmota_config.teleperiod = msg_me.value["TelePeriod"]
                case "POWERDELTA1":
                    td.tasmota_config.powerdelta1 = msg_me.value["PowerDelta1"]
                case "SETOPTION4":
                    td.tasmota_config.setoption4 = msg_me.value["SetOption4"]
                case "TIMER1":
                    td.tasmota_config.timer1 = msg_me.value["Timer1"]
                case "TIMER2":
                    td.tasmota_config.timer2 = msg_me.value["Timer2"]
                case "TIMER3":
                    td.tasmota_config.timer3 = msg_me.value["Timer3"]
                case "TIMER4":
                    td.tasmota_config.timer4 = msg_me.value["Timer4"]


                # 17:04:45.530 CMD: setoption4 1
                # 17:04:45.535 MQT: stat/tasmota_AB65C8/SETOPTION = {"SetOption4":"ON"}
                # 17:04:46.840 CMD: powerdelta
                # 17:04:46.846 MQT: stat/tasmota_AB65C8/POWERDELTA = {"PowerDelta1":103}

            if result_topic in resp_data:
                del resp_data[result_topic]
            if cmd_res_topic in resp_data:
                del resp_data[cmd_res_topic]

            mq.remove_message_callback(sub=result_topic)
            mq.remove_message_callback(sub=cmd_res_topic)

        # logger.debug(f"tzconfig:{get_pretty_dict_json(tzconfig)}")
        if len(tzconfig) > 0:
            logger.debug("OLD TZ CONFIG:")
            if td.tasmota_config.timezoneconfig:
                logger.debug(td.tasmota_config.timezoneconfig.model_dump())
            else:
                logger.debug("NONE")

            td.tasmota_config.timezoneconfig = TasmotaTimezoneConfig(**tzconfig)
            logger.debug("NEW TZ CONFIG:")
            logger.debug(td.tasmota_config.timezoneconfig.model_dump())

        # logger.debug(get_pretty_dict_jsonnosort(td.model_dump(mode="python", exclude_none=False, exclude_defaults=False, by_alias=False)))

    mq.disconnect()

    return tasmotas



def ensure_correct_timezone_settings_for_tasmotas(online_tasmotas: List[TasmotaDevice]) -> List[TasmotaDevice]:
    to_be_updated_tasmotas: List[TasmotaDevice] = []

    to_be_sent_commands: List[str] = [
        "Latitude",
        "Longitude",
        "TimeDST",
        "TimeSTD",
        "TimeZone"
    ]
    values_to_send:  list[list[str | float | dict | int] | None] = []

    for tdo in online_tasmotas:
        assert tdo.tasmota_config is not None and tdo.tasmota_config.timezoneconfig is not None

        if tdo.is_online() and tdo.tasmota_config.timezoneconfig.timezone != 99:
            logger.debug(f"TIMEZONE is off for {tdo.tasmota_config.device_name} -> {tdo.tasmota_config.topic} -> TIMEZONE={tdo.tasmota_config.timezoneconfig.timezone}")
            to_be_updated_tasmotas.append(tdo)
            values_to_send.append(
                [
                    53.6437753,
                    9.8940783,
                    "0,0,3,1,1,120",
                    "0,0,10,1,1,60",
                    99
                ]
            )

    return send_cmds_to_online_tasmotas(
        tasmotas=online_tasmotas,
        to_be_used_commands=to_be_sent_commands,
        values_to_send=values_to_send
    )

def read_tasmotas_from_latest_file(tasmota_json_dir: Path|None=None, noisy: bool = False) -> Optional[List[TasmotaDevice]]:
    if tasmota_json_dir is None:
        tasmota_json_dir = Path(__file__)
        tasmota_json_dir = Path(tasmota_json_dir.parent.resolve(), "tasmotas")
        if not tasmota_json_dir.exists():
            tasmota_json_dir.mkdir()

    jsonfiles: List[Path] = [fm for fm in tasmota_json_dir.glob("tasmota_devices_*json")]
    jsonfiles = sorted(jsonfiles, key=lambda p: os.stat(p).st_mtime, reverse=True)

    for f in jsonfiles:
        dateme: datetime = datetime.fromtimestamp(os.stat(f).st_mtime, tz=config.TZBERLIN)
        logger.debug(f"{f.absolute()} -> {dateme}")

        json_data: List[Dict]|Dict|None = None
        with open(f) as fin:
            json_data = json.load(fin)


        if json_data and type(json_data) is list:
            ret: List[TasmotaDevice] = []
            for td_dict in json_data:
                tdm: TasmotaDevice = TasmotaDevice(**td_dict)
                ret.append(tdm)
            return ret
    return None


def filter_online_tasmotas_from_retained(all_tasmotas: List[TasmotaDevice], update_lwt_current_value: bool = True) -> List[TasmotaDevice]:
    all_online_tasmotas: List[TasmotaDevice] = get_all_tasmota_devices_from_retained()

    online_topics: Dict[str, Literal["Online", "Offline"]|None] = {}

    ret: List[TasmotaDevice] = []
    for tdo in all_online_tasmotas:
        assert tdo.tasmota_config is not None

        if tdo.is_online():
            online_topics[tdo.tasmota_config.topic] = tdo.lwt_current_value  # type: ignore
            logger.debug(f"ONLINE: {tdo.tasmota_config.topic}")
        else:
            logger.debug(f"OFFLINE: {tdo.tasmota_config.topic}")

    for tdo in all_tasmotas:
        assert tdo.tasmota_config is not None

        if tdo.tasmota_config.topic in online_topics:
            if update_lwt_current_value:
                tdo.lwt_current_value = online_topics[tdo.tasmota_config.topic]
            ret.append(tdo)

    # online_tasmotas: List[TasmotaDevice] = update_online_tasmotas(tasmotas=all_tasmotas)  # also does updates INLINE !!!

    return ret

def read_tasmotas_from_file_update_save_to_file() -> None:
    tds: List[TasmotaDevice]|None = read_tasmotas_from_latest_file()

    if not tds:
        return

    tds_dumps: List[str] = [
        get_pretty_dict_json_no_sort(td.model_dump(mode="python", exclude_none=False, exclude_defaults=False, by_alias=False)) for td in tds
    ]

    online_tasmotas: List[TasmotaDevice] = filter_online_tasmotas_from_retained(
        all_tasmotas=tds,
        update_lwt_current_value=True
    )

    updated_tasmotas: List[TasmotaDevice] = update_online_tasmotas(tasmotas=online_tasmotas)  # das update_online_tasmots macht AUCH ein inline update -> tds[X] wird aktualisiert...

    for index, td in enumerate(tds):
        mydump: str = get_pretty_dict_json_no_sort(td.model_dump(mode="python", exclude_none=False, exclude_defaults=False, by_alias=False))
        previous_data: str = tds_dumps[index]


        diff_str: StringIO = StringIO()
        changecount: int = 0
        for l in difflib.unified_diff(previous_data, mydump, fromfile=f"PREVIOUS", tofile=f"UPDATED"):
            diff_str.write(l)
            changecount += 1

        assert td.tasmota_config is not None
        if changecount > 0:
            logger.debug(f"{td.tasmota_config.topic} -> [{changecount=}]\n{textwrap.indent(diff_str.getvalue(), "\t")}")
        else:
            logger.debug(f"{td.tasmota_config.topic} -> NOTHING CHANGED.")



    write_tasmota_devices_file(tasmotas=tds)


def main() -> None:
    read_tasmotas_from_file_update_save_to_file()


if __name__ == "__main__":
    # WebPassword	Show current web server password
    # 0 = disable use of password for web UI
    # 1 = reset password to firmware default (WEB_PASSWORD)
    # <value> = set web UI password (32 char limit) for user WEB_USERNAME (Default WEB_USERNAME = admin)
    #
    # decode-config --source mqtt://venom:kaiGh5esgael3OuH@mosquittoi.heidk8.elasticc.io  --fulltopic tele/tasmota_AAF678

    # cmnd/tasmota_06888F/SetOption4 1 => enables mqtt result to stat/tasmota_06888F/[CMDNAME]

    main()

    # cmnd/tasmota_06888F/rule1
    # => stat/tasmota_06888F/RESULT
    # {"Rule1":{"State":"OFF","Once":"OFF","StopOnError":"OFF","Length":258,"Free":253,"Rules":"ON Time#Minute|5 DO BackLog WebQuery http://hetzner3.linkedlabs.de/ GET ENDON ON WebQuery#Data=Done DO Publish stat/tasmota_06888F/CONNECTIVITY OK ENDON ON WebQuery#Data$!Done DO BackLog AP 0 ; Delay 400; Publish stat/tasmota_06888F/CONNECTIVITY FAILED ENDON"}}


    # TODO: stat/tasmota_17968F
    # TODO: cmnd/tasmota_17968F
    # TODO: stat/tasmota_779336/RESULT

    # TODO tele/tasmota_x/STATE
    # {"Time":"2024-09-17T10:17:43","Uptime":"2T21:34:31","UptimeSec":250471,"Heap":25,"SleepMode":"Dynamic","Sleep":50,"LoadAvg":19,"MqttCount":1,"POWER":"OFF","Wifi":{"AP":1,"SSId":"heidk8turris","BSSId":"9A:A6:7E:53:4D:83","Channel":13,"Mode":"11n","RSSI":82,"Signal":-59,"LinkCount":1,"Downtime":"0T00:00:05"}}


    # TODO: tele/tasmota_17968F/SENSOR
    #   LWT = Online
    #   STATE = {"Time":"2024-09-16T09:20:07","Uptime":"0T07:29:11","UptimeSec":26951,"Heap":26,"SleepMode":"Dynamic","Sleep":50,"LoadAvg":19,"MqttCount":11,"POWER":"OFF","Wifi":{"AP":1,"SSId":"heidk8","BSSId":"98:9B:CB:16:FB:C5","Channel":13,"Mode":"11n","RSSI":90,"Signal":-55,"LinkCount":11,"Downtime":"0T00:18:43"}}
    #   SENSOR = {"Time":"2024-09-16T09:20:07","ENERGY":{"TotalStartTime":"2023-05-29T15:19:56","Total":1.703,"Yesterday":0.000,"Today":0.000,"Period":0,"Power":0,"ApparentPower":0,"ReactivePower":0,"Factor":0.00,"Voltage":0,"Current":0.000}}
    #?   INFO1 = {"Info1":{"Module":"NOUS A1T","Version":"14.2.0(release-tasmota)","FallbackTopic":"cmnd/DVES_17968F_fb/","GroupTopic":"cmnd/tasmotas/"}}
    #?   INFO2 = {"Info2":{"WebServerMode":"Admin","Hostname":"nous8","IPAddress":"192.168.101.192"}}
    #?   INFO3 = {"Info3":{"RestartReason":"Software/System restart","BootCount":184}}


    #get_retained([("tasmota/discovery/#", 1)])
    # get_all_retained_OLD([("tasmota/discovery/#", 1)])

    exit(1)
    # send_telegram_msg("<b>i am a message</b>", htmlmode=True)
    # topics: list[str] = []
    #
    # tasmotas: dict = {
    #     "nous4": "183BC5",
    #     "nous5": "07321C",
    #     "nous6": "186F87"
    # }
    #
    # topics.append("tele/tasmota_779336/STATE")  # efhtor

    # for tasmota_name, tasmo_macshort in tasmotas.items():
    #     logger.debug(f"ADDING {tasmota_name} :: tele/tasmota_{tasmo_macshort}/STATE")
    #     topics.append(f"tele/tasmota_{tasmo_macshort}/STATE")
    #     logger.debug(f"ADDING {tasmota_name} :: tele/tasmota_{tasmo_macshort}/POWER_STATE")
    #     topics.append(f"tele/tasmota_{tasmo_macshort}/POWER_STATE")
    #
    # topics.append("esp32/esp32_94b97ed440b0/LWT")
    # topics.append("esp32/esp32_94b97ed440b0/LWT")
    # topics.append("esp32/esp32_2462abe033d0/LWT")
    # topics.append("esp32/esp32_246f28228360/LWT")
    #
    # topics.append("stat/#")
    # topics.append("nodered/drainagepumpen/#")
    # topics.append("esp32/#")

    # for c, i in enumerate(topics):
    #     logger.debug(f"TOPIC #{c+1} :: {i}")
    #
    #
    #
    #
    # mqtc: MqttCommander = MqttCommander(topics=topics)
    # mqtc.start_loop_forever()

    # cmnd/tasmota_183BC5/SetOption57 1


# kubectl --context=ht@heidk8 -n datatron run mqttcomm-$$ -i --image=xomoxcc/mqttcommander:latest --restart=Never --rm --labels="app=mqttpcommander" --overrides='{ "apiVersion": "v1", "spec": {"imagePullSecrets": [{"name": "privateregcred"}] } }' --env="MQTT__HOST=mosquitto.mosquitto.svc" -- python3 mqttcommander.py


#
# rule 1
# SetOption56 0
# SetOption57 0



# Backlog SSID1 heidk8turris; Password1 Jahsh0eioogh6iMe; SetOption53 1
#
# Backlog SSID2 FB7580; Password2 22054714640313721020
#
# Backlog MqttHost mosquittoi.heidk8.elasticc.io; MqttUser tasmota; MqttPassword yi4Yo3eefi3mahTh; TelePeriod 60

