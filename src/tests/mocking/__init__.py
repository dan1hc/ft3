__all__ = (
    'examples',
    'ApiDeriv',
    'Derivative',
    'DubDeriv',
    'MixinDeriv',
    'NewDeriv',
    'TripDeriv',
    'AntiTripDeriv',
    )

import ft3

from ft3 . core import lib

from . import examples


class Derivative(ft3.Object):
    """Simple test derivative."""

    secondary_key: ft3.Field[int] = 123
    str_field: ft3.Field[str] = 'abc'
    bool_field: ft3.Field[bool] = True
    int_field: ft3.Field[int] = 2
    forward_ref_alias_field: 'ft3.Field[ft3.core.typ.AnyType]' = 2
    forward_ref_union_field: 'ft3.Field[float | int | tuple[int | float, ...]]' = 2  # noqa
    forward_ref_field: ft3.Field[list['Derivative']] = []
    enumerated_bool_field: ft3.Field[bool] = ft3.Field(
        default=False,
        enum=ft3.core.enm.Boolean,
        )
    from_dict_field: ft3.Field[lib.t.Optional[str]] = {
        'default': 'asc',
        'enum': {'asc', 'desc'},
        'required': False,
        'type': lib.t.Optional[str]
        }
    null_field: ft3.Field[ft3.core.typ.NoneType] = None
    non_nullable_field: ft3.Field[int] = ft3.Field(default=4, type=int)
    required_field: ft3.Field[int]
    date_field: ft3.Field[lib.datetime.date] = (  # noqa: E731
        lambda: lib.datetime.datetime.now(lib.datetime.timezone.utc).date()
        )
    datetime_field: ft3.Field[lib.datetime.datetime] = (  # noqa: E731
        lambda: lib.datetime.datetime.now(lib.datetime.timezone.utc)
        )
    decimal_field: ft3.Field[lib.decimal.Decimal] = lib.decimal.Decimal(1e-3)
    tuple_field: ft3.Field[tuple] = (1, 2)
    generic_tuple_field: ft3.Field[tuple[str, float, bool]] = ('a', 2.5, False)  # noqa


class DubDeriv(Derivative):

    test_again: ft3.Field[bool] = True
    bob: ft3.Field[str] = 'Dan'
    other_field: ft3.Field[lib.t.Optional[str]] = ft3.Field(
        default='Paul',
        enum=['Paul'],
        type_=lib.t.Optional[str]
        )

    def do_stuff(self):
        ...


class MixinDeriv(ft3.Object):

    test_again: ft3.Field[bool] = True
    bob: ft3.Field[str] = 'David'
    other_field: ft3.Field[lib.t.Optional[str]] = ft3.Field(
        default='Albert',
        enum=['Albert'],
        type_=lib.t.Optional[str]
        )

    def do_stuff(self):
        ...


class NewDeriv(ft3.Object):

    anti_field_1: ft3.Field[str] = 'cba'
    anti_field_2: ft3.Field[bool] = False
    generic_tuple_deriv_field: ft3.Field[tuple[MixinDeriv, ...]] = lambda: (  # noqa: E731
        MixinDeriv(bob='Frank'),
        MixinDeriv(bob='Bob'),
        )


class TripDeriv(MixinDeriv, DubDeriv):

    test_another: ft3.Field[bool] = False
    new_deriv: ft3.Field[NewDeriv] = NewDeriv()
    dict_field: ft3.Field[dict] = {'record_id': 'Arnold'}
    generic_dict_field: ft3.Field[dict[str, float]] = {'record_id': 1.23}


class AntiTripDeriv(DubDeriv, MixinDeriv):

    test_another: ft3.Field[bool] = False
    new_deriv: ft3.Field[NewDeriv] = NewDeriv()
    dict_field: ft3.Field[dict] = {'record_id': 'Lauren'}
    generic_dict_field: ft3.Field[dict[str, float]] = {'record_id': 1.23}


class TypedObj(lib.t.TypedDict):

    name: str
    integer: int


BasicNumber = lib.t.TypeVar('BasicNumber', bound=float | int)
ConstrainedNumber = lib.t.TypeVar('int', int, complex)


class ApiDeriv(MixinDeriv, DubDeriv):

    test_another: ft3.Field[bool] = False
    new_deriv: ft3.Field[NewDeriv] = NewDeriv()
    dict_field: ft3.Field[dict] = {'record_id': 'Arnold'}
    generic_dict_field: ft3.Field[dict[str, float]] = {'record_id': 1.23}
    typed_dict_field: ft3.Field[TypedObj] = {'name': 'Dan', 'integer': 42}
    literal_field: ft3.Field[lib.t.Literal[1]] = 1
    bound_typevar_field:ft3.Field[BasicNumber] = 42.42
    constrained_typevar_field:ft3.Field[ConstrainedNumber] = 42
