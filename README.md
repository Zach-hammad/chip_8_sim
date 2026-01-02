# CHIP-8 Emulator

A CHIP-8 emulator written in Python.

## Requirements

- Python 3
- pygame

```bash
pip install pygame
```

## Usage

```bash
python main.py
```

Edit `main.py` to load your ROM:

```python
def main():
    chip = Chip8()
    chip.load_rom("path/to/rom.ch8")
    chip.run()
```

## Controls

CHIP-8 uses a 16-key hex keypad. This emulator maps it to:

```
CHIP-8 Keypad       Keyboard
+---+---+---+---+   +---+---+---+---+
| 1 | 2 | 3 | C |   | 1 | 2 | 3 | 4 |
+---+---+---+---+   +---+---+---+---+
| 4 | 5 | 6 | D |   | Q | W | E | R |
+---+---+---+---+   +---+---+---+---+
| 7 | 8 | 9 | E |   | A | S | D | F |
+---+---+---+---+   +---+---+---+---+
| A | 0 | B | F |   | Z | X | C | V |
+---+---+---+---+   +---+---+---+---+
```

## Features

- All 35 CHIP-8 opcodes implemented
- 64x32 display with 10x scaling
- 60Hz timer updates
- ~500Hz CPU speed
- Full keyboard input support

## Resources

- [Cowgod's CHIP-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)
- [CHIP-8 ROMs](https://github.com/dmatlack/chip8/tree/master/roms)
