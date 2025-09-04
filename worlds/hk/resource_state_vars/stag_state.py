from . import RCStateVariable, cs, rs


class StagStateVariable(RCStateVariable):
    prefix = "$STAGSTATEMODIFIER"

    def parse_term(self) -> None:
        pass

    @classmethod
    def try_match(cls, term: str) -> bool:
        return term.startswith(cls.prefix)

    @property
    def terms(self) -> list[str]:
        return []

    def _modify_state(self, state_blob: rs, item_state: cs) -> tuple[bool, rs]:
        state_blob["NOFLOWER"] = 1
        return True, state_blob

    def can_exclude(self, options) -> bool:
        return False
