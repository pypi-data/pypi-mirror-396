import unittest
from pathlib import Path


# Ensure `jarvis_model` is importable in this workspace without packaging yet.
_REPOS_DIR = Path(__file__).resolve().parents[2]
_MODEL_DIR = _REPOS_DIR / "Jarvis" / "Model"
import sys

sys.path.insert(0, str(_MODEL_DIR))

from tool_registry.catalog import ToolCatalog, load_domain_tools  # noqa: E402
from tool_registry.server import ToolRegistryApp  # noqa: E402


class TestToolRegistryApiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        catalog = ToolCatalog(load_domain_tools(["core"]))
        cls._app = ToolRegistryApp(catalog)

    @classmethod
    def tearDownClass(cls) -> None:
        return

    def test_list_tools_returns_minimal_planner_view(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1/tools", body=None)
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, list)
        names = set()
        for item in body:
            self.assertIsInstance(item, dict)
            self.assertEqual(set(item.keys()), {"name", "description"})
            names.add(item["name"])
        self.assertTrue({"echo", "calc", "time_now"}.issubset(names))

    def test_get_tool_definition(self) -> None:
        status, body, _ = self._app.handle(method="GET", path="/v1/tools/echo", body=None)
        self.assertEqual(int(status), 200)
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("name"), "echo")
        self.assertIn("schema_version", body)
        self.assertIn("parameters", body)
        self.assertIsInstance(body["parameters"], dict)

    def test_invoke_ok(self) -> None:
        status, body, _ = self._app.handle(method="POST", path="/v1/tools/echo:invoke", body={"args": {"text": "hi"}})
        self.assertEqual(int(status), 200)
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("result", {}).get("text"), "hi")
        self.assertIsInstance(body.get("metrics", {}).get("latency_ms"), int)

    def test_invoke_invalid_args(self) -> None:
        status, body, _ = self._app.handle(method="POST", path="/v1/tools/echo:invoke", body={"args": {}})
        self.assertEqual(int(status), 400)
        self.assertFalse(body.get("ok"))
        self.assertEqual(body.get("error", {}).get("code"), "tool.invalid_args")
        issues = body.get("error", {}).get("details", {}).get("issues")
        self.assertIsInstance(issues, list)
        self.assertGreaterEqual(len(issues), 1)
        self.assertIsInstance(body.get("metrics", {}).get("latency_ms"), int)

    def test_invoke_unknown_tool(self) -> None:
        status, body, _ = self._app.handle(method="POST", path="/v1/tools/nope:invoke", body={"args": {}})
        self.assertEqual(int(status), 404)
        self.assertFalse(body.get("ok"))
        self.assertEqual(body.get("error", {}).get("code"), "tool.not_found")

    def test_invoke_invalid_json(self) -> None:
        status, body, _ = self._app.handle(method="POST", path="/v1/tools/echo:invoke", body=None)
        self.assertEqual(int(status), 400)
        self.assertEqual(body.get("error", {}).get("code"), "request.invalid_json")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
