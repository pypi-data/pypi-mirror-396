def json_to_prompt(objects: list[dict]) -> str:
    """
    Transforms a list of 3D objets into readable text, optimized for T5
    """
    lines = []
    for obj in objects:
        title = obj.get("title", "Unknown title")
        country = obj.get("country", "Unknown country")
        description = obj.get("description", "No description available")
        lines.append(f"Title: {title}\nCountry: {country}\nDescription: {description}")
    return (
        """The following is a curated list of 3D models representing historical landmarks. Each item includes a title,"""
        + """the country of origin, and a short description. Write a short expert summary highlighting their cultural and visual significance."""
        + ":\n"
        + "\n\n".join(lines)
    )
