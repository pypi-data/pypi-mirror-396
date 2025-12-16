"""Spread Monitoring Configuration

This module provides configuration types for bid/ask spread monitoring.
Introduced with OTB-284 enhancement for configurable spread monitoring.

The spread monitoring feature detects when the bid/ask spread of an option
exceeds a configurable threshold, which may indicate illiquid market conditions
or potential pricing issues.

Example config.yaml:
    general:
      spread_monitoring:
        mode: all  # 'off', 'active_strikes', or 'all'
        multiplier: 2.0
        min_ask_threshold: 0.30
"""

from dataclasses import dataclass
from enum import Enum


class SpreadMonitoringMode(Enum):
    """
    Defines the monitoring mode for bid/ask spread checks.
    
    Attributes:
        OFF: Spread monitoring is completely disabled
        ACTIVE_STRIKES: Only monitor strikes that are part of active trades
        ALL: Monitor all strikes in the option chain (default behavior)
    """
    OFF = 'off'
    ACTIVE_STRIKES = 'active_strikes'
    ALL = 'all'


@dataclass
class SpreadMonitoringConfig:
    """
    Configuration for bid/ask spread monitoring.
    
    The spread is considered "high" when:
        spread = ask_price - bid_price
        spread > bid_price * multiplier
    
    Attributes:
        mode: Determines which strikes to monitor (default: OFF)
        multiplier: The ask/bid ratio threshold for high spread detection
        min_ask_threshold: Minimum ask price to trigger monitoring
    """
    mode: SpreadMonitoringMode = SpreadMonitoringMode.OFF
    multiplier: float = 2.0
    min_ask_threshold: float = 0.30
    
    @classmethod
    def from_config_dict(cls, config_dict: dict | None) -> 'SpreadMonitoringConfig':
        """
        Creates a SpreadMonitoringConfig from a configuration dictionary.
        
        Args:
            config_dict: Dictionary with spread_monitoring configuration
            
        Returns:
            SpreadMonitoringConfig instance with values from dict or defaults
            
        Example:
            >>> config_dict = {'mode': 'active_strikes', 'multiplier': 1.5}
            >>> config = SpreadMonitoringConfig.from_config_dict(config_dict)
            >>> config.mode
            <SpreadMonitoringMode.ACTIVE_STRIKES: 'active_strikes'>
        """
        if not config_dict:
            return cls()
        
        mode_str = config_dict.get('mode', 'off')
        try:
            mode = SpreadMonitoringMode(mode_str)
        except ValueError:
            # Fall back to OFF if invalid mode string provided
            mode = SpreadMonitoringMode.OFF
            
        return cls(
            mode=mode,
            multiplier=config_dict.get('multiplier', 2.0),
            min_ask_threshold=config_dict.get('min_ask_threshold', 0.30)
        )
