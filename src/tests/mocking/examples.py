import ft3


class Pet(ft3.Object):
    """A pet."""

    id_: ft3.Field[str]
    _alternate_id: ft3.Field[str]

    name: ft3.Field[str]
    type: ft3.Field[str]
    in_: ft3.Field[str]
    is_tail_wagging: ft3.Field[bool] = True
