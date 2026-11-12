# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Part of VIRUS MUSIC BOT - API Reliability Architecture
# Maintained by Aspirant (https://t.me/aspirant_u)

import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "CLOSED"        # Normal operation: requests pass through
    OPEN = "OPEN"            # Tripped: requests are blocked to allow recovery
    HALF_OPEN = "HALF_OPEN"  # Trial: testing if provider has recovered


class CircuitBreaker:
    """
    Production-grade Circuit Breaker to prevent hammering failing providers.
    Transitions:
    - CLOSED -> OPEN when failure_count >= failure_threshold
    - OPEN -> HALF_OPEN after recovery_timeout seconds have passed
    - HALF_OPEN -> CLOSED on successful trial probe
    - HALF_OPEN -> OPEN on failed trial probe
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        """Determines if a request should be allowed through."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.recovery_timeout:
                logger.info(f"[CircuitBreaker:{self.name}] Recovery timeout elapsed. Transitioning OPEN -> HALF_OPEN.")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow limited probe in half-open state
            return True

        return False

    def record_success(self):
        """Records a successful call and recovers state if appropriate."""
        self.failure_count = 0
        self.success_count += 1
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"[CircuitBreaker:{self.name}] Probe succeeded! Transitioning HALF_OPEN -> CLOSED.")
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()

    def record_failure(self):
        """Records a failed call and trips circuit if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"[CircuitBreaker:{self.name}] Probe failed in HALF_OPEN. Re-opening circuit for {self.recovery_timeout}s.")
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            logger.warning(f"[CircuitBreaker:{self.name}] Failure threshold ({self.failure_threshold}) exceeded! Tripping circuit CLOSED -> OPEN.")
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def reset(self):
        """Manual reset of circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def get_status(self) -> dict:
        """Returns health telemetry."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "is_available": self.can_execute(),
            "time_in_state": round(time.time() - self.last_state_change, 1),
        }
