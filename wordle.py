import random
import csv
import os
import sys

with open(os.path.join(sys._MEIPASS, "wordle.csv")) as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # 첫 번째 행 건너뛰기
    words = []
    for row in reader:
        words.append(row[0])


def choose_word():
    """단어 목록에서 무작위로 단어 선택."""
    return random.choice(words)


def check_guess(secret_word, guess):
    """추측 단어와 정답 단어 비교하여 결과 반환."""
    feedback = ""
    for i in range(len(guess)):
        if guess[i] == secret_word[i]:
            feedback += "🟩"  # 초록색: 정확한 위치, 정확한 글자
        elif guess[i] in secret_word:
            feedback += "🟨"  # 노란색: 다른 위치에 글자 포함
        else:
            feedback += "⬜"  # 흰색: 글자 포함되지 않음
    return feedback


def display_keyboard(letter_states):
    """쿼티 키보드 배열로 알파벳 상태 표시."""
    keyboard = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

    for row in keyboard:
        padding = " " * (10 - len(row))  # 행 정렬을 위한 패딩
        display_row = ""
        for letter in row:
            if letter.lower() in letter_states:
                if letter_states[letter.lower()] == "🟩":
                    display_row += f"\033[42m {letter} \033[0m"  # 초록색 배경
                elif letter_states[letter.lower()] == "🟨":
                    display_row += f"\033[43m {letter} \033[0m"  # 노란색 배경
                else:
                    display_row += f"\033[47m {letter} \033[0m"  # 회색 배경
            else:
                display_row += f" {letter} "
        print(padding + display_row)


def get_letter_states(secret_word, guess):
    """각 알파벳의 상태를 반환."""
    letter_states = {}

    # 초록색 (정확한 위치) 먼저 체크
    for i, letter in enumerate(guess):
        if letter == secret_word[i]:
            letter_states[letter] = "🟩"

    # 노란색 (포함되지만 다른 위치) 체크
    for i, letter in enumerate(guess):
        if letter not in letter_states:
            if letter in secret_word:
                letter_states[letter] = "🟨"
            else:
                letter_states[letter] = "⬜"

    return letter_states


def find_similar_words(words, guess, letter_states, max_suggestions=5):
    """현재까지의 정보를 바탕으로 유사한 단어 추천."""
    word_scores = []

    for word in words:
        if word == guess:  # 이미 시도한 단어는 제외
            continue

        # 회색 글자가 포함된 단어는 제외
        skip_word = False
        for letter, state in letter_states.items():
            if state == "⬜" and letter in word:
                skip_word = True
                break
        if skip_word:
            continue

        score = 0
        for i, letter in enumerate(word):
            if letter in letter_states:
                if letter_states[letter] == "🟩":
                    # 초록색 글자는 같은 위치에 있어야 함
                    if guess[i] == letter:
                        score += 3
                    else:
                        score -= 2
                elif letter_states[letter] == "🟨":
                    # 노란색 글자는 다른 위치에 있어야 함
                    if guess[i] != letter:
                        score += 2
                    else:
                        score -= 1

        # 노란색 글자가 모두 포함되어 있는지 확인
        yellow_letters = [l for l, s in letter_states.items() if s == "🟨"]
        if all(letter in word for letter in yellow_letters):
            score += 5

        word_scores.append((word, score))

    # 점수 기준으로 정렬하고 상위 5개 반환
    word_scores.sort(key=lambda x: x[1], reverse=True)
    return [word for word, _ in word_scores[:max_suggestions]]


def play_wordle():
    """워들 게임 실행."""
    secret_word = choose_word()
    attempts = 6
    all_letter_states = {}
    print("5글자 단어를 맞춰보세요!")

    attempt = 0
    while attempt < attempts:
        # 키보드 상태 표시
        print("\n현재 키보드 상태:")
        display_keyboard(all_letter_states)

        guess = input(f"\n[{attempt + 1}/{attempts}] 추측 단어를 입력하세요: ").lower()

        if guess not in words:
            print("사전에 없는 단어입니다.")
            continue

        feedback = check_guess(secret_word, guess)
        print(feedback)

        # 알파벳 상태 업데이트
        new_letter_states = get_letter_states(secret_word, guess)
        all_letter_states.update(new_letter_states)

        # 추천 단어 표시
        similar_words = find_similar_words(words, guess, all_letter_states)
        print("\n추천 단어:", ", ".join(similar_words))

        if guess == secret_word:
            print(f"\n🎉 정답입니다! {attempt + 1}번 만에 맞추셨어요! 🎉")
            break

        attempt += 1

    else:
        print(f"\n😭 아쉽네요! 정답은 '{secret_word}'였습니다. 😭")


if __name__ == "__main__":
    play_wordle()
os.system("pause")
