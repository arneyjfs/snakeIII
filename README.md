# SnakeIII

A micropython version of the classic retro game 'SnakeII' available on some nokia mobile phones c. 2000. 
This version is designed to be run on the Raspberry Pi Pico Microcontroller, and a display based on the GC9A01 chip.

## Setup

### Hardware
- Raspberry Pi Pico Microcontroller (standard, W, or WH)
![image](https://github.com/arneyjfs/snakeIII/assets/53710727/eb8b3fc9-d5a4-46c8-b186-6c34b18ab11f)
https://thepihut.com/products/raspberry-pi-pico-w

- 1.28” Round LCD HAT for Raspberry Pi Pico
![image](https://github.com/arneyjfs/snakeIII/assets/53710727/391df0e3-58a4-452a-bbe6-535fcef4a72d)
https://thepihut.com/products/1-28-round-lcd-hat-for-raspberry-pi-pico

### Software
You will need to load the GC9A01 firmware onto the board, available [here](https://github.com/russhughes/gc9a01_mpy) - big thanks to @russhughes

The easiest way to get started is to follow the device installation instructions:

https://learn.sb-components.co.uk/Pico-1.28-Round-LCD-HAT

Then save main.py from this repo to the board and you're good to go.

Try playing around with the game settings at the start of the script to change game speed and pixel sizes of the snake and food.


