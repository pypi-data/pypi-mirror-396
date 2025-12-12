"""Face Preprocessing Library for Face Embedding.

This module provides preprocessing functions for face images before embedding extraction.
Designed as a flexible, configurable library for various face embedding models.

Pipeline (all steps are optional and configurable):
1. Brightness normalization (gamma correction + CLAHE) - can be skipped
2. 5-point face alignment using warp affine transform - can be skipped
3. Resize to target size (112x112, 160x160, or custom)
4. RGB value normalization - can be skipped

Supported output sizes:
- 112x112 (ArcFace, MobileFaceNet)
- 160x160 (FaceNet, InceptionResNet)
- Custom sizes

Input: OpenCV image (RGB or BGR, configurable)
Output: OpenCV image at target size, normalized and aligned (RGB or BGR, configurable)
"""

import cv2
import numpy as np
import numpy.typing as npt
from typing import Optional, Tuple, Union, Literal, Dict
from dataclasses import dataclass, field
from enum import Enum


class ColorFormat(Enum):
    """Color format for input/output images."""
    RGB = "rgb"
    BGR = "bgr"


# Standard ArcFace 112x112 reference landmarks
# [left_eye, right_eye, nose_tip, left_mouth_corner, right_mouth_corner]
ARCFACE_REF_LANDMARKS = np.array([
    [38.2946, 51.6963],  # left eye
    [73.5318, 51.5014],  # right eye
    [56.0252, 71.7366],  # nose tip
    [41.5493, 92.3655],  # left mouth corner
    [70.7299, 92.2041],  # right mouth corner
], dtype=np.float32)


# Reference landmarks presets for different output sizes
# These are optimized landmark positions for each model input size
REFERENCE_LANDMARKS_PRESETS: Dict[Tuple[int, int], np.ndarray] = {
    # ArcFace, MobileFaceNet, CosFace standard
    (112, 112): ARCFACE_REF_LANDMARKS.copy(),

    # FaceNet, InceptionResNet-V1 (scaled from 112x112)
    (160, 160): np.array([
        [54.7066, 73.8519],   # left eye (38.2946 * 160/112)
        [105.0454, 73.5734],  # right eye
        [80.0360, 102.4809],  # nose tip
        [59.3561, 131.9507],  # left mouth corner
        [101.0427, 131.7201],  # right mouth corner
    ], dtype=np.float32),

    # Some models use 128x128
    (128, 128): np.array([
        [43.7651, 59.0815],   # left eye
        [84.0364, 58.8588],   # right eye
        [64.0288, 82.0132],   # nose tip
        [47.4849, 105.5606],  # left mouth corner
        [80.8342, 105.3761],  # right mouth corner
    ], dtype=np.float32),

    # VGGFace2, some ResNet models
    (224, 224): np.array([
        [76.5893, 103.3927],  # left eye
        [147.0636, 103.0028],  # right eye
        [112.0504, 143.4732],  # nose tip
        [82.9986, 184.7310],  # left mouth corner
        [141.4598, 184.4082],  # right mouth corner
    ], dtype=np.float32),
}


def get_reference_landmarks(
    output_size: Tuple[int, int],
    base_landmarks: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Get reference landmarks for a specific output size.

    If a preset exists for the output size, returns the preset.
    Otherwise, scales the base landmarks (default: 112x112 ArcFace) to the target size.

    Args:
        output_size: Target output size (width, height)
        base_landmarks: Base landmarks to scale from. If None, uses ARCFACE_REF_LANDMARKS.

    Returns:
        Reference landmarks array, shape (5, 2)
    """
    # Check if preset exists
    if output_size in REFERENCE_LANDMARKS_PRESETS:
        return REFERENCE_LANDMARKS_PRESETS[output_size].copy()

    # Scale from base landmarks
    if base_landmarks is None:
        base_landmarks = ARCFACE_REF_LANDMARKS

    base_size = (112, 112)  # Base size for ARCFACE_REF_LANDMARKS
    scale_x = output_size[0] / base_size[0]
    scale_y = output_size[1] / base_size[1]

    scaled = base_landmarks.copy()
    scaled[:, 0] *= scale_x
    scaled[:, 1] *= scale_y

    return scaled


@dataclass
class PreprocessConfig:
    """
    Configuration for face preprocessing pipeline.

    All preprocessing steps can be enabled/disabled individually for maximum flexibility.

    Example:
        >>> # Default config (all steps enabled)
        >>> config = PreprocessConfig()

        >>> # Only alignment, no brightness or RGB normalization
        >>> config = PreprocessConfig(
        ...     use_brightness_normalization=False,
        ...     use_rgb_normalization=False,
        ...     use_alignment=True
        ... )

        >>> # 160x160 output for FaceNet
        >>> config = PreprocessConfig(
        ...     output_size=(160, 160),
        ...     normalize_mean=(0.5, 0.5, 0.5),
        ...     normalize_std=(0.5, 0.5, 0.5)
        ... )

        >>> # Skip all preprocessing, just resize
        >>> config = PreprocessConfig(
        ...     use_brightness_normalization=False,
        ...     use_alignment=False,
        ...     use_rgb_normalization=False
        ... )
    """

    # ===== Output Configuration =====
    # Common: (112, 112), (160, 160), (224, 224)
    output_size: Tuple[int, int] = (112, 112)

    # ===== Color Format =====
    input_color_format: ColorFormat = ColorFormat.RGB   # Input image color format
    output_color_format: ColorFormat = ColorFormat.RGB  # Output image color format

    # ===== Step Enable/Disable Flags =====
    # Enable/disable entire brightness normalization
    use_brightness_normalization: bool = True
    # Enable/disable gamma correction (within brightness norm)
    use_gamma_correction: bool = True
    # Enable/disable CLAHE (within brightness norm)
    use_clahe: bool = True
    use_alignment: bool = True                 # Enable/disable face alignment
    # Enable/disable RGB value normalization
    use_rgb_normalization: bool = True

    # ===== Gamma Correction Parameters =====
    # Manual gamma value (1.0 = no change, <1 = brighten, >1 = darken)
    gamma: float = 1.0
    # Automatically estimate gamma based on image brightness
    auto_gamma: bool = True
    gamma_target_mean: float = 127.0  # Target mean brightness for auto gamma
    gamma_range: Tuple[float, float] = (0.5, 2.0)  # Clamp range for auto gamma

    # ===== CLAHE Parameters =====
    # Contrast limiting threshold (1.0-3.0)
    clahe_clip_limit: float = 1.5
    # Grid size for adaptive histogram
    clahe_grid_size: Tuple[int, int] = (8, 8)

    # ===== RGB Normalization Parameters =====
    normalize_mean: Tuple[float, float, float] = (
        0.5, 0.5, 0.5)  # Mean for normalization
    normalize_std: Tuple[float, float, float] = (
        0.5, 0.5, 0.5)   # Std for normalization
    normalize_to_float: bool = False  # Output float32 instead of uint8

    # ===== Alignment Parameters =====
    reference_landmarks: Optional[np.ndarray] = field(default=None, repr=False)
    # Custom reference landmarks. If None, uses preset for output_size or scales from 112x112

    # ===== Interpolation =====
    interpolation: int = cv2.INTER_LINEAR  # cv2 interpolation flag for resize/warp

    def __post_init__(self):
        """Validate and process configuration after initialization."""
        # Validate output_size
        if not isinstance(self.output_size, tuple) or len(self.output_size) != 2:
            raise ValueError(
                f"output_size must be a tuple of (width, height), got {self.output_size}")
        if self.output_size[0] <= 0 or self.output_size[1] <= 0:
            raise ValueError(
                f"output_size dimensions must be positive, got {self.output_size}")

        # Convert string color format to enum if needed
        if isinstance(self.input_color_format, str):
            self.input_color_format = ColorFormat(
                self.input_color_format.lower())
        if isinstance(self.output_color_format, str):
            self.output_color_format = ColorFormat(
                self.output_color_format.lower())

    @classmethod
    def for_arcface(cls, **kwargs) -> 'PreprocessConfig':
        """Create config preset for ArcFace/MobileFaceNet models (112x112)."""
        defaults = {
            'output_size': (112, 112),
            'normalize_mean': (0.5, 0.5, 0.5),
            'normalize_std': (0.5, 0.5, 0.5),
            'normalize_to_float': True,
        }
        defaults.update(kwargs)
        return cls(**defaults)

    @classmethod
    def for_facenet(cls, **kwargs) -> 'PreprocessConfig':
        """Create config preset for FaceNet/InceptionResNet models (160x160)."""
        defaults = {
            'output_size': (160, 160),
            'normalize_mean': (0.5, 0.5, 0.5),
            'normalize_std': (0.5, 0.5, 0.5),
            'normalize_to_float': True,
        }
        defaults.update(kwargs)
        return cls(**defaults)

    @classmethod
    def for_vggface(cls, **kwargs) -> 'PreprocessConfig':
        """Create config preset for VGGFace models (224x224)."""
        defaults = {
            'output_size': (224, 224),
            # VGGFace typically uses ImageNet normalization
            'normalize_mean': (0.485, 0.456, 0.406),
            'normalize_std': (0.229, 0.224, 0.225),
            'normalize_to_float': True,
        }
        defaults.update(kwargs)
        return cls(**defaults)

    @classmethod
    def minimal(cls, output_size: Tuple[int, int] = (112, 112), **kwargs) -> 'PreprocessConfig':
        """Create minimal config - only resize, no preprocessing."""
        defaults = {
            'output_size': output_size,
            'use_brightness_normalization': False,
            'use_alignment': False,
            'use_rgb_normalization': False,
        }
        defaults.update(kwargs)
        return cls(**defaults)


def gamma_correction(
    image: npt.NDArray[np.uint8],
    gamma: float = 1.0
) -> npt.NDArray[np.uint8]:
    """
    Apply gamma correction to adjust image brightness.

    Gamma < 1.0: Brightens dark images
    Gamma > 1.0: Darkens bright images
    Gamma = 1.0: No change

    Args:
        image: Input RGB image (uint8)
        gamma: Gamma value for correction

    Returns:
        Gamma-corrected RGB image (uint8)
    """
    if gamma == 1.0:
        return image

    # Build lookup table for efficiency
    inv_gamma = 1.0 / gamma
    table = np.array([
        ((i / 255.0) ** inv_gamma) * 255
        for i in np.arange(256)
    ]).astype(np.uint8)

    return cv2.LUT(image, table)


def estimate_gamma(image: npt.NDArray[np.uint8], target_mean: float = 127.0) -> float:
    """
    Estimate optimal gamma value based on image brightness.

    Args:
        image: Input RGB image
        target_mean: Target mean brightness (0-255)

    Returns:
        Estimated gamma value
    """
    # Convert to grayscale for brightness analysis
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    current_mean = np.mean(gray)

    # Avoid division by zero and extreme values
    if current_mean < 1:
        current_mean = 1
    if current_mean > 254:
        current_mean = 254

    # Calculate gamma: gamma = log(target/255) / log(current/255)
    # Simplified: gamma = log(target_normalized) / log(current_normalized)
    gamma = np.log(target_mean / 255.0) / np.log(current_mean / 255.0)

    # Clamp gamma to reasonable range
    gamma = np.clip(gamma, 0.5, 2.0)

    return float(gamma)


def apply_clahe(
    image: npt.NDArray[np.uint8],
    clip_limit: float = 1.5,
    grid_size: Tuple[int, int] = (8, 8)
) -> npt.NDArray[np.uint8]:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to RGB image.

    CLAHE is applied to the L channel in LAB color space to preserve colors
    while enhancing local contrast.

    Args:
        image: Input RGB image (uint8)
        clip_limit: Threshold for contrast limiting (lower = more subtle)
        grid_size: Size of grid for histogram equalization

    Returns:
        CLAHE-enhanced RGB image (uint8)
    """
    # Convert RGB to LAB
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

    # Split channels
    l_channel, a_channel, b_channel = cv2.split(lab)

    # Apply CLAHE to L channel only
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    l_enhanced = clahe.apply(l_channel)

    # Merge channels back
    lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])

    # Convert back to RGB
    result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

    return result


def normalize_brightness(
    image: npt.NDArray[np.uint8],
    gamma: float = 1.0,
    auto_gamma: bool = True,
    use_gamma: bool = True,
    use_clahe: bool = True,
    clahe_clip_limit: float = 1.5,
    clahe_grid_size: Tuple[int, int] = (8, 8),
    gamma_target_mean: float = 127.0,
    gamma_range: Tuple[float, float] = (0.5, 2.0)
) -> npt.NDArray[np.uint8]:
    """
    Normalize image brightness using gamma correction and/or CLAHE.

    Each step can be individually enabled/disabled:
    1. Gamma correction (auto or manual) - controlled by use_gamma
    2. CLAHE for local contrast enhancement - controlled by use_clahe

    Args:
        image: Input RGB image (uint8)
        gamma: Manual gamma value (ignored if auto_gamma=True)
        auto_gamma: Automatically estimate gamma based on image brightness
        use_gamma: Enable/disable gamma correction step
        use_clahe: Enable/disable CLAHE step
        clahe_clip_limit: CLAHE clip limit (1.0-3.0, lower = more subtle)
        clahe_grid_size: CLAHE grid size
        gamma_target_mean: Target mean brightness for auto gamma estimation
        gamma_range: (min, max) clamp range for auto gamma

    Returns:
        Brightness-normalized RGB image (uint8)
    """
    result = image

    # Step 1: Gamma correction
    if use_gamma:
        if auto_gamma:
            gamma = estimate_gamma(image, gamma_target_mean)
            gamma = np.clip(gamma, gamma_range[0], gamma_range[1])
        result = gamma_correction(result, gamma)

    # Step 2: CLAHE
    if use_clahe:
        result = apply_clahe(result, clahe_clip_limit, clahe_grid_size)

    return result


def estimate_affine_matrix(
    src_landmarks: npt.NDArray[np.float32],
    dst_landmarks: npt.NDArray[np.float32]
) -> npt.NDArray[np.float64]:
    """
    Estimate similarity transform matrix using least squares.

    This computes a 2x3 affine matrix for cv2.warpAffine that includes:
    - Translation
    - Rotation
    - Uniform scaling

    Args:
        src_landmarks: Source landmarks, shape (N, 2)
        dst_landmarks: Destination landmarks, shape (N, 2)

    Returns:
        2x3 affine transformation matrix
    """
    num_pts = src_landmarks.shape[0]

    # Build system of equations for similarity transform
    # [x'] = [s*cos(θ)  -s*sin(θ)  tx] [x]
    # [y']   [s*sin(θ)   s*cos(θ)  ty] [y]
    #                                  [1]

    # Reshape for solving
    src_x = src_landmarks[:, 0]
    src_y = src_landmarks[:, 1]
    dst_x = dst_landmarks[:, 0]
    dst_y = dst_landmarks[:, 1]

    # Build matrix A and vector b for least squares: Ax = b
    # Parameters: [a, b, tx, ty] where transformation is:
    # x' = a*x - b*y + tx
    # y' = b*x + a*y + ty

    A = np.zeros((2 * num_pts, 4), dtype=np.float64)
    b = np.zeros(2 * num_pts, dtype=np.float64)

    for i in range(num_pts):
        A[2*i] = [src_x[i], -src_y[i], 1, 0]
        A[2*i + 1] = [src_y[i], src_x[i], 0, 1]
        b[2*i] = dst_x[i]
        b[2*i + 1] = dst_y[i]

    # Solve using least squares
    params, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    a, b_val, tx, ty = params

    # Build 2x3 affine matrix
    affine_matrix = np.array([
        [a, -b_val, tx],
        [b_val, a, ty]
    ], dtype=np.float64)

    return affine_matrix


def align_face_5point(
    image: npt.NDArray[np.uint8],
    landmarks: Optional[npt.NDArray[np.float32]] = None,
    output_size: Tuple[int, int] = (112, 112),
    reference_landmarks: Optional[npt.NDArray[np.float32]] = None,
    interpolation: int = cv2.INTER_LINEAR
) -> npt.NDArray[np.uint8]:
    """
    Align face using 5-point landmarks with warp affine transform.

    The 5 landmarks expected are:
    - Left eye center
    - Right eye center
    - Nose tip
    - Left mouth corner
    - Right mouth corner

    If landmarks are not provided, the image is simply resized to output_size.

    Args:
        image: Input RGB image (uint8), cropped face
        landmarks: 5 facial landmarks, shape (5, 2) or (10,) flattened
                   Order: [left_eye, right_eye, nose, left_mouth, right_mouth]
        output_size: Output image size (width, height), default (112, 112)
        reference_landmarks: Custom reference landmarks for alignment.
                            If None, uses preset for output_size or scales from 112x112
        interpolation: cv2 interpolation flag (default: cv2.INTER_LINEAR)

    Returns:
        Aligned face image of size output_size (uint8)
    """
    if landmarks is None:
        # No landmarks provided, just resize
        return cv2.resize(image, output_size, interpolation=interpolation)

    # Ensure landmarks are in correct shape
    landmarks = np.array(landmarks, dtype=np.float32)
    if landmarks.shape == (10,):
        landmarks = landmarks.reshape(5, 2)

    if landmarks.shape != (5, 2):
        raise ValueError(
            f"Expected landmarks shape (5, 2), got {landmarks.shape}")

    # Get reference landmarks for output size
    if reference_landmarks is None:
        dst_landmarks = get_reference_landmarks(output_size)
    else:
        dst_landmarks = np.array(reference_landmarks, dtype=np.float32)

    # Estimate similarity transform
    affine_matrix = estimate_affine_matrix(landmarks, dst_landmarks)

    # Apply warp affine
    aligned = cv2.warpAffine(
        image,
        affine_matrix,
        output_size,
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0)
    )

    return aligned


def normalize_rgb(
    image: npt.NDArray[np.uint8],
    mean: Tuple[float, float, float] = (0.5, 0.5, 0.5),
    std: Tuple[float, float, float] = (0.5, 0.5, 0.5),
    to_float: bool = False
) -> Union[npt.NDArray[np.uint8], npt.NDArray[np.float32]]:
    """
    Normalize RGB values of the image.

    Two modes of operation:
    1. to_float=False (default): Returns uint8 image with values remapped
    2. to_float=True: Returns float32 image normalized to [-1, 1] or [0, 1]

    The normalization formula is:
        normalized = (pixel / 255.0 - mean) / std

    For ArcFace models, typical normalization is mean=0.5, std=0.5
    which maps [0, 255] to [-1, 1]

    Args:
        image: Input RGB image (uint8)
        mean: Mean values for each channel (R, G, B)
        std: Standard deviation for each channel (R, G, B)
        to_float: If True, return float32; if False, return uint8

    Returns:
        Normalized image (float32 if to_float=True, else uint8)
    """
    # Convert to float
    img_float = image.astype(np.float32) / 255.0

    # Apply normalization per channel
    mean = np.array(mean, dtype=np.float32).reshape(1, 1, 3)
    std = np.array(std, dtype=np.float32).reshape(1, 1, 3)

    normalized = (img_float - mean) / std

    if to_float:
        return normalized
    else:
        # Convert back to uint8 range [0, 255]
        # First denormalize to [0, 1] range for uint8 output
        # Note: This is mainly for visualization, for model inference use to_float=True
        normalized_clipped = np.clip(normalized, -1, 1)
        result = ((normalized_clipped + 1) / 2 * 255).astype(np.uint8)
        return result


def preprocess_face(
    image: npt.NDArray[np.uint8],
    landmarks: Optional[npt.NDArray[np.float32]] = None,
    config: Optional[PreprocessConfig] = None
) -> Union[npt.NDArray[np.uint8], npt.NDArray[np.float32]]:
    """
    Complete face preprocessing pipeline for embedding extraction.

    All pipeline steps are configurable and can be skipped:
    1. Color format conversion (BGR <-> RGB if needed)
    2. Brightness normalization (gamma correction + CLAHE) - optional
    3. 5-point face alignment using warp affine - optional
    4. Resize to target size
    5. RGB value normalization - optional
    6. Output color format conversion (if needed)

    Args:
        image: Input image (uint8), color format specified in config.input_color_format
        landmarks: Optional 5-point facial landmarks for alignment
                   Shape: (5, 2) or (10,) flattened
                   Order: [left_eye, right_eye, nose, left_mouth, right_mouth]
        config: Preprocessing configuration. If None, uses default config.

    Returns:
        Preprocessed face image at config.output_size
        - uint8 if config.normalize_to_float=False
        - float32 if config.normalize_to_float=True

    Example:
        >>> from synapsis_face_preprocessor_lib import preprocess_face, PreprocessConfig
        >>> 
        >>> # Basic usage with defaults (all steps enabled, 112x112 output)
        >>> processed = preprocess_face(face_crop)
        >>> 
        >>> # With alignment
        >>> landmarks = np.array([...])  # 5 points from face detector
        >>> processed = preprocess_face(face_crop, landmarks)
        >>> 
        >>> # For FaceNet (160x160, skip brightness normalization)
        >>> config = PreprocessConfig(
        ...     output_size=(160, 160),
        ...     use_brightness_normalization=False,
        ...     normalize_to_float=True
        ... )
        >>> processed = preprocess_face(face_crop, landmarks, config)
        >>> 
        >>> # Minimal preprocessing - just resize
        >>> config = PreprocessConfig.minimal(output_size=(112, 112))
        >>> processed = preprocess_face(face_crop, config=config)
        >>> 
        >>> # Using preset configs
        >>> config = PreprocessConfig.for_arcface()
        >>> processed = preprocess_face(face_crop, landmarks, config)
    """
    if config is None:
        config = PreprocessConfig()

    # Validate input
    if image is None or image.size == 0:
        raise ValueError("Input image is empty or None")

    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError(
            f"Expected 3-channel image with shape (H, W, 3), got {image.shape}")

    result = image.copy()

    # Step 0: Convert input color format to RGB for processing
    if config.input_color_format == ColorFormat.BGR:
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    # Step 1: Brightness normalization (optional)
    if config.use_brightness_normalization:
        result = normalize_brightness(
            result,
            gamma=config.gamma,
            auto_gamma=config.auto_gamma,
            use_gamma=config.use_gamma_correction,
            use_clahe=config.use_clahe,
            clahe_clip_limit=config.clahe_clip_limit,
            clahe_grid_size=config.clahe_grid_size,
            gamma_target_mean=config.gamma_target_mean,
            gamma_range=config.gamma_range
        )

    # Step 2: Alignment and resize
    if config.use_alignment and landmarks is not None:
        # Get reference landmarks
        ref_landmarks = config.reference_landmarks
        if ref_landmarks is None:
            ref_landmarks = get_reference_landmarks(config.output_size)

        result = align_face_5point(
            result,
            landmarks,
            output_size=config.output_size,
            reference_landmarks=ref_landmarks,
            interpolation=config.interpolation
        )
    else:
        # Just resize if no alignment
        result = cv2.resize(
            result,
            config.output_size,
            interpolation=config.interpolation
        )

    # Step 3: RGB normalization (optional)
    if config.use_rgb_normalization:
        result = normalize_rgb(
            result,
            mean=config.normalize_mean,
            std=config.normalize_std,
            to_float=config.normalize_to_float
        )
    elif config.normalize_to_float:
        # If no RGB normalization but float output requested, just convert to float
        result = result.astype(np.float32) / 255.0

    # Step 4: Convert output color format if needed (only for uint8 output)
    if not config.normalize_to_float and config.output_color_format == ColorFormat.BGR:
        result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    return result


class FacePreprocessor:
    """
    Face Preprocessor class for face embedding preparation.

    This class wraps the preprocessing pipeline with a configurable interface,
    supporting various embedding models with different input requirements.

    Attributes:
        config: PreprocessConfig instance defining preprocessing behavior

    Example:
        >>> from synapsis_face_preprocessor_lib import FacePreprocessor, PreprocessConfig
        >>> 
        >>> # Default preprocessor (112x112, all steps enabled)
        >>> preprocessor = FacePreprocessor()
        >>> processed = preprocessor(face_crop, landmarks)
        >>> 
        >>> # For ArcFace model
        >>> preprocessor = FacePreprocessor(PreprocessConfig.for_arcface())
        >>> tensor = preprocessor.to_model_input(face_crop, landmarks)
        >>> 
        >>> # For FaceNet model (160x160)
        >>> preprocessor = FacePreprocessor(PreprocessConfig.for_facenet())
        >>> tensor = preprocessor.to_model_input(face_crop, landmarks)
        >>> 
        >>> # Custom configuration - skip brightness normalization
        >>> config = PreprocessConfig(
        ...     output_size=(112, 112),
        ...     use_brightness_normalization=False,
        ...     normalize_to_float=True
        ... )
        >>> preprocessor = FacePreprocessor(config)
        >>> 
        >>> # Input is BGR (from cv2.imread)
        >>> config = PreprocessConfig(
        ...     input_color_format='bgr',  # or ColorFormat.BGR
        ...     output_color_format='rgb'
        ... )
        >>> preprocessor = FacePreprocessor(config)
    """

    def __init__(self, config: Optional[PreprocessConfig] = None):
        """
        Initialize FacePreprocessor.

        Args:
            config: Preprocessing configuration. Uses defaults if None.
        """
        self.config = config if config is not None else PreprocessConfig()

    @property
    def output_size(self) -> Tuple[int, int]:
        """Get the output image size."""
        return self.config.output_size

    def __call__(
        self,
        image: npt.NDArray[np.uint8],
        landmarks: Optional[npt.NDArray[np.float32]] = None
    ) -> Union[npt.NDArray[np.uint8], npt.NDArray[np.float32]]:
        """
        Preprocess face image for embedding extraction.

        Args:
            image: Input image (uint8), color format per config.input_color_format
            landmarks: Optional 5-point landmarks for alignment

        Returns:
            Preprocessed face image at config.output_size
        """
        return preprocess_face(image, landmarks, self.config)

    def preprocess(
        self,
        image: npt.NDArray[np.uint8],
        landmarks: Optional[npt.NDArray[np.float32]] = None
    ) -> Union[npt.NDArray[np.uint8], npt.NDArray[np.float32]]:
        """
        Preprocess face image. Alias for __call__ method.

        Args:
            image: Input image (uint8)
            landmarks: Optional 5-point landmarks for alignment

        Returns:
            Preprocessed face image at config.output_size
        """
        return self(image, landmarks)

    def preprocess_batch(
        self,
        images: list[npt.NDArray[np.uint8]],
        landmarks_list: Optional[list[Optional[npt.NDArray[np.float32]]]] = None
    ) -> list[Union[npt.NDArray[np.uint8], npt.NDArray[np.float32]]]:
        """
        Preprocess a batch of face images.

        Args:
            images: List of RGB face images
            landmarks_list: Optional list of landmarks for each image

        Returns:
            List of preprocessed face images
        """
        if landmarks_list is None:
            landmarks_list = [None] * len(images)

        results = []
        for image, landmarks in zip(images, landmarks_list):
            try:
                processed = self(image, landmarks)
                results.append(processed)
            except Exception as e:
                # Log error but continue processing
                print(f"Warning: Failed to preprocess face: {e}")
                # Return resized image as fallback
                resized = cv2.resize(image, self.config.output_size,
                                     interpolation=cv2.INTER_LINEAR)
                results.append(resized)

        return results

    def to_model_input(
        self,
        image: npt.NDArray[np.uint8],
        landmarks: Optional[npt.NDArray[np.float32]] = None
    ) -> npt.NDArray[np.float32]:
        """
        Preprocess face and convert to model input format (NCHW).

        This method always returns a float32 array suitable for model inference,
        with shape (1, 3, H, W) in NCHW format where H, W = config.output_size.

        Args:
            image: Input image (uint8), color format per config.input_color_format
            landmarks: Optional 5-point landmarks for alignment

        Returns:
            Model-ready input tensor, shape (1, 3, H, W), float32
            where H, W matches config.output_size

        Example:
            >>> preprocessor = FacePreprocessor(PreprocessConfig.for_arcface())
            >>> tensor = preprocessor.to_model_input(face_bgr, landmarks)
            >>> # tensor.shape = (1, 3, 112, 112)
            >>> output = model(tensor)
        """
        # Temporarily override config for float output
        orig_to_float = self.config.normalize_to_float
        orig_use_rgb_norm = self.config.use_rgb_normalization

        self.config.normalize_to_float = True
        # Ensure RGB normalization is enabled for model input
        if not self.config.use_rgb_normalization:
            self.config.use_rgb_normalization = True

        try:
            processed = self(image, landmarks)
        finally:
            self.config.normalize_to_float = orig_to_float
            self.config.use_rgb_normalization = orig_use_rgb_norm

        # Transpose from HWC to CHW and add batch dimension
        # (H, W, C) -> (C, H, W) -> (1, C, H, W)
        tensor = np.transpose(processed, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)

        return tensor.astype(np.float32)

    def to_batch_input(
        self,
        images: list[npt.NDArray[np.uint8]],
        landmarks_list: Optional[list[Optional[npt.NDArray[np.float32]]]] = None
    ) -> npt.NDArray[np.float32]:
        """
        Preprocess multiple faces and return as batch tensor.

        Args:
            images: List of input images
            landmarks_list: Optional list of landmarks for each image

        Returns:
            Batch tensor, shape (N, 3, H, W), float32

        Example:
            >>> preprocessor = FacePreprocessor(PreprocessConfig.for_arcface())
            >>> batch = preprocessor.to_batch_input([face1, face2, face3])
            >>> # batch.shape = (3, 3, 112, 112)
        """
        if landmarks_list is None:
            landmarks_list = [None] * len(images)

        tensors = []
        for image, landmarks in zip(images, landmarks_list):
            tensor = self.to_model_input(image, landmarks)
            tensors.append(tensor)

        return np.concatenate(tensors, axis=0)
