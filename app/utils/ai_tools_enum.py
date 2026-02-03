from enum import Enum
class AiAgentToolsList(Enum):
    # External tool visibkle to platform users
    RESEARCH_TOOL = "PERPLEXITY_DUCKDUCK_GO_RESEARCH_TOOL"

    # Internal tool used by the platform itself
    DUCK_DUCK_GO_SEARCH_TOOL = "DUCK_DUCK_GO_SEARCH_TOOL"