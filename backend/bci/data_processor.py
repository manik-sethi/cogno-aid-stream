import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from scipy import signal
from collections import deque
import asyncio

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes raw EEG signals with filtering, artifact removal, and feature extraction."""
    
    def __init__(self, sample_rate: int = 128):
        self.sample_rate = sample_rate
        self.buffer_size = sample_rate * 2  # 2 seconds of data
        self.channel_buffers = {}
        self.initialized = False
        
        # Filter parameters
        self.highpass_freq = 1.0   # Remove DC drift
        self.lowpass_freq = 50.0   # Remove high-frequency noise
        self.notch_freq = 60.0     # Remove power line interference
        
        # Artifact detection thresholds
        self.amplitude_threshold = 200.0  # microvolts
        self.gradient_threshold = 50.0    # microvolts/sample
        
    async def process_eeg_signal(self, eeg_data: Dict) -> Dict:
        """
        Process raw EEG data with filtering and artifact removal.
        
        Args:
            eeg_data: Raw EEG data from BCI device
            
        Returns:
            Processed EEG data with clean signals
        """
        try:
            processed_data = {
                'eeg': {},
                'timestamp': eeg_data.get('timestamp', asyncio.get_event_loop().time()),
                'sample_rate': self.sample_rate,
                'channels': eeg_data.get('channels', []),
                'quality': {}
            }
            
            eeg_channels = eeg_data.get('eeg', {})
            
            for channel, signal_data in eeg_channels.items():
                # Initialize buffer for this channel if needed
                if channel not in self.channel_buffers:
                    self.channel_buffers[channel] = deque(maxlen=self.buffer_size)
                
                # Add new data to buffer
                if isinstance(signal_data, (int, float)):
                    self.channel_buffers[channel].append(signal_data)
                else:
                    # Handle array data
                    for sample in signal_data:
                        self.channel_buffers[channel].append(sample)
                
                # Process channel if we have enough data
                if len(self.channel_buffers[channel]) >= 128:  # At least 1 second
                    processed_signal, quality = await self._process_channel(
                        channel, 
                        list(self.channel_buffers[channel])
                    )
                    
                    processed_data['eeg'][channel] = processed_signal[-1] if processed_signal else 0.0
                    processed_data['quality'][channel] = quality
                else:
                    processed_data['eeg'][channel] = signal_data
                    processed_data['quality'][channel] = 0.5  # Unknown quality
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing EEG signal: {e}")
            return eeg_data  # Return original data if processing fails
    
    async def _process_channel(self, channel: str, signal_data: List[float]) -> Tuple[List[float], float]:
        """Process a single EEG channel."""
        try:
            signal_array = np.array(signal_data)
            
            # 1. Apply bandpass filter
            filtered_signal = self._apply_bandpass_filter(signal_array)
            
            # 2. Apply notch filter for power line interference
            notched_signal = self._apply_notch_filter(filtered_signal)
            
            # 3. Detect and handle artifacts
            clean_signal, quality_score = self._detect_artifacts(notched_signal)
            
            # 4. Apply additional smoothing if needed
            smoothed_signal = self._apply_smoothing(clean_signal)
            
            return smoothed_signal.tolist(), quality_score
            
        except Exception as e:
            logger.error(f"Error processing channel {channel}: {e}")
            return signal_data, 0.0
    
    def _apply_bandpass_filter(self, signal_data: np.ndarray) -> np.ndarray:
        """Apply bandpass filter to remove unwanted frequencies."""
        try:
            # Design Butterworth bandpass filter
            nyquist = self.sample_rate / 2
            low = self.highpass_freq / nyquist
            high = self.lowpass_freq / nyquist
            
            b, a = signal.butter(4, [low, high], btype='band')
            filtered_signal = signal.filtfilt(b, a, signal_data)
            
            return filtered_signal
            
        except Exception as e:
            logger.error(f"Error applying bandpass filter: {e}")
            return signal_data
    
    def _apply_notch_filter(self, signal_data: np.ndarray) -> np.ndarray:
        """Apply notch filter to remove power line interference."""
        try:
            # Design notch filter at 60Hz
            nyquist = self.sample_rate / 2
            freq = self.notch_freq / nyquist
            quality_factor = 30
            
            b, a = signal.iirnotch(freq, quality_factor)
            notched_signal = signal.filtfilt(b, a, signal_data)
            
            return notched_signal
            
        except Exception as e:
            logger.error(f"Error applying notch filter: {e}")
            return signal_data
    
    def _detect_artifacts(self, signal_data: np.ndarray) -> Tuple[np.ndarray, float]:
        """Detect and handle artifacts in EEG signal."""
        try:
            # Calculate signal quality metrics
            amplitude_quality = self._check_amplitude_artifacts(signal_data)
            gradient_quality = self._check_gradient_artifacts(signal_data)
            
            # Overall quality score (0.0 = poor, 1.0 = excellent)
            quality_score = (amplitude_quality + gradient_quality) / 2.0
            
            # Apply artifact correction if quality is poor
            if quality_score < 0.5:
                corrected_signal = self._correct_artifacts(signal_data)
            else:
                corrected_signal = signal_data
            
            return corrected_signal, quality_score
            
        except Exception as e:
            logger.error(f"Error detecting artifacts: {e}")
            return signal_data, 0.5
    
    def _check_amplitude_artifacts(self, signal_data: np.ndarray) -> float:
        """Check for amplitude-based artifacts (muscle movements, electrode pops)."""
        # Count samples exceeding threshold
        artifact_samples = np.sum(np.abs(signal_data) > self.amplitude_threshold)
        quality = 1.0 - (artifact_samples / len(signal_data))
        return max(quality, 0.0)
    
    def _check_gradient_artifacts(self, signal_data: np.ndarray) -> float:
        """Check for gradient-based artifacts (sudden jumps)."""
        # Calculate signal gradient
        gradient = np.diff(signal_data)
        artifact_samples = np.sum(np.abs(gradient) > self.gradient_threshold)
        quality = 1.0 - (artifact_samples / len(gradient))
        return max(quality, 0.0)
    
    def _correct_artifacts(self, signal_data: np.ndarray) -> np.ndarray:
        """Apply artifact correction techniques."""
        try:
            # Simple artifact correction: replace outliers with interpolated values
            corrected_signal = signal_data.copy()
            
            # Find outliers
            outliers = np.abs(corrected_signal) > self.amplitude_threshold
            
            if np.any(outliers):
                # Interpolate outlier values
                valid_indices = np.where(~outliers)[0]
                outlier_indices = np.where(outliers)[0]
                
                if len(valid_indices) > 1:
                    corrected_signal[outliers] = np.interp(
                        outlier_indices, 
                        valid_indices, 
                        corrected_signal[valid_indices]
                    )
            
            return corrected_signal
            
        except Exception as e:
            logger.error(f"Error correcting artifacts: {e}")
            return signal_data
    
    def _apply_smoothing(self, signal_data: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Apply smoothing to reduce noise."""
        try:
            # Apply moving average smoothing
            if len(signal_data) < window_size:
                return signal_data
            
            smoothed = np.convolve(signal_data, np.ones(window_size)/window_size, mode='same')
            return smoothed
            
        except Exception as e:
            logger.error(f"Error applying smoothing: {e}")
            return signal_data
    
    def get_signal_statistics(self, channel: str) -> Dict:
        """Get statistical information about a channel's signal quality."""
        if channel not in self.channel_buffers or len(self.channel_buffers[channel]) == 0:
            return {}
        
        signal_data = np.array(list(self.channel_buffers[channel]))
        
        return {
            'mean': float(np.mean(signal_data)),
            'std': float(np.std(signal_data)),
            'min': float(np.min(signal_data)),
            'max': float(np.max(signal_data)),
            'peak_to_peak': float(np.max(signal_data) - np.min(signal_data)),
            'samples': len(signal_data)
        }
    
    def reset_buffers(self):
        """Reset all channel buffers."""
        self.channel_buffers.clear()
        logger.info("Signal processing buffers reset")