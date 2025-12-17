from trytond.tests.test_tryton import ModuleTestCase, with_transaction

class PartyTestCase(ModuleTestCase):
    "Party Test Case"
    module = 'akademy_party'

    @with_transaction()
    def test_method(self):
        "Test method"
        self.assertTrue(True)

del ModuleTestCase
