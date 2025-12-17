import runpy
import unittest
from unittest.mock import patch


class TestModuleEntryPoint(unittest.TestCase):
    def test_python_m_uses_cli_main(self):
        """Ensure `python -m deployfolder` delegates to deployfolder.cli.main."""
        with patch("deployfolder.cli.main", return_value=123) as mock_main:
            with self.assertRaises(SystemExit) as ctx:
                runpy.run_module("deployfolder", run_name="__main__", alter_sys=True)

        mock_main.assert_called_once()
        self.assertEqual(ctx.exception.code, 123)


if __name__ == "__main__":
    unittest.main()
