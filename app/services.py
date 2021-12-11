import random
import re
import string
from collections import namedtuple
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
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


ChangesInfo = namedtuple('ChangesInfo', ['files_changed', 'insertions', 'deletions'])
CommitsInfo = namedtuple('CommitsInfo', ['changes', 'timestamp'])
HoursRange = namedtuple('HoursRange', ['start', 'end'])
LOCAL_TZ = pytz.timezone('Europe/Kiev')


class ManagementAnalyzer:

    def create_plot(self, file_path, raw_be_git_info, raw_fe_git_info, event_started_at, event_ended_at):
        be_commits_info = self._get_commits_info(raw_be_git_info)
        fe_commits_info = self._get_commits_info(raw_fe_git_info)
        development_hours_range = self._get_development_hours_range(
            event_started_at, event_ended_at, be_commits_info, fe_commits_info
        )
        be_development_info = self._get_development_info(be_commits_info, development_hours_range)
        fe_development_info = self._get_development_info(fe_commits_info, development_hours_range)

        x = np.array(range(1, len(development_hours_range) + 1))
        be_values = [be_development_info[i - 1] for i in x]
        fe_values = [fe_development_info[i - 1] for i in x]

        plt.rcParams["figure.figsize"] = (16, 8)

        fig, ax = plt.subplots()
        width = 0.3
        back_bars = ax.bar(x + width / 2, be_values, width, label='Backend')
        front_bars = ax.bar(x - width / 2, fe_values, width, label='Frontend')

        ax.set_xticks(x)
        ax.set_ylabel('Amount of lines changed')
        ax.set_xlabel('Hour')
        ax.legend()

        fig.tight_layout()

        plt.savefig(file_path)

    def _get_commits_info(self, raw_be_git_info):
        content = raw_be_git_info.strip().split('\n\n')
        temp = []
        for raw_commit_info in content:
            raw_commit_info = raw_commit_info.strip().split('\n')
            commit_timestamp, *_, commit_changes = raw_commit_info
            files_changed_search = re.search(r'(\d+) files? change', commit_changes)
            insertions_search = re.search(r'(\d+) insertion', commit_changes)
            deletion_search = re.search(r'(\d+) deletion', commit_changes)
            if files_changed_search:
                files_changed = int(files_changed_search.group(1))
            else:
                files_changed = 0
            if insertions_search:
                insertions = int(insertions_search.group(1))
            else:
                insertions = 0
            if deletion_search:
                deletions = int(deletion_search.group(1))
            else:
                deletions = 0
            temp.append(CommitsInfo(ChangesInfo(files_changed, insertions, deletions), int(commit_timestamp)))
        return temp

    def _get_development_hours_range(self, event_start_dt, event_end_dt, first_repo_commits_info, second_repo_commits_info):
        event_start_dt = datetime.fromisoformat(event_start_dt).replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ).replace(
            hour=12)
        event_end_dt = datetime.fromisoformat(event_end_dt).replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ).replace(
            hour=12)
        first_commit_dt = get_datetime_from_timestamp(min(
            first_repo_commits_info[-1],
            second_repo_commits_info[-1],
            key=lambda info: info.timestamp
        ).timestamp)
        last_commit_dt = get_datetime_from_timestamp(max(
            first_repo_commits_info[0],
            second_repo_commits_info[0],
            key=lambda info: info.timestamp
        ).timestamp)

        if event_start_dt < first_commit_dt:
            first_commit_dt = event_start_dt

        if event_end_dt > last_commit_dt:
            last_commit_dt = event_end_dt

        start_of_range = first_commit_dt.replace(minute=0, second=0)
        end_of_range = last_commit_dt.replace(minute=0, second=0) + timedelta(hours=1)

        range_of_development_hours = []
        current = start_of_range
        while current < end_of_range:
            temp = current
            current = current + timedelta(hours=1)
            range_of_development_hours.append(HoursRange(temp, current))
        return range_of_development_hours

    def _get_development_info(self, commits_info, development_hours_range):
        development_info = {}
        for i in range(len(development_hours_range)):
            hours_range = development_hours_range[i]

            development_info[i] = 0

            for commit_info in commits_info:
                commit_dt = get_datetime_from_timestamp(commit_info.timestamp)
                if commit_dt >= hours_range.start and commit_dt < hours_range.end:
                    development_info[i] += commit_info.changes.insertions + commit_info.changes.deletions
        return development_info


def get_datetime_from_timestamp(timestamp):
    dt = datetime.utcfromtimestamp(timestamp)
    dt = dt.replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
    return dt
