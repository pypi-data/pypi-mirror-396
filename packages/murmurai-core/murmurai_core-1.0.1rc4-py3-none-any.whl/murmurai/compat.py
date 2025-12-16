"""Compatibility patches for modern PyTorch/pyannote/torchaudio.

This module provides patches for:
0. cuDNN library path configuration (for isolated environments like uvx)
1. Torch 2.6+ weights_only default change
2. Pyannote 4.x use_auth_token -> token rename
3. Torchaudio 2.9+ list_audio_backends removal

These patches are applied at import time before any other murmurai imports.
"""

import os

# =============================================================================
# PATCH 0: cuDNN library path configuration (MUST be before torch import)
# =============================================================================
# In isolated environments (uvx, fresh venvs), LD_LIBRARY_PATH may not include
# the nvidia.cudnn package's lib directory. This causes "Unable to load libcudnn"
# errors even when cudnn is installed via pip.
# We set LD_LIBRARY_PATH AND preload via ctypes for maximum compatibility.
# =============================================================================
import ctypes
import glob

def _setup_nvidia_libs():
    """Configure nvidia library paths for isolated environments."""
    nvidia_libs = []

    # Find nvidia package lib directories
    for pkg in ["nvidia.cudnn", "nvidia.cublas", "nvidia.cuda_runtime", "nvidia.nvjitlink"]:
        try:
            mod = __import__(pkg, fromlist=[""])
            lib_path = os.path.join(mod.__path__[0], "lib")
            if os.path.isdir(lib_path):
                nvidia_libs.append(lib_path)
        except ImportError:
            continue

    if not nvidia_libs:
        return

    # Update LD_LIBRARY_PATH for subprocess calls
    current_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    new_paths = [p for p in nvidia_libs if p not in current_ld_path]
    if new_paths:
        os.environ["LD_LIBRARY_PATH"] = ":".join(new_paths + ([current_ld_path] if current_ld_path else []))

    # Preload cudnn libraries via ctypes (for current process)
    for lib_dir in nvidia_libs:
        for pattern in ["libcudnn*.so*", "libcublas*.so*", "libnvJitLink*.so*"]:
            for lib_file in sorted(glob.glob(os.path.join(lib_dir, pattern))):
                try:
                    ctypes.CDLL(lib_file, mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    continue

_setup_nvidia_libs()

import warnings

# Suppress pyannote version mismatch warnings (models work fine despite version differences)
warnings.filterwarnings("ignore", message="Model was trained with")
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
warnings.filterwarnings("ignore", category=UserWarning, module="pytorch_lightning")

# =============================================================================
# PATCH 1: Torch 2.6+ compatibility
# =============================================================================
# Torch 2.6+ changed weights_only=True as default for torch.load().
# Pyannote/lightning models serialize custom types that need weights_only=False.
# =============================================================================
import torch


def _patched_load(path_or_url, map_location=None, **kwargs):
    """Patched load that uses weights_only=False for trusted pyannote models."""
    kwargs.pop("weights_only", None)
    return torch.load(path_or_url, map_location=map_location, weights_only=False, **kwargs)


_patched_modules = []

try:
    import lightning.fabric.utilities.cloud_io as cloud_io

    cloud_io._load = _patched_load
    _patched_modules.append("lightning.fabric.utilities.cloud_io")
except ImportError:
    pass

try:
    import lightning.pytorch.core.saving as saving

    saving.pl_load = _patched_load
    _patched_modules.append("lightning.pytorch.core.saving.pl_load")
except ImportError:
    pass

try:
    import lightning_fabric.utilities.cloud_io as cloud_io2

    cloud_io2._load = _patched_load
    _patched_modules.append("lightning_fabric.utilities.cloud_io")
except ImportError:
    pass

if _patched_modules:
    pass  # Patches applied silently

# =============================================================================
# PATCH 2: Pyannote 4.x compatibility (use_auth_token -> token)
# =============================================================================
# murmurai uses `use_auth_token` parameter, but pyannote 4.x renamed it to `token`.
# =============================================================================
try:
    from pyannote.audio.pipelines import voice_activity_detection as vad_module

    _original_vad_init = vad_module.VoiceActivityDetection.__init__

    def _patched_vad_init(self, segmentation=None, fscore=False, **inference_kwargs):
        """Patched __init__ that converts use_auth_token to token for pyannote 4.x."""
        if "use_auth_token" in inference_kwargs:
            inference_kwargs["token"] = inference_kwargs.pop("use_auth_token")
        return _original_vad_init(
            self, segmentation=segmentation, fscore=fscore, **inference_kwargs
        )

    vad_module.VoiceActivityDetection.__init__ = _patched_vad_init
    _patched_modules.append("pyannote.vad.use_auth_token")
except (ImportError, AttributeError):
    pass

try:
    from pyannote.audio.core import inference as inference_module

    _original_inference_init = inference_module.Inference.__init__

    def _patched_inference_init(self, model, *args, **kwargs):
        """Patched __init__ that converts use_auth_token to token for pyannote 4.x."""
        if "use_auth_token" in kwargs:
            kwargs["token"] = kwargs.pop("use_auth_token")
        return _original_inference_init(self, model, *args, **kwargs)

    inference_module.Inference.__init__ = _patched_inference_init
    _patched_modules.append("pyannote.inference.use_auth_token")
except (ImportError, AttributeError):
    pass

# Also patch Model.from_pretrained for pyannote 4.x
try:
    from pyannote.audio import Model as PyannoteModel

    _original_model_from_pretrained = PyannoteModel.from_pretrained

    @classmethod
    def _patched_model_from_pretrained(cls, checkpoint, *args, **kwargs):
        """Patched from_pretrained that converts use_auth_token to token."""
        if "use_auth_token" in kwargs:
            kwargs["token"] = kwargs.pop("use_auth_token")
        return _original_model_from_pretrained.__func__(cls, checkpoint, *args, **kwargs)

    PyannoteModel.from_pretrained = _patched_model_from_pretrained
    _patched_modules.append("pyannote.Model.from_pretrained")
except (ImportError, AttributeError):
    pass

# Patch Pipeline.from_pretrained too
try:
    from pyannote.audio import Pipeline as PyannotePipeline

    _original_pipeline_from_pretrained = PyannotePipeline.from_pretrained

    @classmethod
    def _patched_pipeline_from_pretrained(cls, checkpoint, *args, **kwargs):
        """Patched from_pretrained that converts use_auth_token to token."""
        if "use_auth_token" in kwargs:
            kwargs["token"] = kwargs.pop("use_auth_token")
        return _original_pipeline_from_pretrained.__func__(cls, checkpoint, *args, **kwargs)

    PyannotePipeline.from_pretrained = _patched_pipeline_from_pretrained
    _patched_modules.append("pyannote.Pipeline.from_pretrained")
except (ImportError, AttributeError):
    pass

if any("pyannote" in m for m in _patched_modules):
    pass  # Patches applied silently

# =============================================================================
# PATCH 3: Torchaudio 2.9+ compatibility (list_audio_backends removed)
# =============================================================================
# speechbrain calls torchaudio.list_audio_backends() which was removed in 2.9+
# =============================================================================
import torchaudio

if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: []
