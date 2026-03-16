import math
import time
import os
import sys
import random

def rgb(r, g, b):      return f'\033[38;2;{r};{g};{b}m'
def bg_rgb(r, g, b):   return f'\033[48;2;{r};{g};{b}m'
def bold():            return '\033[1m'
def italic():          return '\033[3m'
RESET       = '\033[0m'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'

def clear():           return '\033[2J\033[H'
def move(r, c):        return f'\033[{r};{c}H'

def term_size():
    try:
        s = os.get_terminal_size()
        return s.columns, s.lines
    except:
        return 80, 24

def heart_sdf(x, y):
    return (x*x + y*y - 1)**3 - x*x * y*y*y


BG = (13, 5, 8)

def lerp(a, b, t): return a + (b - a) * t
def clamp(v, lo=0, hi=255): return max(lo, min(hi, int(v)))

def heart_color(t, x, y, cx, cy, w, h):
    nx = (x - cx) / (w * 0.14)
    ny = (y - cy) / (h * 0.24)
    d  = math.sqrt(nx*nx + ny*ny + 1e-9)

    s1 = 0.5 + 0.5*math.sin(t*3.1 + nx*2.8 - ny*1.4)
    s2 = 0.5 + 0.5*math.cos(t*2.3 + ny*3.2 + nx*1.1)
    s3 = 0.5 + 0.5*math.sin(t*1.7 - d*2.5)

    blend = s3 * 0.5 + s1 * 0.3 + s2 * 0.2

    zone = clamp((-ny + 0.2) * 2.5, 0, 1)   

    r = clamp(lerp(lerp(200, 255, blend), lerp(255, 230, blend), zone))
    g = clamp(lerp(lerp(55,  130, blend), lerp(130, 170, blend), zone) * 0.8)
    b = clamp(lerp(lerp(90,  160, blend), lerp(160, 190, blend), zone) * 0.85)

    if ny < -0.35 and nx < -0.05:
        glint = max(0, 1 - d * 3) * s1 * 0.55
        r = clamp(r + glint * 60)
        g = clamp(g + glint * 50)
        b = clamp(b + glint * 55)

    return r, g, b

def glow_color(t, dist_val):
    pulse = 0.5 + 0.5*math.sin(t*2.4)
    fade  = max(0, 1 - dist_val / 0.22) ** 2
    r = clamp(180 * fade * pulse)
    g = clamp( 60 * fade * pulse)
    b = clamp( 90 * fade * pulse)
    return r, g, b

DENSE  = '█'
CHARS  = ['█','▓','▒','░','·']

def body_char(t, nx, ny, noise):
    v = 0.5 + 0.5*math.sin(nx*4 + t*2.2) * math.cos(ny*3.5 - t*1.8)
    if noise > 0.55: return '✦'
    if v > 0.72: return '█'
    if v > 0.50: return '▓'
    if v > 0.28: return '▒'
    return '░'

HEART_CHARS = ['♥','♡','❤','💕','✿','❀','·','°','˚']

class FloatingHeart:
    def __init__(self, x, y):
        self.x  = float(x)
        self.y  = float(y)
        self.vx = random.uniform(-0.15, 0.15)
        self.vy = random.uniform(-0.6, -0.2)
        self.life   = 1.0
        self.decay  = random.uniform(0.018, 0.04)
        self.char   = random.choice(HEART_CHARS)
        self.wobble = random.uniform(0, math.tau)

    def update(self, t):
        self.x  += self.vx + 0.08*math.sin(t*3 + self.wobble)
        self.y  += self.vy
        self.vy += 0.012       
        self.life -= self.decay
        return self.life > 0

MESSAGES = [
    " like ot  ",
    "  loy ot kter   ",
    "  lida   ",
    "  kal thom     ",
    "  nham bay nv  ",
]

def render(t, w, h, floats):
    cx, cy   = w / 2, h / 2 - 1
    sx, sy   = w * 0.145, h * 0.235
    pulse    = 1.0 + 0.055*math.sin(t * 2.6)

    buf = [clear()]
    buf.append(bg_rgb(*BG))
    for row in range(1, h):
        buf.append(move(row, 1))
        buf.append(' ' * w)

    prev_col = (-1,-1,-1)
    prev_bg  = (-1,-1,-1)

    for row in range(1, h - 3):
        line_parts = [move(row, 1)]
        for col in range(1, w + 1):
            x  = (col - cx) / (sx * pulse)
            y  = -(row - cy) / (sy * pulse) * 0.88

            sdf = heart_sdf(x, y)

            if sdf <= 0:
                r, g, b = heart_color(t, col, row, cx, cy, w, h)
               
                noise = 0.5 + 0.5*math.sin(col*1.3 + t*2)*math.cos(row*0.9 - t*1.5)
                nx_ = x; ny_ = y
                ch  = body_char(t, nx_, ny_, noise)

                if (r,g,b) != prev_col:
                    line_parts.append(rgb(r,g,b))
                    prev_col = (r,g,b)
                bg_c = (clamp(BG[0]+8), clamp(BG[1]+3), clamp(BG[2]+5))
                if bg_c != prev_bg:
                    line_parts.append(bg_rgb(*bg_c))
                    prev_bg = bg_c
                line_parts.append(ch)

            elif 0 < sdf < 0.22:
                r,g,b = glow_color(t, sdf)
                if r > 10 or b > 10:
                    bg_r = clamp(BG[0] + r//4)
                    bg_g = clamp(BG[1])
                    bg_b = clamp(BG[2] + b//5)
                    if (r,g,b) != prev_col:
                        line_parts.append(rgb(r,g,b))
                        prev_col = (r,g,b)
                    bg_c = (bg_r, bg_g, bg_b)
                    if bg_c != prev_bg:
                        line_parts.append(bg_rgb(*bg_c))
                        prev_bg = bg_c
                    line_parts.append('·' if sdf > 0.12 else '░')
                else:
                    if BG != prev_bg:
                        line_parts.append(bg_rgb(*BG))
                        prev_bg = BG
                    line_parts.append(' ')
            else:
                if BG != prev_bg:
                    line_parts.append(bg_rgb(*BG))
                    prev_bg = BG
                if BG != prev_col:
                    line_parts.append(rgb(*BG))
                    prev_col = BG
                line_parts.append(' ')

        buf.append(''.join(line_parts))

    for fh in floats:
        r2, c2 = int(fh.y), int(fh.x)
        if 1 <= r2 < h-3 and 1 <= c2 <= w:
            alpha = fh.life
            fr = clamp(255 * alpha)
            fg = clamp(140 * alpha * 0.7)
            fb = clamp(170 * alpha * 0.8)
            buf.append(move(r2, c2))
            buf.append(bg_rgb(*BG))
            buf.append(rgb(fr, fg, fb))
            buf.append(fh.char)

    msg_idx = int(t / 3) % len(MESSAGES)
    msg     = MESSAGES[msg_idx]
    fade    = 0.5 + 0.5*math.sin(t * math.pi / 3)   

    pulse_r = clamp(230 + 25*fade)
    pulse_g = clamp(160 + 40*fade)
    pulse_b = clamp(175 + 30*fade)

    mc = (w - len(msg)) // 2 + 1
    mr = h - 2
    buf.append(move(mr, max(1, mc)))
    buf.append(bg_rgb(*BG))
    buf.append(bold() + italic())
    buf.append(rgb(pulse_r, pulse_g, pulse_b))
    buf.append(msg)

    credit = "♥  for you, ktrit  ♥"
    cc = (w - len(credit)) // 2 + 1
    buf.append(move(h - 1, max(1, cc)))
    buf.append(rgb(80, 35, 50))
    buf.append(RESET + bg_rgb(*BG) + rgb(80,35,50))
    buf.append(credit)

    buf.append(RESET)
    return ''.join(buf)

def heart_boundary_points(cx, cy, sx, sy, n=48):
    pts = []
    for i in range(n):
        θ = math.tau * i / n
        hx = 16 * math.sin(θ)**3
        hy = -(13*math.cos(θ) - 5*math.cos(2*θ) - 2*math.cos(3*θ) - math.cos(4*θ))
        tx = cx + hx / 16 * sx
        ty = cy + hy / 13 * sy * 0.88
        pts.append((tx, ty))
    return pts

def main():
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    floats   = []
    spawn_t  = 0
    t        = 0.0
    fps      = 24
    dt       = 1.0 / fps

    try:
        while True:
            t0 = time.time()
            w, h = term_size()

            cx = w / 2
            cy = h / 2 - 1
            sx = w * 0.145
            sy = h * 0.235
            
            spawn_t += 1
            if spawn_t % 4 == 0 and len(floats) < 60:
                pts = heart_boundary_points(cx, cy, sx, sy)
                px, py = random.choice(pts)
                floats.append(FloatingHeart(px, py))

            floats = [fh for fh in floats if fh.update(t)]

            frame = render(t, w, h, floats)
            sys.stdout.write(frame)
            sys.stdout.flush()

            elapsed = time.time() - t0
            time.sleep(max(0, dt - elapsed))
            t += dt * 1.15

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(clear())
        print(rgb(255, 160, 180) + "  ♥  with love, 1010101  ♥" + RESET)

if __name__ == '__main__':
    main()
