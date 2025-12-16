import ssl
import socket
import datetime


class Certificate:
    def __init__(self, hostname, expiring_days_threshold=30):
        self._hostname = hostname
        self._cert = None
        self._context = ssl.create_default_context()
        self._expiring_days_threshold = expiring_days_threshold

    def _fetch_certificate(self, timeout=5):
        """Fetches the SSL certificate from the server."""
        if self._cert is not None:
            # the certificate is already fetched
            return self._cert

        try:
            with socket.create_connection(
                (self._hostname, 443), timeout=timeout
            ) as sock:
                with self._context.wrap_socket(
                    sock, server_hostname=self._hostname
                ) as ssock:
                    self._cert = ssock.getpeercert()
        except (OSError, ssl.SSLError, ValueError) as e:
            raise ConnectionError(
                f"Could not retrieve certificate for {self._hostname}: {e}"
            )

    def expiry_date(self):
        """Returns the expiry date of the certificate as a datetime object."""

        if self._cert is None:
            self._fetch_certificate()

        try:
            expiry_date_str = self._cert.get("notAfter")

            if not expiry_date_str:
                raise ValueError("Expiry date not found in certificate.")

            return datetime.datetime.strptime(
                str(expiry_date_str), "%b %d %H:%M:%S %Y %Z"
            )

        except (ValueError, KeyError) as e:
            raise ValueError(f"Could not parse expiry date for {self._hostname}: {e}")

    def _days_until_expiration(self):
        """Returns the number of days until the certificate expires."""
        expiry_date = self.expiry_date()
        return (expiry_date - datetime.datetime.now()).days

    def get_expiry_status(self):
        """Returns a string indicating the expiry status of the certificate."""
        try:
            days_left = self._days_until_expiration()
            expiry_date = self.expiry_date().strftime("%Y-%m-%d")

            if self.is_expiring_soon():
                return (
                    f"Status: WARNING - Expires in {days_left} days (on {expiry_date})"
                )

            return f"Status: OK - Valid for {days_left} more days (expires on {expiry_date})"

        except ValueError as e:
            return f"Status: ERROR - Could not determine expiry status: {e}"

    def is_expiring_soon(self):
        """Checks if the certificate is expired or expiring within the threshold."""
        days_threshold = self._expiring_days_threshold
        try:
            days_left = self._days_until_expiration()
            return days_left <= days_threshold
        except ValueError:
            # If we can't determine the days left, treat it as an issue to be reported.
            return True
