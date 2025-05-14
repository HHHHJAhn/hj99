# main.py
import pygame
import math
from path_planning import calc_optimal_path   # RS 경로 생성
from motion_planning import generate_path     # Motion Planning 경로 생성

# =============================================================================
# 1) Pygame 초기 설정
# =============================================================================
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiple Path Planning Demo")

# 색 정의
WHITE = (255, 255, 255)
GRAY  = (200, 200, 200)
BLACK = (  0,   0,   0)
BLUE  = (  0,   0, 255)
RED   = (255,   0,   0)

font = pygame.font.Font(None, 24)

# 자동차 이미지 로드 & 크기 조정 (한 번만)
car_img_orig = pygame.image.load("car.png")
car_img_orig = pygame.transform.scale(car_img_orig, (50, 25))

# =============================================================================
# 2) 자동차 & 주차장 위치 (픽셀)
# =============================================================================
car_px, car_py = 100.0, 300.0
car_yaw_deg    = 0.0

parking_rect   = pygame.Rect(650, 150, 40, 90)
apriltag_rect  = pygame.Rect(660, 130, 20, 10)

# =============================================================================
# 3) 월드 ↔ 픽셀 변환
# =============================================================================
M2P = 50.0  # 1 m = 50 px
def world_to_pix(wx, wy):
    return wx * M2P, HEIGHT - wy * M2P

def pix_to_world(px, py):
    return px / M2P, (HEIGHT - py) / M2P

# =============================================================================
# 4) 시작·목표 상태 정의 (월드 좌표, m, rad)
# =============================================================================
sx, sy = pix_to_world(car_px, car_py)
syaw   = math.radians(-car_yaw_deg)

goal_px = parking_rect.centerx
goal_py = parking_rect.bottom
gx, gy  = pix_to_world(goal_px, goal_py)
gyaw    = -math.pi / 2

max_curvature = 0.1

# RS용
rs_waypoints = []
show_rs      = False

# MotionPlanning용
mp_waypoints = []
show_mp      = False

# =============================================================================
# 5) 버튼 정의
# =============================================================================
btn_rs    = pygame.Rect( 10, HEIGHT - 50, 120, 30)
btn_mp    = pygame.Rect(150, HEIGHT - 50, 120, 30)
btn_reset = pygame.Rect(290, HEIGHT - 50, 120, 30)

txt_rs    = font.render("Show RS Path", True, BLACK)
txt_mp    = font.render("Show MP Path", True, BLACK)
txt_reset = font.render("Reset Paths",  True, BLACK)

# =============================================================================
# 6) 메인 루프
# =============================================================================
clock   = pygame.time.Clock()
running = True

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if btn_rs.collidepoint(ev.pos):
                # RS 경로 계산
                path = calc_optimal_path(sx, sy, syaw, gx, gy, gyaw, max_curvature)
                rs_waypoints = [world_to_pix(x, y) for x, y in zip(path.x, path.y)]
                show_rs = True

            elif btn_mp.collidepoint(ev.pos):
                # Motion Planning 경로 계산
                s = [
                    [sx, sy, math.degrees(syaw)],
                    [gx, gy, math.degrees(gyaw)]
                ]
                px_segs, py_segs, _, _, x_all, y_all = generate_path(s)
                mp_waypoints = [world_to_pix(x, y) for x, y in zip(x_all, y_all)]
                show_mp = True

            elif btn_reset.collidepoint(ev.pos):
                # 경로 리셋
                show_rs = False
                show_mp = False
                rs_waypoints.clear()
                mp_waypoints.clear()

    # 배경
    screen.fill(WHITE)

    # (1) 주차공간 & ApriTag
    pygame.draw.rect(screen, GRAY, parking_rect, 2)
    pygame.draw.rect(screen, RED, apriltag_rect)

    # (2) 버튼
    pygame.draw.rect(screen, GRAY, btn_rs)
    screen.blit(txt_rs,    (btn_rs.x + 10,    btn_rs.y + 6))
    pygame.draw.rect(screen, GRAY, btn_mp)
    screen.blit(txt_mp,    (btn_mp.x + 10,    btn_mp.y + 6))
    pygame.draw.rect(screen, GRAY, btn_reset)
    screen.blit(txt_reset, (btn_reset.x + 10, btn_reset.y + 6))

    # (3) 경로 그리기
    if show_rs and len(rs_waypoints) >= 2:
        pygame.draw.lines(screen, BLUE, False, rs_waypoints, 2)
    if show_mp and len(mp_waypoints) >= 2:
        pygame.draw.lines(screen, RED, False, mp_waypoints, 2)

    # (4) 자동차 (고정)
    rotated = pygame.transform.rotate(car_img_orig, -car_yaw_deg)
    rect    = rotated.get_rect(center=(car_px, car_py))
    screen.blit(rotated, rect.topleft)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
