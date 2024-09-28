import unittest

import ft3

from ft3 import template

from . import cfg


class Constants(cfg.Constants):
    """Constant values specific to this file."""

    PATH_ROOT = (
        cfg.Constants.API_PATH
        + cfg.Constants.DEFAULT_VERSION
        )


class TestEndpoint(unittest.TestCase):
    """Fixture for testing the endpoint."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.api = ft3.api.api_from_package(
            f'{Constants.PACAKGE}.template',
            Constants.DEFAULT_VERSION,
            Constants.API_PATH
            )
        cls.handler = ft3.api.Handler(api=cls.api)
        return super().setUpClass()

    def test_01_post(self):
        """Test POST."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='Sophie', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)
        self.assertEqual(response.status_code, 201)

    def test_02_body_syntax_error_raised(self):
        """Test POST with syntax error."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=ft3.api.lib.json.dumps(
                [
                    template
                    .pkg
                    .obj
                    .PetWithPet(name='Sophie', pets=[])
                    .to_dict(
                        camel_case=True,
                        include_null=False,
                        include_private=False,
                        include_write_only=True,
                        include_read_only=False
                        )
                    ]
                )
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 400)

    def test_03_put(self):
        """Test PUT."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='Ralph', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        response.body['in'] = template.pkg.enm.PetLocation.inside.value
        url += ('/' + response.body['id'])

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.PUT,
            body=response.body
            )

        response = self.handler(request)

        self.assertEqual(
            response.body['in'],
            template.pkg.enm.PetLocation.inside.value
            )

    def test_04_delete(self):
        """Test DELETE."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.DELETE,
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 204)

    def test_05_get(self):
        """Test GET."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        response.body['in'] = template.pkg.enm.PetLocation.inside.value
        url += (f'?type={template.pkg.enm.PetType.dog.value}')

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.GET,
            )

        response = self.handler(request)

        self.assertEqual(
            response.body[0]['type'],
            template.pkg.enm.PetType.dog.value
            )

    def test_06_patch(self):
        """Test PATCH."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        url += ('?in=' + template.pkg.enm.PetLocation.inside.value)

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.PATCH
            )

        response = self.handler(request)

        self.assertEqual(
            response.body['in'],
            template.pkg.enm.PetLocation.inside.value
            )

    def test_07_sub_patch(self):
        """Test PATCH for pet's pet."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        url += '/pets'

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.Pet(
                name='Gak',
                pet_with_pet_id=response.body['id']
                ).to_dict(
                    camel_case=True,
                    include_null=False,
                    include_private=False,
                    include_write_only=True,
                    include_read_only=False
                    )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        url += ('?in=' + template.pkg.enm.PetLocation.inside.value)

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.PATCH
            )

        response = self.handler(request)

        self.assertEqual(
            response.body['in'],
            template.pkg.enm.PetLocation.inside.value
            )

    def test_08_sub_delete_get(self):
        """Test DELETE and GET for pet's pet."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        url += '/pets'

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.Pet(
                name='Gak',
                pet_with_pet_id=response.body['id']
                ).to_dict(
                    camel_case=True,
                    include_null=False,
                    include_private=False,
                    include_write_only=True,
                    include_read_only=False
                    )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.DELETE
            )

        response = self.handler(request)

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.GET
            )

        response = self.handler(request)

        self.assertEqual(
            response.body['errorMessage'],
            'No pet could be found for that `petId`.'
            )

    def test_09_sub_put(self):
        """Test PUT for pet's pet."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        url += '/pets'

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.Pet(
                name='Gak',
                pet_with_pet_id=response.body['id']
                ).to_dict(
                    camel_case=True,
                    include_null=False,
                    include_private=False,
                    include_write_only=True,
                    include_read_only=False
                    )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        response.body['in'] = template.pkg.enm.PetLocation.inside.value

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.PUT,
            body=response.body
            )

        response = self.handler(request)

        self.assertEqual(
            response.body['in'],
            template.pkg.enm.PetLocation.inside.value
            )

    def test_10_sub_put_sophie(self):
        """Test PUT for pet's pet."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        url += '/pets'

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.Pet(
                name='Sophie',
                pet_with_pet_id=response.body['id']
                ).to_dict(
                    camel_case=True,
                    include_null=False,
                    include_private=False,
                    include_write_only=True,
                    include_read_only=False
                    )
            )

        response = self.handler(request)

        url += ('/' + response.body['id'])
        response.body['in'] = template.pkg.enm.PetLocation.inside.value

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.PUT,
            body=response.body
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 500)

    def test_11_patch_with_error(self):
        """Test PATCH 404."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='James', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        url += ('/' + '123')
        url += ('?in=' + template.pkg.enm.PetLocation.inside.value)

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.PATCH
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 404)

    def test_12_post_serialization(self):
        """Test POST serialization."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='Sophie', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        self.assertIsInstance(response.serialize(), str)

    def test_13_post_serialization(self):
        """Test POST serialization idempotency."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.POST,
            body=template.pkg.obj.PetWithPet(name='Sophie', pets=[]).to_dict(
                camel_case=True,
                include_null=False,
                include_private=False,
                include_write_only=True,
                include_read_only=False
                )
            )

        response = self.handler(request)

        response.body = response.serialize()

        self.assertEqual(response.body, response.serialize())

    def test_14_get_file(self):
        """Test GET file."""

        request = ft3.api.Request(
            url=Constants.API_PATH,
            path=Constants.API_PATH,
            method=Constants.GET
            )

        response = self.handler(request)

        self.assertEqual(
            response.body,
            ft3.api.FILES[Constants.API_PATH].content
            )

    def test_15_get_file_unexpected_error(self):
        """Test GET file raises unexpected error."""

        request = ft3.api.Request(
            url=Constants.PATH_ROOT,
            path=Constants.PATH_ROOT,
            method=Constants.GET
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 500)

    def test_16_options(self):
        """Test OPTIONS."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method=Constants.OPTIONS
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 204)

    def test_17_not_implemented(self):
        """Test method not implemented."""

        url = '/'.join(
            (
                Constants.PATH_ROOT,
                ft3.core.strings.utl.pluralize(
                    template.pkg.obj.PetWithPet.__name__[0].lower()
                    + template.pkg.obj.PetWithPet.__name__[1:]
                    )
                )
            )

        request = ft3.api.Request(
            url=url,
            path=url,
            method='NOT_IMPLEMENTED'
            )

        response = self.handler(request)

        self.assertEqual(response.status_code, 500)
