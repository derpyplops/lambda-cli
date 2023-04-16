import typer
import requests
import bullet
from yaspin import yaspin
from yaspin.spinners import Spinners
import time
import os
from rich import print
from rich.console import Console
console = Console()

try:
    key = os.environ["LAMBDA_KEY"]
except Exception:
    console.print("error: LAMBDA_KEY is not set", style="red")
    exit(1)

INSTANCES_URL = "https://cloud.lambdalabs.com/api/v1/instances"
INSTANCE_TYPES_URL = "https://cloud.lambdalabs.com/api/v1/instance-types"
LAUNCH_URL = "https://cloud.lambdalabs.com/api/v1/instance-operations/launch"
TERMINATE_URL = "https://cloud.lambdalabs.com/api/v1/instance-operations/terminate"

app = typer.Typer()

auth = (key, "")

def get_or_throw(request):
    if request.status_code == 200:
        return request.json()["data"]
    else:
        raise Exception("Request failed with status code: " + str(request.status_code))


def get_random_memorable_name():
    r = requests.get("https://random-word-api.herokuapp.com/word?number=2")
    return r.json()[0] + "-" + r.json()[1]


def entry(name, ip):
    return f"""\nHost lambda | {name}
  HostName {ip}
  User ubuntu
  ForwardAgent yes
"""


@app.command()
def new(ssh: bool = typer.Option(False, help="Add to ssh config at ~/.ssh/config")):
    with yaspin(Spinners.moon, "Loading Instances...") as spinner:
        instances = get_or_throw(requests.get(INSTANCE_TYPES_URL, auth=auth))
    available = {}
    for instance in instances.values():
        if instance["regions_with_capacity_available"]:
            desc = instance["instance_type"]["description"]
            cost = instance["instance_type"]["price_cents_per_hour"]
            rendered = f"{desc} | ${cost/100:.2f}/hr"
            available[rendered] = instance

    ans = bullet.Bullet(
        prompt="Choose an instance type: ", choices=list(available.keys())
    )
    result = available[ans.launch()]
    name = get_random_memorable_name()
    config = {
        "region_name": result["regions_with_capacity_available"][0]["name"],
        "instance_type_name": result["instance_type"]["name"],
        "ssh_key_names": ["macbook"],
        "name": name,
    }
    with yaspin(Spinners.moon, "Creating Instance...") as spinner:
        ids = get_or_throw(
            requests.post(LAUNCH_URL, json=config, auth=auth)
        )  # todo err handling
        instance_id = ids["instance_ids"][0]
    print(f"Created instance with id: {instance_id}")
    with yaspin(Spinners.moon, "Instance Status [0s]: booting") as spinner:
        instance = get_or_throw(
            requests.get(INSTANCES_URL + "/" + instance_id, auth=auth)
        )
        t = 0
        while instance["status"] != "active":
            time.sleep(1)
            instance = get_or_throw(
                requests.get(INSTANCES_URL + "/" + instance_id, auth=auth)
            )
            t += 1
            spinner.text = f"Instance Status [{t}s]: {instance['status']}"
    
    if ssh:
        with open(os.path.expanduser("~/.ssh/config"), "a") as f:
            f.write(entry(name, instance["ip"]))
    else:
        print(f"Instance is ready! You can ssh to it with")
        print(f"> ssh ubuntu@{instance['ip']}", style="green")



@app.command()
def stop():
    with yaspin(Spinners.moon, "Loading Instances...") as spinner:
        instances = get_or_throw(requests.get(INSTANCES_URL, auth=auth))
    if not instances:
        print("No instances found.")
        return
    available = {}
    for instance in instances:
        name = instance["name"]
        name_rendered = f"{name} | " if name else ""
        instance_type = instance["instance_type"]["description"]
        rendered = name_rendered + f"{instance_type} | {instance['status']}"
        available[rendered] = instance

    ans = bullet.Bullet(
        prompt="Choose an instance to stop: ", choices=list(available.keys())
    )
    result = available[ans.launch()]
    instance_id = result["id"]
    with yaspin(Spinners.moon, "Stopping Instance...") as spinner:
        _ = get_or_throw(
            requests.post(
                TERMINATE_URL, json={"instance_ids": [instance_id]}, auth=auth
            )
        )
    print(f"Stopped successfully.")


@app.command()
def ls():
    with yaspin(Spinners.moon, "Loading Instances...") as spinner:
        instances = get_or_throw(requests.get(INSTANCES_URL, auth=auth))
    if not instances:
        print("No instances found.")
        return
    for instance in instances:
        rendered = f"{instance['name']} | {instance['instance_type']['description']} | {instance['status']}"
        print(rendered)


if __name__ == "__main__":
    app()
