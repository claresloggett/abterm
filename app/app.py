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
    MOVE_CARD = 3

class ABTerm(App):
    
    # These may contain duplicate hotkeys so long as the ACTION_LISTS do not overlap
    BINDINGS = [
        Binding("r", "refresh_cache", "Refresh Cache", show=True),
        Binding("s", "cmds_cardstate", "Change Card State", show=True),
        Binding("m", "cmds_move_card", "Move Card", show=True),
        Binding("o", "open_card_url", "Open Card URL", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "cancel", "Cancel", show=False),
        
        Binding("n", "card_set_state('New')", "New", show=True),
        Binding("a", "card_set_state('Active')", "Active", show=True),
        Binding("d", "card_set_state('Development Completed')", "DevCompleted", show=True),
        Binding("c", "card_set_state('Closed')", "Close", show=True),
        
        Binding("n", "move_card(1)", "Next", show=True),
        Binding("p", "move_card(-1)", "Previous", show=True),
        Binding("b", "move_card_to_backlog()", "Backlog", show=True),
    ]
    
    # These actions are available in each command state
    ACTION_LISTS = {
        CommandState.NORMAL: ["refresh_cache", "cmds_cardstate",  "cmds_move_card", 
                              "open_card_url", "quit"],
        CommandState.CHANGE_CARDSTATE: ["card_set_state", "cancel", "quit"],
        CommandState.MOVE_CARD: ["move_card", "move_card_to_backlog", "cancel", "quit"],
    }
    
    def __init__(self, base_url, org, project, team, token, **kwargs):
        super().__init__(**kwargs)
        self.title = "Azure Boards Terminal"
        self.base_url = base_url
        self.organisation = org
        self.project = project
        self.team = team
        self.sprint_client = SprintClient(base_url, org, project, team, token)
        self.card_client = CardClient(base_url, org, project, token)
        self.sprints_panel = SprintsPanel(self.sprint_client)
        self.cards_panel = CardsPanel(self.sprint_client, self.card_client)
        self.current_sprint_id = None
        self.current_card_id = None
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
            self.cards_panel.get_cards(self.current_sprint_id)
    
    def action_open_card_url(self):
        """
        Open the selected card in the web browser.
        """
        if self.current_card_id is not None:
            url = f"{self.base_url}/{self.organisation}/{self.project}/_workitems/edit/{self.current_card_id}/"
            self.open_url(url)
    
    def action_cmds_cardstate(self):
        """
        Change the state of the selected card.
        """
        if self.current_card_id is not None:
            self.command_state = CommandState.CHANGE_CARDSTATE
        self.refresh_bindings()

    def action_card_set_state(self, new_state: str):
        if self.current_card_id is not None:
            self.card_client.update_card_state(self.current_card_id, new_state)
            # Refresh the cards panel
            if self.current_sprint_id is not None:
                self.cards_panel.get_cards(self.current_sprint_id)
        self.command_state = CommandState.NORMAL
        self.refresh_bindings()
    
    def action_cmds_move_card(self):
        """
        Move the selected card to another sprint.
        """
        if self.current_card_id is not None:
            self.command_state = CommandState.MOVE_CARD
        self.refresh_bindings()
    
    def action_move_card(self, offset: int):
        """
        Move the selected card to another sprint.
        """
        if self.current_card_id is None:
            return
        # Get the current sprint of the card
        card = self.card_client.get_card(self.current_card_id)
        current_sprint_path = card['fields'].get('System.IterationPath', None)
        if current_sprint_path is None:
            return
        new_sprint = self.sprints_panel.get_sprint_by_offset(current_sprint_path, offset)
        if new_sprint is None:
            return
        self.card_client.update_card_sprint(self.current_card_id, new_sprint.path, self.sprint_client)
        # Refresh the cards panel
        if self.current_sprint_id is not None:
            self.cards_panel.get_cards(self.current_sprint_id)
        self.command_state = CommandState.NORMAL
        self.refresh_bindings()
    
    def action_move_card_to_backlog(self):
        """
        Move the selected card to the backlog.
        """
        if self.current_card_id is None:
            return
        backlog = self.project
        self.card_client.update_card_sprint(self.current_card_id, f"{backlog}", self.sprint_client)
        # Refresh the cards panel
        if self.current_sprint_id is not None:
            self.cards_panel.get_cards(self.current_sprint_id)
        self.command_state = CommandState.NORMAL
        self.refresh_bindings()
    
    def action_cancel(self):
        """
        Cancel the current action, returning to normal mode.
        """
        self.command_state = CommandState.NORMAL
        self.refresh_bindings()
    

        
