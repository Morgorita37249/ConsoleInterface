import sys
from shutil import get_terminal_size
from os import system
from pynput import keyboard

# Получаем размеры терминала
restrictions = get_terminal_size()
buffer = ''
cursor_left = 0
cursor_top = 0
help = 0


def print_there(x, y, text):
    """
    Функция для вывода текста на определенную позицию в терминале.
    x, y - координаты строки и столбца.

    """
    global cursor_left
    global cursor_top
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
    sys.stdout.write("\x1b7\x1b[%d;%dH" % (cursor_left, cursor_top))
    sys.stdout.flush()


def print_info(text):
    """
    Функция для вывода информации в нижней части экрана.

    """
    global restrictions
    print_there(restrictions.lines - 1, 0, text)


def refresh_screen():
    """
    Обновление экрана и установка курсора на последнюю позицию.

    """
    global cursor_left
    global cursor_top
    global buffer
    to_print = buffer + "[EOF]"
    print_there(0, 0, to_print)
    sys.stdout.write("\x1b7\x1b[%d;%dH" % (cursor_top, cursor_left))
    sys.stdout.flush()


def show_help():
    """
    Показ справочной информации о горячих клавишах.

    """
    help_message = ('F2 - save file\
     F1 - continue editing\
     DOWN,UP,RIGHT,LEFT - move the cursor\
     BACKSPACE - delete symbol\
     SHIFT - go to the next part of the text\
     ESC - exit')  # todo shift
    print_info(help_message)


def on_press(key):
    """
    Обработка нажатия клавиш.

    """
    global cursor_left
    global cursor_top
    global restrictions
    global help
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

    if key == keyboard.Key.f1:
        if help == 0:
            show_help()
            help = 1
        else:
            clear_screen()
            help = 0

    if key == keyboard.Key.f2:
        save_files()
        return

    try:
        add_to_buffer(key.char)
        cursor_left = cursor_left + 1
        if cursor_left >= restrictions.columns:
            cursor_left = restrictions.columns - 1

    except AttributeError:
        pass  # Необрабатываемые клавиши

    refresh_screen()


def save_files():
    """
    Сохранение буфера в файл.

    """
    global buffer
    try:
        with open(sys.argv[1], "w") as file:
            file.write(buffer)
        print_info("file {0} saved successfully".format(sys.argv[1]))
    except Exception as e:
        print_there(restrictions.lines - 1, 0, repr(e))


def spaces(times):
    """
    Генерация строки из пробелов.

    """
    return ' ' * times


def add_to_buffer(char):
    """
    Добавление символа в буфер.

    """
    global buffer
    global cursor_left
    global cursor_top
    global restrictions
    buffer_shift = restrictions.columns * cursor_top + cursor_left
    if buffer_shift <= len(buffer):
        buffer = buffer[:buffer_shift] + char + buffer[buffer_shift:]


def delete_from_buffer():
    """
    Удаление символа из буфера.

    """
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
    """
    Очистка экрана терминала.

    """
    if sys.platform == "win32":
        system('cls')
    else:
        system('clear')


def on_release(key):
    """
    Обработка отпускания клавиш.

    """
    if key == keyboard.Key.esc:
        clear_screen()
        # Остановка слушателя
        return False


def main():
    global buffer
    if len(sys.argv) < 2:
        print("usage: py pykey.py [file to edit]")
        sys.exit()

    # Чтение содержимого файла в буфер
    with open(sys.argv[1], "r") as file:
        for line in file:
            buffer += line

    print_there(0, 0, buffer)

    # Сбор событий до тех пор, пока не будет выпущена клавиша
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
