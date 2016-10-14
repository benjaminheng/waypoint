from unittest import TestCase
from waypoint.navigation.heading import calculate_turn_direction


class TestHeading(TestCase):
    def test_calculate_turn_direction(self):
        result = calculate_turn_direction(
            from_x=100,
            from_y=100,
            to_x=200,
            to_y=200,
            heading=30,
            north=0
        )
        self.assertEquals(('right', 15), result)

        result = calculate_turn_direction(
            from_x=200,
            from_y=200,
            to_x=100,
            to_y=100,
            heading=30,
            north=0
        )
        self.assertEquals(('left', 165), result)

    def test_calculate_turn_direction_with_normalized_north(self):
        result = calculate_turn_direction(
            from_x=100,
            from_y=100,
            to_x=200,
            to_y=200,
            heading=0,
            north=45
        )
        self.assertEquals(0, result[1])

        result = calculate_turn_direction(
            from_x=100,
            from_y=100,
            to_x=200,
            to_y=200,
            heading=30,
            north=180
        )
        self.assertEquals(('left', 165), result)

        result = calculate_turn_direction(
            from_x=100,
            from_y=100,
            to_x=200,
            to_y=200,
            heading=15,
            north=90
        )
        self.assertEquals(('left', 60), result)

        result = calculate_turn_direction(
            from_x=100,
            from_y=100,
            to_x=200,
            to_y=200,
            heading=180,
            north=90
        )
        self.assertEquals(('right', 135), result)
