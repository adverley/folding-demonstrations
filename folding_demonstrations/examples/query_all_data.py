import random
import time

from folding_demonstrations.dataset import FoldingDemonstrationDataSet


def main(home_dir):
    # Load the data
    dataset = FoldingDemonstrationDataSet(home_dir)
    # Iterate over data and query available information
    for demonstration in dataset:
        random_frame_nr = random.randint(0, len(demonstration) - 1)
        info = demonstration[random_frame_nr]
        rgb_imgs = info['left']['rgb'], info['middle']['rgb'], info['right']['rgb']
        rgb_imgs[0].show()
        depth_imgs = info['left']['depth'], info['middle']['depth'], info['right']['depth']
        depth_imgs[1].show()
        subtask = info['subtask']
        reward = info['reward']
        pose = info['left']['pose']
        nose_x, nose_y, nose_confidence = pose['Nose']

        time.sleep(3)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Videos to images')
    parser.add_argument('home_dir', type=str, help='Home directory where video dataset is stored')
    args = parser.parse_args()
    main(args.home_dir)
