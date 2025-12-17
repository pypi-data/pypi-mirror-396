"""
PyX Layout Utilities
Convenient layout components for common patterns.
"""
from typing import List, Any, Optional
from .ui import ui


class Container:
    """
    Centered container with max-width.
    
    Usage:
        Container(
            ui.h1("Hello"),
            ui.p("Content here"),
            size="md"
        )
    """
    
    SIZES = {
        "sm": "max-w-screen-sm",
        "md": "max-w-screen-md",
        "lg": "max-w-screen-lg",
        "xl": "max-w-screen-xl",
        "2xl": "max-w-screen-2xl",
        "full": "max-w-full",
    }
    
    def __init__(self, *children, size: str = "lg", padding: bool = True, center: bool = True, className: str = ""):
        self.children = children
        self.size = size
        self.padding = padding
        self.center = center
        self.className = className
    
    def render(self) -> str:
        children_html = ""
        for child in self.children:
            children_html += child.render() if hasattr(child, 'render') else str(child)
        
        size_class = self.SIZES.get(self.size, self.SIZES["lg"])
        padding_class = "px-4 sm:px-6 lg:px-8" if self.padding else ""
        center_class = "mx-auto" if self.center else ""
        
        return f'<div class="{size_class} {padding_class} {center_class} {self.className}">{children_html}</div>'
    
    def __str__(self):
        return self.render()


class Stack:
    """
    Vertical stack with consistent spacing.
    
    Usage:
        Stack(
            ui.h1("Title"),
            ui.p("Description"),
            ui.button("Action"),
            gap="md"
        )
    """
    
    GAPS = {
        "none": "gap-0",
        "xs": "gap-1",
        "sm": "gap-2",
        "md": "gap-4",
        "lg": "gap-6",
        "xl": "gap-8",
    }
    
    def __init__(self, *children, gap: str = "md", align: str = "stretch", className: str = ""):
        self.children = children
        self.gap = gap
        self.align = align
        self.className = className
    
    def render(self) -> str:
        children_html = ""
        for child in self.children:
            children_html += child.render() if hasattr(child, 'render') else str(child)
        
        gap_class = self.GAPS.get(self.gap, self.GAPS["md"])
        align_classes = {
            "stretch": "items-stretch",
            "start": "items-start",
            "center": "items-center",
            "end": "items-end",
        }
        align_class = align_classes.get(self.align, "items-stretch")
        
        return f'<div class="flex flex-col {gap_class} {align_class} {self.className}">{children_html}</div>'
    
    def __str__(self):
        return self.render()


class HStack:
    """
    Horizontal stack with consistent spacing.
    
    Usage:
        HStack(
            ui.button("Cancel"),
            ui.button("Save"),
            gap="sm",
            justify="end"
        )
    """
    
    GAPS = Stack.GAPS
    
    def __init__(self, *children, gap: str = "md", align: str = "center", justify: str = "start", wrap: bool = False, className: str = ""):
        self.children = children
        self.gap = gap
        self.align = align
        self.justify = justify
        self.wrap = wrap
        self.className = className
    
    def render(self) -> str:
        children_html = ""
        for child in self.children:
            children_html += child.render() if hasattr(child, 'render') else str(child)
        
        gap_class = self.GAPS.get(self.gap, self.GAPS["md"])
        
        align_classes = {
            "start": "items-start",
            "center": "items-center",
            "end": "items-end",
            "stretch": "items-stretch",
            "baseline": "items-baseline",
        }
        align_class = align_classes.get(self.align, "items-center")
        
        justify_classes = {
            "start": "justify-start",
            "center": "justify-center",
            "end": "justify-end",
            "between": "justify-between",
            "around": "justify-around",
            "evenly": "justify-evenly",
        }
        justify_class = justify_classes.get(self.justify, "justify-start")
        
        wrap_class = "flex-wrap" if self.wrap else ""
        
        return f'<div class="flex {gap_class} {align_class} {justify_class} {wrap_class} {self.className}">{children_html}</div>'
    
    def __str__(self):
        return self.render()


class Center:
    """
    Center content horizontally and vertically.
    
    Usage:
        Center(ui.spinner(), height="400px")
    """
    
    def __init__(self, child, height: str = None, className: str = ""):
        self.child = child
        self.height = height
        self.className = className
    
    def render(self) -> str:
        child_html = self.child.render() if hasattr(self.child, 'render') else str(self.child)
        height_style = f"height: {self.height};" if self.height else ""
        
        return f'<div class="flex items-center justify-center {self.className}" style="{height_style}">{child_html}</div>'
    
    def __str__(self):
        return self.render()


class Spacer:
    """
    Flexible spacer that fills available space.
    
    Usage:
        HStack(
            ui.span("Left"),
            Spacer(),
            ui.span("Right")
        )
    """
    
    def render(self) -> str:
        return '<div class="flex-1"></div>'
    
    def __str__(self):
        return self.render()


class Divider:
    """
    Horizontal or vertical divider.
    
    Usage:
        Divider()
        Divider(vertical=True)
        Divider(label="OR")
    """
    
    def __init__(self, vertical: bool = False, label: str = None, className: str = ""):
        self.vertical = vertical
        self.label = label
        self.className = className
    
    def render(self) -> str:
        if self.vertical:
            return f'<div class="w-px bg-gray-200 self-stretch {self.className}"></div>'
        
        if self.label:
            return f'''
            <div class="flex items-center {self.className}">
                <div class="flex-1 h-px bg-gray-200"></div>
                <span class="px-4 text-sm text-gray-500">{self.label}</span>
                <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            '''
        
        return f'<div class="h-px bg-gray-200 w-full {self.className}"></div>'
    
    def __str__(self):
        return self.render()


class Grid:
    """
    CSS Grid layout.
    
    Usage:
        Grid(
            *cards,
            cols=3,
            gap="md"
        )
    """
    
    def __init__(self, *children, cols: int = 1, sm_cols: int = None, md_cols: int = None, lg_cols: int = None, gap: str = "md", className: str = ""):
        self.children = children
        self.cols = cols
        self.sm_cols = sm_cols
        self.md_cols = md_cols
        self.lg_cols = lg_cols
        self.gap = gap
        self.className = className
    
    def render(self) -> str:
        children_html = ""
        for child in self.children:
            children_html += child.render() if hasattr(child, 'render') else str(child)
        
        gap_class = Stack.GAPS.get(self.gap, "gap-4")
        
        cols_class = f"grid-cols-{self.cols}"
        if self.sm_cols:
            cols_class += f" sm:grid-cols-{self.sm_cols}"
        if self.md_cols:
            cols_class += f" md:grid-cols-{self.md_cols}"
        if self.lg_cols:
            cols_class += f" lg:grid-cols-{self.lg_cols}"
        
        return f'<div class="grid {cols_class} {gap_class} {self.className}">{children_html}</div>'
    
    def __str__(self):
        return self.render()


class AspectRatio:
    """
    Maintain aspect ratio for content.
    
    Usage:
        AspectRatio(ui.img(src="video.jpg"), ratio="16/9")
    """
    
    RATIOS = {
        "square": "aspect-square",
        "video": "aspect-video",
        "16/9": "aspect-video",
        "4/3": "aspect-[4/3]",
        "3/2": "aspect-[3/2]",
        "1/1": "aspect-square",
    }
    
    def __init__(self, child, ratio: str = "video", className: str = ""):
        self.child = child
        self.ratio = ratio
        self.className = className
    
    def render(self) -> str:
        child_html = self.child.render() if hasattr(self.child, 'render') else str(self.child)
        ratio_class = self.RATIOS.get(self.ratio, f"aspect-[{self.ratio}]")
        
        return f'<div class="{ratio_class} {self.className}">{child_html}</div>'
    
    def __str__(self):
        return self.render()


def Card(*children, padding="md", shadow="sm", rounded="lg", border=True, className=""):
    """
    Zen Mode Card component (Factory Function).
    Returns a chainable PyxElement.
    """
    padding_classes = {"none": "p-0", "sm": "p-3", "md": "p-4", "lg": "p-6", "xl": "p-8"}
    shadow_classes = {"none": "", "sm": "shadow-sm", "md": "shadow-md", "lg": "shadow-lg"}
    rounded_classes = {"none": "", "sm": "rounded-sm", "md": "rounded-md", "lg": "rounded-lg", "xl": "rounded-xl"}
    
    # Base Element
    el = ui.div(list(children)).bg("white")
    
    # Apply props via Zen Logic
    if padding in padding_classes: el.cls(padding_classes[padding])
    if shadow in shadow_classes: el.cls(shadow_classes[shadow])
    if rounded in rounded_classes: el.cls(rounded_classes[rounded])
    if border: el.border().border_color("gray-200")
    if className: el.cls(className)
    
    return el
