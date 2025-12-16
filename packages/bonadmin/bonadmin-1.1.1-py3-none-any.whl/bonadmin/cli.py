from __future__ import annotations
import json
import requests
import os
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Optional, List
import typer
from typing_extensions import Annotated
import yaml

app = typer.Typer(
    no_args_is_help=True,
    help="bonadmin — Bot or Not CLI Tool to help see the sessions information, see the results and register/unregister to sessions."
)

CONFIG_PATH = Path.home() / ".config" / "bon" / "config.yaml"


# ----- Config helpers -----

def load_config_or_exit():
    """Load ~/.config/bon/config.yaml or print an error and exit."""
    if not CONFIG_PATH.exists():
        typer.echo(f"ERROR: missing config file at {CONFIG_PATH}. To generate the config file run: bonadmin config init", err=True)
        raise typer.Exit(code=2)
    try:
        data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            typer.echo("ERROR: config must be a YAML mapping (key: value).", err=True)
            raise typer.Exit(code=2)
        return data
    except Exception as e:
        typer.echo(f"ERROR: failed to read config: {e}", err=True)
        raise typer.Exit(code=2)


def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")


def set_dotted(cfg: dict, dotted_key: str, value: str) -> dict:
    """Set cfg['a']['b']... using 'a.b' path. Values parsed via YAML (so 'true', '123' become bool/int)."""
    parts = dotted_key.split(".")
    cur = cfg
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    # Parse as YAML scalar to allow ints/bools/null naturally.
    cur[parts[-1]] = yaml.safe_load(value)
    return cfg

def login(cfg: dict):
    """Update the team authentication token."""
    try:
        base_url = cfg.get('api', {}).get('base_url')
        name = cfg.get('auth', {}).get('team_name')
        password = cfg.get('auth', {}).get('password')

        if name == '' or name == None or password == '' or password == None:
            typer.echo(f"Error: Before starting any command make sure to add your team name and password. You can do so using the command bonadmin set-team [team_name] [password]. Currently team_name={name} and password={password}")
            raise typer.Exit(code=2)
        
        response = requests.post(base_url + '/api/auth/login', headers={'Content-Type': 'application/json'}, data=json.dumps({"team_name": name, "team_password": password}))
        response.raise_for_status()
        token = response.text
        cfg = set_dotted(cfg, "auth.team_token", token)
        save_config(cfg)
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")
        raise typer.Exit(code=2)
    
def get_player_type(player_name: str) -> str:
    """Get the type of a player and make sure it's a player belonging to the team."""
    cfg = load_config_or_exit()
    try:
        team_token =  cfg.get('auth', {}).get('team_token')
        base_url = cfg.get('api', {}).get('base_url')
        response = requests.post(base_url + '/api/team/player/token', headers={'Authorization': 'bearer ' + team_token, 'Content-Type': 'application/json'}, data=json.dumps({"player_name": player_name}))
        response.raise_for_status()
        type = response.json()["player_type"]
        return type
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")
        raise typer.Exit(code=2)

def choose_id(session_id, cfg: dict) -> int:
    if session_id is None:
        default_id = cfg.get('defaults', {}).get('session_id')
        if default_id is None:
            raise typer.BadParameter("session_id not provided and defaults.session_id missing in config")
        try:
            id_to_use = int(default_id)
        except Exception:
            raise typer.BadParameter("defauls.session_id in config must be an integer")
    else:
        try:
            id_to_use = int(session_id)
        except Exception:
            raise typer.BadParameter("defauls.session_id in config must be an integer")
    
    return id_to_use

def parse_env_vars(_ctx: typer.Context, _param: typer.CallbackParam, value: Optional[str]) -> List[Dict[str, str]]:
    if not value:                   # omitted or empty -> []
        return []
    try:
        data = json.loads(value)
    except json.JSONDecodeError as e:
        raise typer.BadParameter(f"Invalid JSON: {e}")

    # Accept either a list of {"key","value"} or a mapping object
    if isinstance(data, dict):
        return [{"key": k, "value": str(v)} for k, v in data.items()]
    if isinstance(data, list):
        out: List[Dict[str, str]] = []
        for i, item in enumerate(data):
            if not (isinstance(item, dict) and "key" in item and "value" in item):
                raise typer.BadParameter(f"Item {i} must be an object with 'key' and 'value'")
            out.append({"key": str(item["key"]), "value": str(item["value"])})
        return out
    raise typer.BadParameter("Must be a JSON array of objects or a JSON object")

# ----- Commands -----
@app.command()
def team_info():
    """Show the current team informations."""
    cfg = load_config_or_exit()
    try:
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.get(base_url + '/api/team/info', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'})
        response.raise_for_status()
        typer.echo(json.dumps(response.json(), indent=2))
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            team_info()
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def add_bot(player_name: str, player_update_email: Annotated[str, typer.Argument(help="The email at which the update specific to this player are sent at the end of the run of a session")]):
    """Add a bot player to the team."""
    cfg = load_config_or_exit()
    try:
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.post(base_url + '/api/team/player/bot/add', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'}, data=json.dumps({"player_name": player_name, "player_update_email": player_update_email}))
        response.raise_for_status()
        typer.echo(f"The bot player {player_name} was successfully added and the email attached to it is {player_update_email}.")
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            add_bot(player_name, player_update_email)
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def add_detector(player_name: str, player_update_email: Annotated[str, typer.Argument(help="The email at which the update specific to this player are sent at the end of the run of a session")]):
    """Add a detector player to the team."""
    cfg = load_config_or_exit()
    try:
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.post(base_url + '/api/team/player/detector/add', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'}, data=json.dumps({"player_name": player_name, "player_update_email": player_update_email}))
        response.raise_for_status()
        typer.echo(f"The detector player {player_name} was successfully added and the email attached to it is {player_update_email}.")
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            add_detector(player_name, player_update_email)
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def list_sessions():
    """Show past sessions and those open for registration."""
    cfg = load_config_or_exit()
    try:
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.get(base_url + '/api/team/session/info', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'})
        response.raise_for_status()
        typer.echo(json.dumps(response.json(), indent=2))
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            list_sessions()
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def session_info(session_id: Optional[int] = typer.Argument(None)):
    """Before a session runs, show which of your players are registered to the session. If so shows your registration info for each players. After a session happened show the session results followed by the registration info of your players for this session."""
    cfg = load_config_or_exit()
    try:
        s_id = choose_id(session_id, cfg)
        name = cfg.get('auth', {}).get('team_name')
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.get(base_url + '/api/team/session/' + str(s_id) + '/registration_status', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'})
        response.raise_for_status()
    except(requests.exceptions.RequestException) as error:
        if error.response.json().get('message') == 'Unauthorized':
            login(cfg)
            session_info(session_id)
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

    try:
        sessions_list = requests.get(base_url + '/api/team/session/info', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'})
        past_session = False
        for session in sessions_list.json()["past_sessions"]:
            if session["session_id"] == s_id:
                past_session = True
                typer.echo(f"Session results of session {s_id}:\n\n")
                get_session_results(s_id)
                typer.echo(f"\n")

        no_player_registered = True
        for resp in response.json()["players_registration_status"]:
            if resp["registered"]:
                no_player_registered = False
                break

        if not no_player_registered:
            info_response = requests.get(base_url + '/api/team/session/' + str(s_id) + '/registration_info', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'})
            info_response.raise_for_status()
            typer.echo(f"Registration information of session {s_id} for the players of team {name}:\n\n{json.dumps(info_response.json(), indent=2)}\n\nIf a player is not registered then the dockerhub_image and dockerhub_tag are \"\" and env_vars is [].")
        else:
            if past_session:
                typer.echo(f"No players of team {name} were registered for session {s_id}.")
            else:
                typer.echo(f"No players of team {name} are registered for session {s_id}.")
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def get_session_results(session_id: Optional[int] = typer.Argument(None)):
    """Get results for a specific session."""
    cfg = load_config_or_exit()
    try:
        s_id = choose_id(session_id, cfg)
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.get(base_url + '/api/team/session/' + str(s_id) + '/results', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'})
        response.raise_for_status()
        typer.echo(f"{json.dumps(response.json(), indent=2)}")
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            get_session_results(session_id)
        else:
            typer.echo(f"Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def register(player_name: str, dockerhub_image: str, dockerhub_tag: str, session_id: Optional[int] = typer.Argument(None, help="If none entered we use as a default the one set in the config file at defaults.session_id"), env_vars: Optional[str] = typer.Option(None, "--env", help="This optional parameter is a json list entered as a string. To set enter: '[{\"key\": \"A\", \"value\": \"B\"}]' OR '{\"A\": \"B\", \"ressource\": \"token\"}'. For Windows users the \" are not working so enter: '{\\\"A\\\": \\\"B\\\", \\\"ressource\\\": \\\"token\\\"}'", callback=parse_env_vars)):
    """Register a player for a session."""
    cfg = load_config_or_exit()
    try:
        s_id = choose_id(session_id, cfg)
        type = get_player_type(player_name)
        base_url = cfg.get('api', {}).get('base_url')
        token = cfg.get('auth', {}).get('team_token')

        response = requests.post(base_url + '/api/team/player/session/' + str(s_id) + '/register', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'}, data=json.dumps({"player_name": player_name, "dockerhub_image": dockerhub_image, "dockerhub_tag": dockerhub_tag, "env_vars": env_vars}))
        response.raise_for_status()
        typer.echo(f"Successful registration of {type} player {player_name} to session {s_id}. Here are the registration info:\n\nplayer name: {player_name}\ndockerhub image: {dockerhub_image}:{dockerhub_tag}\nenv_vars: {env_vars}")
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            register(player_name, dockerhub_image, dockerhub_tag, session_id, env_vars)
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def unregister(player_name: str, session_id: Optional[int] = typer.Argument(None)):
    """Unregister a player for a session."""
    cfg = load_config_or_exit()
    try:
        s_id = choose_id(session_id, cfg)
        base_url = cfg.get('api', {}).get('base_url')
        type = get_player_type(player_name)
        token = cfg.get('auth', {}).get('team_token')

        response = requests.post(base_url + '/api/team/player/session/' + str(s_id) + '/withdraw', headers={'Authorization': 'bearer ' + token, 'Content-Type': 'application/json'}, data=json.dumps({"player_name": player_name}))
        response.raise_for_status()
        typer.echo(f"Successfully unregistered {type} player {player_name} from session {s_id}.")
    except(requests.exceptions.RequestException) as error:
        error_details = error.response.json()
        if error_details.get('message') == 'Unauthorized':
            login(cfg)
            unregister(player_name, session_id)
        else:
            typer.echo(f"An error occurred: {error}. Error Message: {error_details.get('message', 'No message available')}")

@app.command()
def set_team(team_name: str, password: Optional[str] = typer.Argument(None, help="If the password stay the same no need to enter it")):
    """Set the team name (and password if entered) that is used."""
    cfg = load_config_or_exit()
    if password is None:
        pw = cfg.get('auth', {}).get('password')
    else:
        pw = password
    cfg = set_dotted(cfg, "auth.team_name", team_name)
    cfg = set_dotted(cfg, "auth.password", str(pw))
    save_config(cfg)
    login(cfg)
    if password is None:
        typer.echo(f"Set team to team_name: {cfg.get('auth', {}).get('team_name')}.")
    else:
        typer.echo(f"Set team to team_name: {cfg.get('auth', {}).get('team_name')} and password.")

# ----- Config Tools to Look or Modify the local config file -----

config_app = typer.Typer(help="Inspect or modify the local config file")
app.add_typer(config_app, name="config")

@config_app.command("path")
def config_path():
    """Show where the config is expected to live."""
    typer.echo(CONFIG_PATH)

@config_app.command("show")
def config_show():
    """Print the current config file content (or error if missing)."""
    cfg = load_config_or_exit()
    typer.echo(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), nl=False)

@config_app.command("set")
def config_set(key: str, value: str):
    """
    Set a value in the config by dotted path or add new ones and save it.
    Examples:\n
      bonadmin config set auth.team_name bob\n
      bonadmin config set auth.password s3cr3t\n
      bonadmin config set api.base_url http://localhost:3000\n
      bonadmin config set defaults.session_id 10\n
    """
    cfg = {}
    if CONFIG_PATH.exists():
        cfg = load_config_or_exit()  # strict read
    # If the file didn't exist, we'll create it now.
    if key == 'team_name':
        typer.echo(f"Error: To change the team use the command bonadmin set-team <team_name> <password>.")
        raise typer.Exit(code=2)
    cfg = set_dotted(cfg, key, value)
    save_config(cfg)
    if key == 'player_name':
        type = get_player_type(value)
        cfg = set_dotted(cfg, "auth.type", type)
        save_config(cfg)
    typer.echo(f"Changed {key} to {value} in {CONFIG_PATH}")

@config_app.command("init")
def init_cmd(force: bool = typer.Option(False, "--force", "-f", help="Overwrite an existing config file")):
    """
    Create ~/.config/bon/config.yaml from a template.

    Uses the bundled bonadmin/example_config.yaml.
    Use --force to overwrite an existing file and reset it to the example_config.yaml.
    """
    target = CONFIG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not force:
        typer.echo(f"Config already exists at {target}. Use --force to overwrite.")
        return

    
    content = resources.files("bonadmin").joinpath("example_config.yaml").read_text(encoding="utf-8")
    target.write_text(content, encoding="utf-8")

    # Best practice on POSIX: user-read/write only
    try:
        if os.name == "posix":
            os.chmod(target, 0o600)
    except Exception:
        # ignore permissions errors on non-POSIX or unusual FS
        pass

    typer.echo(f"Created {target}")


if __name__ == "__main__":
    app()
