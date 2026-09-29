OPPOSITE_DIRECTIONS = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}

BASE_ACTIONS = ("Look", "Move", "Take", "Use", "Attack", "Status", "Quit")


class Character:
    def __init__(self, name: str, max_health: int, damage: int) -> None:
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.damage = damage

    def attack(self, target: "Character") -> None:
        pass

    def take_damage(self, amount: int):
        pass


class Enemy(Character):
    pass


class Player(Character):
    def __init__(self, name: str, max_health: int, damage: int) -> None:
        super().__init__(name, max_health, damage)

        self.inventory = []

    def take(self, item: "Item"):
        self.inventory.append(item)

    def drop(self, item: "Item"):
        pass

    def use(self, item: "Item"):
        if item in self.inventory:
            if item.function == "heal":
                if self.health == self.max_health:
                    print(f"Cannot use {item.name}. Health already at maximum level.")
                else:
                    self.health = min(self.max_health, self.health + item.effect)
                    print(
                        f"You have used {item.name}. Your health is: {self.health}/{self.max_health}"
                    )
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


class Game:
    def __init__(self) -> None:
        emergency_biscuit = Item("Emergency Biscuit", "heal", 25)
        starting_path = Location(
            "Starting Path",
            items=[emergency_biscuit],
            characters=[Enemy("The Black Knight", 50, 5)],
        )

        tiny_bridge = Location("Tiny Bridge")

        self.current_location = starting_path
        starting_path.connect("north", tiny_bridge)
        # self.state = "running"  # other states "won", "lost", "quit"

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
                    f'{direction.title()} - {location.name}'
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

    def get_living_character_names(self):
        return [
            character.name
            for character in self.current_location.characters
            if character.health > 0
        ]

    def display_situation(self):
        print(f"=== {self.current_location.name} ===")
        print(f"Health: {self.player.health}/{self.player.max_health}")
        items = self.current_location.items
        if items != []:
            print(f"Items: {', '.join(item.name for item in items)}")
        characters_alive = self.get_living_character_names()
        if characters_alive != []:
            print(
                f"{', '.join(character for character in characters_alive)} blocking the path."
            )

    def get_available_actions(self):
        available_actions = list(BASE_ACTIONS)
        characters_alive = self.get_living_character_names()
        if characters_alive != []:
            available_actions.remove("Move")
        if self.current_location.items == []:
            available_actions.remove("Take")
        if characters_alive == []:
            available_actions.remove("Attack")
        if self.player.inventory == []:
            available_actions.remove("Use")
        return available_actions

    def choose_option(self, labels: list) -> int:
        while True:
            user_choice = input(
                "\n".join(f"{n}. {option}" for n, option in enumerate(labels, 1))
                + "\nEnter corresponding number: "
            ).strip()
            if user_choice.isdigit() and 1 <= int(user_choice) <= len(labels):
                return int(user_choice) - 1
            else:
                print(
                    "Invalid choice. Please enter a number corresponding to an option."
                )

    def run(self):
        while True:
            self.display_situation()
            available_actions = self.get_available_actions()
            choice_index = self.choose_option(available_actions)
            user_action = available_actions[choice_index].lower()

            if user_action == "look":
                self.look()
            if user_action == "take":
                pass
            if user_action == "quit":
                print("Right then! Off I go, bravely running away (away!)")
                break
