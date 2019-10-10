import cv2
import numpy as np

from folding_demonstrations.dataset import FoldingDemonstrationDataSet


def main(home_dir, sample_id, perspective):
    dataset = FoldingDemonstrationDataSet(home_dir)
    demonstration = dataset[sample_id]
    for frame in demonstration:
        rgb = frame[perspective]['rgb']
        bgr = np.array(rgb)[..., ::-1]
        cv2.imshow('Folding sample demo', bgr)
        cv2.waitKey(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Videos to images')
    parser.add_argument('home_dir', type=str, help='Home directory where video dataset is stored')
    parser.add_argument('--sample_id', default=0, type=int, help='ID of the sample to play')
    parser.add_argument('--perspective', default='left', type=str, help='Perspective to display')
    args = parser.parse_args()
    main(args.home_dir, args.sample_id, args.perspective)
