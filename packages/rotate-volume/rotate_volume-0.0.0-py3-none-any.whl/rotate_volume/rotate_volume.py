import cupy as cp
import math

def crop_invalid_edges(volume: cp.ndarray, 
                       valid_threshold: float = 0.5) -> cp.ndarray:
    """
    Crop invalid edge data (white edges) of 3D volume data, retain only the bounding box of valid data
    
    Args:
        volume: cupy.ndarray - 3D volume data to be cropped
        valid_threshold: float - Threshold for determining valid data (≥ this value is valid)
    
    Returns:
        cupy.ndarray - Cropped volume data with invalid edges removed, empty array if no valid data
    """
    # Find coordinates of valid data
    valid_coords = cp.where(volume >= valid_threshold)
    
    # Return empty array if no valid data
    if len(valid_coords[0]) == 0:
        return cp.array([], dtype=volume.dtype)
    
    # Calculate bounding box of valid data
    z_min = cp.min(valid_coords[0])
    z_max = cp.max(valid_coords[0])
    y_min = cp.min(valid_coords[1])
    y_max = cp.max(valid_coords[1])
    x_min = cp.min(valid_coords[2])
    x_max = cp.max(valid_coords[2])
    
    # Crop to valid bounding box
    cropped_volume = volume[z_min:z_max+1, 
                            y_min:y_max+1, 
                            x_min:x_max+1]
    
    return cropped_volume

def create_rotation_matrix(axis: str, angle_deg: float) -> cp.ndarray:
    """
    Create 3x3 rotation matrix for 3D volume rotation (inverse rotation for coordinate mapping)
    
    Args:
        axis: str - Rotation axis, options: 'x'/'y'/'z'
        angle_deg: float - Rotation angle (in degrees)
    
    Returns:
        cp.ndarray - 3x3 rotation matrix (float32)
    """
    if axis not in ['x', 'y', 'z']:
        raise ValueError("Rotation axis can only be 'x'/'y'/'z'")
    
    # Convert angle from degrees to radians
    angle_rad = cp.radians(angle_deg)
    cos_a = cp.cos(angle_rad)
    sin_a = cp.sin(angle_rad)
    
    # Initialize identity matrix
    rot_matrix = cp.eye(3, dtype=cp.float32)
    
    # Update rotation matrix based on specified axis
    if axis == 'x':
        rot_matrix[1, 1] = cos_a
        rot_matrix[1, 2] = sin_a
        rot_matrix[2, 1] = -sin_a
        rot_matrix[2, 2] = cos_a
    elif axis == 'y':
        rot_matrix[0, 0] = cos_a
        rot_matrix[0, 2] = -sin_a
        rot_matrix[2, 0] = sin_a
        rot_matrix[2, 2] = cos_a
    elif axis == 'z':
        rot_matrix[0, 0] = cos_a
        rot_matrix[0, 1] = sin_a
        rot_matrix[1, 0] = -sin_a
        rot_matrix[1, 1] = cos_a
    
    return rot_matrix

def rotate_volume(volume: cp.ndarray, 
                  rot_matrix: cp.ndarray,
                  valid_threshold: float = 0.5) -> cp.ndarray:
    """
    CuPy-accelerated volume rotation function that rotates around the center, resamples, 
    automatically crops invalid edge data (0), and retains all valid data (1)
    
    Args:
        volume: cupy.ndarray - 3D volume data (shape=(depth, height, width)) with values ranging from 0 to 1
        rot_matrix: cp.ndarray - 3 * 3 maxtrix to describe the rotation
        valid_threshold: float - Threshold for determining valid data, values ≥ this threshold are considered valid 
                                (default 0.5, suitable for 0/1 data)
    
    Returns:
        cupy.ndarray - 3D volume data after rotation, resampling and cropping of invalid edges
    """
    # ===================== Input Validation =====================
    if volume.ndim != 3:
        raise ValueError("Input must be a 3D CuPy array")
    if cp.min(volume) < 0 or cp.max(volume) > 1:
        raise ValueError("Volume data values must be between 0 and 1")
    
    # ===================== Step 1: Crop Invalid Edges of Original Data =====================
    # Use the new crop function to get valid sub-volume (maintain original timer name)
    valid_volume = crop_invalid_edges(volume, valid_threshold)
    if valid_volume.size == 0:
        return valid_volume  # Return empty array if no valid data
    orig_depth, orig_height, orig_width = valid_volume.shape
    
    # ===================== Key Improvement: Create √3x Enlarged Canvas and Center Valid Data =====================
    # √3 ≈ 1.732, ensuring data does not go out of bounds after rotation
    scale_factor = math.sqrt(3)
    # Calculate enlarged dimensions (rounded up to integer)
    new_depth = math.ceil(orig_depth * scale_factor)
    new_height = math.ceil(orig_height * scale_factor)
    new_width = math.ceil(orig_width * scale_factor)
    
    # Create empty enlarged canvas
    enlarged_volume = cp.zeros((new_depth, new_height, new_width), dtype=valid_volume.dtype)
    
    # Calculate center position of valid data in the enlarged canvas
    z_offset = (new_depth - orig_depth) // 2
    y_offset = (new_height - orig_height) // 2
    x_offset = (new_width - orig_width) // 2
    
    # Place valid data in the center of the enlarged canvas
    enlarged_volume[z_offset:z_offset+orig_depth,
                    y_offset:y_offset+orig_height,
                    x_offset:x_offset+orig_width] = valid_volume
    
    # Update to enlarged dimensions
    depth, height, width = enlarged_volume.shape
    
    # ===================== Step 2: Volume Rotation (Based on Enlarged Canvas) =====================
    # Calculate center of the enlarged canvas
    center = cp.array([(depth-1)/2, (height-1)/2, (width-1)/2], dtype=cp.float32)
    
    # Generate grid coordinates of the enlarged canvas
    z_coords = cp.arange(depth, dtype=cp.float32)
    y_coords = cp.arange(height, dtype=cp.float32)
    x_coords = cp.arange(width, dtype=cp.float32)
    z_grid, y_grid, x_grid = cp.meshgrid(z_coords, y_coords, x_coords, indexing='ij')
    coords = cp.stack([z_grid, y_grid, x_grid], axis=-1)  # (depth, height, width, 3)
    
    # Coordinate transformation: centerization -> inverse rotation -> coordinate restoration
    coords_centered = coords - center[None, None, None, :]
    coords_rotated = cp.matmul(coords_centered, rot_matrix.T)
    coords_original = coords_rotated + center[None, None, None, :]
    
    # Separate coordinates for each dimension
    z_ori = coords_original[..., 0]
    y_ori = coords_original[..., 1]
    x_ori = coords_original[..., 2]
    
    # ===================== Step 3: Linear Interpolation Resampling =====================
    # Calculate interpolation integer coordinates and weights
    z_floor = cp.floor(z_ori).astype(cp.int32)
    y_floor = cp.floor(y_ori).astype(cp.int32)
    x_floor = cp.floor(x_ori).astype(cp.int32)
    z_ceil = z_floor + 1
    y_ceil = y_floor + 1
    x_ceil = x_floor + 1
    
    # Interpolation weights
    z_weight = z_ori - z_floor
    y_weight = y_ori - y_floor
    x_weight = x_ori - x_floor
    
    # Boundary mask: only process coordinates within the enlarged canvas
    mask = (
        (z_floor >= 0) & (z_ceil < depth) &
        (y_floor >= 0) & (y_ceil < height) &
        (x_floor >= 0) & (x_ceil < width)
    )
    
    # Initialize rotated data
    rotated_volume = cp.zeros_like(enlarged_volume, dtype=enlarged_volume.dtype)
    
    # Calculate values of valid regions using linear interpolation
    if cp.any(mask):
        v000 = enlarged_volume[z_floor[mask], y_floor[mask], x_floor[mask]]
        v001 = enlarged_volume[z_floor[mask], y_floor[mask], x_ceil[mask]]
        v010 = enlarged_volume[z_floor[mask], y_ceil[mask], x_floor[mask]]
        v011 = enlarged_volume[z_floor[mask], y_ceil[mask], x_ceil[mask]]
        v100 = enlarged_volume[z_ceil[mask], y_floor[mask], x_floor[mask]]
        v101 = enlarged_volume[z_ceil[mask], y_floor[mask], x_ceil[mask]]
        v110 = enlarged_volume[z_ceil[mask], y_ceil[mask], x_floor[mask]]
        v111 = enlarged_volume[z_ceil[mask], y_ceil[mask], x_ceil[mask]]
        
        # 3D linear interpolation
        c00 = v000 * (1 - x_weight[mask]) + v001 * x_weight[mask]
        c01 = v010 * (1 - x_weight[mask]) + v011 * x_weight[mask]
        c10 = v100 * (1 - x_weight[mask]) + v101 * x_weight[mask]
        c11 = v110 * (1 - x_weight[mask]) + v111 * x_weight[mask]
        c0 = c00 * (1 - y_weight[mask]) + c01 * y_weight[mask]
        c1 = c10 * (1 - y_weight[mask]) + c11 * y_weight[mask]
        rotated_volume[mask] = c0 * (1 - z_weight[mask]) + c1 * z_weight[mask]
    
    # Ensure values remain in the 0~1 range
    rotated_volume = cp.clip(rotated_volume, 0.0, 1.0)
    
    # ===================== Step 4: Crop Invalid Edges of Rotated Data =====================
    # Reuse the crop function to remove invalid edges of rotated data
    cropped_volume = crop_invalid_edges(rotated_volume, valid_threshold)
    
    return cropped_volume