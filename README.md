# abterm

Currently expects a `config.txt` in the same directory that you launch `abterm` from, of the form

```
ORGANISATION="<myorg>"
PROJECT="<myproject>"
TEAM="<myteam>"
TOKEN="<auth-token>"
```

The token should be a Personal Access Token with at least the `Work Items (Read)` scope. If you want to make any changes to cards, you also need the `Work Items (Write)` scope. 
No other scopes are needed. Personal Access Tokens are generated under User Settings in the Azure DevOps web view.

The organisation, project, and team can be found in the Azure Boards UI. Your usual URL for viewing, for instance, sprint listings, will also contain these variables, in a form resembling 
`https://dev.azure.com/<myorg>/<myproject>/_sprints/backlog/<myteam>/....`.
