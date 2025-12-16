"""
Arabic End-of-Utterance (EOU) Model for LiveKit Agents

This module provides a turn detector for Arabic conversations,
optimized for Saudi dialect. It predicts whether a user has
finished speaking based on conversation context.
"""

from __future__ import annotations

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from livekit.agents import llm

from .log import logger
from .version import __version__

# Default model on HuggingFace
DEFAULT_MODEL_PATH = "salmamohammedhamed22/arabic-eou-model"

# Maximum conversation turns to consider
MAX_HISTORY_TURNS = 6


class ArabicEOUModel:
    """
    Arabic End-of-Utterance detection model for LiveKit Agents.
    
    This model predicts whether a user has finished speaking based on
    the conversation context. Optimized for Saudi Arabic dialect.
    
    The model uses [SEP] tokens to separate conversation turns and
    outputs a binary classification (0=incomplete, 1=complete).
    
    Example:
        ```python
        from livekit.plugins.arabic_eou import ArabicEOUModel
        
        session = AgentSession(
            turn_detection=ArabicEOUModel(),
            stt=deepgram.STT(language="ar"),
            ...
        )
        ```
    """
    
    def __init__(
        self,
        *,
        model_path: str = DEFAULT_MODEL_PATH,
        unlikely_threshold: float = 0.5,
        device: str | None = None,
    ):
        """
        Initialize the Arabic EOU model.
        
        Args:
            model_path: Path to the fine-tuned model on HuggingFace
            unlikely_threshold: Probability threshold below which the user
                               is considered to still be speaking.
                               If prediction < threshold, wait longer.
            device: Device to run inference on (cuda/cpu/auto)
        """
        self._model_path = model_path
        self._unlikely_threshold = unlikely_threshold
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Lazy loading - model loads on first use
        self._model: AutoModelForSequenceClassification | None = None
        self._tokenizer: AutoTokenizer | None = None
        self._loaded = False
        
        logger.info(
            f"ArabicEOUModel initialized (model={model_path}, device={self._device})"
        )
    
    def _ensure_loaded(self) -> None:
        """Load model and tokenizer if not already loaded."""
        if self._loaded:
            return
        
        logger.info(f"Loading Arabic EOU model from {self._model_path}...")
        
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self._model_path,
                trust_remote_code=True,
            )
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self._model_path,
                trust_remote_code=True,
            ).to(self._device)
            self._model.eval()
            
            self._loaded = True
            logger.info(f"Arabic EOU model loaded successfully on {self._device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(
                f"Could not load Arabic EOU model from {self._model_path}. "
                "Make sure you have downloaded the model files. "
                "Run: python your_agent.py download-files"
            ) from e
    
    @property
    def model(self) -> str:
        """Return model identifier."""
        return "arabic-eou"
    
    @property
    def provider(self) -> str:
        """Return provider name."""
        return "hams-ai"
    
    async def unlikely_threshold(self, language: str | None) -> float | None:
        """
        Return the threshold for detecting incomplete utterances.
        
        If the predicted probability is below this threshold,
        the system waits longer (max_endpointing_delay) before responding.
        
        Args:
            language: The detected language code (e.g., "ar", "ar-SA")
            
        Returns:
            The threshold value for Arabic, None for unsupported languages
        """
        if language is None:
            return self._unlikely_threshold
        
        lang = language.lower()
        # Support various Arabic language codes
        if lang in ["ar", "ar-sa"]:
            return self._unlikely_threshold
        
        # Not supported for non-Arabic languages
        return None
    
    async def supports_language(self, language: str | None) -> bool:
        """
        Check if the given language is supported.
        
        Args:
            language: The language code to check
            
        Returns:
            True if Arabic, False otherwise
        """
        threshold = await self.unlikely_threshold(language)
        return threshold is not None
    
    def _format_chat_context(self, chat_ctx: llm.ChatContext) -> str:
        """
        Format the chat context for model input.
        
        Converts the conversation to the [SEP] separated format
        expected by the model.
        
        Args:
            chat_ctx: The LiveKit chat context
            
        Returns:
            Formatted string with [SEP] separators
        """
        messages = []
        
        for item in chat_ctx.items:
            if item.type != "message":
                continue
            if item.role not in ("user", "assistant"):
                continue
            
            text_content = item.text_content
            if text_content:
                messages.append(text_content.strip())
        
        # Keep only recent turns
        messages = messages[-MAX_HISTORY_TURNS:]
        
        # Join with [SEP] tokens (matching training format)
        formatted = " [SEP] ".join(messages)
        
        return formatted
    
    async def predict_end_of_turn(
        self,
        chat_ctx: llm.ChatContext,
        *,
        timeout: float | None = 3.0,
    ) -> float:
        """
        Predict the probability that the user has finished speaking.
        
        This is the main method called by LiveKit's AudioRecognition
        to determine when to end the user's turn.
        
        Args:
            chat_ctx: The conversation context from LiveKit
            timeout: Maximum time for inference (not used, kept for interface)
            
        Returns:
            float: Probability (0.0-1.0) that user finished their turn
                   - High (>0.5): User likely finished → respond soon
                   - Low (<unlikely_threshold): User likely has more to say → wait
        """
        self._ensure_loaded()
        
        # Format input text
        text = self._format_chat_context(chat_ctx)
        
        if not text:
            # No context available, assume user is done
            logger.debug("Empty context, returning 1.0")
            return 1.0
        
        # Tokenize
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        ).to(self._device)
        
        # Run inference
        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits
            
            # Apply softmax to get probabilities
            probs = torch.softmax(logits, dim=-1)
            
            # Class 1 = complete (end of turn)
            # Class 0 = incomplete (more to come)
            eou_probability = probs[0, 1].item()
        
        logger.debug(
            "Arabic EOU prediction",
            extra={
                "probability": round(eou_probability, 3),
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
            }
        )
        
        return eou_probability
    
    @classmethod
    def download_files(cls, model_path: str = DEFAULT_MODEL_PATH) -> None:
        """
        Download model files for offline use.
        
        Call this before running the agent in production:
            python agent.py download-files
        
        Args:
            model_path: HuggingFace model path to download
        """
        logger.info(f"Downloading Arabic EOU model from {model_path}...")
        
        # Download tokenizer
        AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        logger.info("Tokenizer downloaded")
        
        # Download model
        AutoModelForSequenceClassification.from_pretrained(
            model_path, trust_remote_code=True
        )
        logger.info("Model downloaded")
        
        logger.info(f" Arabic EOU model downloaded successfully!")
