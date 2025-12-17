import unittest

from tna_utilities.url import QueryStringTransformer


class TestQueryStringObject:
    def lists(self):
        return iter(
            [
                ("a", ["1"]),
                ("b", ["2", "3"]),
            ]
        )


class TestQuery(unittest.TestCase):
    def test_init(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.get_query_string(), "?a=1&b=2&b=3")

    def test_parameter_values(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.parameter_values("a"), ["1"])
        self.assertEqual(manipulator.parameter_values("b"), ["2", "3"])
        with self.assertRaises(AttributeError):
            manipulator.parameter_values("c")

    def test_add_parameter(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)

        self.assertEqual(manipulator.add_parameter("c", []), manipulator)
        self.assertTrue(manipulator.parameter_exists("c"))
        self.assertEqual(manipulator.parameter_values("c"), [])

        self.assertEqual(manipulator.add_parameter("d", None), manipulator)
        self.assertTrue(manipulator.parameter_exists("d"))
        self.assertEqual(manipulator.parameter_values("d"), [])

        self.assertEqual(manipulator.add_parameter("e", ""), manipulator)
        self.assertTrue(manipulator.parameter_exists("e"))
        self.assertEqual(manipulator.parameter_values("e"), [""])

        self.assertEqual(manipulator.add_parameter("f", "4"), manipulator)
        self.assertTrue(manipulator.parameter_exists("f"))
        self.assertEqual(manipulator.parameter_values("f"), ["4"])

        self.assertEqual(manipulator.add_parameter("g", ["5", "6"]), manipulator)
        self.assertTrue(manipulator.parameter_exists("g"))
        self.assertEqual(manipulator.parameter_values("g"), ["5", "6"])

        self.assertEqual(manipulator.add_parameter("h", [False]), manipulator)
        self.assertTrue(manipulator.parameter_exists("h"))
        self.assertEqual(manipulator.parameter_values("h"), ["False"])

        self.assertEqual(
            manipulator.get_query_string(), "?a=1&b=2&b=3&e=&f=4&g=5&g=6&h=False"
        )

    def test_update_parameter(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.update_parameter("a", "10"), manipulator)
        self.assertEqual(manipulator.parameter_values("a"), ["10"])
        self.assertEqual(manipulator.update_parameter("b", ["20", "30"]), manipulator)
        self.assertEqual(manipulator.parameter_values("b"), ["20", "30"])
        self.assertEqual(manipulator.update_parameter("c", ["40"]), manipulator)
        self.assertEqual(manipulator.parameter_values("c"), ["40"])
        self.assertEqual(manipulator.get_query_string(), "?a=10&b=20&b=30&c=40")

    def test_remove_parameter(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.remove_parameter("a"), manipulator)
        self.assertFalse(manipulator.parameter_exists("a"))
        self.assertEqual(manipulator.remove_parameter("b"), manipulator)
        self.assertFalse(manipulator.parameter_exists("b"))
        with self.assertRaises(AttributeError):
            self.assertEqual(manipulator.remove_parameter("c"), manipulator)
        self.assertEqual(manipulator.get_query_string(), "?")

    def test_is_value_in_parameter(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertTrue(manipulator.is_value_in_parameter("a", "1"))
        self.assertTrue(manipulator.is_value_in_parameter("b", "2"))
        self.assertTrue(manipulator.is_value_in_parameter("b", "3"))
        self.assertFalse(manipulator.is_value_in_parameter("b", "4"))
        with self.assertRaises(AttributeError):
            self.assertFalse(manipulator.is_value_in_parameter("c", "5"))

    def test_toggle_parameter_value(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.toggle_parameter_value("a", "1"), manipulator)
        self.assertFalse(manipulator.is_value_in_parameter("a", "1"))
        self.assertEqual(manipulator.toggle_parameter_value("a", "10"), manipulator)
        self.assertTrue(manipulator.is_value_in_parameter("a", "10"))
        self.assertEqual(manipulator.toggle_parameter_value("b", "2"), manipulator)
        self.assertFalse(manipulator.is_value_in_parameter("b", "2"))
        self.assertEqual(manipulator.get_query_string(), "?a=10&b=3")
        self.assertEqual(manipulator.toggle_parameter_value("a", "1"), manipulator)
        self.assertTrue(manipulator.is_value_in_parameter("a", "1"))
        self.assertEqual(manipulator.get_query_string(), "?a=10&a=1&b=3")

    def test_add_remove_parameter_value(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.add_parameter_value("a", "10"), manipulator)
        self.assertTrue(manipulator.is_value_in_parameter("a", "10"))
        self.assertEqual(manipulator.parameter_values("a"), ["1", "10"])

    def test_remove_parameter_value(self):
        test_query = TestQueryStringObject()
        manipulator = QueryStringTransformer(test_query)
        self.assertEqual(manipulator.remove_parameter_value("b", "2"), manipulator)
        self.assertFalse(manipulator.is_value_in_parameter("b", "2"))
        self.assertEqual(manipulator.parameter_values("b"), ["3"])
