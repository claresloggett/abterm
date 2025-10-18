from textual.app import App, ComposeResult
from textual.containers import Horizontal

from app import CardsPanel, SprintsPanel
from api import CardClient, SprintClient

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
        
