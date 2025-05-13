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

# 차량 이미지 로드 및 비율 유지 축소
car_image = pygame.image.load("car.png")  # 이미지 파일명 확인!
orig_width, orig_height = car_image.get_size()
scale_factor = 0.5  # 50% 축소
new_size = (int(orig_width * scale_factor), int(orig_height * scale_factor))
car_image = pygame.transform.scale(car_image, new_size)

# 차량 변수
car_pos = [400.0, 500.0]
car_angle = 0.0
car_speed = 0.0
steering_angle = 0.0
L = new_size[0]  # 가로 길이 = 축간 거리로 사용

# 주차 영역
parking_rect = pygame.Rect(200, 100, 80, 40)
apriltag_rect = pygame.Rect(220, 80, 40, 20)

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000  # 초 단위

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력
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

    # 자전거 모델
    theta = math.radians(car_angle)
    delta = math.radians(steering_angle)

    if abs(delta) > 1e-4:
        R = L / math.tan(delta)
        omega = car_speed / R
    else:
        omega = 0

    car_angle -= math.degrees(omega * dt)  # 회전방향 보정
    theta = math.radians(car_angle)
    car_pos[0] += car_speed * math.cos(theta) * dt
    car_pos[1] += car_speed * math.sin(theta) * dt

    # 그리기
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, parking_rect, 2)
    pygame.draw.rect(screen, RED, apriltag_rect)

    rotated_car = pygame.transform.rotate(car_image, -car_angle)
    car_rect = rotated_car.get_rect(center=car_pos)
    screen.blit(rotated_car, car_rect.topleft)

    pygame.display.flip()

pygame.quit()
