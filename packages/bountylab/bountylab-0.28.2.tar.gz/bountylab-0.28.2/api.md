# RawUsers

Types:

```python
from bountylab.types import RawUserRetrieveResponse, RawUserByLoginResponse, RawUserGraphResponse
```

Methods:

- <code title="post /api/raw/users">client.raw_users.<a href="./src/bountylab/resources/raw_users.py">retrieve</a>(\*\*<a href="src/bountylab/types/raw_user_retrieve_params.py">params</a>) -> <a href="./src/bountylab/types/raw_user_retrieve_response.py">RawUserRetrieveResponse</a></code>
- <code title="post /api/raw/users/by-login">client.raw_users.<a href="./src/bountylab/resources/raw_users.py">by_login</a>(\*\*<a href="src/bountylab/types/raw_user_by_login_params.py">params</a>) -> <a href="./src/bountylab/types/raw_user_by_login_response.py">RawUserByLoginResponse</a></code>
- <code title="post /api/raw/users/{id}/graph/{relationship}">client.raw_users.<a href="./src/bountylab/resources/raw_users.py">graph</a>(relationship, \*, id, \*\*<a href="src/bountylab/types/raw_user_graph_params.py">params</a>) -> <a href="./src/bountylab/types/raw_user_graph_response.py">RawUserGraphResponse</a></code>

# RawRepos

Types:

```python
from bountylab.types import RawRepoRetrieveResponse, RawRepoByFullnameResponse, RawRepoGraphResponse
```

Methods:

- <code title="post /api/raw/repos">client.raw_repos.<a href="./src/bountylab/resources/raw_repos.py">retrieve</a>(\*\*<a href="src/bountylab/types/raw_repo_retrieve_params.py">params</a>) -> <a href="./src/bountylab/types/raw_repo_retrieve_response.py">RawRepoRetrieveResponse</a></code>
- <code title="post /api/raw/repos/by-fullname">client.raw_repos.<a href="./src/bountylab/resources/raw_repos.py">by_fullname</a>(\*\*<a href="src/bountylab/types/raw_repo_by_fullname_params.py">params</a>) -> <a href="./src/bountylab/types/raw_repo_by_fullname_response.py">RawRepoByFullnameResponse</a></code>
- <code title="post /api/raw/repos/{id}/graph/{relationship}">client.raw_repos.<a href="./src/bountylab/resources/raw_repos.py">graph</a>(relationship, \*, id, \*\*<a href="src/bountylab/types/raw_repo_graph_params.py">params</a>) -> <a href="./src/bountylab/types/raw_repo_graph_response.py">RawRepoGraphResponse</a></code>

# UserEmails

Types:

```python
from bountylab.types import (
    UserEmailBestEmailResponse,
    UserEmailBestEmailByLoginResponse,
    UserEmailReplySignalResponse,
)
```

Methods:

- <code title="post /api/users/best-email">client.user_emails.<a href="./src/bountylab/resources/user_emails.py">best_email</a>(\*\*<a href="src/bountylab/types/user_email_best_email_params.py">params</a>) -> <a href="./src/bountylab/types/user_email_best_email_response.py">UserEmailBestEmailResponse</a></code>
- <code title="post /api/users/best-email/by-login">client.user_emails.<a href="./src/bountylab/resources/user_emails.py">best_email_by_login</a>(\*\*<a href="src/bountylab/types/user_email_best_email_by_login_params.py">params</a>) -> <a href="./src/bountylab/types/user_email_best_email_by_login_response.py">UserEmailBestEmailByLoginResponse</a></code>
- <code title="post /api/users/best-email/signal/reply">client.user_emails.<a href="./src/bountylab/resources/user_emails.py">reply_signal</a>(\*\*<a href="src/bountylab/types/user_email_reply_signal_params.py">params</a>) -> <a href="./src/bountylab/types/user_email_reply_signal_response.py">UserEmailReplySignalResponse</a></code>

# SearchUsers

Types:

```python
from bountylab.types import SearchUserNaturalLanguageResponse, SearchUserSearchResponse
```

Methods:

- <code title="post /api/search/users/natural-language">client.search_users.<a href="./src/bountylab/resources/search_users.py">natural_language</a>(\*\*<a href="src/bountylab/types/search_user_natural_language_params.py">params</a>) -> <a href="./src/bountylab/types/search_user_natural_language_response.py">SearchUserNaturalLanguageResponse</a></code>
- <code title="post /api/search/users">client.search_users.<a href="./src/bountylab/resources/search_users.py">search</a>(\*\*<a href="src/bountylab/types/search_user_search_params.py">params</a>) -> <a href="./src/bountylab/types/search_user_search_response.py">SearchUserSearchResponse</a></code>

# SearchRepos

Types:

```python
from bountylab.types import SearchRepoNaturalLanguageResponse, SearchRepoSearchResponse
```

Methods:

- <code title="post /api/search/repos/natural-language">client.search_repos.<a href="./src/bountylab/resources/search_repos.py">natural_language</a>(\*\*<a href="src/bountylab/types/search_repo_natural_language_params.py">params</a>) -> <a href="./src/bountylab/types/search_repo_natural_language_response.py">SearchRepoNaturalLanguageResponse</a></code>
- <code title="post /api/search/repos">client.search_repos.<a href="./src/bountylab/resources/search_repos.py">search</a>(\*\*<a href="src/bountylab/types/search_repo_search_params.py">params</a>) -> <a href="./src/bountylab/types/search_repo_search_response.py">SearchRepoSearchResponse</a></code>
