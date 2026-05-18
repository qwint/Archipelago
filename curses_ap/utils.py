#!/usr/bin/env python3
import curses
import curses.textpad
import curses.ascii


class CursesCancel(Exception):
    pass


def curses_select(data: list[str]) -> str | None:
    def select_box(stdscr):
        nonlocal ret
        POINTER_COL = 1
        DATA_COL = POINTER_COL + 1
        MAX_POINTER = len(data) - 1
        VERTICAL_OFFSET = 1
        MAX_BOX_HEIGHT = 10
        MAX_BOX_LENGTH = 40
        SCROLLING_ENABLED = MAX_POINTER > MAX_BOX_HEIGHT
        BOX_HEIGHT = min(MAX_BOX_HEIGHT, MAX_POINTER)
        MAX_SCROLL_OFFSET = MAX_POINTER + 1 - BOX_HEIGHT

        # shared attrs for the select
        pointer = 0
        scroll_offset = 0

        def write_data(self):
            for index, line in enumerate(data):
                offset_index = index - scroll_offset
                if 0 <= offset_index < BOX_HEIGHT:
                    self.addstr(VERTICAL_OFFSET + offset_index, DATA_COL, line + " " * (MAX_BOX_LENGTH - 1 - len(line)))
            self.refresh()

        def move_pointer(self, down: bool):
            nonlocal pointer
            nonlocal scroll_offset
            if pointer <= 0 and not down:
                return
            if pointer >= MAX_POINTER and down:
                return
            previous = pointer
            pointer += int(down or -1)
            if SCROLLING_ENABLED and previous == scroll_offset and not down:
                scroll_offset -= 1
                write_data(self)
            elif SCROLLING_ENABLED and previous - scroll_offset == BOX_HEIGHT - 1 and down:
                scroll_offset += 1
                write_data(self)

            set_pointer(self, pointer)

        def set_pointer(self, new):
            for i in range(BOX_HEIGHT):
                self.addch(VERTICAL_OFFSET + i, POINTER_COL, " ", curses.A_NORMAL)
                self.chgat(VERTICAL_OFFSET + i, POINTER_COL, MAX_BOX_LENGTH, curses.A_NORMAL)
            self.addch(VERTICAL_OFFSET + new - scroll_offset, POINTER_COL, "*", curses.A_STANDOUT)
            self.chgat(VERTICAL_OFFSET + new - scroll_offset, POINTER_COL, MAX_BOX_LENGTH, curses.A_STANDOUT)

        def page(self, down: bool):
            nonlocal pointer
            nonlocal scroll_offset
            new_pointer = pointer + (int(down or -1) * BOX_HEIGHT)
            if new_pointer >= MAX_POINTER:
                # scroll to bottom, move pointer to retain pointer - offset visual position
                # *potentially check if no scrolling is required, if so jump pointer to extreme
                # if scroll_offset == MAX_POINTER + 1 - BOX_HEIGHT:

                pointer = MAX_POINTER
                scroll_offset = MAX_SCROLL_OFFSET
            elif new_pointer <= 0:
                # scroll to top, move pointer to retain pointer - offset visual position
                # *potentially check if no scrolling is required, if so jump pointer to extreme
                pointer = 0
                scroll_offset = 0
            else:
                pointer = new_pointer
                scroll_offset += (int(down or -1) * BOX_HEIGHT)
                if scroll_offset < 0:
                    pointer -= scroll_offset
                    scroll_offset -= scroll_offset
                elif scroll_offset > MAX_SCROLL_OFFSET:
                    pointer -= (scroll_offset - MAX_SCROLL_OFFSET)
                    scroll_offset -= (scroll_offset - MAX_SCROLL_OFFSET)
            write_data(self)
            set_pointer(self, pointer)

        def poll(self) -> int | None:
            key = self.getch()
            if key == curses.KEY_UP:
                move_pointer(self, False)
            elif key == curses.KEY_DOWN:
                move_pointer(self, True)
            elif key == curses.KEY_RIGHT:
                page(self, True)
            elif key == curses.KEY_LEFT:
                page(self, False)
            elif key == curses.ascii.ESC:
                raise CursesCancel("User Cancelled")
            else:
                return pointer

        curses.textpad.rectangle(stdscr, 0, 0, BOX_HEIGHT + 1, MAX_BOX_LENGTH + 1)
        write_data(stdscr)

        stdscr.addch(VERTICAL_OFFSET + 0, POINTER_COL, "*", curses.A_STANDOUT)
        set_pointer(stdscr, 0)

        while ret is None:
            ret = poll(stdscr)
            pass

    ret = None
    try:
        curses.wrapper(select_box)
    except CursesCancel:
        return None
    return data[ret]

# example usage
# my_data = ["hello", "there", "angel", "from", "my", "nightmare", "shadow", "in", "the", "background", "of", "the", "morgue", "the", "unspecting", "victim", "of", "darkness", "in", "the", "valley", "we", "can", "live", "like", "jack", "and", "sally", "if", "you", "want"]
# print(curses_select(my_data))
