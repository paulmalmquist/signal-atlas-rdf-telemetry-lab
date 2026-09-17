"""Work-side extension contract, NOT an implemented connection to any company system.

Do not add credentials, real URLs or company fixtures to this personal repository.
Implement this protocol inside the approved work environment after owner review.
The existing local fixture mapper is backend.build; it intentionally does not auto-
discover or invoke external adapters.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping, Protocol, Literal

@dataclass(frozen=True)
class SourceSnapshot:
    source_system: str
    source_record_id: str
    source_revision: str
    event_time: datetime
    retrieved_at: datetime
    authority_owner: str
    mapping_version: str
    classification: str
    approved_fields: Mapping[str, object]

@dataclass(frozen=True)
class IdentityDecision:
    source_system: str
    source_id: str
    canonical_iri: str | None
    status: Literal['approved', 'ambiguous', 'unmapped']
    reviewer: str | None
    evidence_reference: str | None

class ApprovedWorkAdapter(Protocol):
    """Idempotent snapshot reads. No source writes and no silent fallback to mock data."""
    def read_snapshot(self, *, as_of: datetime) -> Iterable[SourceSnapshot]: ...
    def resolve_identity(self, record: SourceSnapshot) -> IdentityDecision: ...
    def health(self) -> Mapping[str, object]: ...
