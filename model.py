
from typing import List, Union

FLOOR_STR_SIZE = 4 + 2 + 1 # 7, current format is 'F: ' + TWO_CHARS + ')'
PASSENGER_STR_SIZE = 4 + (FLOOR_STR_SIZE*2) + 4 + 1 # 23, current format is '[P: ' + FLOOR + ' -> ' + FLOOR + ']'
ELEVATOR_STR_SIZE = PASSENGER_STR_SIZE + 2 # 25, current format is '|' + PASSENGER + '|'


class Floor:
    floor_id = None

    def __init__(self, floor_id: str):
        if floor_id is None:
            raise ValueError("ERROR: floor_id may not be None")
        self.floor_id = floor_id

    def __str__(self):
        return "(F: {0: >2s})".format(self.floor_id)


class Passenger:

    origin_floor = None
    desired_floor = None
    time_waiting_for_elevator = 0
    time_inside_elevator = 0

    def __init__(self, origin_floor: Union[str, Floor], desired_floor: Union[str, Floor], building):
        if building is None:
            raise ValueError("ERROR: building may not be None")
        if origin_floor is None:
            raise ValueError("ERROR: origin_floor may not be None")
        if desired_floor is None:
            raise ValueError("ERROR: desired_floor may not be None")
        origin_floor = origin_floor if type(origin_floor) == Floor else Floor(origin_floor)
        desired_floor = desired_floor if type(desired_floor) == Floor else Floor(desired_floor)
        if not building.floor_exists(origin_floor):
            raise ValueError("ERROR: origin_floor does not exist in the building")
        if not building.floor_exists(desired_floor):
            raise ValueError("ERROR: desired_floor does not exist in the building")
        if origin_floor == desired_floor:
            raise ValueError("ERROR: in order to be an Elevator Passenger, the person in question should want to go to another floor")
        self.origin_floor = origin_floor
        self.desired_floor = desired_floor

    def incr_elevator_wait_time(self):
        self.time_waiting_for_elevator += 1

    def incr_elevator_time(self):
        self.time_inside_elevator += 1

    def __str__(self):
        return "[P: {0} -> {1}]".format(self.origin_floor, self.desired_floor)


class Building:

    floors = []
    elevators = []
    passengers = []

    def __init__(self, floors: List[Union[str, Floor]]):
        self.floors = [
            floor if type(floor) == Floor else Floor(floor)
            for floor in floors
        ]

    def add_passenger(self, passenger: Passenger) -> None:
        self.passengers.append(passenger)

    def add_passengers(self, passengers: List[Passenger]) -> None:
        self.add_passenger(passengers.pop(0))
        if len(passengers) > 0:
            self.add_passengers(passengers)

    def build_elevator(self, elevator) -> None:
        self.elevators.append(elevator)

    def build_elevators(self, elevators=None, number=0) -> None:
        if elevators != None:
            self.build_elevator(elevators.pop(0))
            if len(elevators) > 0:
                self.build_elevators(elevators)
        elif number > 0:
            self.build_elevator(
                Elevator(building=self)
            )
            self.build_elevators(number=(number - 1))

    def floor_exists(self, floor: Floor) -> bool:
        return floor in self.floors

    def floor_distance(self, floor1, floor2) -> int:
        if self.floor_exists(floor1) and self.floor_exists(floor2):
            return abs(self.floors.index(floor1) - self.floors.index(floor2))
        else:
            return -1

    def get_vector_direction(self, floor1, floor2) -> str:
        vector = self.floors.index(floor2) - self.floors.index(floor1)
        if vector > 0:
            return "^" # going up
        elif vector < 0:
            return "v" # going down
        else:
            return " " # idling

    def get_starting_floor(self) -> Floor:
        if len(self.elevators) == 0:
            return self.floors[0]
        elif len(self.elevators) == 1:
            return self.floors[-1]
        elif len(self.elevators) == 2:
            middle_idx = len(self.floors)
            if middle_idx % 2 == 1:
                middle_idx -= 1
            middle_idx /= 2
            middle_idx = int(middle_idx)
            return self.floors[middle_idx]
        else:
            distances_between_elevators = list(
                filter(
                    lambda elevators_distance: elevators_distance['dist'] > 0,
                    [
                        {
                            'elevator1': elevator1,
                            'elevator2': elevator2,
                            'dist': self.floor_distance(
                                elevator1.current_floor,
                                elevator2.current_floor
                            )
                        }
                        for elevator1 in self.elevators[0:-2]
                            for elevator2 in self.elevators[1:-1]
                    ]
                )
            )
            if len(distances_between_elevators) > 0:
                max_distance = max(
                    map(lambda ed: ed['dist'], distances_between_elevators)
                )
                first_max_dist = filter(
                    lambda ed: ed['dist'] == max_distance,
                    distances_between_elevators
                ).next()
                min_floor = min(
                    self.floors.index(first_max_dist['elevator1'].current_floor),
                    self.floors.index(first_max_dist['elevator2'].current_floor),
                )
                if max_distance % 2 == 0:
                    return self.floors[min_floor + int(max_distance / 2)]
                else:
                    return self.floors[min_floor + int((max_distance - 1) / 2)]
            else:
                middle_idx = len(self.floors)
                if middle_idx % 2 == 1:
                    middle_idx -= 1
                middle_idx /= 2
                middle_idx = int(middle_idx)
                return self.floors[middle_idx]

    def get_floor_path(self, floor1: Floor, floor2: Floor) -> List[Floor]:
        idx_floor1 = self.floors.index(floor1)
        idx_floor2 = self.floors.index(floor2)
        if idx_floor1 < idx_floor2:
            return self.floors[idx_floor1+1:idx_floor2+1]
        else:
            return self.floors[idx_floor2-1:idx_floor1-1:-1]

    def time_step(self) -> None:
        for passenger in self.passengers:
            passenger.incr_elevator_wait_time()
        for elevator in self.elevators:
            if len(elevator.passengers) > 0:
                for passenger in elevator.passengers:
                    passenger.incr_elevator_time()
                passengers_who_want_to_get_off = list(
                    filter(
                        lambda passenger: (
                            passenger.desired_floor ==
                            elevator.current_floor
                        ), elevator.passengers
                    )
                )
                if len(passengers_who_want_to_get_off) > 0:
                    elevator.unload_passenger(
                        passengers_who_want_to_get_off[-1]
                    )
                else:
                    passengers_who_want_to_get_on = list(
                        filter(
                            lambda passenger: (
                                passenger.origin_floor ==
                                elevator.current_floor
                            ) and (
                                elevator.current_vector == ' ' or
                                self.get_vector_direction(
                                    passenger.origin_floor,
                                    passenger.desired_floor
                                ) == elevator.current_vector
                            ),
                            self.passengers
                        )
                    )
                    if len(passengers_who_want_to_get_on) > 0:
                        elevator.load_passenger(
                            passenger=passengers_who_want_to_get_on[0],
                            building=self
                        )
                        self.passengers.remove(
                            passengers_who_want_to_get_on[0]
                        )
                    else:
                        if len(elevator.floor_path) == 0:
                            if elevator.desired_floor is None:
                                pending_passengers = self.passengers
                                for passenger in self.passengers:
                                    for inner_elevator in self.elevators:
                                        if passenger.origin_floor in inner_elevator.floor_path \
                                            and self.get_vector_direction(
                                                passenger.origin_floor, passenger.desired_floor
                                            ) == inner_elevator.current_vector:
                                            pending_passengers.remove(passenger)
                                distance_to_passengers = [
                                    {
                                        'passenger': passenger,
                                        'distance': self.floor_distance(
                                            elevator.current_floor, passenger.origin_floor
                                        )
                                    }
                                    for passenger in pending_passengers
                                ]
                                min_distance = min(
                                    map(
                                        lambda passenger_dist: passenger_dist['distance'],
                                        distance_to_passengers
                                    )
                                )
                                closest_passenger = list(filter(
                                    lambda passenger: passenger['distance'] == min_distance,
                                    distance_to_passengers
                                ))[0]
                                elevator.move_to_floor(
                                    floor=self.get_floor_path(
                                        elevator.current_floor,
                                        closest_passenger['passenger'].origin_floor
                                    )[0],
                                    desired_floor=closest_passenger['passenger'].origin_floor,
                                    building=self
                                )
                            else:
                                elevator.move_to_floor(
                                    floor=self.get_floor_path(
                                        elevator.current_floor,
                                        elevator.desired_floor
                                    )[0],
                                    building=self
                                )
                        else:
                            elevator.move_to_floor(
                                floor=elevator.floor_path[0],
                                building=self
                            )
            elif len(elevator.floor_path) > 0:
                passengers_who_want_to_get_on = list(
                    filter(
                        lambda passenger: (
                            passenger.origin_floor ==
                            elevator.current_floor
                        ) and (
                            elevator.current_vector == ' ' or
                            self.get_vector_direction(
                                passenger.origin_floor,
                                passenger.desired_floor
                            ) == elevator.current_vector
                        ),
                        self.passengers
                    )
                )
                if len(passengers_who_want_to_get_on) > 0:
                    elevator.load_passenger(
                        passenger=passengers_who_want_to_get_on[0],
                        building=self
                    )
                    building.passengers.remove(
                        passengers_who_want_to_get_on[0]
                    )
                else:
                    elevator.move_to_floor(
                        floor=elevator.floor_path[0],
                        building=self
                    )
            elif len(self.passengers) > 0:
                passengers_who_want_to_get_on = list(
                    filter(
                        lambda passenger: (
                            passenger.origin_floor ==
                            elevator.current_floor
                        ) and (
                            elevator.current_vector == ' ' or
                            self.get_vector_direction(
                                passenger.origin_floor,
                                passenger.desired_floor
                            ) == elevator.current_vector
                        ),
                        self.passengers
                    )
                )
                if len(passengers_who_want_to_get_on) > 0:
                    elevator.load_passenger(
                        passenger=passengers_who_want_to_get_on[0],
                        building=self
                    )
                    self.passengers.remove(
                        passengers_who_want_to_get_on[0]
                    )
                else:
                    pending_passengers = self.passengers
                    for passenger in self.passengers:
                        for inner_elevator in self.elevators:
                            if passenger.origin_floor in inner_elevator.floor_path \
                                and self.get_vector_direction(
                                    passenger.origin_floor, passenger.desired_floor
                                ) == inner_elevator.current_vector:
                                pending_passengers.remove(passenger)
                    distance_to_passengers = [
                        {
                            'passenger': passenger,
                            'distance': self.floor_distance(
                                elevator.current_floor, passenger.origin_floor
                            )
                        }
                        for passenger in pending_passengers
                    ]
                    min_distance = min(
                        map(
                            lambda passenger_dist: passenger_dist['distance'],
                            distance_to_passengers
                        )
                    )
                    closest_passenger = list(
                        filter(
                            lambda passenger: passenger['distance'] == min_distance,
                            distance_to_passengers
                        )
                    )[0]
                    elevator.move_to_floor(
                        floor=self.get_floor_path(
                            elevator.current_floor,
                            closest_passenger['passenger'].origin_floor
                        )[0],
                        desired_floor=closest_passenger['passenger'].origin_floor,
                        building=self
                    )
            else:
                # This is a simple and easy optimization, we reset idle
                # elevators in the middle of the building where they are closest
                # to all potential future passengers (assuming an even
                # distribution throughout the building). Further optimizations
                # are possible such as minimizing floor holes between elevators
                # (real time floor balancing) but that is beyond the current
                # scope of study.
                top_floor_idx = len(self.floors) - 1
                top_floor_idx = (
                    top_floor_idx
                    if top_floor_idx % 2 == 0
                    else (
                        top_floor_idx - 1
                    )
                )
                elevator.move_to_floor(
                    floor=self.get_floor_path(
                        elevator.current_floor,
                        self.floors[top_floor_idx / 2]
                    )[0],
                    desired_floor=self.floors[top_floor_idx / 2],
                    building=self
                )

    def __str__(self):
        floor_sep = ("-" * FLOOR_STR_SIZE)
        for e in range(len(self.elevators)):
            floor_sep += "+" + ("-" * (ELEVATOR_STR_SIZE - 2))
        floor_sep += "+" + ("-" * PASSENGER_STR_SIZE)
        building_str = floor_sep
        for floor in self.floors:
            floor_str = floor_sep + "\n" + str(floor) + "|"
            elevators_on_this_floor = list(filter(
                lambda elevator: elevator.current_floor == floor,
                self.elevators
            ))
            max_elevator_passengers = 0
            if len(elevators_on_this_floor) > 0:
                max_elevator_passengers = max(
                    map(
                        lambda elevator: len(elevator.passengers),
                        elevators_on_this_floor
                    )
                )
            passengers_on_this_floor = list(
                filter(
                    lambda passenger: passenger.origin_floor == floor,
                    self.passengers
                )
            )
            num_of_floor_lines = max(
                max_elevator_passengers, len(passengers_on_this_floor), 1
            )
            for line_num in range(num_of_floor_lines):
                if line_num > 0:
                    floor_str += (" " * FLOOR_STR_SIZE) + "|"
                for elevator in self.elevators:
                    if elevator.current_floor == floor:
                        if len(elevator.passengers) > 0:
                            if line_num < len(elevator.passengers):
                                floor_str += str(elevator.passengers[line_num])
                            else:
                                if line_num == (num_of_floor_lines - 1):
                                    floor_str += "*" * PASSENGER_STR_SIZE
                                else:
                                    floor_str += "*" + (" " * (PASSENGER_STR_SIZE - 2)) + "*"
                        else:
                            if line_num == 0 or line_num == (
                                num_of_floor_lines - 1
                            ):
                                floor_str += "*" * PASSENGER_STR_SIZE
                            else:
                                floor_str += "*" + (" " * (PASSENGER_STR_SIZE - 2)) + "*"
                    else:
                        floor_str += " " * PASSENGER_STR_SIZE
                    floor_str += "|"
                if line_num < len(passengers_on_this_floor):
                    floor_str += str(passengers_on_this_floor[line_num])
                floor_str += "\n"
            building_str = floor_str + building_str
        return building_str


class Elevator:

    current_floor = None
    desired_floor = None # no current destination
    destination_floors = []
    floor_path = []
    passengers = []
    current_vector = " " # neutral / idle

    def __init__(self, building: Building):
        if building is None:
            raise ValueError("ERROR: building may not be None")
        self.current_floor = building.get_starting_floor()

    def move_to_floor(self, floor: Floor, vector: str=None, desired_floor: Floor=None, building: Building=None) -> None:
        self.current_floor = floor
        if floor in self.destination_floors:
            self.destination_floors.remove(floor)
        if desired_floor is not None:
            self.desired_floor = desired_floor
            self.floor_path = building.get_floor_path(self.current_floor, self.desired_floor)
            self.current_vector = building.get_vector_direction(self.current_floor, self.desired_floor)
        if vector is not None:
            self.vector = vector
        if self.desired_floor == floor:
            self.desired_floor = None
            self.current_vector = " "

    def load_passenger(self, passenger: Passenger, building: Building) -> None:
        self.passengers.append(passenger)
        if self.desired_floor is not None:
            current_vector_distance = building.floor_distance(
                self.current_floor, self.desired_floor
            )
            new_vector_distance = building.floor_distance(
                self.current_floor, passenger.desired_floor
            )
            if new_vector_distance > current_vector_distance:
                self.desired_floor = passenger.desired_floor
                self.floor_path = building.get_floor_path(self.current_floor, self.desired_floor)
        else:
            self.desired_floor = passenger.desired_floor
            self.floor_path = building.get_floor_path(self.current_floor, self.desired_floor)
        if passenger.desired_floor not in self.destination_floors:
            self.destination_floors.append(passenger.desired_floor)
            self.destination_floors = sorted(
                self.destination_floors,
                key=lambda floor: building.floor_distance(
                    self.current_floor, floor
                )
            )
        if self.current_vector == " ":
            self.current_vector = building.get_vector_direction(
                self.current_floor, self.desired_floor
            )

    def unload_passenger(self, passenger: Passenger) -> None:
        print("Time waiting, Time inside Elevator = {0}, {1}".format(
                passenger.time_waiting_for_elevator,
                passenger.time_inside_elevator
            )
        )
        self.passengers.remove(passenger)
