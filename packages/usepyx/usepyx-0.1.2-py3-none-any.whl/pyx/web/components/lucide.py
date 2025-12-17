from ..ui import PyxElement

def Lucide(name, size=24, color=None, stroke_width=2):
    """
    Renders a Lucide icon using the client-side library.
    Usage: Lucide("home"), Lucide("activity", color="red-500")
    """
    el = PyxElement("i") \
        .attr("data-lucide", name) \
        .attr("width", size) \
        .attr("height", size) \
        .attr("stroke-width", stroke_width)
    
    if color:
        el.text(color) # Tailwind text-color affects SVG stroke if currentColor is used
        
    return el
