import textwrap

from models import Character, Enemy, Item, Location, Player

BASE_ACTIONS = ("Status", "Look", "Take", "Use", "Attack", "Talk", "Move", "Quit")
TALK_OPTIONS = ("Ask to join", "Taunt")
DASH_LINE = "--------------------------------------------------------"
DASH_LINE_LEN = len(DASH_LINE)
INDENT = "   "

WELCOME_MESSAGE = f"""\
{DASH_LINE}
{"THE HOLY GRAIL QUEST".center(DASH_LINE_LEN)}
{DASH_LINE}
Cross the Black Knight's bridge and reach the village.
"""

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

    def move(self, direction: str) -> str:
        """Attempt to leave the current location in the chosen direction."""
        destination = self.current_location.exits.get(direction)
        if destination is None:
            return f"No path leads {direction} from here."

        blocker = self.current_location.exit_blockers.get(direction)
        if blocker is not None and blocker.health > 0:
            move_message = f"{blocker.name} bars the {direction} exit."
            if blocker.block_message:
                return f"{move_message}\n{blocker.name}: {blocker.block_message}"
            return move_message

        self.current_location = destination
        move_message = self.show_place_description()
        if self.current_location is self.goal_location:
            self.state = "Won"
        return move_message

    def talk(self, character: Character) -> None:
        options: list[str] = list(TALK_OPTIONS)
        if not character.can_join:
            options.remove("Ask to join")
        user_choice = self.choose_option(options, allow_back=True)
        if user_choice is not None:
            if options[user_choice] == "Ask to join":
                print(self.join_party(character))
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

    def join_party(self, character: Character) -> str:
        if character in self.party:
            return f"{character.name} is already travelling with you."
        if character not in self.current_location.characters:
            return f"{character.name} is not here."
        if not character.can_join:
            return f"{character.name} declines to join the quest."

        self.current_location.characters.remove(character)
        self.party.append(character)
        return (
            "Patsy falls in behind you, coconuts at the ready."
            if character.name == "Patsy the Servant"
            else f"{character.name} joins the party."
        )

    def fight_round(self, enemy: Enemy) -> str:
        fight_msg = []
        fight_msg.append(self.player.attack(enemy))
        if enemy.health > 0:
            fight_msg.append(enemy.attack(self.player))
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
                fight_msg.append(f"The {opened_exit} exit is now clear.")

        if self.player.health == 0:
            self.state = "Lost"
        return "\n".join(fight_msg)

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

    def choose_option(
        self,
        labels: list[str],
        allow_back: bool = False,
        heading: str = "Choose an option:",
    ) -> int | None:
        """Return a selected index, or None when the player goes back."""
        while True:
            print(DASH_LINE)
            print(heading)

            if allow_back:
                print("0. Go back")

            for number, label in enumerate(labels, 1):
                print(f"{number}. {label.title()}")

            print(DASH_LINE)
            user_choice = input("Choose a number: ").strip()

            if allow_back and user_choice.isdigit() and int(user_choice) == 0:
                print()
                return None

            if user_choice.isdigit() and 1 <= int(user_choice) <= len(labels):
                print()
                return int(user_choice) - 1

            print("Invalid choice. Choose one of the numbers shown.")
            print()

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
                print(self.player.take(self.current_location.items[user_choice]))
                self.current_location.items.pop(user_choice)

        if user_action == "use":
            player_items = [item.name for item in self.player.inventory]
            user_choice = self.choose_option(player_items, allow_back=True)
            if user_choice is not None:
                print(self.player.use(self.player.inventory[user_choice]))

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
                print(self.fight_round(enemy))

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
                print(self.move(exit_labels[user_choice]))

        if user_action == "quit":
            user_choice = self.choose_option(
                ["Quit"],
                allow_back=True,
                heading="Leave the quest?",
            )

            if user_choice is not None:
                print(DASH_LINE)
                print(f"Brave {self.player.name} Ran Away!")
                print("Bravely Ran Away Away!")
                print(
                    "When danger reared its ugly head, he bravely turned his tail and fled!"
                )
                print(f"Yes, brave {self.player.name} turned about,")
                print("And gallantly, he chickened out!")
                print("Swiftly taking to his feet, he beat a very brave retreat!")
                print(f"Bravest of the Brave, {self.player.name.upper()}!")
                print(DASH_LINE)
                self.state = "Quit"

    def show_place_description(self) -> str:
        centered_name = self.current_location.name.center(DASH_LINE_LEN)
        wrapped_description = textwrap.fill(
            self.current_location.description, width=DASH_LINE_LEN
        )

        return f"{DASH_LINE}\n{centered_name}\n{DASH_LINE}\n{wrapped_description}"

    def look(self) -> None:
        """Display the current location's exits, characters, and items."""
        print(self.show_place_description())
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
        look_list.append("")
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
        # look_list.append("")
        print("\n".join(look_list))
