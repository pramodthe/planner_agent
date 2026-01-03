try:
    from openagents.workspace.tool_decorator import tool
    print("Import successful: openagents.workspace.tool_decorator.tool")
except ImportError as e:
    print(f"Import failed: {e}")

try:
    from openagents.core.tool_decorator import tool
    print("Import successful: openagents.core.tool_decorator.tool")
except ImportError as e:
    print(f"Import failed: {e}")
