#!/nix/store/1yqa5nksxbmg3knw8daz3gdpf9xm5iw1-python3-s390x-unknown-linux-gnu-3.12.11/bin/python


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        f"command alias in_call_stack breakpoint command add --python-function {__name__}.in_call_stack -k name -v %1"
    )


def in_call_stack(frame, bp_loc, arg_dict, _):
    """Only break if the given name is in the current call stack."""
    name = arg_dict.GetValueForKey("name").GetStringValue(1000)
    thread = frame.GetThread()
    found = False
    for frame in thread.frames:
        # Check the symbol.
        symbol = frame.GetSymbol()
        if symbol and name in frame.GetSymbol().GetName():
            return True
        # Check the function.
        function = frame.GetFunction()
        if function and name in function.GetName():
            return True
    return False
