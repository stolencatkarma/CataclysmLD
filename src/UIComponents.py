
import glooey
import pyglet

class CustomBackground(glooey.Background):
    custom_center = pyglet.resource.texture("center.png")
    custom_top = pyglet.resource.texture("top.png")
    custom_bottom = pyglet.resource.texture("bottom.png")
    custom_left = pyglet.resource.texture("left.png")
    custom_right = pyglet.resource.texture("right.png")
    custom_top_left = pyglet.resource.image("top_left.png")
    custom_top_right = pyglet.resource.image("top_right.png")
    custom_bottom_left = pyglet.resource.image("bottom_left.png")
    custom_bottom_right = pyglet.resource.image("bottom_right.png")


class InputBox(glooey.Form):
    custom_alignment = "center"
    custom_height_hint = 12

    class Label(glooey.EditableLabel):
        custom_font_size = 10
        custom_color = "#b9ad86"
        custom_alignment = "center"
        custom_horz_padding = 4
        custom_top_padding = 2
        custom_width_hint = 200
        custom_height_hint = 12
        # TODO: import string; def format_alpha(entered_string): return "".join(char for char in entered_string if char in string.ascii_letters) # only allow valid non-space asicii

    class Base(glooey.Background):
        custom_center = pyglet.resource.texture("form_center.png")
        custom_left = pyglet.resource.image("form_left.png")
        custom_right = pyglet.resource.image("form_right.png")


class CharacterGenerationInputBox(glooey.Form):
    custom_alignment = "center"
    custom_height_hint = 12

    class Label(glooey.EditableLabel):
        custom_font_size = 12
        custom_color = "#b9ad86"
        custom_alignment = "center"
        custom_horz_padding = 4
        custom_top_padding = 2
        custom_width_hint = 200
        custom_height_hint = 12
        # TODO: import string; def format_alpha(entered_string): return "".join(char for char in entered_string if char in string.ascii_letters) # only allow valid non-space asicii

    class Base(glooey.Background):
        custom_center = pyglet.resource.texture("form_center.png")
        custom_left = pyglet.resource.image("form_left.png")
        custom_right = pyglet.resource.image("form_right.png")


class CustomScrollBox(glooey.ScrollBox):
    # custom_alignment = 'center'
    custom_size_hint = 300, 200
    custom_height_hint = 200

    class Frame(glooey.Frame):
        class Decoration(glooey.Background):
            custom_center = pyglet.resource.texture("scrollbox_center.png")

        class Box(glooey.Bin):
            custom_horz_padding = 2

    class VBar(glooey.VScrollBar):
        class Decoration(glooey.Background):
            custom_top = pyglet.resource.image("bar_top.png")
            custom_center = pyglet.resource.texture("bar_vert.png")
            custom_bottom = pyglet.resource.image("bar_bottom.png")

        class Forward(glooey.Button):
            class Base(glooey.Image):
                custom_image = pyglet.resource.image("forward_base.png")

            class Over(glooey.Image):
                custom_image = pyglet.resource.image("forward_over.png")

            class Down(glooey.Image):
                custom_image = pyglet.resource.image("forward_down.png")

        class Backward(glooey.Button):
            class Base(glooey.Image):
                custom_image = pyglet.resource.image("backward_base.png")

            class Over(glooey.Image):
                custom_image = pyglet.resource.image("backward_over.png")

            class Down(glooey.Image):
                custom_image = pyglet.resource.image("backward_down.png")

        class Grip(glooey.ButtonScrollGrip):
            class Base(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_base.png")
                custom_center = pyglet.resource.texture("grip_vert_base.png")
                custom_bottom = pyglet.resource.image("grip_bottom_base.png")

            class Over(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_over.png")
                custom_center = pyglet.resource.texture("grip_vert_over.png")
                custom_bottom = pyglet.resource.image("grip_bottom_over.png")

            class Down(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_down.png")
                custom_center = pyglet.resource.texture("grip_vert_down.png")
                custom_bottom = pyglet.resource.image("grip_bottom_down.png")


class CharacterGenerationScrollBox(glooey.ScrollBox):
    custom_alignment = "center"
    custom_size_hint = 200, 300
    custom_height_hint = 200

    class Frame(glooey.Frame):
        class Decoration(glooey.Background):
            custom_center = pyglet.resource.texture("scrollbox_center.png")

        class Box(glooey.Bin):
            custom_horz_padding = 2

    class VBar(glooey.VScrollBar):
        class Decoration(glooey.Background):
            custom_top = pyglet.resource.image("bar_top.png")
            custom_center = pyglet.resource.texture("bar_vert.png")
            custom_bottom = pyglet.resource.image("bar_bottom.png")

        class Forward(glooey.Button):
            class Base(glooey.Image):
                custom_image = pyglet.resource.image("forward_base.png")

            class Over(glooey.Image):
                custom_image = pyglet.resource.image("forward_over.png")

            class Down(glooey.Image):
                custom_image = pyglet.resource.image("forward_down.png")

        class Backward(glooey.Button):
            class Base(glooey.Image):
                custom_image = pyglet.resource.image("backward_base.png")

            class Over(glooey.Image):
                custom_image = pyglet.resource.image("backward_over.png")

            class Down(glooey.Image):
                custom_image = pyglet.resource.image("backward_down.png")

        class Grip(glooey.ButtonScrollGrip):
            class Base(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_base.png")
                custom_center = pyglet.resource.texture("grip_vert_base.png")
                custom_bottom = pyglet.resource.image("grip_bottom_base.png")

            class Over(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_over.png")
                custom_center = pyglet.resource.texture("grip_vert_over.png")
                custom_bottom = pyglet.resource.image("grip_bottom_over.png")

            class Down(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_down.png")
                custom_center = pyglet.resource.texture("grip_vert_down.png")
                custom_bottom = pyglet.resource.image("grip_bottom_down.png")


class ConnectButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14

    Label = MyLabel
    # custom_alignment = 'fill'
    # custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


class CharacterListButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


class CreateNewCharacterButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self):
        super().__init__("Create a Character")


class CharacterGenButton(glooey.Button):
    custom_padding = 8

    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 12
        custom_padding = 2

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


class ServerListButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 12

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#3465a4"

    class Over(glooey.Background):
        custom_color = "#204a87"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)

