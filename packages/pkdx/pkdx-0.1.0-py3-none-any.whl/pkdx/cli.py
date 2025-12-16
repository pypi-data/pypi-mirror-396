import sys, click, random, json
import os
from . import __version__
from .defi import *
import importlib.resources as res
from importlib.resources import files

CONFIG_PATH = os.path.expanduser("~/.config/pkdx/config.json")
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"save_dir": os.getcwd()}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
config = load_config()
dex = files("pkdx").joinpath("pokedex.json")
img = files("pkdx").joinpath("images/thumbnails")
@click.group()
@click.version_option(__version__)
def main():
    """Simple CLI editable Pokedex. Use 'pkdx --help' for details."""
    pass

@main.command()
@click.argument("name", required=True)
def search(name):
    """Searches for a specific Pokemon. Usage: search <name>"""
    find(0,name,dex,img)

@main.command() 
@click.argument("path", required=True)
def svc(path):
    """Set the default save directory."""
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        click.echo("Invalid directory")
        return
    
    config["save_dir"] = path
    save_config(config)
    click.echo(f"Default save directory set to: {path}")

@main.command()
@click.argument("num", required=True)
def dexnum(num):
    """Searches for the corresponding ID number from the dex. Usage: dexnum <ID> <region>"""
    find(1,num,dex,img)
@main.command()
@click.option("-t",is_flag=True,default=False,help="Translates the name to other languages for metadata")
@click.option("-v",is_flag=True,default=False,help="Write even more info about the Pokemon")
@click.option("-g",is_flag=True,default=False,help="Randomly generates statistics for the Pokemon")
def mkpk(t,v,g):
    """Makes a new pokemon. Usage: mkpk [-t][-v][-g]"""
    mkpkmn(dex,t,v,g)
@main.command()
@click.argument("path",required=True)
@click.argument("name",required=True)
def mkimg(path,name):
    """Adds an image to the path. Usage mkimg </path/to/file.png> <name>"""
    mkImage(path,name,dex,img)
@main.command()
@click.argument("name", required=True)
def look(name):
    """Shows an image of the pokemon. Usage: look <name>"""
    imgSearch(name,dex,img)
if __name__ == "__main__":
    main()
