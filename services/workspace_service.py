import difflib
import json
import os
import subprocess
import webbrowser

class WorkspaceService:
    """
    Handles saved workspaces for ATLAS

    This service stores projects,
    opens folders, launches apps,
    opens saved links, and manages
    project todo lists

    FEATURES:
        1. Save workspaces
        2. Launch projects
        3. Open project links
        4. Store project todos
        5. Match similar project names
    """

    def __init__(self, path="workspace.json"):
        self.path = path
        self.workspace = self.load()

    def load(self):
        """
        Loads saved workspaces

        Creates an empty workspace list
        if no file exists

        RETURNS:
            dict
        """

        #Return empty list if no saved file exists
        if not os.path.exists(self.path):
            return {}

        with open(self.path, "r") as file:
            return json.load(file)

    def launch(self, name):
        """
        Opens a saved workspace

        Finds the closest project name,
        opens the folder, launches apps,
        and opens saved links

        ARGS:
            name (str): Project name

        RETURNS:
            str
        """

        #Find the best matching project name
        proj_name = self.find_diff_names(name)

        # Stop if project is unknown
        if proj_name not in self.workspace:
            return f"I don't know a project called {name} yet"

        #Load the project settings
        work_s = self.workspace[proj_name]
        folder_path = work_s.get("path")
        app = work_s.get("apps", [])
        links = work_s.get("links", [])

        #Open folder in VS Code if enabled
        # Open folder in File Explorer
        if folder_path and os.path.exists(folder_path):
            if "vscode" in app:
                subprocess.Popen(f'code "{folder_path}"', shell=True)
            subprocess.Popen(f'explorer "{folder_path}"', shell=True)

        #Open saved project links
        for link in links:
            webbrowser.open(link)

        return f"Opening project {name}"

    def save(self):
        with open(self.path, "w") as file:
            json.dump(self.workspace, file, indent=4)

    def add_workspace(self, name, path, apps=None, links=None):
        """
        Saves a new workspace

        Stores the project path,
        apps, and links for later use

        ARGS:
            name (str): Project name
            path (str): Folder path
            apps (list): Apps to open
            links (list): Websites to open

        RETURNS:
            str
        """
        proj_name = self.find_diff_names(name)

        self.workspace["proj_name"] = {
            "path": path,
            "apps": apps,
            "links": links or []
        }

        self.save()
        return f"saved {name}"

    def find_projs(self):
        if not self.workspace:
            return "you do not have any projects yet"

        name = ", ".join(self.workspace.keys())
        return f"your saved projects are {name}."

    def add_todo(self, name, todo):
        proj_name = self.find_diff_names(name)

        if proj_name not in self.workspace:
            return f"project not found"

        if "todos" not in self.workspace[proj_name]:
            self.workspace[proj_name]["todo"] = []

        self.workspace[proj_name]["todos"].append(todo)
        self.save()

        return f"add list to your project"

    def get_todos(self, name):
        proj_name = self.find_diff_names(name)

        if proj_name not in self.workspace:
            return f"project not found"

        todo_list = self.workspace[proj_name].get("todos", [])

        if not todo_list:
            return f"you have nothing on this list"

        return f"Your leftover work consists of: "+"; ".join(todo_list)

    def clear_list(self, name):
        proj_name = self.find_diff_names(name)

        if proj_name not in self.workspace:
            return f"project not found"

        self.workspace[proj_name]["todos"] = []
        self.save()

        return "cleared the list"

    def find_diff_names(self, name):
        """
        Finds the closest saved project name

        Allows ATLAS to still open a project
        even if the spoken name is slightly different

        ARGS:
            name (str): Spoken project name

        RETURNS:
            str
        """

        #Clean up the spoken name
        q = name.lower().strip()

        # Check exact project name first
        if q in self.workspace:
            return q

        # Check the alternate saved names
        for key, projects in self.workspace.items():
            names = projects.get("names", [])

            for a in names:
                if q == a.lower().strip():
                    return key

        choices = []

        #Find possible name choices
        for key, projects in self.workspace.items():
            choices.append((key, key))

            for a in projects.get("names", []):
                choices.append((a.lower().strip(), key))

        # Use close matching for small mistakes
        n = []

        for item in choices:
            n.append(item[0])
        match = difflib.get_close_matches(q, n, n=1, cutoff=0.45)

        if not match:
            return None


        matched_proj = match[0]

        # Return real project key
        for d_name, r_key in choices:
            if d_name == matched_proj:
                return r_key

        return None

    def launch_coding_mode(self, name):
        launcher = self.launch(name)
        return launcher







