import pygame
import sqlite3
import os
import sys
import random
import time

TIMER_END_GAME = 120

WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 60
pygame.init()
# Создаёт поверхность для отображения всего дисплея
screen = pygame.display.set_mode(DISPLAY_SIZE)

pygame.display.set_caption("Race Game")
# Создаём объект для отслеживания времени
clock = pygame.time.Clock()
speed = 20

# обозначения занятости средней полосы
middle_mutex = True


# создание объектов
all_sprites = pygame.sprite.Group()
car_sprites = pygame.sprite.Group()
truck_sprites = pygame.sprite.Group()

car1 = None
car2 = None

x1_road, x2_road = 0, WIDTH
x1_snow, y1_snow, x2_snow, y2_snow, x3_snow, y3_snow, x4_snow, y4_snow, = 0, 0, -WIDTH, -HEIGHT, 0, -HEIGHT, WIDTH, 0
time_count = 0
metres1 = 0
metres2 = 0
timer_mutex = True
# Создаём своё кастомное событие с указанным  ID
MYEVENTTYPE = pygame.USEREVENT + 1
TIMEREVENT = pygame.USEREVENT + 2
# События будут генерироваться с указанными интервалами в мс
# Далее будем ловить их внутри программного цикла


def reset_game():
    global truck_sprites
    global car_sprites
    global all_sprites
    global time_count
    global metres1, metres2
    global timer_mutex
    global car1, car2
    global middle_mutex

    truck_number = 1
    for one_sprite in truck_sprites.sprites():
        print(f'Truck # {truck_number}')
        truck_number = truck_number + 1
        truck_sprites.remove(one_sprite)

    car_number = 1
    for one_car in car_sprites.sprites():
        car_sprites.remove(one_car)
        print(f'car # = {car_number}')
        car_number += 1

    sprite_number = 1
    for one_sprite in all_sprites.sprites():
        all_sprites.remove(one_sprite)
        print(f'sprite # = {sprite_number}')
        sprite_number += 1

    middle_mutex = True
    
    time_count = 0
    metres1 = 0
    metres2 = 0
    timer_mutex = True
    pygame.time.set_timer(MYEVENTTYPE, 10000)   # 10 сек - событие появления новой встречной машины
    pygame.time.set_timer(TIMEREVENT, 1000)     # 1 сек - событие срабатывания таймера
    car1 = Car(1, car_sprites, all_sprites)
    car2 = Car(2, car_sprites, all_sprites)
    return


# Ф-ия зарузки изображения
# и придания изображению прозрачного фона при необходимости
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

# Устанавливает надпись в определённом месте экрана 
# Возвращает прямоугольник с координатами надписи
def print_text(message="", x=0, y=0, font_color='black', font_size=30, frame_color=None, frame_indent=0, frame_width=1):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
    if frame_color:
        pygame.draw.rect(screen, frame_color, (
            x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2,
            text.get_rect()[3] + frame_indent * 2), frame_width)
    return (x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2 + x,
            text.get_rect()[3] + frame_indent * 2 + y)



def winner_screen(score1, score2):
    fon1 = load_image('shop_fon4.jpg')
    # Подогнали масштаб изображения
    fon_img = pygame.transform.scale(fon1, (fon1.get_width(), fon1.get_height()*1.1))
    # Отрисовываем на основной поверхности в координате (0,0) фоновую картинку
    screen.blit(fon_img, (0, 0))
    counter = 0
    while True:
        clock.tick(10)
        screen.blit(fon_img, (0, 0))
        print_text('Конец игры', 300 , 200, 'green', 150)
        if (score1 > score2):
            print_text('Победил Игрок1', 250 , 400, 'green', 150)
        elif (score2 > score1):
            print_text('Победил Игрок2', 250 , 400, 'green', 150)
        else:
            print_text('Ничья!', 450 , 400, 'green', 150)
        counter = counter + 1
        if (counter == 20):
            #reset_game()
            return start_screen()
        pygame.display.flip()


# Начальный экран с выбором действий
def start_screen():
    fon1 = load_image('start_fon8.jpeg')
    # Подогнали масштаб изображения
    fon_img = pygame.transform.scale(fon1, (fon1.get_width() * 0.25, fon1.get_height() * 0.25))
    # Отрисовываем на основной поверхности в координате (0,0) фоновую картинку
    screen.blit(fon_img, (0, 0))
    # Координаты для отрисовки снега
    y1_snow, y2_snow = 0, -HEIGHT
    while True:
        # Задание максимального кол-ва кадров в секунду
        clock.tick(10)
        screen.blit(fon_img, (0, 0))
        play_btn = print_text('Играть!', 30 // 2, 100, 'grey', 200, 'grey')
        shop_btn = print_text('Магазин1', 30 // 2, 270, 'grey', 200, 'grey')
        shop_btn2 = print_text('Магазин2', 30 // 2, 440, 'grey', 200, 'grey')
        #settings_btn = print_text('Настройки', 30 // 2, 440, 'grey', 200, 'grey')
        # Создание анимации со снегом с помощью 2 склеенных рисунков
        y1_snow = y1_snow + speed if y1_snow < HEIGHT else -HEIGHT + speed
        y2_snow = y2_snow + speed if y2_snow < HEIGHT else -HEIGHT + speed
        screen.blit(pygame.transform.scale(load_image('snow.png'), (WIDTH, HEIGHT)), (0, y1_snow))
        screen.blit(pygame.transform.scale(load_image('snow.png'), (WIDTH, HEIGHT)), (0, y2_snow))

        # Просмотр прошедших с момента отрисовки последнего кадра событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Если была нажата кнопка "Играть"
                if play_btn[0] < event.pos[0] < play_btn[2] and play_btn[1] < event.pos[1] < play_btn[3]:
                    print('Go to the game')
                    reset_game()
                    # Выход из этой ф-ии означает выполненеие дальнейших команд в файле (начало гонки)
                    return
                # Если была нажата кнопка "Магазин1"
                elif shop_btn[0] < event.pos[0] < shop_btn[2] and shop_btn[1] < event.pos[1] < shop_btn[3]:
                    return shop(1)
                # Если была нажата кнопка "Магазин2"
                elif shop_btn2[0] < event.pos[0] < shop_btn2[2] and shop_btn2[1] < event.pos[1] < shop_btn2[3]:
                    return shop(2)

        # Обновляем содержимое дисплея (перерисовка ранее загруженного содержимого на экран)
        pygame.display.flip()


# конект с бд
con = sqlite3.connect("Race project")
cur = con.cursor()

# Пункт меню "Магазин" (пока только для одного игрока - первого)
def shop(player):
    COIN_COLOR = (234, 156, 0)
    player = player

    def cars_draw(last_choice = 0):
        # отрисовка машинок, цен, статусов
        x, y = 750, 0
        cars_bords = list()
        # Выбираем из таблицы БД все машинки
        for car in cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall():
            car_img = pygame.transform.scale(load_image(car[3] + '.png', None), (180, 180))
            car_stat, car_price, car_stat2 = car[1], int(car[2]), car[4]
            screen.blit(car_img, (x, y))
            # Для первого игрока
            if (player == 1):
                # Подписываем уже купленные 1 игроком машинки зелёным цветом
                if car_stat == 'unlock' or car_stat == 'choosed':
                    print_text('purchased', x + 60, y + 160, 'green', 25)
                # Ещё не купленные машинки подписываем ценой жёлтого цвета
                else:
                    print_text(str(car_price), x + 70, y + 160, 'yellow', 30)
            # Для второго игрока
            else:
                # Подписываем уже купленные 2 игроком машинки зелёным цветом
                if car_stat2 == 'unlock' or car_stat2 == 'choosed':
                    print_text('purchased', x + 60, y + 160, 'green', 25)
                # Ещё не купленные машинки подписываем ценой жёлтого цвета
                else:
                    print_text(str(car_price), x + 70, y + 160, 'yellow', 30)
            
            cars_bords.append((x, y, x + 180, y + 180))
            y = y + 180 if x == 1110 else y
            x = x + 180 if x < 1110 else 750

        # Получаем информацию о выбранной игроком в данный момент машине
        name, stat, price, img, stat2 = car_info = cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall()[
            last_choice]

        # отрисовка выбранной машинки
        screen.blit(pygame.transform.scale(load_image(img + '.png'), (700, 700)), (5, 50))

        # отрисовка квадрата подсветки
        clck = cars_bords[last_choice]
        pygame.draw.rect(screen, 'grey', (clck[0], clck[1], clck[2] - clck[0], clck[3] - clck[1]), 1)

        # отрисовка кнопки *Купить* для первого игрока
        if (player == 1):
            if stat == 'lock':
                buy_bords = print_text(f'Купить за {price}', 100, 800, COIN_COLOR, 100, (234, 156, 0),
                                    10)
            elif stat == 'choosed':
                buy_bords = print_text('Выбрано', 100, 800, (170, 226, 57), 100, 'green', 10)

            else:
                buy_bords = print_text('Взять', 100, 800, (32, 119, 42), 100, 'green', 10)
        # отрисовка кнопки *Купить* для второго игрока
        else:
            if stat2 == 'lock':
                buy_bords = print_text(f'Купить за {price}', 100, 800, COIN_COLOR, 100, (234, 156, 0),
                                    10)
            elif stat2 == 'choosed':
                buy_bords = print_text('Выбрано', 100, 800, (170, 226, 57), 100, 'green', 10)

            else:
                buy_bords = print_text('Взять', 100, 800, (32, 119, 42), 100, 'green', 10)

        return cars_bords, buy_bords, car_info

    # Отрисовка монет и подписи к ним ???
    def coins_draw():
        # Рисуем саму картинку с монетой
        screen.blit(pygame.transform.scale(load_image('coin.png'), (40, 40)), (200, 0))
        # Делаем подпись данными о балансе игрока из БД
        if (player == 1):
            print_text(str(cur.execute("""SELECT * FROM progress""").fetchall()[0][1]), 250, 0, COIN_COLOR, 68)
        else:
            print_text(str(cur.execute("""SELECT * FROM progress""").fetchall()[0][3]), 250, 0, COIN_COLOR, 68)

    # Сброс экрана ( в зависимости от выбранной машины ) ???
    def screen_reset(last_choice):
        screen.blit(pygame.transform.scale(load_image('shop_fon4.jpg'), (WIDTH, HEIGHT)), (0, 0))
        cars_draw(last_choice)
        coins_draw()
        # кнопка выхода в главное меню
        exit_bords = print_text('Выход', 0, 0, 'red', 50, 'red', 20, 5)
        return exit_bords

    # При переходе в магазин, всегда активной будет первая машинка из списка
    last_choice = 0
    # фон
    screen.blit(pygame.transform.scale(load_image('road.png'), (WIDTH, HEIGHT)), (0, 0))
    # отрисовка баланса
    #coins_draw()
    exit_bords = screen_reset(last_choice)

    # цикл отрисовки
    while True:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # нажатие на мышку ( выбор машинки/покупка машинки/выход из магазина )
            elif event.type == pygame.MOUSEBUTTONDOWN:

                cars_bords, buy_bords, car_info = cars_draw(last_choice)
                # проверка на клик по машинке
                for index, clck in enumerate(cars_bords):
                    # Если попадание в координаты карточки с машиной
                    if clck[0] < event.pos[0] < clck[2] and clck[1] < event.pos[1] < clck[3]:
                        # Запоминаем индекс этой машины
                        last_choice = index
                        cars_bords, buy_bords, car_info = cars_draw(last_choice)
                        screen_reset(last_choice)
                        name, stat, price, img, stat2 = car_info

                # проверка на клик по кнопке "купить"
                if buy_bords[0] < event.pos[0] < buy_bords[2] and buy_bords[1] < event.pos[1] < buy_bords[3]:
                    if (player == 1):
                        coins = cur.execute("""SELECT * FROM progress""").fetchall()[0][1]

                        # покупка
                        if coins >= price and stat == 'lock':
                            cur.execute(f'''UPDATE car_icons SET status = 'unlock' WHERE name = '{name}' ''')
                            cur.execute(f'''UPDATE progress SET coins == {coins - price}''')
                            con.commit()
                            print_text(f'Вы приобрели {name}', 50, WIDTH // 2, 'green', 100)

                        # В случае недостаточного кол-ва средств, вывести надпись
                        elif coins < price and stat == 'lock':
                            print_text(f'Недостаточно средств', 50, WIDTH // 2, 'red', 100)

                        # Замена текущей машины на уже купленную ранее
                        elif stat == 'unlock':
                            cur.execute(f'''UPDATE car_icons SET status = 'unlock' WHERE status = 'choosed' ''')
                            cur.execute(f'''UPDATE car_icons SET status = 'choosed' WHERE name = '{name}' ''')
                            con.commit()

                        # Если эта машина активна в текущий момент
                        elif stat == 'choosed':
                            print_text(f'Машина уже выбрана', 50, WIDTH // 2, 'yellow', 100)
                    else:
                        coins2 = cur.execute("""SELECT * FROM progress""").fetchall()[0][3]

                        # покупка
                        if coins2 >= price and stat2 == 'lock':
                            cur.execute(f'''UPDATE car_icons SET status2 = 'unlock' WHERE name = '{name}' ''')
                            cur.execute(f'''UPDATE progress SET coins2 == {coins2 - price}''')
                            con.commit()
                            print_text(f'Вы приобрели {name}', 50, WIDTH // 2, 'green', 100)

                        # В случае недостаточного кол-ва средств, вывести надпись
                        elif coins2 < price and stat2 == 'lock':

                            print_text(f'Недостаточно средств', 50, WIDTH // 2, 'red', 100)

                        # Замена текущей машины на уже купленную ранее
                        elif stat2 == 'unlock':
                            cur.execute(f'''UPDATE car_icons SET status2 = 'unlock' WHERE status2 = 'choosed' ''')
                            cur.execute(f'''UPDATE car_icons SET status2 = 'choosed' WHERE name = '{name}' ''')
                            con.commit()

                        # Если эта машина активна в текущий момент
                        elif stat2 == 'choosed':
                            print_text(f'Машина уже выбрана', 50, WIDTH // 2, 'yellow', 100)


                    screen_reset(last_choice)

                # выход из магазина
                if exit_bords[0] < event.pos[0] < exit_bords[2] and exit_bords[1] < event.pos[1] < exit_bords[3]:
                    return start_screen()

            pygame.display.flip()


# Класс встречных машин
class Truck(pygame.sprite.Sprite):

    def __init__(self, line, *groups):
        super().__init__(*groups)
        con = sqlite3.connect("Race project")
        cur = con.cursor()
        # Делаем выборку всех названий файлов с изображениями машин по возрастанию их цены
        imgs = list(cur.execute("""SELECT link FROM car_icons WHERE status != "choosed" ORDER BY price """).fetchall())
        # Добавляем картинку грузовика к списку
        imgs.append(['truck'])
        # Пишет произвольное имя картинки
        print(imgs[random.randint(0, len(imgs) - 1)][0] + '.png')
        # Выбираем произвольно одну из машин в полученном списке
        self.image_name = imgs[random.randint(0, len(imgs) - 1)][0] + '.png'
        self.image = pygame.transform.scale(load_image(self.image_name), (256, 256))
        # Поворот всех картинок на 270, а грузовика на 180 градусов
        self.image = pygame.transform.rotate(self.image, 270 if self.image_name != 'truck.png' else 180)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        # Установка изображения по осям
        self.rect.x = WIDTH
        self.rect.y = line * 150 + 60
        # Признак разбитой машины
        self.broken = False

    def truck_crash(self):
        self.image = pygame.transform.scale(load_image('minus_heart.png'), (80, 60))

    def update(self):
        global metres1, metres2
        # Создание искусственной "тряски" встречной машины (небольшие смещения на каждом такте по оси Х)
        self.rect.move_ip(random.randrange(-1, 2), 0)
        self.rect.x -= 30
        player = 0
        for c in car_sprites:
            # При столкновении с нашей машиной встречная исчезает, появляется разбитое сердечко
            if pygame.sprite.collide_mask(self, c):
                self.truck_crash()
                # Если машина только разбилась, отнимаем 2 метра у соответствующего игрока
                if not self.broken:
                    print(f"Player # =  '{player}' ")
                    if (player == 0):
                        metres1 = metres1 - 2
                    else:
                        metres2 = metres2 - 2
                    self.broken = True
            player = player + 1



class Car(pygame.sprite.Sprite):
    con = sqlite3.connect("Race project")
    cur = con.cursor()
    

    def __init__(self, player, *groups):
        super().__init__(*groups)
        self.player = player
        if (player == 1):
            image = load_image(cur.execute("""SELECT link FROM car_icons WHERE status == 'choosed' """).fetchone()[0] + '.png')
        else:
            image = load_image(cur.execute("""SELECT link FROM car_icons WHERE status2 == 'choosed' """).fetchone()[0] + '.png')
        image = pygame.transform.rotate(image, 90) 
        self.image = image
        self.image = pygame.transform.scale(self.image, (256, 256))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        

        # Начальная позиция машинок оп оси Х одинаковая
        self.rect.x = 0
        # Начальная позиция машинки первого игрока (верхняя полоса из трёх)
        if (player == 1):
            self.rect.y = 210
        # Начальная позиция машинки второго игрока (нижняя полоса из трёх)
        else:
            self.rect.y = 520

    # Перемещение на соседнюю полосу при нажатии на кнопку "вверх" или "вниз"
    def line_move(self, pressed_keys):
        global middle_mutex
        # Для первого игрока управление стрелками вверх и вниз по первой и второй полосам
        if (self.player == 1):
            if pressed_keys[pygame.K_UP]:
                if self.rect.y > 300:
                    self.rect.y -= 150
                    middle_mutex = True
            if pressed_keys[pygame.K_DOWN]:
                if (self.rect.y < 300) and middle_mutex:
                    self.rect.y += 150
                    middle_mutex = False
        # Для второго игрока управление стрелками 1 и 2 по второй и третьей полосам
        else:
            if pressed_keys[pygame.K_1]:
                if (self.rect.y > 500) and middle_mutex:
                    self.rect.y -= 150
                    middle_mutex = False
            if pressed_keys[pygame.K_2]:
                if self.rect.y < 500:
                    self.rect.y += 150
                    middle_mutex = True

    # Создание искусственной "тряски" машины (небольшие смещения на каждом такте по оси Х)
    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)



# пауза игры
def pause():
    paused = True
    while paused:
        print_text('Пауза. Нажмите пробел для продолжения.', 50, 500, 'white', 70)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_PAUSE]:
                    return
def finish_screen():
    pass


# запуск начального экрана
start_screen()

#car1 = Car(1, car_sprites, all_sprites)
#car2 = Car(2, car_sprites, all_sprites)

reset_game() 

# Основной цикл игры
running = True
while running:
    # Заливка фона
    screen.fill('black')
    # Подгрузка фонового изображения города
    fon = pygame.transform.scale(load_image('town0.png', None), (WIDTH, 1000))

    # Подгрузка изображения дороги
    road = pygame.transform.scale(load_image('town0_1.png', None), (WIDTH, 1000))
    x1_road = x1_road - speed if x1_road > -WIDTH else WIDTH - speed
    x2_road = x2_road - speed if x2_road > -WIDTH else WIDTH - speed
    metres1 = metres1 + 1 if x1_road % 50 == 0 else metres1
    metres2 = metres2 + 1 if x1_road % 50 == 0 else metres2
    # Склейкой двух картинок по горизонтали создаём эффект движения дороги
    screen.blit(road, (x1_road, 0))
    screen.blit(road, (x2_road, 0))

    # Цикл для отслеживания событий произошедших с момента последней отрисовки
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            for car in car_sprites:
                # Ловим только события если кнопка нажата и удерживается
                car.line_move(pygame.key.get_pressed())
            # По нажатию на Esc показывает стартовый экран
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                start_screen()
        # Каждые 10 сек генерируем новую машину ???
        elif event.type == MYEVENTTYPE:
            truck = Truck(random.randint(1, 3), truck_sprites, all_sprites)
        # Каждую секунду прибавляем счётчик времени
        elif event.type == TIMEREVENT:
            time_count += 1


    truck_sprites.update()
    car_sprites.update()

    # отрисовка гг
    car_sprites.draw(screen)

    # отрисовка остальных машин
    truck_sprites.draw(screen)

    # отрисовка снега
    snow = pygame.transform.scale(load_image('snow6.png'), (WIDTH, HEIGHT))
    x1_snow = x1_snow - speed if x1_snow > -WIDTH else WIDTH - speed
    x2_snow = x2_snow - speed if x2_snow > -WIDTH else WIDTH - speed
    x3_snow = x3_snow - speed if x3_snow > -WIDTH else WIDTH - speed
    x4_snow = x4_snow - speed if x4_snow > -WIDTH else WIDTH - speed

    y1_snow = y1_snow + speed if y1_snow < HEIGHT else -HEIGHT + speed
    y2_snow = y2_snow + speed if y2_snow < HEIGHT else -HEIGHT + speed
    y3_snow = y3_snow + speed if y3_snow < HEIGHT else -HEIGHT + speed
    y4_snow = y4_snow + speed if y4_snow < HEIGHT else -HEIGHT + speed

    screen.blit(snow, (x1_snow, y1_snow))
    screen.blit(snow, (x2_snow, y2_snow))
    screen.blit(snow, (x3_snow, y3_snow))
    screen.blit(snow, (x4_snow, y4_snow))
    # отрисовка  таймера
    print_text(time.strftime("%M:%S", time.gmtime(time_count)), 10, 10, 'white', 100)
    # отрисовка расстояния
    print_text(str(metres1) + 'metres', 250, 10, 'white', 100)
    print_text(str(metres2) + 'metres', 240, 890, 'white', 100)
    clock.tick(FPS)
    # Отображаем экран на котором предварительно отрисовали все вышеуказанные элементы
    pygame.display.flip()

    if (time_count >= TIMER_END_GAME):
        timer_mutex = False
        pygame.time.set_timer(MYEVENTTYPE, 0)   # попытка остановить таймеры с событиями
        pygame.time.set_timer(TIMEREVENT, 0)   
        winner_screen(metres1, metres2)

pygame.quit()
con.close()
