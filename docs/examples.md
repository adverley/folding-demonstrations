# Code examples

Code examples on how to use the _folding_demonstrations_ API can be found [here](https://github.com/adverley/folding-demonstrations/tree/master/folding_demonstrations/examples).

Installation instructions are available in the [readme](https://github.com/adverley/folding-demonstrations) of the git project.
## Scenario 1 - query RGB images from one perspective
```
from folding_demonstrations.dataset import FoldingDemonstrationDataSet

# Set to the directory where the folding demonstrations dataset is stored
home_dir = '/media/data/folding_data_output'

# Load the data
dataset = FoldingDemonstrationDataSet(home_dir, perspectives: Tuple = ('left'),
                 rgb=True, depth=False, pose=False, subtask=False, reward=False)

# Iterate over data and query available information
for demonstration in dataset:
    for frame in demonstration:
        rgb = frame['left']['rgb']
        
        # Do something with the RGB image 
```

## Scenario 2 - query wrist pose estimation from folding sub-task only
```
from folding_demonstrations.dataset import FoldingDemonstrationDataSet

# Set to the directory where the folding demonstrations dataset is stored
home_dir = '/media/data/folding_data_output'

# Load the data
dataset = FoldingDemonstrationDataSet(home_dir, perspectives: Tuple = ('right'),
                 rgb=False, depth=False, pose=True, subtask=True, reward=False)

minimum_score = 0.5
# Iterate over data and query available information
for demonstration in dataset:
    for frame in demonstration:
        if frame['subtask'] == 'folding':
            pose = frame['right']['pose']
            if pose.confidence >= minimum_score:
                LWrist_xy = pose['LWrist'][0:2]
                RWrist_xy = pose['RWrist'][0:2]
        
             # Do something with the pose data  
```