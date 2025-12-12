# rotate_volume
An efficient volume rotation algorithm based on Cupy.

GitHub repo: [https://github.com/GGN-2015/rotate_volume](https://github.com/GGN-2015/rotate_volume)

## Installation
```bash
pip install rotate_volume
```

## Usage
```python
import cupy as cp
from rotate_volume import rotate_volume, create_rotation_matrix

# Create test volume data, replace the data with your own 3d cupy array
# in volume data, zero means empty, one means valid voxel
test_volume = cp.ones((20, 20, 20), dtype=cp.float32)

# make rotation matrix
rotation_x   = create_rotation_matrix('x', angle_deg=10)
rotation_y   = create_rotation_matrix('y', angle_deg=20)
rotation_z   = create_rotation_matrix('z', angle_deg=30)
rotation_all = rotation_z @ rotation_y @ rotation_x

# Rotate
rotated_cropped = rotate_volume(test_volume, rotation_all)

# Verify results
print(f"Original data shape: {test_volume.shape}")
print(f"Rotated and cropped data shape: {rotated_cropped.shape}")
print(f"Original valid data count: {cp.count_nonzero(test_volume >= 0.5)}")
print(f"Rotated and cropped valid data count: {cp.count_nonzero(rotated_cropped >= 0.5)}")

# If you want to visualize the 3d data, you can use `visualize_volume`
# Use `pip install visualize_volume` to install it before using it
from visualize_volume import visualize_volume
visualize_volume(cp.asnumpy(rotated_cropped))
```
