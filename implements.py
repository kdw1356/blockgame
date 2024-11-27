import math
import random
import time

import config

import pygame
from pygame.locals import Rect, K_LEFT, K_RIGHT


class Basic:
    def __init__(self, color: tuple, speed: int = 0, pos: tuple = (0, 0), size: tuple = (0, 0)):
        self.color = color
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.center = (self.rect.centerx, self.rect.centery)
        self.speed = speed
        self.start_time = time.time()
        self.dir = 270

    def move(self):
        dx = math.cos(math.radians(self.dir)) * self.speed
        dy = -math.sin(math.radians(self.dir)) * self.speed
        self.rect.move_ip(dx, dy)
        self.center = (self.rect.centerx, self.rect.centery)


class Block(Basic):
    def __init__(self, color: tuple, pos: tuple = (0,0), alive = True):
        super().__init__(color, 0, pos, config.block_size)
        self.pos = pos
        self.alive = alive

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
    
    def collide(self):
        self.alive = False
        


class Paddle(Basic):
    def __init__(self):
        super().__init__(config.paddle_color, 0, config.paddle_pos, config.paddle_size)
        self.start_pos = config.paddle_pos
        self.speed = config.paddle_speed
        self.cur_size = config.paddle_size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_paddle(self, event: pygame.event.Event):
        if event.key == K_LEFT and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        elif event.key == K_RIGHT and self.rect.right < config.display_dimension[0]:
            self.rect.move_ip(self.speed, 0)


class Ball(Basic):
    def __init__(self, pos: tuple = config.ball_pos):
        super().__init__(config.ball_color, config.ball_speed, pos, config.ball_size)
        self.power = 1
        self.dir = 90 + random.randint(-45, 45)

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_block(self, blocks: list):
 
        def absolute_value(x):
            return x if x >= 0 else -x

        for block in blocks[:]:
            if self.rect.colliderect(block.rect):
                block.collide()  
                if not block.alive:
                    blocks.remove(block)   # 블록제거

                # 가로면/세로면 충돌시 계산
                if absolute_value(self.rect.bottom - block.rect.top) < self.speed or absolute_value(self.rect.top - block.rect.bottom) < self.speed:
                    self.dir = (360 - self.dir) % 360
                else:
                    self.dir = (180 - self.dir) % 360
                return



    def collide_paddle(self, paddle: Paddle) -> None:
        if self.rect.colliderect(paddle.rect):
            self.dir = 360 - self.dir + random.randint(-5, 5)

    
    def hit_wall(self):
        screen_length, screen_breadth = config.display_dimension
        hit_increase = 0.1  # 벽 충돌 시 속도 증가량

        # 좌우 벽 충돌 (수평)
        if self.rect.left <= 0 or self.rect.right >= screen_length:
            self.dir = (180 - self.dir) % 360  
            self.speed += hit_increase  

        # 상단 벽 충돌 (수직)
        if self.rect.top <= 0:
            self.dir = (360 - self.dir) % 360  
            self.speed += hit_increase  

        # 공이 너무 빨라지지 않도록 제한
        max_speed = config.display_dimension[1] / 50
        self.speed = min(self.speed, max_speed)


    def alive(self):
        screen_length = config.display_dimension[1]

        if self.rect.top > screen_length:   # 공이 아래로 빠졌을떄
            return False  
        
        return True  # 공이 빠지지 않았을 때