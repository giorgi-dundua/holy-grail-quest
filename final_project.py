class Game:
    def __init__(self) -> None:
        pass

    def move(self):
        pass

    def look(self):
        pass

    def talk(self):
        pass

    def status(self):
        pass


class Character:
    def __init__(self, name: str, max_health: int, attack_power: int) -> None:
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.attack_power = attack_power

    def attack(self, target: Character):
        pass

    def take_damage(self, damage: int):
        pass


class Enemy(Character):
    def __init__(self, name: str, max_health: int, attack_power: int) -> None:
        super().__init__(name, max_health, attack_power)


class Player(Character):
    def __init__(self, name: str, max_health: int, attack_power: int) -> None:
        super().__init__(name, max_health, attack_power)

        self.inventory = []

    def take(self, item):
        pass

    def drop(self, item):
        pass

    def use(self, item):
        pass


class Item:
    def __init__(self, name: str, effect) -> None:
        pass


class Location:
    def __init__(self, name: str, items: object, characters: object) -> None:
        pass
