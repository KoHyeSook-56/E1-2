"""여러 기능에서 함께 사용하는 입력 함수."""

def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("빈 입력입니다. 내용을 입력하세요.")

def read_int(prompt, minimum, maximum):
    while True:
        value = read_text(prompt)
        try:
            number = int(value)
        except ValueError:
            print("숫자로 입력하세요.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"{minimum}~{maximum} 사이의 번호를 입력하세요.")
