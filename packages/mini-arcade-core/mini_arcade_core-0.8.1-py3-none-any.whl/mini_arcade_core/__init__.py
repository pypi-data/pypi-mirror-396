"""
Entry point for the mini_arcade_core package.
Provides access to core classes and a convenience function to run a game.
"""

from __future__ import annotations

import logging
from importlib.metadata import PackageNotFoundError, version

from .backend import Backend, Event, EventType
from .boundaries2d import (
    RectKinematic,
    RectSprite,
    VerticalBounce,
    VerticalWrap,
)
from .collision2d import RectCollider
from .entity import Entity, KinematicEntity, SpriteEntity
from .game import Game, GameConfig
from .geometry2d import Bounds2D, Position2D, Size2D
from .kinematics2d import KinematicData
from .physics2d import Velocity2D
from .scene import Scene

logger = logging.getLogger(__name__)


def run_game(initial_scene_cls: type[Scene], config: GameConfig | None = None):
    """
    Convenience helper to bootstrap and run a game with a single scene.

    :param initial_scene_cls: The Scene subclass to instantiate as the initial scene.
    :type initial_scene_cls: type[Scene]

    :param config: Optional GameConfig to customize game settings.
    :type config: GameConfig | None

    :raises ValueError: If the provided config does not have a valid Backend.
    """
    cfg = config or GameConfig()
    if config.backend is None:
        raise ValueError(
            "GameConfig.backend must be set to a Backend instance"
        )
    game = Game(cfg)
    scene = initial_scene_cls(game)
    game.run(scene)


__all__ = [
    "Game",
    "GameConfig",
    "Scene",
    "Entity",
    "SpriteEntity",
    "run_game",
    "Backend",
    "Event",
    "EventType",
    "Velocity2D",
    "Position2D",
    "Size2D",
    "KinematicEntity",
    "KinematicData",
    "RectCollider",
    "VerticalBounce",
    "Bounds2D",
    "VerticalWrap",
    "RectSprite",
    "RectKinematic",
]

PACKAGE_NAME = "mini-arcade-core"  # or whatever is in your pyproject.toml


def get_version() -> str:
    """
    Return the installed package version.

    This is a thin helper around importlib.metadata.version so games can do:

        from mini_arcade_core import get_version
        print(get_version())

    :return: The version string of the installed package.
    :rtype: str

    :raises PackageNotFoundError: If the package is not installed.
    """
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:  # if running from source / editable
        logger.warning(
            f"Package '{PACKAGE_NAME}' not found. Returning default version '0.0.0'."
        )
        return "0.0.0"


__version__ = get_version()
