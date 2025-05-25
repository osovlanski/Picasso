from enum import Enum, IntEnum
from itertools import permutations

class Floor(IntEnum):
    First = 1
    Second = 2
    Third = 3
    Fourth = 4
    Fifth = 5

class Color(Enum):
    Red = 'Red'
    Green = 'Green'
    Blue = 'Blue'
    Yellow = 'Yellow'
    Orange = 'Orange'

class Animal(Enum):
    Frog = 'Frog'
    Rabbit = 'Rabbit'
    Grasshopper = 'Grasshopper'
    Bird = 'Bird'
    Chicken = 'Chicken'

class AttributeType(Enum):
    Floor = 'Floor'
    Color = 'Color'
    Animal = 'Animal'

class Piccaso:
    """Represents the state of the Piccaso puzzle, tracking possible floors for colors and animals"""    
    def __init__(self):
        self.floors_number = len(Floor)
        self.color_floors = {color: set(range(1, self.floors_number+1)) for color in Color}
        self.animal_floors = {animal: set(range(1, self.floors_number+1)) for animal in Animal}

        # Track which attributes are assigned to which floors
        self.floor_colors = {}  # floor -> color (if uniquely determined)
        self.floor_animals = {}  # floor -> animal (if uniquely determined)

    def get_state(self):
        """Get current state for comparison"""
        return (
            {c: f.copy() for c, f in self.color_floors.items()},
            {a: f.copy() for a, f in self.animal_floors.items()}
        )
    
    def get_possible_floors(self, attr):
        """Get set of possible floors for an attribute"""
        if isinstance(attr, Floor):
            return {int(attr)}
        elif isinstance(attr, Color):
            return self.color_floors[attr].copy()
        elif isinstance(attr, Animal):
            return self.animal_floors[attr].copy()
        
    def set_possible_floors(self, attr, floors):
        """Set possible floors for an attribute"""
        if isinstance(attr, Color):
            self.color_floors[attr] = floors.copy()
        elif isinstance(attr, Animal):
            self.animal_floors[attr] = floors.copy()
        # Floor attributes are fixed
            
    def assign_to_floor(self, attr, floor):
        """Assign an attribute to a specific floor and propagate"""
        if isinstance(attr, Color):
            self.floor_colors[floor] = attr
            # Remove this floor from other colors
            for other_color in Color:
                if other_color != attr:
                    self.color_floors[other_color].discard(floor)
        elif isinstance(attr, Animal):
            self.floor_animals[floor] = attr
            # Remove this floor from other animals
            for other_animal in Animal:
                if other_animal != attr:
                    self.animal_floors[other_animal].discard(floor)

class FloorAssignment(object):
    """Represents a complete assignment of colors and animals to floors"""
    
    def __init__(self, animal: Animal, color: Color):
        """
        Args:
            animal: Animal assigned to the floor
            color: Color assigned to the floor
        """
        self.animal = animal
        self.color = color
    
class FloorsAssignment(object):    

    def __init__(self, floor_animals: dict[int, Color], floor_colors: dict[int, Color]):
        """
        Args:
            floors: List of FloorAssignment objects for each floor
        """
        self.floors_assignment = {floor: FloorAssignment(floor_animals.get(floor), floor_colors.get(floor)) for floor in range(1, len(Floor) + 1)}
        self.animal_to_floor = {v.animal: k for k, v in self.floors_assignment.items() if v.animal is not None}
        self.color_to_floor = {v.color: k for k, v in self.floors_assignment.items() if v.color is not None}
        self.attr_to_floor = {
            **{color: floor for floor, color in floor_colors.items()},
            **{animal: floor for floor, animal in floor_animals.items()},
            **{floor: floor for floor in range(1, len(Floor) + 1)}
        }

    def get_assigned_floor(self, attr):
        return self.attr_to_floor[attr]

class Hint(object):
    """Base class for all the hint classes"""
    def is_consistent(self) -> bool:
        raise NotImplementedError
    def propagate(self, picasso: Piccaso) -> bool:
        raise NotImplementedError
    def satisfies(self, floors_assignment: FloorsAssignment) -> bool:
        raise NotImplementedError
    

class AbsoluteHint(Hint):
    """
    Represents a hint on a specific floor. Examples:
    The third floor is red:
        AbsoluteHint(Floor.Third, Color.Red)
    The frog lives on the fifth floor:
        AbsoluteHint(Animal.Frog, Floor.Fifth)
    The orange floor is the floor where the chicken lives:
        AbsoluteHint(Color.Orange, Animal.Chicken)
    """
    def __init__(self, attr1, attr2):
        self._attr1 = attr1
        self._attr2 = attr2

    def is_consistent(self):
        # Cannot bind something to itself (nonsensical)
        return self._attr1 != self._attr2

    def propagate(self, picasso: Piccaso):
        """Apply constraint that attr1 and attr2 are on the same floor"""
        floors1 = picasso.get_possible_floors(self._attr1)
        floors2 = picasso.get_possible_floors(self._attr2)
        
        # They must be on same floor - intersect possibilities
        common_floors = floors1 & floors2
        if not common_floors:
            return False  # Impossible
        
        # Update domains
        picasso.set_possible_floors(self._attr1, common_floors)
        picasso.set_possible_floors(self._attr2, common_floors)
        
        # If there's only one possible floor, enforce the assignment
        if len(common_floors) == 1:
            floor = next(iter(common_floors))
            picasso.assign_to_floor(self._attr1, floor)
            picasso.assign_to_floor(self._attr2, floor)
        
        return True
    
    def satisfies(self, floors_assignment: FloorsAssignment):
        floor1 = floors_assignment.get_assigned_floor(self._attr1)
        floor2 = floors_assignment.get_assigned_floor(self._attr2)
        return floor1 == floor2

class RelativeHint(Hint):
    """
    Represents a hint of a relation between two floor
    that are of a certain distance of each other.
    Examples:
    The red floor is above the blue floor:
        RelativeHint(Color.Red, Color.Blue, 1)
    The frog lives three floor below the yellow floor:
        RelativeHint(Animal.Frog, Color.Yellow, -3)
    The third floor is two floors below the fifth floor:
        RelativeHint(Floor.Third, Floor.Fifth, -2)
    """
    def __init__(self, attr1, attr2, difference):
        self._attr1 = attr1
        self._attr2 = attr2
        self._difference = difference

    def is_consistent(self):
        # Only validate if both are floors
        if self._attr1 == self._attr2:
            return self._difference == 0
    
        # If both are floors, validate the math
        if isinstance(self._attr1, Floor) and isinstance(self._attr2, Floor):
            return int(self._attr1) - int(self._attr2) == self._difference
        
        # General rule for floors: the difference must be within the range of valid floor indices
        return abs(self._difference) < len(Floor)  # floor diff can't be higher than the number of floors

    def propagate(self, picasso: Piccaso):
        """Apply constraint that attr1 - difference = attr2 (in terms of floors)"""
        floors1 = picasso.get_possible_floors(self._attr1)
        floors2 = picasso.get_possible_floors(self._attr2)
        
        # For attr1: only floors where floor - difference is in floors2
        valid_floors1 = {f for f in floors1 if f - self._difference in floors2}
        # For attr2: only floors where floor + difference is in floors1  
        valid_floors2 = {f for f in floors2 if f + self._difference in floors1}
        
        if not valid_floors1 or not valid_floors2:
            return False
        
        picasso.set_possible_floors(self._attr1, valid_floors1)
        picasso.set_possible_floors(self._attr2, valid_floors2)
        
        return True
    
    def satisfies(self, floors_assignment: FloorsAssignment):
        attr1, attr2 = self._attr1, self._attr2
        floor1 = floors_assignment.get_assigned_floor(attr1)
        floor2 = floors_assignment.get_assigned_floor(attr2)
        difference = self._difference
        return floor1 - difference == floor2


class NeighborHint(Hint):
    """
    Represents a hint of a relation between two floors that are adjacent
    (first either above or below the second).
    Examples:
    The green floor is neighboring the floor where the chicken lives:
        NeighborHint(Color.Green, Animal.Chicken)
    The grasshopper is a neighbor of the rabbit:
        NeighborHint(Animal.Grasshopper, Animal.Rabbit)
    The yellow floor is neighboring the third floor:
        NeighborHint(Color.Yellow, Floor.Third)
    """
    def __init__(self, attr1, attr2):
        self._attr1 = attr1
        self._attr2 = attr2

    def is_consistent(self):
        return self._attr1 != self._attr2

    def propagate(self, picasso: Piccaso):
        """Apply constraint that attr1 and attr2 are on adjacent floors"""
        floors1 = picasso.get_possible_floors(self._attr1)
        floors2 = picasso.get_possible_floors(self._attr2)
        
        # For attr1: only floors that have a neighbor in floors2
        valid_floors1 = set()
        for f in floors1:
            if (f-1 in floors2) or (f+1 in floors2):
                valid_floors1.add(f)
        
        # For attr2: only floors that have a neighbor in floors1
        valid_floors2 = set()
        for f in floors2:
            if (f-1 in floors1) or (f+1 in floors1):
                valid_floors2.add(f)
        
        if not valid_floors1 or not valid_floors2:
            return False
        
        picasso.set_possible_floors(self._attr1, valid_floors1)
        picasso.set_possible_floors(self._attr2, valid_floors2)
        
        return True
    
    def satisfies(self, floors_assignment: FloorsAssignment):
        attr1, attr2 = self._attr1, self._attr2
        floor1 = floors_assignment.get_assigned_floor(attr1)
        floor2 = floors_assignment.get_assigned_floor(attr2)
        return abs(floor1 - floor2) == 1

class PiccasoSolver:
    def __init__(self):
        self.picasso = Piccaso()


    def propagate_constraints(self, hints: list[Hint]) -> bool:
        """Apply all hints with constraint propagation until convergence"""
        if not all(h.is_consistent() for h in hints):
            return False    

        prev_state = None

        while True:
            current_state = self.picasso.get_state()

            if current_state == prev_state:
                break  # No more changes — fixpoint reached

            prev_state = current_state

            for hint in hints:
                if not hint.propagate(self.picasso):
                    return False

            # After processing all hints, check for unique assignments
            for color in Color:
                if len(self.picasso.color_floors[color]) == 1:
                    floor = next(iter(self.picasso.color_floors[color]))
                    if floor not in self.picasso.floor_colors:
                        self.picasso.assign_to_floor(color, floor)

            for animal in Animal:
                if len(self.picasso.animal_floors[animal]) == 1:
                    floor = next(iter(self.picasso.animal_floors[animal]))
                    if floor not in self.picasso.floor_animals:
                        self.picasso.assign_to_floor(animal, floor)

        
        return True
            
    def count_valid_assignments(self, hints: list[Hint]) -> int:
        unassigned_colors = set(c for c in Color if c not in self.picasso.floor_colors.values())
        unassigned_animals = set(a for a in Animal if a not in self.picasso.floor_animals.values())

        unassigned_colors_floors = set(f for f in Floor if f not in self.picasso.floor_colors)
        unassigned_animals_floors = set(f for f in Floor if f not in self.picasso.floor_animals)

        # use permutations to generate all possible assignments        
        count = 0
        for color_perm in permutations(unassigned_colors):
            for animal_perm in permutations(unassigned_animals):
                # Create a temporary assignment
                trial_color_floors = self.picasso.floor_colors.copy()
                trial_animal_floors = self.picasso.floor_animals.copy()
                
                # Assign colors and animals to floors
                for c, floor in zip(color_perm, unassigned_colors_floors):                    
                    trial_color_floors[int(floor)] = c

                for a, floor in zip(animal_perm, unassigned_animals_floors):
                    trial_animal_floors[int(floor)] = a
                
                # Check if this assignment satisfies all hints
                floors_assignment = FloorsAssignment(trial_animal_floors, trial_color_floors)
                if all(hint.satisfies(floors_assignment) for hint in hints):
                    count += 1

        return count

# Test cases - corrected based on problem description
HINTS_EX1 = [
    AbsoluteHint(Animal.Rabbit, Floor.First),           
    AbsoluteHint(Animal.Chicken, Floor.Second),         
    AbsoluteHint(Floor.Third, Color.Yellow),            
    AbsoluteHint(Animal.Bird, Floor.Fifth),             
    AbsoluteHint(Animal.Grasshopper, Color.Blue),       
    NeighborHint(Color.Red, Color.Green),               
]

HINTS_EX2 = [
    AbsoluteHint(Animal.Bird, Floor.Fifth),
    AbsoluteHint(Floor.First, Color.Green),
    AbsoluteHint(Animal.Frog, Color.Yellow),
    NeighborHint(Animal.Frog, Animal.Grasshopper),
    NeighborHint(Color.Red, Color.Orange),
    RelativeHint(Animal.Chicken, Color.Blue, -4)
]

HINTS_EX3 = [
    RelativeHint(Animal.Rabbit, Color.Green, -2)
]

# expects floor! * floor! = 5! * 5! = 120 * 120 = 14400
HINTS_EX4 = []

# expects 0 due to the conflicting hints (red can't be both 1 and 2)
HINTS_EX5 = [
    AbsoluteHint(Color.Red, Floor.First),
    AbsoluteHint(Color.Red, Floor.Second),
]

# expects 120 due to the conflicting hints being removed
HINTS_EX6 = [
    AbsoluteHint(Floor.First, Color.Red),
    AbsoluteHint(Floor.Second, Color.Green),
    NeighborHint(Color.Red, Color.Green)
]

# expects 0 due to the conflicting hints (green can't be both 5 and 1)
HINTS_EX7 = [    
    RelativeHint(Animal.Chicken, Color.Green, 5)
]

# expects 
HINTS_EX8 = [
    AbsoluteHint(Floor.First, Color.Red),
    AbsoluteHint(Floor.First, Color.Green)
]
                            
def count_assignments(hints):
    """
    Given a list of Hint objects, return the number of
    valid assignments that satisfy these hints.
    Uses efficient constraint propagation when possible.
    """
    solver = PiccasoSolver()
    if not solver.propagate_constraints(hints):
        return 0
    return solver.count_valid_assignments(hints)

def test():
    assert count_assignments(HINTS_EX1) == 2, 'Failed on example #1'
    assert count_assignments(HINTS_EX2) == 4, 'Failed on example #2'
    assert count_assignments(HINTS_EX3) == 1728, 'Failed on example #3'
    assert count_assignments(HINTS_EX4) == 14400, 'Failed on example #4'
    assert count_assignments(HINTS_EX5) == 0, 'Failed on example #5'
    assert count_assignments(HINTS_EX6) == 720, 'Failed on example #6'
    assert count_assignments(HINTS_EX7) == 0, 'Failed on example #7'
    assert count_assignments(HINTS_EX8) == 0, 'Failed on example #8'
    
    print('\nAll tests passed!')
    
if __name__ == '__main__':
    test()