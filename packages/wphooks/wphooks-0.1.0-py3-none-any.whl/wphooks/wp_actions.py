"""
Filters functions based on WordPress actions
(https://developer.wordpress.org/plugins/hooks/actions/)

Actions are one of the two types of Hooks.

They provide a way for running a function at a specific point in the execution of your script.
They are the counterpart to Filters.

Callback functions for an Action do not return anything back to the calling Action hook.
Here is a refresher of the difference between actions and filters.
"""

wp_actions: dict = {}


def action(hook_name: str, priority: int = 10, accepted_args: int = 1):
    """
    Decorator for registering function as action

    Args:
        hook_name (str): The name of the action to add the callback to.
        priority (int, optional): Used to specify the order in which the functions
                                associated with a particular action are executed.
                                Lower numbers correspond with earlier execution,
                                and functions with the same priority are executed
                                in the order in which they were added to the action. Default 10.
        accepted_args (int, optional): The number of arguments the function accepts. Default 1.
    """

    def hook(callback):
        add_action(hook_name, callback, priority, accepted_args)

    return hook


def add_action(
    hook_name: str, callback, priority: int = 10, accepted_args: int = 1
) -> None:
    """
    Adds a callback function to an action hook.
    Actions are the hooks that the wplib launches at specific points
    during execution, or when specific events occur.

    Args:
        hook_name (str): The name of the action to add the callback to.
        callback (function): The callback to be run when the action is called.
        priority (int, optional): Used to specify the order in which the functions
                                associated with a particular action are executed.
                                Lower numbers correspond with earlier execution,
                                and functions with the same priority are executed
                                in the order in which they were added to the action. Default 10.
        accepted_args (int, optional): The number of arguments the function accepts. Default 1.
    """

    wp_actions[hook_name] = wp_actions.get(hook_name, {})
    wp_actions[hook_name][priority] = wp_actions[hook_name].get(priority, [])
    wp_actions[hook_name][priority].append(
        {"hook_name": hook_name, "callback": callback, "accepted_args": accepted_args}
    )


def do_action(hook_name: str, *args) -> None:
    """
    Calls the callback functions that have been added to an action hook.

    This function invokes all functions attached to action hook `hook_name`.
    It is possible to create new action hooks by simply calling this function,
    specifying the name of the new hook using the `hook_name` parameter.

    You can pass extra arguments to the hooks

    Args:
        hook_name (str): The name of the action to be executed.
        *args: Optional arguments to pass to the callback functions.

    Note:
        If the number of arguments passed to do_action is less than accepted_args
        specified in add_action, the callback will be called with the available arguments.
    """
    actions: dict = wp_actions.get(hook_name, {})
    # pylint: disable-next=unused-variable
    for priority, hooks in sorted(actions.items()):
        for hook in hooks:
            max_args: int = hook["accepted_args"]
            max_args = min(max_args, len(args))

            if args and max_args:
                hook["callback"](*args[:max_args])
            else:
                hook["callback"]()