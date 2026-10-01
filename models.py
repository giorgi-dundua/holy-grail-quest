import random

OPPOSITE_DIRECTIONS = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}


class Character:
    """A character with health and a fixed damage value."""

    def __init__(
        self,
        name: str,
        max_health: int,
        damage: int,
        can_join: bool = False,
        hurt_message: list[str] | None = None,
        defeat_message: str | None = None,
        block_message: str = "",
    ) -> None:
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.damage = damage
        self.can_join = can_join
        self.hurt_message = hurt_message
        self.defeat_message = (
            defeat_message
            if defeat_message is not None
            else f"{self.name} is defeated."
        )
        self.block_message = block_message

    def attack(self, target: "Character") -> None:
        print(f"{self.name} strikes {target.name} for {self.damage} damage.")
        target.take_damage(self.damage)

    def take_damage(self, amount: int) -> None:
        """Reduce health without going below zero and report the result."""
        self.health = max(0, self.health - amount)

        if self.health == 0:
            print(self.defeat_message)
        elif self.hurt_message:
            print(random.choice(self.hurt_message))

        print(f"{self.name}'s health: {self.health}/{self.max_health}")
        print()


class Enemy(Character):
    """A hostile character in the adventure."""


class Player(Character):
    """A character who can carry and use items."""

    def __init__(self, name: str, max_health: int, damage: int) -> None:
        super().__init__(name, max_health, damage)

        self.inventory: list[Item] = []

    def take(self, item: "Item") -> None:
        """Add an item to the inventory and show its description."""
        self.inventory.append(item)
        print(f"You have acquired: {item.name}")
        print(item.description)

    def use(self, item: "Item") -> None:
        """Use a carried healing item and consume it after restoring health."""
        if item not in self.inventory:
            print(f"You are not carrying {item.name}.")
            return
        if item.function != "heal":
            print(f"{item.name} has no usable effect here.")
            return

        if self.health == self.max_health:
            print(f"Cannot use {item.name}. Health is already full.")
            return

        self.health = min(self.max_health, self.health + item.effect)
        self.inventory.remove(item)
        print(
            f"You used {item.name}. Your health is now: {self.health}/{self.max_health}"
        )


class Item:
    """An item with a named function and numeric effect."""

    def __init__(
        self,
        name: str,
        function: str,
        effect: int,
        description: str,
    ) -> None:
        self.name = name
        self.function = function
        self.effect = effect
        self.description = description


class Location:
    """A place containing exits, items, and characters."""

    def __init__(
        self,
        name: str,
        exits: dict[str, "Location"] | None = None,
        items: list["Item"] | None = None,
        characters: list["Character"] | None = None,
        exit_blockers: dict[str, Character] | None = None,
        description: str = "",
    ) -> None:
        self.name = name
        self.exits = exits if exits is not None else {}
        self.characters = characters if characters is not None else []
        self.items = items if items is not None else []
        self.exit_blockers = exit_blockers if exit_blockers is not None else {}
        self.description = description

    def connect(self, direction: str, other_location: "Location") -> None:
        """Connect this location to another in both directions.
        Raise ValueError if the direction has no known opposite.
        """
        if direction not in OPPOSITE_DIRECTIONS:
            raise ValueError(
                f"Unknown direction: '{direction}'. Must be one of {list(OPPOSITE_DIRECTIONS.keys())}"
            )

        reverse_direction = OPPOSITE_DIRECTIONS[direction]

        self.exits[direction] = other_location
        other_location.exits[reverse_direction] = self
