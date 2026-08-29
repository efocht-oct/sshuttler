import unittest

from sshuttle.resilience import RetryPolicy, add_keepalives, run_with_retries


class ResilienceTests(unittest.TestCase):
    def test_backoff_is_bounded(self):
        policy = RetryPolicy(0.5, 2.0)
        self.assertEqual([policy.delay_after(n) for n in range(1, 6)],
                         [0.5, 1.0, 2.0, 2.0, 2.0])

    def test_default_ssh_gets_keepalives(self):
        command = add_keepalives(None, 15, 3)
        self.assertIsNotNone(command)
        self.assertIsInstance(command, str)
        self.assertIn("ServerAliveInterval=15", command)
        self.assertIn("ServerAliveCountMax=3", command)
        self.assertIn("TCPKeepAlive=yes", command)

    def test_custom_ssh_command_is_preserved(self):
        command = "ssh -W %h:%p jump-host"
        self.assertEqual(add_keepalives(command, 15, 3), command)

    def test_restarts_until_limit(self):
        results = iter((255, 1, 2))
        starts = []
        sleeps = []

        def run_once():
            starts.append(True)
            return next(results)

        self.assertEqual(
            run_with_retries(run_once, RetryPolicy(1, 2), 2, sleeps.append), 2)
        self.assertEqual(len(starts), 3)
        self.assertEqual(sleeps, [1, 2])

    def test_normal_exit_does_not_sleep(self):
        sleeps = []
        self.assertEqual(
            run_with_retries(lambda: 0, sleeper=sleeps.append), 0)
        self.assertEqual(sleeps, [])


if __name__ == "__main__":
    unittest.main()
