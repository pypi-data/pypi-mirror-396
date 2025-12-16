from __future__ import annotations
import ostk.core.type
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.environment.object
import ostk.physics.time
import typing
__all__ = ['Eclipse', 'EclipsePhase', 'eclipse_intervals_at_position', 'montenbruck_gill_shadow_function']
class Eclipse:
    """
    
                Eclipse.
                
                This class represents an eclipse event between two celestial objects,
                containing information about the occulted and occulting objects, as well
                as the phases of the eclipse.
            
    """
    def __init__(self, occulted_celestial_object: ostk.physics.environment.object.Celestial, occulting_celestial_object: ostk.physics.environment.object.Celestial, phases: list[EclipsePhase]) -> None:
        """
                        Constructor
        
                        Args:
                            occulted_celestial_object (Celestial): The occulted celestial object.
                            occulting_celestial_object (Celestial): The occulting celestial object.
                            phases (list[EclipsePhase]): The phases of the eclipse.
        
                        Raises:
                            RuntimeError: If the phases are not contiguous.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_duration(self, include_penumbra: bool = True) -> ostk.physics.time.Duration:
        """
                        Get the duration of the eclipse.
        
                        Args:
                            include_penumbra (bool, optional): Whether to include the penumbra phases. Defaults to True.
        
                        Returns:
                            Duration: The duration of the eclipse.
        """
    def get_interval(self, include_penumbra: bool = True) -> ostk.physics.time.Interval:
        """
                        Get the interval of the eclipse.
        
                        Args:
                            include_penumbra (bool, optional): Whether to include the penumbra phases. Defaults to True.
        
                        Returns:
                            Interval: The interval of the eclipse. Returns Interval::Undefined() if there are no umbra phases
                                    and penumbras are not included.
        
                        Raises:
                            RuntimeError: If there are multiple umbra phases and penumbras are not included.
        """
    def get_occulted_celestial_object(self) -> ostk.physics.environment.object.Celestial:
        """
                        Get the occulted celestial object.
        
                        Returns:
                            Celestial: The occulted celestial object.
        """
    def get_occulting_celestial_object(self) -> ostk.physics.environment.object.Celestial:
        """
                        Get the occulting celestial object.
        
                        Returns:
                            Celestial: The occulting celestial object.
        """
    def get_phases(self) -> list[EclipsePhase]:
        """
                        Get the phases of the eclipse.
        
                        Returns:
                            list[EclipsePhase]: The phases of the eclipse.
        """
class EclipsePhase:
    """
    
                Phase of an eclipse.
                
                This class represents a single phase of an eclipse, including the region type
                (umbra or penumbra), the time interval, and whether the phase is complete.
            
    """
    class Region:
        """
        Members:
        
          Umbra
        
          Penumbra
        """
        Penumbra: typing.ClassVar[EclipsePhase.Region]  # value = <Region.Penumbra: 1>
        Umbra: typing.ClassVar[EclipsePhase.Region]  # value = <Region.Umbra: 0>
        __members__: typing.ClassVar[dict[str, EclipsePhase.Region]]  # value = {'Umbra': <Region.Umbra: 0>, 'Penumbra': <Region.Penumbra: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: EclipsePhase) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (EclipsePhase): Other EclipsePhase.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, region: EclipsePhase.Region, interval: ostk.physics.time.Interval, is_complete: bool) -> None:
        """
                        Constructor
        
                        Args:
                            region (EclipsePhase.Region): The region of the eclipse phase (Umbra or Penumbra).
                            interval (Interval): The time interval of the phase.
                            is_complete (bool): Whether the phase is complete.
        """
    def __ne__(self, arg0: EclipsePhase) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (EclipsePhase): Other EclipsePhase.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        The time interval of the phase.
        """
    def get_region(self) -> EclipsePhase.Region:
        """
                        The region of the eclipse phase (Umbra or Penumbra).
        """
    def is_complete(self) -> bool:
        """
                        Whether the phase is complete.
        """
def eclipse_intervals_at_position(analysis_interval: ostk.physics.time.Interval, position: ostk.physics.coordinate.Position, environment: ostk.physics.Environment, include_penumbra: bool = True, time_step: ostk.physics.time.Duration = ...) -> list[ostk.physics.time.Interval]:
    """
                Calculate eclipse intervals for a given position.
    
                Args:
                    analysis_interval (Interval): An analysis interval.
                    position (Position): A position.
                    environment (Environment): An environment.
                    include_penumbra (bool, optional): Whether to include penumbra phases. Defaults to True.
                    time_step (Duration, optional): The time step for analysis, the lower the more accurate the result will be. Defaults to one minute.
    
                Returns:
                    list[Interval]: Array of eclipse intervals for a given position.
    """
def montenbruck_gill_shadow_function(instant: ostk.physics.time.Instant, position: ostk.physics.coordinate.Position, occulted_celestial_object: ostk.physics.environment.object.Celestial, occulting_celestial_object: ostk.physics.environment.object.Celestial) -> ostk.core.type.Real:
    """
                Montenbruck-Gill shadow function.
    
                Reference: Montenbruck and Gill, Satellite Orbits: Models, Methods, and Applications, 4th edition, Springer.
    
                Args:
                    instant (Instant): The instant at which the shadow function is evaluated.
                    position (Position): The position for which the shadow function is evaluated.
                    occulted_celestial_object (Celestial): The occulted celestial object.
                    occulting_celestial_object (Celestial): The occulting celestial object.
    
                Returns:
                    float: The value of the shadow function (0.0 for umbra, 1.0 for fully illuminated, and between 0.0 and 1.0 for penumbra).
    """
