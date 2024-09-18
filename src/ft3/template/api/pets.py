"""Template Pets endpoints."""

__all__ = (
    'delete',
    'insert',
    'read',
    'replace',
    'update',
    )

from ... api import Request

from .. import pkg


@pkg.obj.Pet.DELETE
def delete(request: Request) -> None:
    """Delete a single record."""

    parent_id = request.path_params['petWithPetId']
    id_ = request.path_params['petId']

    pet_with_pet: pkg.obj.PetWithPet = (
        pkg.clients.DatabaseClient.find_one(parent_id)
        )

    if pet_with_pet is None:
        raise FileNotFoundError  # pragma: no cover

    pet_with_pet.pets = [
        pet
        for pet
        in pet_with_pet.pets
        if pet.id_ != id_
        ]

    pkg.clients.DatabaseClient.update_one(pet_with_pet)

    return None


@pkg.obj.Pet.GET
def read(request: Request) -> pkg.obj.Pet:
    """Read a single record."""

    parent_id = request.path_params['petWithPetId']
    id_ = request.path_params['petId']

    pet_with_pet: pkg.obj.PetWithPet = (
        pkg.clients.DatabaseClient.find_one(parent_id)
        )

    if pet_with_pet is None:  # pragma: no cover
        raise FileNotFoundError

    for pet in pet_with_pet.pets:
        if pet.id_ == id_:  # pragma: no cover
            return pet

    raise FileNotFoundError('No pet could be found for that `petId`.')


@pkg.obj.Pet.PATCH
def update(request: Request) -> pkg.obj.Pet:
    """Update a single record."""

    parent_id = request.path_params['petWithPetId']
    id_ = request.path_params['petId']

    pet_with_pet: pkg.obj.PetWithPet = (
        pkg.clients.DatabaseClient.find_one(parent_id)
        )

    if pet_with_pet is None:  # pragma: no cover
        raise FileNotFoundError

    for pet in pet_with_pet.pets:
        if pet.id_ == id_:
            pet |= request.query_params
            pkg.clients.DatabaseClient.update_one(pet_with_pet)
            return pet

    raise FileNotFoundError  # pragma: no cover


@pkg.obj.Pet.POST
def insert(request: Request) -> pkg.obj.Pet:
    """Insert single record."""

    if isinstance(request.body, dict):
        parent_id = request.path_params['petWithPetId']

        pet_with_pet: pkg.obj.PetWithPet = (
            pkg.clients.DatabaseClient.find_one(parent_id)
            )

        if pet_with_pet is None:
            raise FileNotFoundError  # pragma: no cover

        pet = pkg.obj.Pet(pet_with_pet_id=parent_id, **request.body)  # type: ignore[misc]
        pet_with_pet.pets.append(pet)
        pkg.clients.DatabaseClient.update_one(pet_with_pet)

        return pet
    else:
        raise SyntaxError  # pragma: no cover


@pkg.obj.Pet.PUT
def replace(request: Request) -> pkg.obj.Pet:
    """Replace a single record."""

    if isinstance(request.body, dict):
        parent_id = request.path_params['petWithPetId']
        id_ = request.path_params['petId']

        pet_with_pet: pkg.obj.PetWithPet = (
            pkg.clients.DatabaseClient.find_one(parent_id)
            )

        if pet_with_pet is None:
            raise FileNotFoundError  # pragma: no cover

        for pet in pet_with_pet.pets:
            if pet.id_ == id_:
                if pet.name == 'Sophie':
                    raise pkg.exc.CustomExampleError
                pet |= request.body
                pkg.clients.DatabaseClient.update_one(pet_with_pet)
                return pet

        raise FileNotFoundError  # pragma: no cover
    else:  # pragma: no cover
        raise SyntaxError
