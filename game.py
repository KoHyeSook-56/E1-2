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

    def play(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return
        correct = 0
        total = len(self.quizzes)
        print(f"\n퀴즈를 시작합니다! 총 {total}문제")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[문제 {number}/{total}]")
            quiz.display()
            answer = read_int("정답 입력 (1~4): ", 1, 4)
            if quiz.is_correct(answer):
                correct += 1
                print("정답입니다!")
            else:
                print(f"오답입니다. 정답: {quiz.answer}. {quiz.choices[quiz.answer - 1]}")
        score = round(correct / total * 100, 2)
        print(f"\n결과: {total}문제 중 {correct}문제 정답! ({score:g}점)")
        self.update_best(score, correct, total)
        self.save_state()

    def add_quiz(self):
        print("\n새로운 퀴즈를 추가합니다.")
        question = read_text("문제를 입력하세요: ")
        choices = [read_text(f"선택지 {i}: ") for i in range(1, 5)]
        answer = read_int("정답 번호 (1~4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            print("퀴즈가 추가되고 저장되었습니다!")
        else:
            print("퀴즈는 현재 실행 중에만 추가되었습니다. 저장 오류를 확인하세요.")

    def list_quizzes(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
