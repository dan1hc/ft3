"""Objects module."""

__all__ = (
    'Component',
    'Content',
    'Operation',
    'Parameter',
    'Path',
    'RequestBody',
    'ResponseObject',
    'Responses',
    'Schema',
    )

from .. import core
from .. import Field, Object

from . import cfg
from . import enm
from . import lib
from . import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""


class Component(Object):
    """
    [OpenAPI](https://swagger.io/docs/specification/components/) Component.

    """

    _title_: Field[str]


class Schema(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#schema-object) Schema Object.

    """

    type_: Field[list[typ.ApiType]] = Field(
        default=[enm.Type.string.name],
        enum=enm.Type
        )
    format_: Field[lib.t.Optional[typ.ApiFormat]] = Field(
        default=None,
        enum=enm.Format
        )

    default: Field[lib.t.Optional[typ.ApiTypeValue]] = None
    required: Field[lib.t.Optional[bool]] = None
    enum: Field[lib.t.Optional[typ.Enum]] = None

    min_length: Field[lib.t.Optional[int]] = None
    max_length: Field[lib.t.Optional[int]] = None
    pattern: Field[lib.t.Optional[str]] = None

    minimum: Field[lib.t.Optional[float]] = None
    exclusive_minimum: Field[lib.t.Optional[bool]] = None
    maximum: Field[lib.t.Optional[float]] = None
    exclusive_maximum: Field[lib.t.Optional[bool]] = None
    multiple_of: Field[lib.t.Optional[float]] = None

    min_items: Field[lib.t.Optional[int]] = None
    max_items: Field[lib.t.Optional[int]] = None
    unique_items: Field[lib.t.Optional[bool]] = None

    read_only: Field[lib.t.Optional[bool]] = None
    write_only: Field[lib.t.Optional[bool]] = None

    items_: Field[lib.t.Optional['Schema']] = None
    properties: Field[
        lib.t.Optional[dict[typ.string[typ.camelCase], 'Schema']]
        ] = None

    all_of: Field[lib.t.Optional[list['Schema']]] = None
    any_of: Field[lib.t.Optional[list['Schema']]] = None
    one_of: Field[lib.t.Optional[list['Schema']]] = None

    def __post_init__(self) -> None:
        self.type_.append(enm.Type.null.name)
        return super().__post_init__()

    @classmethod
    def from_obj(
        cls,
        obj: type[Object],
        /,
        **kwargs: lib.t.Any
        ) -> 'Schema':
        """Parse Schema definition from `Object`."""

        title_: typ.string[lib.t.Any] = kwargs.pop('name', obj.__name__)
        kwargs['title'] = title_

        properties = {
            (
                name_ := (
                    core
                    .strings
                    .utl
                    .snake_case_to_camel_case(field_name.strip('_'))
                    )
                ): (
                    cls.from_type(
                        name=title_ + name_[0].upper() + name_[1:],
                        **{
                            k: v
                            for k, v
                            in field.items()
                            if k != 'name'
                            }
                        )
                    )
            for field_name, field
            in obj.__dataclass_fields__.items()
            }

        return cls(
            properties=properties,
            type_=[enm.Type.object.name],
            **kwargs
            )

    @classmethod
    def from_type(
        cls,
        /,
        *,
        type_: lib.t.Any = None,
        **kwargs: lib.t.Any
        ) -> 'Schema':
        """Parse Schema definition from python `type`."""

        typ_ = kwargs.pop('type', type_)
        title_: typ.string[lib.t.Any] = kwargs.pop(
            'name',
            getattr(typ_, '__name__', typ_.__class__.__name__)
            )
        kwargs['title'] = core.strings.utl.snake_case_to_camel_case(
            title_.strip('_')
            )

        if (
            typ.utl.check.is_union(typ_)
            or typ.utl.check.is_wrapper_type(typ_)
            ):
            schemae = [
                cls.from_type(type_=tp)
                for tp
                in typ.utl.check.get_type_args(typ_)
                ]
            return cls(any_of=schemae, **kwargs)
        elif typ.utl.check.is_typevar(typ_):
            if typ_.__constraints__:
                schemae = [
                    cls.from_type(type_=tp)
                    for tp
                    in typ_.__constraints__
                    ]
                return cls(one_of=schemae, **kwargs)
            elif typ_.__bound__:
                return cls(
                    all_of=[cls.from_type(type_=typ_.__bound__)],
                    **kwargs
                    )
            else:
                return cls(**kwargs)
        elif typ.utl.check.is_literal(typ_):
            literal_tp = typ.utl.check.get_type_args(typ_)[0]
            return cls.from_type(type_=literal_tp, **kwargs)
        elif typ.utl.check.is_object_type(typ_):
            return cls.from_obj(typ_, **kwargs)
        elif typ.utl.check.is_typed(typ_):
            return cls(
                properties={
                    core.strings.utl.snake_case_to_camel_case(annotation): (
                        cls.from_type(type_=tp)
                        )
                    for annotation, tp
                    in typ_.__annotations__.items()
                    },
                type_=[enm.Type.object.name],
                **kwargs
                )
        elif typ.utl.check.is_array_type(typ_):
            if (tps := typ.utl.check.get_args(typ_)):
                tp = tps[0]
            else:
                tp = str
            return cls(
                type_=[enm.Type.array.name],
                items_=cls.from_type(type_=tp),
                **kwargs
                )
        elif typ.utl.check.is_mapping_type(typ_):
            return cls(type_=[enm.Type.object.name], **kwargs)
        elif typ.utl.check.is_bool_type(typ_):
            return cls(
                type_=[enm.Type.boolean.name],
                format_=enm.Format.boolean.name,
                **kwargs
                )
        elif typ.utl.check.is_none_type(typ_):
            return cls(type_=[], **kwargs)
        elif typ.utl.check.is_number_type(typ_):
            otp = lib.t.get_origin(typ_) or typ_
            if issubclass(otp, lib.decimal.Decimal):
                return cls(
                    type_=[enm.Type.number.name],
                    format_=enm.Format.double.name,
                    **kwargs
                    )
            elif issubclass(otp, int):
                return cls(
                    type_=[enm.Type.integer.name],
                    format_=enm.Format.int32.name,
                    **kwargs
                    )
            elif issubclass(otp, float):
                return cls(
                    type_=[enm.Type.number.name],
                    format_=enm.Format.float.name,
                    **kwargs
                    )
            else:  # pragma: no cover
                return cls(type_=[enm.Type.number.name], **kwargs)
        elif typ.utl.check.is_datetime_type(typ_):
            return cls(
                type_=[enm.Type.string.name],
                format_=enm.Format.datetime.name,
                **kwargs
                )
        elif typ.utl.check.is_date_type(typ_):
            return cls(
                type_=[enm.Type.string.name],
                format_=enm.Format.date.name,
                **kwargs
                )
        else:
            return cls(**kwargs)


class Parameter(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-object) Parameter Object.

    """

    name: Field[str]

    in_: Field[str] = Field(
        default=enm.ParameterLocation.query.name,
        enum=enm.ParameterLocation
        )

    description: Field[lib.t.Optional[str]] = None

    required: Field[bool] = False
    deprecated: Field[lib.t.Optional[bool]] = None

    schema: Field[lib.t.Optional[Schema]] = None


class Content(Component):
    """
    Sub component for common content types.

    ---

    Pass content type as title.

    Example: `Content(_title_='application/json')`

    """

    schema: Field[lib.t.Optional[Schema]] = None


class RequestBody(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#request-body-object) Request Body Object.

    """

    name: Field[str]
    content: Field[Content] = Content(_title_=enm.ContentType.json.value)


class ResponseObject(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#response-object) Request Body Object.

    ---

    Pass HTTP Status Code as title (as a `str`).

    Example: `ResponseObject(_title_='200', description='Success.')`

    """

    description: Field[str]

    headers: Field[lib.t.Optional[list[Parameter]]] = None
    content: Field[Content] = Content(_title_=enm.ContentType.json.value)


class Responses(Component):
    """Possible Responses."""

    _200_: Field[lib.t.Optional[ResponseObject]] = None
    _201_: Field[lib.t.Optional[ResponseObject]] = None
    _204_: Field[lib.t.Optional[ResponseObject]] = None
    _301_: Field[lib.t.Optional[ResponseObject]] = None
    _400_: Field[lib.t.Optional[ResponseObject]] = None
    _401_: Field[lib.t.Optional[ResponseObject]] = None
    _403_: Field[lib.t.Optional[ResponseObject]] = None
    _404_: Field[lib.t.Optional[ResponseObject]] = None
    _405_: Field[lib.t.Optional[ResponseObject]] = None
    _409_: Field[lib.t.Optional[ResponseObject]] = None
    _423_: Field[lib.t.Optional[ResponseObject]] = None
    _429_: Field[lib.t.Optional[ResponseObject]] = None
    _500_: Field[lib.t.Optional[ResponseObject]] = None
    _502_: Field[lib.t.Optional[ResponseObject]] = None
    _504_: Field[lib.t.Optional[ResponseObject]] = None


class Operation(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#operation-object) Operation Object.

    """

    description: Field[lib.t.Optional[str]] = None
    summary: Field[lib.t.Optional[str]] = None

    tags: Field[lib.t.Optional[list[str]]] = None

    parameters: Field[lib.t.Optional[list[Parameter]]] = None
    request_body: Field[lib.t.Optional[RequestBody]] = None

    responses: Field[lib.t.Optional[Responses]] = None


class Path(Component):
    """
    [OpenAPI](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#path-item-object) Path Item Object.

    """

    description: Field[lib.t.Optional[str]] = None
    summary: Field[lib.t.Optional[str]] = None

    delete: Field[lib.t.Optional[Operation]] = None
    get_: Field[lib.t.Optional[Operation]] = None
    options: Field[lib.t.Optional[Operation]] = None
    patch: Field[lib.t.Optional[Operation]] = None
    post: Field[lib.t.Optional[Operation]] = None
    put: Field[lib.t.Optional[Operation]] = None
