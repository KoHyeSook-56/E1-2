"""한 문제의 속성과 동작을 정의합니다."""

class Quiz:
    def __init__(self, question, choices, answer):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")
        if any(not isinstance(c, str) or not c.strip() for c in choices):
            raise ValueError("선택지는 비어 있지 않은 문자열이어야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답은 1~4의 정수여야 합니다.")
        self.question = question.strip()
        self.choices = [c.strip() for c in choices]
        self.answer = answer

    def display(self):
        print(self.question)
        for number, choice in enumerate(self.choices, start=1):
            print(f"  {number}. {choice}")

    def is_correct(self, answer):
        return self.answer == answer

    def to_dict(self):
        return {"question": self.question, "choices": self.choices, "answer": self.answer}

    @classmethod
    def from_dict(cls, data):
        return cls(data["question"], data["choices"], data["answer"])
