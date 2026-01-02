import random, time, pygame

KEY_MAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
}
FONT = [
    0xF0,
    0x90,
    0x90,
    0x90,
    0xF0,  # 0
    0x20,
    0x60,
    0x20,
    0x20,
    0x70,  # 1
    0xF0,
    0x10,
    0xF0,
    0x80,
    0xF0,  # 2
    0xF0,
    0x10,
    0xF0,
    0x10,
    0xF0,  # 3
    0x90,
    0x90,
    0xF0,
    0x10,
    0x10,  # 4
    0xF0,
    0x80,
    0xF0,
    0x10,
    0xF0,  # 5
    0xF0,
    0x80,
    0xF0,
    0x90,
    0xF0,  # 6
    0xF0,
    0x10,
    0x20,
    0x40,
    0x40,  # 7
    0xF0,
    0x90,
    0xF0,
    0x90,
    0xF0,  # 8
    0xF0,
    0x90,
    0xF0,
    0x10,
    0xF0,  # 9
    0xF0,
    0x90,
    0xF0,
    0x90,
    0x90,  # A
    0xE0,
    0x90,
    0xE0,
    0x90,
    0xE0,  # B
    0xF0,
    0x80,
    0x80,
    0x80,
    0xF0,  # C
    0xE0,
    0x90,
    0x90,
    0x90,
    0xE0,  # D
    0xF0,
    0x80,
    0xF0,
    0x80,
    0xF0,  # E
    0xF0,
    0x80,
    0xF0,
    0x80,
    0x80,  # F
]


class Chip8:

    def __init__(self) -> None:
        self.keys = [False] * 16
        self.opcodes = {
            0x0: {0xE0: self.cls, 0xEE: self.ret},
            0x1: self.jump,
            0x2: self.call,
            0x3: self.skip_if_eq,
            0x4: self.skip_if_not_eq,
            0x5: {0x0: self.skip_if_vx_eq_vy},
            0x6: self.set_vx,
            0x7: self.add_nn_vx,
            0x8: {
                0x0: self.store_vy_in_vx,
                0x1: self.or_vx_vy,
                0x2: self.and_vx_vy,
                0x3: self.xor_vx_vy,
                0x4: self.add_vx_vy,
                0x5: self.sub_vx_vy,
                0x6: self.sh_right_vx,
                0x7: self.sub_vy_vx,
                0xE: self.sh_left_vx,
            },
            0x9: {0x0: self.skip_if_vx_not_eq_vy},
            0xA: self.load_i,
            0xB: self.jump_v0,
            0xC: self.rand_vx,
            0xD: self.draw_sprite,
            0xE: {0x9E: self.skip_if_vx_pressed, 0xA1: self.skip_if_vx_not_pressed},
            0xF: {
                0x07: self.load_delay_timer,
                0x0A: self.store_key_vx,
                0x15: self.dt_eq_vx,
                0x18: self.load_sound_timer,
                0x1E: self.add_i_vx,
                0x29: self.set_i_sprite,
                0x33: self.store_bcd_i_1_2,
                0x55: self.store_v0_vx,
                0x65: self.read_v0_vx,
            },
        }
        self.memory = bytearray(4096)
        self.v = [0] * 16
        self.i = 0
        self.pc = 0x200
        self.sp = 0
        self.stack = [0] * 16
        self.delay_timer = 0
        self.sound_timer = 0
        self.display = [[0] * 64 for _ in range(32)]
        self.waiting_for_key = False
        self.waiting_register = None
        self.memory[0:80] = FONT

    def fetch(self):
        opcode = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]
        self.pc += 2
        return opcode

    def decode(self, opcode):
        fnnn = opcode >> 12 & 0xFF
        op_fam = self.opcodes[fnnn]
        if isinstance(op_fam, dict):
            if fnnn in (0x0, 0xE, 0xF):
                n = opcode & 0xFF
            else:
                n = opcode & 0xF
            return self.opcodes[fnnn][n]
        else:
            return self.opcodes[fnnn]

    def execute(self, opcode, func):
        func(opcode)

    def cycle(self):
        if self.waiting_for_key:
            return
        opcode = self.fetch()
        func = self.decode(opcode)
        self.execute(opcode, func)

    def load_rom(self, path):
        with open(path, "rb") as f:
            rom = f.read()
        self.memory[0x200 : 0x200 + len(rom)] = rom

    def cls(self, opcode):
        self.display = [[0] * 64 for _ in range(32)]

    def ret(self, opcode):
        if self.sp == 0:
            raise Exception("Can't ret on empty stack")
        self.sp -= 1
        self.pc = self.stack[self.sp]

    def jump(self, opcode):
        nnn = opcode & 0x0FFF
        self.pc = nnn

    def call(self, opcode):
        if self.sp == 16:
            raise Exception("Can't add to stack")
        self.stack[self.sp] = self.pc
        self.sp += 1
        self.jump(opcode)

    def set_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        self.v[x] = nn

    def skip_if_eq(self, opcode):
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        if self.v[x] == nn:
            self.pc += 2

    def skip_if_not_eq(self, opcode):
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        if self.v[x] != nn:
            self.pc += 2

    def add_nn_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        self.v[x] = (self.v[x] + nn) & 0xFF

    def skip_if_vx_eq_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        if self.v[x] == self.v[y]:
            self.pc += 2

    def store_vy_in_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[x] = self.v[y]

    def or_vx_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[x] = self.v[x] | self.v[y]

    def and_vx_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[x] = self.v[x] & self.v[y]

    def xor_vx_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[x] = self.v[x] ^ self.v[y]

    def add_vx_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[0xF], self.v[x] = (
            1 if self.v[x] + self.v[y] > 255 else 0,
            (self.v[x] + self.v[y]) & 0xFF,
        )

    def sub_vx_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[0xF], self.v[x] = 1 if self.v[x] >= self.v[y] else 0, self.v[x] - self.v[
            y
        ] & 0xFF

    def sh_right_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[0xF], self.v[x] = 1 if self.v[x] & 0x01 == 1 else 0, self.v[x] >> 1

    def sub_vy_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[0xF], self.v[x] = 1 if self.v[x] <= self.v[y] else 0, self.v[y] - self.v[
            x
        ] & 0xFF

    def sh_left_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        self.v[0xF], self.v[x] = 1 if self.v[x] & 0x80 != 0 else 0, (
            self.v[x] << 1
        ) & 0xFF

    def skip_if_vx_not_eq_vy(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        if self.v[x] != self.v[y]:
            self.pc += 2

    def load_i(self, opcode):
        nnn = opcode & 0x0FFF
        self.i = nnn

    def jump_v0(self, opcode):
        nnn = opcode & 0x0FFF
        self.pc = self.v[0] + nnn

    def rand_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        rand = random.randint(0, 255)
        self.v[x] = rand & nn

    def draw_sprite(self, opcode):
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F

        x_pos = self.v[x]
        y_pos = self.v[y]

        self.v[0xF] = 0  # reset collision flag

        for row in range(n):
            sprite_byte = self.memory[self.i + row]
            for bit in range(8):
                pixel = (sprite_byte >> (7 - bit)) & 1
                x_coord = (x_pos + bit) % 64
                y_coord = (y_pos + row) % 32
                if pixel == 1 and self.display[y_coord][x_coord] == 1:
                    self.v[0xF] = 1
                self.display[y_coord][x_coord] ^= pixel

    def skip_if_vx_pressed(self, opcode):
        x = (opcode & 0x0F00) >> 8
        if self.keys[self.v[x]]:
            self.pc += 2

    def skip_if_vx_not_pressed(self, opcode):
        x = (opcode & 0x0F00) >> 8
        if not self.keys[self.v[x]]:
            self.pc += 2

    def load_delay_timer(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.v[x] = self.delay_timer

    def load_sound_timer(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.sound_timer = self.v[x]

    def add_i_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.i = self.i + self.v[x]

    def set_i_sprite(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.i = self.v[x] * 5

    def dt_eq_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.delay_timer = self.v[x]

    def store_key_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.waiting_for_key = True
        self.waiting_register = x

    def key_press(self, key):
        self.keys[key] = True
        if self.waiting_for_key:
            self.v[self.waiting_register] = key
            self.waiting_for_key = False

    def key_release(self, key):
        self.keys[key] = False

    def store_bcd_i_1_2(self, opcode):
        x = (opcode & 0x0F00) >> 8
        self.memory[self.i] = self.v[x] // 100
        self.memory[self.i + 1] = (self.v[x] // 10) % 10
        self.memory[self.i + 2] = self.v[x] % 10

    def store_v0_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        for i in range(0, x + 1):
            self.memory[self.i + i] = self.v[i]

    def read_v0_vx(self, opcode):
        x = (opcode & 0x0F00) >> 8
        for i in range(0, x + 1):
            self.v[i] = self.memory[self.i + i]

    def run(self):
        pygame.init()
        scale = 10
        screen = pygame.display.set_mode((64 * scale, 32 * scale))

        while True:
            start = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in KEY_MAP:
                        self.key_press(KEY_MAP[event.key])
                elif event.type == pygame.KEYUP:
                    if event.key in KEY_MAP:
                        self.key_release(KEY_MAP[event.key])

            for _ in range(8):
                self.cycle()
            if self.delay_timer > 0:
                self.delay_timer -= 1
            if self.sound_timer > 0:
                self.sound_timer -= 1

            screen.fill((0, 0, 0))

            for y in range(32):
                for x in range(64):
                    if self.display[y][x] == 1:
                        pygame.draw.rect(
                            screen,
                            (255, 255, 255),
                            (x * scale, y * scale, scale, scale),
                        )

            pygame.display.flip()

            elapsed = time.time() - start
            sleep_time = 1 / 60 - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


def main():
    chip = Chip8()
    chip.load_rom("pong.rom")
    chip.run()


if __name__ == "__main__":
    main()
