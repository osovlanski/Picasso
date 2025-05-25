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

class Hint(object):
    """Base class for all the hint classes"""
    # pass
    def satisfies(self, assignment: "Assignment") -> bool:
        raise NotImplementedError

    def is_consistent(self) -> bool:
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

    def satisfies(self, assignment):
        return assignment.get_floor_of_attribute(self._attr1) == assignment.get_floor_of_attribute(self._attr2)
    
    def is_consistent(self):
        # Cannot bind something to itself (nonsensical)
        return self._attr1 != self._attr2

        
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

    def satisfies(self, assignment):
        f1 = assignment.get_floor_of_attribute(self._attr1)
        f2 = assignment.get_floor_of_attribute(self._attr2)
        return f1 - self._difference == f2

    def is_consistent(self):
        # Only validate if both are floors
        if self._attr1 == self._attr2:
            return self._difference == 0
    
        # If both are floors, validate the math
        if isinstance(self._attr1, Floor) and isinstance(self._attr2, Floor):
            return int(self._attr1) - int(self._attr2) == self._difference
        
        # General rule for floors: the difference must be within the range of valid floor indices
        return abs(self._difference) < len(Floor)  # floor diff can't be 5 or more

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

    def satisfies(self, assignment):
        f1 = assignment.get_floor_of_attribute(self._attr1)
        f2 = assignment.get_floor_of_attribute(self._attr2)
        return abs(f1 - f2) == 1

    def is_consistent(self):
        return self._attr1 != self._attr2

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

class Assignment:
    """Represents a complete assignment of colors and animals to floors"""
    
    def __init__(self, color_assignment, animal_assignment):
        """
        Args:
            color_assignment: tuple of N colors (floor 1 to N)
            animal_assignment: tuple of N animals (floor 1 to N)
        """
        self.colors = color_assignment
        self.animals = animal_assignment
        
        # Create lookup dictionaries for efficiency
        self.color_to_floor = {color: i + 1 for i, color in enumerate(color_assignment)}
        self.animal_to_floor = {animal: i + 1 for i, animal in enumerate(animal_assignment)}
    
    def get_floor_of_attribute(self, attr):
        """Return the floor number (1-N) where the given attribute is located"""
        if isinstance(attr, Floor):
            return int(attr)
        elif isinstance(attr, Color):
            return self.color_to_floor[attr]
        elif isinstance(attr, Animal):
            return self.animal_to_floor[attr]
        else:
            raise ValueError(f"Unknown attribute type: {type(attr)}")

def satisfies_all_hints(assignment, hints):
    """Check if assignment satisfies all given hints"""
    return all(h.satisfies(assignment) for h in hints)

def count_assignments(hints):
    """
    Given a list of Hint objects, return the number of
    valid assignments that satisfy these hints.
    Note: in case there are some conflicting hints, the function should return 0.
    """
    
    if not all(h.is_consistent() for h in hints):
        return 0    
    valid_count = 0
    
    # Generate all permutations of colors and animals
    for color_perm in permutations(Color):
        for animal_perm in permutations(Animal):
            assignment = Assignment(color_perm, animal_perm)
            
            # Check if this assignment satisfies all hints
            if satisfies_all_hints(assignment, hints):
                valid_count += 1                
    
    return valid_count

def test():
    assert count_assignments(HINTS_EX1) == 2, 'Failed on example #1'
    assert count_assignments(HINTS_EX2) == 4, 'Failed on example #2'
    assert count_assignments(HINTS_EX3) == 1728, 'Failed on example #3'
    assert count_assignments(HINTS_EX4) == 14400, 'Failed on example #4'
    assert count_assignments(HINTS_EX5) == 0, 'Failed on example #5'
    assert count_assignments(HINTS_EX6) == 720, 'Failed on example #6'
    assert count_assignments(HINTS_EX7) == 0, 'Failed on example #7'
    assert count_assignments(HINTS_EX8) == 0, 'Failed on example #8'
    print('Success!')
    
if __name__ == '__main__':
    test()
