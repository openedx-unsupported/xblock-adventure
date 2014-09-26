# Imports ###########################################################

import os
import sys
import time

import pkg_resources

from django.template import Context, Template

from selenium.webdriver.support.ui import WebDriverWait

from workbench import scenarios
from workbench.test.selenium_test import SeleniumTest

# Classes ###########################################################


def SeleniumBaseTest(module_name, default_css_selector, relative_scenario_path='xml'):
    base_dir = os.path.dirname(os.path.realpath(sys.modules[module_name].__file__))
    xml_path = os.path.join(base_dir, relative_scenario_path)

    def _load_resource(resource_path):
        """
        Gets the content of a resource
        """
        resource_content = pkg_resources.resource_string(module_name, resource_path)
        return unicode(resource_content)

    def _render_template(template_path, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = _load_resource(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def _load_scenarios_from_path(xml_path):
        scenarios = []
        if os.path.isdir(xml_path):
            for template in os.listdir(xml_path):
                if not template.endswith('.xml'):
                    continue
                identifier = template[:-4]
                title = identifier.replace('_', ' ').title()
                template_path = os.path.join(relative_scenario_path, template)
                scenario = unicode(_render_template(template_path, {"url_name": identifier}))
                scenarios.append((identifier, title, scenario))
        return scenarios

    class SeleniumBaseTest(SeleniumTest):
        def setUp(self):
            super(SeleniumBaseTest, self).setUp()

            # Use test scenarios
            self.browser.get(self.live_server_url)  # Needed to load tests once
            scenarios.SCENARIOS.clear()
            scenarios_list = _load_scenarios_from_path(xml_path)
            for identifier, title, xml in scenarios_list:
                scenarios.add_xml_scenario(identifier, title, xml)
                self.addCleanup(scenarios.remove_scenario, identifier)

            # Suzy opens the browser to visit the workbench
            self.browser.get(self.live_server_url)

            # She knows it's the site by the header
            header1 = self.browser.find_element_by_css_selector('h1')
            self.assertEqual(header1.text, 'XBlock scenarios')

        def wait_until_disabled(self, submit):
            wait = WebDriverWait(submit, 10)
            wait.until(lambda s: not s.is_enabled(), "{} should be disabled".format(submit.text))

        def wait_until_clickable(self, submit):
            wait = WebDriverWait(submit, 10)
            wait.until(lambda s: s.is_displayed() and s.is_enabled(), "{} should be cliclable".format(submit.text))

        def wait_until_text_in(self, text, elem):
            wait = WebDriverWait(elem, 10)
            wait.until(lambda elem: text in elem.text, "{} should be in {}".format(text, elem.text))

        def go_to_page(self, page_name, css_selector='div.adventure'):
            """
            Navigate to the page `page_name`, as listed on the workbench home
            Returns the DOM element on the visited page located by the `css_selector`
            """
            self.browser.get(self.live_server_url)
            self.browser.find_element_by_link_text(page_name).click()
            time.sleep(1)
            mentoring = self.browser.find_element_by_css_selector(css_selector)
            return mentoring
    return SeleniumBaseTest

AdventureBaseTest = SeleniumBaseTest(__name__, 'div.adventure', 'xml')
