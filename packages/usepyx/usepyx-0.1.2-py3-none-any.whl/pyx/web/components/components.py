from ..ui import UI, Element
import json

class PyxUI:
    """
    Standard PyX UI Components.
    Premium, accessible, and beautiful defaults.
    """
    
    # --- BASICS ---
    
    @staticmethod
    def Card(children, className=""):
        return UI.div(children, className=f"rounded-xl border bg-card text-card-foreground shadow-sm {className}")

    @staticmethod
    def CardHeader(children, className=""):
        return UI.div(children, className=f"flex flex-col space-y-1.5 p-6 {className}")

    @staticmethod
    def CardTitle(text, className=""):
        return UI.h3(text, className=f"text-2xl font-semibold leading-none tracking-tight {className}")
        
    @staticmethod
    def CardDescription(text, className=""):
        return UI.p(text, className=f"text-sm text-muted-foreground {className}")

    @staticmethod
    def CardContent(children, className=""):
        return UI.div(children, className=f"p-6 pt-0 {className}")
        
    @staticmethod
    def CardFooter(children, className=""):
        return UI.div(children, className=f"flex items-center p-6 pt-0 {className}")

    @staticmethod
    def Button(text, variant="default", size="default", onClick=None, className="", id=None):
        variants = {
            "default": "bg-primary text-primary-foreground hover:bg-primary/90",
            "destructive": "bg-destructive text-destructive-foreground hover:bg-destructive/90",
            "outline": "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
            "secondary": "bg-secondary text-secondary-foreground hover:bg-secondary/80",
            "ghost": "hover:bg-accent hover:text-accent-foreground",
            "link": "text-primary underline-offset-4 hover:underline",
        }
        sizes = {
            "default": "h-10 px-4 py-2",
            "sm": "h-9 rounded-md px-3",
            "lg": "h-11 rounded-md px-8",
            "icon": "h-10 w-10",
        }
        
        base_cls = "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
        
        btn = UI.button(text, className=f"{base_cls} {variants.get(variant)} {sizes.get(size)} {className}")
        if id:
            btn.id(id)
        if onClick:
            btn.on_click(onClick)
        return btn

    @staticmethod
    def Input(placeholder="", value="", name="", type="text", className="", onChange=None):
        el = UI.input(
            type=type,
            placeholder=placeholder,
            value=value,
            name=name,
            className=f"flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 {className}"
        )
        if onChange:
             el.on("input", onChange)
        return el

    @staticmethod
    def Label(text, htmlFor="", className=""):
        return UI.label(text, htmlFor=htmlFor, className=f"text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 {className}")
        
    @staticmethod
    def Textarea(placeholder="", value="", name="", className="", rows=3):
        return UI.textarea(value, placeholder=placeholder, name=name, rows=str(rows), className=f"flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 {className}")

    @staticmethod
    def Table(headers: list, rows: list, actions=None):
        """Standard Table"""
        # Header
        th_els = [UI.th(h, className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0") for h in headers]
        if actions:
            th_els.append(UI.th("", className="h-12 px-4 text-left align-middle font-medium text-muted-foreground"))
            
        thead = UI.thead(UI.tr(th_els, className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"))
        
        # Body
        tr_els = []
        for row in rows:
            td_els = []
            # Handle Dict or Object
            data = row if isinstance(row, dict) else row.__dict__
            
            for h in headers:
                key = h.lower().replace(" ", "_")
                val = data.get(key, "-")
                td_els.append(UI.td(str(val), className="p-4 align-middle [&:has([role=checkbox])]:pr-0"))
            
            if actions:
                td_els.append(UI.td(actions(row), className="p-4 align-middle"))

            tr_els.append(UI.tr(td_els, className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"))

        tbody = UI.tbody(tr_els, className="[&_tr:last-child]:border-0")
        
        return UI.div(
            UI.table([thead, tbody], className="w-full caption-bottom text-sm"),
            className="w-full overflow-auto rounded-md border"
        )
    
    # --- FEEDBACK ---

    @staticmethod
    def Badge(text, variant="default", className=""):
        variants = {
            "default": "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
            "secondary": "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
            "destructive": "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
            "outline": "text-foreground",
        }
        return UI.div(text, className=f"inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 {variants.get(variant)} {className}")
        
    @staticmethod
    def Alert(title, description, variant="default", className=""):
        variants = {
            "default": "bg-background text-foreground",
            "destructive": "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
        }
        return UI.div([
            UI.h5(title, className="mb-1 font-medium leading-none tracking-tight"),
            UI.div(description, className="text-sm [&_p]:leading-relaxed")
        ], className=f"relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground {variants.get(variant)} {className}")
        
    @staticmethod
    def Skeleton(className=""):
         return UI.div("", className=f"animate-pulse rounded-md bg-muted {className}")
         
    # --- LAYOUT ---
    
    @staticmethod
    def Separator(orientation="horizontal", className=""):
        base = "shrink-0 bg-border"
        styles = "h-[1px] w-full" if orientation == "horizontal" else "h-full w-[1px]"
        return UI.div("", className=f"{base} {styles} {className}")
        
    @staticmethod
    def Avatar(src, alt="Avatar", fallback="CN", className=""):
        return UI.div([
             UI.img(src, alt, className="aspect-square h-full w-full") if src else None,
             UI.div(fallback, className="flex h-full w-full items-center justify-center rounded-full bg-muted") if not src else None
        ], className=f"relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full {className}")

    # --- INTERACTIVE ---
    
    @staticmethod
    def Checkbox(checked=False, name="", className=""):
        return UI.input(type="checkbox", checked=checked, name=name, className=f"peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground {className}")
        
    @staticmethod
    def Switch(checked=False, name="", onChange=None, className=""):
        return UI.label([
            UI.input(type="checkbox", checked=checked, name=name, className="sr-only peer"),
            UI.div("", className="w-11 h-6 bg-input peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-ring/20 dark:peer-focus:ring-ring/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-background after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary")
        ], className=f"relative inline-flex items-center cursor-pointer {className}")
        
    @staticmethod
    def Select(options: list, name="", placeholder="Select...", className=""):
        opts = [UI.option(o['label'], value=o['value']) for o in options]
        return UI.select(opts, name=name, className=f"flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 {className}")

    @staticmethod
    def Tabs(triggers: list, contents: list, defaultValue=None, className=""):
        trigs = [UI.button(t['label'], className="inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm") for t in triggers]
        
        return UI.div([
            UI.div(trigs, className="inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground w-full"),
            UI.div([c['content'] for c in contents], className="mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2")
        ], className=className)

    # --- COMPLEX INTERACTIVE (Dialog, Drawer, Dropdown) ---
    # These use pure CSS/JS toggles for simplicity in Zen Mode

    @staticmethod
    def Dialog(id, trigger, title, children, footer=None):
        """
        modal = Shadcn.Dialog("my-modal", Shadcn.Button("Open"), "Title", "Content")
        """
        from ..client import JS
        
        # Overlay & Content Wrapper
        overlay_id = f"{id}-overlay"
        content_id = f"{id}-content"
        
        # Trigger opens functionality
        trigger.on_click(JS.remove_class(f"#{overlay_id}", "hidden"))
        
        # Close Button
        close_btn = PyxUI.Button("✕", variant="ghost", size="icon", className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground")
        close_btn.on_click(JS.add_class(f"#{overlay_id}", "hidden"))
        
        return UI.div([
            trigger,
            UI.div([
                # Overlay
                UI.div("", className="fixed inset-0 z-50 bg-black/80  data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0"),
                # Content
                UI.div([
                    close_btn,
                    UI.div([
                        UI.h2(title, className="text-lg font-semibold leading-none tracking-tight"),
                        UI.div(children, className="mt-4"),
                         UI.div(footer, className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 mt-4") if footer else None
                    ], className="grid gap-4")
                ], id=content_id, className="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg")
            ], id=overlay_id, className="hidden fixed inset-0 z-50 flex items-center justify-center")
        ])

    @staticmethod
    def Sheet(id, trigger, title, children, side="right"):
        """
        Sidebar Drawer.
        side: left, right, top, bottom
        """
        from ..client import JS
        
        overlay_id = f"{id}-overlay"
        content_id = f"{id}-content"
        
        trigger.on_click(JS.remove_class(f"#{overlay_id}", "hidden"))
        
        close_btn = PyxUI.Button("✕", variant="ghost", size="icon", className="absolute right-4 top-4")
        close_btn.on_click(JS.add_class(f"#{overlay_id}", "hidden"))
        
        animations = {
            "right": "inset-y-0 right-0 h-full border-l data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right sm:max-w-sm",
            "left": "inset-y-0 left-0 h-full border-r data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left sm:max-w-sm",
            "top": "inset-x-0 top-0 border-b data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top",
            "bottom": "inset-x-0 bottom-0 border-t data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom"
        }
        
        sheet_cls = f"fixed z-50 gap-4 bg-background p-6 shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:duration-500 {animations.get(side)}"

        return UI.div([
            trigger,
            UI.div([
                 UI.div("", className="fixed inset-0 z-50 bg-black/80").on_click(JS.add_class(f"#{overlay_id}", "hidden")),
                 UI.div([
                     close_btn,
                     UI.h2(title, className="text-lg font-semibold text-foreground"),
                     UI.div(children, className="mt-4")
                 ], className=sheet_cls, attr={"data-state": "open"}) 
            ], id=overlay_id, className="hidden fixed inset-0 z-50")
        ])

    @staticmethod
    def DropdownMenu(id, trigger, items):
        """
        Simple Dropdown.
        items: [{'label': 'Profile', 'href': '/profile'}, {'label': 'Logout', 'onClick': ...}]
        """
        from ..client import JS
        menu_id = f"{id}-menu"
        
        trigger.on_click(JS.toggle_class(f"#{menu_id}", "hidden"))
        
        menu_items = []
        for item in items:
            cls = "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 hover:bg-accent hover:text-accent-foreground cursor-pointer block w-full text-left"
            if 'href' in item:
                el = UI.a(item['label'], href=item['href'], className=cls)
            else:
                el = UI.button(item['label'], className=cls)
                if 'onClick' in item:
                    el.on_click(item['onClick'])
            menu_items.append(el)
            
        return UI.div([
            trigger,
            UI.div(menu_items, id=menu_id, className="hidden absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2")
        ], className="relative inline-block text-left")
