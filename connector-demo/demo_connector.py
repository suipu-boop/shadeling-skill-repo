"""connector-demo 积木实现文件（市场拉取型 fixture）。

由 SkillLibrary.install 按 files[].dest 从仓库源下载落盘到
SHADELING_HOME/bricks/连接器演示/runtime/connectors/demo_connector.py。
本文件同时用于测试 IPC 动态加载（_load_connector_module 优先命中安装位置）。
"""

MARKER = "demo-connector-installed"

# 真实 agent_mail 由 AgentMailStore 提供；本 fixture 用同名接口简化验证。
class AgentMailStore:
    """演示用存储：构造时留下落盘标记，验证安装链路已生效。"""

    def __init__(self):
        self.marker = MARKER
        self.messages = []

    def ping(self):
        return {"ok": True, "marker": self.marker}


class AgentMailConnector:
    """演示用网关连接器（注册后经 GatewayRegistry 可见）。"""

    def __init__(self):
        self.marker = MARKER

    def on_start(self):
        return None
