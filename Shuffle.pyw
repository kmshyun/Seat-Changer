import pygame
import sys
import random
import time
from tkinter import simpledialog, messagebox

# 파일 이름을 지정합니다.
file_name = 'Seats.txt'
file_name2 = 'Pos.txt'

# 파일을 읽기 모드로 엽니다.
with open(file_name, 'r', encoding='utf-8') as file:
    # 파일의 모든 줄을 읽어서 lines 리스트에 저장합니다.
    lines = file.readlines()
    lines = [word.replace("\n", "") for word in lines]

with open(file_name2, 'r', encoding='utf-8') as file:
    # 파일의 모든 줄을 읽어서 lines 리스트에 저장합니다.
    lines2 = file.readlines()
    lines2 = [word.replace("\n", "") for word in lines2]


# Pygame 초기화
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
RED = (255, 69, 0)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (169, 169, 169)
GREEN = (50, 205, 50)
YELLOW = (255, 255, 0)

pin_number = []
pin_position = []

# 화면 크기 설정
screen_width = 1000  # 화면 크기 확대
screen_height = 700  # 화면 크기 확대
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("자리 배치 프로그램")

# 버튼 설정
button_width = 100
button_height = 50
button_x = screen_width - button_width - 10
button_y = 10

button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
edit_button_rect = pygame.Rect(button_x, button_y + 60, button_width, button_height)
save_button_rect = pygame.Rect(button_x, button_y + 120, button_width, button_height)

add_button_rect = pygame.Rect(button_x, button_y + 180, button_width, button_height)
remove_button_rect = pygame.Rect(button_x, button_y + 240, button_width, button_height)

pin_button_rect = pygame.Rect(button_x, button_y + 300, button_width, button_height)
unpin_button_rect = pygame.Rect(button_x, button_y + 360, button_width, button_height)

preset_button_rect = pygame.Rect(button_x, button_y + 120, button_width, button_height)
load_button_rect = pygame.Rect(button_x, button_y + 180, button_width, button_height)
save2_button_rect = pygame.Rect(button_x, button_y + 240, button_width, button_height)

# 자리 크기 설정
seat_width = 100
seat_height = 100
seat_margin = 10
rows = 5
cols = 6

# 프리셋 모드
preset_mode = -1

# 폰트 설정
font = pygame.font.Font(pygame.font.get_default_font(), 25)

# 스크롤 변수
scroll_y = 0
scroll_speed = 20

# 초기 자리 숫자 리스트 (1 ~ 26)
def generate_sequential_seat_numbers(a):
    return list(range(1, int(a) + 1))

# 자리 위치 계산
def calculate_seat_positions():
    seat_positions = []
    for row in range(rows):
        for col in range(cols):
            if row == 0 and col < 4:
                continue
            seat_x = seat_margin + col * (seat_width + seat_margin) + 80
            seat_y = seat_margin + row * (seat_height + seat_margin) + 40
            seat_positions.append((seat_x, seat_y))
    return seat_positions

# 자리 위치
seat_positions = calculate_seat_positions()

# 순서대로 배열된 숫자 리스트 생성
seat_numbers = generate_sequential_seat_numbers(26)

# 버튼 그리기 함수
def draw_buttons():
    if not edit_mode:  # EDIT 모드가 아닌 경우에만 Shuffle 버튼을 그림
        pygame.draw.rect(screen, BLUE if not shuffle_mode else RED, button_rect, border_radius=10)
        text = font.render("Shuffle", True, WHITE)
        screen.blit(text, (button_x + 10, button_y + 10))

        pygame.draw.rect(screen, BLUE if preset_mode -1 and not edit_mode else RED, preset_button_rect, border_radius=10)
        text = font.render("Presets", True, WHITE)
        screen.blit(text, (button_x + 5, button_y + 130))

    if preset_mode == 1:
        pygame.draw.rect(screen, BLUE, load_button_rect, border_radius=10)
        text = font.render("Load", True, WHITE)
        screen.blit(text, (button_x + 20, button_y + 190))

        pygame.draw.rect(screen, BLUE, save2_button_rect, border_radius=10)
        text = font.render("Save", True, WHITE)
        screen.blit(text, (button_x + 20, button_y + 250))

    
    pygame.draw.rect(screen, BLUE if not edit_mode else RED, edit_button_rect, border_radius=10)
    text = font.render("Edit", True, WHITE)
    screen.blit(text, (button_x + 20, button_y + 70))
    
    if edit_mode:
        pygame.draw.rect(screen, BLUE, save_button_rect, border_radius=10)
        text = font.render("Save", True, WHITE)
        screen.blit(text, (button_x + 20, button_y + 130))
        
        pygame.draw.rect(screen, GREEN, add_button_rect, border_radius=10)
        text = font.render("+", True, WHITE)
        screen.blit(text, (button_x + 40, button_y + 190))
        
        pygame.draw.rect(screen, RED, remove_button_rect, border_radius=10)
        text = font.render("-", True, WHITE)
        screen.blit(text, (button_x + 40, button_y + 250))

        pygame.draw.rect(screen, BLUE, pin_button_rect, border_radius=10)
        text = font.render("Pin", True, WHITE)
        screen.blit(text, (pin_button_rect.x + 25, pin_button_rect.y + 10))

        pygame.draw.rect(screen, BLUE, unpin_button_rect, border_radius=10)
        text = font.render("Unpin", True, WHITE)
        screen.blit(text, (unpin_button_rect.x + 10, unpin_button_rect.y + 10))

# 메인 루프 변수
running = True
edit_mode = False
shuffle_mode = False
dragging = False
drag_index = -1
pinned_seats = []
scroll_dragging = False

def snap_to_grid(x, y):
    col = round((x - seat_margin - 80) / (seat_width + seat_margin))
    row = round((y - seat_margin - 40) / (seat_height + seat_margin))
    col = max(0, min(col, cols - 1))
    row = max(0, min(row, rows - 1))
    return (seat_margin + col * (seat_width + seat_margin) + 80, seat_margin + row * (seat_height + seat_margin) + 40)

def find_empty_spot():
    global rows
    occupied_spots = set(seat_positions)
    for row in range(rows):
        for col in range(cols):
            new_spot = (seat_margin + col * (seat_width + seat_margin) + 80, seat_margin + row * (seat_height + seat_margin) + 40)
            if new_spot not in occupied_spots:
                return new_spot
    # 새로운 행 추가
    rows += 1
    return (seat_margin + 0 * (seat_width + seat_margin) + 80, seat_margin + (rows - 1) * (seat_height + seat_margin) + 40)

# 셔플 애니메이션 함수
def shuffle_animation():
        # 셔플 버튼 클릭 시 좌석 색깔을 잠깐 바꿔주는 애니메이션
    for i, (seat_x, seat_y) in enumerate(seat_positions):
        pygame.draw.rect(screen, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (seat_x, seat_y, seat_width, seat_height), 5, border_radius=10)  # 노란색으로 변경
        pygame.display.update()
        pygame.time.delay(8)  # 5ms 대기
        pygame.draw.rect(screen, BLACK, (seat_x, seat_y, seat_width, seat_height), 2, border_radius=10)  # 검은색으로 변경
        pygame.display.update()
        pygame.time.delay(8)  # 5ms 대기
    pygame.display.update()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                shuffle_mode = True
                shuffle_animation()  # 셔플 애니메이션 호출

                # 무작위로 배열된 숫자 리스트 생성
                seat_numbers = generate_sequential_seat_numbers(len(seat_numbers))
                random.shuffle(seat_numbers)
                for x in range(len(pin_position)):
                    seat_numbers.remove(pin_number[x])
                    seat_numbers.insert(pin_position[x] - 1, pin_number[x])
                shuffle_mode = False

            elif edit_button_rect.collidepoint(event.pos):
                edit_mode = not edit_mode
                pinned_seats = []
                if edit_mode:
                    # Edit 모드에 들어갈 때 자리 초기화
                    seat_positions = calculate_seat_positions()
                    seat_numbers = generate_sequential_seat_numbers(len(seat_numbers))
            elif save_button_rect.collidepoint(event.pos) and edit_mode:
                edit_mode = False
                messagebox.showinfo("알림", "변경사항을 저장합니다")

            elif add_button_rect.collidepoint(event.pos) and edit_mode:
                seat_numbers.append(len(seat_numbers) + 1)
                new_seat_x, new_seat_y = find_empty_spot()
                seat_positions.append((new_seat_x, new_seat_y))

            elif remove_button_rect.collidepoint(event.pos) and edit_mode:
                if len(seat_positions) > 0:
                    seat_positions.pop()
                    seat_numbers.pop()

            elif preset_button_rect.collidepoint(event.pos) and not edit_mode:
                preset_mode *= -1

            elif load_button_rect.collidepoint(event.pos) and preset_mode == 1:  # Load 버튼 클릭
                try:
                    with open(file_name2, 'r') as f:
                        new_positions = [eval(line.strip()) for line in f]
                    seat_positions = new_positions
                    with open(file_name, 'r') as f:
                        new_numbers = [int(line.strip()) for line in f]
                    seat_numbers = new_numbers
                    with open('Pins.txt', 'r') as f:
                        pins = [int(line.strip()) for line in f]
                    pin_number = pins
                    with open('Pos2.txt', 'r') as f:
                        pin_pos = [eval(line.strip()) for line in f]
                    pin_position = pin_pos
                    print("좌석 배치를 불러왔습니다.")
                except FileNotFoundError:
                    print("저장된 파일이 없습니다.")
            
            elif save2_button_rect.collidepoint(event.pos) and preset_mode == 1:  # Save2 버튼 클릭
                with open(file_name2, 'w') as f:
                    for seat_pos in seat_positions:
                        f.write(f"{seat_pos}\n")
                with open(file_name, 'w') as f:
                    for num in seat_numbers:
                        f.write(f"{num}\n")
                with open('Pins.txt', 'w') as f:
                    for pin in pin_number:
                        f.write(f"{pin}\n")
                with open('Pos2.txt', 'w') as f:
                    for pos in pin_position:
                        f.write(f"{pos}\n")
                print("좌석 배치가 저장되었습니다.")


                with open(file_name2, 'w', encoding='utf-8') as file:
                    for pos in seat_positions:
                        file.write(str(pos) + "\n")
                    messagebox.showinfo("알림", "현재 좌석 배치를 저장하였습니다")

            
            elif pin_button_rect.collidepoint(event.pos) and edit_mode:
                # Pin 버튼 기능
                a = simpledialog.askinteger("고정할 숫자를 입력하세요", "고정할 숫자를 입력하세요:")
                b = simpledialog.askinteger("고정할 자리를 입력하세요", "고정할 자리를 입력하세요:")
                if a in seat_numbers and a not in pin_number and b in seat_numbers and b not in pin_position:
                    pin_number.append(a)
                    pin_position.append(b)
                else:
                    messagebox.showerror("오류", "중복되거나 유효하지 않는 숫자입니다")
                    break
            
            elif unpin_button_rect.collidepoint(event.pos) and edit_mode:
                # Pin 버튼 기능
                pin_number = []
                pin_position = []
                messagebox.showinfo("알림", "모든 고정석을 제거하였습니다")

            else:
                if edit_mode:
                    for i, (seat_x, seat_y) in enumerate(seat_positions):
                        seat_rect = pygame.Rect(seat_x, seat_y, seat_width, seat_height)
                        if seat_rect.collidepoint(event.pos):
                            dragging = True
                            drag_index = i
                            break
                else:
                    for i, (seat_x, seat_y) in enumerate(seat_positions):
                        seat_rect = pygame.Rect(seat_x, seat_y, seat_width, seat_height)

            # 스크롤바 클릭 체크
            if 'scroll_bar' in locals() and scroll_bar.collidepoint(event.pos):
                scroll_dragging = True
                mouse_y_start = event.pos[1]
                scroll_y_start = scroll_y

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging and drag_index != -1:
                seat_positions[drag_index] = snap_to_grid(*seat_positions[drag_index])
            dragging = False
            drag_index = -1
            scroll_dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            if drag_index != -1:
                seat_positions[drag_index] = (event.pos[0] - seat_width // 2, event.pos[1] - seat_height // 2)

        elif event.type == pygame.MOUSEMOTION and scroll_dragging:
            dy = event.pos[1] - mouse_y_start
            scroll_y = scroll_y_start + dy * (rows * (seat_height + seat_margin) + seat_margin - screen_height) / screen_height
            scroll_y = min(0, scroll_y)
            max_scroll = -(rows * (seat_height + seat_margin) + seat_margin - screen_height) - 350
            scroll_y = max(scroll_y, max_scroll)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                scroll_y -= scroll_speed
            elif event.key == pygame.K_UP:
                scroll_y += scroll_speed
            scroll_y = min(0, scroll_y)
            max_scroll = -(rows * (seat_height + seat_margin) + seat_margin - screen_height) - 350
            scroll_y = max(scroll_y, max_scroll)

    # 화면 그리기
    screen.fill(WHITE if not edit_mode else LIGHT_GRAY)

    # 스크롤 적용
    scroll_surface = pygame.Surface((screen_width, screen_height))
    scroll_surface.fill(WHITE if not edit_mode else LIGHT_GRAY)

    # 가장 아래쪽에 있는 타일의 y좌표 - 50에 "WHITEBOARD" 위치 설정
    max_seat_y = max(seat_y for seat_x, seat_y in seat_positions)
    board_y = max_seat_y + 150 + scroll_y

    # 칠판 그리기
    board_text = font.render("WHITEBOARD", True, BLACK)
    board_rect = board_text.get_rect(center=(screen_width / 2, board_y))
    scroll_surface.blit(board_text, board_rect)

    # 자리 그리기
    for i, (seat_x, seat_y) in enumerate(seat_positions):
        if i >= len(seat_numbers):
            continue
        pygame.draw.rect(scroll_surface, BLACK, (seat_x, seat_y + scroll_y, seat_width, seat_height), 2, border_radius=10)
        seat_number = seat_numbers[i]
        seat_text = font.render(str(seat_number), True, BLACK)
        text_rect = seat_text.get_rect(center=(seat_x + seat_width / 2, seat_y + seat_height / 2 + scroll_y))
        scroll_surface.blit(seat_text, text_rect)

    screen.blit(scroll_surface, (0, 0))

    # 스크롤바 그리기
    if rows * (seat_height + seat_margin) + seat_margin > screen_height:
        scroll_bar_height = screen_height * (screen_height / (rows * (seat_height + seat_margin) + seat_margin))
        scroll_bar = pygame.Rect(screen_width - 20, -scroll_y * (screen_height / (rows * (seat_height + seat_margin) + seat_margin)), 10, scroll_bar_height)
        pygame.draw.rect(screen, DARK_GRAY, scroll_bar, border_radius=5)

    # 버튼 그리기
    draw_buttons()

    # 화면 업데이트
    pygame.display.flip()

# Pygame 종료
pygame.quit()
sys.exit()
