import arcade
from core import constants as const
from core.menu import MenuView


def main():
    window = arcade.Window(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, "Void Caller")
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()