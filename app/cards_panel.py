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

DONE_STATES = ['Development Completed', 'Ready for UAT', 'Closed', 'Removed']

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
        self.table.add_column("Assigned", width=9)
        self.table.add_column("Feature", width=35)
        self.table.add_column("Epic", width=35)
        self.table.add_column("Initial", width=20)

    def compose(self) -> ComposeResult:
        yield self.table

    def get_cards(self, sprint_id):
        """Fetch cards for the given sprint ID."""
        cards = self.card_client.get_sprint_cards(sprint_id, self.sprint_client)
        self.cards = [self.card_client.get_card_and_parents(card) for card in cards]
        self.cards = [self.card_client.add_initial_sprint(card) for card in self.cards]
        self.update_table()
    
    def card(self, card_id):
        """Get a card by its ID from the current list."""
        for card in self.cards:
            if str(card.id) == str(card_id):
                return card
        return None

    def update_table(self):
        """Update the table with the fetched cards."""
        self.table.clear()
        for card in self.cards:
            # Add a row for each card
            # Checking type is Task works for us for indenting, 
            # but the more generic solution would be to check if the parent is in the sprint
            prefix = ""
            if card.fields['System.WorkItemType'] == "Task":
                prefix = "  "
            card_type_colour = CARD_TYPE_COLOURS.get(
                card.fields["System.WorkItemType"], "black"
            )
            text_style = ""
            if card.fields['System.State'] in DONE_STATES:
                text_style = "dim "
            card_id = Text(str(card.id), style=f"on {card_type_colour}")
            card_title = Text(prefix + card.fields['System.Title'], style=text_style)
            card_state = Text(card.fields['System.State'], style=text_style)
            card_initial_sprint = card.fields.get('Initial Sprint', "unknown")

            # Extract first name from assigned user
            if 'System.AssignedTo' in card.fields:
                display_name = card.fields['System.AssignedTo']['displayName']
                assigned_name = display_name.split()[0]  # Get first name
            else:
                assigned_name = "-"

            card_assigned = Text(assigned_name, style=text_style)
            card_feature = Text(card.fields.get('Parent Feature', {}).get('Title', "unknown"),
                                style=text_style)
            card_epic = Text(card.fields.get('Parent Epic', {}).get('Title', "unknown"),
                             style=text_style)
            self.table.add_row(
                card_id,
                card_title,
                card_state,
                card_assigned,
                card_feature,
                card_epic,
                card_initial_sprint,
                key=str(card.id)
            )


    def on_data_table_row_highlighted(self, event):
        """Handle selection of a card from the table."""
        self.app.current_card_id = event.row_key.value
    
 