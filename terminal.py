from game import CHAPTER_COMPLETE, GAME_OVER, WELCOME_MESSAGE, Game


def run(game: Game) -> None:
    """Repeat the command menu until the game state changes."""
    print(WELCOME_MESSAGE)
    print(game.show_place_description())

    while game.state == "Running":
        display_summary(game)
        available_actions = game.get_available_actions()

        choice_index = game.choose_option(
            available_actions,
            heading="Choose an action:",
        )

        if choice_index is not None:
            game.handle_action(user_action=available_actions[choice_index].lower())

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
