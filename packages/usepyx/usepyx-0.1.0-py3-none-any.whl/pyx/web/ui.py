from ..core.events import EventManager
import json

class PyxElement:
    def __init__(self, tag="div", content=None, component_id=None):
        self.tag = tag
        self.children = []
        self.classes = []
        self.attrs = {}
        if component_id:
            self.attrs["id"] = component_id
            
        if content is not None:
            if isinstance(content, list):
                # Auto-flatten 1 level for convenience (e.g. UI.div([a,b]))
                for item in content:
                    if isinstance(item, list):
                        self.children.extend(item)
                    else:
                        self.children.append(item)
            else:
                self.children.append(content)

    # =========================================================================
    # CORE ENGINE
    # =========================================================================
    def cls(self, *classes):
        for c in classes:
            if c: self.classes.append(c)
        return self

    def id(self, component_id):
        self.attrs["id"] = component_id
        return self

    def attr(self, key, value):
        self.attrs[key] = value
        return self

    def aria(self, key, value):
        self.attrs[f"aria-{key}"] = value
        return self

    # =========================================================================
    # PYTHONIC STYLING
    # =========================================================================
    def style(self, **kwargs):
        """
        Pythonic styling without Tailwind strings.
        
        Usage:
            ui.div("Hello").style(
                text="sm",
                color="red-500",
                font="bold",
                p=4,
                bg="white",
                rounded="lg",
                shadow="md"
            )
        """
        from .styles import Style
        s = Style(**kwargs)
        return self.cls(str(s))
    
    def apply(self, style_obj):
        """
        Apply a Style object or preset.
        
        Usage:
            from pyx import presets
            ui.div("Card").apply(presets.card)
        """
        return self.cls(str(style_obj))
    
    def sx(self, **kwargs):
        """Short alias for style()"""
        return self.style(**kwargs)

    # =========================================================================
    # EVENT HANDLING (ZEN MODE)
    # =========================================================================
    def on(self, event_name, handler, form_id=None):
        """
        Bind a Python function to a browser event using PyX Engine.
        Example: ui.button("Save").on("click", save_handler)
        """
        if callable(handler):
            # Register function to global registry
            func_name = EventManager.register(handler)
            if form_id:
                js_code = f"PyX.sendEvent('{func_name}', '{form_id}')"
            else:
                js_code = f"PyX.sendEvent('{func_name}', null)"
        elif hasattr(handler, 'code'):
            # It's a JS Helper Object
            js_code = str(handler)
        else:
            # Fallback for raw string (legacy)
            js_code = handler

        self.attrs[f"on{event_name}"] = js_code
        return self

    def on_click(self, handler, form_id=None):
        """Shortcut for click event"""
        return self.on("click", handler, form_id)

    def on_change(self, handler, form_id=None):
        """
        Shortcut for change event.
        
        Supports:
        - Regular Python functions
        - State setter methods (e.g., AuthState.set_username)
        """
        return self._bind_value_event("change", handler, form_id)

    def on_input(self, handler):
        """
        Handler for input events (fires on every keystroke).
        
        Supports:
        - Regular Python functions  
        - State setter methods (e.g., AuthState.set_username)
        """
        return self._bind_value_event("input", handler, None)
    
    def _bind_value_event(self, event_name, handler, form_id=None):
        """
        Internal method to bind value-based events.
        Detects if handler is a State setter and generates appropriate JS.
        """
        from ..core.state import State
        import inspect
        
        if callable(handler):
            handler_name = getattr(handler, '__name__', str(handler))
            
            # Check if this looks like a State setter (set_*)
            is_state_setter = (
                handler_name.startswith('set_') and 
                hasattr(handler, '__self__') and 
                isinstance(handler.__self__, type) and 
                issubclass(handler.__self__, State)
            )
            
            # Or if it's an unbound method on a State class
            if not is_state_setter and hasattr(handler, '__qualname__'):
                # Check qualname like "AuthState.set_username"
                parts = handler.__qualname__.split('.')
                if len(parts) == 2 and parts[1].startswith('set_'):
                    is_state_setter = True
            
            if is_state_setter or handler_name.startswith('set_'):
                # This is a State setter - send value with event
                func_name = EventManager.register(handler)
                js_code = f"""
                    (function() {{
                        const val = this.value;
                        PyX.sendEvent('{func_name}', null, val);
                    }}).call(this)
                """
            else:
                # Regular handler
                func_name = EventManager.register(handler)
                if form_id:
                    js_code = f"PyX.sendEvent('{func_name}', '{form_id}')"
                else:
                    js_code = f"PyX.sendEvent('{func_name}', null)"
        elif hasattr(handler, 'code'):
            js_code = str(handler)
        else:
            js_code = handler
        
        self.attrs[f"on{event_name}"] = js_code
        return self

    def on_mount(self, handler):
        """
        Trigger an event when this element is mounted to the DOM.
        Valid for Zen Mode.
        """
        if callable(handler):
            func_name = EventManager.register(handler)
            self.attrs["data-pyx-mount"] = func_name
        return self
        
    def on_submit(self, handler):
        """
        Special handler for Form Submission.
        Prevents default and sends all form data.
        """
        if callable(handler):
            func_name = EventManager.register(handler)
            self.attrs["data-pyx-submit"] = func_name
        return self
    
    def bind(self, reactive_value, sync_on="input"):
        """
        Two-way binding to a reactive value.
        
        Usage:
            email = ui.rx("")
            ui.input().bind(email)
            
        The input value will be synced with the reactive value.
        Changes to reactive value will update the input.
        Changes to input will update the reactive value.
        
        Args:
            reactive_value: A ReactiveValue to bind to
            sync_on: Event to sync on ('input' for real-time, 'change' for blur)
        """
        from ..core.reactive import ReactiveValue
        
        # Generate unique ID for this element if not exists
        if "id" not in self.attrs:
            import uuid
            self.attrs["id"] = f"bound-{uuid.uuid4().hex[:8]}"
        
        element_id = self.attrs["id"]
        
        # Register binding on reactive value
        if isinstance(reactive_value, ReactiveValue):
            reactive_value.bind(element_id)
            
            # Set initial value
            self.attrs["value"] = str(reactive_value.value)
            
            # Create sync handler
            def sync_handler():
                # This runs on server, but we need client-side sync
                pass
            
            # Add client-side sync via JS
            # This sends the value back to server to update reactive value
            self.attrs[f"on{sync_on}"] = f"""
                (function() {{
                    const val = this.value;
                    if (window.ws && window.ws.readyState === WebSocket.OPEN) {{
                        window.ws.send(JSON.stringify({{
                            type: 'reactive_sync',
                            id: '{reactive_value._id}',
                            value: val
                        }}));
                    }}
                }}).call(this)
            """
        
        return self
    
    def model(self, name: str):
        """
        Set the name attribute for form models.
        
        Usage:
            ui.input().model("email")  # Same as .attr("name", "email")
        """
        self.attrs["name"] = name
        return self


    # =========================================================================
    # 1. RESPONSIVE & STATES (Modifiers)
    # =========================================================================
    def _state(self, prefix, *classes):
        return self.cls(*[f"{prefix}:{c}" for c in classes])

    def sm(self, *classes): return self._state("sm", *classes)
    def md(self, *classes): return self._state("md", *classes)
    def lg(self, *classes): return self._state("lg", *classes)
    def xl(self, *classes): return self._state("xl", *classes)
    def xxl(self, *classes): return self._state("2xl", *classes)

    def hover(self, *classes): return self._state("hover", *classes)
    def focus(self, *classes): return self._state("focus", *classes)
    def active(self, *classes): return self._state("active", *classes)
    def focus_within(self, *classes): return self._state("focus-within", *classes)
    def visited(self, *classes): return self._state("visited", *classes)
    def disabled(self, *classes): return self._state("disabled", *classes)
    def dark(self, *classes): return self._state("dark", *classes)
    def group_hover(self, *classes): return self._state("group-hover", *classes)
    def peer_checked(self, *classes): return self._state("peer-checked", *classes)
    def group(self): return self.cls("group")

    # =========================================================================
    # 2. LAYOUT
    # =========================================================================
    def aspect(self, val): return self.cls(f"aspect-{val}") # aspect-ratio
    def columns(self, val): return self.cls(f"columns-{val}")
    def break_after(self, val): return self.cls(f"break-after-{val}")
    def break_before(self, val): return self.cls(f"break-before-{val}")
    def break_inside(self, val): return self.cls(f"break-inside-{val}")
    def box_decoration(self, val): return self.cls(f"box-decoration-{val}")
    def box_sizing(self, val): return self.cls(f"box-{val}") # border / content
    
    # Display
    def block(self): return self.cls("block")
    def inline_block(self): return self.cls("inline-block")
    def inline(self): return self.cls("inline")
    def flex(self): return self.cls("flex")
    def inline_flex(self): return self.cls("inline-flex")
    def grid(self): return self.cls("grid")
    def inline_grid(self): return self.cls("inline-grid")
    def hidden(self): return self.cls("hidden")
    
    # Float & Clear & Isolation
    def float(self, val): return self.cls(f"float-{val}") # right, left, none
    def clear(self, val): return self.cls(f"clear-{val}")
    def isolate(self): return self.cls("isolate")
    def isolation_auto(self): return self.cls("isolation-auto")
    
    # Object Fit & Position
    def object_fit(self, val): return self.cls(f"object-{val}") # cover, contain
    def object_pos(self, val): return self.cls(f"object-{val}") # center, top...
    
    # Overflow & Overscroll
    def overflow_hidden(self): return self.cls("overflow-hidden")
    def overflow(self, val): return self.cls(f"overflow-{val}")
    def overflow_x(self, val): return self.cls(f"overflow-x-{val}")
    def overflow_y(self, val): return self.cls(f"overflow-y-{val}")
    def overscroll(self, val): return self.cls(f"overscroll-{val}")
    
    # Position
    def static(self): return self.cls("static")
    def fixed(self): return self.cls("fixed")
    def absolute(self): return self.cls("absolute")
    def relative(self): return self.cls("relative")
    def sticky(self): return self.cls("sticky")
    def top(self, val): return self.cls(f"top-{val}")
    def right(self, val): return self.cls(f"right-{val}")
    def bottom(self, val): return self.cls(f"bottom-{val}")
    def left(self, val): return self.cls(f"left-{val}")
    def inset(self, val): return self.cls(f"inset-{val}")
    def inset_x(self, val): return self.cls(f"inset-x-{val}")
    def inset_y(self, val): return self.cls(f"inset-y-{val}")
    
    # Visibility & Z-Index
    def visible(self): return self.cls("visible")
    def invisible(self): return self.cls("invisible")
    def z(self, val): return self.cls(f"z-{val}")

    # =========================================================================
    # 3. FLEXBOX & GRID
    # =========================================================================
    def basis(self, val): return self.cls(f"basis-{val}")
    def flex_row(self): return self.cls("flex-row")
    def flex_row_reverse(self): return self.cls("flex-row-reverse")
    def flex_col(self): return self.cls("flex-col")
    def flex_col_reverse(self): return self.cls("flex-col-reverse")
    def flex_wrap(self): return self.cls("flex-wrap")
    def flex_nowrap(self): return self.cls("flex-nowrap")
    def flex_1(self): return self.cls("flex-1")
    def flex_auto(self): return self.cls("flex-auto")
    def flex_none(self): return self.cls("flex-none")
    def grow(self): return self.cls("grow")
    def grow_0(self): return self.cls("grow-0")
    def shrink(self): return self.cls("shrink")
    def shrink_0(self): return self.cls("shrink-0")
    def order(self, val): return self.cls(f"order-{val}")
    
    # Grid
    def cols(self, val): return self.cls(f"grid-cols-{val}")
    def col_span(self, val): return self.cls(f"col-span-{val}")
    def col_start(self, val): return self.cls(f"col-start-{val}")
    def rows(self, val): return self.cls(f"grid-rows-{val}")
    def row_span(self, val): return self.cls(f"row-span-{val}")
    def row_start(self, val): return self.cls(f"row-start-{val}")
    def grid_flow(self, val): return self.cls(f"grid-flow-{val}") # row, col, dense
    def auto_cols(self, val): return self.cls(f"auto-cols-{val}")
    def auto_rows(self, val): return self.cls(f"auto-rows-{val}")
    
    # Gap
    def gap(self, val): return self.cls(f"gap-{val}")
    def gap_x(self, val): return self.cls(f"gap-x-{val}")
    def gap_y(self, val): return self.cls(f"gap-y-{val}")
    
    # Alignment
    def justify(self, val): return self.cls(f"justify-{val}") # start, end, center, between...
    def justify_items(self, val): return self.cls(f"justify-items-{val}")
    def justify_self(self, val): return self.cls(f"justify-self-{val}")
    def items(self, val): return self.cls(f"items-{val}") # align-items
    def content(self, children_val):
        if isinstance(children_val, list):
            self.children.extend(children_val)
        else:
            self.children.append(children_val)
        return self
    def align_content(self, val): return self.cls(f"content-{val}")
    def self(self, val): return self.cls(f"self-{val}") # align-self
    def place_content(self, val): return self.cls(f"place-content-{val}")
    def place_items(self, val): return self.cls(f"place-items-{val}")
    def place_self(self, val): return self.cls(f"place-self-{val}")

    # =========================================================================
    # 4. SPACING
    # =========================================================================
    def p(self, val): return self.cls(f"p-{val}")
    def px(self, val): return self.cls(f"px-{val}")
    def py(self, val): return self.cls(f"py-{val}")
    def pt(self, val): return self.cls(f"pt-{val}")
    def pr(self, val): return self.cls(f"pr-{val}")
    def pb(self, val): return self.cls(f"pb-{val}")
    def pl(self, val): return self.cls(f"pl-{val}")
    
    def m(self, val): return self.cls(f"m-{val}")
    def mx(self, val): return self.cls(f"mx-{val}")
    def my(self, val): return self.cls(f"my-{val}")
    def mt(self, val): return self.cls(f"mt-{val}")
    def mr(self, val): return self.cls(f"mr-{val}")
    def mb(self, val): return self.cls(f"mb-{val}")
    def ml(self, val): return self.cls(f"ml-{val}")
    
    def space_x(self, val): return self.cls(f"space-x-{val}")
    def space_y(self, val): return self.cls(f"space-y-{val}")

    # =========================================================================
    # 5. SIZING
    # =========================================================================
    def w(self, val): return self.cls(f"w-{val}")
    def w_full(self): return self.cls("w-full")
    def w_screen(self): return self.cls("w-screen")
    def min_w(self, val): return self.cls(f"min-w-{val}")
    def max_w(self, val): return self.cls(f"max-w-{val}")
    
    def h(self, val): return self.cls(f"h-{val}")
    def h_full(self): return self.cls("h-full")
    def h_screen(self): return self.cls("h-screen")
    def min_h(self, val): return self.cls(f"min-h-{val}")
    def max_h(self, val): return self.cls(f"max-h-{val}")

    # =========================================================================
    # 6. TYPOGRAPHY
    # =========================================================================
    def font(self, val): return self.cls(f"font-{val}") # sans, serif, mono, bold...
    def text(self, val): return self.cls(f"text-{val}") # size or color
    def antialiased(self): return self.cls("antialiased")
    def subpixel_antialiased(self): return self.cls("subpixel-antialiased")
    def italic(self): return self.cls("italic")
    def not_italic(self): return self.cls("not-italic")
    def tracking(self, val): return self.cls(f"tracking-{val}") # letter-spacing
    def line_clamp(self, val): return self.cls(f"line-clamp-{val}")
    def leading(self, val): return self.cls(f"leading-{val}") # line-height
    
    # List Style
    def list_style(self, val): return self.cls(f"list-{val}") # none, disc, decimal
    def list_inside(self): return self.cls("list-inside")
    def list_outside(self): return self.cls("list-outside")
    
    # Alignment & Color
    def text_align(self, val): return self.cls(f"text-{val}") # left, center...
    def center(self): return self.cls("text-center")
    def color(self, val): return self.cls(f"text-{val}")
    
    # Decoration
    def underline(self): return self.cls("underline")
    def overline(self): return self.cls("overline")
    def line_through(self): return self.cls("line-through")
    def no_underline(self): return self.cls("no-underline")
    def decoration(self, val): return self.cls(f"decoration-{val}") # color or style
    def decoration_style(self, val): return self.cls(f"decoration-{val}") # solid, double, dotted
    def decoration_thickness(self, val): return self.cls(f"decoration-{val}") # auto, from-font, 2...
    def underline_offset(self, val): return self.cls(f"underline-offset-{val}")
    
    # Transform & Layout
    def uppercase(self): return self.cls("uppercase")
    def lowercase(self): return self.cls("lowercase")
    def capitalize(self): return self.cls("capitalize")
    def truncate(self): return self.cls("truncate")
    def text_overflow(self, val): return self.cls(f"text-{val}") # ellipsis, clip
    def text_wrap(self, val): return self.cls(f"text-{val}") # wrap, nowrap, balance
    def indent(self, val): return self.cls(f"indent-{val}")
    def align_vertical(self, val): return self.cls(f"align-{val}") # baseline, top, middle...
    def whitespace(self, val): return self.cls(f"whitespace-{val}")
    def break_words(self): return self.cls("break-words")
    def break_all(self): return self.cls("break-all")
    def hyphens(self, val): return self.cls(f"hyphens-{val}")
    def content_none(self): return self.cls("content-none")

    # =========================================================================
    # 7. BACKGROUNDS
    # =========================================================================
    def bg(self, val): return self.cls(f"bg-{val}")
    def bg_image(self, val): return self.cls(f"bg-{val}") # none, gradient-to-r...
    def bg_gradient(self, dir="to-r"): return self.cls(f"bg-gradient-{dir}")
    def from_(self, val): return self.cls(f"from-{val}")
    def via_(self, val): return self.cls(f"via-{val}")
    def to_(self, val): return self.cls(f"to-{val}")
    
    def bg_attach(self, val): return self.cls(f"bg-{val}") # fixed, local, scroll
    def bg_clip(self, val): return self.cls(f"bg-clip-{val}") # border, padding, content, text
    def bg_origin(self, val): return self.cls(f"bg-origin-{val}")
    def bg_pos(self, val): return self.cls(f"bg-{val}") # bottom, center, left-bottom...
    def bg_repeat(self, val): return self.cls(f"bg-{val}") # repeat, no-repeat...
    def bg_size(self, val): return self.cls(f"bg-{val}") # auto, cover, contain

    # =========================================================================
    # 8. BORDERS & OUTLINES
    # =========================================================================
    def rounded(self, val=""): return self.cls(f"rounded-{val}" if val else "rounded")
    def rounded_t(self, val): return self.cls(f"rounded-t-{val}")
    # ... (other rounded variants imply standard usage)
    
    def border(self, val=""): return self.cls(f"border-{val}" if val else "border")
    def border_t(self, val=""): return self.cls(f"border-t-{val}" if val else "border-t")
    def border_b(self, val=""): return self.cls(f"border-b-{val}" if val else "border-b")
    def border_l(self, val=""): return self.cls(f"border-l-{val}" if val else "border-l")
    def border_r(self, val=""): return self.cls(f"border-r-{val}" if val else "border-r")
    def border_x(self, val=""): return self.cls(f"border-x-{val}" if val else "border-x")
    def border_y(self, val=""): return self.cls(f"border-y-{val}" if val else "border-y")
    def border_color(self, val): return self.cls(f"border-{val}")
    def border_style(self, val): return self.cls(f"border-{val}") # solid, dashed, dotted...
    
    def divide_x(self, val=""): return self.cls(f"divide-x-{val}" if val else "divide-x")
    def divide_y(self, val=""): return self.cls(f"divide-y-{val}" if val else "divide-y")
    def divide_color(self, val): return self.cls(f"divide-{val}")
    
    def outline(self, val=""): return self.cls(f"outline-{val}" if val else "outline") # 1, 2, none...
    def outline_color(self, val): return self.cls(f"outline-{val}")
    def outline_style(self, val): return self.cls(f"outline-{val}")
    def outline_offset(self, val): return self.cls(f"outline-offset-{val}")
    
    def ring(self, val=""): return self.cls(f"ring-{val}" if val else "ring")
    def ring_inset(self): return self.cls("ring-inset")
    def ring_color(self, val): return self.cls(f"ring-{val}")
    def ring_offset(self, val): return self.cls(f"ring-offset-{val}")

    # =========================================================================
    # 9. EFFECTS & FILTERS
    # =========================================================================
    def shadow(self, val=""): return self.cls(f"shadow-{val}" if val else "shadow")
    def shadow_color(self, val): return self.cls(f"shadow-{val}")
    def opacity(self, val): return self.cls(f"opacity-{val}")
    def mix_blend(self, val): return self.cls(f"mix-blend-{val}")
    def bg_blend(self, val): return self.cls(f"bg-blend-{val}")
    
    # Filters
    def filter(self): return self.cls("filter")
    def blur(self, val=""): return self.cls(f"blur-{val}" if val else "blur")
    def brightness(self, val): return self.cls(f"brightness-{val}")
    def contrast(self, val): return self.cls(f"contrast-{val}")
    def drop_shadow(self, val): return self.cls(f"drop-shadow-{val}")
    def grayscale(self, val=""): return self.cls(f"grayscale-{val}" if val else "grayscale")
    def hue_rotate(self, val): return self.cls(f"hue-rotate-{val}")
    def invert(self, val=""): return self.cls(f"invert-{val}" if val else "invert")
    def saturate(self, val): return self.cls(f"saturate-{val}")
    def sepia(self, val=""): return self.cls(f"sepia-{val}" if val else "sepia")
    def backdrop_blur(self, val=""): return self.cls(f"backdrop-blur-{val}" if val else "backdrop-blur")

    # =========================================================================
    # 10. TABLES
    # =========================================================================
    def border_collapse(self): return self.cls("border-collapse")
    def border_separate(self): return self.cls("border-separate")
    def border_spacing(self, val): return self.cls(f"border-spacing-{val}")
    def table_layout(self, val): return self.cls(f"table-{val}") # auto, fixed
    def caption_side(self, val): return self.cls(f"caption-{val}")

    # =========================================================================
    # 11. TRANSITIONS & ANIMATION
    # =========================================================================
    def transition(self, val="all"): return self.cls(f"transition-{val}" if val != "all" else "transition")
    def duration(self, val): return self.cls(f"duration-{val}")
    def ease(self, val): return self.cls(f"ease-{val}")
    def delay(self, val): return self.cls(f"delay-{val}")
    def animate(self, val): return self.cls(f"animate-{val}") # spin, ping, pulse, bounce

    # =========================================================================
    # 12. TRANSFORMS
    # =========================================================================
    def scale(self, val): return self.cls(f"scale-{val}")
    def rotate(self, val): return self.cls(f"rotate-{val}")
    def translate_x(self, val): return self.cls(f"translate-x-{val}")
    def translate_y(self, val): return self.cls(f"translate-y-{val}")
    def skew_x(self, val): return self.cls(f"skew-x-{val}")
    def skew_y(self, val): return self.cls(f"skew-y-{val}")
    def origin(self, val): return self.cls(f"origin-{val}")

    # =========================================================================
    # 13. INTERACTIVITY & SVG
    # =========================================================================
    # Method 'on' removed as it shadows the main implementation at line 83.
    # def on(self, event_name, handler):
    #     ...

    def accent(self, val): return self.cls(f"accent-{val}")
    def appearance_none(self): return self.cls("appearance-none")
    def cursor(self, val): return self.cls(f"cursor-{val}")
    def caret(self, val): return self.cls(f"caret-{val}")
    def pointer_events(self, val): return self.cls(f"pointer-events-{val}")
    def resize(self, val=""): return self.cls(f"resize-{val}" if val else "resize")
    def scroll_behavior(self, val): return self.cls(f"scroll-{val}") # auto, smooth
    def scroll_m(self, val): return self.cls(f"scroll-m-{val}")
    def scroll_p(self, val): return self.cls(f"scroll-p-{val}")
    def scroll_snap(self, val): return self.cls(f"snap-{val}") # none, x, y, both
    def snap_align(self, val): return self.cls(f"snap-{val}") # start, end, center
    def touch(self, val): return self.cls(f"touch-{val}") # auto, none, pan-x...
    def select(self, val): return self.cls(f"select-{val}") # none, text, all
    def will_change(self, val): return self.cls(f"will-change-{val}")
    
    # SVG
    def fill(self, val): return self.cls(f"fill-{val}")
    def stroke(self, val): return self.cls(f"stroke-{val}")
    def stroke_width(self, val): return self.cls(f"stroke-{val}")

    # =========================================================================
    # 14. ACCESSIBILITY
    # =========================================================================
    def sr_only(self): return self.cls("sr-only")
    def not_sr_only(self): return self.cls("not-sr-only")
    def forced_color_adjust(self, val): return self.cls(f"forced-color-adjust-{val}")

    # =========================================================================
    # CHILDREN MANAGEMENT (Helper)
    # =========================================================================
    def add(self, *children):
        # If children is a string, convert to list first
        if isinstance(self.children, str):
            if self.children:
                self.children = [self.children]
            else:
                self.children = []
        elif not isinstance(self.children, list):
            self.children = [self.children] if self.children else []
        
        self.children.extend(children)
        return self

    def render(self):
        c_str = " ".join(self.classes)
        a_str = " ".join([f'{k}="{v}"' for k,v in self.attrs.items()])
        
        inner = ""
        if isinstance(self.children, list):
            inner = "".join([c.render() if hasattr(c, 'render') else str(c) for c in self.children])
        elif hasattr(self.children, 'render'):
            inner = self.children.render()
        else:
            inner = str(self.children)
            
        void_tags = {"img", "input", "br", "hr", "meta", "link", "source", "area", "base", "col", "embed", "param", "track", "wbr"}
        if self.tag in void_tags:
            return f'<{self.tag} class="{c_str}" {a_str} />'
            
        return f'<{self.tag} class="{c_str}" {a_str}>{inner}</{self.tag}>'


class RawElement:
    """Element that renders raw HTML without escaping."""
    def __init__(self, html: str):
        self.html = html
        self.classes = []
        self.attrs = {}
    
    def render(self):
        return self.html
    
    # Allow chaining (no-op for raw elements)
    def cls(self, *classes): return self
    def id(self, component_id): return self
    def attr(self, key, value): return self


Element = PyxElement


# =========================================================================
# ZEN MODE ENGINE (Global Context)
# =========================================================================

class ContextStack:
    """Manages the current hierarchy of UI elements (The Zen Stack)."""
    def __init__(self):
        self.stack = [] 
        self.root = None

    def push(self, element):
        """Enter a container (e.g. inside a row or card)"""
        # Always add to current top of stack first
        if self.stack:
            self.stack[-1].add(element)
        elif self.root:
            # If stack is empty but root exists (direct child of root)
            self.root.add(element)
            
        self.stack.append(element)
        return element

    def pop(self):
        """Exit the current container"""
        if self.stack:
            return self.stack.pop()
        return None

    def add(self, element):
        """Add an element to the current active container"""
        if self.stack:
            self.stack[-1].add(element)
        elif self.root:
            self.root.add(element)

    def reset(self):
        """Reset the context for a new page render"""
        self.stack = []
        # Default Root: Clean container with max width, acts as body wrapper
        self.root = PyxElement("div").cls("min-h-screen bg-slate-50 text-slate-900 font-sans p-8")
        return self.root

# Global Context Instance (Thread-safe ideally, but simplified for single worker/async)
_ctx = ContextStack()

class LayoutContext:
    def __init__(self, element):
        self.element = element
        
    def __enter__(self):
        _ctx.push(self.element)
        return self.element
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        _ctx.pop()

class UI:
    """
    Unified Factory for UI components.
    Supports both Direct Mode (UI.div()) and Zen Mode (UI.page()).
    """
    
    # --- ZEN MODE METHODS ---
    @staticmethod
    def page():
        """Initialize a new page context. Call this at start of function."""
        return _ctx.reset()

    @staticmethod
    def add(element):
        """Add an arbitrary element to the current Zen Context."""
        _ctx.add(element)
        return element

    @staticmethod
    def raw(html: str):
        """Create a raw HTML element (no escaping)."""
        return RawElement(html)


    @staticmethod
    def title(text):
        el = UI.h1(text).text("3xl").font("bold").text("gray-900").mb(2)
        _ctx.add(el)
        return el

    @staticmethod
    def subtitle(text):
        el = UI.p(text).text("lg").text("gray-500").mb(6)
        _ctx.add(el)
        return el
    
    @staticmethod
    def text(text):
        el = UI.p(text).text("gray-600").mb(2)
        _ctx.add(el)
        return el

    @staticmethod
    def button(text, on_click=None, primary=True):
        el = PyxElement("button", text).px(4).py(2).rounded("md").bg("blue-600").text("white").font("medium").hover("bg-blue-700").cursor("pointer")
        
        if on_click:
            handler_name = on_click.__name__ if callable(on_click) else str(on_click)
            el.attr("onclick", f"ws.send(JSON.stringify({{ 'type': 'event', 'handler': '{handler_name}' }}))")

        if not primary:
            # Secondary override
            el.bg("white").text("gray-700").border("gray-300").hover("bg-gray-50")
            
        _ctx.add(el)
        return el
    
    @staticmethod
    def divider():
        el = UI.div().h("px").bg("gray-200").my(6)
        _ctx.add(el)
        return el

    # --- CLIENT INTERACTION METHODS ---
    
    @staticmethod
    def navigate(url: str):
        """
        Navigate to a URL (client-side).
        Returns a script element that triggers navigation.
        
        Usage:
            ui.button("Go to Dashboard").attr("onclick", "PyX.navigate('/dashboard')")
        """
        return RawElement(f'<script>PyX.navigate("{url}")</script>')
    
    @staticmethod
    def toast(message: str, variant: str = "info", duration: int = 3000):
        """
        Show a toast notification.
        
        Args:
            message: Toast message
            variant: success, error, warning, info
            duration: Duration in milliseconds
        
        Usage in event handler:
            # Server-side (sends via WebSocket)
            ui.toast("Data saved!", "success")
        """
        return RawElement(f'<script>PyX.toast("{message}", "{variant}", {duration})</script>')
    
    @staticmethod
    def form(id: str, on_submit: str = None):
        """
        Create a form element with automatic binding.
        
        Args:
            id: Form ID
            on_submit: Handler name to call on submit
            
        Usage:
            with ui.form("login-form", on_submit="handle_login") as form:
                ui.input("email", "Email")
                ui.input("password", "Password")
                ui.button("Submit")
        """
        el = UI.element("form").id(id)
        if on_submit:
            el.attr("data-pyx-submit", on_submit)
            el.attr("onsubmit", f"event.preventDefault(); PyX.submitForm('{id}', '{on_submit}')")
        return LayoutContext(el)
    
    @staticmethod

    # --- LAYOUT MANAGERS (Context Managers) ---
    @staticmethod
    def container():
        el = UI.div()
        return LayoutContext(el)
        
    @staticmethod
    def row(gap=4):
        el = UI.div().flex().flex_row().gap(gap).items("center")
        return LayoutContext(el)

    @staticmethod
    def col(gap=4):
        el = UI.div().flex().flex_col().gap(gap)
        return LayoutContext(el)
    
    @staticmethod
    def grid(cols=2, gap=6):
        el = UI.div().grid().cols(cols).gap(gap)
        return LayoutContext(el)

    # --- MODERN LAYOUT HELPERS (Reflex/SwiftUI Style) ---
    @staticmethod
    def vstack(gap=4):
        """Vertical Stack (Column)"""
        el = UI.div().flex().flex_col().gap(gap)
        return LayoutContext(el)
        
    @staticmethod
    def hstack(gap=4):
        """Horizontal Stack (Row)"""
        el = UI.div().flex().flex_row().items("center").gap(gap)
        return LayoutContext(el)
        
    @staticmethod
    def center():
        """Center Content"""
        el = UI.div().flex().justify("center").items("center")
        return LayoutContext(el)

    @staticmethod
    def card(title=None):
        el = UI.div().bg("white").p(6).rounded("xl").shadow("sm").border("gray-200")
        if title:
             el.add(UI.h3(title).text("lg").font("semibold").mb(4))
        return LayoutContext(el)
        
    @staticmethod
    def metric(label, value, trend=None, color=None):
        """Smart Metric Card"""
        if trend and not color:
            color = "green" if "+" in trend else "red"
        
        el = UI.div(
            UI.p(label).text("sm").font("medium").text("gray-500"),
            UI.div(
                UI.h3(value).text("3xl").font("bold").text("gray-900"),
                UI.span(trend).bg(f"{color}-100").text(f"{color}-800").px(2).rounded("full").text("xs").font("bold") if trend else ""
            ).flex().items("baseline").gap(3)
        ).bg("white").p(6).rounded("xl").shadow("sm").border("gray-200")
        
        # REMOVED: _ctx.add(el) -- Fixes Ghost Element bug
        return el

    # --- STANDARD FACTORY METHODS ---
    @staticmethod
    def div(*children, className=""): return PyxElement("div", list(children)).cls(className)
    
    # Semantic Tags
    @staticmethod
    def section(*children): return PyxElement("section", list(children))
    @staticmethod
    def article(*children): return PyxElement("article", list(children))
    @staticmethod
    def header(*children): return PyxElement("header", list(children))
    @staticmethod
    def footer(*children): return PyxElement("footer", list(children))
    @staticmethod
    def nav(*children): return PyxElement("nav", list(children))
    @staticmethod
    def main(*children): return PyxElement("main", list(children))
    
    # Forms & Lists
    @staticmethod
    def form(*children): return PyxElement("form", list(children))
    @staticmethod
    def label(text): return PyxElement("label", text)
    @staticmethod
    def ul(*children): return PyxElement("ul", list(children))
    @staticmethod
    def li(*children): return PyxElement("li", list(children))

    @staticmethod
    def span(text, className=""): return PyxElement("span", text).cls(className)
    @staticmethod
    def p(text="", className=""): return PyxElement("p", text).cls(className)
    @staticmethod
    def a(text, href="#", className=""): return PyxElement("a", text).attr("href", href).cls(className)
    
    @staticmethod
    def i(text="", **kwargs):
        """Icon element (i tag)"""
        el = PyxElement("i", text)
        for k, v in kwargs.items():
            el.attr(k.replace("_", "-"), v)
        return el
    
    @staticmethod
    def pre(text=""): return PyxElement("pre", text)
    @staticmethod
    def code(text=""): return PyxElement("code", text)
    
    # UI.input, UI.textarea etc... (Compact version)
    @staticmethod
    def input(type="text", placeholder=""):
        return PyxElement("input").attr("type", type).attr("placeholder", placeholder) \
            .p(2).border("gray-300").rounded("md").w_full().bg("white").text("gray-900").focus("ring-2", "ring-blue-500")

    @staticmethod
    def textarea(placeholder=""):
        return PyxElement("textarea").attr("placeholder", placeholder) \
            .p(2).border("gray-300").rounded("md").w_full().bg("white").text("gray-900").focus("ring-2", "ring-blue-500")

    @staticmethod
    def select(*children):
        return PyxElement("select", list(children)).p(2).border("gray-300").rounded("md").bg("white").text("gray-900")

    @staticmethod
    def option(text, value=None):
        el = PyxElement("option", text)
        if value: el.attr("value", value)
        return el
        
    @staticmethod
    def h1(text, className=""): return PyxElement("h1", text).text("3xl").font("bold").cls(className)
    @staticmethod
    def h2(text, className=""): return PyxElement("h2", text).text("2xl").font("semibold").cls(className)
    @staticmethod
    def h3(text, className=""): return PyxElement("h3", text).text("xl").font("medium").cls(className)
    @staticmethod
    def h4(text, className=""): return PyxElement("h4", text).text("lg").font("medium").cls(className)
    @staticmethod
    def h5(text, className=""): return PyxElement("h5", text).font("medium").cls(className)
    @staticmethod
    def h6(text, className=""): return PyxElement("h6", text).font("medium").cls(className)
    
    @staticmethod
    def strong(text): return PyxElement("strong", text).font("bold")
    @staticmethod
    def em(text): return PyxElement("em", text).cls("italic")
    @staticmethod
    def hr(): return PyxElement("hr").cls("my-4 border-gray-200")
    @staticmethod
    def br(): return PyxElement("br")
    
    @staticmethod
    def img(
        src: str,
        alt: str = "",
        width: int = None,
        height: int = None,
        lazy: bool = True,
        placeholder: str = None,  # "blur", "skeleton", "color"
        blur_data_url: str = None,
        priority: bool = False,
        sizes: str = None,
        srcset: list = None,
        object_fit: str = "cover",  # "cover", "contain", "fill", "none"
        className: str = ""
    ):
        """
        Enhanced Image component with optimization.
        
        Usage:
            ui.img("/hero.jpg", alt="Hero image")
            ui.img("/photo.jpg", width=800, height=600, lazy=True)
            ui.img("/avatar.jpg", placeholder="blur", blur_data_url="data:...")
            ui.img("/banner.jpg", priority=True)  # No lazy loading
            ui.img("/responsive.jpg", srcset=[
                {"src": "/img-400.jpg", "size": "400w"},
                {"src": "/img-800.jpg", "size": "800w"},
            ], sizes="(max-width: 600px) 400px, 800px")
        """
        # Build attributes
        attrs = {
            "src": src,
            "alt": alt,
        }
        
        if width:
            attrs["width"] = width
        if height:
            attrs["height"] = height
        
        # Lazy loading
        if lazy and not priority:
            attrs["loading"] = "lazy"
            attrs["decoding"] = "async"
        
        # Object fit
        fit_classes = {
            "cover": "object-cover",
            "contain": "object-contain",
            "fill": "object-fill",
            "none": "object-none",
        }
        fit_class = fit_classes.get(object_fit, "object-cover")
        
        # Responsive srcset
        if srcset:
            srcset_str = ", ".join([f"{s['src']} {s['size']}" for s in srcset])
            attrs["srcset"] = srcset_str
        if sizes:
            attrs["sizes"] = sizes
        
        # Build element
        el = PyxElement("img")
        for key, val in attrs.items():
            el = el.attr(key, val)
        el = el.cls(f"{fit_class} {className}")
        
        # Placeholder wrapper
        if placeholder:
            wrapper_id = f"img-{id(el)}"
            placeholder_html = ""
            
            if placeholder == "blur" and blur_data_url:
                placeholder_html = f'''
                    <img src="{blur_data_url}" alt="" 
                         class="absolute inset-0 w-full h-full {fit_class} blur-xl scale-110 transition-opacity duration-300"
                         aria-hidden="true">
                '''
            elif placeholder == "skeleton":
                placeholder_html = f'''
                    <div class="absolute inset-0 bg-gray-200 animate-pulse"></div>
                '''
            elif placeholder == "color":
                placeholder_html = f'''
                    <div class="absolute inset-0 bg-gray-300"></div>
                '''
            
            return PyxElement("div").cls(f"relative overflow-hidden {className}").attr("style", f"width:{width}px;height:{height}px" if width and height else "").content(f'''
                {placeholder_html}
                <img src="{src}" alt="{alt}" 
                     {"loading='lazy' decoding='async'" if lazy and not priority else ""}
                     {f"width='{width}'" if width else ""} {f"height='{height}'" if height else ""}
                     {f"srcset='{srcset_str}'" if srcset else ""} {f"sizes='{sizes}'" if sizes else ""}
                     class="{fit_class} relative z-10 transition-opacity duration-300"
                     onload="this.style.opacity=1; this.previousElementSibling && (this.previousElementSibling.style.opacity=0)"
                     style="opacity: 0">
            ''')
        
        return el
    
    @staticmethod
    def picture(
        src: str,
        alt: str = "",
        formats: list = None,  # ["webp", "avif"]
        width: int = None,
        height: int = None,
        lazy: bool = True,
        className: str = ""
    ):
        """
        Picture element with multiple formats.
        
        Usage:
            ui.picture("/hero.jpg", formats=["webp", "avif"])
        """
        formats = formats or ["webp"]
        
        sources = ""
        for fmt in formats:
            # Assume same filename with different extension
            fmt_src = src.rsplit(".", 1)[0] + f".{fmt}"
            sources += f'<source srcset="{fmt_src}" type="image/{fmt}">\n'
        
        return PyxElement("picture").cls(className).content(f'''
            {sources}
            <img src="{src}" alt="{alt}" 
                 {"loading='lazy' decoding='async'" if lazy else ""}
                 {f"width='{width}'" if width else ""} {f"height='{height}'" if height else ""}
                 class="w-full h-auto">
        ''')

    @staticmethod
    def svg(path_d, viewbox="0 0 24 24"):
        return PyxElement("svg", content=[
            PyxElement("path").attr("stroke-linecap", "round").attr("stroke-linejoin", "round").attr("d", path_d)
        ]).attr("viewBox", viewbox).attr("fill", "none").attr("stroke", "currentColor").attr("stroke-width", "1.5").cls("w-6 h-6")

    # =========================================================================
    # ENTERPRISE COMPONENTS (Zen Mode Wrappers)
    # =========================================================================
    
    @staticmethod
    def datagrid(data, **kwargs):
        """
        Zen Mode DataGrid.
        
        Usage:
            ui.datagrid(users)
            ui.datagrid(products, pagination=True, page_size=20)
        """
        from ..web.components.datagrid import DataGrid
        return DataGrid(data=data, **kwargs)
    
    @staticmethod
    def kanban(columns, render_card, **kwargs):
        """
        Zen Mode Kanban Board.
        
        Usage:
            ui.kanban(columns, render_card=lambda c: ui.div(c["title"]))
        """
        from ..web.components.dragdrop import Kanban
        return Kanban(columns=columns, render_card=render_card, **kwargs)
    
    @staticmethod
    def sortable(items, render_item, **kwargs):
        """
        Zen Mode Sortable List.
        
        Usage:
            ui.sortable(tasks, render_item=lambda t: ui.div(t["name"]))
        """
        from ..web.components.dragdrop import SortableList
        return SortableList(items=items, render_item=render_item, **kwargs)
    
    @staticmethod
    def candlestick(data, **kwargs):
        """
        Zen Mode Candlestick Chart.
        
        Usage:
            ui.candlestick(ohlc_data, with_volume=True)
        """
        from ..web.components.trading import CandlestickChart
        return CandlestickChart(data=data, **kwargs)
    
    @staticmethod
    def trading_chart(data, series, **kwargs):
        """
        Zen Mode Trading Chart (multi-series).
        
        Usage:
            ui.trading_chart(data, series=[Series(type="line")])
        """
        from ..web.components.trading import TradingChart
        return TradingChart(data=data, series=series, **kwargs)
    
    @staticmethod
    def draggable(content, data=None, **kwargs):
        """
        Zen Mode Draggable element.
        
        Usage:
            ui.draggable(ui.div("Drag me"), data={"id": 1})
        """
        from ..web.components.dragdrop import Draggable
        return Draggable(content=content, data=data, **kwargs)
    
    @staticmethod
    def dropzone(content=None, on_drop=None, **kwargs):
        """
        Zen Mode Drop Zone.
        
        Usage:
            ui.dropzone(ui.div("Drop here"), on_drop=handle_drop)
        """
        from ..web.components.dragdrop import DropZone
        return DropZone(content=content, on_drop=on_drop, **kwargs)

    # =========================================================================
    # REACTIVE CONTROL FLOW (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def cond(condition, true_component, false_component=None):
        """
        Conditional rendering.
        
        Usage:
            ui.cond(
                UserState.is_logged_in,
                ui.div("Welcome!"),
                ui.div("Please login")
            )
        """
        from ..core.reactive import Cond
        return Cond(condition, true_component, false_component)
    
    @staticmethod
    def foreach(items, render_fn, key="id"):
        """
        List rendering.
        
        Usage:
            ui.foreach(
                ProductState.products,
                lambda p: ui.div(p["name"])
            )
        """
        from ..core.reactive import ForEach
        return ForEach(items, render_fn, key)
    
    @staticmethod
    def match(value, cases, default=None):
        """
        Pattern matching / switch-case.
        
        Usage:
            ui.match(
                PageState.tab,
                {
                    "home": ui.div("Home"),
                    "settings": ui.div("Settings"),
                },
                default=ui.div("Not Found")
            )
        """
        from ..core.reactive import Match
        return Match(value, cases, default)
    
    @staticmethod
    def text(value):
        """
        Reactive text that auto-updates.
        
        Usage:
            ui.text(CounterState.count)
            ui.text(lambda: f"Total: {CartState.total}")
        """
        from ..core.reactive import ReactiveText
        return ReactiveText(value)
    
    @staticmethod
    def rx(initial_value):
        """
        Create a reactive value.
        
        Usage:
            count = ui.rx(0)
            count.value = 5  # Triggers UI update
        """
        from ..core.reactive import ReactiveValue
        return ReactiveValue(initial_value)

    # =========================================================================
    # ESSENTIAL COMPONENTS (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def tabs(tabs, default=None, **kwargs):
        """
        Zen Mode Tabs.
        
        Usage:
            ui.tabs([
                {"id": "home", "label": "Home", "content": ui.div("...")},
                {"id": "settings", "label": "Settings", "content": ui.div("...")},
            ])
        """
        from ..web.components.essential import Tabs
        return Tabs(tabs=tabs, default=default, **kwargs)
    
    @staticmethod
    def accordion(items, **kwargs):
        """
        Zen Mode Accordion.
        
        Usage:
            ui.accordion([
                {"title": "Section 1", "content": ui.div("...")},
                {"title": "Section 2", "content": ui.div("...")},
            ])
        """
        from ..web.components.essential import Accordion
        return Accordion(items=items, **kwargs)
    
    @staticmethod
    def progress(value, max=100, **kwargs):
        """
        Zen Mode Progress Bar.
        
        Usage:
            ui.progress(75)
            ui.progress(value, color="green", show_label=True)
        """
        from ..web.components.essential import Progress
        return Progress(value=value, max=max, **kwargs)
    
    @staticmethod
    def skeleton(width="100%", height="20px", **kwargs):
        """
        Zen Mode Skeleton Loading.
        
        Usage:
            ui.skeleton()
            ui.skeleton("200px", "40px")
        """
        from ..web.components.essential import Skeleton
        return Skeleton(width=width, height=height, **kwargs)
    
    @staticmethod
    def tooltip(content, text, **kwargs):
        """
        Zen Mode Tooltip.
        
        Usage:
            ui.tooltip(ui.button("?"), "Help text here")
        """
        from ..web.components.essential import Tooltip
        return Tooltip(content=content, text=text, **kwargs)
    
    @staticmethod
    def badge(text, color="blue", **kwargs):
        """
        Zen Mode Badge.
        
        Usage:
            ui.badge("New", "green")
            ui.badge("Pending", "yellow", variant="subtle")
        """
        from ..web.components.essential import Badge
        return Badge(text=text, color=color, **kwargs)

    # =========================================================================
    # DASHBOARD COMPONENTS (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def stat(title, value, **kwargs):
        """
        Zen Mode Stat Card.
        
        Usage:
            ui.stat("Revenue", "$12,450", change="+12%", trend="up")
        """
        from ..web.components.dashboard import StatCard
        return StatCard(title=title, value=value, **kwargs)
    
    @staticmethod
    def timeline(items, **kwargs):
        """
        Zen Mode Timeline.
        
        Usage:
            ui.timeline([
                {"title": "Order placed", "time": "2 hours ago"},
                {"title": "Shipped", "time": "1 hour ago", "active": True},
            ])
        """
        from ..web.components.dashboard import Timeline
        return Timeline(items=items, **kwargs)
    
    @staticmethod
    def stepper(steps, current=0, **kwargs):
        """
        Zen Mode Stepper.
        
        Usage:
            ui.stepper(["Account", "Profile", "Done"], current=1)
        """
        from ..web.components.dashboard import Stepper
        return Stepper(steps=steps, current=current, **kwargs)
    
    @staticmethod
    def alert(message, variant="info", **kwargs):
        """
        Zen Mode Alert.
        
        Usage:
            ui.alert("Success!", variant="success")
            ui.alert("Warning", variant="warning", dismissible=True)
        """
        from ..web.components.dashboard import Alert
        return Alert(message=message, variant=variant, **kwargs)
    
    @staticmethod
    def empty(title, **kwargs):
        """
        Zen Mode Empty State.
        
        Usage:
            ui.empty("No results", description="Try another search", icon="search")
        """
        from ..web.components.dashboard import EmptyState
        return EmptyState(title=title, **kwargs)
    
    @staticmethod
    def avatar(src=None, name=None, **kwargs):
        """
        Zen Mode Avatar.
        
        Usage:
            ui.avatar("/user.jpg", "John Doe")
            ui.avatar(name="JD", size="lg")
        """
        from ..web.components.dashboard import Avatar
        return Avatar(src=src, name=name, **kwargs)
    
    @staticmethod
    def avatar_group(avatars, **kwargs):
        """
        Zen Mode Avatar Group.
        
        Usage:
            ui.avatar_group([
                {"src": "/user1.jpg", "name": "John"},
                {"name": "Jane"},
            ], max=3)
        """
        from ..web.components.dashboard import AvatarGroup
        return AvatarGroup(avatars=avatars, **kwargs)
    
    @staticmethod
    def breadcrumb(items, **kwargs):
        """
        Zen Mode Breadcrumb.
        
        Usage:
            ui.breadcrumb([
                {"label": "Home", "href": "/"},
                {"label": "Products"},
            ])
        """
        from ..web.components.dashboard import Breadcrumb
        return Breadcrumb(items=items, **kwargs)

    # =========================================================================
    # ADVANCED COMPONENTS (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def command_palette(commands, **kwargs):
        """
        Zen Mode Command Palette (Cmd+K).
        
        Usage:
            ui.command_palette([
                {"id": "home", "label": "Go to Home", "icon": "home"},
                {"id": "settings", "label": "Settings", "shortcut": "⌘S"},
            ])
        """
        from ..web.components.advanced import CommandPalette
        return CommandPalette(commands=commands, **kwargs)
    
    @staticmethod
    def dropdown(trigger, items, **kwargs):
        """
        Zen Mode Dropdown Menu.
        
        Usage:
            ui.dropdown(
                ui.button("Actions"),
                [
                    {"label": "Edit", "icon": "edit"},
                    {"type": "divider"},
                    {"label": "Delete", "icon": "trash-2", "variant": "danger"},
                ]
            )
        """
        from ..web.components.advanced import DropdownMenu
        return DropdownMenu(trigger=trigger, items=items, **kwargs)
    
    @staticmethod
    def drawer(content, **kwargs):
        """
        Zen Mode Drawer/Slide Panel.
        
        Usage:
            ui.drawer(ui.div("Content"), title="Settings", position="right")
        """
        from ..web.components.advanced import Drawer
        return Drawer(content=content, **kwargs)
    
    @staticmethod
    def pagination(total, page_size=10, current=1, **kwargs):
        """
        Zen Mode Pagination.
        
        Usage:
            ui.pagination(total=100, page_size=10, current=1)
        """
        from ..web.components.advanced import Pagination
        return Pagination(total=total, page_size=page_size, current=current, **kwargs)

    # =========================================================================
    # WEB STRUCTURE COMPONENTS (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def footer(
        brand=None,
        links=None,
        social=None,
        copyright=None,
        className=""
    ):
        """
        Zen Mode Footer component.
        
        Usage:
            ui.footer(
                brand=ui.span("MyApp"),
                links=[
                    {"title": "Product", "items": [
                        {"label": "Features", "href": "/features"},
                        {"label": "Pricing", "href": "/pricing"},
                    ]},
                    {"title": "Company", "items": [
                        {"label": "About", "href": "/about"},
                        {"label": "Blog", "href": "/blog"},
                    ]},
                ],
                social=[
                    {"icon": "twitter", "href": "https://twitter.com"},
                    {"icon": "github", "href": "https://github.com"},
                ],
                copyright="© 2024 MyApp. All rights reserved."
            )
        """
        links = links or []
        social = social or []
        
        # Brand
        brand_html = ""
        if brand:
            brand_html = brand.render() if hasattr(brand, 'render') else str(brand)
        
        # Link columns
        links_html = ""
        for col in links:
            items_html = ""
            for item in col.get("items", []):
                items_html += f'<a href="{item.get("href", "#")}" class="block text-gray-500 hover:text-gray-700 py-1">{item.get("label", "")}</a>'
            links_html += f'''
                <div>
                    <h3 class="font-semibold text-gray-900 mb-3">{col.get("title", "")}</h3>
                    {items_html}
                </div>
            '''
        
        # Social icons
        social_html = ""
        for s in social:
            social_html += f'''
                <a href="{s.get('href', '#')}" class="text-gray-400 hover:text-gray-600 p-2" target="_blank">
                    <i data-lucide="{s.get('icon', 'link')}" class="w-5 h-5"></i>
                </a>
            '''
        
        return PyxElement("footer").cls(f"bg-gray-50 border-t {className}").content(f'''
            <div class="container mx-auto px-4 py-12">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
                    <div class="col-span-2 md:col-span-1">
                        <div class="mb-4">{brand_html}</div>
                        <div class="flex gap-2">{social_html}</div>
                    </div>
                    {links_html}
                </div>
                <div class="border-t pt-8 text-center text-gray-500 text-sm">
                    {copyright or ""}
                </div>
            </div>
            <script src="https://unpkg.com/lucide@latest"></script>
            <script>lucide.createIcons();</script>
        ''')
    
    @staticmethod
    def sidebar(
        items=None,
        header=None,
        footer=None,
        collapsed=False,
        className=""
    ):
        """
        Zen Mode Sidebar component.
        
        Usage:
            ui.sidebar(
                header=ui.span("Dashboard").style(font="bold", text="lg"),
                items=[
                    {"label": "Home", "icon": "home", "href": "/"},
                    {"label": "Users", "icon": "users", "href": "/users"},
                    {"type": "divider"},
                    {"label": "Settings", "icon": "settings", "href": "/settings"},
                ]
            )
        """
        items = items or []
        
        header_html = ""
        if header:
            header_html = header.render() if hasattr(header, 'render') else str(header)
        
        footer_html = ""
        if footer:
            footer_html = footer.render() if hasattr(footer, 'render') else str(footer)
        
        items_html = ""
        for item in items:
            if item.get("type") == "divider":
                items_html += '<div class="border-t my-2"></div>'
            elif item.get("type") == "header":
                items_html += f'<p class="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">{item.get("label", "")}</p>'
            else:
                icon = item.get("icon", "")
                icon_html = f'<i data-lucide="{icon}" class="w-5 h-5"></i>' if icon else ""
                active = "bg-blue-50 text-blue-600" if item.get("active") else "text-gray-700 hover:bg-gray-100"
                items_html += f'''
                    <a href="{item.get('href', '#')}" class="flex items-center gap-3 px-4 py-2.5 rounded-lg {active}">
                        {icon_html}
                        <span class="{'hidden' if collapsed else ''}">{item.get('label', '')}</span>
                    </a>
                '''
        
        width = "w-16" if collapsed else "w-64"
        
        return PyxElement("aside").cls(f"{width} bg-white border-r h-screen flex flex-col {className}").content(f'''
            <div class="p-4 border-b">{header_html}</div>
            <nav class="flex-1 p-2 space-y-1 overflow-y-auto">{items_html}</nav>
            <div class="p-4 border-t">{footer_html}</div>
            <script src="https://unpkg.com/lucide@latest"></script>
            <script>lucide.createIcons();</script>
        ''')
    
    @staticmethod
    def hero(
        title=None,
        subtitle=None,
        actions=None,
        image=None,
        align="center",
        className=""
    ):
        """
        Zen Mode Hero Section.
        
        Usage:
            ui.hero(
                title="Build Amazing Apps",
                subtitle="The Python framework for modern web development",
                actions=ui.hstack(
                    ui.button("Get Started").style(bg="blue-600", color="white", px=6, py=3, rounded="lg"),
                    ui.button("Learn More").style(border="gray-300", px=6, py=3, rounded="lg"),
                ),
                image="/hero.png"
            )
        """
        title_html = title or ""
        subtitle_html = subtitle or ""
        
        actions_html = ""
        if actions:
            actions_html = actions.render() if hasattr(actions, 'render') else str(actions)
        
        image_html = ""
        if image:
            image_html = f'<img src="{image}" alt="Hero" class="w-full max-w-lg mx-auto rounded-lg shadow-xl">'
        
        align_class = "text-center" if align == "center" else "text-left"
        
        return PyxElement("section").cls(f"py-20 px-4 {className}").content(f'''
            <div class="container mx-auto max-w-4xl {align_class}">
                <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">{title_html}</h1>
                <p class="text-xl text-gray-600 mb-8 max-w-2xl {'mx-auto' if align == 'center' else ''}">{subtitle_html}</p>
                <div class="flex gap-4 {'justify-center' if align == 'center' else ''} mb-12">{actions_html}</div>
                {image_html}
            </div>
        ''')
    
    @staticmethod
    def breadcrumb(items, separator="/", className=""):
        """
        Zen Mode Breadcrumb.
        
        Usage:
            ui.breadcrumb([
                {"label": "Home", "href": "/"},
                {"label": "Products", "href": "/products"},
                {"label": "Electronics"},  # Current (no href)
            ])
        """
        items_html = ""
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            if is_last:
                items_html += f'<span class="text-gray-900 font-medium">{item.get("label", "")}</span>'
            else:
                items_html += f'''
                    <a href="{item.get('href', '#')}" class="text-gray-500 hover:text-gray-700">{item.get("label", "")}</a>
                    <span class="mx-2 text-gray-400">{separator}</span>
                '''
        
        return PyxElement("nav").cls(f"flex items-center text-sm {className}").attr("aria-label", "Breadcrumb").content(items_html)
    
    @staticmethod
    def tabs(items, default=0, className=""):
        """
        Zen Mode Tabs component.
        
        Usage:
            ui.tabs([
                {"label": "Overview", "content": ui.div("Overview content")},
                {"label": "Features", "content": ui.div("Features content")},
                {"label": "Pricing", "content": ui.div("Pricing content")},
            ])
        """
        import uuid
        tabs_id = f"tabs-{uuid.uuid4().hex[:8]}"
        
        tabs_html = ""
        panels_html = ""
        for i, item in enumerate(items):
            active = i == default
            tab_class = "border-b-2 border-blue-600 text-blue-600" if active else "text-gray-500 hover:text-gray-700"
            content = item.get("content", "")
            content_html = content.render() if hasattr(content, 'render') else str(content)
            
            tabs_html += f'''
                <button onclick="switchTab('{tabs_id}', {i})" 
                        class="px-4 py-3 font-medium {tab_class}" 
                        data-tab="{i}">
                    {item.get("label", "")}
                </button>
            '''
            panels_html += f'''
                <div class="tab-panel {'block' if active else 'hidden'}" data-panel="{i}">
                    {content_html}
                </div>
            '''
        
        return PyxElement("div").cls(className).content(f'''
            <div class="border-b flex gap-2" id="{tabs_id}-tabs">{tabs_html}</div>
            <div class="py-4" id="{tabs_id}-panels">{panels_html}</div>
            <script>
                function switchTab(id, index) {{
                    document.querySelectorAll('#' + id + '-tabs button').forEach((btn, i) => {{
                        btn.className = i === index 
                            ? 'px-4 py-3 font-medium border-b-2 border-blue-600 text-blue-600'
                            : 'px-4 py-3 font-medium text-gray-500 hover:text-gray-700';
                    }});
                    document.querySelectorAll('#' + id + '-panels .tab-panel').forEach((panel, i) => {{
                        panel.className = i === index ? 'tab-panel block' : 'tab-panel hidden';
                    }});
                }}
            </script>
        ''')
    
    @staticmethod
    def accordion(items, multiple=False, className=""):
        """
        Zen Mode Accordion component.
        
        Usage:
            ui.accordion([
                {"title": "What is PyX?", "content": "PyX is a Python web framework..."},
                {"title": "How to install?", "content": "pip install pyx"},
                {"title": "Is it free?", "content": "Yes, it's open source!"},
            ])
        """
        import uuid
        acc_id = f"acc-{uuid.uuid4().hex[:8]}"
        
        items_html = ""
        for i, item in enumerate(items):
            content = item.get("content", "")
            content_html = content.render() if hasattr(content, 'render') else str(content)
            
            items_html += f'''
                <div class="border-b">
                    <button onclick="toggleAccordion('{acc_id}', {i}, {str(multiple).lower()})"
                            class="w-full flex items-center justify-between px-4 py-4 text-left hover:bg-gray-50">
                        <span class="font-medium text-gray-900">{item.get("title", "")}</span>
                        <svg class="w-5 h-5 text-gray-500 transform transition-transform" data-icon="{i}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                    </button>
                    <div class="hidden px-4 pb-4 text-gray-600" data-content="{i}">
                        {content_html}
                    </div>
                </div>
            '''
        
        return PyxElement("div").cls(f"border-t rounded-lg {className}").attr("id", acc_id).content(f'''
            {items_html}
            <script>
                function toggleAccordion(id, index, multiple) {{
                    const container = document.getElementById(id);
                    const content = container.querySelector('[data-content="' + index + '"]');
                    const icon = container.querySelector('[data-icon="' + index + '"]');
                    const isOpen = !content.classList.contains('hidden');
                    
                    if (!multiple) {{
                        container.querySelectorAll('[data-content]').forEach(c => c.classList.add('hidden'));
                        container.querySelectorAll('[data-icon]').forEach(i => i.classList.remove('rotate-180'));
                    }}
                    
                    if (isOpen) {{
                        content.classList.add('hidden');
                        icon.classList.remove('rotate-180');
                    }} else {{
                        content.classList.remove('hidden');
                        icon.classList.add('rotate-180');
                    }}
                }}
            </script>
        ''')
    
    @staticmethod
    def modal(trigger, title=None, content=None, footer=None, size="md", className=""):
        """
        Zen Mode Modal dialog.
        
        Usage:
            ui.modal(
                trigger=ui.button("Open Modal"),
                title="Confirm Action",
                content=ui.p("Are you sure you want to proceed?"),
                footer=ui.hstack(
                    ui.button("Cancel").on_click("closeModal()"),
                    ui.button("Confirm").style(bg="blue-600", color="white"),
                )
            )
        """
        import uuid
        modal_id = f"modal-{uuid.uuid4().hex[:8]}"
        
        trigger_html = trigger.render() if hasattr(trigger, 'render') else str(trigger)
        title_html = title or ""
        content_html = content.render() if hasattr(content, 'render') else str(content) if content else ""
        footer_html = footer.render() if hasattr(footer, 'render') else str(footer) if footer else ""
        
        sizes = {
            "sm": "max-w-sm",
            "md": "max-w-md",
            "lg": "max-w-lg",
            "xl": "max-w-xl",
            "full": "max-w-4xl",
        }
        size_class = sizes.get(size, "max-w-md")
        
        return PyxElement("div").cls(className).content(f'''
            <div onclick="document.getElementById('{modal_id}').classList.remove('hidden')">{trigger_html}</div>
            
            <div id="{modal_id}" class="hidden fixed inset-0 z-50 overflow-y-auto">
                <div class="flex items-center justify-center min-h-screen px-4">
                    <div class="fixed inset-0 bg-black/50" onclick="document.getElementById('{modal_id}').classList.add('hidden')"></div>
                    <div class="relative bg-white rounded-xl shadow-xl {size_class} w-full">
                        <div class="flex items-center justify-between p-4 border-b">
                            <h3 class="text-lg font-semibold">{title_html}</h3>
                            <button onclick="document.getElementById('{modal_id}').classList.add('hidden')" 
                                    class="p-2 text-gray-400 hover:text-gray-600 rounded-lg">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                </svg>
                            </button>
                        </div>
                        <div class="p-4">{content_html}</div>
                        <div class="flex justify-end gap-2 p-4 border-t">{footer_html}</div>
                    </div>
                </div>
            </div>
        ''')
    
    @staticmethod
    def section(title=None, subtitle=None, children=None, className=""):
        """
        Zen Mode Section wrapper.
        
        Usage:
            ui.section(
                title="Features",
                subtitle="What makes us different",
                children=ui.grid(...)
            )
        """
        title_html = f'<h2 class="text-3xl font-bold text-gray-900 mb-4">{title}</h2>' if title else ""
        subtitle_html = f'<p class="text-lg text-gray-600 mb-8">{subtitle}</p>' if subtitle else ""
        children_html = ""
        if children:
            children_html = children.render() if hasattr(children, 'render') else str(children)
        
        return PyxElement("section").cls(f"py-16 {className}").content(f'''
            <div class="container mx-auto px-4">
                <div class="text-center mb-12">
                    {title_html}
                    {subtitle_html}
                </div>
                {children_html}
            </div>
        ''')

    # =========================================================================
    # NAVIGATION (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def navbar(
        brand=None,
        items=None,
        actions=None,
        sticky=True,
        transparent=False,
        className=""
    ):
        """
        Zen Mode Navbar with responsive support.
        
        Usage:
            ui.navbar(
                brand=ui.span("MyApp").style(font="bold", text="xl"),
                items=[
                    {"label": "Home", "href": "/"},
                    {"label": "Products", "items": [  # Dropdown!
                        {"label": "All Products", "href": "/products"},
                        {"label": "Categories", "href": "/categories"},
                    ]},
                    {"label": "About", "href": "/about"},
                    {"label": "Contact", "href": "/contact"},
                ],
                actions=ui.button("Sign In").style(bg="blue-600", color="white", px=4, py=2, rounded="lg")
            )
        """
        items = items or []
        
        # Build nav items
        nav_items_html = ""
        mobile_items_html = ""
        
        for item in items:
            if "items" in item:
                # Dropdown menu
                dropdown_items = ""
                for sub in item["items"]:
                    if sub.get("type") == "divider":
                        dropdown_items += '<div class="border-t my-1"></div>'
                    else:
                        dropdown_items += f'''
                            <a href="{sub.get('href', '#')}" 
                               class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                {sub.get('label', '')}
                            </a>
                        '''
                
                nav_items_html += f'''
                    <div class="relative group">
                        <button class="flex items-center gap-1 px-3 py-2 text-gray-700 hover:text-gray-900">
                            {item.get('label', '')}
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                        </button>
                        <div class="absolute left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border opacity-0 invisible 
                                    group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                            {dropdown_items}
                        </div>
                    </div>
                '''
                
                # Mobile version
                mobile_items_html += f'''
                    <div class="border-b pb-2 mb-2">
                        <p class="px-4 py-2 font-medium text-gray-900">{item.get('label', '')}</p>
                        {dropdown_items}
                    </div>
                '''
            else:
                # Regular link
                nav_items_html += f'''
                    <a href="{item.get('href', '#')}" 
                       class="px-3 py-2 text-gray-700 hover:text-gray-900 font-medium">
                        {item.get('label', '')}
                    </a>
                '''
                mobile_items_html += f'''
                    <a href="{item.get('href', '#')}" 
                       class="block px-4 py-3 text-gray-700 hover:bg-gray-50">
                        {item.get('label', '')}
                    </a>
                '''
        
        # Brand
        brand_html = ""
        if brand:
            brand_html = brand.render() if hasattr(brand, 'render') else str(brand)
        
        # Actions
        actions_html = ""
        if actions:
            actions_html = actions.render() if hasattr(actions, 'render') else str(actions)
        
        # Sticky/transparent classes
        nav_classes = "w-full z-50"
        if sticky:
            nav_classes += " sticky top-0"
        if transparent:
            nav_classes += " bg-transparent"
        else:
            nav_classes += " bg-white border-b"
        
        import uuid
        nav_id = f"nav-{uuid.uuid4().hex[:8]}"
        
        return PyxElement("div").cls(className).content(f'''
            <nav class="{nav_classes}">
                <div class="container mx-auto px-4">
                    <div class="flex items-center justify-between h-16">
                        <!-- Brand -->
                        <div class="flex-shrink-0">
                            {brand_html}
                        </div>
                        
                        <!-- Desktop Nav -->
                        <div class="hidden md:flex items-center space-x-1">
                            {nav_items_html}
                        </div>
                        
                        <!-- Actions -->
                        <div class="hidden md:flex items-center space-x-4">
                            {actions_html}
                        </div>
                        
                        <!-- Mobile menu button -->
                        <button onclick="document.getElementById('{nav_id}').classList.toggle('hidden')"
                                class="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <!-- Mobile menu -->
                <div id="{nav_id}" class="hidden md:hidden bg-white border-t">
                    <div class="py-2">
                        {mobile_items_html}
                    </div>
                    <div class="px-4 py-3 border-t">
                        {actions_html}
                    </div>
                </div>
            </nav>
        ''')
    
    @staticmethod
    def nav_link(label, href="#", active=False, **kwargs):
        """
        Zen Mode Navigation Link.
        
        Usage:
            ui.nav_link("Home", href="/", active=True)
        """
        active_class = "text-blue-600 font-semibold" if active else "text-gray-700 hover:text-gray-900"
        return PyxElement("a", label).attr("href", href).cls(f"px-3 py-2 {active_class}")
    
    @staticmethod
    def nav_dropdown(label, items, **kwargs):
        """
        Zen Mode Navigation Dropdown.
        
        Usage:
            ui.nav_dropdown("Products", [
                {"label": "All Products", "href": "/products"},
                {"type": "divider"},
                {"label": "Categories", "href": "/categories"},
            ])
        """
        dropdown_id = f"dropdown-{id(label)}"
        
        items_html = ""
        for item in items:
            if item.get("type") == "divider":
                items_html += '<div class="border-t my-1"></div>'
            else:
                items_html += f'''
                    <a href="{item.get('href', '#')}" 
                       class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        {item.get('label', '')}
                    </a>
                '''
        
        return PyxElement("div").cls("relative group").content(f'''
            <button class="flex items-center gap-1 px-3 py-2 text-gray-700 hover:text-gray-900">
                {label}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
            </button>
            <div class="absolute left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border opacity-0 invisible 
                        group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                {items_html}
            </div>
        ''')

    # =========================================================================
    # LAYOUT UTILITIES (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def container(*children, size="lg", **kwargs):
        """
        Zen Mode Container.
        
        Usage:
            ui.container(ui.h1("Title"), ui.p("Content"), size="md")
        """
        from ..web.layout import Container
        return Container(*children, size=size, **kwargs)
    
    @staticmethod
    def stack(*children, gap="md", **kwargs):
        """
        Zen Mode Vertical Stack.
        
        Usage:
            ui.stack(ui.h1("Title"), ui.p("Text"), gap="lg")
        """
        from ..web.layout import Stack
        return Stack(*children, gap=gap, **kwargs)
    
    @staticmethod
    def hstack(*children, gap="md", **kwargs):
        """
        Zen Mode Horizontal Stack.
        
        Usage:
            ui.hstack(ui.button("A"), ui.button("B"), gap="sm")
        """
        from ..web.layout import HStack
        return HStack(*children, gap=gap, **kwargs)
    
    @staticmethod
    def center(child, **kwargs):
        """
        Zen Mode Center.
        
        Usage:
            ui.center(ui.spinner(), height="400px")
        """
        from ..web.layout import Center
        return Center(child, **kwargs)
    
    @staticmethod
    def spacer():
        """
        Zen Mode Spacer (fills available space).
        
        Usage:
            ui.hstack(ui.span("Left"), ui.spacer(), ui.span("Right"))
        """
        from ..web.layout import Spacer
        return Spacer()
    
    @staticmethod
    def divider(vertical=False, label=None, **kwargs):
        """
        Zen Mode Divider.
        
        Usage:
            ui.divider()
            ui.divider(label="OR")
        """
        from ..web.layout import Divider
        return Divider(vertical=vertical, label=label, **kwargs)
    
    @staticmethod
    def card(*children, **kwargs):
        """
        Zen Mode Card.
        
        Usage:
            ui.card(ui.h3("Title"), ui.p("Content"), shadow="md")
        """
        from ..web.layout import Card
        return Card(*children, **kwargs)

    # =========================================================================
    # ANIMATION UTILITIES (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def animate(child, animation="fadeIn", **kwargs):
        """
        Zen Mode Animation Wrapper.
        
        Usage:
            ui.animate(ui.div("Hello"), animation="slideUp")
            ui.animate(ui.card(...), animation="fadeIn", delay="0.2s")
        """
        from ..web.animation import Animate
        return Animate(child, animation=animation, **kwargs)
    
    @staticmethod
    def spinner(size="md", color="blue", **kwargs):
        """
        Zen Mode Loading Spinner.
        
        Usage:
            ui.spinner()
            ui.spinner(size="lg", color="green")
        """
        from ..web.animation import Spinner
        return Spinner(size=size, color=color, **kwargs)
    
    @staticmethod
    def dark_mode_toggle():
        """
        Zen Mode Dark Mode Toggle Button.
        
        Usage:
            ui.dark_mode_toggle()
        """
        from ..web.theme import DarkModeToggle
        return DarkModeToggle()

    # =========================================================================
    # FORM COMPONENTS (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def field(input_element, label=None, error=None, helper=None, **kwargs):
        """
        Zen Mode Form Field with label and validation.
        
        Usage:
            ui.field(ui.input(), label="Email", error="Invalid email")
        """
        from ..web.components.forms import FormField
        return FormField(input_element, label=label, error=error, helper=helper, **kwargs)
    
    @staticmethod
    def search(placeholder="Search...", suggestions=None, **kwargs):
        """
        Zen Mode Search Input with autocomplete.
        
        Usage:
            ui.search("Search products...", suggestions=["Apple", "Banana"])
        """
        from ..web.components.forms import SearchInput
        return SearchInput(placeholder=placeholder, suggestions=suggestions, **kwargs)
    
    @staticmethod
    def rating(value=0, max=5, **kwargs):
        """
        Zen Mode Star Rating.
        
        Usage:
            ui.rating(value=4, max=5)
        """
        from ..web.components.forms import Rating
        return Rating(value=value, max=max, **kwargs)
    
    @staticmethod
    def copy(text, **kwargs):
        """
        Zen Mode Copy Button.
        
        Usage:
            ui.copy("secret-api-key")
        """
        from ..web.components.forms import CopyButton
        return CopyButton(text=text, **kwargs)
    
    @staticmethod
    def toggle(value=False, label=None, **kwargs):
        """
        Zen Mode Toggle/Switch.
        
        Usage:
            ui.toggle(value=True, label="Enable notifications")
        """
        from ..web.components.forms import Toggle
        return Toggle(value=value, label=label, **kwargs)
    
    @staticmethod
    def table(headers, rows, **kwargs):
        """
        Zen Mode Simple Table.
        
        Usage:
            ui.table(["Name", "Email"], [["John", "john@mail.com"]])
        """
        from ..web.components.forms import Table
        return Table(headers=headers, rows=rows, **kwargs)

    # =========================================================================
    # TOAST/NOTIFICATION (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def toast_container(position="top-right"):
        """
        Zen Mode Toast Container. Include once in layout.
        
        Usage:
            ui.toast_container("top-right")
        """
        from ..web.components.toast import ToastContainer
        return ToastContainer(position=position)
    
    @staticmethod
    def notification(message, variant="info", **kwargs):
        """
        Zen Mode Inline Notification.
        
        Usage:
            ui.notification("Trial expires in 3 days", variant="warning")
        """
        from ..web.components.toast import Notification
        return Notification(message=message, variant=variant, **kwargs)

    # =========================================================================
    # DEVELOPER TOOLS (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def icon_browser(**kwargs):
        """
        Zen Mode Icon Browser.
        
        Usage:
            ui.icon_browser()
        """
        from ..web.devtools import IconBrowser
        return IconBrowser(**kwargs)
    
    @staticmethod
    def responsive_preview(content, device="iphone-14", **kwargs):
        """
        Zen Mode Responsive Preview.
        
        Usage:
            ui.responsive_preview(my_page, device="ipad")
        """
        from ..web.devtools import ResponsivePreview
        return ResponsivePreview(content=content, device=device, **kwargs)
    
    @staticmethod
    def dev_toolbar():
        """
        Zen Mode Developer Toolbar. Shows viewport size, breakpoints, etc.
        
        Usage:
            ui.dev_toolbar()  # Include in dev mode only
        """
        from ..web.devtools import DevToolbar
        return DevToolbar()
    
    @staticmethod
    def icon_search(query: str):
        """
        Search Lucide icons by name.
        
        Usage:
            icons = ui.icon_search("arrow")  # Returns list of matching icons
        """
        from ..web.devtools import IconBrowser
        return IconBrowser.search(query)

    # =========================================================================
    # FORM VALIDATION (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def validated_input(type="text", placeholder="", rules=None, **kwargs):
        """
        Zen Mode Validated Input.
        
        Usage:
            from pyx import Validators as v
            ui.validated_input("email", rules=[v.required(), v.email()])
        """
        from ..web.validation import ValidatedInput
        return ValidatedInput(type=type, placeholder=placeholder, rules=rules, **kwargs)
    
    @staticmethod
    def validated_form(content, on_submit=None, **kwargs):
        """
        Zen Mode Validated Form.
        
        Usage:
            ui.validated_form(
                ui.stack(
                    ui.validated_input(label="Email", rules=[...]),
                    ui.button("Submit")
                ),
                on_submit=handle_submit
            )
        """
        from ..web.validation import ValidatedForm
        return ValidatedForm(content=content, on_submit=on_submit, **kwargs)

    # =========================================================================
    # ACCESSIBILITY (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def skip_link(target="#main"):
        """
        Zen Mode Skip Link for keyboard users.
        
        Usage:
            ui.skip_link("#main-content")
        """
        from ..web.a11y import SkipLink
        return SkipLink(target=target)
    
    @staticmethod  
    def hidden_text(text):
        """
        Zen Mode Visually Hidden Text (for screen readers).
        
        Usage:
            ui.hidden_text("Opens in new window")
        """
        from ..web.a11y import VisuallyHidden
        return VisuallyHidden(text=text)
    
    @staticmethod
    def focus_trap(content, **kwargs):
        """
        Zen Mode Focus Trap (for modals).
        
        Usage:
            ui.focus_trap(modal_content)
        """
        from ..web.a11y import FocusTrap
        return FocusTrap(content=content, **kwargs)
    
    @staticmethod
    def live_region(id="live", mode="polite"):
        """
        Zen Mode Live Region for announcements.
        
        Usage:
            ui.live_region()  # Then use PyxA11y.announce("Message")
        """
        from ..web.a11y import LiveRegion
        return LiveRegion(id=id, mode=mode)
    
    @staticmethod
    def a11y_styles():
        """
        Include accessibility CSS utilities.
        
        Usage:
            ui.a11y_styles()
        """
        from ..web.a11y import A11yStyles
        return A11yStyles()

    # =========================================================================
    # SUSPENSE & LOADING (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def suspense(content, loading=None, error=None, **kwargs):
        """
        Zen Mode Suspense wrapper for async content.
        
        Usage:
            ui.suspense(
                AsyncComponent(),
                loading=ui.skeleton(),
                error=ui.alert("Error loading", variant="error")
            )
        """
        from ..web.suspense import Suspense
        return Suspense(content=content, loading=loading, error=error, **kwargs)
    
    @staticmethod
    def error_boundary(content, fallback=None, **kwargs):
        """
        Zen Mode Error Boundary for graceful error handling.
        
        Usage:
            ui.error_boundary(RiskyComponent(), fallback=ErrorMessage())
        """
        from ..web.suspense import ErrorBoundary
        return ErrorBoundary(content=content, fallback=fallback, **kwargs)
    
    @staticmethod
    def loading(variant="spinner", size="md", **kwargs):
        """
        Zen Mode Loading indicator.
        
        Usage:
            ui.loading()
            ui.loading(variant="skeleton", lines=3)
            ui.loading(variant="dots")
        """
        from ..web.suspense import Loading
        return Loading(variant=variant, size=size, **kwargs)
    
    @staticmethod
    def skeleton(lines=3, **kwargs):
        """
        Zen Mode Skeleton loader.
        
        Usage:
            ui.skeleton()
            ui.skeleton(lines=5)
        """
        from ..web.suspense import Loading
        return Loading(variant="skeleton", lines=lines, **kwargs)

    # =========================================================================
    # PYTHONIC STYLES (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def styled(tag="div", content=None, **style_kwargs):
        """
        Create a styled element with Pythonic style kwargs.
        
        Usage:
            ui.styled("div", "Hello", text="lg", color="blue-600", p=4)
        """
        from .styles import Style
        el = PyxElement(tag, content)
        return el.style(**style_kwargs)
    
    @staticmethod
    def preset(name: str):
        """
        Get a preset style by name.
        
        Usage:
            ui.div("Card").apply(ui.preset("card"))
        """
        from .styles import presets
        return getattr(presets, name, None)

    # =========================================================================
    # RESPONSIVE (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def show_on(device: str, content):
        """
        Show content only on specific device.
        
        Usage:
            ui.show_on("mobile", MobileNav())
            ui.show_on("desktop", DesktopSidebar())
        """
        from ..web.responsive import Show
        if device == "mobile":
            return Show.on_mobile(content)
        elif device == "tablet":
            return Show.on_tablet(content)
        elif device == "desktop":
            return Show.on_desktop(content)
        return content
    
    @staticmethod
    def hide_on(device: str, content):
        """
        Hide content on specific device.
        
        Usage:
            ui.hide_on("mobile", DesktopTable())
        """
        from ..web.responsive import Hide
        if device == "mobile":
            return Hide.on_mobile(content)
        elif device == "desktop":
            return Hide.on_desktop(content)
        return content
    
    @staticmethod
    def responsive_grid(cols=1, sm=None, md=None, lg=None, xl=None, gap=4):
        """
        Get responsive grid classes.
        
        Usage:
            ui.div(*cards).cls(ui.responsive_grid(1, md=2, lg=4))
        """
        from ..web.responsive import responsive
        return responsive.grid(cols, sm=sm, md=md, lg=lg, xl=xl, gap=gap)

    # =========================================================================
    # I18N / TRANSLATION (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def t(key: str, **kwargs):
        """
        Translate a key (i18n).
        
        Usage:
            ui.h1(ui.t("welcome"))
            ui.p(ui.t("greeting", name="John"))
        """
        from ..lib.i18n import t as translate
        return translate(key, **kwargs)
    
    @staticmethod
    def lang_switcher(className=""):
        """
        Language switcher component.
        
        Usage:
            ui.lang_switcher()
        """
        from ..lib.i18n import i18n
        return i18n.language_switcher(className)

    # =========================================================================
    # SEO (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def head(title=None, description=None, og_image=None, **kwargs):
        """
        SEO Head component.
        
        Usage:
            ui.head(
                title="My Page",
                description="Page description",
                og_image="/og.jpg"
            )
        """
        from ..lib.seo import Head
        return Head(title=title, description=description, og_image=og_image, **kwargs)
    
    @staticmethod
    def json_ld(type: str, **kwargs):
        """
        Generate JSON-LD structured data.
        
        Usage:
            ui.json_ld("article", headline="My Post", author_name="John", ...)
            ui.json_ld("product", name="Widget", price="99", ...)
        """
        from ..lib.seo import JSONLD
        if type == "article":
            return JSONLD.article(**kwargs)
        elif type == "product":
            return JSONLD.product(**kwargs)
        elif type == "breadcrumb":
            return JSONLD.breadcrumb(**kwargs)
        elif type == "faq":
            return JSONLD.faq(**kwargs)
        elif type == "organization":
            return JSONLD.organization(**kwargs)
        return {}

    # =========================================================================
    # PWA (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def pwa_meta(name: str, theme_color: str = "#3B82F6", **kwargs):
        """
        PWA meta tags for head.
        
        Usage:
            ui.pwa_meta("My App", theme_color="#3B82F6")
        """
        from ..lib.pwa import PWA, PWAConfig
        config = PWAConfig(name=name, theme_color=theme_color, **kwargs)
        return PWA(config).head_tags()
    
    @staticmethod
    def install_prompt(button_text: str = "Install App"):
        """
        PWA install prompt component.
        
        Usage:
            ui.install_prompt()
        """
        from ..lib.pwa import PWA, PWAConfig
        return PWA(PWAConfig(name="App")).install_prompt(button_text)

    # =========================================================================
    # VIEWPORT & BASE STYLES (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def viewport_meta():
        """
        Essential viewport meta tag.
        
        Usage:
            ui.viewport_meta()
        """
        from ..web.responsive import ResponsiveStyles
        return ResponsiveStyles.viewport_meta()
    
    @staticmethod
    def base_styles():
        """
        Base responsive CSS styles.
        
        Usage:
            ui.base_styles()
        """
        from ..web.responsive import ResponsiveStyles
        return ResponsiveStyles.base_styles()

    # =========================================================================
    # FILE UPLOAD (Zen Mode)
    # =========================================================================
    
    @staticmethod
    def file_upload(
        name: str = "file",
        accept: str = "*/*",
        multiple: bool = False,
        max_size: str = "10MB",
        upload_url: str = "/api/upload",
        preview: bool = True,
        drag_drop: bool = True,
        on_upload: str = None,
        className: str = ""
    ):
        """
        Zen Mode File Upload component.
        
        Usage:
            ui.file_upload()
            ui.file_upload(accept="image/*", max_size="5MB")
            ui.file_upload(multiple=True, drag_drop=True)
        """
        import uuid
        input_id = f"upload-{uuid.uuid4().hex[:8]}"
        
        # Parse max size
        size_map = {"KB": 1024, "MB": 1024*1024, "GB": 1024*1024*1024}
        max_bytes = 10 * 1024 * 1024  # default 10MB
        for unit, multiplier in size_map.items():
            if unit in max_size.upper():
                max_bytes = int(max_size.upper().replace(unit, "").strip()) * multiplier
                break
        
        callback = on_upload or f"console.log('Uploaded:', result)"
        
        if drag_drop:
            return PyxElement("div").cls(f"pyx-file-upload {className}").content(f'''
                <div class="relative">
                    <input type="file" id="{input_id}" name="{name}" 
                           accept="{accept}" {"multiple" if multiple else ""}
                           class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                           onchange="handleFileSelect_{input_id}(this)">
                    
                    <div id="{input_id}-dropzone" 
                         class="flex flex-col items-center justify-center w-full h-32 
                                border-2 border-dashed border-gray-300 rounded-lg 
                                hover:border-blue-500 hover:bg-blue-50/50 transition-all duration-200">
                        <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                        </svg>
                        <span class="mt-2 text-sm text-gray-500">Drop files here or click to upload</span>
                        <span class="text-xs text-gray-400">Max: {max_size}</span>
                    </div>
                    
                    <!-- Preview -->
                    <div id="{input_id}-preview" class="hidden mt-3 space-y-2"></div>
                    
                    <!-- Progress -->
                    <div id="{input_id}-progress" class="hidden mt-3">
                        <div class="flex items-center gap-3">
                            <div class="flex-1 bg-gray-200 rounded-full h-2">
                                <div id="{input_id}-bar" class="bg-blue-600 h-2 rounded-full transition-all" style="width: 0%"></div>
                            </div>
                            <span id="{input_id}-percent" class="text-sm text-gray-600">0%</span>
                        </div>
                    </div>
                </div>
                
                <script>
                function handleFileSelect_{input_id}(input) {{
                    const files = input.files;
                    const preview = document.getElementById('{input_id}-preview');
                    const progress = document.getElementById('{input_id}-progress');
                    
                    if (!files.length) return;
                    
                    // Show preview
                    preview.innerHTML = '';
                    preview.classList.remove('hidden');
                    
                    Array.from(files).forEach((file, i) => {{
                        // Validate size
                        if (file.size > {max_bytes}) {{
                            alert('File too large: ' + file.name + '. Max: {max_size}');
                            return;
                        }}
                        
                        const item = document.createElement('div');
                        item.className = 'flex items-center gap-3 p-2 bg-gray-50 rounded-lg';
                        
                        // Image preview
                        if (file.type.startsWith('image/')) {{
                            const img = document.createElement('img');
                            img.src = URL.createObjectURL(file);
                            img.className = 'w-10 h-10 object-cover rounded';
                            item.appendChild(img);
                        }} else {{
                            const icon = document.createElement('div');
                            icon.className = 'w-10 h-10 bg-gray-200 rounded flex items-center justify-center';
                            icon.innerHTML = '<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>';
                            item.appendChild(icon);
                        }}
                        
                        const info = document.createElement('div');
                        info.className = 'flex-1';
                        info.innerHTML = '<p class="text-sm font-medium text-gray-700">' + file.name + '</p>' +
                                        '<p class="text-xs text-gray-500">' + (file.size / 1024).toFixed(1) + ' KB</p>';
                        item.appendChild(info);
                        
                        const removeBtn = document.createElement('button');
                        removeBtn.className = 'p-1 text-gray-400 hover:text-red-500';
                        removeBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';
                        removeBtn.onclick = () => {{ item.remove(); }};
                        item.appendChild(removeBtn);
                        
                        preview.appendChild(item);
                    }});
                    
                    // Auto upload
                    uploadFiles_{input_id}(files);
                }}
                
                async function uploadFiles_{input_id}(files) {{
                    const progress = document.getElementById('{input_id}-progress');
                    const bar = document.getElementById('{input_id}-bar');
                    const percent = document.getElementById('{input_id}-percent');
                    
                    progress.classList.remove('hidden');
                    
                    const formData = new FormData();
                    Array.from(files).forEach(f => formData.append('file', f));
                    
                    const xhr = new XMLHttpRequest();
                    
                    xhr.upload.onprogress = (e) => {{
                        if (e.lengthComputable) {{
                            const p = Math.round((e.loaded / e.total) * 100);
                            bar.style.width = p + '%';
                            percent.textContent = p + '%';
                        }}
                    }};
                    
                    xhr.onload = () => {{
                        if (xhr.status >= 200 && xhr.status < 300) {{
                            const result = JSON.parse(xhr.responseText);
                            bar.style.width = '100%';
                            bar.classList.remove('bg-blue-600');
                            bar.classList.add('bg-green-500');
                            percent.textContent = 'Done!';
                            {callback};
                        }} else {{
                            bar.classList.remove('bg-blue-600');
                            bar.classList.add('bg-red-500');
                            percent.textContent = 'Error';
                        }}
                    }};
                    
                    xhr.onerror = () => {{
                        bar.classList.add('bg-red-500');
                        percent.textContent = 'Error';
                    }};
                    
                    xhr.open('POST', '{upload_url}');
                    xhr.send(formData);
                }}
                </script>
            ''')
        else:
            # Simple file input
            return PyxElement("input").attr("type", "file").attr("name", name).attr("accept", accept).attr("id", input_id).cls(className)

# Expose lowercase ui as alias for UI (Zen Style Preference)
ui = UI