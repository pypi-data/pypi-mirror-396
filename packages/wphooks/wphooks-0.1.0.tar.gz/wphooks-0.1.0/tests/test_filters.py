import unittest

from wphooks.wp_filters import wp_filters, filter, add_filter, apply_filters


class FiltersTests(unittest.TestCase):
    """Test filter hooks"""

    def setUp(self):
        wp_filters.clear()

    def test_add_filter(self):
        """Test adding a filter with add_filter"""
        hook_name: str = "test.filter1"
        add_filter(hook_name, lambda x: True)

        self.assertNotEqual(wp_filters, {})
        self.assertNotEqual(wp_filters[hook_name], {})
        self.assertNotEqual(wp_filters[hook_name][10], {})
        self.assertEqual(wp_filters[hook_name][10][0]["hook_name"], hook_name)
        self.assertEqual(wp_filters[hook_name][10][0]["accepted_args"], 1)
        self.assertTrue(wp_filters[hook_name][10][0]["callback"](10), True)

    def test_apply_filters_with_add_filter(self):
        """Test applying a filter with add_filter"""

        hook_name: str = "test.filter2"
        add_filter(hook_name, lambda x: x + 1)

        self.assertEqual(apply_filters(hook_name, 6), 7)
        self.assertEqual(apply_filters(hook_name, 10), 11)

    def test_apply_filters_default_value(self):
        """Test applying a filter with a default value and without filters"""

        hook_name: str = "test.filter3"

        self.assertEqual(apply_filters(hook_name, 6), 6)
        self.assertTrue(apply_filters(hook_name, True))
        self.assertEqual(apply_filters(hook_name, {"foo": "bar"}), {"foo": "bar"})

    def test_add_filter_with_accepted_args(self):
        """Test adding a filter with accepted args"""

        hook_name: str = "test.filter_args"
        add_filter(hook_name, lambda x, y: x + y, accepted_args=2)

        self.assertEqual(apply_filters(hook_name, 1, 2, "extra1", "extra2"), 3)

    def test_filter_decorator(self):
        """Test the filter decorator"""

        hook_name: str = "test.decorator_filter"

        @filter(hook_name)
        def my_filter(x):
            return x * 2

        self.assertEqual(apply_filters(hook_name, 5), 10)

    def test_different_priority(self):
        """
        Test filter priority.
        Priority is used to specify the order in which the functions
        associated with a particular filter are executed.
        Lower numbers correspond with earlier execution, and functions
        with the same priority are executed in the order in which they were
        added to the filter.
        """

        hook_name: str = "test.priority"

        # Add priority 10 first, then 5. 5 should run first.
        add_filter(hook_name, lambda x: x + "a", priority=10)
        add_filter(hook_name, lambda x: x + "b", priority=5)

        # If 5 runs first: "start" + "b" = "startb"
        # Then 10 runs: "startb" + "a" = "startba"
        self.assertEqual(apply_filters(hook_name, "start"), "startba")

    def test_multiple_filters(self):
        """Test multiple filters on the same hook"""

        hook_name: str = "test.multiple"

        add_filter(hook_name, lambda x: x + 1)
        add_filter(hook_name, lambda x: x * 2)

        # Default priority 10 for both. Execution order is insertion order.
        # (1 + 1) * 2 = 4
        self.assertEqual(apply_filters(hook_name, 1), 4)

    def test_args_passing(self):
        """Test passing arguments to filters"""

        hook_name: str = "test.args"

        add_filter(hook_name, lambda x, y, z: x + y + z, accepted_args=3)
        # default_value=1, args=(2, 3) -> callback(1, 2, 3)
        self.assertEqual(apply_filters(hook_name, 1, 2, 3), 6)

    def test_same_priority(self):
        """Test that filters with the same priority run in insertion order"""

        hook_name: str = "test.same_priority"

        add_filter(hook_name, lambda x: x + "a", priority=10)
        add_filter(hook_name, lambda x: x + "b", priority=10)

        self.assertEqual(apply_filters(hook_name, "start"), "startab")

    def test_apply_filters_fewer_args_than_accepted(self):
        """Test applying a filter with fewer arguments than accepted_args"""
        hook_name: str = "test.fewer_args_filter"

        # accepted_args=3 (val + 2 extras). But we pass fewer.
        def hook(val, *extras):
            return val + "".join(map(str, extras))

        add_filter(hook_name, hook, accepted_args=3)

        # Pass 0 extra args (total 1: val). 1 < 3. Should call hook(val).
        self.assertEqual(apply_filters(hook_name, "a"), "a")

        # Pass 1 extra arg (total 2: val, e1). 2 < 3. Should call hook(val, e1).
        self.assertEqual(apply_filters(hook_name, "a", "b"), "ab")

        # Pass 2 extra args (total 3: val, e1, e2). 3 == 3. Should call hook(val, e1, e2).
        self.assertEqual(apply_filters(hook_name, "a", "b", "c"), "abc")
