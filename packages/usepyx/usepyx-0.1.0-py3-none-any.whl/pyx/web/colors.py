
class ColorScale:
    """Helper untuk mengakses shade warna (50-950)"""
    def __init__(self, name):
        self.name = name

    def __getitem__(self, shade):
        """Usage: Colors.red[500] -> 'red-500'"""
        return f"{self.name}-{shade}"
    
    def __call__(self, shade):
        """Usage: Colors.red(500) -> 'red-500'"""
        return f"{self.name}-{shade}"

class Colors:
    """
    Daftar lengkap Palet Standar Tailwind.
    Memudahkan autocomplete di IDE.
    """
    # Neutrals
    slate   = ColorScale("slate")
    gray    = ColorScale("gray")
    zinc    = ColorScale("zinc")
    neutral = ColorScale("neutral")
    stone   = ColorScale("stone")
    
    # Colors
    red     = ColorScale("red")
    orange  = ColorScale("orange")
    amber   = ColorScale("amber")
    yellow  = ColorScale("yellow")
    lime    = ColorScale("lime")
    green   = ColorScale("green")
    emerald = ColorScale("emerald")
    teal    = ColorScale("teal")
    cyan    = ColorScale("cyan")
    sky     = ColorScale("sky")
    blue    = ColorScale("blue")
    indigo  = ColorScale("indigo")
    violet  = ColorScale("violet")
    purple  = ColorScale("purple")
    fuchsia = ColorScale("fuchsia")
    pink    = ColorScale("pink")
    rose    = ColorScale("rose")
    
    # Base
    white   = "white"
    black   = "black"
    transparent = "transparent"

    # --- THEME GENERATOR (Fitur Powerfull) ---
    @staticmethod
    def generate_custom_theme(custom_colors: dict):
        """
        Mengubah Dictionary Python menjadi CSS Variables (@theme).
        Input: {"brand": "#123456", "primary": "oklch(0.9 0.1 100)"}
        Output: CSS String untuk disuntikkan ke Head.
        """
        css_lines = []
        for name, value in custom_colors.items():
            css_lines.append(f"--color-{name}: {value};")
        
        return f"""
        <style>
        @theme {{
            {chr(10).join(css_lines)}
        }}
        </style>
        """
