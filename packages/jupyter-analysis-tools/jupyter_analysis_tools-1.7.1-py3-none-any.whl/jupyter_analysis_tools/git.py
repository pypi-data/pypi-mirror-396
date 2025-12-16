# -*- coding: utf-8 -*-
# git.py

import os
import subprocess
import sys


def isRepo(path):
    return os.path.exists(os.path.join(path, ".git"))


def isNBstripoutInstalled():
    out = subprocess.run(
        [sys.executable, "-m", "nbstripout", "--status"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.decode("utf-8")
    return len(out) and "not recognized" not in out


def isNBstripoutActivated():
    out = subprocess.run(
        [sys.executable, "-m", "nbstripout", "--status"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.decode("utf-8")
    return len(out) and "is installed" in out


def checkRepo():
    if not isRepo("."):
        print("Not a GIT repository.")
        return
    # is git installed?
    try:
        import git
    except ImportError:
        print("Could not load git module, is GIT installed and in PATH?")
        return
    # check the repository in detail
    from IPython.display import HTML, display

    repo = git.Repo(".")
    #    currentNB = os.path.basename(currentNBpath())
    try:
        editedOn = repo.git.show(no_patch=True, format="%cd, version %h by %cn", date="iso")
    except git.GitCommandError:
        print("Not a GIT repository.")
        return
    editedOn = editedOn.split(", ")
    opacity = 0.3  # 1.0 if repo.is_dirty() else 0.5
    display(
        HTML(
            '<div style="opacity: {opacity};">'
            "<h3>Document updated on {}</h3>"
            "<h4>({})</h4></div>".format(*editedOn, opacity=opacity)
        )
    )
    if repo.is_dirty():
        edits = repo.git.diff(stat=True)
        import re

        edits = re.sub(r" (\++)", r' <span style="color: green;">\1</span>', edits)
        edits = re.sub(r"(\+)?(-+)(\s)", r'\1<span style="color: red;">\2</span>\3', edits)
        display(
            HTML(
                '<div style="border-style: solid; border-color: darkred; border-width: 1px; '
                'padding: 0em 1em 1em 1em; margin: 1em 0em;">'
                '<h4 style="color: darkred;">There are changes in this repository:</h4>'
                "<pre>"
                + edits
                + "</pre></div>"
            )
        )
