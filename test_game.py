"""실제 파일과 터미널 입력을 검증하는 표준 라이브러리 테스트."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from game import QuizGame
from inputs import read_int
from quiz import Quiz


class GameTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="quiz-test-", dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "state.json"
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def game(self):
        return QuizGame(self.path)

    def test_missing_file_uses_eight_defaults(self):
        game = self.game()
        self.assertEqual(len(game.quizzes), 8)
        self.assertIsNone(game.best_score)

    def test_numeric_retry_and_spaces(self):
        with patch("builtins.input", side_effect=["", "  ", "abc", "9", "0", " 2 "]):
            self.assertEqual(read_int("번호: ", 1, 4), 2)
        self.assertIn("빈 입력", self.output.getvalue())
        self.assertIn("숫자로", self.output.getvalue())
        self.assertIn("1~4", self.output.getvalue())

    def test_add_and_reload(self):
        game = self.game()
        with patch("builtins.input", side_effect=["", " 모발의 바깥층은? ", "큐티클", "피지", "눈물", "침", "abc", "5", "1"]):
            game.add_quiz()
        again = self.game()
        self.assertEqual(len(again.quizzes), 9)
        self.assertEqual(again.quizzes[-1].question, "모발의 바깥층은?")
        self.assertEqual(again.quizzes[-1].answer, 1)
        self.assertIn("큐티클", self.path.read_text(encoding="utf-8"))

    def test_play_and_best_persist(self):
        game = self.game()
        answers = [str(q.answer) for q in game.quizzes]
        with patch("game.random.shuffle"), patch("builtins.input", side_effect=answers):
            game.play()
        self.assertEqual(self.game().best_score, 100)
        with patch("game.random.shuffle"), patch("builtins.input", side_effect=[str(q.answer % 4 + 1) for q in game.quizzes]):
            game.play()
        self.assertEqual(self.game().best_score, 100)
        self.assertIn("오답입니다", self.output.getvalue())

    def test_play_shuffles_questions_without_reordering_saved_quizzes(self):
        game = self.game()
        original_questions = [quiz.question for quiz in game.quizzes]
        shuffled_quizzes = list(reversed(game.quizzes))
        answers = [str(quiz.answer) for quiz in shuffled_quizzes]
        with patch("game.random.shuffle", side_effect=lambda quizzes: quizzes.reverse()), patch(
            "builtins.input", side_effect=answers
        ):
            game.play()
        output = self.output.getvalue()
        positions = [output.index(quiz.question) for quiz in shuffled_quizzes]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual([quiz.question for quiz in game.quizzes], original_questions)
        self.assertEqual(game.best_score, 100)

    def test_zero_score_differs_from_not_played(self):
        game = self.game()
        with patch("game.random.shuffle"), patch("builtins.input", side_effect=[str(q.answer % 4 + 1) for q in game.quizzes]):
            game.play()
        self.assertEqual(self.game().best_score, 0)
        game.show_score()
        self.assertIn("최고 점수: 0점", self.output.getvalue())

    def test_corrupt_data_backup_and_recover(self):
        for text in ['{broken', '{"quizzes": [{"question": "x", "choices": [], "answer": 1}], "best_score": null}', '[]', '{"quizzes": [], "best_score": 99, "best_total": 2, "best_correct": 1}']:
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                game = self.game()
                self.assertEqual(len(game.quizzes), 8)
                self.assertTrue(game.save_state())
                self.assertEqual(len(json.loads(self.path.read_text(encoding="utf-8"))["quizzes"]), 8)
        self.assertEqual(len(list(self.path.parent.glob("state.corrupt.*.json"))), 4)

    def test_invalid_utf8_recovers(self):
        self.path.write_bytes(b"\xff\xfe")
        self.assertEqual(len(self.game().quizzes), 8)

    def test_empty_quizzes_load_play_and_list(self):
        self.path.write_text('{"quizzes": [], "best_score": null}', encoding="utf-8")
        game = self.game()
        self.assertEqual(game.quizzes, [])
        game.play()
        game.list_quizzes()
        game.show_score()
        self.assertIn("등록된 퀴즈가 없습니다", self.output.getvalue())
        self.assertIn("아직 완료한", self.output.getvalue())

    def test_read_error_preserves_original(self):
        with patch.object(Path, "open", side_effect=PermissionError):
            game = self.game()
        self.assertFalse(game.writable)
        self.assertFalse(game.save_state())

    def test_write_error_returns_false(self):
        game = self.game()
        with patch.object(Path, "open", side_effect=PermissionError):
            self.assertFalse(game.save_state())

    def test_interruption_saves_completed_state(self):
        for error in (KeyboardInterrupt, EOFError):
            with self.subTest(error=error):
                game = self.game()
                with patch("game.random.shuffle"), patch("builtins.input", side_effect=error):
                    game.run()
                self.assertTrue(self.path.is_file())
        self.assertIn("입력이 중단", self.output.getvalue())

    def test_interrupted_registration_is_not_added(self):
        game = self.game()
        with patch("builtins.input", side_effect=["2", "새 문제", KeyboardInterrupt]):
            game.run()
        self.assertEqual(len(self.game().quizzes), 8)

    def test_interrupted_play_does_not_record_partial_score(self):
        game = self.game()
        with patch("builtins.input", side_effect=["1", "2", EOFError]):
            game.run()
        self.assertIsNone(self.game().best_score)

    def test_quiz_validation(self):
        for question, choices, answer in [("", ["a"] * 4, 1), ("Q", ["a"] * 3, 1), ("Q", ["a"] * 4, 0), ("Q", ["a"] * 4, True)]:
            with self.assertRaises(ValueError):
                Quiz(question, choices, answer)

    def test_real_console_eof_and_script_relative_path(self):
        # 외부 작업 폴더에서 시작해도 지정된 프로젝트 위치에 저장합니다.
        script = Path(__file__).with_name("main.py")
        project_state = script.with_name("state.json")
        old = project_state.read_bytes() if project_state.exists() else None
        try:
            process = subprocess.run([sys.executable, "-X", "utf8", str(script)], input="", text=True, encoding="utf-8", capture_output=True, cwd=self.directory.name)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("입력이 중단", process.stdout)
            self.assertTrue(project_state.exists())
            self.assertFalse(self.path.exists())
        finally:
            if old is None:
                project_state.unlink(missing_ok=True)
            else:
                project_state.write_bytes(old)


if __name__ == "__main__":
    unittest.main(verbosity=2)
