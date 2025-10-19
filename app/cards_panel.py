from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from rich.text import Text

CARD_TYPE_COLOURS = {
    "User Story": "#2a7fff",
    "Task": "#803300",
    "Bug": "#b82727",
    "Feature": "#7137c8",
    "Epic": "#e69138",
}

class CardsPanel(Widget):
    """A panel to display cards as a selectable list."""

    def __init__(self, sprint_client, card_client, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()
        self.table.cursor_type = "row"
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
            card_type_colour = CARD_TYPE_COLOURS.get(
                card.fields["System.WorkItemType"], "black"
            )
            card_id = Text(str(card.id), style=f"on {card_type_colour}")
            self.table.add_row(
                card_id,
                prefix + card.fields['System.Title'],
                card.fields['System.State'],
                card.fields.get('Parent Feature', {}).get('Title', "unknown"),
                card.fields.get('Parent Epic', {}).get('Title', "unknown"))
            
 