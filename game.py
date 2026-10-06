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
    """Manage the player, and world"""

    def __init__(self) -> None:
        # Characters
        king_arthur = Player("King Arthur", "king", 50, 10)
        black_knight = Enemy(
            "The Black Knight",
            "black_knight",
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
        patsy_servant = Character("Patsy the Servant", "patsy", 1, 0, can_join=True)
        bedevere = Character("Sir Bedevere the Wise", "bedevere", 1, 0)
        witch = Character("Witch", "village_witch", 1, 0)
        village_crowd = Character("Villagers", "witch_villagers", 1, 0)

        # Items
        coconut_shells = Item(
            "Coconut Shells",
            function="prop",
            effect=0,
            description="banging together imitates horse-galloping",
            id="coconut",
        )
        emergency_biscuit = Item(
            "Emergency Biscuit",
            function="heal",
            effect=25,
            description="restores up to 25 health",
            id="biscuit",
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
        if self.current_location is self.goal_location:
            self.state = "Won"
        return f"You arrive at {self.current_location.name}."

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

    def get_state(self) -> dict:
        return {
            "state": self.state,
            "location": {
                "name": self.current_location.name,
                "description": self.current_location.description,
                "characters": [
                    {
                        "name": character.name,
                        "id": character.id,
                        "health": character.health,
                        "max_health": character.max_health,
                    }
                    for character in self.current_location.characters
                ],
                "items": [
                    {"name": item.name, "description": item.description, "id": item.id}
                    for item in self.current_location.items
                ],
                "exits": [
                    {
                        "direction": direction,
                        "destination": destination.name,
                        "blocked": bool(
                            self.current_location.exit_blockers.get(direction)
                            is not None
                            and self.current_location.exit_blockers[direction].health
                            > 0
                        ),
                    }
                    for direction, destination in self.current_location.exits.items()
                ],
            },
            "player": {
                "name": self.player.name,
                "id": self.player.id,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "inventory": [
                    {"name": item.name, "description": item.description, "id": item.id}
                    for item in self.player.inventory
                ],
            },
            "party": [
                {
                    "name": member.name,
                    "id": member.id,
                    "health": member.health,
                    "max_health": member.max_health,
                }
                for member in self.party
            ],
            "actions": self.get_available_actions() if self.state == "Running" else [],
        }
