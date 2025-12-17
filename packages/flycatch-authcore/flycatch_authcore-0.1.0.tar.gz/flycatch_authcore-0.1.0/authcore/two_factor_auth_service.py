from __future__ import annotations
from .config import TwoFAConfig
import random
import string
from typing import Dict, Any, Tuple
import time
import threading


class OtpExpiredError(Exception):
    pass


class InvalidOtpError(Exception):
    pass


class TransportNotFoundError(Exception):
    pass


class TooManyAttemptsError(Exception):
    pass


class TwoFactorAuth:
    """
    Best-effort hardening:
    - Attempt limiting is done in-process by default (thread-safe).
    - For true production (multi-worker/pod), implement attempts in your OTP store itself.
    """
    def __init__(self, config: TwoFAConfig):
        if not config.enabled:
            raise ValueError("Two Factor Authentication is disabled in config.")
        if not config.store_otp or not config.get_stored_otp:
            raise ValueError("Both store_otp and get_stored_otp must be implemented.")
        self.config = config

        self._attempt_lock = threading.RLock()
        # user_id -> (window_start_ts, attempts)
        self._attempts: Dict[str, Tuple[float, int]] = {}

    def _generate_otp(self) -> str:
        if self.config.otp_type == "numeric":
            chars = string.digits
        elif self.config.otp_type == "alphanumeric":
            chars = string.ascii_letters + string.digits
        else:
            raise ValueError("Invalid OTP type")
        return "".join(random.choice(chars) for _ in range(self.config.otp_length))

    def _uid(self, user: Dict[str, Any]) -> str:
        return str(user.get("id"))

    def _check_and_inc_attempt(self, user_id: str) -> None:
        if self.config.max_attempts <= 0:
            return

        now = time.time()
        with self._attempt_lock:
            wstart, cnt = self._attempts.get(user_id, (0.0, 0))
            if (now - wstart) > float(self.config.attempt_window_seconds):
                wstart, cnt = now, 0

            if cnt >= int(self.config.max_attempts):
                raise TooManyAttemptsError("Too many OTP attempts. Try again later.")

            self._attempts[user_id] = (wstart, cnt + 1)

    def _clear_attempts(self, user_id: str) -> None:
        with self._attempt_lock:
            self._attempts.pop(user_id, None)

    async def initiate_2fa(self, user: Dict[str, Any]) -> None:
        otp = self._generate_otp()
        expires_in = self.config.otp_expires_in

        if self.config.on_otp_generated:
            await self.config.on_otp_generated(otp, user)

        await self.config.store_otp(user["id"], otp, expires_in)

        if not self.config.transport:
            raise TransportNotFoundError("No transport configured to send OTP.")

        await self.config.transport(otp, user)

        if self.config.on_otp_sent:
            await self.config.on_otp_sent(user)

        # reset attempts on new OTP
        self._clear_attempts(self._uid(user))

    async def verify_otp(self, user: Dict[str, Any], input_otp: str) -> bool:
        user_id = self._uid(user)

        self._check_and_inc_attempt(user_id)

        stored_otp = await self.config.get_stored_otp(user["id"])
        if not stored_otp:
            error = OtpExpiredError("OTP expired or invalid.")
            if self.config.on_verify_fail:
                await self.config.on_verify_fail(user, error)
            raise error

        if str(stored_otp) != str(input_otp):
            error = InvalidOtpError("Invalid OTP.")
            if self.config.on_verify_fail:
                await self.config.on_verify_fail(user, error)
            raise error

        if self.config.clear_otp:
            await self.config.clear_otp(user["id"])

        if self.config.on_verify_success:
            await self.config.on_verify_success(user)

        self._clear_attempts(user_id)
        return True
