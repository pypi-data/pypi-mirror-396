from dataclasses import dataclass


@dataclass
class IEVIScore:
    """
    Represents the calculated risk index based on the paper's formula.
    """

    damage_potential: int
    reproducibility: int
    exploitability: int
    affected_users: int
    discoverability: int
    total_score: float
    risk_level: str
