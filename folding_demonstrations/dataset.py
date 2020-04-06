import json
import os
from typing import Tuple

from PIL import Image

from folding_demonstrations.utils import all_directories_in


class FoldingDemonstrationDataSet:
    """
    Represents all folding demonstrations in the dataset.
    A single demonstration consists of a FoldingDemonstrationSample which wraps the available data of a sample.
    """

    def __init__(self, home_dir: str,
                 perspectives: Tuple = ('left', 'middle', 'right'),
                 rgb: bool = True, depth: bool = True,
                 pose: bool = True, subtask: bool = True, reward: bool = True) -> None:
        """

        :param home_dir: directory where the downloaded video folding demonstration dataset is stored
        :param perspectives: tuple indicating which perspectives to use. only left, middle, right allowed.
        :param rgb: query rgb images?
        :param depth: query depth frames?
        :param pose: query pose information?
        :param subtask: query subtask label?
        :param reward: query reward, i.e. the amount of executed folds in the cloth?
        """
        self.raise_error_on_faulty_home_dir(home_dir)
        self.home_dir = home_dir
        self.perspectives = perspectives
        self.rgb = rgb
        self.depth = depth
        self.pose = pose
        self.subtask = subtask
        self.reward = reward

        self.sample_ids = all_directories_in(self.home_dir)
        self._sample_nr = 0

    def raise_error_on_faulty_home_dir(self, home_dir: str):
        """ Checks for errors in the specified home directory of the data """
        if not os.path.isdir(home_dir) and not os.path.exists(home_dir):
            raise ValueError(f'WRONG HOME_DIR: Path "{home_dir}" is not a valid path')

        if len(all_directories_in(home_dir)) == 0:
            raise ValueError(f'WRONG HOME_DIR: Path "{home_dir}" exists but contains no files!')

        # check first sample
        for perspective in ('left', 'middle', 'right'):
            for dtype in ('rgb', 'depth'):
                d = os.path.join(home_dir, '0', perspective, dtype)
                if not os.path.isdir(d):
                    raise ValueError(f'WRONG HOME_DIR: path "{d}" should exist. Is all data downloaded?')

        d = os.path.join(home_dir, '0', 'annotations.json')
        if not os.path.isfile(d):
            raise ValueError(f'WRONG HOME_DIR: file "{d}" does not exist. Is all data downloaded?')

    def __len__(self):
        return len(self.sample_ids)

    def __iter__(self):
        return self

    def __next__(self):
        if self._sample_nr < len(self):
            result = self.__getitem__(self.sample_ids[self._sample_nr])
            self._sample_nr += 1
            return result

        raise StopIteration

    def __getitem__(self, sample_id: int):
        """
        Makes an object of this class indexable
        :param sample_id: int
        :return: a FoldingDemonstrationSample which can be indexed and contains all the information specified in the constructor of the current class
        """
        if str(sample_id) in self.sample_ids:
            sample = FoldingDemonstrationSample(self.home_dir, sample_id, self.perspectives, self.rgb, self.depth,
                                                self.pose, self.subtask, self.reward)

            return sample
        else:
            raise IndexError(f'Sample with ID "{sample_id}" does not exist in path {self.home_dir}')


class FoldingDemonstrationSample:
    """
    Represents all captured frames in a folding demonstration
    """

    def __init__(self, home_dir: str, sample_id: int, perspectives: Tuple,
                 rgb: bool, depth: bool, pose: bool, subtask: bool, reward: bool):
        self.home_dir = home_dir
        self.idx = sample_id
        self.sample_dir = os.path.join(self.home_dir, f'{sample_id}')
        self.annotations = self._load_annotations(self.sample_dir)
        self.perspectives = perspectives
        self.rgb = rgb
        self.depth = depth
        self.pose = pose
        self.subtask = subtask
        self.reward = reward

        self.poses = None
        if self.pose:
            self.poses = self._load_poses(self.sample_dir)

        self._frame_nr = 0

    @staticmethod
    def _load_annotations(sample_dir: str):
        filename = 'annotations.json'
        fp = os.path.join(sample_dir, filename)
        with open(fp, 'r') as f:
            annotations = json.load(f)

        annotations = FoldingDemonstrationSample._annotations_keys_to_ints(annotations)

        return annotations

    @staticmethod
    def _annotations_keys_to_ints(annotations: dict):
        """
        The annotations.json files contains two inner dictionaries of which the keys are ints stored as strings.
        This method converts them to ints so they are easy to index.
        """
        if 'nb_folds' in annotations.keys():
            reward_changes = annotations['nb_folds']
            reward_changes_new = {}
            for k, v in reward_changes.items():
                reward_changes_new[int(k)] = v

            annotations['nb_folds'] = reward_changes_new
        else:
            print(f'WARNING: could not find key "nb_folds" in annotations. Do you have the latest version of the dataset?')

        if 'subtask_changes' in annotations.keys():
            step_changes = annotations['subtask_changes']
            step_changes_new = {}
            for k, v in step_changes.items():
                step_changes_new[int(k)] = v

            annotations['subtask_changes'] = step_changes_new
        else:
            print(f'WARNING: could not find key "subtask_changes" in annotations. Do you have the latest version of the dataset?')

        return annotations

    def _load_poses(self, sample_dir: str):
        perspective_to_poses = {}
        filename = 'pose.json'
        for perspective in self.perspectives:
            fp = os.path.join(sample_dir, perspective, filename)
            with open(fp, 'r') as f:
                poses = json.load(f)
                perspective_to_poses[perspective] = poses

        return perspective_to_poses

    def __len__(self):
        return self.annotations['nb_frames']

    def __iter__(self):
        return self

    def __next__(self):
        if self._frame_nr < len(self):
            result = self.__getitem__(self._frame_nr)
            self._frame_nr += 1
            return result

        raise StopIteration

    def __getitem__(self, frame_idx: int):
        '''
        :param frame_idx: index of the frame of an example demonstration that is being queried
        :return: Nested dictionary containing information as specified in the constructor.
        '''
        if 0 <= frame_idx < len(self):
            sample = {}

            for perspective in self.perspectives:
                if perspective not in sample.keys():
                    sample[perspective] = {}

                if self.rgb:
                    fp = os.path.join(self.sample_dir, perspective, 'rgb', f'{frame_idx:04d}.png')
                    sample[perspective]['rgb'] = Image.open(fp)

                if self.depth:
                    fp = os.path.join(self.sample_dir, perspective, 'depth', f'{frame_idx:04d}.png')
                    sample[perspective]['depth'] = Image.open(fp)

                if self.pose:
                    sample[perspective]['pose'] = self._find_pose(frame_idx, perspective)

            if self.subtask:
                sample['subtask'] = self._find_subtask(frame_idx)

            if self.reward:
                sample['reward'] = self._find_reward(frame_idx)

            return sample

        else:
            raise IndexError(f'Frame index {frame_idx} out of bounds, it should be between [0, {len(self)}[')

    def _find_pose(self, frame_idx: int, perspective: str):
        return self.poses[perspective][str(frame_idx)]

    def _find_subtask(self, frame_idx: int):
        steps = self.annotations['subtask_changes']
        steps_frames = list(steps.keys())
        for i in range(len(steps_frames) - 1):
            current_idx = i
            next_idx = current_idx + 1

            if current_idx <= frame_idx < next_idx:
                return steps[steps_frames[current_idx]]

        return steps[steps_frames[-1]]

    def _find_reward(self, frame_idx: int):
        rewards = self.annotations['nb_folds']
        rewards_frames = list(rewards.keys())
        for i in range(len(rewards_frames) - 1):
            current_idx = i
            next_idx = current_idx + 1

            if current_idx <= frame_idx < next_idx:
                return rewards[rewards_frames[current_idx]]

        return rewards[rewards_frames[-1]]
