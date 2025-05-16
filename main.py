# main.py
import pygame
import math
from path_planning import calc_optimal_path
from tracking import RSTracker

# ─────────────────────────────────────────────────────────────────────────────
# 1) 초기화 & 상수
# ─────────────────────────────────────────────────────────────────────────────
pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("RS Forward/Reverse Parking (Auto-Stop)")

WHITE, GRAY, BLACK = (255,255,255), (200,200,200), (0,0,0)
BLUE, GREEN, RED  = (0,0,255),    (0,200,0),    (255,0,0)
font = pygame.font.Font(None, 24)

# 차량 이미지
car_img = pygame.image.load("car.png")
car_img = pygame.transform.scale(car_img, (50,25))

# 초기 위치
px, py, yaw_deg = 100.0, 300.0, 0.0

# 주차 슬롯
slot = pygame.Rect(650, 150, 40, 90)
tag  = pygame.Rect(660, 130, 20, 10)

# 픽셀↔월드 변환
M2P = 50.0
def w2p(wx, wy): return wx*M2P, H-wy*M2P
def p2w(px, py): return px/M2P, (H-py)/M2P

sx, sy = p2w(px, py)
syaw   = math.radians(-yaw_deg)
gx, gy = p2w(slot.centerx, slot.bottom)
gyaw   = -math.pi/2
maxc   = 0.1

# 버튼
btn_path  = pygame.Rect( 10, H-50,120,30)
btn_reset = pygame.Rect(150, H-50,120,30)
btn_go    = pygame.Rect(290, H-50,120,30)
t_path    = font.render("Make RS Path",    True, BLACK)
t_reset   = font.render("Reset",            True, BLACK)
t_go      = font.render("Start Parking",   True, BLACK)

# 상태
way_px    = []   # [(x_px,y_px), ...]
way_dir   = []   # [1 or -1, ...]
tracker   = None
made_path = False

# 멈춤 임계값 (픽셀)
stop_threshold = 5

clock = pygame.time.Clock()
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            # ─── Make RS Path ───────────────────────────────────────────
            if btn_path.collidepoint(ev.pos):
                path = calc_optimal_path(sx, sy, syaw, gx, gy, gyaw, maxc)

                raw = [w2p(x,y) for x,y in zip(path.x, path.y)]
                dirs = list(path.directions)

                # 슬롯 깊이만큼 연장
                if len(raw) >= 2:
                    x1,y1 = raw[-2]
                    x2,y2 = raw[-1]
                    dx,dy = x2-x1, y2-y1
                    norm = math.hypot(dx,dy) or 1.0
                    ux,uy = dx/norm, dy/norm
                    depth = slot.height
                    raw.append((x2+ux*depth, y2+uy*depth))
                    dirs.append(dirs[-1])

                way_px    = raw
                way_dir   = dirs
                made_path = True
                tracker   = None

            # ─── Reset ───────────────────────────────────────────────────
            elif btn_reset.collidepoint(ev.pos):
                way_px.clear()
                way_dir.clear()
                made_path = False
                tracker   = None
                px,py,yaw_deg = 100.0, 300.0, 0.0

            # ─── Start Parking ────────────────────────────────────────────
            elif btn_go.collidepoint(ev.pos) and made_path:
                tracker = RSTracker(
                    way_px, way_dir,
                    lookahead=30.0,
                    wheelbase=25.0,
                    speed=2.5
                )

    # ─── 화면 그리기 ───────────────────────────────────────────────────────
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, slot, 2)
    pygame.draw.rect(screen, RED,  tag)

    for b,t,c in [
        (btn_path,  t_path,  GRAY),
        (btn_reset, t_reset, GRAY),
        (btn_go,    t_go,    GREEN),
    ]:
        pygame.draw.rect(screen, c, b)
        screen.blit(t, (b.x+10, b.y+6))

    if made_path and len(way_px) > 1:
        pygame.draw.lines(screen, BLUE, False, way_px, 2)

    # ─── 주차 업데이트 ───────────────────────────────────────────────────
    if tracker:
        px, py, yaw_deg, done = tracker.step(px, py, math.radians(yaw_deg))

        # 슬롯 중앙에 도달했으면 즉시 멈추고 스냅
        dx = px - slot.centerx
        dy = py - slot.centery
        if math.hypot(dx, dy) < stop_threshold:
            px, py = slot.centerx, slot.centery
            tracker = None

    # ─── 차량 그리기 ───────────────────────────────────────────────────────
    rot = pygame.transform.rotate(car_img, -yaw_deg)
    r   = rot.get_rect(center=(px, py))
    screen.blit(rot, r.topleft)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
