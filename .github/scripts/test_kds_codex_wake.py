import importlib.util
import os
from pathlib import Path
import sys
import unittest


SCRIPT = Path(__file__).with_name('kds_codex_wake.py')
SPEC = importlib.util.spec_from_file_location('kds_codex_wake', SCRIPT)
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)


class CompanyTestNotificationTests(unittest.TestCase):
    def setUp(self):
        self.original_event_name = os.environ.get('GITHUB_EVENT_NAME')
        os.environ['GITHUB_EVENT_NAME'] = 'issue_comment'

    def tearDown(self):
        if self.original_event_name is None:
            os.environ.pop('GITHUB_EVENT_NAME', None)
        else:
            os.environ['GITHUB_EVENT_NAME'] = self.original_event_name

    def test_company_report_creates_email_notification_context(self):
        event = {
            'repository': {'full_name': 'hallurg/hladvarp'},
            'issue': {'number': 17},
            'comment': {
                'user': {'login': 'hallurg'},
                'html_url': 'https://github.com/hallurg/hladvarp/issues/17#issuecomment-1',
                'body': '## Fyrirtækjaprófun — KN\n\n**Staða:** 8/11 staðist · 1 þarfnast lagfæringar\n\n- [!] **Bókhald** — FAIL',
            },
        }
        ctx = bridge.build_context(event)
        self.assertEqual(ctx.reason, 'company test report')
        self.assertTrue(ctx.should_ack)
        self.assertTrue(ctx.should_dispatch)
        message = bridge.company_test_notification(ctx, dispatched=False)
        self.assertIn('@hallurg', message)
        self.assertIn('1 þarfnast lagfæringar', message)
        self.assertIn('— FAIL', message)
        self.assertIn(ctx.comment_url, message)

    def test_bot_notification_does_not_trigger_bridge(self):
        event = {
            'repository': {'full_name': 'hallurg/hladvarp'},
            'issue': {'number': 17},
            'comment': {'user': {'login': 'github-actions[bot]'}, 'body': '## KN prófunartilkynning'},
        }
        ctx = bridge.build_context(event)
        self.assertFalse(ctx.should_dispatch)


if __name__ == '__main__':
    unittest.main()
