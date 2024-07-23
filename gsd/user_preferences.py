from pydantic import BaseModel
import pathlib, os, sys, platform

class UserPreferences(BaseModel):
    selected_tool: int = 0
    dark_mode: bool = False
    recent_workspaces: list[str] = []

    def save(self):
        file_path = self.get_user_settings_path()
        path = pathlib.Path(file_path)
        if not path.parent.exists():
            path.parent.mkdir(exist_ok=True)

        with open(path, 'w') as f:
            f.write(self.model_dump_json(indent=2))

    @staticmethod
    def get_user_settings_path():
        if platform.system() == 'Windows':
            path = os.getenv('APPDATA')
            return os.path.join(path, 'gsd', 'user_preferences.json')
        else:
            raise ValueError(f'GSD is not currently available on the {platform.system()} operating system.')
    
    
    @staticmethod
    def load():
        path = pathlib.Path(UserPreferences.get_user_settings_path())
        if not path.exists():
            user_prefs = UserPreferences()
            user_prefs.save()
        else:
            with open(path, 'r') as f:
                json_txt = f.read()
            user_prefs = UserPreferences.model_validate_json(json_txt)
        return user_prefs
    
    def add_recent_workspace(self, path):
        if path in self.recent_workspaces:
            self.recent_workspaces.remove(path)
        self.recent_workspaces.insert(0, path)
        self.save()


