
"""
This wraps the Work API; specifically it covers the parts to do with sprints/iterations
"""

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import TeamContext

BASE_URL = "https://dev.azure.com/"

class SprintClient:
    def __init__(self, org, project, team, token):
        credentials = BasicAuthentication('', token)
        print(BASE_URL+org)
        connection = Connection(base_url=BASE_URL+org, creds=credentials)
        self.client = connection.clients.get_work_client()
        self.team_context = TeamContext(project=project, team=team)
    
    def get_sprints(self):
        return self.client.get_team_iterations(self.team_context)
    
    def get_sprint_cardrefs(self, sprint_id):
        return self.client.get_iteration_work_items(self.team_context, sprint_id)
    