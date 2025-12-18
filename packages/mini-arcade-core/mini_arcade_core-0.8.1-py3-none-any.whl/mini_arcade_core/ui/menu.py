"""
Menu system for mini arcade core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from mini_arcade_core.backend import Backend, Color, Event, EventType

MenuAction = Callable[[], None]


@dataclass(frozen=True)
class MenuItem:
    """
    Represents a single item in a menu.

    :ivar label (str): The text label of the menu item.
    :ivar on_select (MenuAction): The action to perform when the item is selected.
    """

    label: str
    on_select: MenuAction


@dataclass
class MenuStyle:
    """
    Styling options for the Menu.

    :ivar normal (Color): Color for unselected items.
    :ivar selected (Color): Color for the selected item.
    :ivar line_height (int): Vertical spacing between items.
    """

    normal: Color = (220, 220, 220)
    selected: Color = (255, 255, 0)
    line_height: int = 28


class Menu:
    """A simple text-based menu system."""

    def __init__(
        self,
        items: Sequence[MenuItem],
        *,
        x: int = 40,
        y: int = 40,
        style: MenuStyle | None = None,
    ):
        """
        :param items: Sequence of MenuItem instances to display.
        type items: Sequence[MenuItem]

        :param x: X coordinate for the menu's top-left corner.
        :param y: Y coordinate for the menu's top-left corner.

        :param style: Optional MenuStyle for customizing appearance.
        :type style: MenuStyle | None
        """
        self.items = list(items)
        self.x = x
        self.y = y
        self.style = style or MenuStyle()
        self.selected_index = 0

    def move_up(self):
        """Move the selection up by one item, wrapping around if necessary."""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)

    def move_down(self):
        """Move the selection down by one item, wrapping around if necessary."""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)

    def select(self):
        """Select the currently highlighted item, invoking its action."""
        if self.items:
            self.items[self.selected_index].on_select()

    def handle_event(
        self,
        event: Event,
        *,
        up_key: int,
        down_key: int,
        select_key: int,
    ):
        """
        Handle an input event to navigate the menu.

        :param event: The input event to handle.
        :type event: Event

        :param up_key: Key code for moving selection up.
        type up_key: int

        :param down_key: Key code for moving selection down.
        :type down_key: int

        :param select_key: Key code for selecting the current item.
        :type select_key: int
        """
        if event.type != EventType.KEYDOWN or event.key is None:
            return
        if event.key == up_key:
            self.move_up()
        elif event.key == down_key:
            self.move_down()
        elif event.key == select_key:
            self.select()

    def draw(self, surface: Backend):
        """
        Draw the menu onto the given backend surface.

        :param surface: The backend surface to draw on.
        :type surface: Backend
        """
        for i, item in enumerate(self.items):
            color = (
                self.style.selected
                if i == self.selected_index
                else self.style.normal
            )
            surface.draw_text(
                self.x,
                self.y + i * self.style.line_height,
                item.label,
                color=color,
            )
