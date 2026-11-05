"""실행: python main.py (Python 3.10 이상)."""
from game import QuizGame

def main():
    try:
        game = QuizGame()
    except (KeyboardInterrupt, EOFError):
        print("\n시작이 중단되어 안전하게 종료합니다.")
        return
    game.run()

if __name__ == "__main__":
    main()
