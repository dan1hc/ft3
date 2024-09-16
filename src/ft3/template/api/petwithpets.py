"""Template PetWithPets endpoints."""

__all__ = (
    'delete',
    'insert',
    'read',
    'replace',
    'update',
    )

from ... api import Request

from .. import pkg


@pkg.obj.PetWithPet.DELETE
def delete(request: Request) -> None:
    """Delete a single record."""

    if isinstance(request.body, dict):
        id_ = request.path_params['petWithPetId']
        pkg.clients.DatabaseClient.delete_one(id_)
    else:
        raise SyntaxError

    return None


@pkg.obj.PetWithPet.GET
def read(request: Request) -> list[pkg.obj.PetWithPet]:
    """Read many records."""

    pets: list[pkg.obj.PetWithPet] = (
        pkg.clients.DatabaseClient.find_many(request.query_params)
        )

    return pets


@pkg.obj.PetWithPet.PATCH
def update(request: Request) -> pkg.obj.PetWithPet:
    """Update a single record."""

    if isinstance(request.body, dict):
        id_ = request.path_params['petWithPetId']
        pet: pkg.obj.PetWithPet = pkg.clients.DatabaseClient.find_one(id_)
        if pet is None:
            raise FileNotFoundError
        pet |= request.query_params
        pkg.clients.DatabaseClient.update_one(pet)
    else:
        raise SyntaxError

    return pet


@pkg.obj.PetWithPet.POST
def insert(request: Request) -> pkg.obj.PetWithPet:
    """Insert single record."""

    if isinstance(request.body, dict):
        pet = pkg.obj.PetWithPet(request.body)  # type: ignore[arg-type, call-arg]
        pkg.clients.DatabaseClient.insert_one(pet)
    else:
        raise SyntaxError

    return pet


@pkg.obj.PetWithPet.PUT
def replace(request: Request) -> pkg.obj.PetWithPet:
    """Replace a single record."""

    if isinstance(request.body, dict):
        pet = pkg.clients.DatabaseClient.update_one(
            pkg.obj.PetWithPet(  # type: ignore[misc]
                id_=request.path_params['petWithPetId'],
                **request.body
                )
            )
    else:
        raise SyntaxError

    return pet