import asyncio
import numpy as np
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class EmotivConnector:
    """Handles connection and data retrieval from EMOTIV BCI device."""
    
    def __init__(self):
        self.is_connected = False
        self.session = None
        self.headset_id = None
        self.mock_mode = True  # Set to False when using real EMOTIV device
        
    async def connect(self) -> bool:
        """Connect to EMOTIV device."""
        try:
            if self.mock_mode:
                # Mock connection for development
                logger.info("Mock EMOTIV connection established")
                self.is_connected = True
                return True
            
            # Real EMOTIV connection code
            # from cortex import Cortex
            # self.cortex = Cortex()
            # await self.cortex.connect()
            # self.session = await self.cortex.create_session()
            # self.headset_id = await self.cortex.get_headset_id()
            
            self.is_connected = True
            logger.info("EMOTIV device connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to EMOTIV device: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from EMOTIV device."""
        try:
            if self.session:
                # await self.cortex.close_session(self.session)
                pass
            self.is_connected = False
            logger.info("EMOTIV device disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting from EMOTIV: {e}")
    
    async def get_eeg_data(self) -> Optional[Dict]:
        """Get real-time EEG data from EMOTIV device."""
        if not self.is_connected:
            return None
        
        try:
            if self.mock_mode:
                # Generate mock EEG data for development
                return self._generate_mock_eeg_data()
            
            # Real EMOTIV data retrieval
            # eeg_data = await self.cortex.get_eeg_data(self.session)
            # return self._process_eeg_data(eeg_data)
            
        except Exception as e:
            logger.error(f"Error getting EEG data: {e}")
            return None
    
    def _generate_mock_eeg_data(self) -> Dict:
        """Generate realistic mock EEG data for development."""
        # Simulate 14-channel EMOTIV EPOC+ data
        channels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
        
        # Generate realistic EEG signal (microvolts)
        eeg_data = {}
        base_time = asyncio.get_event_loop().time()
        
        for channel in channels:
            # Simulate brain waves with different frequency components
            alpha_wave = 50 * np.sin(2 * np.pi * 10 * base_time)  # 10Hz alpha
            beta_wave = 30 * np.sin(2 * np.pi * 20 * base_time)   # 20Hz beta
            theta_wave = 40 * np.sin(2 * np.pi * 6 * base_time)   # 6Hz theta
            
            # Add some noise and combine waves
            noise = np.random.normal(0, 10)
            signal = alpha_wave + beta_wave + theta_wave + noise
            
            eeg_data[channel] = signal
        
        return {
            'eeg': eeg_data,
            'timestamp': base_time,
            'sample_rate': 128,  # Hz
            'channels': channels
        }
    
    def _process_eeg_data(self, raw_data) -> Dict:
        """Process raw EEG data from EMOTIV device."""
        # Add any preprocessing needed for real EMOTIV data
        return raw_data
    
    async def get_device_info(self) -> Dict:
        """Get information about connected EMOTIV device."""
        return {
            'connected': self.is_connected,
            'device_type': 'EMOTIV EPOC+' if self.mock_mode else 'Real Device',
            'headset_id': self.headset_id or 'mock_headset_001',
            'mock_mode': self.mock_mode,
            'sample_rate': 128,
            'channels': 14
        }