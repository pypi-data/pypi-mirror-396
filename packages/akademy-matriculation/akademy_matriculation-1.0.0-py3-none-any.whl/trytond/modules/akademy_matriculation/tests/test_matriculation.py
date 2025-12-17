from trytond.tests.test_tryton import ModuleTestCase, with_transaction

class MatriculationTestCase(ModuleTestCase):
    "Matriculation Test Case"
    module = 'akademy_matriculation'

    @with_transaction()
    def test_method(self):
        "Test method"
        self.assertTrue(True)

del ModuleTestCase
