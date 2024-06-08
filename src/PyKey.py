import sys
from shutil import get_terminal_size
from os import system
from pynput import keyboard

restrictions = get_terminal_size()


def print_there(x, y, text):
    global cursor_left
    global cursor_top
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.write("\x1b7\x1b[%d;%dH" % (cursor_left, cursor_top))
    sys.stdout.flush()


def print_info(text):
    global restrictions
    print_there(restrictions.lines - 1, 0, text)


cursor_left = 0
cursor_top = 0


def refresh_screen():
    global cursor_left
    global cursor_top
    global buffer
    to_print = buffer + "[EOF]"
    print_there(0, 0, to_print)
    sys.stdout.write("\x1b7\x1b[%d;%dH" % (cursor_top, cursor_left))
    sys.stdout.flush()


def on_press(key):
    global cursor_left
    global cursor_top
    global restrictions
    if key == keyboard.Key.right:
        cursor_left = cursor_left + 1
        if cursor_left >= restrictions.columns:
            cursor_left = restrictions.columns - 1

    if key == keyboard.Key.left:
        cursor_left = cursor_left - 1
        if cursor_left < 0:
            cursor_left = 0

    if key == keyboard.Key.down:
        cursor_top = cursor_top + 1
        if cursor_top >= restrictions.lines:
            cursor_top = restrictions.lines - 1

    if key == keyboard.Key.up:
        cursor_top = cursor_top - 1
        if cursor_top < 0:
            cursor_top = 0

    if key == keyboard.Key.space:
        add_to_buffer(" ")

    if key == keyboard.Key.backspace:
        delete_from_buffer()

    if key == keyboard.Key.f2:
        save_files()
        return

    try:
        add_to_buffer(key.char)
        cursor_left = cursor_left + 1
        if cursor_left >= restrictions.columns:
            cursor_left = restrictions.columns - 1

    except AttributeError:
        print_info(key)
    refresh_screen()


def save_files():
    global buffer
    try:
        file = open(sys.argv[1], "w")
        file.write(buffer)
        file.close()
        print_info("file {0} saved successfully".format(sys.argv[1]))
    except Exception as e:
        print_there(restrictions.lines - 1, 0, repr(e))


def spaces(times):
    s = ''
    for i in range(times):
        s += ' '
    return s


def add_to_buffer(char):
    global buffer
    global cursor_left
    global cursor_top
    global restrictions
    buffer_shift = restrictions.columns * cursor_top + cursor_left
    if buffer_shift <= len(buffer):
        buffer = buffer[:buffer_shift] + char + buffer[buffer_shift:]


def delete_from_buffer():
    global buffer
    global cursor_left
    global cursor_top
    global restrictions
    buffer_shift = restrictions.columns * cursor_top + cursor_left
    if buffer_shift > 0:
        buffer = buffer[:buffer_shift - 1] + buffer[buffer_shift:]
        cursor_left -= 1
        if cursor_left < 0:
            cursor_left = 0


def clear_screen():
    if sys.platform == "win32":
        system('cls')
    else:
        system('clear')


def on_release(key):
    if key == keyboard.Key.esc:
        clear_screen()
        # Stop listener
        return False


n = len(sys.argv)
print("Total arguments passed:", n)
if n < 2:
    print("usage: py pykey.py [file to edit]")
    sys.exit()

f = open(sys.argv[1], "r")
system('cls' if sys.platform == 'win32' else 'clear')
buffer = f.read()
f.close()

print_there(0, 0, buffer)

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
