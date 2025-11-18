from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Listing:
    title: str
    price: float
    url: str

    #optional fields
    source: str = "Unknown"
    image_urls: List[str] = field(default_factory=list)
    current_bid: Optional[float] = None
    shipping_cost: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


