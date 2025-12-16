"""
Lazy loaders for audio datasets.

Provides efficient lazy loading of audio from path columns.
"""
from pathlib import Path
from typing import Union, List, Optional, Tuple
import pandas as pd
import numpy as np


class AudioColumn:
    """
    Lazy audio loader for path columns.

    Loads audio on-demand when indexed, avoiding memory overhead
    of loading all audio upfront.

    Examples:
        >>> import warpdata as wd
        >>> from warpdata.loaders import AudioColumn
        >>>
        >>> df = wd.load("warpdata://audio/vctk", as_format="pandas")
        >>> audio_files = AudioColumn(df['audio_path'])
        >>>
        >>> # Load single audio file
        >>> audio, sr = audio_files[0]  # (np.ndarray, sample_rate)
        >>> print(f"Shape: {audio.shape}, SR: {sr} Hz")
        >>>
        >>> # Load batch
        >>> batch = audio_files[0:10]  # List of (audio, sr) tuples
        >>>
        >>> # Iterate
        >>> for audio, sr in audio_files[:5]:
        ...     print(f"Duration: {len(audio)/sr:.2f}s")
    """

    def __init__(self, paths: Union[pd.Series, List[str], List[Path]]):
        """
        Initialize lazy audio loader.

        Args:
            paths: Series or list of audio file paths
        """
        if isinstance(paths, pd.Series):
            self.paths = paths.tolist()
        else:
            self.paths = [Path(p) if not isinstance(p, Path) else p for p in paths]

    def __len__(self):
        """Return number of audio files."""
        return len(self.paths)

    def __getitem__(self, idx) -> Union[Tuple[np.ndarray, int], List[Tuple[np.ndarray, int]]]:
        """
        Load audio file(s) at index.

        Args:
            idx: int or slice

        Returns:
            (audio, sample_rate) for int index
            List[(audio, sample_rate)] for slice
        """
        try:
            import soundfile as sf
        except ImportError:
            raise ImportError(
                "soundfile is required for audio loading. "
                "Install with: pip install soundfile"
            )

        if isinstance(idx, slice):
            # Batch loading
            paths = self.paths[idx]
            return [sf.read(str(p)) for p in paths]
        else:
            # Single audio file
            return sf.read(str(self.paths[idx]))

    def load(self, idx: Union[int, slice]):
        """
        Alias for __getitem__ for explicit loading.

        Args:
            idx: Index or slice

        Returns:
            (audio, sr) or List[(audio, sr)]
        """
        return self[idx]

    def load_batch(self, indices: List[int]) -> List[Tuple[np.ndarray, int]]:
        """
        Load multiple audio files by index list.

        Args:
            indices: List of indices to load

        Returns:
            List[(audio, sample_rate)]
        """
        try:
            import soundfile as sf
        except ImportError:
            raise ImportError(
                "soundfile is required for audio loading. "
                "Install with: pip install soundfile"
            )

        return [sf.read(str(self.paths[i])) for i in indices]

    def get_info(self, idx: int) -> dict:
        """
        Get audio file metadata without loading full audio.

        Args:
            idx: Index

        Returns:
            Dict with keys: samplerate, channels, duration, frames, format, subtype
        """
        try:
            import soundfile as sf
        except ImportError:
            raise ImportError(
                "soundfile is required for audio info. "
                "Install with: pip install soundfile"
            )

        info = sf.info(str(self.paths[idx]))
        return {
            'samplerate': info.samplerate,
            'channels': info.channels,
            'duration': info.duration,
            'frames': info.frames,
            'format': info.format,
            'subtype': info.subtype,
        }

    def to_array(
        self,
        idx: Union[int, slice],
        target_sr: Optional[int] = None,
        mono: bool = False
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Load audio as numpy array with optional resampling.

        Args:
            idx: Index or slice
            target_sr: Target sample rate (resamples if different from source)
            mono: Convert to mono if True

        Returns:
            np.ndarray for single audio, List[np.ndarray] for batch
        """
        import soundfile as sf

        audio_files = self[idx]

        if not isinstance(idx, slice):
            # Single file
            audio, sr = audio_files

            if mono and len(audio.shape) > 1:
                audio = audio.mean(axis=1)

            if target_sr and sr != target_sr:
                # Simple resampling (for better quality, use librosa)
                import numpy as np
                duration = len(audio) / sr
                target_length = int(duration * target_sr)
                audio = np.interp(
                    np.linspace(0, len(audio), target_length),
                    np.arange(len(audio)),
                    audio
                )

            return audio
        else:
            # Batch
            result = []
            for audio, sr in audio_files:
                if mono and len(audio.shape) > 1:
                    audio = audio.mean(axis=1)

                if target_sr and sr != target_sr:
                    import numpy as np
                    duration = len(audio) / sr
                    target_length = int(duration * target_sr)
                    audio = np.interp(
                        np.linspace(0, len(audio), target_length),
                        np.arange(len(audio)),
                        audio
                    )

                result.append(audio)

            return result


def load_audio_column(paths: Union[pd.Series, List[str]]) -> AudioColumn:
    """
    Create lazy audio loader from path column.

    Args:
        paths: Series or list of audio paths

    Returns:
        AudioColumn lazy loader

    Examples:
        >>> from warpdata.loaders import load_audio_column
        >>>
        >>> df = wd.load("warpdata://audio/vctk")
        >>> audio_loader = load_audio_column(df['audio_path'])
        >>>
        >>> # Load first audio file
        >>> audio, sr = audio_loader[0]
        >>> print(f"Shape: {audio.shape}, SR: {sr}")
        >>>
        >>> # Get metadata without loading
        >>> info = audio_loader.get_info(0)
        >>> print(f"Duration: {info['duration']:.2f}s")
        >>>
        >>> # Load batch as normalized arrays
        >>> arrays = audio_loader.to_array(slice(0, 10), target_sr=16000, mono=True)
    """
    return AudioColumn(paths)
