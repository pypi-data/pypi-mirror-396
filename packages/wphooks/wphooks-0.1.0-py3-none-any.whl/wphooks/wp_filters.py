"""
Filters functions based on WordPress filters
(https://developer.wordpress.org/plugins/hooks/filters/).

Filters are one of the two types of Hooks.

They provide a way for functions to modify data during the execution of your script.
They are the counterpart to Actions.

Unlike Actions, filters are meant to work in an isolated manner, and should never
have side effects such as affecting global variables and output. Filters expect to have
something returned back to them.
"""

wp_filters: dict = {}


# pylint: disable-next=redefined-builtin
def filter(hook_name: str, priority: int = 10, accepted_args: int = 1):
    """
    Decorator for registering callback as filter

    Args:
        hook_name (str): The name of the filter to add the callback to.
        priority (int, optional): Used to specify the order in which the functions
                                  associated with a particular filter are executed.
                                  Lower numbers correspond with earlier execution,
                                  and functions with the same priority are executed
                                  in the order in which they were added to the filter. Default 10.
        accepted_args (int, optional): The number of arguments the function accepts. Default 1.
    """

    def hook(callback):
        add_filter(hook_name, callback, priority, accepted_args)

    return hook


def add_filter(
    hook_name: str, callback, priority: int = 10, accepted_args: int = 1
) -> None:
    """
    Adds a callback function to a filter hook.

    Args:
        hook_name (str): The name of the filter to add the callback to.
        callback (function): The callback to be run when the filter is applied.
        priority (int, optional): Optional. Used to specify the order in which the functions
                                  associated with a particular filter are executed.
                                  Lower numbers correspond with earlier execution,
                                  and functions with the same priority are executed
                                  in the order in which they were added to the filter. Default 10.
        accepted_args (int, optional): The number of arguments the function accepts. Default 1.
    """

    wp_filters[hook_name] = wp_filters.get(hook_name, {})
    wp_filters[hook_name][priority] = wp_filters[hook_name].get(priority, [])
    wp_filters[hook_name][priority].append(
        {"hook_name": hook_name, "callback": callback, "accepted_args": accepted_args}
    )


def apply_filters(hook_name: str, default_value, *args):
    """
    Calls the callback functions that have been added to a filter hook.
    This function invokes all functions attached to filter hook `$hook_name`.
    It is possible to create new filter hooks by simply calling this function,
    specifying the name of the new hook using the `$hook_name` parameter.
    The function also allows for multiple additional arguments to be passed to hooks.

    Args:
        hook_name (str): The name of the filter hook.
        default_value (_type_): The value to filter.

    Note:
        If the number of arguments passed to apply_filters (including default_value)
        is less than accepted_args specified in add_filter, the callback will be
        called with the available arguments.

    Returns:
        The filtered value after all hooked functions are applied to it.
    """
    filters: dict = wp_filters.get(hook_name, {})
    # pylint: disable-next=unused-variable
    for priority, hooks in sorted(filters.items()):
        for hook in hooks:
            max_args: int = hook["accepted_args"]
            max_args = min(max_args, len(args) + 1)

            filter_args: list = [default_value] + list(args)

            default_value = hook["callback"](*filter_args[:max_args])

    return default_value
