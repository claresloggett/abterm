
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, ListView, ListItem

class SprintsPanel(Widget):
    """A panel to display sprints as a selectable list."""

    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.styles.width = 20
        self.client = client
        self.list_view = ListView()
        self.sprints = []

    def compose(self) -> ComposeResult:
        yield self.list_view

    def on_mount(self):
        self.get_sprints()

    def get_sprints(self):
        """Fetch sprints from Azure DevOps and update the list view."""
        self.sprints = self.client.get_sprints()[::-1]
        self.update_list_view()
    
    def get_sprint_by_offset(self, sprint_path, offset=1):
        """Get the sprint N after/before the given sprint ID."""
        for index, sprint in enumerate(self.sprints):
            if sprint.path == sprint_path:
                # minus, because sprints are in reverse chronological order
                # positive offset means move to later sprint
                new_index = index - offset
                if 0 <= new_index < len(self.sprints):
                    return self.sprints[new_index]
        return None

    def update_list_view(self):
        self.list_view.clear()
        for sprint in self.sprints:
            item = ListItem(Static(sprint.name), id='ID'+sprint.id)
            self.list_view.append(item)

    def on_list_view_highlighted(self, event):
        """Handle selection of a sprint from the list."""
        sprint_id = event.item.id[2:]
        self.app.current_sprint_id = sprint_id
        self.app.cards_panel.get_cards(sprint_id)
