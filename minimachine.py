# minimachine.py

import pygame as pg

from interpreter import cycle

import compiler
import assembler
from assembler import LOCATION

pg.font.init()

FONT = pg.font.SysFont('Jetbrains Mono, Consolas', 32)
CHAR_SIZE = (19, 32)

def draw_text(surface: pg.Surface, text: str, 
			  pos: tuple[int, int], 
			  color: pg.Color = (255, 255, 255), 
			  bkgd: pg.Color = (0, 0, 0),
			  font: pg.font.Font = FONT):
	text_surface = font.render(text, True, color, bkgd)
	surface.blit(text_surface, pos)


def simulate(state: bytearray, fps: int = 5, auto: int = 0):
	pg.init()

	screen = pg.display.set_mode((1280, 720))
	pg.display.set_caption('Minimachine')

	clock = pg.time.Clock()
	running = True

	while running:
		pressed = pg.key.get_pressed()

		for _ in range(auto):
			cycle(state)

		if pressed[pg.K_SPACE]:
			cycle(state)

		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False

			if event.type == pg.KEYDOWN:
				if event.key == pg.K_s:
					cycle(state)

		screen.fill((0, 0, 0))

		state_iter = enumerate(iter(state))
		for y in range(16):
			for x in range(16):
				xpos = x * CHAR_SIZE[0] * 2
				ypos = y * CHAR_SIZE[1]
				index, byte = next(state_iter)
				byte_as_str = f'{byte:02x}'
				color = (255, 255, 255) if x % 2 else (155, 155, 155)
				bkgd = (0, 0, 0)

				if index in (state[LOCATION.INSTR_PTR], state[LOCATION.STACK_PTR]):
					color, bkgd = bkgd, color

				draw_text(screen, byte_as_str, (xpos, ypos), color, bkgd)


		mouse_x, mouse_y = pg.mouse.get_pos()
		selected_x = mouse_x // (CHAR_SIZE[0] * 2)
		selected_y = mouse_y // CHAR_SIZE[1]
		selected_index = selected_y * 16 + selected_x
		if selected_index in range(len(state)):
			selected_byte = state[selected_index]
			draw_text(screen, f'Byte 0x{selected_index:02x}:', (0, CHAR_SIZE[1] * 17))
			draw_text(screen, f'  Value: 0x{selected_byte:02x} ({selected_byte})', (0, CHAR_SIZE[1] * 18))
			draw_text(screen, f'  From stack ptr: {selected_index - state[LOCATION.STACK_PTR]}', (0, CHAR_SIZE[1] * 19))


		# Draw FPS in bottom left corner
		draw_text(screen, f'FPS: {clock.get_fps():.2f}', (0, 720 - 32))
		pg.display.update()
		clock.tick(fps)


	pg.quit()


if __name__ == '__main__':
	# file_name = 'basic.masm'
	# state = assembler.masm_to_bytecode(open(file_name))

	compiler.compile('basic.mcom', 'basic.masm')
	with open('basic.masm', 'r') as file:
		state = assembler.masm_to_bytecode(file)

	simulate(state, fps=60, auto=0)
