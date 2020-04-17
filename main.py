from game import *

def main():
    game = Game()
    while game.running and game.present_generation <= MAX_GEN:
        game.reset()
        game.run()


if __name__ == '__main__':
    main()