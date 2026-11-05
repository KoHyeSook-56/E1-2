"""메뉴, 게임 진행, 상태 저장을 관리합니다."""
import json
import os
from datetime import datetime
from pathlib import Path
from defaults import default_quizzes
from inputs import read_int, read_text
from quiz import Quiz

class QuizGame:
    def __init__(self, state_path=None):
        self.state_path = Path(state_path) if state_path is not None else Path(__file__).with_name("state.json")
        self.quizzes = default_quizzes()
        self.best_score = None
        self.best_correct = 0
        self.best_total = 0
        self.writable = True
        self.load_state()

    def show_menu(self):
        print("\n========================================")
        print("        두피·모발 퀴즈 게임")
        print("========================================")
        print("1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = read_int("선택: ", 1, 5)
                if choice == 1:
                    self.play()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                else:
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되었습니다. 완료된 내용을 저장하고 종료합니다.")
        finally:
            self.save_state()
            print("게임을 종료합니다.")
