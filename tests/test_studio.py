from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from comedy_studio.scenarios import SCENARIOS, choose_scenario
from comedy_studio.video import create_video, validate_video


class ScenarioTests(unittest.TestCase):
    def test_every_scenario_has_four_original_captioned_scenes(self):
        self.assertGreaterEqual(len(SCENARIOS), 10)
        for scenario in SCENARIOS:
            self.assertEqual(len(scenario["scenes"]), 4)
            self.assertTrue(all(scene["caption"].strip() and scene["description"].strip()
                                for scene in scenario["scenes"]))

    def test_recent_history_avoids_repeating_a_concept(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / "history.json"
            seen = set()
            for seed in range(7):
                scenario, state = choose_scenario(history, seed=seed, recent_limit=6)
                self.assertNotIn(scenario["id"], seen)
                seen.add(scenario["id"])
                self.assertEqual(state["recent"][0], scenario["id"])
            self.assertEqual(json.loads(history.read_text())["recent"][0], scenario["id"])

    def test_category_selection_and_unknown_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            scenario, _ = choose_scenario(Path(tmp) / "history.json", category="funny-animals", seed=4)
            self.assertEqual(scenario["category"], "funny-animals")
            with self.assertRaises(ValueError):
                choose_scenario(Path(tmp) / "bad.json", category="not-a-category")


class VideoTests(unittest.TestCase):
    def test_renders_and_validates_playable_mp4(self):
        # A tiny fast integration encode exercises actual drawing, AAC/H.264 encoding and full decode.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "comedy.mp4"
            scenario = SCENARIOS[0]
            created = create_video(scenario, path, fps=4, seconds_per_scene=0.5)
            self.assertTrue(created.is_file())
            info = validate_video(created)
            self.assertEqual((info["width"], info["height"]), (720, 1280))
            self.assertEqual(info["video_codec"], "h264")
            self.assertEqual(info["audio_codec"], "aac")
            self.assertGreaterEqual(info["duration"], 1)

    def test_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                validate_video(Path(tmp) / "missing.mp4")


if __name__ == "__main__":
    unittest.main()
