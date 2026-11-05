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

    def update_best(self, score, correct, total):
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            print("새로운 최고 점수입니다!")

    def show_score(self):
        if self.best_score is None:
            print("아직 완료한 퀴즈가 없습니다.")
        else:
            print(f"최고 점수: {self.best_score:g}점 ({self.best_total}문제 중 {self.best_correct}문제 정답)")

    def load_state(self):
        try:
            with self.state_path.open(encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not isinstance(data["quizzes"], list):
                raise ValueError("퀴즈 목록 형식 오류")
            quizzes = [Quiz.from_dict(row) for row in data["quizzes"]]
            score = data["best_score"]
            correct = data.get("best_correct", 0)
            total = data.get("best_total", 0)
            if type(correct) is not int or type(total) is not int or not 0 <= correct <= total:
                raise ValueError("정답 수 형식 오류")
            if score is not None:
                if type(score) not in (int, float) or not 0 <= score <= 100 or total == 0:
                    raise ValueError("점수 형식 오류")
                if score != round(correct / total * 100, 2):
                    raise ValueError("점수와 정답 수 불일치")
            elif correct != 0 or total != 0:
                raise ValueError("미플레이 상태 불일치")
            self.quizzes = quizzes
            self.best_score, self.best_correct, self.best_total = score, correct, total
            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개)")
        except FileNotFoundError:
            print("첫 실행입니다. 기본 퀴즈 8개로 시작합니다.")
        except (ValueError, TypeError, KeyError, OverflowError):
            print("데이터 파일이 손상되었습니다. 원본을 백업하고 기본 퀴즈로 복구합니다.")
            backup = self.state_path.with_name("state.corrupt." + datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json")
            try:
                self.state_path.rename(backup)
            except OSError:
                self.writable = False
                print("백업할 수 없어 원본 보호를 위해 저장을 중지합니다.")
        except OSError:
            self.writable = False
            print("파일을 읽을 수 없습니다. 기본 퀴즈로 시작하며 원본 보호를 위해 저장을 중지합니다.")

    def save_state(self):
        if not self.writable:
            print("저장이 중지된 상태입니다. 파일 경로와 권한을 확인하세요.")
            return False
        temporary = self.state_path.with_name(self.state_path.name + ".tmp")
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
        }
        try:
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            temporary.replace(self.state_path)
            return True
        except OSError:
            print("저장하지 못했습니다. 파일 경로와 쓰기 권한을 확인하세요.")
            return False
