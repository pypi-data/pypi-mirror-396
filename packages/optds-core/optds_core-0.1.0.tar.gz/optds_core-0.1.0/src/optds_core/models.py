import hashlib
import json
from decimal import Decimal
from enum import Enum
from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, computed_field

class OptionType(str, Enum):
    CALL = "C"
    PUT = "P"

class ExerciseStyle(str, Enum):
    AMERICAN = "A"
    EUROPEAN = "E"
    UNKNOWN = "U"

class OptionContract(BaseModel):
    """
    Immutable instrument definition.
    frozen=True ensures IDs never drift after instantiation.
    """
    model_config = ConfigDict(frozen=True)

    underlying_id: str    # Canonical ID (e.g. "OM:102030")
    root_symbol: str      # Human readable (e.g. "SPX")
    expiration: date
    strike: Decimal       # Precision critical
    option_type: OptionType
    style: ExerciseStyle = ExerciseStyle.UNKNOWN
    multiplier: int = 100

    @computed_field
    def contract_id(self) -> str:
        """
        Stable hash generation (Blake2b-16).
        Normalizes strike to 6 decimals to ensure 150 == 150.000000.
        """
        payload = {
            "uid": self.underlying_id,
            "exp": self.expiration.isoformat(),
            "opt": self.option_type.value,
            "strk": f"{self.strike:.6f}",
            "styl": self.style.value,
            "mult": self.multiplier,
        }
        # sort_keys=True is vital for deterministic hashing and JSON stability
        raw_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.blake2b(raw_str.encode(), digest_size=16).hexdigest()

class OptionQuote(BaseModel):
    """Raw Market Data / Observables."""
    contract_id: str
    date: date
    # Using Decimal for prices is safer for crypto, though float is common for speed. We stick with Decimal for precision.
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    last: Optional[Decimal] = None
    volume: Optional[int] = None
    open_interest: Optional[int] = None

class DerivedMetrics(BaseModel):
    """Calculated Data (IV, Greeks)."""
    contract_id: str
    date: date
    iv: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    
    iv_method: Optional[Literal["vendor", "bs_newton", "bachelier"]] = None
    iv_source: Optional[str] = None

    