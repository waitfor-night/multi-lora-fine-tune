import json
import requests
from InquirerPy import inquirer
from InquirerPy import validator
from InquirerPy.base import Choice
from rich import print
from rich.table import Table
from rich.box import ASCII
from typing import Dict

from .setting import url


def list_adapter(obj):
    ret = requests.get(url() + "/adapter")
    ret = json.loads(ret.text)

    table = Table(show_header=True, show_lines=True, box=ASCII)
    table.add_column("name", justify="center")
    table.add_column("type", justify="center")
    table.add_column("dir", justify="center")
    table.add_column("state", justify="center")

    obj.ret_ = []

    for item in ret:
        item = json.loads(item)
        table.add_row(item["name"], item["type"], item["path"], item["state"])
        obj.ret_.append(item["name"])

    obj.pret_ = table


def adapter_type_set(adapter_conf: Dict[str, any]):
    adapter_type = inquirer.select(
        message="type:", choices=["lora", "loraplus"]).execute()
    adapter_conf["type"] = adapter_type

    if adapter_type == "loraplus":
        lr_ratio = inquirer.number(
            message="lr_ratio:",
            float_allowed=True,
            default=8.0,
            replace_mode=True
        ).execute()
        adapter_conf["lr_ratio"] = lr_ratio

    return adapter_conf


def adapter_optimizer_set(adapter_conf: Dict[str, any]):
    optimizer = inquirer.select(
        message="optimizer:", choices=["adamw", "sgd"]).execute()
    adapter_conf["optimizer"] = optimizer

    lr = inquirer.number(
        message="learning rate:",
        float_allowed=True,
        default=3e-4,
        replace_mode=True
    ).execute()
    adapter_conf["lr"] = lr

    if optimizer == "sgd":
        momentum = inquirer.number(
            message="momentum:",
            float_allowed=True,
            default=0.0,
            replace_mode=True
        ).execute()
        adapter_conf["momentum"] = momentum
    return adapter_conf


def adapter_lr_scheduler_set(adapter_conf: Dict[str, any]):
    need_lr_scheduler = inquirer.confirm(
        message="Need learning rate scheduler:", default=False).execute()
    if not need_lr_scheduler:
        return adapter_conf

    lr_scheduler_type = inquirer.select(
        message="optimizer:", choices=["cosine"]).execute()
    adapter_conf["lrscheduler"] = lr_scheduler_type

    if lr_scheduler_type == "cosine":
        t_max = inquirer.number(
            message="maximum number of iterations:",
            replace_mode=True,
            default=100000,
        ).execute()
        adapter_conf["t_max"] = t_max

        eta_min = inquirer.number(
            message="minimum learning rate:",
            float_allowed=True,
            replace_mode=True,
            default=0.0,
        ).execute()
        adapter_conf["eta_min"] = eta_min

    return adapter_conf


def adapter_set(adapter_conf: Dict[str, any]):
    r = inquirer.number(
        message="rank:",
        default=32
    ).execute()
    adapter_conf["r"] = r

    alpha = inquirer.number(
        message="alpha:",
        default=64
    ).execute()
    adapter_conf["alpha"] = alpha

    dropout = inquirer.number(
        message="dropout:",
        float_allowed=True,
        replace_mode=True,
        default=0.05
    ).execute()
    adapter_conf["dropout"] = dropout

    adapter_conf["target_modules"] = {
        "q_proj": False,
        "k_proj": False,
        "v_proj": False,
        "o_proj": False,
        "gate_proj": False,
        "down_proj": False,
        "up_proj": False,
    }
    target_modules = inquirer.checkbox(
        message="target_modules:",
        choices=[Choice("q_proj", enabled=True),
                 Choice("k_proj", enabled=True),
                 Choice("v_proj", enabled=True),
                 Choice("o_proj", enabled=True),
                 Choice("gate_proj", enabled=False),
                 Choice("down_proj", enabled=False),
                 Choice("up_proj", enabled=False)]
    ).execute()
    for target in target_modules:
        adapter_conf["target_modules"][target] = True

    return adapter_conf


def create_adapter():
    adapter_conf = {}

    name = inquirer.text(
        message="name:",
        validate=validator.EmptyInputValidator("Input should not be empty")).execute()
    adapter_conf["name"] = name

    adapter_conf = adapter_type_set(adapter_conf)
    adapter_conf = adapter_optimizer_set(adapter_conf)
    adapter_conf = adapter_lr_scheduler_set(adapter_conf)
    adapter_conf = adapter_set(adapter_conf)

    ret = requests.post(url() + "/adapter", json=adapter_conf)

    print(json.loads(ret.text))


def help_adapter(_):
    print("Usage of adapter:")
    print("  ls")
    print("    list all the adapter.")
    print("  create")
    print("    create a new adapter.")


def do_adapter(obj, args):
    args = args.split(" ")

    if args[0] == "ls":
        list_adapter(obj)
        return print(obj.pret_)
    elif args[0] == "create":
        return create_adapter()

    help_adapter(None)
