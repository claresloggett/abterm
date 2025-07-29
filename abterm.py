
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Static, ListView, ListItem
from textual.containers import Grid, Horizontal, Vertical

from cardclient import CardClient
from sprintclient import SprintClient

# the config file is currently Python-like; could technically import it instead
# TODO: should put it into user's home dir; this is reliant on relative path
CONFIG_FILE = "config.txt"

def read_config():
    expected_keys = ['ORGANISATION', 'PROJECT', 'TEAM', 'TOKEN']
    with open(CONFIG_FILE, "r") as f:
        config = {}
        for line in f:
            key, value = line.split("=")
            config[key.strip()] = value.strip(" \"'\n")
        for key in expected_keys:
            if key not in config:
                raise ValueError(f"Missing required key in config: {key}")
    return config

class ABTerm(App):
    def __init__(self, org, project, team, token, **kwargs):
        super().__init__(**kwargs)
        self.title = "Azure Boards Terminal"
        self.organisation = org
        self.project = project
        self.team = team
        self.sprint_client = SprintClient(org, project, team, token)
        self.card_client = CardClient(org, project, token)
        self.sprints_panel = SprintsPanel(self.sprint_client)
        self.cards_panel = CardsPanel()
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            self.sprints_panel,
            self.cards_panel,
        )
        

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
        sprints = self.client.get_sprints()
        self.sprints = [sprint.name for sprint in sprints][::-1]
        self.update_list_view()

    def update_list_view(self):
        self.list_view.clear()
        for sprint in self.sprints:
            item = ListItem(Static(sprint), id=sprint.replace(" ", "_"))
            self.list_view.append(item)

class CardsPanel(Widget):
    """A panel to display cards as a selectable list."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def render(self):
        return("This is the cards panel")


if __name__ == "__main__":
    config = read_config()
    app = ABTerm(config['ORGANISATION'], config['PROJECT'], config['TEAM'], config['TOKEN'])
    app.run()
