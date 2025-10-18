
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
