"""
This wraps the WorkItems API; it covers the backlog and manipulation of individual cards
"""

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import Wiql, WorkItemBatchGetRequest, JsonPatchOperation

# TODO add dataframe versions

BASE_URL = "https://dev.azure.com/"

class CardClient:
    def __init__(self, org, project, token):
        self.project = project
        credentials = BasicAuthentication('', token)
        connection = Connection(base_url=BASE_URL+org, creds=credentials)
        self.client = connection.clients.get_work_item_tracking_client()

    def add_state_to_card(self, card):
        """Add state as a top-level entry on the dict"""
        card['state'] = card['fields']['System.State']
        return card

    def get_epics(self):
        """Get all Epics in self.project"""
        # If no fields provided, gets all fields
        # TODO allow taking fields as input to function
        query = Wiql("SELECT * FROM WorkItems WHERE [System.WorkItemType] = 'Epic'")
        listing = self.client.query_by_wiql(query)
        # TODO should check listing is not over 200 items, and batch
        ids = [item.id for item in listing.work_items]
        if len(ids)==0:
            return []
        epics = self.client.get_work_items_batch(WorkItemBatchGetRequest(ids=ids, fields=fields), project=self.project)
        return [self.add_state_to_card(epic.as_dict()) for epic in epics]

    def get_children(self, card_id, fields=None):
        """Get all children of the given card"""
        workitem = self.client.get_work_item(card_id, expand='relations')
        child_ids = [item['url'].split('/')[-1] for item in workitem.as_dict()['relations'] if item['attributes']['name']=='Child']
        if len(child_ids)==0:
            return []
        # TODO should check listing is not over 200 items, and batch
        cards = self.client.get_work_items_batch(WorkItemBatchGetRequest(ids=child_ids, fields=fields), project=self.project)
        return [self.add_state_to_card(card.as_dict()) for card in cards]

    def update_card_state(self, card_id, new_state):
        """Set card state to requested state"""
        action = JsonPatchOperation(op='Replace', path='/fields/System.State', value=new_state)
        result = self.client.update_work_item([action], card_id)
        return result.as_dict()