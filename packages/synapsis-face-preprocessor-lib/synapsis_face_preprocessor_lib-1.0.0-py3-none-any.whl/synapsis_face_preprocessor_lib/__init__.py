"""
Face Preprocessing Library for Face Embedding.

A flexible, configurable preprocessing library for various face embedding models.
Supports ArcFace (112x112), FaceNet (160x160), VGGFace (224x224), and custom sizes.

Quick Start:
    >>> from synapsis_face_preprocessor_lib import FacePreprocessor, PreprocessConfig
    >>> 
    >>> # Default (112x112, all preprocessing enabled)
    >>> preprocessor = FacePreprocessor()
    >>> tensor = preprocessor.to_model_input(face_image, landmarks)
    >>> 
    >>> # For FaceNet (160x160)
    >>> preprocessor = FacePreprocessor(PreprocessConfig.for_facenet())
    >>> 
    >>> # Minimal preprocessing (just resize)
    >>> config = PreprocessConfig.minimal(output_size=(112, 112))
    >>> preprocessor = FacePreprocessor(config)
"""

from .face_preprocessor import (
    # Main classes
    FacePreprocessor,
    PreprocessConfig,
    ColorFormat,

    # Main function
    preprocess_face,

    # Individual preprocessing functions
    normalize_brightness,
    apply_clahe,
    gamma_correction,
    estimate_gamma,
    align_face_5point,
    normalize_rgb,
    estimate_affine_matrix,

    # Reference landmarks
    ARCFACE_REF_LANDMARKS,
    REFERENCE_LANDMARKS_PRESETS,
    get_reference_landmarks,
)

__all__ = [
    # Main classes
    "FacePreprocessor",
    "PreprocessConfig",
    "ColorFormat",

    # Main function
    "preprocess_face",

    # Individual preprocessing functions
    "normalize_brightness",
    "apply_clahe",
    "gamma_correction",
    "estimate_gamma",
    "align_face_5point",
    "normalize_rgb",
    "estimate_affine_matrix",

    # Reference landmarks
    "ARCFACE_REF_LANDMARKS",
    "REFERENCE_LANDMARKS_PRESETS",
    "get_reference_landmarks",
]

__version__ = "1.0.0"
