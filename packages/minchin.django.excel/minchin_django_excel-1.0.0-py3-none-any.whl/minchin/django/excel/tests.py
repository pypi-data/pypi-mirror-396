from django.test import TestCase


class TestSetup(TestCase):

    def test_always_pass(self):
        """Should always pass. Shows test runner is working."""
        self.assertTrue(True)
