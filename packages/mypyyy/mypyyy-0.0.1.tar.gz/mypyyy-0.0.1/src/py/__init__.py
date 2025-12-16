from .practicals import *
import inspect

def help():
    """Displays the list of all available practical functions."""
    print("\nAvailable Practical Functions:")
    print("="*65)
    print(f"{'Function':<15} | {'Description'}")
    print("-" * 65)
    
    # Filter functions: Exclude helpers and built-ins
    excluded = {'help', 'display_source', 'inspect', 'os'}
    funcs = []
    all_globals = globals().copy()
    
    for name, obj in all_globals.items():
        if inspect.isfunction(obj) and name not in excluded and not name.startswith('_'):
             funcs.append((name, obj))
    
    # Sort alphabetically
    funcs.sort(key=lambda x: x[0])
    
    for name, func in funcs:
        doc = func.__doc__.strip().split('\n')[0] if func.__doc__ else "No description"
        print(f"{name:<15} | {doc}")
    print("="*65)
