from enum import Enum

class PRStatus(str, Enum):
    
        DRAFT = 'draft'
        
        OPEN = 'open'
        
        MERGED = 'merged'
        
        CLOSED = 'closed'
        