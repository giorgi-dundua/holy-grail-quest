import random
import textwrap

OPPOSITE_DIRECTIONS = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}

BASE_ACTIONS = ("Status", "Look", "Take", "Use", "Attack", "Talk", "Move", "Quit")
TALK_OPTIONS = ("Ask to join", "Taunt")
DASH_LINE = "--------------------------------------------------------"
DASH_LINE_LEN = len(DASH_LINE)
INDENT = "   "

CHAPTER_COMPLETE = f"""\
{DASH_LINE}
{"CHAPTER COMPLETE".center(DASH_LINE_LEN)}
{DASH_LINE}
The bridge is crossed. The Black Knight objects.
His objection has been noted and walked past.
Ahead lies Witch Trial Village.
The quest continues. This chapter, however, does not.
{DASH_LINE}
"""

GAME_OVER = f"""\
{DASH_LINE}
{"GAME OVER".center(DASH_LINE_LEN)}
{DASH_LINE}
Your quest ends here. The Grail remains unfound.
Applications for a replacement king will be accepted
in due course. Please bring your own coconuts.
{DASH_LINE}
"""


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


class Game:
    """Manage the player, world, and terminal command loop."""

    def __init__(self) -> None:
        # Characters
        king_arthur = Player("King Arthur", 50, 10)
        black_knight = Enemy(
            "The Black Knight",
            max_health=40,
            damage=20,
            hurt_message=[
                "Tis but a scratch.",
                "I've had worse.",
                "Just a flesh wound.",
            ],
            defeat_message=textwrap.fill(
                "Defeated limbless Black Knight: Oh, oh, I see. Running away, eh? You yellow bastards! Come back here and take what's coming to you! I'll bite your legs off!",
                width=DASH_LINE_LEN,
            ),
            block_message="None shall pass",
        )
        patsy_servant = Character("Patsy the Servant", 1, 0, can_join=True)
        bedevere = Character("Bedevere", 1, 0)
        witch = Character("Witch", 1, 0)
        village_crowd = Character("Villagers", 1, 0)

        # Items
        coconut_shells = Item(
            "Coconut Shells",
            function="prop",
            effect=0,
            description="banging together imitates horse-galloping",
        )
        emergency_biscuit = Item(
            "Emergency Biscuit",
            function="heal",
            effect=25,
            description="restores up to 25 health",
        )

        # Locations
        starting_path = Location(
            "Starting Path",
            items=[coconut_shells],
            characters=[patsy_servant],
            description="A muddy track leads north. The hoofprints suggest a horse of unusually consistent stride.",
        )

        black_knights_bridge = Location(
            "Black Knight's Bridge",
            items=[emergency_biscuit],
            characters=[black_knight],
            exit_blockers={"north": black_knight},
            description="A narrow bridge crosses a stream of very little consequence. Turning around would require some planning.",
        )

        witch_trial_village = Location(
            "Witch Trial Village",
            characters=[bedevere, witch, village_crowd],
            description="The village square stands ready for a trial. Its standards of evidence are less ready.",
        )

        # Location connections
        self.current_location = starting_path
        self.goal_location = witch_trial_village
        starting_path.connect("north", black_knights_bridge)
        black_knights_bridge.connect("north", witch_trial_village)

        self.state = "Running"  # other states "Won", "Lost", "Quit"

        self.player = king_arthur
        self.party: list[Character] = [self.player]

    def move(self, direction: str) -> None:
        """Attempt to leave the current location in the chosen direction."""
        destination = self.current_location.exits.get(direction)
        if destination is None:
            print(f"No path leads {direction} from here.")
            return

        blocker = self.current_location.exit_blockers.get(direction)
        if blocker is not None and blocker.health > 0:
            print(f"{blocker.name} bars the {direction} exit.")
            if blocker.block_message:
                print(f"{blocker.name}: {blocker.block_message}")
            return

        self.current_location = destination
        self.show_place_description()
        if self.current_location is self.goal_location:
            self.state = "Won"

    def talk(self, character: Character) -> None:
        options: list[str] = list(TALK_OPTIONS)
        if not character.can_join:
            options.remove("Ask to join")
        user_choice = self.choose_option(options, allow_back=True)
        if user_choice is not None:
            if options[user_choice] == "Ask to join":
                self.join_party(character)
            if options[user_choice] == "Taunt":
                print(
                    f"{self.player.name} delivers an insult. The conversation fails to improve."
                )

    def status(self) -> None:
        status_list = [
            DASH_LINE,
            f"STATUS - {self.player.name}",
            DASH_LINE,
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Attack damage: {self.player.damage}",
            "",
        ]
        if len(self.party) > 1:
            status_list.append("Companions:")
            status_list.append(
                "\n".join(f"{INDENT}{companion.name}" for companion in self.party[1:])
            )
        else:
            status_list.append("Companions: none")
        status_list.append("")
        if self.player.inventory != []:
            status_list.append("Inventory:")
            status_list.append(
                "\n".join(
                    f"{INDENT}{item.name} - {item.description}"
                    for item in self.player.inventory
                )
            )
        else:
            status_list.append("Inventory: empty")
        status_list.append(DASH_LINE)

        print("\n".join(status_list))

    def join_party(self, character: Character) -> None:
        if character in self.party:
            print(f"{character.name} is already travelling with you.")
            return
        if character not in self.current_location.characters:
            print(f"{character.name} is not here.")
            return
        if not character.can_join:
            print(f"{character.name} declines to join the quest.")
            return

        self.current_location.characters.remove(character)
        self.party.append(character)
        print(
            "Patsy falls in behind you, coconuts at the ready."
            if character.name == "Patsy the Servant"
            else f"{character.name} joins the party."
        )

    def fight_round(self, enemy: Enemy) -> None:
        self.player.attack(enemy)
        if enemy.health > 0:
            enemy.attack(self.player)
        else:
            opened_exit = next(
                (
                    direction
                    for direction, blocker in self.current_location.exit_blockers.items()
                    if blocker is enemy
                ),
                None,
            )
            if opened_exit is not None:
                print(f"The {opened_exit} exit is now clear.")

        if self.player.health == 0:
            self.state = "Lost"

    def get_living_characters(self) -> list["Character"]:
        """Return the characters here with health above zero."""
        return [
            character
            for character in self.current_location.characters
            if character.health > 0
        ]

    def get_available_actions(self) -> list[str]:
        """Return the actions currently offered in the main menu."""
        available_actions: list[str] = list(BASE_ACTIONS)
        characters_alive = self.get_living_characters()
        if not self.current_location.exits:
            available_actions.remove("Move")
        if self.current_location.items == []:
            available_actions.remove("Take")
        if not any(isinstance(character, Enemy) for character in characters_alive):
            available_actions.remove("Attack")
        if self.player.inventory == []:
            available_actions.remove("Use")
        if not characters_alive:
            available_actions.remove("Talk")
        return available_actions

    def choose_option(self, labels: list[str], allow_back: bool = False) -> int | None:
        """Ask for a numbered choice until the input is valid.
        Return a zero-based index, or None when Back is allowed and selected.
        """
        while True:
            if allow_back:
                print("0. Go back")
            user_choice = input(
                "\n".join(
                    f"{n}. {option.title()}" for n, option in enumerate(labels, 1)
                )
                + "\nChoose a number: "
            ).strip()
            if allow_back and user_choice.isdigit() and int(user_choice) == 0:
                return None
            if user_choice.isdigit() and 1 <= int(user_choice) <= len(labels):
                return int(user_choice) - 1
            else:
                print("Invalid choice. Choose one of the numbers shown.")
                print("=" * len("Invalid choice. Choose one of the numbers shown."))

    def handle_action(self, user_action: str) -> None:
        """Perform an implemented main-menu action."""
        if user_action == "status":
            self.status()

        if user_action == "look":
            self.look()

        if user_action == "take":
            item_labels = [item.name for item in self.current_location.items]
            user_choice = self.choose_option(item_labels, allow_back=True)
            if user_choice is not None:
                self.player.take(self.current_location.items[user_choice])
                self.current_location.items.pop(user_choice)

        if user_action == "use":
            player_items = [item.name for item in self.player.inventory]
            user_choice = self.choose_option(player_items, allow_back=True)
            if user_choice is not None:
                self.player.use(self.player.inventory[user_choice])

        if user_action == "attack":
            alive_enemies = [
                enemy
                for enemy in self.current_location.characters
                if enemy.health > 0 and isinstance(enemy, Enemy)
            ]
            enemy_names = [enemy.name for enemy in alive_enemies]
            user_choice = self.choose_option(enemy_names, allow_back=True)
            if user_choice is not None:
                enemy = alive_enemies[user_choice]
                self.fight_round(enemy)

        if user_action == "talk":
            characters_alive = self.get_living_characters()
            user_choice = self.choose_option(
                [character.name for character in characters_alive],
                allow_back=True,
            )
            if user_choice is not None:
                self.talk(characters_alive[user_choice])

        if user_action == "move":
            exit_labels = list(self.current_location.exits)
            user_choice = self.choose_option(exit_labels, allow_back=True)
            if user_choice is not None:
                self.move(exit_labels[user_choice])

        if user_action == "quit":
            quit_labels = ["quit"]
            user_choice = self.choose_option(quit_labels, allow_back=True)
            if user_choice is not None:
                print(f"Brave {self.player.name} Ran Away!")
                print("Bravely Ran Away Away!")
                print(
                    "When danger reared its ugly head, he bravely turned his tail and fled!"
                )
                print("Yes, brave Sir Robin turned about,")
                print("And gallantly, he chickened out!")
                print("Swiftly taking to his feet, he beat a very brave retreat!")
                print(f"Bravest of the Brave, {self.player.name.upper()}!")
                self.state = "Quit"

    def show_place_description(self) -> None:
        centered_name = self.current_location.name.center(DASH_LINE_LEN)
        wrapped_description = textwrap.fill(
            self.current_location.description, width=DASH_LINE_LEN
        )

        output = f"{DASH_LINE}\n{centered_name}\n{DASH_LINE}\n{wrapped_description}"
        print(output)

    def display_summary(self) -> None:
        """Display a brief summary before the action menu."""
        summary = [""]
        summary.append(f"--- {self.current_location.name} ---")
        summary.append(f"Health: {self.player.health}/{self.player.max_health}")

        # Conditional lines
        if len(self.party) > 1:
            summary.append(
                f"Companions: {', '.join(character.name for character in self.party[1:])}"
            )
        living_characters = self.get_living_characters()
        if living_characters != []:
            summary.append(
                f"Nearby: {', '.join(character.name for character in living_characters)}"
            )
        if self.current_location.items != []:
            summary.append(
                f"On the ground: {', '.join(item.name for item in self.current_location.items)}"
            )

        summary.append(
            f"Exits: {', '.join(f'{direction.title()}' for direction in self.current_location.exits)}"
        )
        summary.append("")

        print("\n".join(summary))

    def look(self) -> None:
        """Display the current location's exits, characters, and items."""
        self.show_place_description()
        look_list = [
            "",
            "Exits:",
            "\n".join(
                f"{INDENT}{direction.title()} - {location.name}{f' (blocked by {self.current_location.exit_blockers[direction].name})' if self.current_location.exit_blockers.get(direction) is not None and self.current_location.exit_blockers[direction].health > 0 else ''}"
                for direction, location in self.current_location.exits.items()
            ),
            "",
        ]
        if self.current_location.characters == []:
            look_list.append("Nearby: no one")
        else:
            look_list.append("Nearby:")
            look_list.append(
                "\n".join(
                    f"{INDENT}{character.name}{' - defeated' if character.health == 0 else ''}"
                    for character in self.current_location.characters
                )
            )
        if self.current_location.items == []:
            look_list.append("On the ground: nothing")
        else:
            look_list.append("On the ground:")
            look_list.append(
                "\n".join(
                    f"{INDENT}{item.name} - {item.description}"
                    for item in self.current_location.items
                )
            )
        look_list.append("")
        print("\n".join(look_list))

    def run(self) -> None:
        """Repeat the command menu until the game state changes."""
        self.show_place_description()

        while self.state == "Running":
            self.display_summary()
            available_actions = self.get_available_actions()
            choice_index = self.choose_option(available_actions)

            if choice_index is not None:
                self.handle_action(user_action=available_actions[choice_index].lower())

        if self.state == "Won":
            print(CHAPTER_COMPLETE)
        elif self.state == "Lost":
            print(GAME_OVER)
