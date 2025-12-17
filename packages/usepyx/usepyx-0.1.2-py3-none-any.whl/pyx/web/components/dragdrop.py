"""
PyX Drag & Drop Components
Interactive drag and drop functionality.
"""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import json


class Draggable:
    """
    Makes an element draggable.
    
    Usage:
        from pyx import Draggable
        
        Draggable(
            content=ui.div("Drag me!"),
            data={"id": 1, "name": "Item 1"},
            on_drag_start=handle_start,
            on_drag_end=handle_end,
        )
    """
    
    def __init__(
        self,
        content,  # PyxElement or string
        data: Dict[str, Any] = None,
        drag_handle: str = None,  # CSS selector for drag handle
        on_drag_start: Callable = None,
        on_drag_end: Callable = None,
        disabled: bool = False,
        className: str = "",
        draggable_id: str = None,
    ):
        self.content = content
        self.data = data or {}
        self.drag_handle = drag_handle
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
        self.disabled = disabled
        self.className = className
        self.draggable_id = draggable_id or f"draggable-{id(self)}"
        
    def render(self) -> str:
        content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        data_json = json.dumps(self.data)
        
        # Event handlers
        drag_start_handler = ""
        drag_end_handler = ""
        
        if self.on_drag_start:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_drag_start)
            drag_start_handler = f"PyX.sendEvent('{handler_name}');"
            
        if self.on_drag_end:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_drag_end)
            drag_end_handler = f"PyX.sendEvent('{handler_name}');"
        
        disabled_attr = "false" if not self.disabled else "true"
        
        return f"""
        <div 
            id="{self.draggable_id}"
            class="pyx-draggable {self.className}"
            draggable="{disabled_attr}"
            data-pyx-drag-data='{data_json}'
            ondragstart="
                event.dataTransfer.setData('application/json', this.getAttribute('data-pyx-drag-data'));
                event.dataTransfer.effectAllowed = 'move';
                this.classList.add('dragging');
                {drag_start_handler}
            "
            ondragend="
                this.classList.remove('dragging');
                {drag_end_handler}
            "
            style="cursor: grab;"
        >
            {content_html}
        </div>
        """
    
    def __str__(self):
        return self.render()


class DropZone:
    """
    Creates a drop zone that accepts draggable items.
    
    Usage:
        from pyx import DropZone
        
        DropZone(
            content=ui.div("Drop items here"),
            on_drop=handle_drop,
            accept=["task", "file"],  # Only accept specific types
        )
    """
    
    def __init__(
        self,
        content=None,  # PyxElement or string
        on_drop: Callable = None,
        on_drag_over: Callable = None,
        on_drag_enter: Callable = None,
        on_drag_leave: Callable = None,
        accept: List[str] = None,  # Filter by data.type
        className: str = "",
        active_class: str = "drag-over",
        zone_id: str = None,
    ):
        self.content = content
        self.on_drop = on_drop
        self.on_drag_over = on_drag_over
        self.on_drag_enter = on_drag_enter
        self.on_drag_leave = on_drag_leave
        self.accept = accept
        self.className = className
        self.active_class = active_class
        self.zone_id = zone_id or f"dropzone-{id(self)}"
        
    def render(self) -> str:
        content_html = ""
        if self.content:
            content_html = self.content.render() if hasattr(self.content, 'render') else str(self.content)
        
        # Build drop handler
        drop_handler = ""
        if self.on_drop:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_drop)
            drop_handler = f"""
                const data = JSON.parse(event.dataTransfer.getData('application/json'));
                window.ws.send(JSON.stringify({{
                    type: 'event',
                    handler: '{handler_name}',
                    data: data
                }}));
            """
        
        accept_check = ""
        if self.accept:
            accept_types = json.dumps(self.accept)
            accept_check = f"""
                const acceptTypes = {accept_types};
                if (data.type && !acceptTypes.includes(data.type)) {{
                    return;
                }}
            """
        
        return f"""
        <div 
            id="{self.zone_id}"
            class="pyx-dropzone {self.className}"
            ondragover="
                event.preventDefault();
                event.dataTransfer.dropEffect = 'move';
            "
            ondragenter="
                event.preventDefault();
                this.classList.add('{self.active_class}');
            "
            ondragleave="
                this.classList.remove('{self.active_class}');
            "
            ondrop="
                event.preventDefault();
                this.classList.remove('{self.active_class}');
                {drop_handler}
            "
        >
            {content_html}
        </div>
        """
    
    def __str__(self):
        return self.render()


class SortableList:
    """
    Creates a sortable/reorderable list.
    
    Usage:
        from pyx import SortableList
        
        items = [
            {"id": 1, "title": "Task 1"},
            {"id": 2, "title": "Task 2"},
            {"id": 3, "title": "Task 3"},
        ]
        
        SortableList(
            items=items,
            render_item=lambda item: ui.div(item["title"]),
            on_reorder=handle_reorder,
        )
    """
    
    # SortableJS CDN
    SORTABLE_JS = "https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
    
    def __init__(
        self,
        items: List[Dict[str, Any]],
        render_item: Callable[[Dict], Any],
        on_reorder: Callable = None,
        item_key: str = "id",
        direction: str = "vertical",  # 'vertical' or 'horizontal'
        handle: str = None,  # CSS selector for drag handle
        group: str = None,  # For drag between lists
        animation: int = 150,
        ghost_class: str = "sortable-ghost",
        chosen_class: str = "sortable-chosen",
        drag_class: str = "sortable-drag",
        className: str = "",
        list_id: str = None,
    ):
        self.items = items
        self.render_item = render_item
        self.on_reorder = on_reorder
        self.item_key = item_key
        self.direction = direction
        self.handle = handle
        self.group = group
        self.animation = animation
        self.ghost_class = ghost_class
        self.chosen_class = chosen_class
        self.drag_class = drag_class
        self.className = className
        self.list_id = list_id or f"sortable-{id(self)}"
        
    def render(self) -> str:
        # Render items
        items_html = ""
        for item in self.items:
            item_content = self.render_item(item)
            item_html = item_content.render() if hasattr(item_content, 'render') else str(item_content)
            item_id = item.get(self.item_key, id(item))
            items_html += f'<div class="sortable-item" data-id="{item_id}">{item_html}</div>'
        
        # Build reorder handler
        reorder_handler = ""
        if self.on_reorder:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_reorder)
            reorder_handler = f"""
                onEnd: function(evt) {{
                    const order = Array.from(evt.to.children).map(el => el.dataset.id);
                    window.ws.send(JSON.stringify({{
                        type: 'event',
                        handler: '{handler_name}',
                        data: {{
                            oldIndex: evt.oldIndex,
                            newIndex: evt.newIndex,
                            order: order
                        }}
                    }}));
                }},
            """
        
        # Options
        group_opt = f"group: '{self.group}'," if self.group else ""
        handle_opt = f"handle: '{self.handle}'," if self.handle else ""
        direction_class = "flex flex-row gap-2" if self.direction == "horizontal" else "flex flex-col gap-2"
        
        return f"""
        <script src="{self.SORTABLE_JS}"></script>
        
        <div id="{self.list_id}" class="pyx-sortable {direction_class} {self.className}">
            {items_html}
        </div>
        
        <script>
            (function() {{
                new Sortable(document.getElementById('{self.list_id}'), {{
                    animation: {self.animation},
                    ghostClass: '{self.ghost_class}',
                    chosenClass: '{self.chosen_class}',
                    dragClass: '{self.drag_class}',
                    {group_opt}
                    {handle_opt}
                    {reorder_handler}
                }});
            }})();
        </script>
        
        <style>
            .{self.ghost_class} {{
                opacity: 0.4;
                background: #c8ebfb;
            }}
            .{self.chosen_class} {{
                background: #f0f9ff;
            }}
            .sortable-item {{
                cursor: grab;
            }}
            .sortable-item:active {{
                cursor: grabbing;
            }}
        </style>
        """
    
    def __str__(self):
        return self.render()


class Kanban:
    """
    Pre-built Kanban board component.
    
    Usage:
        from pyx import Kanban
        
        columns = [
            {"id": "todo", "title": "To Do", "items": [...]},
            {"id": "doing", "title": "In Progress", "items": [...]},
            {"id": "done", "title": "Done", "items": [...]},
        ]
        
        Kanban(
            columns=columns,
            render_card=lambda item: ui.div(item["title"]),
            on_card_move=handle_move,
        )
    """
    
    SORTABLE_JS = "https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
    
    def __init__(
        self,
        columns: List[Dict[str, Any]],
        render_card: Callable[[Dict], Any],
        on_card_move: Callable = None,
        column_key: str = "id",
        card_key: str = "id",
        className: str = "",
        column_class: str = "",
        card_class: str = "",
        kanban_id: str = None,
    ):
        self.columns = columns
        self.render_card = render_card
        self.on_card_move = on_card_move
        self.column_key = column_key
        self.card_key = card_key
        self.className = className
        self.column_class = column_class
        self.card_class = card_class
        self.kanban_id = kanban_id or f"kanban-{id(self)}"
        
    def render(self) -> str:
        # Build cards handler
        move_handler_js = ""
        if self.on_card_move:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_card_move)
            move_handler_js = f"""
                onEnd: function(evt) {{
                    window.ws.send(JSON.stringify({{
                        type: 'event',
                        handler: '{handler_name}',
                        data: {{
                            cardId: evt.item.dataset.id,
                            fromColumn: evt.from.dataset.column,
                            toColumn: evt.to.dataset.column,
                            oldIndex: evt.oldIndex,
                            newIndex: evt.newIndex
                        }}
                    }}));
                }},
            """
        
        # Render columns
        columns_html = ""
        init_scripts = []
        
        for col in self.columns:
            col_id = col.get(self.column_key)
            col_title = col.get("title", col_id)
            items = col.get("items", [])
            
            # Render cards
            cards_html = ""
            for item in items:
                card_content = self.render_card(item)
                card_html = card_content.render() if hasattr(card_content, 'render') else str(card_content)
                card_id = item.get(self.card_key, id(item))
                cards_html += f'<div class="kanban-card {self.card_class}" data-id="{card_id}">{card_html}</div>'
            
            list_id = f"{self.kanban_id}-{col_id}"
            
            columns_html += f"""
            <div class="kanban-column {self.column_class}">
                <div class="kanban-column-header">{col_title}</div>
                <div id="{list_id}" class="kanban-cards" data-column="{col_id}">
                    {cards_html}
                </div>
            </div>
            """
            
            init_scripts.append(f"""
                new Sortable(document.getElementById('{list_id}'), {{
                    group: '{self.kanban_id}-group',
                    animation: 150,
                    ghostClass: 'kanban-ghost',
                    {move_handler_js}
                }});
            """)
        
        return f"""
        <script src="{self.SORTABLE_JS}"></script>
        
        <div id="{self.kanban_id}" class="kanban-board {self.className}">
            {columns_html}
        </div>
        
        <script>
            (function() {{
                {"".join(init_scripts)}
            }})();
        </script>
        
        <style>
            .kanban-board {{
                display: flex;
                gap: 16px;
                overflow-x: auto;
                padding: 16px;
            }}
            .kanban-column {{
                min-width: 280px;
                background: #f1f5f9;
                border-radius: 8px;
                padding: 12px;
            }}
            .kanban-column-header {{
                font-weight: 600;
                padding: 8px;
                margin-bottom: 8px;
                color: #334155;
            }}
            .kanban-cards {{
                min-height: 100px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .kanban-card {{
                background: white;
                border-radius: 6px;
                padding: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                cursor: grab;
            }}
            .kanban-card:active {{
                cursor: grabbing;
            }}
            .kanban-ghost {{
                opacity: 0.4;
                background: #dbeafe;
            }}
        </style>
        """
    
    def __str__(self):
        return self.render()
