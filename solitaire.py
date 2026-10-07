# -*- coding: utf-8 -*-
"""
LA CASA DE PAPEL — Пасьянс «Косынка» + реалистичный Профессор
"""

import pygame
import random
import sys
import math
import os

pygame.init()

# ---------------------------------------------------------------
#  КОНСТАНТЫ
# ---------------------------------------------------------------
CARD_W, CARD_H = 90, 130
MARGIN         = 30
GAP            = 18
TOP_Y          = 30

PROF_Y         = 195
PROF_H         = 175
TABLEAU_Y      = 400

WIDTH, HEIGHT  = 1000, 1100
FOOTER_H       = 130
FOOTER_Y       = HEIGHT - FOOTER_H

FOUND_X = WIDTH - MARGIN - CARD_W - 3 * (CARD_W + GAP)

CHAR_SIZE       = 60
HERO_ROTATE_MS  = 6000

BG         = (48, 12, 16)
BG_DARK    = (28, 6, 9)
RED        = (200, 24, 36)
RED_LIGHT  = (226, 70, 70)
DARK_RED   = (108, 14, 22)
GOLD       = (226, 187, 74)
GOLD_LIGHT = (250, 222, 130)
GOLD_DARK  = (140, 100, 20)
CREAM      = (246, 241, 228)
CARD_WHITE = (255, 255, 255)
CARD_BLACK = (18, 18, 22)
CARD_BORDER= (30, 26, 28)
BLACK      = (26, 22, 24)
SHADOW     = (12, 3, 5)
QUOTE_COL  = (208, 168, 128)

RANKS = ['', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SPADES, HEARTS, DIAMONDS, CLUBS = 0, 1, 2, 3

CHARACTERS = [
    ("ПРОФЕССОР", "El Profesor", "profesor",
     "План был идеальным. Всё идёт по плану.",             (86, 130, 180)),
    ("ТОКИО",     "Tokyo",       "tokyo",
     "Живи быстро. Умирай молодой. Но не сегодня.",        (200, 60, 80)),
    ("БЕРЛИН",    "Berlin",      "berlin",
     "Я — король. А короли не отступают.",                 (180, 40, 40)),
    ("НАЙРОБИ",   "Nairobi",     "nairobi",
     "Мы — семья. А семья не бросает своих.",              (220, 130, 60)),
    ("ДЕНВЕР",    "Denver",      "denver",
     "Никогда не сдавайся, даже если весь мир против.",    (60, 150, 90)),
    ("РИО",       "Rio",         "rio",
     "Хакер всегда найдёт лазейку.",                       (80, 100, 200)),
    ("ХЕЛЬСИНКИ", "Helsinki",    "helsinki",
     "Слово — золото. Молчание — платина.",                (130, 100, 70)),
    ("ЛИССАБОН",  "Lisboa",      "lisboa",
     "Правда всегда всплывает наружу.",                    (150, 60, 160)),
    ("МАРСЕЛЬ",   "Marseille",   "marseille",
     "Я приду, когда буду нужен.",                         (100, 100, 120)),
    ("ПАЛЕРМО",   "Palermo",     "palermo",
     "Рим падёт. А я — нет.",                              (200, 170, 40)),
    ("СТОКГОЛЬМ", "Stockholm",   "stockholm",
     "Иногда нужно просто довериться.",                    (220, 100, 140)),
    ("БОГОТА",    "Bogotá",      "bogota",
     "Тишина — лучший план.",                              (110, 150, 130)),
]

PROFESSOR_QUOTES = [
    "Всё идёт по плану.",
    "Держите позиции, ребята.",
    "Мы не воры. Мы — сопротивленцы.",
    "Не паникуйте. Это часть плана.",
    "Берлин, не натвори глупостей.",
    "Ещё немного. Мы почти у цели.",
    "Доверьтесь мне. Всё под контролем.",
    "Внимание. Начинаем следующий этап.",
    "Помните: главное — выйти живыми.",
]


def load_font(names, size, bold=False):
    for n in names:
        path = pygame.font.match_font(n, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def load_background(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                raw = pygame.image.load(p).convert()
                iw, ih = raw.get_size()
                scale = max(size[0] / iw, size[1] / ih)
                new = (max(1, int(iw * scale)), max(1, int(ih * scale)))
                raw = pygame.transform.smoothscale(raw, new)
                surf = pygame.Surface(size)
                x = (new[0] - size[0]) // 2
                y = (new[1] - size[1]) // 2
                surf.blit(raw, (-x, -y))
                print(f"[OK] Фон загружен: {p}")
                return surf
            except Exception as e:
                print(f"[!] Не смог загрузить {p}: {e}")
    print("[i] Фон не найден — используется стандартный тёмный.")
    return None


def load_card_back(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                raw = pygame.image.load(p).convert_alpha()
                iw, ih = raw.get_size()
                scale = max(size[0] / iw, size[1] / ih)
                new = (max(1, int(iw * scale)), max(1, int(ih * scale)))
                raw = pygame.transform.smoothscale(raw, new)
                surf = pygame.Surface(size, pygame.SRCALPHA)
                x = (new[0] - size[0]) // 2
                y = (new[1] - size[1]) // 2
                surf.blit(raw, (-x, -y))
                print(f"[OK] Рубашка карт загружена: {p}")
                return surf
            except Exception as e:
                print(f"[!] Не смог загрузить рубашку {p}: {e}")
    print("[i] Рубашка карт не найдена — использую нарисованную маску.")
    return None


def load_mask_img(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                raw = pygame.image.load(p).convert_alpha()
                print(f"[OK] Маска загружена: {p}")
                return raw
            except Exception as e:
                print(f"[!] Не смог загрузить маску {p}: {e}")
    print("[i] Маска (mask.png) не найдена — рисую встроенную.")
    return None


class Card:
    __slots__ = ('suit', 'rank', 'face_up')

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False

    @property
    def is_red(self):
        return self.suit in (HEARTS, DIAMONDS)


# ===============================================================
#  ПРОФЕССОР — реалистичная отрисовка
# ===============================================================
class Professor:

    def __init__(self, x, y, f_quote):
        self.x = x
        self.y = y
        self.f_quote = f_quote

        self.quote_index = 0
        self.quote_timer = 0
        self.quote_duration = 5500

        self.blinking = False
        self.blink_timer = 0
        self.blink_len = 130
        self.blink_next = random.randint(2500, 5000)

        self.fold_timer = 0
        self.fold_cycle = 1100
        self.fold_frame = 0

        self.phone_pulse = 0.0

    def update(self, dt_ms):
        self.quote_timer += dt_ms
        if self.quote_timer >= self.quote_duration:
            self.quote_timer = 0
            self.quote_index = (self.quote_index + 1) % len(PROFESSOR_QUOTES)

        if self.blinking:
            self.blink_timer += dt_ms
            if self.blink_timer >= self.blink_len:
                self.blinking = False
                self.blink_timer = 0
                self.blink_next = random.randint(2500, 5000)
        else:
            self.blink_timer += dt_ms
            if self.blink_timer >= self.blink_next:
                self.blinking = True
                self.blink_timer = 0

        self.fold_timer += dt_ms
        if self.fold_timer >= self.fold_cycle:
            self.fold_timer = 0
            self.fold_frame = (self.fold_frame + 1) % 3

        self.phone_pulse = math.sin(pygame.time.get_ticks() / 500.0) * 1.5

    # ------------------------------------------------------------
    def draw(self, surf):
        cx = self.x
        cy = self.y

        # ---------- стол ----------
        table_w = 230
        table_h = 8
        pygame.draw.rect(surf, (32, 20, 12),
                         (cx - table_w // 2, cy - table_h, table_w, table_h),
                         border_radius=3)
        pygame.draw.rect(surf, (95, 65, 38),
                         (cx - table_w // 2, cy - table_h, table_w, 2),
                         border_radius=3)

        # ---------- торс: костюм ----------
        torso_w, torso_h = 104, 92
        torso_x = cx - torso_w // 2
        torso_y = cy - table_h - torso_h + 6

        # пиджак
        pygame.draw.rect(surf, (104, 116, 104),
                         (torso_x, torso_y, torso_w, torso_h),
                         border_radius=16)
        pygame.draw.rect(surf, (58, 66, 58),
                         (torso_x, torso_y, torso_w, torso_h),
                         2, border_radius=16)

        # тень на левой половине пиджака
        shade = pygame.Surface((torso_w // 3, torso_h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 45))
        surf.blit(shade, (torso_x, torso_y))

        # рубашка (V-образный вырез)
        pygame.draw.polygon(surf, (78, 88, 92), [
            (cx - 22, torso_y + 4),
            (cx + 22, torso_y + 4),
            (cx + 14, torso_y + torso_h),
            (cx - 14, torso_y + torso_h),
        ])
        # тень на рубашке слева
        pygame.draw.polygon(surf, (48, 55, 58), [
            (cx - 22, torso_y + 4),
            (cx, torso_y + 4),
            (cx, torso_y + torso_h),
            (cx - 14, torso_y + torso_h),
        ])

        # воротник
        pygame.draw.polygon(surf, (206, 210, 205), [
            (cx - 22, torso_y + 4),
            (cx - 7, torso_y + 22),
            (cx - 15, torso_y + 28),
        ])
        pygame.draw.polygon(surf, (206, 210, 205), [
            (cx + 22, torso_y + 4),
            (cx + 7, torso_y + 22),
            (cx + 15, torso_y + 28),
        ])
        pygame.draw.polygon(surf, (150, 155, 150), [
            (cx - 22, torso_y + 4),
            (cx - 7, torso_y + 22),
            (cx - 15, torso_y + 28),
        ], 1)
        pygame.draw.polygon(surf, (150, 155, 150), [
            (cx + 22, torso_y + 4),
            (cx + 7, torso_y + 22),
            (cx + 15, torso_y + 28),
        ], 1)

        # галстук
        pygame.draw.polygon(surf, (34, 44, 62), [
            (cx - 6, torso_y + 22),
            (cx + 6, torso_y + 22),
            (cx + 5, torso_y + torso_h - 6),
            (cx - 5, torso_y + torso_h - 6),
        ])
        # узел
        pygame.draw.polygon(surf, (22, 30, 45), [
            (cx - 5, torso_y + 20),
            (cx + 5, torso_y + 20),
            (cx + 4, torso_y + 28),
            (cx - 4, torso_y + 28),
        ])
        # блик на галстуке
        pygame.draw.line(surf, (70, 85, 110),
                         (cx - 1, torso_y + 32),
                         (cx - 1, torso_y + torso_h - 8), 1)

        # лацканы
        pygame.draw.polygon(surf, (82, 94, 82), [
            (cx - 24, torso_y + 4),
            (cx - 6, torso_y + 32),
            (cx - 18, torso_y + 64),
            (cx - 34, torso_y + 10),
        ])
        pygame.draw.polygon(surf, (82, 94, 82), [
            (cx + 24, torso_y + 4),
            (cx + 6, torso_y + 32),
            (cx + 18, torso_y + 64),
            (cx + 34, torso_y + 10),
        ])

        # ---------- голова ----------
        head_w, head_h = 64, 78
        head_cx = cx
        head_cy = torso_y - head_h // 2 + 10

        # шея
        pygame.draw.rect(surf, (196, 162, 140),
                         (cx - 11, head_cy + head_h // 2 - 10, 22, 22))

        # волосы — задний слой (масса вокруг головы)
        hair_color = (52, 38, 32)
        hair_back = pygame.Rect(head_cx - head_w // 2 - 8,
                                head_cy - head_h // 2 - 10,
                                head_w + 16, head_h - 6)
        pygame.draw.ellipse(surf, hair_color, hair_back)

        # лицо
        face_color = (228, 188, 162)
        face_rect = pygame.Rect(head_cx - head_w // 2,
                                head_cy - head_h // 2,
                                head_w, head_h)
        pygame.draw.ellipse(surf, face_color, face_rect)

        # тень на правой половине лица
        shade = pygame.Surface((head_w, head_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shade, (0, 0, 0, 50),
                            (head_w // 2 - 2, 0, head_w // 2 + 2, head_h))
        surf.blit(shade, (face_rect.x, face_rect.y))

        # волосы спереди (чёлка и виски)
        # чёлка
        pygame.draw.polygon(surf, hair_color, [
            (head_cx - head_w // 2 - 5, head_cy - head_h // 5),
            (head_cx - head_w // 2 + 4, head_cy - head_h // 2 - 6),
            (head_cx - 8, head_cy - head_h // 2 - 10),
            (head_cx + 8, head_cy - head_h // 2 - 9),
            (head_cx + head_w // 2 - 4, head_cy - head_h // 2 - 4),
            (head_cx + head_w // 2 + 5, head_cy - head_h // 5),
            (head_cx + head_w // 2 - 2, head_cy - head_h // 2 + 8),
            (head_cx + 12, head_cy - head_h // 2 + 3),
            (head_cx - 4, head_cy - head_h // 2 + 5),
            (head_cx - 12, head_cy - head_h // 2 + 3),
            (head_cx - head_w // 2 + 2, head_cy - head_h // 2 + 8),
        ])
        # тёмный блик в волосах
        pygame.draw.arc(surf, (80, 60, 52),
                        (head_cx - 22, head_cy - head_h // 2 - 4, 44, 26),
                        1.6, 4.6, 2)

        # виски — прикрывают бока лица
        for side in (-1, 1):
            r = pygame.Rect(head_cx + side * (head_w // 2) - 10,
                            head_cy - head_h // 6,
                            20, head_h // 2 + 4)
            pygame.draw.ellipse(surf, hair_color, r)

        # ---------- глаза и очки ----------
        eye_y = head_cy - 4
        eye_off = 11
        lx = head_cx - eye_off
        rx = head_cx + eye_off

        # линзы (полупрозрачные)
        glass_r = 11
        for ex in (lx, rx):
            lens = pygame.Surface((glass_r * 2, glass_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(lens, (190, 210, 220, 65),
                               (glass_r, glass_r), glass_r)
            surf.blit(lens, (ex - glass_r, eye_y - glass_r))

        # глаза
        if not self.blinking:
            for ex in (lx, rx):
                pygame.draw.circle(surf, (238, 232, 222), (ex, eye_y), 4)
                pygame.draw.circle(surf, (48, 38, 32), (ex, eye_y), 2)
                pygame.draw.circle(surf, (255, 255, 255), (ex - 1, eye_y - 1), 1)
        else:
            for ex in (lx, rx):
                pygame.draw.line(surf, (60, 48, 40),
                                 (ex - 4, eye_y), (ex + 4, eye_y), 2)

        # оправа очков (золотая)
        frame_color = (168, 130, 62)
        for ex in (lx, rx):
            pygame.draw.circle(surf, frame_color, (ex, eye_y), glass_r, 2)
        # перемычка
        pygame.draw.line(surf, frame_color,
                         (lx + glass_r, eye_y - 1),
                         (rx - glass_r, eye_y - 1), 2)
        # дужки
        pygame.draw.line(surf, frame_color,
                         (lx - glass_r + 1, eye_y - 3),
                         (head_cx - head_w // 2 + 3, eye_y - 7), 2)
        pygame.draw.line(surf, frame_color,
                         (rx + glass_r - 1, eye_y - 3),
                         (head_cx + head_w // 2 - 3, eye_y - 7), 2)

        # брови
        brow_color = (48, 34, 28)
        pygame.draw.line(surf, brow_color,
                         (lx - 6, eye_y - 12), (lx + 6, eye_y - 14), 3)
        pygame.draw.line(surf, brow_color,
                         (rx - 6, eye_y - 14), (rx + 6, eye_y - 12), 3)

        # нос
        nose_x = head_cx
        nose_y = eye_y + 10
        pygame.draw.polygon(surf, (205, 168, 142), [
            (nose_x - 3, nose_y - 6),
            (nose_x + 3, nose_y - 6),
            (nose_x + 4, nose_y + 4),
            (nose_x - 4, nose_y + 4),
        ])
        pygame.draw.line(surf, (185, 148, 122),
                         (nose_x - 4, nose_y + 4),
                         (nose_x + 4, nose_y + 4), 1)

        # ---------- борода и усы ----------
        beard_main = (96, 74, 60)
        beard_dark = (62, 46, 38)
        beard_light = (120, 96, 78)

        # основная масса бороды
        beard_rect = pygame.Rect(head_cx - head_w // 2 + 2,
                                 head_cy + 6,
                                 head_w - 4,
                                 head_h // 2 + 8)
        pygame.draw.ellipse(surf, beard_main, beard_rect)
        # тень слева
        shade = pygame.Surface(beard_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(shade, (0, 0, 0, 55),
                            (0, 0, beard_rect.w // 2, beard_rect.h))
        surf.blit(shade, beard_rect.topleft)
        # светлый блик
        pygame.draw.ellipse(surf, beard_light,
                            (head_cx + 4, head_cy + 12, 18, 20))

        # усы
        pygame.draw.ellipse(surf, beard_main,
                            (head_cx - 16, head_cy + 2, 32, 12))
        pygame.draw.ellipse(surf, beard_dark,
                            (head_cx - 15, head_cy + 8, 30, 5))
        pygame.draw.ellipse(surf, beard_light,
                            (head_cx - 6, head_cy + 3, 12, 4))

        # линия губ
        pygame.draw.line(surf, (110, 70, 62),
                         (head_cx - 6, head_cy + 11),
                         (head_cx + 6, head_cy + 11), 1)

        # ---------- левая рука с телефоном ----------
        sh_x = torso_x + 10
        sh_y = torso_y + 16
        el_x = torso_x - 18
        el_y = torso_y + 52

        hd_x = head_cx - head_w // 2 - 4 + self.phone_pulse
        hd_y = head_cy + 4

        pygame.draw.line(surf, (104, 116, 104),
                         (sh_x, sh_y), (el_x, el_y), 17)
        pygame.draw.line(surf, (58, 66, 58),
                         (sh_x, sh_y), (el_x, el_y), 17)
        pygame.draw.line(surf, (104, 116, 104),
                         (el_x, el_y), (hd_x, hd_y), 13)
        pygame.draw.line(surf, (58, 66, 58),
                         (el_x, el_y), (hd_x, hd_y), 13)

        pygame.draw.circle(surf, (196, 162, 140), (hd_x, hd_y), 7)
        pygame.draw.circle(surf, (166, 130, 108), (hd_x, hd_y), 7, 1)

        # телефон у уха
        phone_x = head_cx - head_w // 2 - 6 + self.phone_pulse
        phone_y = head_cy - 4
        pw, ph = 9, 18
        pygame.draw.rect(surf, (18, 18, 22),
                         (phone_x - pw, phone_y, pw, ph),
                         border_radius=2)
        pygame.draw.rect(surf, (90, 200, 120),
                         (phone_x - pw + 2, phone_y + 3,
                          pw - 4, ph - 9),
                         border_radius=1)
        # блик на телефоне
        pygame.draw.line(surf, (60, 60, 70),
                         (phone_x - pw + 2, phone_y + 2),
                         (phone_x - 2, phone_y + 2), 1)

        # ---------- правая рука с оригами ----------
        sh_x2 = torso_x + torso_w - 10
        sh_y2 = torso_y + 16
        el_x2 = torso_x + torso_w + 20
        el_y2 = torso_y + 54

        fold_phase = self.fold_timer / self.fold_cycle
        move = math.sin(fold_phase * math.pi * 2) * 4
        hd_x2 = cx + 44
        hd_y2 = cy - table_h - 10 + move

        pygame.draw.line(surf, (104, 116, 104),
                         (sh_x2, sh_y2), (el_x2, el_y2), 17)
        pygame.draw.line(surf, (58, 66, 58),
                         (sh_x2, sh_y2), (el_x2, el_y2), 17)
        pygame.draw.line(surf, (104, 116, 104),
                         (el_x2, el_y2), (hd_x2, hd_y2), 13)
        pygame.draw.line(surf, (58, 66, 58),
                         (el_x2, el_y2), (hd_x2, hd_y2), 13)

        pygame.draw.circle(surf, (196, 162, 140), (hd_x2, hd_y2), 7)
        pygame.draw.circle(surf, (166, 130, 108), (hd_x2, hd_y2), 7, 1)

        # оригами
        paper_cx = cx + 66
        paper_cy = cy - table_h - 6
        self._draw_origami(surf, paper_cx, paper_cy)

        # облачко
        self._draw_bubble(surf, head_cx + head_w // 2 + 14, head_cy - 10)

    # ------------------------------------------------------------
    def _draw_origami(self, surf, cx, cy):
        paper = (240, 235, 218)
        edge = (170, 155, 130)

        if self.fold_frame == 0:
            half = 12
            pts = [
                (cx - half, cy - half + 2),
                (cx + half, cy - half + 2),
                (cx + half, cy + half + 2),
                (cx - half, cy + half + 2),
            ]
            pygame.draw.polygon(surf, paper, pts)
            pygame.draw.polygon(surf, edge, pts, 1)
            pygame.draw.line(surf, edge,
                             (cx - half, cy - half + 2),
                             (cx + half, cy + half + 2), 1)
        elif self.fold_frame == 1:
            pts = [
                (cx, cy - 12),
                (cx + 14, cy + 10),
                (cx - 14, cy + 10),
            ]
            pygame.draw.polygon(surf, paper, pts)
            pygame.draw.polygon(surf, edge, pts, 1)
            pygame.draw.line(surf, edge, (cx, cy - 12), (cx, cy + 10), 1)
        else:
            body = [
                (cx, cy - 8),
                (cx + 12, cy),
                (cx, cy + 8),
                (cx - 12, cy),
            ]
            pygame.draw.polygon(surf, paper, body)
            pygame.draw.polygon(surf, edge, body, 1)
            for dx in (-1, 1):
                pygame.draw.polygon(surf, paper, [
                    (cx + dx * 12, cy), (cx + dx * 22, cy - 6),
                    (cx + dx * 18, cy + 4)])
                pygame.draw.polygon(surf, edge, [
                    (cx + dx * 12, cy), (cx + dx * 22, cy - 6),
                    (cx + dx * 18, cy + 4)], 1)
            pygame.draw.line(surf, paper, (cx, cy - 8), (cx - 8, cy - 16), 3)
            pygame.draw.circle(surf, paper, (cx - 9, cy - 17), 3)
            pygame.draw.circle(surf, edge, (cx - 9, cy - 17), 3, 1)

    def _draw_bubble(self, surf, bx, by):
        text = PROFESSOR_QUOTES[self.quote_index]
        text_surf = self.f_quote.render(text, True, (30, 20, 25))
        pad_x, pad_y = 12, 7
        bw = text_surf.get_width() + pad_x * 2
        bh = text_surf.get_height() + pad_y * 2

        bubble = pygame.Surface((bw + 20, bh + 16), pygame.SRCALPHA)
        pygame.draw.rect(bubble, (250, 245, 235, 248),
                         (18, 0, bw, bh), border_radius=10)
        pygame.draw.rect(bubble, (130, 90, 55, 255),
                         (18, 0, bw, bh), 2, border_radius=10)

        tail = [
            (18, bh // 2 - 4),
            (0, bh // 2 + 4),
            (18, bh // 2 + 8),
        ]
        pygame.draw.polygon(bubble, (250, 245, 235, 248), tail)
        pygame.draw.lines(bubble, (130, 90, 55, 255), False,
                          [(18, bh // 2 - 4),
                           (0, bh // 2 + 4),
                           (18, bh // 2 + 8)], 2)

        bubble.blit(text_surf, (18 + pad_x, pad_y))
        surf.blit(bubble, (bx, by - bh // 2))


# ===============================================================
#  ИГРА
# ===============================================================
class Solitaire:

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("La Casa de Papel — Пасьянс")
        self.clock = pygame.time.Clock()

        self.f_rank  = load_font(["arial", "dejavusans", "verdana"], 26, True)
        self.f_small = load_font(["arial", "dejavusans", "verdana"], 16)
        self.f_med   = load_font(["arial", "dejavusans", "verdana"], 18)
        self.f_title = load_font(["georgia", "timesnewroman", "dejavuserif", "serif"], 28, True)
        self.f_sub   = load_font(["arial", "dejavusans", "verdana"], 20)
        self.f_big   = load_font(["georgia", "timesnewroman", "dejavuserif", "serif"], 52, True)
        self.f_quote = load_font(["georgia", "timesnewroman", "dejavuserif", "serif"], 16)
        self.f_hero  = load_font(["georgia", "timesnewroman", "dejavuserif", "serif"], 21, True)
        self.f_tiny  = load_font(["arial", "dejavusans", "verdana"], 13)

        self.bg_image = load_background(
            ["background.jpg", "background.png", "bg.jpg", "bg.png"],
            (WIDTH, HEIGHT))

        self.card_back_img = load_card_back(
            ["card_back.png", "card_back.jpg", "card_back.jpeg",
             "back.png", "back.jpg"],
            (CARD_W - 10, CARD_H - 10))

        self.mask_img = load_mask_img(
            ["mask.png", "mask.jpg", "mask.jpeg", "dali.png", "dali.jpg"])

        self._mask_cache = {}
        self.char_photos = {}

        self.professor = Professor(280, PROF_Y + PROF_H, self.f_quote)

        self.new_game()

    def get_char_photo(self, key):
        if key in self.char_photos:
            return self.char_photos[key]
        img = None
        for ext in ('.png', '.jpg', '.jpeg', '.bmp', '.webp',
                    '.PNG', '.JPG', '.JPEG'):
            p = os.path.join('characters', key + ext)
            if os.path.exists(p):
                try:
                    raw = pygame.image.load(p).convert_alpha()
                    w, h = raw.get_size()
                    s = min(w, h)
                    square = pygame.Surface((s, s), pygame.SRCALPHA)
                    square.blit(raw, ((s - w) // 2, (s - h) // 2))
                    img = pygame.transform.smoothscale(square,
                                                       (CHAR_SIZE, CHAR_SIZE))
                    break
                except Exception as e:
                    print(f"[!] Ошибка загрузки {p}: {e}")
        self.char_photos[key] = img
        return img

    def new_game(self):
        deck = [Card(s, r) for s in range(4) for r in range(1, 14)]
        random.shuffle(deck)

        self.stock       = deck
        self.waste       = []
        self.foundations = [[] for _ in range(4)]
        self.tableau     = [[] for _ in range(7)]

        for i in range(7):
            for j in range(i, 7):
                c = self.stock.pop()
                c.face_up = (i == j)
                self.tableau[j].append(c)

        self.drag_src   = None
        self.drag_cards = []
        self.drag_off   = (0, 0)
        self.drag_mouse = (0, 0)
        self.drag_moved = False
        self.drag_start = (0, 0)
        self.selected   = None

        self.moves      = 0
        self.won        = False
        self.start_time = pygame.time.get_ticks()
        self.win_time   = 0

        self.hero_index       = random.randrange(len(CHARACTERS))
        self.last_hero_switch = pygame.time.get_ticks()

    def current_hero(self):
        return CHARACTERS[self.hero_index]

    def update(self, dt_ms):
        now = pygame.time.get_ticks()
        if now - self.last_hero_switch >= HERO_ROTATE_MS:
            self.hero_index = (self.hero_index + 1) % len(CHARACTERS)
            self.last_hero_switch = now
        self.professor.update(dt_ms)

    def stock_rect(self):   return pygame.Rect(MARGIN, TOP_Y, CARD_W, CARD_H)
    def waste_rect(self):   return pygame.Rect(MARGIN + CARD_W + GAP, TOP_Y, CARD_W, CARD_H)
    def foundation_rect(self, i):
        return pygame.Rect(FOUND_X + i * (CARD_W + GAP), TOP_Y, CARD_W, CARD_H)
    def tableau_x(self, i): return MARGIN + i * (CARD_W + GAP)

    def pile_ys(self, pile):
        n = len(pile)
        if n == 0:
            return []
        down_off, up_off = 13, 30
        total = CARD_H
        for c in pile[:-1]:
            total += down_off if not c.face_up else up_off
        max_total = FOOTER_Y - 15 - TABLEAU_Y
        if total > max_total:
            k = max(0.15, (max_total - CARD_H) / max(1, total - CARD_H))
            down_off *= k
            up_off *= k
        ys = [0]
        for i in range(n - 1):
            c = pile[i]
            ys.append(ys[-1] + (down_off if not c.face_up else up_off))
        return ys

    def hit_test(self, pos):
        if self.stock_rect().collidepoint(pos):
            return ('stock', 0, 0)
        if self.waste and self.waste_rect().collidepoint(pos):
            return ('waste', 0, len(self.waste) - 1)
        for i in range(4):
            if self.foundation_rect(i).collidepoint(pos):
                return ('foundation', i, len(self.foundations[i]) - 1)
        for i in range(7):
            pile = self.tableau[i]
            x = self.tableau_x(i)
            if not pile:
                if pygame.Rect(x, TABLEAU_Y, CARD_W, CARD_H).collidepoint(pos):
                    return ('tableau', i, -1)
                continue
            ys = self.pile_ys(pile)
            for j in range(len(pile) - 1, -1, -1):
                r = pygame.Rect(x, TABLEAU_Y + ys[j], CARD_W, CARD_H)
                if r.collidepoint(pos):
                    return ('tableau', i, j)
        return None

    def can_pickup(self, ti, ci):
        pile = self.tableau[ti]
        if ci < 0 or ci >= len(pile):
            return False
        if not pile[ci].face_up:
            return False
        for j in range(ci, len(pile) - 1):
            a, b = pile[j], pile[j + 1]
            if not a.face_up or not b.face_up:
                return False
            if a.is_red == b.is_red or a.rank != b.rank + 1:
                return False
        return True

    def can_place_tableau(self, card, ti):
        pile = self.tableau[ti]
        if not pile:
            return card.rank == 13
        top = pile[-1]
        return (top.face_up and top.is_red != card.is_red
                and card.rank == top.rank - 1)

    def can_place_foundation(self, card, fi):
        pile = self.foundations[fi]
        if not pile:
            return card.rank == 1
        top = pile[-1]
        return top.suit == card.suit and card.rank == top.rank + 1

    def peek(self, src):
        kind, pi, ci = src
        if kind == 'waste':
            return self.waste[-1:]
        if kind == 'foundation':
            return self.foundations[pi][-1:]
        if kind == 'tableau':
            return self.tableau[pi][ci:]
        return []

    def try_move(self, src, dst):
        skind, spidx, scidx = src
        dkind, dpidx, _ = dst

        if dkind in ('stock', 'waste'):
            return False
        if skind == 'tableau' and dkind == 'tableau' and spidx == dpidx:
            return False
        if skind == 'foundation' and dkind == 'foundation':
            return False

        cards = self.peek(src)
        if not cards:
            return False

        if dkind == 'foundation':
            if len(cards) != 1 or not self.can_place_foundation(cards[0], dpidx):
                return False
        else:
            if not self.can_place_tableau(cards[0], dpidx):
                return False

        if skind == 'waste':
            self.waste.pop()
        elif skind == 'foundation':
            self.foundations[spidx].pop()
        else:
            del self.tableau[spidx][scidx:]

        if dkind == 'foundation':
            self.foundations[dpidx].append(cards[0])
        else:
            self.tableau[dpidx].extend(cards)

        if skind == 'tableau' and self.tableau[spidx]:
            top = self.tableau[spidx][-1]
            if not top.face_up:
                top.face_up = True
        return True

    def draw_from_stock(self):
        if self.stock:
            c = self.stock.pop()
            c.face_up = True
            self.waste.append(c)
        elif self.waste:
            while self.waste:
                c = self.waste.pop()
                c.face_up = False
                self.stock.append(c)
            self.moves += 1

    def check_win(self):
        if all(len(f) == 13 for f in self.foundations):
            self.won = True
            self.win_time = (pygame.time.get_ticks() - self.start_time) // 1000

    def start_drag(self, hit, pos):
        kind, pidx, cidx = hit
        if kind == 'tableau':
            x = self.tableau_x(pidx)
            ys = self.pile_ys(self.tableau[pidx])
            y = TABLEAU_Y + ys[cidx]
        elif kind == 'waste':
            x, y = self.waste_rect().topleft
        else:
            x, y = self.foundation_rect(pidx).topleft

        self.drag_src   = hit
        self.drag_cards = self.peek(hit)
        self.drag_off   = (pos[0] - x, pos[1] - y)
        self.drag_mouse = pos
        self.drag_start = pos
        self.drag_moved = False
        self.selected   = hit

    def is_dragged(self, kind, pi, ci):
        if self.drag_src is None:
            return False
        skind, spi, sci = self.drag_src
        if kind != skind or pi != spi:
            return False
        if kind == 'tableau':
            return ci >= sci
        return True

    def handle_mousedown(self, pos):
        if self.won:
            return
        hit = self.hit_test(pos)
        if hit is None:
            self.selected = None
            return

        kind, pidx, cidx = hit

        if self.selected is not None and self.selected != hit:
            if self.try_move(self.selected, hit):
                self.selected = None
                self.moves += 1
                self._after_move()
                return
            self.selected = None

        if kind == 'stock':
            self.draw_from_stock()
            return

        if kind == 'waste' and cidx >= 0:
            self.start_drag(hit, pos)
        elif kind == 'foundation' and cidx >= 0:
            self.start_drag(hit, pos)
        elif kind == 'tableau' and cidx >= 0:
            if self.can_pickup(pidx, cidx):
                self.start_drag(hit, pos)

    def handle_mousemotion(self, pos):
        if self.drag_src is None:
            return
        self.drag_mouse = pos
        if (abs(pos[0] - self.drag_start[0]) +
                abs(pos[1] - self.drag_start[1])) > 6:
            self.drag_moved = True

    def handle_mouseup(self, pos):
        if self.drag_src is None:
            return
        src = self.drag_src
        moved = self.drag_moved
        self.drag_src   = None
        self.drag_cards = []
        self.drag_moved = False
        if not moved:
            return
        hit = self.hit_test(pos)
        if hit is None or hit == src:
            self.selected = None
            return
        if self.try_move(src, hit):
            self.selected = None
            self.moves += 1
            self._after_move()
        else:
            self.selected = None

    def _after_move(self):
        self.check_win()

    def draw_background(self):
        if self.bg_image is not None:
            self.screen.blit(self.bg_image, (0, 0))
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((18, 4, 8, 135))
            self.screen.blit(ov, (0, 0))
            vign = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i in range(0, 260, 4):
                a = int(110 * (1 - i / 260))
                pygame.draw.rect(vign, (0, 0, 0, a // 14),
                                 (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 4)
            self.screen.blit(vign, (0, 0))
        else:
            self.screen.fill(BG)
            vign = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i in range(0, 260, 4):
                a = int(90 * (1 - i / 260))
                pygame.draw.rect(vign, (0, 0, 0, a // 12),
                                 (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 4)
            self.screen.blit(vign, (0, 0))
            ghost = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            r = pygame.Rect(0, 0, 620, 620)
            r.center = (WIDTH // 2, HEIGHT // 2 + 20)
            self.draw_mask(ghost, r, alpha=40)
            self.screen.blit(ghost, (0, 0))

    def draw_slot(self, surf, rect, suit=None):
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 20), s.get_rect(), border_radius=9)
        pygame.draw.rect(s, (255, 255, 255, 60), s.get_rect(), 2, border_radius=9)
        surf.blit(s, rect.topleft)
        if suit is not None:
            self.draw_suit(surf, suit, rect.centerx, rect.centery,
                           46, (255, 255, 255, 65))

    def draw_card_front(self, surf, card, rect):
        color = RED if card.is_red else CARD_BLACK
        radius = 8

        shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 110), shadow.get_rect(),
                         border_radius=radius)
        surf.blit(shadow, (rect.x + 2, rect.y + 3))

        pygame.draw.rect(surf, CARD_WHITE, rect, border_radius=radius)
        inner = rect.inflate(-3, -3)
        pygame.draw.rect(surf, (225, 220, 205), inner, 1,
                         border_radius=radius - 1)
        pygame.draw.rect(surf, CARD_BORDER, rect, 2, border_radius=radius)

        rank_text = RANKS[card.rank]
        f = self.f_rank

        rank_surf = f.render(rank_text, True, color)
        surf.blit(rank_surf, (rect.x + 7, rect.y + 3))
        self.draw_suit(surf, card.suit, rect.x + 15,
                       rect.y + 3 + rank_surf.get_height() + 12, 18, color)

        corner_w = 34
        corner_h = 54
        corner = pygame.Surface((corner_w, corner_h), pygame.SRCALPHA)
        rk = f.render(rank_text, True, color)
        corner.blit(rk, ((corner_w - rk.get_width()) // 2, 0))
        self.draw_suit(corner, card.suit,
                       corner_w // 2, rk.get_height() + 12, 18, color)
        corner = pygame.transform.rotate(corner, 180)
        surf.blit(corner, (rect.right - 7 - corner_w,
                           rect.bottom - 3 - corner_h))

        self.draw_suit(surf, card.suit, rect.centerx, rect.centery + 4,
                       52, color)

    def draw_card_back(self, surf, rect):
        radius = 8
        shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 110), shadow.get_rect(),
                         border_radius=radius)
        surf.blit(shadow, (rect.x + 2, rect.y + 3))

        if self.card_back_img is not None:
            pygame.draw.rect(surf, DARK_RED, rect, border_radius=radius)
            inner = rect.inflate(-10, -10)
            img = self.card_back_img
            if img.get_size() != inner.size:
                img = pygame.transform.smoothscale(img, inner.size)
            mask_surf = pygame.Surface(inner.size, pygame.SRCALPHA)
            pygame.draw.rect(mask_surf, (255, 255, 255, 255),
                             mask_surf.get_rect(), border_radius=6)
            img = img.copy()
            img.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(img, inner.topleft)
            pygame.draw.rect(surf, GOLD, inner, 2, border_radius=6)
            return

        pygame.draw.rect(surf, DARK_RED, rect, border_radius=radius)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surf, RED, inner, border_radius=6)
        pattern = pygame.Surface(inner.size, pygame.SRCALPHA)
        for k in range(-inner.h, inner.w, 14):
            pygame.draw.line(pattern, (0, 0, 0, 28),
                             (k, 0), (k + inner.h, inner.h), 4)
        surf.blit(pattern, inner.topleft)
        pygame.draw.rect(surf, GOLD, inner, 2, border_radius=6)
        mask_rect = pygame.Rect(0, 0, int(inner.w * 0.78), int(inner.h * 0.72))
        mask_rect.center = inner.center
        self.draw_mask(surf, mask_rect)

    def draw_mask(self, surf, rect, alpha=255):
        if rect.w <= 0 or rect.h <= 0:
            return

        if self.mask_img is not None:
            key = (rect.w, rect.h)
            scaled = self._mask_cache.get(key)
            if scaled is None:
                iw, ih = self.mask_img.get_size()
                scale = min(rect.w / iw, rect.h / ih)
                new_w = max(1, int(iw * scale))
                new_h = max(1, int(ih * scale))
                scaled = pygame.transform.smoothscale(
                    self.mask_img, (new_w, new_h))
                self._mask_cache[key] = scaled

            x = rect.x + (rect.w - scaled.get_width()) // 2
            y = rect.y + (rect.h - scaled.get_height()) // 2

            if alpha >= 255:
                surf.blit(scaled, (x, y))
            else:
                tmp = scaled.copy()
                tmp.set_alpha(alpha)
                surf.blit(tmp, (x, y))
            return

        face_color = CREAM
        line_color = BLACK
        w, h = rect.w, rect.h
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        lcx, lcy = w // 2, h // 2
        face = pygame.Rect(0, 0, int(w * 0.66), int(h * 0.68))
        face.center = (lcx, lcy + int(h * 0.02))
        pygame.draw.ellipse(layer, face_color, face)
        er = max(2, int(w * 0.045))
        for dx in (-1, 1):
            ex = lcx + dx * int(w * 0.14)
            ey = lcy - int(h * 0.06)
            pygame.draw.ellipse(layer, line_color,
                                (ex - er, ey - int(er * 1.3),
                                 er * 2, int(er * 2.6)))
        for dx in (-1, 1):
            ex = lcx + dx * int(w * 0.14)
            ey = lcy - int(h * 0.17)
            pygame.draw.line(layer, line_color,
                             (ex - dx * er * 1.6, ey - er * 0.6),
                             (ex + dx * er * 0.4, ey - er * 1.3), 2)
        pygame.draw.line(layer, line_color,
                         (lcx, lcy - int(h * 0.01)),
                         (lcx, lcy + int(h * 0.05)), 2)
        for dx in (-1, 1):
            pts = []
            x0, y0 = lcx + dx * w * 0.03, lcy + h * 0.14
            x1, y1 = lcx + dx * w * 0.19, lcy + h * 0.26
            x2, y2 = lcx + dx * w * 0.31, lcy + h * 0.01
            for i in range(14):
                t = i / 13.0
                x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2
                y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2
                pts.append((x, y))
            pygame.draw.lines(layer, line_color, False, pts, 4)
        if alpha < 255:
            layer.set_alpha(alpha)
        surf.blit(layer, rect.topleft)

    def draw_suit(self, surf, suit, cx, cy, size, color):
        cx, cy = int(cx), int(cy)
        s = size
        if suit == DIAMONDS:
            pts = [(cx, cy - s * 0.5), (cx + s * 0.36, cy),
                   (cx, cy + s * 0.5), (cx - s * 0.36, cy)]
            pygame.draw.polygon(surf, color, pts)
        elif suit == HEARTS:
            r = s * 0.27
            top_y = cy - r * 0.55
            lx = cx - r * 0.9
            rx = cx + r * 0.9
            pygame.draw.circle(surf, color, (int(lx), int(top_y)), int(r))
            pygame.draw.circle(surf, color, (int(rx), int(top_y)), int(r))
            pygame.draw.polygon(surf, color, [
                (lx - r * 0.5, top_y + r * 0.55),
                (rx + r * 0.5, top_y + r * 0.55),
                (cx, cy + s * 0.5)])
        elif suit == SPADES:
            r = s * 0.27
            bot_y = cy + r * 0.55
            lx = cx - r * 0.9
            rx = cx + r * 0.9
            pygame.draw.circle(surf, color, (int(lx), int(bot_y)), int(r))
            pygame.draw.circle(surf, color, (int(rx), int(bot_y)), int(r))
            pygame.draw.polygon(surf, color, [
                (lx - r * 0.5, bot_y - r * 0.55),
                (rx + r * 0.5, bot_y - r * 0.55),
                (cx, cy - s * 0.5)])
            pygame.draw.polygon(surf, color, [
                (cx - r * 0.28, bot_y + r * 0.2),
                (cx + r * 0.28, bot_y + r * 0.2),
                (cx + r * 0.85, cy + s * 0.5),
                (cx - r * 0.85, cy + s * 0.5)])
        else:
            r = s * 0.26
            pygame.draw.circle(surf, color, (cx, int(cy - r * 1.05)), int(r))
            pygame.draw.circle(surf, color,
                               (int(cx - r * 0.9), int(cy + r * 0.5)), int(r))
            pygame.draw.circle(surf, color,
                               (int(cx + r * 0.9), int(cy + r * 0.5)), int(r))
            pygame.draw.polygon(surf, color, [
                (cx - r * 0.28, cy + r * 0.6),
                (cx + r * 0.28, cy + r * 0.6),
                (cx + r * 0.85, cy + s * 0.5),
                (cx - r * 0.85, cy + s * 0.5)])

    def draw_recycle_icon(self, surf, rect):
        cx, cy = rect.center
        r = 17
        pygame.draw.arc(surf, (215, 180, 165),
                        (cx - r, cy - r, 2 * r, 2 * r), 0.5, 5.3, 3)
        ang = 5.3
        ex, ey = cx + r * math.cos(ang), cy - r * math.sin(ang)
        pygame.draw.polygon(surf, (215, 180, 165), [
            (ex + 3, ey - 8), (ex + 9, ey + 2), (ex - 3, ey + 2)])

    def draw_character_badge(self, surf, rect, key, color):
        photo = self.get_char_photo(key)
        pygame.draw.rect(surf, (18, 5, 8), rect, border_radius=8)
        if photo is not None:
            pygame.draw.rect(surf, color, rect, 2, border_radius=8)
            inner = rect.inflate(-6, -6)
            small = pygame.transform.smoothscale(photo, inner.size)
            surf.blit(small, inner.topleft)
        else:
            pygame.draw.rect(surf, color, rect, 2, border_radius=8)
            m = rect.inflate(-10, -10)
            self.draw_mask(surf, m)

    def draw_header(self):
        cx = (self.waste_rect().right +
              self.foundation_rect(0).left) // 2

        plate = pygame.Surface((360, 150), pygame.SRCALPHA)
        plate.fill((20, 5, 8, 110))
        self.screen.blit(plate, plate.get_rect(center=(cx, TOP_Y + 65)))

        mask_rect = pygame.Rect(0, 0, 78, 78)
        mask_rect.center = (cx, TOP_Y + 42)
        self.draw_mask(self.screen, mask_rect)

        title = self.f_title.render("LA CASA DE PAPEL", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(cx, TOP_Y + 100)))

        sub = self.f_sub.render("П А С Ь Я Н С", True, (210, 165, 150))
        self.screen.blit(sub, sub.get_rect(center=(cx, TOP_Y + 132)))

    def draw_professor_strip(self):
        panel = pygame.Surface((WIDTH, PROF_H + 14), pygame.SRCALPHA)
        panel.fill((14, 4, 6, 200))
        self.screen.blit(panel, (0, PROF_Y - 7))

        pygame.draw.line(self.screen, (110, 70, 40),
                         (0, PROF_Y - 7), (WIDTH, PROF_Y - 7), 1)
        pygame.draw.line(self.screen, (110, 70, 40),
                         (0, PROF_Y + PROF_H + 7),
                         (WIDTH, PROF_Y + PROF_H + 7), 1)

        self.professor.draw(self.screen)

    def draw_footer(self):
        bar = pygame.Surface((WIDTH, FOOTER_H), pygame.SRCALPHA)
        bar.fill((16, 4, 7, 220))
        self.screen.blit(bar, (0, FOOTER_Y))
        pygame.draw.line(self.screen, GOLD, (0, FOOTER_Y), (WIDTH, FOOTER_Y), 1)

        name, en_name, key, quote, color = self.current_hero()

        badge = pygame.Rect(MARGIN, FOOTER_Y + 15, CHAR_SIZE, CHAR_SIZE)
        self.draw_character_badge(self.screen, badge, key, color)

        name_surf = self.f_hero.render(name, True, color)
        self.screen.blit(name_surf, (badge.right + 15, FOOTER_Y + 20))

        quote_surf = self.f_quote.render(f'«{quote}»', True, QUOTE_COL)
        self.screen.blit(quote_surf, (badge.right + 15, FOOTER_Y + 54))

        if self.won:
            secs = self.win_time
        else:
            secs = (pygame.time.get_ticks() - self.start_time) // 1000
        mm, ss = divmod(secs, 60)

        stats = self.f_med.render(
            f"Ходы: {self.moves}      Время: {mm:02d}:{ss:02d}",
            True, (210, 178, 160))
        self.screen.blit(stats,
                         (WIDTH - MARGIN - stats.get_width(),
                          FOOTER_Y + 30))

        hint = self.f_tiny.render("N — новая      ESC — выход",
                                  True, (140, 100, 100))
        self.screen.blit(hint,
                         (WIDTH - MARGIN - hint.get_width(),
                          FOOTER_Y + 70))

    def draw_drag_cards(self):
        if not self.drag_cards:
            return
        mx, my = self.drag_mouse
        ox, oy = self.drag_off
        x = mx - ox
        y = my - oy

        kind, pi, ci = self.drag_src
        if kind == 'tableau':
            ys = self.pile_ys(self.tableau[pi])
            base = ys[ci]
            for i, c in enumerate(self.drag_cards):
                dy = ys[ci + i] - base
                r = pygame.Rect(x, y + dy, CARD_W, CARD_H)
                self.draw_card_front(self.screen, c, r)
        else:
            for i, c in enumerate(self.drag_cards):
                r = pygame.Rect(x, y + i * 24, CARD_W, CARD_H)
                self.draw_card_front(self.screen, c, r)

    def draw_win(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 190))
        self.screen.blit(ov, (0, 0))

        name, en_name, key, quote, color = self.current_hero()
        photo = self.get_char_photo(key)
        photo_size = 170
        photo_rect = pygame.Rect(0, 0, photo_size, photo_size)
        photo_rect.center = (WIDTH // 2, HEIGHT // 2 - 180)
        pygame.draw.rect(self.screen, (18, 5, 8), photo_rect, border_radius=12)
        pygame.draw.rect(self.screen, color, photo_rect, 3, border_radius=12)
        if photo is not None:
            inner = photo_rect.inflate(-8, -8)
            big = pygame.transform.smoothscale(photo, inner.size)
            self.screen.blit(big, inner.topleft)
        else:
            self.draw_mask(self.screen, photo_rect.inflate(-20, -20))

        t1 = self.f_big.render("ПЛАН ВЫПОЛНЕН", True, GOLD)
        t2 = self.f_title.render("BELLA CIAO!", True, RED_LIGHT)
        t3 = self.f_sub.render("Нажмите N, чтобы начать заново", True, CREAM)

        self.screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
        self.screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        q1 = self.f_hero.render(f"{name}:", True, color)
        q2 = self.f_quote.render(f'«{quote}»', True, QUOTE_COL)
        self.screen.blit(q1, q1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)))
        self.screen.blit(q2, q2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))

        self.screen.blit(t3, t3.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

    def draw(self):
        self.draw_background()
        self.draw_professor_strip()

        if self.stock:
            self.draw_card_back(self.screen, self.stock_rect())
        else:
            self.draw_slot(self.screen, self.stock_rect())
            self.draw_recycle_icon(self.screen, self.stock_rect())

        wr = self.waste_rect()
        if self.waste and not self.is_dragged('waste', 0, 0):
            self.draw_card_front(self.screen, self.waste[-1], wr)
            if self.selected == ('waste', 0, len(self.waste) - 1):
                pygame.draw.rect(self.screen, GOLD, wr, 3, border_radius=9)
        elif not self.waste:
            self.draw_slot(self.screen, wr)

        for i in range(4):
            r = self.foundation_rect(i)
            if self.foundations[i] and not self.is_dragged('foundation', i, 0):
                self.draw_card_front(self.screen,
                                     self.foundations[i][-1], r)
                if self.selected == ('foundation', i,
                                     len(self.foundations[i]) - 1):
                    pygame.draw.rect(self.screen, GOLD, r, 3, border_radius=9)
            elif not self.foundations[i]:
                self.draw_slot(self.screen, r, suit=i)

        for i in range(7):
            pile = self.tableau[i]
            x = self.tableau_x(i)
            if not pile:
                self.draw_slot(self.screen,
                               pygame.Rect(x, TABLEAU_Y, CARD_W, CARD_H))
                continue
            ys = self.pile_ys(pile)
            for j, c in enumerate(pile):
                if self.is_dragged('tableau', i, j):
                    continue
                r = pygame.Rect(x, TABLEAU_Y + ys[j], CARD_W, CARD_H)
                if c.face_up:
                    self.draw_card_front(self.screen, c, r)
                    if (self.selected == ('tableau', i, j)
                            and self.drag_src is None):
                        pygame.draw.rect(self.screen, GOLD, r, 3,
                                         border_radius=9)
                else:
                    self.draw_card_back(self.screen, r)

        self.draw_header()
        self.draw_footer()

        if self.drag_src and self.drag_moved:
            self.draw_drag_cards()

        if self.won:
            self.draw_win()

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if (event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1):
                    self.handle_mousedown(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mousemotion(event.pos)
                elif (event.type == pygame.MOUSEBUTTONUP
                        and event.button == 1):
                    self.handle_mouseup(event.pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_n:
                        self.new_game()

            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Solitaire().run()