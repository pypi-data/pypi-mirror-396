from collective.ftwslacker.interfaces import ISlackNotifier
from collective.ftwslacker.slack_notifier import DEACTIVATE_SLACK_NOTIFICATION
from collective.ftwslacker.slack_notifier import NOTIFICATION_DEACTIVATION_VALUE
from collective.ftwslacker.slack_notifier import notify_slack
from collective.ftwslacker.slack_notifier import SlackNotifier
from collective.ftwslacker.slack_notifier import STANDARD_SLACK_WEBHOOK
from collective.ftwslacker.tests import ActivateEnvVariables
from collective.ftwslacker.tests import FunctionalTestCase
from collective.ftwslacker.tests import RequestsMock
from zope.component import getUtility
from zope.interface.verify import verifyClass


class TestSlackNotifier(FunctionalTestCase):

    def test_implements_interface(self):
        verifyClass(ISlackNotifier, SlackNotifier)

    def test_utility_is_registered_properly(self):
        slack_notifier = getUtility(ISlackNotifier)
        self.assertIsInstance(slack_notifier, SlackNotifier)

    def test_notify_to_webhook_performs_a_post_request(self):
        with RequestsMock.installed() as requests:
            self.wait_for(notify_slack("https://hooks.slack.com/services/foo"))

            self.assertEqual(1, len(requests.posts))
            self.assertEqual(
                "https://hooks.slack.com/services/foo", requests.posts[0].get("url")
            )

    def test_notify_includes_request_payload(self):
        with RequestsMock.installed() as requests:
            self.wait_for(
                notify_slack("https://hooks.slack.com/services/foo", text="Foo bar")
            )

            self.assertEqual(1, len(requests.posts))
            self.assertEqual({"text": "Foo bar"}, requests.posts[0].get("json"))

    def test_notify_to_webhook_without_webhook_url_will_use_standard_slack_webhook_url(
        self,
    ):
        env_vars = {STANDARD_SLACK_WEBHOOK: "http://hooks.slack.com/services/bar"}

        with ActivateEnvVariables(**env_vars):
            with RequestsMock.installed() as requests:
                self.wait_for(notify_slack())

                self.assertEqual(1, len(requests.posts))
                self.assertEqual(
                    "http://hooks.slack.com/services/bar", requests.posts[0].get("url")
                )

    def test_do_not_post_if_no_webhook_url_is_available(self):
        with ActivateEnvVariables(**{}):
            with RequestsMock.installed() as requests:
                self.wait_for(notify_slack())

                self.assertEqual(0, len(requests.posts))

    def test_do_not_post_if_webhook_contains_notification_deactivation_value(self):
        env_vars = {STANDARD_SLACK_WEBHOOK: "http://hooks.slack.com/services/bar"}

        with ActivateEnvVariables(**env_vars):
            with RequestsMock.installed() as requests:
                self.wait_for(notify_slack(NOTIFICATION_DEACTIVATION_VALUE))

                self.assertEqual(0, len(requests.posts))

    def test_do_not_perform_a_request_if_slacker_is_globally_deactivated(self):
        env_vars = {DEACTIVATE_SLACK_NOTIFICATION: NOTIFICATION_DEACTIVATION_VALUE}

        with ActivateEnvVariables(**env_vars):
            with RequestsMock.installed() as requests:
                self.wait_for(notify_slack("https://hooks.slack.com/services/foo"))

                self.assertEqual(0, len(requests.posts))

    def test_default_request_parameters(self):
        with RequestsMock.installed() as requests:
            self.wait_for(notify_slack("https://hooks.slack.com/services/foo"))

            self.assertItemsEqual(
                {
                    "json": {},
                    "timeout": 2,
                    "url": "https://hooks.slack.com/services/foo",
                    "verify": True,
                },
                requests.posts[0],
            )

    def test_override_default_request_parameters_is_possible(self):
        with RequestsMock.installed() as requests:
            self.wait_for(
                notify_slack(
                    "http://someurl",
                    timeout=5,
                    verify=False,
                    param1="Foo",
                    param2="Bar",
                )
            )

            self.assertItemsEqual(
                {"param1": "Foo", "param2": "Bar"}, requests.posts[0].get("json")
            )
            self.assertEqual("http://someurl", requests.posts[0].get("url"))
            self.assertEqual(5, requests.posts[0].get("timeout"))
            self.assertFalse(requests.posts[0].get("verify"))

    def wait_for(self, thread):
        if not thread:
            return

        thread.join()
