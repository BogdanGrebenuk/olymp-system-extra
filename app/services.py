import random
import re
import string

from rope.base.project import Project
from rope.refactor.rename import Rename


class CodeNormalizer:

    def __init__(self, project_root):
        self._project_root = project_root

    def normalize(self, code, solution_id):
        variable_names = set(re.findall(r'([a-zA-Z_$][a-zA-Z_$0-9]*)\s*=', code))
        new_variable_names_prepared = False
        new_variable_names_info = {}
        while not new_variable_names_prepared:
            new_variable_names_info = {
                var_name: ''.join(random.choice(string.ascii_uppercase) for _ in range(1))
                for var_name in variable_names
            }
            if len(variable_names) == len(set(new_variable_names_info.values())):
                new_variable_names_prepared = True

        code_dir_path = self._project_root + '/code'
        solution_filename = f'solution_{solution_id}.py'
        solution_path = f'/{solution_filename}'
        with open(code_dir_path + solution_path, 'w') as file:
            file.write(code)

        project = Project(code_dir_path)
        example_module = project.find_module(f'solution_{solution_id}')

        for var_name, new_var_name in new_variable_names_info.items():
            with open(code_dir_path + solution_path) as file:
                file_content = file.read()
            var_offset = file_content.find(var_name)
            try:
                changes = Rename(project, example_module, var_offset).get_changes(new_var_name)
                project.do(changes)
            except Exception as e:
                pass

        project.close()

        with open(code_dir_path + solution_path) as file:
            file_content = file.read()
        return file_content
