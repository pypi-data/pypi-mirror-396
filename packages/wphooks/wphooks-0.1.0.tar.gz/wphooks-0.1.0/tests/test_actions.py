import unittest

from wphooks.wp_actions import wp_actions, action, add_action, do_action


class ActionsTests(unittest.TestCase):
    """Test action hooks"""

    def setUp(self):
        wp_actions.clear()

    def test_add_action(self):
        """Test adding a action with add_action"""
        hook_name: str = "test.action"
        add_action(hook_name, lambda x: True)

        self.assertNotEqual(wp_actions, {})
        self.assertNotEqual(wp_actions[hook_name], {})
        self.assertNotEqual(wp_actions[hook_name][10], {})
        self.assertEqual(wp_actions[hook_name][10][0]["hook_name"], hook_name)
        self.assertEqual(wp_actions[hook_name][10][0]["accepted_args"], 1)
        self.assertTrue(wp_actions[hook_name][10][0]["callback"](10), True)

    def test_do_action_with_add_action(self):
        """Test doing an action with add_action"""

        hook_name: str = "test.action2"
        received_action_var: int = 0

        def hook(value: int) -> None:
            nonlocal received_action_var
            received_action_var = value

        add_action(hook_name, hook)

        do_action(hook_name, 6)
        self.assertEqual(received_action_var, 6)

        do_action(hook_name, 10)
        self.assertEqual(received_action_var, 10)

    def test_args_passing(self):
        """Test passing arguments to filters"""
        hook_name: str = "test.args"

        received_action_vars: tuple = ()

        def hook(*values) -> None:
            nonlocal received_action_vars
            received_action_vars = values

        add_action(hook_name, hook, accepted_args=2)

        do_action(hook_name, 1, 2)

        self.assertEqual(received_action_vars, (1, 2))

    def test_add_action_with_accepted_args(self):
        """Test adding an action with accepted args"""

        hook_name: str = "test.action_args"

        received_action_vars: tuple = ()

        def hook(*values) -> None:
            nonlocal received_action_vars
            received_action_vars = values

        add_action(hook_name, hook, accepted_args=2)

        do_action(hook_name, 1, 2, "extra1", "extra2")

        self.assertEqual(received_action_vars, (1, 2))

    def test_action_decorator(self):
        """Test the action decorator"""

        hook_name: str = "test.decorator_action"

        received_action_var: int = 0

        @action(hook_name)
        def my_action(x: int) -> None:
            nonlocal received_action_var
            received_action_var = x

        do_action(hook_name, 5)
        self.assertEqual(received_action_var, 5)

    def test_different_priority(self):
        """
        Test action priority.
        Priority is used to specify the order in which the functions
        associated with a particular action are executed.
        Lower numbers correspond with earlier execution, and functions
        with the same priority are executed in the order in which they were
        added to the action.
        """

        hook_name: str = "test.priority"

        received_action_var: str = ""

        def hook_a(value: str) -> None:
            nonlocal received_action_var
            received_action_var += value + "a."

        def hook_b(value: str) -> None:
            nonlocal received_action_var
            received_action_var += value + "b."

        # Add priority 10 first, then 5. 5 should run first.
        add_action(hook_name, hook_a, priority=10)
        add_action(hook_name, hook_b, priority=5)

        # If 5 runs first: "start" + "b" = "startb."
        # Then 10 runs: "startb" + "a" = "startba."
        do_action(hook_name, "start")
        self.assertEqual(received_action_var, "startb.starta.")

    def test_multiple_filters(self):
        """Test multiple actions on the same hook"""

        hook_name: str = "test.multiple"

        received_action_var: str = ""

        def hook_a(value: str) -> None:
            nonlocal received_action_var
            received_action_var += value + "a."

        def hook_b(value: str) -> None:
            nonlocal received_action_var
            received_action_var += value + "b."

        # Default priority 10 for both. Execution order is insertion order.
        add_action(hook_name, hook_a)
        add_action(hook_name, hook_b)

        do_action(hook_name, "start")
        self.assertEqual(received_action_var, "starta.startb.")

    def test_same_priority(self):
        """Test that actions with the same priority run in insertion order"""

        hook_name: str = "test.same_priority"

        received_action_var: str = ""

        def hook_a(value: str) -> None:
            nonlocal received_action_var
            received_action_var += value + "a."

        def hook_b(value: str) -> None:
            nonlocal received_action_var
            received_action_var += value + "b."

        # Default priority 10 for both. Execution order is insertion order.
        add_action(hook_name, hook_a, priority=10)
        add_action(hook_name, hook_b, priority=10)

        do_action(hook_name, "start")
        self.assertEqual(received_action_var, "starta.startb.")

    def test_do_action_no_args(self):
        """Test doing an action without arguments"""
        hook_name: str = "test.no_args"
        received_action_var: bool = False

        def hook() -> None:
            nonlocal received_action_var
            received_action_var = True

        add_action(hook_name, hook, accepted_args=0)

        do_action(hook_name)
        self.assertTrue(received_action_var)

    def test_do_action_fewer_args_than_accepted(self):
        """Test doing an action with fewer arguments than accepted_args"""
        hook_name: str = "test.fewer_args"
        received_action_vars: tuple = ()

        # accepted_args=2, but we will pass 0 or 1
        def hook(*values) -> None:
            nonlocal received_action_vars
            received_action_vars = values

        add_action(hook_name, hook, accepted_args=2)

        # Pass 0 args (less than 2)
        do_action(hook_name)
        self.assertEqual(received_action_vars, ())

        # Pass 1 arg (less than 2)
        do_action(hook_name, 1)
        self.assertEqual(received_action_vars, (1,))

        # Pass 2 args (equal)
        do_action(hook_name, 1, 2)
        self.assertEqual(received_action_vars, (1, 2))
