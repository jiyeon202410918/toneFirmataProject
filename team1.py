import pyfirmata2
import time
import random

# 보드와 핀 설정
PORT = 'COM7'
board = pyfirmata2.Arduino(PORT)

# Iterator 시작 (통신 필수)
it = pyfirmata2.util.Iterator(board)
it.start()

# 디지털 핀들 설정
LED_PINS = [2, 3, 4, 5]
BUTTON_PINS = [6, 7, 8, 9]
BUZZER_PIN = 10

# 음계 주파수 정의
NOTES = {
    'C4': 261, 'D4': 294, 'E4': 330, 'F4': 349,
    'G4': 392, 'A4': 440, 'B4': 494, 'C5': 523, 'REST': 0
}

# '반짝반짝 작은별' 악보 (음표, 박자)
TWINKLE_STAR = [
    ('C4', 1), ('C4', 1), ('G4', 1), ('G4', 1), ('A4', 1), ('A4', 1), ('G4', 2),
    ('F4', 1), ('F4', 1), ('E4', 1), ('E4', 1), ('D4', 1), ('D4', 1), ('C4', 2),
    ('G4', 1), ('G4', 1), ('F4', 1), ('F4', 1), ('E4', 1), ('E4', 1), ('D4', 2),
    ('G4', 1), ('G4', 1), ('F4', 1), ('F4', 1), ('E4', 1), ('E4', 1), ('D4', 2),
    ('C4', 1), ('C4', 1), ('G4', 1), ('G4', 1), ('A4', 1), ('A4', 1), ('G4', 2),
    ('F4', 1), ('F4', 1), ('E4', 1), ('E4', 1), ('D4', 1), ('D4', 1), ('C4', 2)
]

# TONE 커스텀 명령어 (아두이노 코드와 동일해야 함)
TONE_CMD = 0x7E 

FAIL_BLINK_COUNT = 3
BPM = 120
WHOLE_NOTE_MS = int(60 / BPM * 1000)

random_sequence = []
user_sequence_index = 0
game_end = False

def play_note_firmata(note, duration):
    freq = NOTES.get(note, 0)
    duration_ms = int(duration * WHOLE_NOTE_MS)
    
    data = [
        BUZZER_PIN,
        freq & 0x7F, (freq >> 7) & 0x7F,
        duration_ms & 0x7F, (duration_ms >> 7) & 0x7F
    ]
    board.send_sysex(TONE_CMD, data)
    
    if freq > 0:
        time.sleep(duration_ms / 1000.0)

def ready_effect():
    print("게임 준비 중...")
    for pin in LED_PINS:
        board.digital[pin].write(1)
    time.sleep(1)
    for pin in LED_PINS:
        board.digital[pin].write(0)

def intro_sequence():
    print("인트로 시퀀스 시작 (도, 미, 솔, 시)")
    intro_notes = ['C4', 'E4', 'G4', 'B4']
    for i in range(4):
        board.digital[LED_PINS[i]].write(1)
        play_note_firmata(intro_notes[i], 0.5)
        board.digital[LED_PINS[i]].write(0)
        time.sleep(0.2)

def success_effect():
    print("성공! '반짝반짝 작은별'을 연주합니다.")
    for note, duration in TWINKLE_STAR:
        for pin in LED_PINS:
            board.digital[pin].write(1)
        play_note_firmata(note, duration)
        for pin in LED_PINS:
            board.digital[pin].write(0)
    
    global game_end
    game_end = True

def failure_effect():
    print("실패! 모든 LED가 동시에 깜빡입니다.")
    for _ in range(FAIL_BLINK_COUNT):
        for pin in LED_PINS:
            board.digital[pin].write(1)
        time.sleep(0.5) # 깜빡임 시간 증가
        for pin in LED_PINS:
            board.digital[pin].write(0)
        time.sleep(0.5)
    global game_end
    game_end = True

def on_button_press(pin_data):
    global user_sequence_index
    global game_end

    if game_end: return

    pressed_pin = BUTTON_PINS.index(pin_data.pin_number)

    # 버튼에 해당하는 음을 짧게 재생
    play_note_firmata(list(NOTES.keys())[pressed_pin], 0.1)

    # 정답 판정
    if pressed_pin == random_sequence[user_sequence_index]:
        user_sequence_index += 1
        print(f"✅ 정답입니다! 현재 {user_sequence_index}번째 버튼을 맞췄습니다.")
        if user_sequence_index == len(random_sequence):
            success_effect()
    else:
        print("❌ 틀렸습니다! 게임 종료.")
        failure_effect()

def main():
    print("아두이노 연결 중...")
    time.sleep(1)

    for pin in LED_PINS:
        board.digital[pin].mode = pyfirmata2.OUTPUT
    for pin in BUTTON_PINS:
        board.digital[pin].mode = pyfirmata2.INPUT_PULLUP
        board.digital[pin].register_callback(on_button_press)
        board.digital[pin].enable_reporting()

    ready_effect()
    intro_sequence()

    print("\n게임 시작! 잘 들으세요.")
    global random_sequence
    random_sequence = [random.choice(range(4)) for _ in range(3)]

    for i in random_sequence:
        board.digital[LED_PINS[i]].write(1)
        play_note_firmata(list(NOTES.keys())[i], 0.3)
        board.digital[LED_PINS[i]].write(0)
        time.sleep(random.uniform(1.5, 2.5))

    print("\n이제 맞추세요!")

    while not game_end:
        time.sleep(0.1)

    board.exit()

if __name__ == '__main__':
    main()