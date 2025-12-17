from trytond.tests.test_tryton import ModuleTestCase, with_transaction

class ReportTestCase(ModuleTestCase):
    "Report Test Case"
    module = 'akademy_avaliation'

    @with_transaction()
    def test_method(self):
        "Test method"
        self.assertTrue(True)

del ModuleTestCase
