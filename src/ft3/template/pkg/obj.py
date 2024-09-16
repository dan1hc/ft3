"""Template objects."""

__all__ = (
    'Pet',
    'PetWithPet'
    )

from ... import Api, Field, Object

from . import enm
from . import lib


class Pet(Object):
    """Pet of a pet."""

    pet_with_pet_id: Field[str]
    """The unique identifier of the parent pet."""

    id_: Field[str] = Field(
        default=lambda: lib.uuid.uuid4().hex,  # type: ignore[arg-type]
        read_only=True
        )
    """
    Unique identifier for the [sub] pet.

    ---

    Fields called 'id' (including underscore variations) are special, \
    they will automatically be combined with their class name to form \
    a clear object id.

    In thise case: `petId`.

    """

    name: Field[str]
    """Name of the [sub] pet."""

    type_: Field[str] = Field(
        default=enm.PetType.dog.value,
        required=True,
        enum=enm.PetType
        )
    """Type of [sub] pet. Allowed values: `'Cat', 'Dog'`."""

    in_: Field[str] = {
        'default': enm.PetLocation.outside.value,
        'required': False,
        'enum': enm.PetLocation
        }
    """Locations in which the [sub] pet can be."""

    is_tail_wagging: Field[bool] = True
    """Whether the [sub] pet's tail is currently wagging."""


@Api.register
class PetWithPet(Object):
    """
    A simple pet that makes for a good example.

    * This python docstring will be parsed as the default description \
    for its corresponding RESTful resource.

    * It will always be parsed as the description / docstring for the \
    Pet object itself in all auto-generated documentation.

    * It will be rendered in [markdown](https://www.markdownguide.org/cheat-sheet/).

    """

    id_: Field[str] = Field(
        default=lambda: lib.uuid.uuid4().hex,  # type: ignore[arg-type]
        read_only=True
        )
    """
    Unique identifier for the pet.

    ---

    Fields called 'id' (including underscore variations) are special, \
    they will automatically be combined with their class name to form \
    a clear object id.

    In this case: `petWithPetId`.

    """

    name: Field[str]
    """Name of the pet."""

    type_: Field[str] = Field(
        default=enm.PetType.dog.value,
        required=True,
        enum=enm.PetType
        )
    """Type of pet. Allowed values: `'Cat', 'Dog'`."""

    in_: Field[str] = Field(
        default=enm.PetLocation.outside.value,
        required=False,
        enum=enm.PetLocation
        )
    """Locations in which the pet can be."""

    is_tail_wagging: Field[bool] = True
    """Whether the pet's tail is currently wagging."""

    pets: Field[list[Pet]] = (
        lambda: [
            Pet(  # type: ignore[call-arg]
                name='Fido',
                type_='dog',
                in_='timeout',
                is_tail_wagging=False
                )
            ]
        )
    """The pet(s) of a pet."""

    def __post_init__(self) -> None:
        """Automatically set pets' parent ids on instantiation."""

        for pet in self.pets:
            pet.pet_with_pet_id = self.id_

        return super().__post_init__()
