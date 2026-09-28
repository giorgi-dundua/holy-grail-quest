OPPOSITE_DIRECTIONS = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}


class Game:
    def __init__(self) -> None:
        self.current_location = starting_path
        starting_path.connect("north", tiny_bridge)
        self.state = "running"  # other states "won", "lost", "quit"

        self.player = Player("King Arthur", 100, 10)

    def move(self, direction: str):
        if direction in self.current_location.exits:
            self.current_location = self.current_location.exits[direction]
        else:
            print("Cannot go there")

    def look(self):
        description = []
        description.append(f"Place: {self.current_location.name}")
        description.append(
            f"Direction you can go: {
                ', '.join(
                    f'{direction}.title() - {location.name}'
                    for direction, location in self.current_location.exits.items()
                )
            }"
        )
        description.append(
            f"Characters at this location: {', '.join(character.name for character in self.current_location.characters)}"
        )
        description.append(
            f"Items at this location: {', '.join(item.name for item in self.current_location.items)}"
        )
        print("\n".join(description))

    def talk(self):
        pass

    def status(self):
        pass

    def run(self):
        while self.state == "running":
            self.end_turn = "n"
            while self.end_turn == "n":
                self.look()

                if self.current_location.items != []:
                    for item in self.current_location.items:
                        pick_up = input(f"Type y to pick up {item.name}: ")
                        if pick_up == "y":
                            self.player.take(item)
                            self.current_location.items.remove(item)
                direction = input("What direction should I go?: ")
                self.move(direction)
                print(self.current_location.name)
                self.end_turn = input("End turn? Type y/n: ")
            if self.current_location == tiny_bridge:
                print("You won")
                self.state = "won"


class Character:
    def __init__(self, name: str, max_health: int, attack_power: int) -> None:
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.attack_power = attack_power

    def attack(self, target: "Character") -> None:
        pass

    def take_damage(self, amount: int):
        pass


class Enemy(Character):
    pass


class Player(Character):
    def __init__(self, name: str, max_health: int, attack_power: int) -> None:
        super().__init__(name, max_health, attack_power)

        self.inventory = []

    def take(self, item: "Item"):
        self.inventory.append(item)

    def drop(self, item: "Item"):
        pass

    def use(self, item: "Item"):
        if item in self.inventory:
            if item.function == "heal":
                self.health = min(self.max_health, self.health + item.effect)
                print(f"You have used {item.name}. Your health is: {self.health}")
                self.inventory.remove(item)

        else:
            print(f"You Don't have the {item}")


class Item:
    def __init__(self, name: str, function: str, effect: int) -> None:
        self.name = name
        self.function = function
        self.effect = effect


class Location:
    def __init__(
        self,
        name: str,
        exits: dict[str, "Location"] | None = None,
        items: list["Item"] | None = None,
        characters: list["Character"] | None = None,
    ) -> None:
        self.name = name
        self.exits = exits if exits is not None else {}
        self.characters = characters if characters is not None else []
        self.items = items if items is not None else []

    def connect(self, direction: str, other_location: "Location") -> None:
        """Connects this location to another location"""
        if direction not in OPPOSITE_DIRECTIONS:
            raise ValueError(
                f"Unknown direction: '{direction}'. Must be one of {list(OPPOSITE_DIRECTIONS.keys())}"
            )

        reverse_direction = OPPOSITE_DIRECTIONS[direction]

        self.exits[direction] = other_location
        other_location.exits[reverse_direction] = self


emergency_biscuit = Item("Emergency Biscuit", "heal", 25)

starting_path = Location(
    "Starting Path",
    items=[emergency_biscuit],
    characters=[Enemy("Black Knight", 50, 5)],
)

tiny_bridge = Location(
    "Tiny Bridge",
)
