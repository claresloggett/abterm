from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.widgets import Footer

from app import CardsPanel, SprintsPanel
from api import CardClient, SprintClient

class CommandState(Enum):
    NORMAL = 1
    CHANGE_CARDSTATE = 2

class ABTerm(App):
    
    BINDINGS = [
        Binding("r", "refresh_cache", "Refresh Cache", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("key_esc", "action_cancel", "Cancel", show=False),
        Binding("t", "change_cardstate", "Change Card State", show=True),
        Binding("c", "action_close_card", "Close card", show=True),
    ]
    
    # These actions are available in each command state
    ACTION_LISTS = {
        CommandState.NORMAL: ["refresh_cache", "change_cardstate", "quit"],
        CommandState.CHANGE_CARDSTATE: ["action_close_card", "action_cancel", "quit"],
    }
    
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
        self.command_state = CommandState.NORMAL

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                self.sprints_panel,
                self.cards_panel,
                #self.card_detail_panel
            ),
            Footer()
        )

    def check_action(
            self, action: str, parameters: tuple[object, ...]
    ) -> bool | None:
        """
        Check if the requested action is valid in the current command state.
        If so, return True. If not, return False.
        If the action is not recognized, return None.
        """
        if action in self.ACTION_LISTS[self.command_state]:
            return True
        return False
    
    def action_refresh_cache(self):
        """
        Reset caches, and re-get current sprint cards.
        """
        self.sprint_client.cache.reset()
        self.card_client.cache.reset()
        if self.current_sprint_id is not None:
            self.app.cards_panel.get_cards(self.current_sprint_id)
    
    def action_change_cardstate(self):
        """
        Change the state of the selected card.
        """
        self.command_state = CommandState.CHANGE_CARDSTATE
    
    def action_close_card(self):
        pass
    
    def action_cancel(self):
        """
        Cancel the current action, returning to normal mode.
        """
        self.command_state = CommandState.NORMAL

        
