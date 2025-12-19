def say_hello(name: str) -> str:
    """
    A simple greeting tool. Use this when you want to welcome a client or test connectivity.

    Args:
        name (str): The name of the person to greet.
    Returns:
        str: A formatted greeting string.
    """
    return f"Hello {name}! Welcome to the Shopify Discovery session."

class AgencyBrandingTools:
    def get_agency_mission(self) -> str:
        """Returns the agency's core mission statement."""
        return "Our mission is to build the world's most performant Shopify stores."
