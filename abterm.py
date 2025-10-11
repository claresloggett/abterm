
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Static, ListView, ListItem, DataTable
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
        self.cards_panel = CardsPanel(self.sprint_client, self.card_client)
        self.card_detail_panel = CardDetailPanel()
        self.current_sprint_id = None

    def compose(self) -> ComposeResult:
        yield Horizontal(
            self.sprints_panel,
            self.cards_panel,
            #self.card_detail_panel
        )

    def refresh_cache(self):
        """
        Reset caches, and re-get current sprint cards.
        """
        self.sprint_client.cache.reset()
        self.card_client.cache.reset()
        if self.current_sprint_id is not None:
            self.app.cards_panel.get_cards(self.current_sprint_id)

    def on_key(self, event):
        if event.key == "r":
            self.refresh_cache()
        

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


class CardsPanel(Widget):
    """A panel to display cards as a selectable list."""

    def __init__(self, sprint_client, card_client, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()
        self.sprint_client = sprint_client
        self.card_client = card_client
        self.cards = []

    def on_mount(self):
        self.table.add_column("ID", width=5)
        self.table.add_column("Title", width=60)
        self.table.add_column("State", width=15)
        self.table.add_column("Feature", width=35)
        self.table.add_column("Epic", width=35)

    def compose(self) -> ComposeResult:
        yield self.table

    def get_cards(self, sprint_id):
        """Fetch cards for the given sprint ID."""
        cards = self.card_client.get_sprint_cards(sprint_id, self.sprint_client)
        self.cards = [self.card_client.get_card_parents(card) for card in cards]
        self.update_table()

    def update_table(self):
        """Update the table with the fetched cards."""
        self.table.clear()
        for card in self.cards:
            # Add a row for each card
            # Checking type is Task works for us, but the more generic solution would be 
            # to check if the parent is in the sprint
            prefix = ""
            if card.fields['System.WorkItemType'] == "Task":
                prefix = "  "
            self.table.add_row(
                str(card.id),
                prefix + card.fields['System.Title'],
                card.fields['System.State'],
                card.fields.get('Parent Feature', {}).get('Title', "unknown"),
                card.fields.get('Parent Epic', {}).get('Title', "unknown"))
            
    
# May not keep this; for now for exploring data
class CardDetailPanel(Widget):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card = None

    def set_card(self, card):
        #self.app.card_client.get_card_parents(card)
        self.card = card
    
    def render(self):
        if not self.card:
            return "No card selected"
        return "\n".join([f"{k}: {v}" for k,v in self.card.fields.items()])


if __name__ == "__main__":
    config = read_config()
    app = ABTerm(config['ORGANISATION'], config['PROJECT'], config['TEAM'], config['TOKEN'])
    app.run()
