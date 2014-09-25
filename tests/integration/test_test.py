from .base_test import AdventureBaseTest

class TestSeleniumTest(AdventureBaseTest):
    def test_truism(self):
        self.assertTrue(True)

    def test_go_to_page(self):
        self.go_to_page("Branching Adventure")
        # TODO:
        #expected_output = "Default Title\nAdventure description.\nThis is step 1. Continue to to see what's happen."
        #lets_see_what_happes_button_is_pressable = True
