import pygame
import math

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Parking Simulator")

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# 차량 이미지 불러오기 및 크기 조절
car_image = pygame.image.load("car.png")  # ← 너가 가진 이미지 파일 이름으로 바꿔줘
car_image = pygame.transform.scale(car_image, (60, 120))  # (너비, 높이)

# 차량 변수
car_pos = [400.0, 500.0]       # 화면상의 차량 중심 좌표
car_angle = 0.0                # 차량 회전각 (도 단위)
car_speed = 0.0                # 속도
steering_angle = 0.0           # 조향각
L = 60                         # 축간 거리 (이미지 높이 정도)

# 주차구역 & Apriltag 위치
parking_rect = pygame.Rect(200, 100, 80, 40)
apriltag_rect = pygame.Rect(220, 80, 40, 20)

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000  # 프레임 간 시간 (초 단위)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키보드 입력
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        car_speed = 100
    elif keys[pygame.K_DOWN]:
        car_speed = -100
    else:
        car_speed = 0

    if keys[pygame.K_LEFT]:
        steering_angle = 30
    elif keys[pygame.K_RIGHT]:
        steering_angle = -30
    else:
        steering_angle = 0

    # 자전거 모델 기반 이동
    theta = math.radians(car_angle)
    delta = math.radians(steering_angle)

    # 회전각 있는 경우 회전 반경 계산
    if abs(delta) > 1e-4:
        R = L / math.tan(delta)
        omega = car_speed / R
    else:
        omega = 0

    # 각도 업데이트 (부호 반전!)
    car_angle -= math.degrees(omega * dt)

    # 위치 업데이트
    theta = math.radians(car_angle)
    car_pos[0] += car_speed * math.cos(theta) * dt
    car_pos[1] += car_speed * math.sin(theta) * dt

    # 화면 그리기
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, parking_rect, 2)
    pygame.draw.rect(screen, RED, apriltag_rect)

    # 차량 회전 이미지 그리기
    rotated_car = pygame.transform.rotate(car_image, -car_angle)
    car_rect = rotated_car.get_rect(center=car_pos)
    screen.blit(rotated_car, car_rect.topleft)

    pygame.display.flip()

pygame.quit()
