
import unittest
import random

from model import Building, Elevator, Floor, Passenger


class TestFloorClass(unittest.TestCase):

    def test_constructor(self):
        with self.assertRaises(ValueError):
            Floor(None)

    def test_str(self):
        self.assertEqual(str(Floor("1")),   "(F:  1)")
        self.assertEqual(str(Floor("LB")),  "(F: LB)")
        self.assertEqual(str(Floor("100")), "(F: 100)")


class TestPassengerClass(unittest.TestCase):

    def test_constructor(self):
        pass

    def test_elevator_wait_time(self):
        pass

    def test_elevator_time(self):
        pass

    def test_str(self):
        pass


class TestBuildingClass(unittest.TestCase):

    def test_constructor(self):
        pass

    def test_add_passenger(self):
        pass

    def test_add_passengers(self):
        pass

    def test_build_elevator(self):
        pass

    def test_build_elevators(self):
        pass

    def test_floor_exists(self):
        pass


class CompleteTestElevators(unittest.TestCase):

    building = None

    def setUp(self):
        print("")
        if self.building is None:
            self.building = Building(
                floors=(
                    [
                        Floor("G")
                    ] + [
                        Floor(str(num))
                        for num in range(1, 10)
                    ]
                )
            )
        if len(self.building.elevators) == 0:
            self.building.build_elevators(
                number=3
            )
        print(self.building)
        print("")

    def test_construct_building_3_elevators_10_floors(self):
        self.assertEqual(len(self.building.floors), 10)
        self.assertEqual(len(self.building.elevators), 3)

    def test_building_3_elevators_10_floors_serve_10_initial_random_passengers(self):
        print("")
        passenger_list = []
        for i in range(10):
            pick_two_floors = random.sample(self.building.floors, 2)
            passenger_list.append(Passenger(pick_two_floors[0], pick_two_floors[1], self.building))
        self.building.add_passengers(
            passengers=passenger_list
        )
        print(self.building)
        self.assertEqual(len(self.building.passengers), 10)
        instants = 0
        while instants < 100 and (
            len(self.building.passengers) > 0 or
            max(
                map(
                    lambda elevator: len(elevator.passengers),
                    self.building.elevators
                )
            ) > 0
        ):
            self.building.time_step()
            print(self.building)
            instants += 1
        self.assertNotEqual(instants, 100)
        self.assertEqual(len(self.building.passengers), 0)
        self.assertEqual(
            max(
                map(
                    lambda elevator: len(elevator.passengers),
                    self.building.elevators
                )
            ), 0
        )


if __name__ == '__main__':
    unittest.main()
