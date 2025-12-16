from enum import Enum


class JobType1FlowStatusModulesItemAgentActionsItemType2Type(str, Enum):
    MESSAGE = "message"

    def __str__(self) -> str:
        return str(self.value)
