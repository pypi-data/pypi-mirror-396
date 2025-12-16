import grpc


class SeltzClient:
    """Low-level gRPC client for Seltz API."""

    def __init__(
        self, endpoint: str, api_key: str | None = None, insecure: bool = False
    ):
        """Initialize the Seltz gRPC client.

        Args:
            endpoint: The gRPC endpoint to connect to
            api_key: API key for authentication
            insecure: Whether to use insecure connection (default: False)
        """
        options = [
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.http2.min_time_between_pings_ms", 10000),
            ("grpc.http2.min_ping_interval_without_data_ms", 300000),
            ("grpc.http2.write_buffer_size", 0),
            ("grpc.http2.max_frame_size", 4194304),
        ]

        if insecure:
            channel = grpc.insecure_channel(endpoint, options=options)
        else:
            channel = grpc.secure_channel(
                endpoint, grpc.ssl_channel_credentials(), options=options
            )

        self.channel = channel
        self.api_key = api_key
