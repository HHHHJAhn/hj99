# tracking.py
import math

def normalize(a):
    """-π ~ π 범위로 정규화"""
    while a > math.pi:
        a -= 2*math.pi
    while a < -math.pi:
        a += 2*math.pi
    return a

class RSTracker:
    """
    Reeds-Shepp 경로의 전·후진(directions) 정보를 반영한 Pure Pursuit
    path_px: [(x_px,y_px), ...]
    dir:     [1 or -1,     ...] same length as path_px
    """
    def __init__(self, path_px, path_dir,
                 lookahead=30.0, wheelbase=25.0, speed=2.5):
        self.xs        = [p[0] for p in path_px]
        self.ys        = [p[1] for p in path_px]
        self.dir       = path_dir
        self.N         = len(self.xs)
        self.la        = lookahead
        self.wb        = wheelbase
        self.s         = speed
        self.idx       = 0
        self.align     = False

    def step(self, x, y, yaw):
        """
        :param x, y   현재 픽셀 좌표
        :param yaw    현재 heading (rad, standard)
        :return: new_x, new_y, new_yaw_deg, done
        """
        # 1) 모든 점까지 거리 계산
        dists = [math.hypot(x - xi, y - yi) for xi, yi in zip(self.xs, self.ys)]

        # 2) lookahead 이상인 첫 인덱스 탐색
        idx = self.idx
        while idx < self.N and dists[idx] < self.la:
            idx += 1
        # 안전하게 범위 clamp
        idx = min(idx, self.N - 1)
        self.idx = idx

        # 3) 전·후진 전환 시 제자리 회전
        desired = self.dir[idx]
        prev    = self.dir[idx-1] if idx>0 else desired
        if prev != desired and not self.align:
            self.align = True
            return x, y, math.degrees(yaw), False

        if self.align:
            tx, ty   = self.xs[idx], self.ys[idx]
            base_h   = math.atan2(ty - y, tx - x)
            goal_yaw = base_h + (math.pi if desired<0 else 0)
            err      = normalize(goal_yaw - yaw)
            # 1°/frame로 회전
            if abs(err) > math.radians(1):
                yaw += math.copysign(math.radians(1), err)
                return x, y, math.degrees(yaw), False
            else:
                self.align = False

        # 4) Pure Pursuit 조향
        tx, ty = self.xs[idx], self.ys[idx]
        alpha   = normalize(math.atan2(ty - y, tx - x) - yaw)
        steer   = math.atan2(2 * self.wb * math.sin(alpha), self.la)
        # 후진 시 조향 반전
        steer  *= desired

        # 5) 속도 부호 반영
        vel = self.s * desired

        # 6) 상태 업데이트
        yaw += steer
        x   += vel * math.cos(yaw)
        y   += vel * math.sin(yaw)

        return x, y, math.degrees(yaw), False
