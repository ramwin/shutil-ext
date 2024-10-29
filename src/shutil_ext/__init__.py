# SPDX-FileCopyrightText: 2024-present Xiang Wang <ramwin@qq.com>
#
# SPDX-License-Identifier: MIT


import os
import datetime
import shutil
from typing import List

from pathlib import Path
from duration2.tasks import ThresholdTask


def remove(path: Path) -> None:
    """
    remove the path, no matter it was a file or directory
    """
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def keep_recent(path: Path, max_keep=128, max_delete=128) -> List[Path]:
    """
    delete the file or directory in path, until `max_delete` file/directory was deleted
    or only `max_keep` file/directory exists
    return the deleted path
    """
    max_result_cnt = max_keep + max_delete
    results = []
    for index, f in enumerate(path.iterdir()):
        if index >= max_result_cnt:
            break
        results.append(f)
    results.sort(key=lambda x: x.stat().st_ctime)
    deleted_path = results[:-max_keep]
    for to_delete_path in deleted_path:
        remove(to_delete_path)
    return deleted_path


class RecentFileKeeper:
    """
    keep the file or directory in path no more than `max_count`.
    The timeout parameter was added in order to prevent the os scan the directory too frequently.
    """

    def __init__(self, path: Path, timeout=10, max_keep=128, max_delete=128):
        self.threshold = ThresholdTask(timeout=timeout)
        self.path = path
        self.max_keep = max_keep
        self.max_delete = max_delete

    def run(self):
        if self.threshold.run():
            keep_recent(self.path, self.max_keep, self.max_delete)
