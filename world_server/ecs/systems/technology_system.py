from ..world import World
from ..components.state import StateComponent
from ..components.position import PositionComponent
from ..components.needs import NeedsComponent
from world_server.resource_manager import ResourceManager
from ..system import System


class TechnologySystem(System):
    """
    Manages the global technology level of the world.
    - Tracks technology points for different fields (e.g., Alchemy, Automata).
    - Upgrades technology levels when points thresholds are met.
    - Applies global buffs or changes based on technology levels.
    """
    def __init__(self):
        self.tech_levels = {
            "alchemy": {"level": 0, "points": 0, "next_level_cost": 100},
            "automata": {"level": 0, "points": 0, "next_level_cost": 100}
        }

    def add_tech_points(self, world: World, field: str, points: int):
        """Adds technology points to a specific field."""
        if field in self.tech_levels:
            self.tech_levels[field]["points"] += points
            # print(f"[TechSystem] Added {points} points to {field}. Total: {self.tech_levels[field]['points']}")
            self._check_for_level_up(world, field)

    def _check_for_level_up(self, world: World, field: str):
        """Checks if a technology field has enough points to level up."""
        tech = self.tech_levels[field]
        if tech["points"] >= tech["next_level_cost"]:
            tech["level"] += 1
            tech["points"] -= tech["next_level_cost"]
            tech["next_level_cost"] = int(tech["next_level_cost"] * 2.5) # Increase cost for next level
            print(f"[TechSystem] {field.upper()} has leveled up to Level {tech['level']}!")
            self._apply_tech_effects(world)

    def _apply_tech_effects(self, world: World):
        """Applies the passive effects of the current technology levels."""
        # --- Automata Effect ---
        automata_level = self.tech_levels["automata"]["level"]
        ResourceManager.production_multiplier = 1.0 + (automata_level * 0.2)
        if automata_level > 0:
            print(f"[TechSystem] Automata Lvl {automata_level}: Production multiplier is now {ResourceManager.production_multiplier:.2f}x")

        # --- Alchemy Effect ---
        alchemy_level = self.tech_levels["alchemy"]["level"]
        if alchemy_level > 0:
            bonus = alchemy_level * 0.05 # 5% stress resistance per level
            entities_with_needs = world.get_entities_with_components(NeedsComponent)
            for entity_id in entities_with_needs:
                needs = world.get_component(entity_id, NeedsComponent)
                needs.alchemy_bonus['stress_resistance'] = bonus
            print(f"[TechSystem] Alchemy Lvl {alchemy_level}: All entities now have {bonus:.2f}% stress resistance.")

    def process(self, *args, **kwargs):
        # The main processing loop for this system might not be needed if it's event-driven.
        # For now, we'll leave it passive. Points will be added from other systems (like ActionSystem).
        pass