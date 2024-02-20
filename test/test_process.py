import unittest

from DMMGamePlayerFastLauncher.lib.process_manager import ProcessManager


class TestProcessManager(unittest.TestCase):
    def test_admin_check(self):
        value = ProcessManager.admin_check()
        self.assertFalse(value)

    def test_run(self):
        value = ProcessManager.run(["echo", "test"])
        data = value.communicate()
        self.assertEqual(data, (b"test\r\n", b""))


if __name__ == "__main__":
    unittest.main()
