"""
Embedding computation providers.

Supports multiple embedding providers:
- numpy: Simple random embeddings for testing
- sentence-transformers: Sentence transformers models (text)
- openai: OpenAI embedding API (text)
- clip: CLIP vision encoder (image paths)
- clip-text: CLIP text encoder (text)
"""
from typing import List, Optional, Dict, Any
import numpy as np


class EmbeddingProvider:
    """Base class for embedding providers."""

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts.

        Args:
            texts: List of text strings

        Returns:
            Array of shape (len(texts), dimension)
        """
        raise NotImplementedError

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        raise NotImplementedError


class NumpyProvider(EmbeddingProvider):
    """
    Simple numpy-based random embedding provider for testing.

    NOT for production use - generates random vectors.
    """

    def __init__(self, dimension: int = 128):
        """
        Initialize numpy provider.

        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        # Use a fixed seed for reproducibility in tests
        self.rng = np.random.RandomState(42)

    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate random embeddings."""
        # Generate deterministic random vectors based on text hash
        embeddings = []
        for text in texts:
            # Use text hash as seed for reproducibility
            seed = hash(text) % (2**32)
            rng = np.random.RandomState(seed)
            embedding = rng.randn(self.dimension)
            # Normalize to unit length
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            embeddings.append(embedding)

        return np.array(embeddings)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Sentence transformers embedding provider.

    Requires: pip install sentence-transformers
    """

    def __init__(self, model: str = "all-MiniLM-L6-v2", device: Optional[str] = None, **kwargs):
        """
        Initialize sentence transformers provider.

        Args:
            model: Model name or path
            **kwargs: Additional arguments for SentenceTransformer
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install with: pip install warpdata[embeddings]"
            )

        self.model_name = model
        # Let users override device; if None, SentenceTransformer auto-detects CUDA
        if device is not None:
            self.model = SentenceTransformer(model, device=device, **kwargs)
        else:
            self.model = SentenceTransformer(model, **kwargs)
        self._dimension = self.model.get_sentence_embedding_dimension()

        # Best-effort logging of device (CPU vs CUDA)
        actual_device = None
        try:
            # sentence-transformers exposes underlying model.device / _target_device
            if hasattr(self.model, "device"):
                actual_device = str(self.model.device)
            elif hasattr(self.model, "_target_device"):
                actual_device = str(self.model._target_device)
        except Exception:
            actual_device = None

        if actual_device:
            print(f"[embeddings] sentence-transformers:{self.model_name} using device={actual_device}")

    def embed(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """Embed texts using sentence transformers."""
        # Respect batch_size if provided; suppress internal progress bar (we handle it externally)
        if batch_size is not None:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        else:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # Best-effort: free cached GPU memory between micro-batches
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


class OpenAIProvider(EmbeddingProvider):
    """
    OpenAI embedding provider.

    Requires: pip install openai
    """

    def __init__(self, model: str = "text-embedding-ada-002", api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.

        Args:
            model: OpenAI model name
            api_key: API key (reads from env if not provided)
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai is not installed. " "Install with: pip install warpdata[embeddings]"
            )

        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

        # Dimension depends on model
        dimension_map = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }
        self._dimension = dimension_map.get(model, 1536)

    def embed(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """Embed texts using OpenAI API."""
        all_embeddings = []

        # Process in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(input=batch, model=self.model)
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return np.array(all_embeddings)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


def get_provider(
    provider: str, model: Optional[str] = None, dimension: Optional[int] = None, **kwargs
) -> EmbeddingProvider:
    """
    Get an embedding provider instance.

    Args:
        provider: Provider name ('numpy', 'sentence-transformers', 'openai')
        model: Model name (provider-specific)
        dimension: Embedding dimension (for numpy provider)
        **kwargs: Additional provider-specific arguments

    Returns:
        EmbeddingProvider instance
    """
    if provider == "numpy":
        if dimension is None:
            dimension = 128
        return NumpyProvider(dimension=dimension)

    elif provider == "sentence-transformers":
        if model is None:
            model = "all-MiniLM-L6-v2"
        return SentenceTransformerProvider(model=model, **kwargs)

    elif provider == "openai":
        if model is None:
            model = "text-embedding-ada-002"
        return OpenAIProvider(model=model, **kwargs)

    elif provider == "clip":
        # Image embeddings using CLIP vision tower. Expects list of image paths.
        if model is None:
            model = "openai/clip-vit-base-patch32"
        return CLIPVisionProvider(model=model, **kwargs)
    elif provider in ("clip-text", "clip_text"):
        if model is None:
            model = "openai/clip-vit-base-patch32"
        return CLIPTextProvider(model=model, **kwargs)

    elif provider in ("clap-audio", "clap_audio", "clap"):
        # Audio embeddings using CLAP. Can embed audio files or text.
        if model is None:
            model = "laion/clap-htsat-unfused"
        return CLAPAudioProvider(model=model, **kwargs)

    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


class CLIPVisionProvider(EmbeddingProvider):
    """
    CLIP image embedding provider.

    Expects a list of image file paths (strings) and returns L2-normalized
    image embeddings from the CLIP visual encoder.

    Requires: pip install transformers torch pillow
    """

    def __init__(self, model: str = "openai/clip-vit-base-patch32", device: Optional[str] = None):
        try:
            import torch  # noqa: F401
            from transformers import CLIPModel, CLIPProcessor
        except ImportError:
            raise ImportError(
                "CLIP provider requires transformers, torch, and pillow. "
                "Install with: pip install transformers torch pillow"
            )

        from transformers import CLIPModel, CLIPProcessor
        import torch

        self.model_name = model
        self.model = CLIPModel.from_pretrained(model)
        self.processor = CLIPProcessor.from_pretrained(model)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        print(f"[embeddings] clip-vision:{self.model_name} using device={self.device}")

        # Infer embedding dimension from visual projection layer
        try:
            self._dimension = int(self.model.visual_projection.out_features)
        except Exception:
            # Fallback: run a dummy forward on a tiny image
            from PIL import Image
            import numpy as np
            img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
            inputs = self.processor(images=[img], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                feats = self.model.get_image_features(**inputs)
            self._dimension = int(feats.shape[-1])

    def embed(self, image_paths: List[str]) -> np.ndarray:
        import torch
        from PIL import Image

        # Load images
        images = []
        for p in image_paths:
            try:
                img = Image.open(p).convert("RGB")
            except Exception:
                # If path not loadable, use a black placeholder to keep alignment
                from PIL import Image as _Image
                img = _Image.new("RGB", (224, 224), color=(0, 0, 0))
            images.append(img)

        # Batch through processor/model
        inputs = self.processor(images=images, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            feats = self.model.get_image_features(**inputs)
        arr = feats.cpu().numpy().astype(np.float32)

        # Normalize for cosine distance
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8
        arr = arr / norms
        return arr

    def get_dimension(self) -> int:
        return self._dimension


class CLIPTextProvider(EmbeddingProvider):
    """
    CLIP text embedding provider using the text tower.

    Expects a list of text strings; returns L2-normalized text embeddings.

    Requires: pip install transformers torch
    """

    def __init__(self, model: str = "openai/clip-vit-base-patch32", device: Optional[str] = None):
        try:
            import torch  # noqa: F401
            from transformers import CLIPModel, CLIPProcessor
        except ImportError:
            raise ImportError(
                "CLIP text provider requires transformers and torch. "
                "Install with: pip install transformers torch"
            )

        from transformers import CLIPModel, CLIPProcessor
        import torch

        self.model_name = model
        self.model = CLIPModel.from_pretrained(model)
        self.processor = CLIPProcessor.from_pretrained(model)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        print(f"[embeddings] clip-text:{self.model_name} using device={self.device}")

        # Infer embedding dimension from text projection
        try:
            self._dimension = int(self.model.text_projection.out_features)
        except Exception:
            # Fallback via a dummy forward
            inputs = self.processor(text=["test"], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            import torch
            with torch.no_grad():
                feats = self.model.get_text_features(**inputs)
            self._dimension = int(feats.shape[-1])

    def embed(self, texts: List[str]) -> np.ndarray:
        from transformers import CLIPProcessor  # noqa: F401
        import torch

        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            feats = self.model.get_text_features(**inputs)
        arr = feats.cpu().numpy().astype(np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8
        arr = arr / norms
        return arr

    def get_dimension(self) -> int:
        return self._dimension


class CLAPAudioProvider(EmbeddingProvider):
    """
    LAION CLAP audio embedding provider.

    Supports joint audio-text embeddings using CLAP models.
    Can embed both audio files and text queries.

    Requires: pip install laion-clap
    """

    def __init__(
        self,
        model: str = "laion/clap-htsat-unfused",
        device: Optional[str] = None,
        audio_column: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize CLAP provider.

        Args:
            model: CLAP model name (default: "laion/clap-htsat-unfused")
                   Options: "laion/clap-htsat-unfused", "laion/larger_clap_general"
            device: Device to use ("cuda" or "cpu")
            audio_column: Column containing audio file paths (for audio embedding)
            **kwargs: Additional arguments
        """
        try:
            import laion_clap
        except ImportError:
            raise ImportError(
                "laion-clap is not installed. "
                "Install with: pip install laion-clap"
            )

        self.model_name = model
        self.audio_column = audio_column
        self.device = device or ("cuda" if self._has_cuda() else "cpu")

        # Initialize CLAP model
        import laion_clap
        self.clap_module = laion_clap.CLAP_Module(
            enable_fusion=False,
            device=self.device,
            amodel='HTSAT-tiny' if 'htsat' in model.lower() else 'PANN-14',
        )
        # Load default model (model_id parameter not supported)
        self.clap_module.load_ckpt()

        print(f"[embeddings] clap-audio:{self.model_name} using device={self.device}")
        self._dimension = 512

    def _has_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

    def embed(self, inputs: List[str]) -> np.ndarray:
        """Embed audio files or text."""
        import os
        if inputs and os.path.exists(inputs[0]):
            return self._embed_audio(inputs)
        else:
            return self._embed_text(inputs)

    def _embed_audio(self, audio_paths: List[str]) -> np.ndarray:
        """Embed audio files."""
        embeddings = []
        batch_size = 32
        for i in range(0, len(audio_paths), batch_size):
            batch = audio_paths[i:i+batch_size]
            audio_embed = self.clap_module.get_audio_embedding_from_filelist(
                x=batch,
                use_tensor=False
            )
            embeddings.append(audio_embed)

        embeddings = np.vstack(embeddings).astype(np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
        embeddings = embeddings / norms
        return embeddings

    def _embed_text(self, texts: List[str]) -> np.ndarray:
        """Embed text queries."""
        text_embed = self.clap_module.get_text_embedding(
            texts,
            use_tensor=False
        )
        norms = np.linalg.norm(text_embed, axis=1, keepdims=True) + 1e-8
        text_embed = text_embed / norms
        return text_embed.astype(np.float32)

    def get_dimension(self) -> int:
        return self._dimension
