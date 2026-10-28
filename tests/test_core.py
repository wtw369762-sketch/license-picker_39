"""单元测试：数据集、打分模型、CLI 输出。"""

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from license_picker import cli
from license_picker.core import Preferences, recommend, score_license, top
from license_picker.rules import LicenseDataError, find, load_licenses, parse_license


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.licenses = load_licenses()

    def test_dataset_not_empty(self):
        self.assertGreaterEqual(len(self.licenses), 6)

    def test_spdx_unique_and_sorted(self):
        spdx_ids = [lic.spdx for lic in self.licenses]
        self.assertEqual(len(spdx_ids), len(set(spdx_ids)))
        self.assertEqual(spdx_ids, sorted(spdx_ids))

    def test_every_license_has_obligations(self):
        for lic in self.licenses:
            with self.subTest(spdx=lic.spdx):
                self.assertTrue(lic.obligations)
                self.assertTrue(lic.good_for)
                self.assertIn(lic.category, {
                    "permissive",
                    "weak-copyleft",
                    "strong-copyleft",
                    "network-copyleft",
                    "public-domain",
                })

    def test_find_returns_known_license(self):
        self.assertEqual(find("MIT").spdx, "MIT")

    def test_find_unknown_raises(self):
        with self.assertRaises(KeyError):
            find("WTFPL-NOT-IN-DATASET")

    def test_missing_field_raises(self):
        broken = {
            "spdx": "X-1",
            "name_zh": "测试",
            "category": "permissive",
            "patent_grant": False,
            "trademark_grant": False,
            "osi_approved": True,
            "software_ready": True,
            "summary": "缺少 obligations 与 good_for",
        }
        with self.assertRaises(LicenseDataError):
            parse_license(broken)

    def test_illegal_category_raises(self):
        broken = {
            "spdx": "X-2",
            "name_zh": "测试",
            "category": "copyleft-ish",
            "patent_grant": False,
            "trademark_grant": False,
            "osi_approved": True,
            "software_ready": True,
            "summary": "分类非法",
            "obligations": ["无"],
            "good_for": ["测试"],
        }
        with self.assertRaises(LicenseDataError):
            parse_license(broken)


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.licenses = load_licenses()

    def test_permissive_wins_when_closed_source_allowed(self):
        prefs = Preferences(allow_closed_source=True)
        self.assertEqual(top(prefs, 1)[0].license.category, "permissive")

    def test_copyleft_wins_when_closed_source_forbidden(self):
        prefs = Preferences(allow_closed_source=False)
        self.assertEqual(top(prefs, 1)[0].spdx, "GPL-3.0")

    def test_agpl_wins_for_network_service(self):
        prefs = Preferences(allow_closed_source=False, is_network_service=True)
        self.assertEqual(top(prefs, 1)[0].spdx, "AGPL-3.0")

    def test_patent_grant_raises_mit_penalty(self):
        plain = score_license(find("MIT"), Preferences(allow_closed_source=True))
        patent = score_license(
            find("MIT"), Preferences(allow_closed_source=True, need_patent_grant=True)
        )
        self.assertEqual(patent.score, plain.score - 2)
        self.assertTrue(any("专利" in reason for reason in patent.reasons))

    def test_weak_copyleft_preferred_for_library(self):
        prefs = Preferences(allow_closed_source=True, is_library=True)
        names = [item.spdx for item in top(prefs, 3)]
        self.assertTrue({"LGPL-3.0", "MPL-2.0"} & set(names))

    def test_scores_are_sorted_and_stable(self):
        ranked = recommend(Preferences(allow_closed_source=True, need_patent_grant=True))
        scores = [item.score for item in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(len(ranked), len(self.licenses))
        again = recommend(Preferences(allow_closed_source=True, need_patent_grant=True))
        self.assertEqual([i.spdx for i in ranked], [i.spdx for i in again])

    def test_every_recommendation_explains_itself(self):
        for item in recommend(Preferences(allow_closed_source=False)):
            with self.subTest(spdx=item.spdx):
                self.assertTrue(item.reasons)


class TestCli(unittest.TestCase):
    def test_json_output_is_parseable(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = cli.main(["--profile", "hobby", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertIn("recommendations", payload)
        self.assertEqual(payload["recommendations"][0]["spdx"], "BSD-3-Clause")
        self.assertTrue(payload["preferences"]["keep_it_short"])

    def test_list_mode_prints_every_license(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            cli.main(["--list"])
        output = buffer.getvalue()
        for lic in load_licenses():
            self.assertIn(lic.spdx, output)

    def test_text_output_contains_obligations(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            cli.main(["--profile", "saas", "--top", "2"])
        output = buffer.getvalue()
        self.assertIn("AGPL-3.0", output)
        self.assertIn("主要义务", output)


class TestWebBuild(unittest.TestCase):
    def test_build_web_is_deterministic(self):
        import importlib.util
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location("build_web", root / "tools" / "build_web.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        first = module.render_page()
        second = module.render_page()
        self.assertEqual(first, second)
        self.assertIn("AGPL-3.0", first)
        self.assertIn("<table", first)


if __name__ == "__main__":
    unittest.main()
