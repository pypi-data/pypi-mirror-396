"""
PyX DataGrid Component
Enterprise-grade data table with AG Grid under the hood.
"""
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
import json


@dataclass
class Column:
    """
    Column definition for DataGrid.
    
    Args:
        field: The key in data dict (required)
        header: Display name (defaults to field name)
        sortable: Enable sorting
        filterable: Enable filtering
        editable: Enable inline editing
        width: Column width in pixels
        type: Data type hint ('text', 'number', 'date', 'boolean')
        render: Custom render function or format string
        pin: Pin column ('left' or 'right')
    """
    field: str
    header: str = None
    sortable: bool = True
    filterable: bool = True
    editable: bool = False
    width: int = None
    type: str = "text"
    render: str = None
    pin: str = None
    
    def __post_init__(self):
        if self.header is None:
            # Convert field_name to "Field Name"
            self.header = self.field.replace("_", " ").title()
    
    def to_ag_def(self) -> Dict:
        """Convert to AG Grid column definition"""
        col_def = {
            "field": self.field,
            "headerName": self.header,
            "sortable": self.sortable,
            "filter": self.filterable,
            "editable": self.editable,
        }
        
        if self.width:
            col_def["width"] = self.width
        
        if self.pin:
            col_def["pinned"] = self.pin
            
        # Type-specific settings
        if self.type == "number":
            col_def["filter"] = "agNumberColumnFilter" if self.filterable else False
            col_def["type"] = "numericColumn"
        elif self.type == "date":
            col_def["filter"] = "agDateColumnFilter" if self.filterable else False
        elif self.type == "boolean":
            col_def["cellRenderer"] = "agCheckboxCellRenderer"
            col_def["cellEditor"] = "agCheckboxCellEditor"
            
        if self.render:
            col_def["cellRenderer"] = self.render
            
        return col_def


class DataGrid:
    """
    Enterprise DataGrid Component.
    
    Usage:
        from pyx import DataGrid, Column
        
        # Simple usage (auto-generate columns)
        grid = DataGrid(data=users)
        
        # With custom columns
        grid = DataGrid(
            data=products,
            columns=[
                Column("id", width=80),
                Column("name", header="Product Name"),
                Column("price", type="number", editable=True),
                Column("active", type="boolean"),
            ],
            pagination=True,
            page_size=20,
            row_selection="multiple",
            on_row_click=handle_click,
        )
    """
    
    # CDN URLs for AG Grid
    AG_GRID_CSS = "https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.1/styles/ag-grid.css"
    AG_GRID_THEME = "https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.1/styles/ag-theme-alpine.css"
    AG_GRID_JS = "https://cdn.jsdelivr.net/npm/ag-grid-community@31.0.1/dist/ag-grid-community.min.js"
    
    def __init__(
        self,
        data: List[Dict[str, Any]] = None,
        columns: List[Column] = None,
        # Pagination
        pagination: bool = True,
        page_size: int = 10,
        # Selection
        row_selection: str = None,  # 'single' or 'multiple'
        # Sizing
        height: str = "400px",
        width: str = "100%",
        # Features
        sortable: bool = True,
        filterable: bool = True,
        resizable: bool = True,
        # Events
        on_row_click: Callable = None,
        on_cell_edit: Callable = None,
        on_selection_change: Callable = None,
        # Styling
        theme: str = "alpine",  # 'alpine', 'alpine-dark', 'balham', 'material'
        className: str = "",
        # ID
        grid_id: str = None,
    ):
        self.data = data or []
        self.columns = columns
        self.pagination = pagination
        self.page_size = page_size
        self.row_selection = row_selection
        self.height = height
        self.width = width
        self.sortable = sortable
        self.filterable = filterable
        self.resizable = resizable
        self.on_row_click = on_row_click
        self.on_cell_edit = on_cell_edit
        self.on_selection_change = on_selection_change
        self.theme = theme
        self.className = className
        self.grid_id = grid_id or f"pyx-grid-{id(self)}"
        
    def _auto_columns(self) -> List[Dict]:
        """Auto-generate columns from data"""
        if not self.data:
            return []
        
        first_row = self.data[0]
        columns = []
        
        for key, value in first_row.items():
            col_type = "text"
            if isinstance(value, (int, float)):
                col_type = "number"
            elif isinstance(value, bool):
                col_type = "boolean"
            
            col = Column(field=key, type=col_type, sortable=self.sortable, filterable=self.filterable)
            columns.append(col.to_ag_def())
        
        return columns
    
    def _build_column_defs(self) -> List[Dict]:
        """Build AG Grid column definitions"""
        if self.columns:
            return [col.to_ag_def() for col in self.columns]
        return self._auto_columns()
    
    def _build_grid_options(self) -> Dict:
        """Build AG Grid options object"""
        options = {
            "columnDefs": self._build_column_defs(),
            "rowData": self.data,
            "pagination": self.pagination,
            "paginationPageSize": self.page_size,
            "defaultColDef": {
                "resizable": self.resizable,
                "sortable": self.sortable,
                "filter": self.filterable,
            },
            "animateRows": True,
            "suppressCellFocus": False,
        }
        
        if self.row_selection:
            options["rowSelection"] = self.row_selection
            options["suppressRowClickSelection"] = False
        
        return options
    
    def render(self) -> str:
        """Render the DataGrid as HTML"""
        grid_options = json.dumps(self._build_grid_options())
        theme_class = f"ag-theme-{self.theme}"
        
        # Event handlers
        event_handlers = ""
        
        if self.on_row_click:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_row_click)
            event_handlers += f"""
                gridOptions.onRowClicked = function(event) {{
                    PyX.sendEvent('{handler_name}', null);
                }};
            """
        
        if self.on_cell_edit:
            from ..core.events import EventManager
            handler_name = EventManager.register(self.on_cell_edit)
            event_handlers += f"""
                gridOptions.onCellValueChanged = function(event) {{
                    const data = {{ 
                        field: event.colDef.field, 
                        oldValue: event.oldValue, 
                        newValue: event.newValue,
                        rowData: event.data
                    }};
                    window.ws.send(JSON.stringify({{
                        type: 'event',
                        handler: '{handler_name}',
                        data: data
                    }}));
                }};
            """
        
        html = f"""
        <link rel="stylesheet" href="{self.AG_GRID_CSS}">
        <link rel="stylesheet" href="{self.AG_GRID_THEME}">
        <script src="{self.AG_GRID_JS}"></script>
        
        <div id="{self.grid_id}" class="{theme_class} {self.className}" 
             style="height: {self.height}; width: {self.width};"></div>
        
        <script>
            (function() {{
                const gridOptions = {grid_options};
                {event_handlers}
                
                const gridDiv = document.getElementById('{self.grid_id}');
                new agGrid.Grid(gridDiv, gridOptions);
                
                // Store reference for later access
                window.pyxGrids = window.pyxGrids || {{}};
                window.pyxGrids['{self.grid_id}'] = gridOptions;
            }})();
        </script>
        """
        
        return html
    
    def __str__(self):
        return self.render()


class DataGridElement:
    """
    PyxElement-compatible wrapper for DataGrid.
    Allows chaining like other PyX elements.
    """
    def __init__(self, grid: DataGrid):
        self._grid = grid
        self.tag = "div"
        self.children = []
        self.classes = []
        self.attrs = {}
        
    def render(self) -> str:
        return self._grid.render()
    
    def height(self, h: str):
        self._grid.height = h
        return self
    
    def theme(self, t: str):
        self._grid.theme = t
        return self
        
    def cls(self, *classes):
        self._grid.className += " " + " ".join(classes)
        return self


def datagrid(
    data: List[Dict[str, Any]],
    columns: List[Column] = None,
    **kwargs
) -> DataGridElement:
    """
    Zen Mode helper for creating DataGrid.
    
    Usage:
        from pyx import datagrid
        
        grid = datagrid(users).height("500px").theme("alpine-dark")
    """
    grid = DataGrid(data=data, columns=columns, **kwargs)
    return DataGridElement(grid)
