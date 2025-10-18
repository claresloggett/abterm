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
        self.cache = WorkItemCache(self.client)

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
        epics = self.cache.get_work_items_batch(self.project, ids, fields=fields)
        return [self.add_state_to_card(epic.as_dict()) for epic in epics]

    def get_children(self, card_id, fields=None):
        """Get all children of the given card"""
        workitem = self.cache.get_work_item(card_id, expand='relations')
        child_ids = [item['url'].split('/')[-1] for item in workitem.as_dict()['relations'] if item['attributes']['name']=='Child']
        if len(child_ids)==0:
            return []
        # TODO should check listing is not over 200 items, and batch
        cards = self.cache.get_work_items_batch(self.project, child_ids, fields=fields)
        return [self.add_state_to_card(card.as_dict()) for card in cards]

    def update_card_state(self, card_id, new_state):
        """Set card state to requested state"""
        action = JsonPatchOperation(op='Replace', path='/fields/System.State', value=new_state)
        result = self.client.update_work_item([action], card_id)
        return result.as_dict()
    
    def get_sprint_cards(self, sprint_id, sprint_client):
        cardrefs = sprint_client.get_sprint_cardrefs(sprint_id)
        card_ids = [cardref.target.id for cardref in cardrefs.work_item_relations]
        cards = []
        while len(card_ids) > 0:
            # Get a batch of cards, up to 200 at a time (API limit)
            batch_ids = card_ids[:200]
            card_ids = card_ids[200:]
            batch = self.cache.get_work_items_batch(self.project, batch_ids, expand='relations')
            cards += batch
        return cards

    def get_card_parents(self, card):
        """
        Get all parents of the given card and add them as fields (Parent Feature, Parent Epic, Parent User Story).
        Also add the first parent as a top-level field 'Parent'.
        """
        # In case we need to get it again for the relations
        card = self.cache.get_work_item(card.id, expand='relations')
        current_parent = card
        direct_parent = True
        while (parent_id :=  current_parent.fields.get('System.Parent')):
            # Get the parent card
            current_parent = self.cache.get_work_item(parent_id, expand='relations')
            # Get the workitem type and title of the parent
            parent_type = current_parent.fields['System.WorkItemType']
            parent_title = current_parent.fields['System.Title']
            # Add the parent as a field
            card.fields[f'Parent {parent_type}'] = {
                'Id': parent_id,
                'Title': parent_title
            }
            if direct_parent:
                # If this is the first parent, add it as a direct parent
                card.fields['Parent'] = {
                    'Id': parent_id,
                    'Title': parent_title
                }
                direct_parent = False
        return card


class WorkItemCache:
    def __init__(self, client):
        self.client = client
        self.cache = {}

    def reset(self):
        self.cache = {}

    def get_work_item(self, card_id, expand=None):
        key = (card_id, expand)
        if key not in self.cache:
            self.cache[key] = self.client.get_work_item(card_id, expand=expand)
        return self.cache[key]

    # Does not exactly match the API as doesn't require a WorkItemBatchGetRequest
    def get_work_items_batch(self, project, ids, fields=None, expand=None):
        unknown_ids = [id for id in ids if (id, fields, expand) not in self.cache]
        if len(unknown_ids)>0:
            request = WorkItemBatchGetRequest(ids=unknown_ids, fields=fields, expand=expand)
            cards = self.client.get_work_items_batch(request, project=project)
            for card in cards:
                self.cache[(card.id, fields, expand)] = card
        return [self.cache[(id, fields, expand)] for id in ids]