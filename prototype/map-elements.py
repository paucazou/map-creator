from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

class Climate(Enum):
    TROPICAL = "tropical"
    TEMPERATE = "temperate"
    CONTINENTAL = "continental"
    POLAR = "polar"
    ARID = "arid"

class TerrainType(Enum):
    FLATLAND = "flatland"
    HILLS = "hills"
    MOUNTAINS = "mountains"
    DESERT = "desert"
    FOREST = "forest"
    JUNGLE = "jungle"
    TUNDRA = "tundra"
    SWAMP = "swamp"

@dataclass
class Coordinates:
    x: float
    y: float

@dataclass
class Altitude:
    """Represents altitude with minimum, maximum, and mean heights"""
    min_height: float = 0.0
    max_height: float = 0.0
    mean_height: float = 0.0

    def set_min_height(self, value: float):
        """Setter for minimum height"""
        self.min_height = value

    def set_max_height(self, value: float):
        """Setter for maximum height"""
        self.max_height = value

    def set_mean_height(self, value: float):
        """Setter for mean height"""
        self.mean_height = value

class MapElement(ABC):
    def __init__(self, 
                 name: str = "Unnamed", 
                 coordinates: Optional[List[Coordinates]] = None):
        self._name = name
        self._coordinates = coordinates or [Coordinates(0.0, 0.0)]
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    @property
    def coordinates(self) -> List[Coordinates]:
        return self._coordinates
    
    @coordinates.setter
    def coordinates(self, value: List[Coordinates]):
        self._coordinates = value
        
    @abstractmethod
    def get_description(self) -> str:
        pass

class GeographicalFeature(MapElement):
    def __init__(self, 
                 name: str = "Unnamed Feature", 
                 coordinates: Optional[List[Coordinates]] = None,
                 altitude: Optional[Altitude] = None):
        super().__init__(name, coordinates)
        self._altitude = altitude or Altitude()
        
    @property
    def altitude(self) -> Altitude:
        return self._altitude
    
    @altitude.setter
    def altitude(self, value: Altitude):
        self._altitude = value

class Mountain(GeographicalFeature):
    def __init__(self, 
                 name: str = "Unnamed Mountain", 
                 coordinates: Optional[List[Coordinates]] = None,
                 altitude: Optional[Altitude] = None):
        super().__init__(name, coordinates, altitude)
        
    def get_description(self) -> str:
        return (f"{self.name} is a mountain "
                f"with max height of {self.altitude.max_height}m")

class City(MapElement):
    def __init__(self, 
                 name: str = "Unnamed City", 
                 coordinates: Optional[List[Coordinates]] = None,
                 population: int = 0,
                 is_capital: bool = False):
        super().__init__(name, coordinates)
        self._population = population
        self._is_capital = is_capital
        
    @property
    def population(self) -> int:
        return self._population
    
    @population.setter
    def population(self, value: int):
        if value >= 0:
            self._population = value
        else:
            raise ValueError("Population cannot be negative")
    
    @property
    def is_capital(self) -> bool:
        return self._is_capital
    
    @is_capital.setter
    def is_capital(self, value: bool):
        self._is_capital = value
    
    def get_description(self) -> str:
        capital_status = "capital" if self.is_capital else "city"
        return (f"{self.name} is a {capital_status} "
                f"with population of {self.population}")

class Biome(GeographicalFeature):
    def __init__(self, 
                 name: str = "Unnamed Biome", 
                 coordinates: Optional[List[Coordinates]] = None,
                 climate: Climate = Climate.TEMPERATE,
                 terrain: TerrainType = TerrainType.FLATLAND):
        super().__init__(name, coordinates)
        self._climate = climate
        self._terrain = terrain
        
    @property
    def climate(self) -> Climate:
        return self._climate
    
    @climate.setter
    def climate(self, value: Climate):
        self._climate = value
    
    @property
    def terrain(self) -> TerrainType:
        return self._terrain
    
    @terrain.setter
    def terrain(self, value: TerrainType):
        self._terrain = value
        
    def get_description(self) -> str:
        return (f"{self.name} is a {self.climate.value} "
                f"biome with {self.terrain.value} terrain")

# Example usage
if __name__ == "__main__":
    # Create a mountain with default and custom values
    everest = Mountain(
        name="Mount Everest",
        coordinates=[Coordinates(27.9881, 86.9250)],
        altitude=Altitude(min_height=8000, max_height=8848.86, mean_height=8300)
    )
    
    # Create a city
    paris = City(
        name="Paris",
        coordinates=[Coordinates(48.8566, 2.3522)],
        population=2161000,
        is_capital=True
    )
    
    # Demonstrate setters
    paris.population = 2200000
    everest.name = "Mount Everest (Sagarmatha)"
    
    # Print descriptions
    print(everest.get_description())
    print(paris.get_description())
