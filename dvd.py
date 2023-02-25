import argparse
import contextlib
import curses
import enum
import random

dvd_string = [
    "     @@@@@@@@@@@@@@@@@@@@@@@@          @@@@@@@@@@@@@@@@@@@     ",
    "     @@@@@@@@@@@@@@@@@@@@@@@@@       @@@@@@@@@@@@@@@@@@@@@@@@@ ",
    "    @@@@@@        @@@@@@ @@@@@@    @@@@@@  @@@@@@       @@@@@@@",
    "   @@@@@@@        @@@@@@  @@@@@  @@@@@@   @@@@@@        @@@@@@@",
    "   @@@@@@       @@@@@@@    @@@@@@@@@@     @@@@@@      @@@@@@@  ",
    "  @@@@@@@@@@@@@@@@@@       @@@@@@@@      @@@@@@@@@@@@@@@@@     ",
    "                            @@@@@                              ",
    "                             @@                                ",
    "        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@            ",
    "@@@@@@@@@@@@@@@@@@@@@@@            @@@@@@@@@@@@@@@@@@@@@@@@    ",
    "   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@       ",
]


class Direction(enum.Enum):
    LEFT_DOWN = (-1, 1)
    LEFT_UP = (-1, -1)
    RIGHT_DOWN = (1, 1)
    RIGHT_UP = (1, -1)

    def inverse_horizontal(self) -> "Direction":
        inversion_map = {
            self.LEFT_DOWN: self.RIGHT_DOWN,
            self.LEFT_UP: self.RIGHT_UP,
            self.RIGHT_DOWN: self.LEFT_DOWN,
            self.RIGHT_UP: self.LEFT_UP,
        }

        return inversion_map[self]

    def inverse_vertical(self) -> "Direction":
        inversion_map = {
            self.LEFT_DOWN: self.LEFT_UP,
            self.LEFT_UP: self.LEFT_DOWN,
            self.RIGHT_DOWN: self.RIGHT_UP,
            self.RIGHT_UP: self.RIGHT_DOWN,
        }

        return inversion_map[self]


class Logo:
    direction: Direction

    current_row: int
    current_col: int

    rows: int
    cols: int
    colour: int

    max_row: int
    max_col: int

    def __init__(self, stdscr):
        self.rows, self.cols = stdscr.getmaxyx()

        self.stdscr = stdscr

        self.max_row = self.rows - len(dvd_string)
        self.max_col = self.cols - len(dvd_string[0])

        # self.current_row = random.randint(3, self.max_row - 3)
        # self.current_col = random.randint(3, self.max_col - 3)
        # self.direction = random.choice([d for d in Direction])
        self.current_row = self.max_row - 10
        self.current_col = self.max_col - 10
        self.direction = Direction.RIGHT_DOWN

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        self.colour = random.randint(1, 6)

        stdscr.bkgd(" ", curses.color_pair(self.colour))

    def change_colour(self):
        new_colour = self.colour
        while new_colour == self.colour:
            new_colour = random.randint(1, 6)

        self.colour = new_colour
        self.stdscr.bkgd(" ", curses.color_pair(new_colour))

    def _movement_update(self, *, direction=None) -> tuple[int, int]:
        _direction = direction if direction is not None else self.direction

        return (
            self.current_col + _direction.value[0],
            self.current_row + _direction.value[1],
        )

    def _direction_update(self, *, col: int, row: int, direction=None) -> Direction:
        _direction = direction if direction is not None else self.direction

        # Bounce off of horizontal walls
        if col < 0 or col > self.max_col:
            return _direction.inverse_horizontal()

        # Bounce off of vertical walls
        if row < 0 or row > self.max_row:
            return _direction.inverse_vertical()

        return _direction

    def timestep(self):
        self.stdscr.clear()

        new_col, new_row = self._movement_update()
        new_direction = self._direction_update(col=new_col, row=new_row)

        # Direction was changed because we hit a wall
        if new_direction.value != self.direction.value:
            self.change_colour()

            new_col, new_row = self._movement_update(direction=new_direction)

            # Check if a double bounce has to occur (hitting the corner)
            second_update = self._direction_update(
                col=new_col, row=new_row, direction=new_direction
            )
            if second_update.value != new_direction.value:
                new_direction = second_update
                new_col, new_row = self._movement_update(direction=new_direction)

        self.direction = new_direction
        self.current_col = new_col
        self.current_row = new_row

    def display(self):
        for i, line in enumerate(dvd_string):
            # When writing to the bottom-right position of the screen,
            # curses raises an incorrect error because the cursor is now out of bounds
            # This doesn't matter, so ignore it
            with contextlib.suppress(curses.error):
                self.stdscr.addstr(self.current_row + i, self.current_col, line)


def main(stdscr):
    # Clear screen
    stdscr.clear()
    curses.curs_set(False)

    logo = Logo(stdscr)

    while True:
        logo.display()

        stdscr.refresh()
        curses.delay_output(args.delay)
        logo.timestep()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--delay",
        default=1000,
        type=int,
        help="Delay between frame updates (in milliseconds)",
    )
    args = parser.parse_args()

    curses.wrapper(main)
