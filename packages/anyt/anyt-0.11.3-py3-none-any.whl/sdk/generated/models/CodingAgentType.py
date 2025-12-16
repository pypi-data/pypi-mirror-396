from enum import Enum

class CodingAgentType(str, Enum):
    
        CLAUDE_CODE = 'claude_code'
        
        CODEX = 'codex'
        
        GEMINI_CLI = 'gemini_cli'
        