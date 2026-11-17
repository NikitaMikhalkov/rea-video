import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rea_video import cli


class ReviewApplyLogTest(unittest.TestCase):
    def test_unanswered_log_is_persisted_without_changing_exit_code(self):
        native_log = {"applied": [], "problems": [], "unanswered": ["shot_001"], "before": {}, "packaging": {}}
        breakdown = {"lang": "en", "shots": [{"id": "shot_001", "base": {"label": "live_action"}}],
                     "summary": {"verdict": "unchanged", "vlm": "off"}}
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "breakdown.json").write_text(json.dumps(breakdown), encoding="utf-8")
            (out / "review_answers.json").write_text('{}', encoding="utf-8")
            args = SimpleNamespace(out_dir=directory, answers=None, lang=None, by="operator")
            with patch("rea_video.review.apply_answers", return_value=native_log), \
                 patch("rea_video.pipeline.finalize", side_effect=lambda b, _: b), \
                 contextlib.redirect_stdout(io.StringIO()):
                code = cli.cmd_apply_review(args)
            self.assertEqual(code, 1)
            self.assertEqual(json.loads((out / "review-apply-log.json").read_text(encoding="utf-8")), native_log)


if __name__ == "__main__":
    unittest.main()
