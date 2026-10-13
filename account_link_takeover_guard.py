"""Isolated one-to-one ownership enforcement for verified classroom links.

NOT wired into production; an in-memory example of atomic uniqueness rules.
Real deployment requires durable transactional constraints and recovery controls.
"""
from dataclasses import dataclass


class LinkConflict(ValueError):
    pass


@dataclass(frozen=True)
class Link:
    classroom_id: str
    supabase_id: str


class TestLinkRegistry:
    """Test-only stand-in for UNIQUE(classroom_id) and UNIQUE(supabase_id)."""
    def __init__(self):
        self._classrooms = {}
        self._accounts = {}

    def bind_verified(self, link: Link) -> Link:
        # Both IDs must already be established by independent server verifiers.
        # The registry must never be called directly with browser-controlled IDs.
        if not link.classroom_id.startswith("WEB-") or not link.supabase_id:
            raise ValueError("Verified identities required")
        old_user = self._classrooms.get(link.classroom_id)
        old_classroom = self._accounts.get(link.supabase_id)
        if old_user is not None and old_user != link.supabase_id:
            raise LinkConflict("Classroom already belongs to another account")
        if old_classroom is not None and old_classroom != link.classroom_id:
            raise LinkConflict("Account already belongs to another classroom identity")
        self._classrooms[link.classroom_id] = link.supabase_id
        self._accounts[link.supabase_id] = link.classroom_id
        return link
