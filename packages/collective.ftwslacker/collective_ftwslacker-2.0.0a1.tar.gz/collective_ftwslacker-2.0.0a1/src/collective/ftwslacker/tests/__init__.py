from collective.ftwslacker import slack_notifier
from collective.ftwslacker.testing import FTW_SLACKER_FUNCTIONAL_TESTING
from contextlib import contextmanager
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import TestCase

import os
import transaction


class FunctionalTestCase(TestCase):

    layer = FTW_SLACKER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()

    def assertItemsEqual(self, actual, expected, msg=None):
        """Test that sequence expected contains the same elements as actual.
        regardless of their order.

        This method is renamed to assertCountEqual in Python 3.
        """
        return self.assertCountEqual(actual, expected, msg)
        return super().assertItemsEqual(actual, expected, msg)


class ResponseStub:

    def raise_for_status(self):
        pass


class RequestsMock:

    def __init__(self):
        self.posts = []

    def post(self, url, **kwargs):
        kwargs["url"] = url
        self.posts.append(kwargs)
        return ResponseStub()

    @classmethod
    @contextmanager
    def installed(kls):
        original_requests = slack_notifier.requests
        mock_requests = slack_notifier.requests = kls()
        try:
            yield mock_requests
        finally:
            slack_notifier.requests = original_requests


class ActivateEnvVariables:
    def __init__(self, **kwargs):
        self.variables = kwargs

    def __enter__(self):
        for key, value in self.variables.items():
            os.environ[key] = value

    def __exit__(self, *args):
        for key in self.variables.keys():
            del os.environ[key]
