from pyx.components import PyxUI
from pyx.ui import UI
from pyx.client import JS
from pyx.database import db
from sqlmodel import select

class AdminView:
    def __init__(self, model):
        self.model = model
        self.model_name = model.__name__
        self.slug = self.model_name.lower() + "s" # e.g. users
        self.prefix = f"/admin/{self.slug}"

    def render_list(self):
        """Render the List View (Data Table)"""
        with db.get_session() as session:
            # TODO: Pagination & Search logic
            statement = select(self.model)
            results = session.exec(statement).all()
            
            # Auto-detect headers from model fields
            headers = [f for f in self.model.__fields__ if f != "id"]
            
            # Row Actions
            def actions(row):
                return UI.div([
                    PyxUI.Button("Edit", variant="ghost", size="sm", onClick=JS.navigate(f"{self.prefix}/{row.id}/edit")),
                    PyxUI.Button("Delete", variant="destructive", size="sm", className="ml-2", onClick=JS.server("delete_row", {"id": row.id, "model": self.model_name}))
                ])

            return UI.div([
                UI.div([
                    UI.h1(f"{self.model_name}s", className="text-3xl font-bold tracking-tight"),
                    PyxUI.Button("Add New", onClick=JS.navigate(f"{self.prefix}/create"))
                ], className="flex items-center justify-between mb-8"),
                
                PyxUI.Card([
                    PyxUI.CardContent([
                        PyxUI.Table(headers, results, actions=actions)
                    ], className="p-0")
                ])
            ], className="container mx-auto py-10")

    def render_form(self, id=None):
        """Render Create/Edit Form"""
        is_edit = id is not None
        title = f"Edit {self.model_name}" if is_edit else f"Create {self.model_name}"
        
        fields = []
        # Auto-generate fields
        for field_name, field_info in self.model.__fields__.items():
            if field_name == "id": continue
            
            fields.append(UI.div([
                UI.label(field_name.capitalize(), className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 mb-2 block"),
                PyxUI.Input(name=field_name, placeholder=f"Enter {field_name}")
            ], className="mb-4"))

        return UI.div([
            PyxUI.Card([
                PyxUI.CardHeader([
                    PyxUI.CardTitle(title)
                ]),
                PyxUI.CardContent([
                    UI.form(fields, id="admin-form", 
                           onSubmit=JS.server("save_model", {"model": self.model_name, "id": id})
                           if is_edit else JS.server("create_model", {"model": self.model_name}))
                ]),
                UI.div([
                    PyxUI.Button("Save", variant="default", onClick=JS.submit_form("admin-form")),
                    PyxUI.Button("Cancel", variant="ghost", onClick=JS.navigate(self.prefix), className="ml-2")
                ], className="p-6 pt-0 flex justify-end")
            ], className="max-w-2xl mx-auto mt-10")
        ])
