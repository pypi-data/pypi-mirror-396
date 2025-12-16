# bonadmin — Bot or Not CLI

A small command‑line tool to register bots/bot‑detectors for Bot or Not sessions, look up registration information for sessions, and fetch results.



## Installation

```bash
pip install bonadmin
```


## First‑time setup

1) **Create a starter config** (one time):

```bash
bonadmin config init
# use --force to overwrite an existing file
```

This creates `~/.config/bon/config.yaml`.

2) **Edit your configuration** (fill in team name and password, change the session id):

```yaml
# ~/.config/bon/config.yaml
api:
  base_url: "http://54.145.53.252:3000"
auth:
  team_name: ""
  password: ""
  team_token: ""
defaults:
  session_id: 10
```
_**Important:** If you don't set the team\_name and password you won't be able to run any other commands except `bonadmin set-team` or the `bonadmin config` commands._

> Notes
> - Current default path is `~/.config/bon/config.yaml`. If you need a different location set it up manually (change the default location in the code) and use `bonadmin config set` to populate values.
> - Run `bonadmin config path` to print the path your CLI is using.


## Usage

Every command supports `--help`. For example:

```bash
bonadmin --help
bonadmin list-sessions --help
```

### Commands
---
#### `bonadmin team-info`
Show the current team informations.

**Example**
```bash
bonadmin team-info
```
---
#### `bonadmin add-bot <player_name> <player_update_email>`
Add a bot player to the team. The player update email is the one used to receive informations related to the player.

**Example**
```bash
bonadmin add-bot BotPlayer player.email@gmail.com
```
---
#### `bonadmin add-detector <player_name> <player_update_email>`
Add a detector player to the team. The player update email is the one used to receive informations related to the player.

**Example**
```bash
bonadmin add-detector DetectorPlayer player.email@gmail.com
```
---
#### `bonadmin list-sessions`
Show all sessions past (for which the results are available) and upcoming that are open for registration.

**Example**
```bash
bonadmin list-sessions
```
---
#### `bonadmin session-info <session_id>`
Show your team registration information. If available the session is past shows the results for that session followed by the registration information of that session.

**Example**
```bash
bonadmin session-info 12
```
>_If session id not provided use the default one in the config file (`defaults.session_id`)._
---
#### `bonadmin get-session-results <session_id>`
Fetch and print in json format the results for a session.

**Example**
```bash
bonadmin get-session-results 12
```
>_If session id not provided use the default one in the config file (`defaults.session_id`)._
---
#### `bonadmin register <player_name> <dockerhub_image> <dockerhub_tag> <session_id> --env <env_vars>`
Register a bot or detector player for a session.

**Example (macOS and linux)**
```bash
bonadmin register bob_bot bob/image latest 12 --env '{"ressource": "token"}'
```
**Example (Windows)**
```bash
bonadmin register bob_bot bob/image latest 12 --env '{\"ressource\": \"token\"}'
```
> Notes:
> - The env_vars key need to start with `ENV_` for the backend to accept them.
> - _If session id not provided use the default one in the config file (`defaults.session_id`) and if the environment variable are not provided it automatically returns an empty list._

---
#### `bonadmin unregister <player_name> <session_id>`
Unregister a bot/detector player from a session.

**Example**
```bash
bonadmin unregister bob_bot 12
```
>_If session id not provided use the default one in the config file (`defaults.session_id`)._
---
#### `bonadmin set-team <team_name> <password>`
Fetch and print in json format the results for a session.

**Example**
```bash
bonadmin set-team teamName 12345
```
>_If password not provided don't modify the password entry in the config file (`auth.password`)._
---
#### `bonadmin config init` 
Create `~/.config/bon/config.yaml` from a packaged template.

**Options**
- `--force, -f` — overwrite if the file exists

**Examples**
```bash
bonadmin config init
bonadmin config init --force
```
---
#### `bonadmin config path`
Print the absolute path to the active config file.

**Example**
```bash
bonadmin config path
```
---
#### `bonadmin config show`
Pretty‑print the loaded config.

**Example**
```bash
bonadmin config show
```
---
#### `bonadmin config set <dotted.key> <value>`
Set and save a single value using dotted lookup; creates the file if missing.

**Examples**
```bash
bonadmin config set api.base_url http://localhost:3000
bonadmin config set defaults.session_id 10
```
---

## Example

```bash
# List available sessions
bonadmin list-sessions

# Inspect one session
bonadmin session-info 10

# Register a bot for session 24
bonadmin register bob_bot bob/bot_image latest 24 --env '{\"ressource\": \"token\"}'

# Later, remove it
bonadmin unregister bob_bot 24

# Show config and path
bonadmin config path
bonadmin config show
```


## Troubleshooting

- **`Config not found` / `failed to read config`**  
  Run `bonadmin config init`, then open `~/.config/bon/config.yaml` and fill in username and password. If you've changed the `defaults.session_id` make sure the id correspond to an existing session.

- **HTTP or auth errors**  
  Check `auth.*` values. If the username and password are not set, enter your username and password. For other HTTP error an error message will be provided.
