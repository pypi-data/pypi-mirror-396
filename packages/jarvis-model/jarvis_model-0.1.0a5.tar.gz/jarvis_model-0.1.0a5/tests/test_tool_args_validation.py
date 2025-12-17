import unittest
from typing import Any, cast

from jarvis_model import ToolArgsValidationError, validate_tool_args


class TestToolArgsValidation(unittest.TestCase):
    def test_good_args_pass(self) -> None:
        schema = {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        }
        validate_tool_args(schema, {"text": "hello"})

    def test_bad_args_fail_with_normalized_error(self) -> None:
        schema = {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        }
        with self.assertRaises(ToolArgsValidationError) as ctx:
            validate_tool_args(schema, {})

        self.assertEqual(ctx.exception.error.code, "tool.invalid_args")
        details = ctx.exception.error.details
        self.assertIsInstance(details, dict)
        details_dict = cast(dict[str, Any], details)
        issues = details_dict.get("issues")
        self.assertIsInstance(issues, list)
        issues_list = cast(list[Any], issues)
        self.assertGreaterEqual(len(issues_list), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
