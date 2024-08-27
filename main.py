import sys

import GameState as GameState


def main():
    game_stuff = GameState.GameStuff()

    game_stuff.initialize()

    game_stuff.start()


if __name__ == '__main__':
    sys.exit(main())
