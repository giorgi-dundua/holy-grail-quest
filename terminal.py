import textwrap

from game import (
    CHAPTER_COMPLETE,
    DASH_LINE,
    DASH_LINE_LEN,
    GAME_OVER,
    INDENT,
    TALK_OPTIONS,
    WELCOME_MESSAGE,
    Game,
)
from models import Character, Enemy


def run(game: Game) -> None:
    """Repeat the command menu until the game state changes."""
    print(WELCOME_MESSAGE)
    print(show_place_description(game))

    while game.state == "Running":
        display_summary(game)
        available_actions = game.get_available_actions()

        choice_index = choose_option(
            available_actions,
            heading="Choose an action:",
        )

        if choice_index is not None:
            handle_action(game, user_action=available_actions[choice_index].lower())

    print()

    if game.state == "Won":
        print(CHAPTER_COMPLETE)
    elif game.state == "Lost":
        print(GAME_OVER)


def display_summary(game: Game) -> None:
    """Display a brief summary before the action menu."""
    summary = [""]
    summary.append(f"--- {game.current_location.name} ---")
    summary.append(f"Health: {game.player.health}/{game.player.max_health}")

    # Conditional lines
    if len(game.party) > 1:
        summary.append(
            f"Companions: {', '.join(character.name for character in game.party[1:])}"
        )
    living_characters = game.get_living_characters()
    if living_characters != []:
        summary.append(
            f"Nearby: {', '.join(character.name for character in living_characters)}"
        )
    if game.current_location.items != []:
        summary.append(
            f"On the ground: {', '.join(item.name for item in game.current_location.items)}"
        )

    summary.append(
        f"Exits: {', '.join(f'{direction.title()}' for direction in game.current_location.exits)}"
    )
    summary.append("")

    print("\n".join(summary))


def handle_action(game: Game, user_action: str) -> None:
    """Perform an implemented main-menu action."""
    if user_action == "status":
        status(game)

    if user_action == "look":
        look(game)

    if user_action == "take":
        item_labels = [item.name for item in game.current_location.items]
        user_choice = choose_option(item_labels, allow_back=True)
        if user_choice is not None:
            print(
                game.perform_action(
                    user_action, game.current_location.items[user_choice].id
                )
            )

    if user_action == "use":
        player_items = [item.name for item in game.player.inventory]
        user_choice = choose_option(player_items, allow_back=True)
        if user_choice is not None:
            print(game.perform_action(user_action, game.player.inventory[user_choice].id))

    if user_action == "attack":
        alive_enemies = [
            enemy
            for enemy in game.current_location.characters
            if enemy.health > 0 and isinstance(enemy, Enemy)
        ]
        enemy_names = [enemy.name for enemy in alive_enemies]
        user_choice = choose_option(enemy_names, allow_back=True)
        if user_choice is not None:
            enemy_id = alive_enemies[user_choice].id
            print(game.perform_action(user_action, enemy_id))

    if user_action == "talk":
        characters_alive = game.get_living_characters()
        user_choice = choose_option(
            [character.name for character in characters_alive],
            allow_back=True,
        )
        if user_choice is not None:
            talk(game, characters_alive[user_choice])

    if user_action == "move":
        exit_labels = list(game.current_location.exits)
        user_choice = choose_option(exit_labels, allow_back=True)
        if user_choice is not None:
            previous_location = game.current_location
            move_return = game.perform_action(user_action, exit_labels[user_choice])
            if previous_location is not game.current_location:
                print(show_place_description(game))
            else:
                print(move_return)

    if user_action == "quit":
        user_choice = choose_option(
            ["Quit"],
            allow_back=True,
            heading="Leave the quest?",
        )

        if user_choice is not None:
            print(DASH_LINE)
            print(game.perform_action("quit"))
            print(DASH_LINE)


def talk(game: Game, character: Character) -> None:
    options: list[str] = list(TALK_OPTIONS)
    if not character.can_join:
        options.remove("Ask to join")
    user_choice = choose_option(options, allow_back=True)
    if user_choice is not None:
        if options[user_choice] == "Ask to join":
            print(game.perform_action("join", character.id))
        if options[user_choice] == "Taunt":
            print(
                f"{game.player.name} delivers an insult. The conversation fails to improve."
            )


def choose_option(
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


def status(game: Game) -> None:
    status_list = [
        DASH_LINE,
        f"STATUS - {game.player.name}",
        DASH_LINE,
        f"Health: {game.player.health}/{game.player.max_health}",
        f"Attack damage: {game.player.damage}",
        "",
    ]
    if len(game.party) > 1:
        status_list.append("Companions:")
        status_list.append(
            "\n".join(f"{INDENT}{companion.name}" for companion in game.party[1:])
        )
    else:
        status_list.append("Companions: none")
    status_list.append("")
    if game.player.inventory != []:
        status_list.append("Inventory:")
        status_list.append(
            "\n".join(
                f"{INDENT}{item.name} - {item.description}"
                for item in game.player.inventory
            )
        )
    else:
        status_list.append("Inventory: empty")
    status_list.append(DASH_LINE)

    print("\n".join(status_list))


def look(game: Game) -> None:
    """Display the current location's exits, characters, and items."""
    print(show_place_description(game))
    look_list = [
        "",
        "Exits:",
        "\n".join(
            f"{INDENT}{direction.title()} - {location.name}{f' (blocked by {game.current_location.exit_blockers[direction].name})' if game.current_location.exit_blockers.get(direction) is not None and game.current_location.exit_blockers[direction].health > 0 else ''}"
            for direction, location in game.current_location.exits.items()
        ),
        "",
    ]
    if game.current_location.characters == []:
        look_list.append("Nearby: no one")
    else:
        look_list.append("Nearby:")
        look_list.append(
            "\n".join(
                f"{INDENT}{character.name}{' - defeated' if character.health == 0 else ''}"
                for character in game.current_location.characters
            )
        )
    look_list.append("")
    if game.current_location.items == []:
        look_list.append("On the ground: nothing")
    else:
        look_list.append("On the ground:")
        look_list.append(
            "\n".join(
                f"{INDENT}{item.name} - {item.description}"
                for item in game.current_location.items
            )
        )
    # look_list.append("")
    print("\n".join(look_list))


def show_place_description(game: Game) -> str:
    centered_name = game.current_location.name.center(DASH_LINE_LEN)
    wrapped_description = textwrap.fill(
        game.current_location.description, width=DASH_LINE_LEN
    )

    return f"{DASH_LINE}\n{centered_name}\n{DASH_LINE}\n{wrapped_description}"
