
import arcade
from constants import sc_width, sc_height, sc_title
# game view убрал
from menu_view import StartView


def main():
    window = arcade.Window(sc_width, sc_height, sc_title, antialiasing=False)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()
