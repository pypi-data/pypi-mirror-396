from enum import Enum


class FlowStatusModulesItemAgentActionsItemType2Type(str, Enum):
    MESSAGE = "message"

    def __str__(self) -> str:
        return str(self.value)
