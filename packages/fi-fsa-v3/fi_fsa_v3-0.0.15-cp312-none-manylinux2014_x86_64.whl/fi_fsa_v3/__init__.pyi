"""
FSA module
"""
from __future__ import annotations
import collections.abc
import typing
__all__: list[str] = ['FSA', 'comm_req_get_t', 'comm_resp_get_t', 'comm_timeout_protect_config_t', 'ctrl_mode_e', 'err_code_t', 'net_recv_mode_e', 'parsed_err_code_item_t', 'parsed_err_code_t', 'pd_param_t', 'pid_param_t', 'pvctte_t', 'ret_e', 'sdk_config_t', 'subs_config_t', 'subs_data_t', 'temp_vbus_t', 'type_subversion_t']
class FSA:
    @staticmethod
    def ParseErrCode(err_code: err_code_t, parsed_err_code: parsed_err_code_t) -> ret_e:
        """
            /**
            * @brief 解析执行器错误码
            * @param err_code 获取到的8个uint32_t错误码
            * @param parsed_err_code 解析后的错误码
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def CloseRelay(self, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 关闭机器人电源板继电器
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def CommTimeoutProtect(self, comm_timeout_protect_config: comm_timeout_protect_config_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 配置通信超时保护功能
            * @param comm_timeout_protect_config 通信超时保护功能配置
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def DisableControl(self, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 失能执行器
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def EnableControl(self, ctrl_mode: ctrl_mode_e, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 执行器控制使能
            * @param control_mode 控制模式
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def EnableSubscribe(self, subs_config: subs_config_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        ...
    def GetCommConfig(self, comm_req_get: comm_req_get_t, comm_resp_get: comm_resp_get_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 获取执行器通信配置参数
            * @param comm_req_get 请求哪些通信配置参数
            * @param comm_resp_get 存放获取的通信配置参数
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def GetErrCode(self, rx_errcode: err_code_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 获取执行器当前错误码
            * @param rx_errcode 存放获取的错误码
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def GetPDParams(self, rx_pd: pd_param_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 获取临时立即生效 (imm) PD 参数
            * @param rx_pd_param 存放获取的 PD 参数
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def GetPIDParams(self, rx_pid: pid_param_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 实时获取位置环速度环PID参数
            * @param rx_pid_param 存放获取的 PID 参数
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def GetPVCTTe(self, rx_PVCTTe: pvctte_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 获取执行器位置、速度、电流、力矩，电磁转矩
            * @param rx_PVCTTe 存放获取的位置、速度、电流、力矩、电磁转矩
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def GetSubsData(self, subs_data: subs_data_t) -> ret_e:
        """
            /**
            * @brief 获取最新的订阅数据
            * @param subs_data 存放获取的订阅数据
            * @return 状态码
            */
        """
    def GetTempVbus(self, rx_temp_vbus: temp_vbus_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 获取执行器mos温度，绕组温度，电压
            * @param rx_temp_vbus 存放获取的mos温度，绕组温度，电压
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def GetTypeSubversion(self, type_subversion: type_subversion_t, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 获取执行器型号和子版本号
            * @param type_subversion 存放获取的型号和子版本号
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def Init(self, ip: str, net_recv_mode: net_recv_mode_e = net_recv_mode_e.YIELD_WAIT, rtcko_path: str = '') -> ret_e:
        ...
    def OpenRelay(self, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 开启机器人电源板继电器
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def Reboot(self, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 重启执行器
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetAbsEncoderZero(self, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 内置绝编置零
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetCurrent(self, c_A: typing.SupportsFloat, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 发送电流目标指令，执行器回复数据帧
            * @param c_A 目标电流
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetCurrentNoAck(self, c_A: typing.SupportsFloat) -> ret_e:
        """
            /**
            * @brief 发送电流目标指令，执行器不回复任何数据帧
            * @param c_A 目标电流
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetPDParams(self, pd_kp: typing.SupportsFloat, pd_kd: typing.SupportsFloat, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 实时设置 PD 参数
            * @param pd_kp PD比例增益
            * @param pd_kd PD微分增益
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetPDPositionVelocity(self, p_rad: typing.SupportsFloat, v_radps: typing.SupportsFloat = 0, t_ff_Nm: typing.SupportsFloat = 0, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 发送位置目标指令、速度目标指令、力矩前馈指令，执行器回复数据帧
            * @param p_rad 目标位置
            * @param v_radps 目标速度
            * @param t_ff_Nm 力矩前馈
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetPDPositionVelocityNoAck(self, p_rad: typing.SupportsFloat, v_radps: typing.SupportsFloat = 0, t_ff_Nm: typing.SupportsFloat = 0) -> ret_e:
        """
            /**
            * @brief 发送位置目标指令、速度目标指令、力矩前馈指令，执行器不回复任何数据帧
            * @param p_rad 目标位置
            * @param v_radps 目标速度
            * @param t_ff_Nm 力矩前馈
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetPIDParams(self, p_kp: typing.SupportsFloat, v_kp: typing.SupportsFloat, v_ki: typing.SupportsFloat, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 实时设置位置环速度环PID参数
            * @param p_kp 位置环比例增益
            * @param v_kp 速度环比例增益
            * @param v_ki 速度环积分增益
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetPosition(self, p_rad: typing.SupportsFloat, v_ff_radps: typing.SupportsFloat = 0, t_ff_Nm: typing.SupportsFloat = 0, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 发送位置目标指令、速度前馈指令、力矩前馈指令，执行器回复数据帧
            * @param p_rad 目标位置
            * @param v_ff_radps 速度前馈
            * @param t_ff_Nm 力矩前馈
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetPositionNoAck(self, p_rad: typing.SupportsFloat, v_ff_radps: typing.SupportsFloat = 0, t_ff_Nm: typing.SupportsFloat = 0) -> ret_e:
        """
            /**
            * @brief 发送位置目标指令、速度前馈指令、力矩前馈指令，执行器不回复任何数据帧
            * @param p_rad 目标位置
            * @param v_ff_radps 速度前馈
            * @param t_ff_Nm 力矩前馈
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetTorque(self, t_Nm: typing.SupportsFloat, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 发送力矩目标指令，执行器回复数据帧
            * @param t_Nm 目标力矩
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetTorqueNoAck(self, t_Nm: typing.SupportsFloat) -> ret_e:
        """
            /**
            * @brief 发送力矩目标指令，执行器不回复任何数据帧
            * @param t_Nm 目标力矩
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetVelocity(self, v_radps: typing.SupportsFloat, t_ff_Nm: typing.SupportsFloat = 0, timeout_ms: typing.SupportsFloat = 5, max_retry: typing.SupportsInt = 1) -> ret_e:
        """
            /**
            * @brief 发送速度目标指令、力矩前馈指令，执行器回复数据帧
            * @param v_radps 目标速度
            * @param t_ff_Nm 力矩前馈
            * @param timeout_ms 超时时间
            * @param max_retry 最大重试次数
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def SetVelocityNoAck(self, v_radps: typing.SupportsFloat, t_ff_Nm: typing.SupportsFloat = 0) -> ret_e:
        """
            /**
            * @brief 发送速度目标指令、力矩前馈指令，执行器不回复任何数据帧
            * @param v_radps 目标速度
            * @param t_ff_Nm 力矩前馈
            * @return 返回详细执行状态ret_e(int)
            */
        """
    def __init__(self) -> None:
        ...
class comm_req_get_t:
    def __init__(self) -> None:
        ...
    @property
    def DHCP_enable(self) -> bool:
        """
            是否获取 DHCP 启用状态
        """
    @DHCP_enable.setter
    def DHCP_enable(self, arg0: bool) -> None:
        ...
    @property
    def PCBA_sn(self) -> bool:
        """
            是否获取 PCBA SN
        """
    @PCBA_sn.setter
    def PCBA_sn(self, arg0: bool) -> None:
        ...
    @property
    def dns_1(self) -> bool:
        """
            是否获取 DNS 1
        """
    @dns_1.setter
    def dns_1(self, arg0: bool) -> None:
        ...
    @property
    def dns_2(self) -> bool:
        """
            是否获取 DNS 2
        """
    @dns_2.setter
    def dns_2(self, arg0: bool) -> None:
        ...
    @property
    def gateway(self) -> bool:
        """
            是否获取网关
        """
    @gateway.setter
    def gateway(self, arg0: bool) -> None:
        ...
    @property
    def gearbox_sn(self) -> bool:
        """
            是否获取齿轮箱 SN
        """
    @gearbox_sn.setter
    def gearbox_sn(self, arg0: bool) -> None:
        ...
    @property
    def mac_address(self) -> bool:
        """
            是否获取 MAC 地址
        """
    @mac_address.setter
    def mac_address(self, arg0: bool) -> None:
        ...
    @property
    def mcu_fw_version(self) -> bool:
        """
            是否获取 MCU 固件版本
        """
    @mcu_fw_version.setter
    def mcu_fw_version(self, arg0: bool) -> None:
        ...
    @property
    def name(self) -> bool:
        """
            是否获取名称
        """
    @name.setter
    def name(self, arg0: bool) -> None:
        ...
    @property
    def sn(self) -> bool:
        """
            是否获取 SN
        """
    @sn.setter
    def sn(self, arg0: bool) -> None:
        ...
    @property
    def static_IP(self) -> bool:
        """
            是否获取静态 IP
        """
    @static_IP.setter
    def static_IP(self, arg0: bool) -> None:
        ...
    @property
    def subnet_mask(self) -> bool:
        """
            是否获取子网掩码
        """
    @subnet_mask.setter
    def subnet_mask(self, arg0: bool) -> None:
        ...
    @property
    def type(self) -> bool:
        """
            是否获取类型
        """
    @type.setter
    def type(self, arg0: bool) -> None:
        ...
    @property
    def uid(self) -> bool:
        """
            是否获取 UID
        """
    @uid.setter
    def uid(self, arg0: bool) -> None:
        ...
class comm_resp_get_t:
    DHCP_enable_valid: bool
    PCBA_sn_valid: bool
    dns_1_valid: bool
    dns_2_valid: bool
    gateway_valid: bool
    gearbox_sn_valid: bool
    mac_address_valid: bool
    mcu_fw_version_valid: bool
    name_valid: bool
    sn_valid: bool
    static_IP_valid: bool
    subnet_mask_valid: bool
    type_valid: bool
    uid_valid: bool
    def __init__(self) -> None:
        ...
    @property
    def DHCP_enable(self) -> bool:
        """
            DHCP 启用状态
        """
    @DHCP_enable.setter
    def DHCP_enable(self, arg0: bool) -> None:
        ...
    @property
    def PCBA_sn(self) -> str:
        """
            PCBA SN
        """
    @PCBA_sn.setter
    def PCBA_sn(self, arg0: str) -> None:
        ...
    @property
    def dns_1(self) -> str:
        """
            DNS 1
        """
    @dns_1.setter
    def dns_1(self, arg0: str) -> None:
        ...
    @property
    def dns_2(self) -> str:
        """
            DNS 2
        """
    @dns_2.setter
    def dns_2(self, arg0: str) -> None:
        ...
    @property
    def gateway(self) -> str:
        """
            网关
        """
    @gateway.setter
    def gateway(self, arg0: str) -> None:
        ...
    @property
    def gearbox_sn(self) -> str:
        """
            减速机 SN
        """
    @gearbox_sn.setter
    def gearbox_sn(self, arg0: str) -> None:
        ...
    @property
    def mac_address(self) -> str:
        """
            MAC 地址
        """
    @mac_address.setter
    def mac_address(self, arg0: str) -> None:
        ...
    @property
    def mcu_fw_version(self) -> str:
        """
            MCU 固件版本
        """
    @mcu_fw_version.setter
    def mcu_fw_version(self, arg0: str) -> None:
        ...
    @property
    def name(self) -> str:
        """
            名称
        """
    @name.setter
    def name(self, arg0: str) -> None:
        ...
    @property
    def sn(self) -> str:
        """
            SN
        """
    @sn.setter
    def sn(self, arg0: str) -> None:
        ...
    @property
    def static_IP(self) -> str:
        """
            静态 IP
        """
    @static_IP.setter
    def static_IP(self, arg0: str) -> None:
        ...
    @property
    def subnet_mask(self) -> str:
        """
            子网掩码
        """
    @subnet_mask.setter
    def subnet_mask(self, arg0: str) -> None:
        ...
    @property
    def type(self) -> str:
        """
            类型
        """
    @type.setter
    def type(self, arg0: str) -> None:
        ...
    @property
    def uid(self) -> str:
        """
            UID
        """
    @uid.setter
    def uid(self, arg0: str) -> None:
        ...
class comm_timeout_protect_config_t:
    def __init__(self) -> None:
        ...
    @property
    def config_protect_pos_kp(self) -> bool:
        """
            是否修改进入保护状态时的pos_kp参数
        """
    @config_protect_pos_kp.setter
    def config_protect_pos_kp(self, arg0: bool) -> None:
        ...
    @property
    def config_protect_vel_ki(self) -> bool:
        """
            是否修改进入保护状态时的vel_ki参数
        """
    @config_protect_vel_ki.setter
    def config_protect_vel_ki(self, arg0: bool) -> None:
        ...
    @property
    def config_protect_vel_kp(self) -> bool:
        """
            是否修改进入保护状态时的vel_kp参数
        """
    @config_protect_vel_kp.setter
    def config_protect_vel_kp(self, arg0: bool) -> None:
        ...
    @property
    def config_timeout_ms(self) -> bool:
        """
            是否修改timeout_ms
        """
    @config_timeout_ms.setter
    def config_timeout_ms(self, arg0: bool) -> None:
        ...
    @property
    def get_protect_pid(self) -> pid_param_t:
        """
            获取保护状态pid参数
        """
    @get_protect_pid.setter
    def get_protect_pid(self, arg0: pid_param_t) -> None:
        ...
    @property
    def get_timeout_ms(self) -> int:
        """
            获取超时时间
        """
    @get_timeout_ms.setter
    def get_timeout_ms(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def set_protect_pid(self) -> pid_param_t:
        """
            如果config_protect_xxx为true，则需要用户配置对应参数，false则对应参数不会下发给执行器
        """
    @set_protect_pid.setter
    def set_protect_pid(self, arg0: pid_param_t) -> None:
        ...
    @property
    def set_timeout_ms(self) -> int:
        """
            超时时间，单位毫秒，0代表关闭此功能
        """
    @set_timeout_ms.setter
    def set_timeout_ms(self, arg0: typing.SupportsInt) -> None:
        ...
class ctrl_mode_e:
    """
    Members:
    
      NONE : 
        无控制模式
    
      CURRENT_MODE : 
        电流控制模式，建议使用转矩控制模式
    
      TORQUE_MODE : 
        转矩控制模式
    
      VELOCITY_MODE : 
        转矩速度控制模式
    
      POSITION_MODE : 
        转矩位置控制模式
    
      PD_MODE : 
        转矩PD控制模式
    """
    CURRENT_MODE: typing.ClassVar[ctrl_mode_e]  # value = <ctrl_mode_e.CURRENT_MODE: 1>
    NONE: typing.ClassVar[ctrl_mode_e]  # value = <ctrl_mode_e.NONE: 0>
    PD_MODE: typing.ClassVar[ctrl_mode_e]  # value = <ctrl_mode_e.PD_MODE: 7>
    POSITION_MODE: typing.ClassVar[ctrl_mode_e]  # value = <ctrl_mode_e.POSITION_MODE: 6>
    TORQUE_MODE: typing.ClassVar[ctrl_mode_e]  # value = <ctrl_mode_e.TORQUE_MODE: 4>
    VELOCITY_MODE: typing.ClassVar[ctrl_mode_e]  # value = <ctrl_mode_e.VELOCITY_MODE: 5>
    __members__: typing.ClassVar[dict[str, ctrl_mode_e]]  # value = {'NONE': <ctrl_mode_e.NONE: 0>, 'CURRENT_MODE': <ctrl_mode_e.CURRENT_MODE: 1>, 'TORQUE_MODE': <ctrl_mode_e.TORQUE_MODE: 4>, 'VELOCITY_MODE': <ctrl_mode_e.VELOCITY_MODE: 5>, 'POSITION_MODE': <ctrl_mode_e.POSITION_MODE: 6>, 'PD_MODE': <ctrl_mode_e.PD_MODE: 7>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class err_code_t:
    def __init__(self) -> None:
        ...
    @property
    def arr(self) -> typing.Annotated[list[int], "FixedSize(8)"]:
        ...
    @arr.setter
    def arr(self, arg0: typing.Annotated[collections.abc.Sequence[typing.SupportsInt], "FixedSize(8)"]) -> None:
        ...
class net_recv_mode_e:
    """
    Members:
    
      NONE
    
      YIELD_WAIT : 
        /**
        * @brief 等待时让出 CPU
        * @warning 实际超时返回时间可能会大于指定超时时间(取决于系统调度和负载)
        */
    
      SPIN_WAIT : 
        /**
        * @brief 等待时 while 自旋, 不让出 CPU
        * @warning 可能会造成 CPU 满载
        */
    """
    NONE: typing.ClassVar[net_recv_mode_e]  # value = <net_recv_mode_e.NONE: 0>
    SPIN_WAIT: typing.ClassVar[net_recv_mode_e]  # value = <net_recv_mode_e.SPIN_WAIT: 2>
    YIELD_WAIT: typing.ClassVar[net_recv_mode_e]  # value = <net_recv_mode_e.YIELD_WAIT: 1>
    __members__: typing.ClassVar[dict[str, net_recv_mode_e]]  # value = {'NONE': <net_recv_mode_e.NONE: 0>, 'YIELD_WAIT': <net_recv_mode_e.YIELD_WAIT: 1>, 'SPIN_WAIT': <net_recv_mode_e.SPIN_WAIT: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class parsed_err_code_item_t:
    @property
    def err_bit_index(self) -> int:
        """
            从0到31
        """
    @err_bit_index.setter
    def err_bit_index(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def err_level(self) -> int:
        """
            3:错误，2:警告且限制部分功能，1:警告，-1:信息，-2:信息
        """
    @err_level.setter
    def err_level(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def err_u32_index(self) -> int:
        """
            从0到7
        """
    @err_u32_index.setter
    def err_u32_index(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def parsed_code(self) -> int:
        """
            将定长bit位错误码转换为具体错误码，方便用户查阅
        """
    @parsed_code.setter
    def parsed_code(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def str_for_log(self) -> str:
        """
            方便打印日志的字符串
        """
class parsed_err_code_t:
    def __init__(self) -> None:
        ...
    @property
    def vec(self) -> list[parsed_err_code_item_t]:
        ...
    @vec.setter
    def vec(self, arg0: collections.abc.Sequence[parsed_err_code_item_t]) -> None:
        ...
class pd_param_t:
    def __init__(self) -> None:
        ...
    @property
    def pd_kd(self) -> float:
        ...
    @pd_kd.setter
    def pd_kd(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def pd_kp(self) -> float:
        ...
    @pd_kp.setter
    def pd_kp(self, arg0: typing.SupportsFloat) -> None:
        ...
class pid_param_t:
    def __init__(self) -> None:
        ...
    @property
    def pos_kp(self) -> float:
        ...
    @pos_kp.setter
    def pos_kp(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def vel_ki(self) -> float:
        ...
    @vel_ki.setter
    def vel_ki(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def vel_kp(self) -> float:
        ...
    @vel_kp.setter
    def vel_kp(self, arg0: typing.SupportsFloat) -> None:
        ...
class pvctte_t:
    def __init__(self) -> None:
        ...
    @property
    def cur(self) -> float:
        ...
    @cur.setter
    def cur(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def pos(self) -> float:
        ...
    @pos.setter
    def pos(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def tor(self) -> float:
        ...
    @tor.setter
    def tor(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def tor_e(self) -> float:
        ...
    @tor_e.setter
    def tor_e(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def vel(self) -> float:
        ...
    @vel.setter
    def vel(self, arg0: typing.SupportsFloat) -> None:
        ...
class ret_e:
    """
    Members:
    
      SUCCESS : 
        操作成功
    
      SDK_VER_NOT_MATCH : 
        /**
        * @brief SDK 版本不匹配
        * @note 执行器固件版本过低或 SDK 动态库与头文件版本不匹配
        */
    
      CTRL_PARAM_ERR : 
        /**
        * @brief 执行器获取配置参数错误
        * @note 型号和版本号未获取成功
        */
    
      INTERFACE_HANDLE_ERR : 
        /**
        * @brief 执行器对象未初始化
        * @note 可能未执行 init 函数
        */
    
      ARG_ERR : 
        /**
        * @brief 接口参数非法
        * @note 传入接口的参数不符合要求
        */
    
      NET_ERR : 
        /**
        * @brief 网络错误
        * @note 可能对应 IP 的 FSA 网络已断开
        */
    
      TIMEOUT : 
        /**
        * @brief 网络接收超时
        * @note 接收执行器返回数据等待时间超过指定超时时间
        */
    
      NET_RXBUF_DATA_ERR : 
        /**
        * @brief 网络接收缓冲区数据与发送指令不匹配
        * @note 可能接收到系统 socket 输入缓冲区前几帧数据导致指令不匹配
        */
    """
    ARG_ERR: typing.ClassVar[ret_e]  # value = <ret_e.ARG_ERR: -202>
    CTRL_PARAM_ERR: typing.ClassVar[ret_e]  # value = <ret_e.CTRL_PARAM_ERR: -102>
    INTERFACE_HANDLE_ERR: typing.ClassVar[ret_e]  # value = <ret_e.INTERFACE_HANDLE_ERR: -201>
    NET_ERR: typing.ClassVar[ret_e]  # value = <ret_e.NET_ERR: -301>
    NET_RXBUF_DATA_ERR: typing.ClassVar[ret_e]  # value = <ret_e.NET_RXBUF_DATA_ERR: -303>
    SDK_VER_NOT_MATCH: typing.ClassVar[ret_e]  # value = <ret_e.SDK_VER_NOT_MATCH: -101>
    SUCCESS: typing.ClassVar[ret_e]  # value = <ret_e.SUCCESS: 0>
    TIMEOUT: typing.ClassVar[ret_e]  # value = <ret_e.TIMEOUT: -302>
    __members__: typing.ClassVar[dict[str, ret_e]]  # value = {'SUCCESS': <ret_e.SUCCESS: 0>, 'SDK_VER_NOT_MATCH': <ret_e.SDK_VER_NOT_MATCH: -101>, 'CTRL_PARAM_ERR': <ret_e.CTRL_PARAM_ERR: -102>, 'INTERFACE_HANDLE_ERR': <ret_e.INTERFACE_HANDLE_ERR: -201>, 'ARG_ERR': <ret_e.ARG_ERR: -202>, 'NET_ERR': <ret_e.NET_ERR: -301>, 'TIMEOUT': <ret_e.TIMEOUT: -302>, 'NET_RXBUF_DATA_ERR': <ret_e.NET_RXBUF_DATA_ERR: -303>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class sdk_config_t:
    @property
    def DEFAULT_MAX_RETRY(self) -> int:
        """
            用户默认最大重试次数
        """
    @DEFAULT_MAX_RETRY.setter
    def DEFAULT_MAX_RETRY(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def DEFAULT_TIMEOUT_MS(self) -> int:
        """
            用户默认超时时间, 单位毫秒
        """
    @DEFAULT_TIMEOUT_MS.setter
    def DEFAULT_TIMEOUT_MS(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def MIN_M4_VER(self) -> int:
        """
            最低 M4核 固件版本
        """
    @property
    def MIN_M7_VER(self) -> int:
        """
            最低 M7核 固件版本
        """
    @property
    def SDK_HEADER_VERSION(self) -> int:
        """
            SDK 头文件版本
        """
class subs_config_t:
    def __init__(self) -> None:
        ...
    @property
    def cur(self) -> int:
        """
            电流订阅使能，0:禁用，1:启用
        """
    @cur.setter
    def cur(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def enable(self) -> int:
        """
            订阅使能，0:禁用，1:启用
        """
    @enable.setter
    def enable(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error(self) -> int:
        """
            错误码订阅使能，0:禁用，1:启用
        """
    @error.setter
    def error(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext2(self) -> int:
        """
            错误码扩展2订阅使能，0:禁用，1:启用
        """
    @error_ext2.setter
    def error_ext2(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext3(self) -> int:
        """
            错误码扩展3订阅使能，0:禁用，1:启用
        """
    @error_ext3.setter
    def error_ext3(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext4(self) -> int:
        """
            错误码扩展4订阅使能，0:禁用，1:启用
        """
    @error_ext4.setter
    def error_ext4(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext5(self) -> int:
        """
            错误码扩展5订阅使能，0:禁用，1:启用
        """
    @error_ext5.setter
    def error_ext5(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext6(self) -> int:
        """
            错误码扩展6订阅使能，0:禁用，1:启用
        """
    @error_ext6.setter
    def error_ext6(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext7(self) -> int:
        """
            错误码扩展7订阅使能，0:禁用，1:启用
        """
    @error_ext7.setter
    def error_ext7(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error_ext8(self) -> int:
        """
            错误码扩展8订阅使能，0:禁用，1:启用
        """
    @error_ext8.setter
    def error_ext8(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def freq(self) -> int:
        """
            订阅回传频率，单位Hz
        """
    @freq.setter
    def freq(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def keepalive_time_ms(self) -> int:
        """
            保持时间时间，单位ms
        """
    @keepalive_time_ms.setter
    def keepalive_time_ms(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def pos(self) -> int:
        """
            位置订阅使能，0:禁用，1:启用
        """
    @pos.setter
    def pos(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def temp_coil(self) -> int:
        """
            线圈温度订阅使能，0:禁用，1:启用
        """
    @temp_coil.setter
    def temp_coil(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def temp_mos(self) -> int:
        """
            MOS温度订阅使能，0:禁用，1:启用
        """
    @temp_mos.setter
    def temp_mos(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def tor(self) -> int:
        """
            转矩订阅使能，0:禁用，1:启用
        """
    @tor.setter
    def tor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def tor_em(self) -> int:
        """
            电磁转矩订阅使能，0:禁用，1:启用
        """
    @tor_em.setter
    def tor_em(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def vbus(self) -> int:
        """
            VBUS电压订阅使能，0:禁用，1:启用
        """
    @vbus.setter
    def vbus(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def vel(self) -> int:
        """
            速度订阅使能，0:禁用，1:启用
        """
    @vel.setter
    def vel(self, arg0: typing.SupportsInt) -> None:
        ...
class subs_data_t:
    pvct: pvctte_t
    temp_vbus: temp_vbus_t
    def __init__(self) -> None:
        ...
    @property
    def cnt(self) -> int:
        ...
    @cnt.setter
    def cnt(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def error(self) -> typing.Annotated[list[int], "FixedSize(8)"]:
        ...
    @error.setter
    def error(self, arg0: typing.Annotated[collections.abc.Sequence[typing.SupportsInt], "FixedSize(8)"]) -> None:
        ...
    @property
    def latency_from_recv_ns(self) -> int:
        ...
    @latency_from_recv_ns.setter
    def latency_from_recv_ns(self, arg0: typing.SupportsInt) -> None:
        ...
class temp_vbus_t:
    def __init__(self) -> None:
        ...
    @property
    def coil(self) -> float:
        ...
    @coil.setter
    def coil(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def mos(self) -> float:
        ...
    @mos.setter
    def mos(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def vbus(self) -> float:
        ...
    @vbus.setter
    def vbus(self, arg0: typing.SupportsFloat) -> None:
        ...
class type_subversion_t:
    def __init__(self) -> None:
        ...
    @property
    def sub_version(self) -> typing.Annotated[list[str], "FixedSize(33)"]:
        """
            执行器子版本字符串, 前32字节有效, 最后1字节固定为'\\0'
        """
    @sub_version.setter
    def sub_version(self, arg0: typing.Annotated[collections.abc.Sequence[str], "FixedSize(33)"]) -> None:
        ...
    @property
    def type(self) -> typing.Annotated[list[str], "FixedSize(33)"]:
        """
            执行器型号字符串, 前32字节有效, 最后1字节固定为'\\0'
        """
    @type.setter
    def type(self, arg0: typing.Annotated[collections.abc.Sequence[str], "FixedSize(33)"]) -> None:
        ...
