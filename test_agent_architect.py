import tempfile
import unittest
from pathlib import Path

from agent_architect import load_repositories, recommend, render, search_repositories


class AgentArchitectTests(unittest.TestCase):
    def test_load_deduplicates_urls(self):
        content = (
            "category,name,full_name,url,description,stars\n"
            "a,one,org/one,https://example.com/one,agent memory,10\n"
            "b,one,org/one,https://example.com/one,agent memory,10\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.csv"
            path.write_text(content)
            self.assertEqual(len(load_repositories(path)), 1)

    def test_recommendations_include_matching_capabilities(self):
        rows = [
            {
                "name": "memory-tool",
                "full_name": "org/memory-tool",
                "url": "https://example.com/memory",
                "description": "persistent memory for agents",
                "stars": "100",
            }
        ]
        result = recommend(rows, "personal assistant")
        self.assertEqual(result["memory"][0]["full_name"], "org/memory-tool")

    def test_render_has_build_order(self):
        output = render("research assistant", {"research": []})
        self.assertIn("## Build order", output)
        self.assertIn("research assistant", output)

    def test_search_requires_all_query_words_and_ranks_stars(self):
        rows = [
            {"full_name": "org/low", "url": "low", "description": "agent memory", "stars": "2"},
            {"full_name": "org/high", "url": "high", "description": "agent memory", "stars": "20"},
            {"full_name": "org/other", "url": "other", "description": "agent search", "stars": "100"},
        ]
        result = search_repositories(rows, "agent memory", 10)
        self.assertEqual([row["full_name"] for row in result], ["org/high", "org/low"])


if __name__ == "__main__":
    unittest.main()
