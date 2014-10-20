from .base_test import AdventureBaseTest


class TestSeleniumTest(AdventureBaseTest):
    def assert_hidden(self, elem):
        self.assertFalse(elem.is_displayed())

    def assert_disabled(self, elem):
        self.assertTrue(elem.is_displayed())
        self.assertFalse(elem.is_enabled())

    def assert_clickable(self, elem):
        self.assertTrue(elem.is_displayed())
        self.assertTrue(elem.is_enabled())

    class _GetChoices(object):
        def __init__(self, adventure):
            self._mcq = adventure.find_element_by_css_selector(".choices")

        @property
        def text(self):
            return self._mcq.text

        @property
        def state(self):
            state = {}
            for choice in self._mcq.find_elements_by_css_selector(".choice"):
                state[choice.text] = choice.find_element_by_css_selector(".choice-selector").is_selected()
            return state

        def select(self, text):
            state = {}
            for choice in self._mcq.find_elements_by_css_selector(".choice"):
                if choice.text == text:
                    choice.find_element_by_css_selector(".choice-selector").click()
                    return

    def assert_persistent_elements_present(self, adventure):
        self.assertIn("Branching Adventure", adventure.text)
        self.assertIn("A familiar encounter from 1976", adventure.text)
        self.assertIn("Start Over", adventure.text)

    def get_nav_controls(self, adventure):
        return {
            'back': adventure.find_element_by_css_selector(".navigation-back"),
            'next': adventure.find_element_by_css_selector(".navigation-next"),
            'start-over': adventure.find_element_by_css_selector(".navigation-start-over"),
        }

    def assert_at_step_1(self, adventure):
        self.wait_until_text_in("Welcome to adventure!!", adventure)
        controls = self.get_nav_controls(adventure)

        self.assertIn("Branching Adventure", adventure.text)
        self.assertIn("A familiar encounter from 1976", adventure.text)
        self.assertNotIn("Start Over", adventure.text)

        self.assert_hidden(controls['back'])
        self.assert_clickable(controls['next'])

        return controls

    def _assert_at_step_2(self, adventure):
        self.wait_until_text_in("You enter the dragon's cave. The age-old beast stands before you!", adventure)
        controls = self.get_nav_controls(adventure)

        self.assert_persistent_elements_present(adventure)

        self.assert_clickable(controls['back'])

        choices = self._GetChoices(adventure)
        self.assertIn("What do you do?", choices.text)
        controls['choices'] = choices

        return controls, choices


    def assert_at_step_2(self, adventure):
        controls, choices = self._assert_at_step_2(adventure)

        self.assert_disabled(controls['next'])
        self.assertEquals(choices.state, {"Kill dragon": False, "Leave": False})

        return controls

    def assert_at_step_2_with_saved_values(self, adventure):
        controls, choices = self._assert_at_step_2(adventure)

        self.assert_clickable(controls['next'])
        self.assertEquals(choices.state, {"Kill dragon": True, "Leave": False})

        return controls

    def assert_at_step_3(self, adventure):
        self.wait_until_text_in("With what? Your bare hands?", adventure)
        controls = self.get_nav_controls(adventure)

        self.assert_clickable(controls['back'])
        self.assert_disabled(controls['next'])

        choices = self._GetChoices(adventure)
        self.assertEquals(choices.state, {"Yes": False, "Um... no..": False})
        controls['choices'] = choices

        return controls

    def _assert_linear_step(self, adventure, text):
        self.wait_until_text_in(text, adventure)
        controls = self.get_nav_controls(adventure)

        self.assert_persistent_elements_present(adventure)

        self.assert_hidden(controls['back'])
        self.assert_clickable(controls['next'])

        return controls

    def assert_at_misstep_1(self, adventure):
        return self._assert_linear_step(adventure, "As you turn your back to the dragon, a hellish flame engulfs you.")

    def assert_at_misstep_2(self, adventure):
        return self._assert_linear_step(adventure, "The dragon feels your hesitation and attacks.")

    def assert_at_bad_end(self, adventure):
        return self._assert_linear_step(adventure, "You die in a blaze.")

    def assert_at_good_end(self, adventure):
        return self._assert_linear_step(
            adventure,
            "Congratulations! You have just vanquished a dragon with your bare hands! (Unbelievable, isn't it?)")

    def assert_at_adventure_end(self, adventure):
        self.wait_until_text_in("End of the adventure. I hope you enjoyed it!", adventure)
        controls = self.get_nav_controls(adventure)

        self.assert_hidden(controls['back'])
        self.assert_hidden(controls['next'])

        return controls

    def test_good_path(self):
        adventure = self.go_to_page("Branching Adventure")
        controls = self.assert_at_step_1(adventure)
        controls['next'].click()

        controls = self.assert_at_step_2(adventure)
        controls['choices'].select("Kill dragon")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_step_3(adventure)
        controls['choices'].select("Yes")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_good_end(adventure)
        controls['next'].click()

        self.assert_at_adventure_end(adventure)

    def test_really_long_session_with_step_backs_and_persistence(self):
        adventure = self.go_to_page("Branching Adventure")
        controls = self.assert_at_step_1(adventure)
        controls['next'].click()

        controls = self.assert_at_step_2(adventure)
        controls['choices'].select("Kill dragon")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_step_3(adventure)
        # oh no, this sounds stupid, let's go back one step
        controls['back'].click()

        controls = self.assert_at_step_2_with_saved_values(adventure)
        controls['choices'].select("Leave")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_misstep_1(adventure)
        controls['next'].click()

        controls = self.assert_at_bad_end(adventure)
        controls['next'].click()

        controls = self.assert_at_adventure_end(adventure)
        # oh, fine, let's try again
        controls['start-over'].click()

        controls = self.assert_at_step_1(adventure)
        controls['next'].click()

        controls = self.assert_at_step_2(adventure)
        controls['choices'].select("Kill dragon")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_step_3(adventure)
        controls['choices'].select("Um... no..")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_misstep_2(adventure)
        # Another failure, I will get back to this later
        self.browser.get(self.live_server_url)
        # Later. It seems the adventure remembers my progress
        adventure = self.go_to_page("Branching Adventure")
        controls = self.assert_at_misstep_2(adventure)
        controls['next'].click()

        controls = self.assert_at_bad_end(adventure)
        # oh, fine, let's try it again... I really suck at this, don't I?
        controls['start-over'].click()

        controls = self.assert_at_step_1(adventure)
        controls['next'].click()

        controls = self.assert_at_step_2(adventure)
        controls['choices'].select("Kill dragon")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_step_3(adventure)
        # oh my, I was already here, let's try again...
        controls['start-over'].click()

        controls = self.assert_at_step_1(adventure)
        controls['next'].click()

        controls = self.assert_at_step_2(adventure)
        controls['choices'].select("Kill dragon")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        controls = self.assert_at_step_3(adventure)
        # argh... I give up for now.
        self.browser.get(self.live_server_url)
        # Later. Yeah, I gave up here last time...
        adventure = self.go_to_page("Branching Adventure")
        controls = self.assert_at_step_3(adventure)
        # Actually... why not?
        controls['choices'].select("Yes")
        self.wait_until_clickable(controls['next'])
        controls['next'].click()

        # Finally! what a counter-intuitive game...
        controls = self.assert_at_good_end(adventure)
        controls['next'].click()

        self.assert_at_adventure_end(adventure)
