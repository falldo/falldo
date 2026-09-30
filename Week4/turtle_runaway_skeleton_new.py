# This example is not working in Spyder directly (F5 or Run)
# Please type '!python turtle_runaway.py' on IPython console in your Spyder.
import tkinter as tk
import turtle, random, math

class RunawayGame:
    # 게임 객체와 설정값 초기화
    def __init__(self, canvas, runner, catch_radius=20):
        self.canvas = canvas
        #self.chaser = chaser 
        self.runner = runner
        self.chasers = [] # 시간마다 추가되는 추격자
        self.bullets = []
        self.catch_radius2 = catch_radius**2
        self.catch_radius = catch_radius
        self.render_radius = 350
        self.despawn_radius2 = 1000**2
        self.max_chasers = 150 # 추적자 최대 수 (늘리면 프레임 드랍 발생...)
        self.chaser_collision_radius = 30
        self.chaser_collision_radius2 = self.chaser_collision_radius**2
        self.ai_frame = 0
        self.arena_start_half_size = 1500
        self.arena_min_half_size = 350
        self.arena_half_size = self.arena_start_half_size
        self.poison_zones = []
        self.poison_spawn_cooltime = 3000
        self.poison_warning_duration = 2000
        self.poison_duration = 8000
        self.poison_radius = 120
        self.game_state = 'title'
        self.paused_turtles = []
        self.fire_cooldown = 200 # 총알 발사 쿨타임 (빠르게 하고 싶으면 줄이면 됨.)
        self.fire_timer = 0
        self.is_firing = False
        self.aim_angle = 0
        self.lives = 3 # 목숨수
        self.invincible_duration = 1000 # 무적 프레임(1초)
        self.invincible_timer = 0
        self.score = 0
        self.tk_canvas = self.canvas.getcanvas()

        # 마우스 조준 화살표
        self.aim_arrow = turtle.RawTurtle(canvas)
        self.aim_arrow.shape('arrow')
        self.aim_arrow.color('black')
        self.aim_arrow.penup()

        
        self.life_icon = turtle.RawTurtle(canvas)
        self.life_icon.shape('turtle')
        self.life_icon.color('green')
        self.life_icon.penup()
        self.life_icon.hideturtle()

        # 거북이 목숨
        self.life_icons = []
        for _ in range(3):
            icon = turtle.RawTurtle(canvas)
            icon.shape('turtle')
            icon.color('green')
            icon.setheading(90)
            icon.penup()
            icon.hideturtle()
            self.life_icons.append(icon)

        #아레나 구역 
        self.arena_drawer = turtle.RawTurtle(canvas)
        self.arena_drawer.hideturtle()
        self.arena_drawer.color('black')
        self.arena_drawer.pensize(4)
        self.arena_drawer.penup()

        # Initialize 'runner' and 'chaser'
        # self.chaser.shape('turtle')
        # self.chaser.color('blue')
        # self.chaser.penup()

        self.runner.shape('turtle')
        self.runner.color('green')
        self.runner.penup()

        self.drawer = turtle.RawTurtle(canvas)
        self.drawer.hideturtle()
        self.drawer.penup()

        # 남은 시간 
        self.drawer2 = turtle.RawTurtle(canvas)
        self.drawer2.hideturtle()
        self.drawer2.penup()

        # 개체수 
        self.drawer3 = turtle.RawTurtle(canvas)
        self.drawer3.hideturtle()
        self.drawer3.penup()

        # 점수 
        self.drawer4 = turtle.RawTurtle(canvas)
        self.drawer4.hideturtle()
        self.drawer4.penup()

        # 일시정지
        self.overlay_background = turtle.RawTurtle(canvas)
        self.overlay_background.shape('square')
        self.overlay_background.color('white')
        self.overlay_background.shapesize(35, 35)
        self.overlay_background.penup()
        self.overlay_background.hideturtle()

        # 타이틀
        self.overlay_drawer = turtle.RawTurtle(canvas)
        self.overlay_drawer.hideturtle()
        self.overlay_drawer.penup()
        self.overlay_items = []

    def clear_ui(self):
        for item in self.overlay_items:
            self.tk_canvas.delete(item)
        self.overlay_items = []

    def add_text(self, x, y, text, font):
        self.overlay_items.append(self.tk_canvas.create_text(x, -y, text=text, fill='black', font=font))

    def show_title(self):
        self.runner.hideturtle()
        self.aim_arrow.hideturtle()
        self.life_icon.hideturtle()
        for icon in self.life_icons:
            icon.hideturtle()
        self.clear_ui()
        self.add_text(0, 80, 'TURTLE RUNAWAY', ('Arial', 28, 'bold'))
        self.add_text(0, 20, 'Press Enter to Start', ('Arial', 16, 'normal'))
        self.add_text(0, -20, 'WSAD: 상/하/좌/우 이동   마우스 / 클릭: Aim / Shoot   ESC: Pause', ('Arial', 12, 'normal'))

    # 일시정지 창 표시
    def show_pause(self):
        self.overlay_background.hideturtle()
        self.hide_pause_area()
        for zone in self.poison_zones:
            zone['turtle'].hideturtle()
            zone['warning_turtle'].hideturtle()
            self.tk_canvas.itemconfigure(zone['warning_text'], state='hidden')
        self.clear_ui()
        self.overlay_items.append(self.tk_canvas.create_rectangle(-180, -100, 180, 100, fill='white', outline='black', width=3))
        self.add_text(0, 20, 'PAUSED', ('Arial', 28, 'bold'))
        self.add_text(0, -25, 'Press ESC to Resume', ('Arial', 16, 'normal'))


    def hide_pause_area(self):
        self.paused_turtles = []

        # 중앙 창 범위 안의 객체만 숨김
        def hide_if_in_window(obj, x, y):
            if obj.isvisible() and abs(x) <= 220 and abs(y) <= 140:
                obj.hideturtle()
                self.paused_turtles.append(obj)

        runner_x, runner_y = self.runner.pos()
        hide_if_in_window(self.runner, runner_x, runner_y)
        aim_x, aim_y = self.aim_arrow.pos()
        hide_if_in_window(self.aim_arrow, aim_x, aim_y)
        for chaser in self.chasers:
            hide_if_in_window(chaser, chaser.absolutePos[0] + self.runner.cameraPos[0], chaser.absolutePos[1] + self.runner.cameraPos[1])
        for bullet in self.bullets:
            hide_if_in_window(bullet, bullet.absolutePos[0] + self.runner.cameraPos[0], bullet.absolutePos[1] + self.runner.cameraPos[1])
        for zone in self.poison_zones:
            hide_if_in_window(zone['turtle'], zone['x'] + self.runner.cameraPos[0], zone['y'] + self.runner.cameraPos[1])

    # 게임오버 화면 표시
    def show_game_over(self):
        self.hide_pause_area()
        for zone in self.poison_zones:
            zone['turtle'].hideturtle()
            zone['warning_turtle'].hideturtle()
            self.tk_canvas.itemconfigure(zone['warning_text'], state='hidden')
        self.clear_ui()
        self.overlay_items.append(self.tk_canvas.create_rectangle(-180, -100, 180, 100, fill='white', outline='black', width=3))
        self.add_text(0, 40, 'GAME OVER', ('Arial', 30, 'bold'))
        self.add_text(0, -10, f'Score: {self.score}', ('Arial', 18, 'normal'))
        self.add_text(0, -55, 'Press Enter for Title', ('Arial', 14, 'normal'))

    # 게임 클리어 화면 표시
    def show_clear(self):
        self.hide_pause_area()
        self.clear_ui()
        self.overlay_items.append(self.tk_canvas.create_rectangle(-180, -100, 180, 100, fill='white', outline='black', width=3))
        self.add_text(0, 40, 'CLEAR!', ('Arial', 30, 'bold'))
        self.add_text(0, -10, f'Score: {self.score}', ('Arial', 18, 'normal'))
        self.add_text(0, -55, 'Press Enter for Title', ('Arial', 14, 'normal'))

    # 남은 목숨 아이콘 표시
    def update_lives(self):
        for index, icon in enumerate(self.life_icons):
            icon.setpos(-300 + index * 35, 300)
            icon.color('green' if index < self.lives else 'black')
            icon.showturtle()

    def raise_ui(self):
        for obj in [self.runner, self.aim_arrow, *self.life_icons]:
            item = obj.turtle._item
            if isinstance(item, list):
                for part in item:
                    self.tk_canvas.tag_raise(part)
            else:
                self.tk_canvas.tag_raise(item)
        for drawer in [self.drawer, self.drawer2, self.drawer3, self.drawer4]:
            for item in drawer.items:
                self.tk_canvas.tag_raise(item)

    def lower_zones(self):
        for zone in self.poison_zones:
            for zone_turtle in [zone['turtle'], zone['warning_turtle']]:
                item = zone_turtle.turtle._item
                if isinstance(item, list):
                    for part in item:
                        self.tk_canvas.tag_lower(part)
                else:
                    self.tk_canvas.tag_lower(item)

    # 경고 느낌표 추가
    def raise_warnings(self):
        for zone in self.poison_zones:
            if zone['warning_timer'] > 0 and (zone['warning_timer'] // 200) % 2 == 0:
                self.tk_canvas.tag_raise(zone['warning_text'])

    # Enter키 입력받아서 타이틀로 가기
    def enter_game(self):
        if self.game_state == 'title':
            self.game_state = 'playing'
            self.clear_ui()
            self.runner.showturtle()
        elif self.game_state in ('game_over', 'clear'):
            self.reset_title()

    # 게임 초기화하고 타이틀로
    def reset_title(self):
        for chaser in self.chasers:
            chaser.hideturtle()
        for bullet in self.bullets:
            bullet.hideturtle()
        for zone in self.poison_zones:
            zone['turtle'].hideturtle()
            zone['warning_turtle'].hideturtle()
            self.tk_canvas.delete(zone['warning_text'])
        self.chasers = []
        self.bullets = []
        self.poison_zones = []
        self.lives = 3
        self.score = 0
        self.timer = self.initial_timer
        self.spawnCooltime = 50  
        self.fire_timer = 0
        self.is_firing = False
        self.runner.cameraPos = [0, 0]
        self.runner.setpos(0, 0)
        self.arena_drawer.clear()
        self.drawer.clear()
        self.drawer2.clear()
        self.drawer3.clear()
        self.drawer4.clear()
        self.game_state = 'title'
        self.show_title()

    # 일시정지 전환 toggle
    def pause_game(self):
        if self.game_state == 'playing':
            self.game_state = 'paused'
            self.is_firing = False
            self.show_pause()
        elif self.game_state == 'paused':
            self.game_state = 'playing'
            self.overlay_background.hideturtle()
            self.clear_ui()
            for obj in self.paused_turtles:
                obj.showturtle()
            self.paused_turtles = []

    # 플레이어와 적의 collision 체크
    def is_catched(self):
        for i in self.chasers:
            p = i.absolutePos
            q = [-self.runner.cameraPos[0], -self.runner.cameraPos[1]]
            dx, dy = p[0] - q[0], p[1] - q[1]
            if dx**2 + dy**2 < self.catch_radius2:
                return True
        return False

    # 겹치면 밀기
    def resolve_collisions(self):
        # 맵을 작은 칸으로 divide 함
        cells = {}
        for enemy in self.chasers:
            cell_x = math.floor(enemy.absolutePos[0] / self.chaser_collision_radius)
            cell_y = math.floor(enemy.absolutePos[1] / self.chaser_collision_radius)
            for near_x in range(cell_x - 1, cell_x + 2):
                for near_y in range(cell_y - 1, cell_y + 2):
                    for other in cells.get((near_x, near_y), []):
                        dx = enemy.absolutePos[0] - other.absolutePos[0]
                        dy = enemy.absolutePos[1] - other.absolutePos[1]
                        dist2 = dx**2 + dy**2
                        if dist2 < self.chaser_collision_radius2:
                            if dist2 == 0:
                                dx, dy = 1, 0
                                dist2 = 1
                            dist = math.sqrt(dist2)
                            push = (self.chaser_collision_radius - dist) / 2
                            enemy.absolutePos[0] += dx / dist * push
                            enemy.absolutePos[1] += dy / dist * push
                            other.absolutePos[0] -= dx / dist * push
                            other.absolutePos[1] -= dy / dist * push
            cells.setdefault((cell_x, cell_y), []).append(enemy)

    # 플레이어에서 먼 적을 가까운 곳으로 보내기(뭉치기 방지용)
    def remove_far_enemy(self):
        player_x = -self.runner.cameraPos[0]
        player_y = -self.runner.cameraPos[1]
        far_enemy = max(self.chasers, key=lambda enemy: (enemy.absolutePos[0] - player_x)**2 + (enemy.absolutePos[1] - player_y)**2)
        far_enemy.hideturtle()
        self.chasers.remove(far_enemy)

    # 남은 시간에 맞춰 아레나 축소
    def update_arena(self):
        ratio = min(1, (self.initial_timer - self.timer) / self.initial_timer)
        self.arena_half_size = self.arena_start_half_size - (self.arena_start_half_size - self.arena_min_half_size) * ratio
        player_x = max(-self.arena_half_size, min(self.arena_half_size, -self.runner.cameraPos[0]))
        player_y = max(-self.arena_half_size, min(self.arena_half_size, -self.runner.cameraPos[1]))
        self.runner.cameraPos = [-player_x, -player_y]

    # 카메라 위치에 맞춰 아레나 테두리 draw
    def draw_arena(self):
        left = -self.arena_half_size + self.runner.cameraPos[0]
        right = self.arena_half_size + self.runner.cameraPos[0]
        bottom = -self.arena_half_size + self.runner.cameraPos[1]
        top = self.arena_half_size + self.runner.cameraPos[1]
        self.arena_drawer.clear()
        self.arena_drawer.penup()
        self.arena_drawer.setpos(left, bottom)
        self.arena_drawer.pendown()
        self.arena_drawer.goto(right, bottom)
        self.arena_drawer.goto(right, top)
        self.arena_drawer.goto(left, top)
        self.arena_drawer.goto(left, bottom)
        self.arena_drawer.penup()

    # 플레이어 주변에 무작위 독 구역 생성됨
    def spawn_zone(self):
        player_x = -self.runner.cameraPos[0]
        player_y = -self.runner.cameraPos[1]
        radius = random.randint(self.poison_radius, self.poison_radius + 100)
        limit = self.arena_half_size - radius
        # 플레이어와 너무 가까운 위치는 안되게 함.
        for _ in range(20):
            angle = random.uniform(-math.pi, math.pi)
            distance = random.uniform(250, 400)
            zone_x = max(-limit, min(limit, player_x + distance * math.cos(angle)))
            zone_y = max(-limit, min(limit, player_y + distance * math.sin(angle)))
            if (zone_x - player_x)**2 + (zone_y - player_y)**2 >= 250**2:
                break
        #독 장판 ui
        zone_drawer = turtle.RawTurtle(self.canvas)
        zone_drawer.shape('circle')
        zone_drawer.shapesize(radius / 10, radius / 10)
        zone_drawer.penup()
        #경고 ui
        warn_drawer = turtle.RawTurtle(self.canvas)
        warn_drawer.shape('circle')
        warn_drawer.color('orange')
        warn_drawer.shapesize(radius / 10, radius / 10)
        warn_drawer.penup()
        warn_text = self.tk_canvas.create_text(0, 0, text='!', fill='black', font=('Arial', int(radius / 2), 'bold'))
        self.poison_zones.append({'x': zone_x, 'y': zone_y, 'radius': radius, 'warning_timer': self.poison_warning_duration, 'duration': self.poison_duration, 'turtle': zone_drawer, 'warning_turtle': warn_drawer, 'warning_text': warn_text})

    def update_zones(self):
        active = []
        player_x = -self.runner.cameraPos[0]
        player_y = -self.runner.cameraPos[1]
        in_zone = False
        for zone in self.poison_zones:
            zone['warning_timer'] = max(0, zone['warning_timer'] - self.ai_timer_msec)
            if zone['warning_timer'] == 0:
                zone['duration'] -= self.ai_timer_msec
            if zone['duration'] <= 0 or abs(zone['x']) > self.arena_half_size + zone['radius'] or abs(zone['y']) > self.arena_half_size + zone['radius']:
                zone['turtle'].hideturtle()
                zone['warning_turtle'].hideturtle()
                self.tk_canvas.itemconfigure(zone['warning_text'], state='hidden')
                continue
            screen_x = zone['x'] + self.runner.cameraPos[0]
            screen_y = zone['y'] + self.runner.cameraPos[1]
            if abs(screen_x) <= self.render_radius + zone['radius'] and abs(screen_y) <= self.render_radius + zone['radius']:
                zone['turtle'].setpos(screen_x, screen_y)
                self.tk_canvas.tag_lower(zone['turtle'].turtle._item)
                # 경고 중에는 주황 원과 느낌표 깜빡거림
                if zone['warning_timer'] > 0:
                    zone['turtle'].hideturtle()
                    zone['warning_turtle'].setpos(screen_x, screen_y)
                    self.tk_canvas.coords(zone['warning_text'], screen_x, -screen_y)
                    if (zone['warning_timer'] // 200) % 2 == 0:
                        zone['warning_turtle'].showturtle()
                        self.tk_canvas.itemconfigure(zone['warning_text'], state='normal')
                        self.tk_canvas.tag_raise(zone['warning_text'])
                    else:
                        zone['warning_turtle'].hideturtle()
                        self.tk_canvas.itemconfigure(zone['warning_text'], state='hidden')
                # 경고가 끝나면 보라색 독 구역 생기게 함.
                else:
                    zone['warning_turtle'].hideturtle()
                    self.tk_canvas.itemconfigure(zone['warning_text'], state='hidden')
                    zone['turtle'].color('purple')
                    zone['turtle'].showturtle()
                    if (zone['x'] - player_x)**2 + (zone['y'] - player_y)**2 < zone['radius']**2:
                        in_zone = True
            else:
                zone['turtle'].hideturtle()
                zone['warning_turtle'].hideturtle()
                self.tk_canvas.itemconfigure(zone['warning_text'], state='hidden')
            active.append(zone)
        self.poison_zones = active
        self.raise_ui()
        return in_zone

    # 조준 방향으로 총알 한 발 발사
    def fire(self):
        if self.game_state != 'playing' or self.fire_timer > 0:
            return
        bullet = bulletMover(self.canvas)
        bullet.shape('circle')
        bullet.shapesize(0.4, 0.4)
        bullet.color('black')
        bullet.penup()
        bullet.absolutePos = [-self.runner.cameraPos[0], -self.runner.cameraPos[1]]
        bullet.setheading(self.aim_angle)
        bullet.setpos(self.runner.pos())
        self.bullets.append(bullet)
        self.fire_timer = self.fire_cooldown

    # 마우스 방향으로 조준 화살표 이동
    def update_aim(self, event):
        if self.game_state != 'playing':
            return
        mouse_x = self.tk_canvas.canvasx(event.x) / self.canvas.xscale
        mouse_y = -self.tk_canvas.canvasy(event.y) / self.canvas.yscale
        runner_x, runner_y = self.runner.pos()
        self.aim_angle = math.degrees(math.atan2(mouse_y - runner_y, mouse_x - runner_x))
        self.aim_arrow.setheading(self.aim_angle)
        self.aim_arrow.setpos(runner_x + 25 * math.cos(math.radians(self.aim_angle)), runner_y + 25 * math.sin(math.radians(self.aim_angle)))
        self.aim_arrow.showturtle()

    # 마우스 클릭 시 연사 시작
    def start_fire(self, event):
        if self.game_state != 'playing':
            return
        self.update_aim(event)
        self.is_firing = True
        self.fire()

    # 마우스 버튼을 놓으면 연사 중지
    def stop_fire(self, event):
        self.is_firing = False

    # 총알 이동과 적 피격 처리
    def update_shots(self):
        active = []
        for bullet in self.bullets:
            bullet.run_ai()
            screen_x = bullet.absolutePos[0] + self.runner.cameraPos[0]
            screen_y = bullet.absolutePos[1] + self.runner.cameraPos[1]
            if screen_x**2 + screen_y**2 > self.despawn_radius2:
                bullet.hideturtle()
                continue
            hit_enemy = None
            # 총알과 가장 먼저 닿은 적 확인
            for chaser in self.chasers:
                dx = bullet.absolutePos[0] - chaser.absolutePos[0]
                dy = bullet.absolutePos[1] - chaser.absolutePos[1]
                if dx**2 + dy**2 < self.catch_radius2:
                    hit_enemy = chaser
                    break
            if hit_enemy is not None:
                hit_enemy.health -= 1
                if hit_enemy.health == 0:
                    self.score += {'blue': 1, 'yellow': 5, 'red': 10}[hit_enemy.color()[0]]
                    hit_enemy.hideturtle()
                    self.chasers.remove(hit_enemy)
                bullet.hideturtle()
                continue
            if abs(screen_x) <= self.render_radius and abs(screen_y) <= self.render_radius:
                bullet.setpos(screen_x, screen_y)
                active.append(bullet)
            else:
                bullet.hideturtle()
                active.append(bullet)
        self.bullets = active

    # 무적 시간 동안 플레이어 깜빡거리게 하는 기능
    def update_invincible(self):
        if self.game_state == 'game_over':
            self.runner.hideturtle()
            return
        if self.invincible_timer > 0:
            if (self.invincible_timer // 100) % 2 == 0:
                self.runner.showturtle()
            else:
                self.runner.hideturtle()
            self.invincible_timer = max(0, self.invincible_timer - self.ai_timer_msec)
        elif not self.runner.isvisible():
            self.runner.showturtle()

    # 게임 설정과 입력 이벤트 등록
    def start(self, init_dist=400, ai_timer_msec=10):
        # self.runner.setpos((-init_dist / 2, 0))
        # self.runner.setheading(0)
        # self.chaser.setpos((+init_dist / 2, 0))
        # self.chaser.setheading(180)


#################시간 혹은 거북이 쿨타임을 바꾸고 싶으면 여기서 바꾸시오#######################


        # TODO) You can do something here and follows.
        timer_set = 10 # minute
        self.timer = timer_set * 60 * 1000
        self.initial_timer = self.timer
        self.spawnCooltime = 500 # 거북이 쿨

        self.ai_timer_msec = ai_timer_msec
        self.tk_canvas.bind('<Motion>', self.update_aim)
        self.tk_canvas.bind('<ButtonPress-1>', self.start_fire)
        self.tk_canvas.bind('<ButtonRelease-1>', self.stop_fire)
        self.canvas.onkeypress(self.enter_game, 'Return')
        self.canvas.onkeypress(self.pause_game, 'Escape')
        self.canvas.listen()
        self.show_title()
        self.canvas.ontimer(self.step, self.ai_timer_msec)

    #게임 로직 실행
    def step(self):
        if self.game_state != 'playing':
            screen.update()
            self.canvas.ontimer(self.step, self.ai_timer_msec)
            return
        self.ai_frame += 1

        # spawnCooltime(현재 0.5초)마다 적 거북이 1마리 생성

        if self.timer % self.spawnCooltime == 0:
            if len(self.chasers) >= self.max_chasers:
                self.remove_far_enemy()
            chaserInf = ChaseMover(screen)
            chaserInf.shape('turtle')
            chaserInf.penup()
            chaser_type = random.choices([('blue', 1, 1.0), ('yellow', 3, 1.35), ('red', 5, 1.7)],weights=[60, 30, 10])[0]
            chaserInf.color(chaser_type[0])
            chaserInf.health = chaser_type[1]
            chaserInf.shapesize(chaser_type[2], chaser_type[2])

            # ai_timer_msec 마다 추적자 하나씩 추가
            self.chasers.append(chaserInf)

            #가운데 기준 원형 범위로 적 생성
            r = random.randint(350,450)
            if random.random() < 0.75:
                theta = math.radians(self.runner.heading() + random.randint(-45, 45))
            else:
                theta = math.radians(random.randint(-180, 180))
            x = r * math.cos(theta)
            y = r * math.sin(theta)

            self.chasers[-1].setpos((x, y))
            self.chasers[-1].absolutePos = [x - self.runner.cameraPos[0], y - self.runner.cameraPos[1]]
            self.chasers[-1].setheading(0)

        if self.timer % 60000 == 0:
            self.spawnCooltime = max(50,self.spawnCooltime - 50) # 1분마다 거북이 스폰 쿨 감소 (하한: 0.05초)

        if self.timer % self.poison_spawn_cooltime == 0:
            for _ in range(random.randint(2, 4)):
                self.spawn_zone()


        #모든 추격자와 도망자의 ai를 실행
        active_chasers = []
        for i in self.chasers:
            i.run_ai(self.runner, self.runner.heading())
            i.absolutePos[0] = max(-self.arena_half_size, min(self.arena_half_size, i.absolutePos[0]))
            i.absolutePos[1] = max(-self.arena_half_size, min(self.arena_half_size, i.absolutePos[1]))
            screen_x = i.absolutePos[0] + self.runner.cameraPos[0]
            screen_y = i.absolutePos[1] + self.runner.cameraPos[1]
            if screen_x**2 + screen_y**2 > self.despawn_radius2:
                if i.isvisible():
                    i.hideturtle()
            else:
                active_chasers.append(i)
        self.chasers = active_chasers

        self.resolve_collisions()
        for i in self.chasers:
            i.absolutePos[0] = max(-self.arena_half_size, min(self.arena_half_size, i.absolutePos[0]))
            i.absolutePos[1] = max(-self.arena_half_size, min(self.arena_half_size, i.absolutePos[1]))

        visible_chasers = []
        for i in self.chasers:
            screen_x = i.absolutePos[0] + self.runner.cameraPos[0]
            screen_y = i.absolutePos[1] + self.runner.cameraPos[1]
            if abs(screen_x) <= self.render_radius and abs(screen_y) <= self.render_radius:
                visible_chasers.append((i, screen_x, screen_y))
            elif i.isvisible():
                i.hideturtle()

        if len(visible_chasers) > 150:
            render_interval = 3
        elif len(visible_chasers) > 75:
            render_interval = 2
        else:
            render_interval = 1
        render_chasers = self.ai_frame % render_interval == 0

        for i, screen_x, screen_y in visible_chasers:
            if not i.isvisible():
                i.setheading(i.target_angle)
                i.setpos(screen_x, screen_y)
                i.showturtle()
            elif render_chasers:
                i.setheading(i.target_angle)
                i.setpos(screen_x, screen_y)
        self.runner.run_ai(self.chasers)
        self.update_arena()
        self.draw_arena()
        in_zone = self.update_zones()
        if self.is_firing:
            self.fire()
        self.update_shots()
        if self.invincible_timer == 0 and (self.is_catched() or in_zone):
            self.lives = max(0, self.lives - 1)
            self.invincible_timer = self.invincible_duration
            self.update_lives()
            if self.lives == 0:
                self.game_state = 'game_over'
                self.show_game_over()
        self.update_invincible()
        
        # TODO) You can do something here and follows.
        # 0.2초마다 업데이트(메모리 절약)
        if self.timer % 200 == 0:
            # is_catched = self.is_catched()
            self.drawer.clear()
            self.life_icon.hideturtle()
            self.update_lives()

            # add timer
            self.drawer2.undo()
            self.drawer2.penup()
            self.drawer2.setpos(200, 300)
            self.drawer2.write(f'남은 시간) {self.timer // 60000:02d}:{self.timer % 60000 // 1000:02d}')

            self.drawer3.undo()
            self.drawer3.penup()
            self.drawer3.setpos(200, 270)
            self.drawer3.write(f'개체수) {len(self.chasers)}')

            self.drawer4.undo()
            self.drawer4.penup()
            self.drawer4.setpos(0, 300)
            self.drawer4.write(f'Score: {self.score}', align='center', font=('Arial', 16, 'bold'))
            self.raise_ui()


        
        self.timer -= self.ai_timer_msec
        self.fire_timer = max(0, self.fire_timer - self.ai_timer_msec)
        if self.timer <= 0:
            self.game_state = 'clear'
            self.show_clear()

        screen.update()
        self.lower_zones()
        self.raise_warnings()
        self.raise_ui()

        # Note) The following line should be the last of this function to keep the game playing
        self.canvas.ontimer(self.step, self.ai_timer_msec)


# bullet 객체 통제를 위한 클래스
class bulletMover(turtle.RawTurtle):
    def __init__(self, canvas = None, shape = "classic", undobuffersize = 1000, visible = True):
        super().__init__(canvas, shape, undobuffersize, visible)
        self.step_move = 10
        self.absolutePos = [0, 0]

    # 현재 방향으로 총알 이동
    def run_ai(self):
        angle = math.radians(self.heading())
        self.absolutePos[0] += self.step_move * math.cos(angle)
        self.absolutePos[1] += self.step_move * math.sin(angle)

# 플레이어 객체
class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=3, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
        self.Up = False
        self.Down = False
        self.Left = False
        self.Right = False
        self.cameraPos = [0,0]

        # Register event handlers
        canvas.onkeypress(lambda: self.move('Up','keydown'), "w")
        canvas.onkeypress(lambda: self.move('Down','keydown'), "s")
        canvas.onkeypress(lambda: self.move('Left','keydown'), "a")
        canvas.onkeypress(lambda: self.move('Right','keydown'), "d")
        canvas.listen()
        canvas.onkeyrelease(lambda: self.move('Up','keyup'), "w")
        canvas.onkeyrelease(lambda: self.move('Down','keyup'), "s")
        canvas.onkeyrelease(lambda: self.move('Left','keyup'), "a")
        canvas.onkeyrelease(lambda: self.move('Right','keyup'), "d")
        canvas.listen()

    # 가장 가까운 적 탐색 및 플레이어 이동
    def run_ai(self, opp_list):
        #가장 가까운 enemy 탐지(bullet 발사용)
        Nearest_dist2 = math.inf
        Nearest_enemy = None
        for i in opp_list:
            x0,y0 = self.pos()
            x1,y1 = i.pos()
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            dist2 = dx**2 + dy**2
            if Nearest_dist2 > dist2:
                Nearest_dist2 = dist2
                Nearest_enemy = i
        self.target = Nearest_enemy
        #self.target.color('green') # 테스트용 색칠 코드 

        # 플레이어 이동 처리 (플레이어는 중앙에 고정)
        if self.Up:
            # for i in opp_list:
            #     i.setpos(i.pos()[0], i.pos()[1] - self.step_move)
            self.cameraPos[1] -= self.step_move
            self.setheading(90)
        if self.Down:
            # for i in opp_list:
            #     i.setpos(i.pos()[0], i.pos()[1] + self.step_move)
            self.cameraPos[1] += self.step_move
            self.setheading(-90)

        ## 대각선 이동 처리
        if self.Left:
            # for i in opp_list:
            #     i.setpos(i.pos()[0] + self.step_move, i.pos()[1])
            self.cameraPos[0] += self.step_move
            if self.Up:
                self.setheading(135)
            elif self.Down:
                self.setheading(-135)
            else:
                self.setheading(180)
        if self.Right:
            # for i in opp_list:
            #     i.setpos(i.pos()[0] - self.step_move, i.pos()[1])
            self.cameraPos[0] -= self.step_move
            if self.Up:
                self.setheading(45)
            elif self.Down:
                self.setheading(-45)
            else:
                self.setheading(0)
            

    # 중복 키입력 처리
    def move(self, heading, key):
        if key == 'keydown':
            if heading == 'Up':
                self.Up = True
            elif heading == 'Down':
                self.Down = True
            elif heading == 'Left':
                self.Left = True
            else:
                self.Right = True
                
        elif key == 'keyup':
            if heading == 'Up':
                self.Up = False
            elif heading == 'Down':
                self.Down = False
            elif heading == 'Left':
                self.Left = False
            else:
                self.Right = False


# 적 객체
class ChaseMover(turtle.RawTurtle):
    # 메모리 절약용 slot 지정
    __slots__ = ['step_move','step_turn','p','dx','dy','target_angle','absolutePos','health']

    def __init__(self, canvas, step_move=1, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
        self.absolutePos = [0, 0]
        self.health = 1

    # 플레이어한테 이동함
    def run_ai(self, opp, opp_heading):
        p = self.absolutePos # x0,y0
        q = [-opp.cameraPos[0], -opp.cameraPos[1]] # x1,y1
        dx = q[0] - p[0]
        dy = q[1] - p[1]
        self.target_angle = math.atan2(dy,dx) *  180 / math.pi
        self.absolutePos[0] += self.step_move * math.cos(math.radians(self.target_angle))
        self.absolutePos[1] += self.step_move * math.sin(math.radians(self.target_angle))
        # 참고용으로 남겨둔 코드
        # mode = random.randint(0, 2)
        # if mode == 0:
        #     self.forward(self.step_move)
        # elif mode == 1:
        #     self.left(self.step_turn)
        # elif mode == 2:
        #     self.right(self.step_turn)

if __name__ == '__main__':
    # Use 'TurtleScreen' instead of 'Screen' to prevent an exception from the singleton 'Screen'
    root = tk.Tk()
    root.title("Turtle Runaway")
    canvas = tk.Canvas(root, width=700, height=700)
    canvas.pack()
    screen = turtle.TurtleScreen(canvas)
    screen.bgcolor("skyblue")
    screen.tracer(0)

    # TODO) Change the follows to your turtle if necessary
    #chaser = ChaseMover(screen) // 밖에서 객체 생성X 
    runner = ManualMover(screen)
    

    game = RunawayGame(screen, runner)
    game.start()
    screen.mainloop()
