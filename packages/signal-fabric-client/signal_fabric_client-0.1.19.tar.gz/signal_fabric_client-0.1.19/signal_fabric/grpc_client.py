"""
gRPC Client for Signal Fabric
Provides a clean interface for connecting to Signal Fabric server
"""

import json
import grpc
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Import generated protobuf code from package
from generated.signal_processor_pb2_grpc import SignalProcessorStub
from generated.signal_processor_pb2 import SignalRequest, SignalResponse


@dataclass
class SignalOutcome:
    """
    Represents the outcome of a signal computation
    Mirrors the server's Outcome/DetailedOutcome structure

    Fields:
        result: Signal computation result (parsed from serialization format, None if errors)
        computation: Name of the computation performed
        computed_at: Timestamp when signal was computed
        target: Target of the signal computation (e.g., 'BTC', 'ETH')
        result_format: Format used for result serialization (e.g., 'json')
        errors: Dictionary of error messages (key: error code, value: message)
        details: Dictionary of additional computation details
        handler_request: Parsed handler request data (can be dict, list, scalar, or None)
    """
    result: Optional[Any]
    computation: str
    computed_at: str
    target: Optional[str] = None
    result_format: Optional[str] = None
    errors: Dict[str, str] = None
    details: Dict[str, str] = None
    handler_request: Optional[Any] = None

    def __post_init__(self):
        """Initialize empty collections if None"""
        if self.errors is None:
            self.errors = {}
        if self.details is None:
            self.details = {}

    def has_errors(self) -> bool:
        """Check if outcome contains errors"""
        return len(self.errors) > 0

    def is_detailed(self) -> bool:
        """Check if this is a detailed outcome (has errors or details)"""
        return len(self.errors) > 0 or len(self.details) > 0


class GrpcClient:
    """
    gRPC client for Signal Fabric server

    Usage:
        from signal_fabric import GrpcClient

        # Connect to server
        client = GrpcClient(host='localhost', port=50051)

        # Process a signal
        outcome = client.process_signal(
            target='BTC',
            signal_name='trend',
            signal_op='analyze',
            handler_request={'period': 14}
        )

        # Check result
        if outcome.has_errors():
            print(f"Errors: {outcome.errors}")
        else:
            print(f"Result: {outcome.result}")
            # handler_request is parsed from JSON automatically
            if outcome.handler_request:
                print(f"Request params: {outcome.handler_request}")
    """

    def __init__(self, host: str = 'localhost', port: int = 50051, timeout_sec: int = 30,
                 ca_cert_path: str = None, use_tls: bool = True):
        """
        Initialize gRPC client

        Args:
            host: Server hostname or IP address
            port: Server port number
            timeout_sec: Request timeout in seconds
            ca_cert_path: Path to CA certificate for server verification (optional, uses system CAs if not provided)
            use_tls: Whether to use TLS/SSL encryption (default: True)
        """
        self.host = host
        self.port = port
        self.timeout_sec = timeout_sec
        self.ca_cert_path = ca_cert_path
        self.use_tls = use_tls
        self.server_address = f'{host}:{port}'
        self._channel = None
        self._stub = None

    def connect(self):
        """
        Establish connection to the server
        Creates gRPC channel and stub with or without TLS encryption based on use_tls setting
        """
        if self.use_tls:
            # Use TLS - secure channel
            if self.ca_cert_path:
                # Use custom CA certificate
                with open(self.ca_cert_path, 'rb') as f:
                    ca_cert = f.read()
                credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)
            else:
                # Use system CA certificates
                credentials = grpc.ssl_channel_credentials()

            self._channel = grpc.secure_channel(self.server_address, credentials)
        else:
            # Use insecure channel (no TLS)
            self._channel = grpc.insecure_channel(self.server_address)

        self._stub = SignalProcessorStub(self._channel)

    def disconnect(self):
        """
        Close the connection to the server
        """
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None

    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._stub is not None

    def _ensure_connected(self):
        """Ensure client is connected, connect if not"""
        if not self.is_connected():
            self.connect()

    @staticmethod
    def _parse_handler_request(json_str: Optional[str]) -> Optional[Any]:
        """
        Parse handler_request JSON string to Python object

        Args:
            json_str: JSON string from protobuf response

        Returns:
            Parsed Python object (dict, list, scalar, etc.) or None if empty/invalid
        """
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Return the raw string if JSON parsing fails
            return json_str

    @staticmethod
    def _parse_result(result_str: Optional[str], result_format: Optional[str]) -> Optional[Any]:
        """
        Parse result string according to the specified format

        Args:
            result_str: Serialized result string from protobuf response
            result_format: Format of serialization (e.g., 'json')

        Returns:
            Parsed Python object or None if result is None

        Raises:
            ValueError: If result_format is not None and not 'json'
        """
        if result_str is None:
            return None

        # If no format specified, return as-is (raw string or unformatted result)
        if result_format is None:
            return result_str

        # Only 'json' format is supported
        if result_format == 'json':
            try:
                return json.loads(result_str)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, raise an exception
                raise ValueError(f"Failed to parse result as JSON: {e}")
        else:
            # Unsupported format
            raise ValueError(f"Unsupported result format: '{result_format}'. Only 'json' is supported.")

    def process_signal(
        self,
        target: str,
        signal_name: str,
        signal_op: str,
        handler_request: Optional[Dict[str, Any]] = None
    ) -> SignalOutcome:
        """
        Process a signal request

        Args:
            target: Target for signal computation (e.g., 'BTC', 'ETH')
            signal_name: Signal handler name or profile name (e.g., 'hello', 'happy_hello')
            signal_op: Signal operation to perform (e.g., 'greet', 'analyze')
            handler_request: Optional request data as dictionary

        Returns:
            SignalOutcome containing the result

        Raises:
            grpc.RpcError: If the RPC call fails
        """
        self._ensure_connected()

        # Convert handler_request dict to JSON string if provided
        handler_request_json = None
        if handler_request is not None:
            handler_request_json = json.dumps(handler_request)

        # Build gRPC request
        request = SignalRequest(
            target=target,
            signal_name=signal_name,
            signal_op=signal_op,
            handler_request=handler_request_json
        )

        # Make RPC call
        try:
            response: SignalResponse = self._stub.ProcessSignal(
                request,
                timeout=self.timeout_sec
            )

            # Convert response to SignalOutcome
            # Protobuf map fields need explicit dict() conversion
            # Parse result according to format and handler_request JSON to Python object
            result_raw = response.result if response.HasField('result') else None
            result_format = response.result_format if response.HasField('result_format') else None
            handler_request_raw = response.handler_request if response.HasField('handler_request') else None

            return SignalOutcome(
                result=self._parse_result(result_raw, result_format),
                computation=response.computation,
                computed_at=response.computed_at,
                target=response.target,
                result_format=result_format,
                errors={k: v for k, v in response.errors.items()},
                details={k: v for k, v in response.details.items()},
                handler_request=self._parse_handler_request(handler_request_raw)
            )

        except grpc.RpcError as e:
            # Wrap gRPC errors in SignalOutcome for consistent error handling
            return SignalOutcome(
                result=None,
                computation="gRPC Error",
                computed_at="",
                target=None,
                result_format=None,
                errors={"GRPC_ERROR": f"{e.code()}: {e.details()}"},
                details={"grpc_code": str(e.code())},
                handler_request=None
            )

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
