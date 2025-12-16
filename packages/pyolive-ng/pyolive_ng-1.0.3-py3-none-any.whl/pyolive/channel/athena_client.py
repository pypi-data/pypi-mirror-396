"""
Athena Broker 클라이언트 (async 버전)
MSM 프로토콜을 사용하여 Athena Broker와 통신
"""
import struct
import time
import uuid
import asyncio
from typing import Optional, Tuple
from pynng import Req0, Push0, Timeout
from pynng.exceptions import ConnectionRefused

# Opcodes
MSG_OP_CONNECT = 0x01
MSG_OP_CONNACK = 0x02
MSG_OP_PUBLISH = 0x03
MSG_OP_PUBACK = 0x04
MSG_OP_SUBSCRIBE = 0x05
MSG_OP_SUBACK = 0x06
MSG_OP_UNSUBSCRIBE = 0x07
MSG_OP_UNSUBACK = 0x08
MSG_OP_ACK = 0x0A
MSG_OP_CONSUME = 0x1A
MSG_OP_DELIVER = 0x1B
MSG_OP_NACK = 0x1C
MSG_OP_QUEUE_DECLARE = 0x10
MSG_OP_QUEUE_DECLARE_OK = 0x11
MSG_OP_QUEUE_BIND = 0x12
MSG_OP_QUEUE_BIND_OK = 0x13

# Response codes
MSM_RESP_SUCCESS = 0x00
MSM_RESP_TIMEOUT = 0x0A  # Timeout

# Protocol version
MSM_PROTOCOL_VERSION = 0x01  # Protocol version 1

# Timeout constants (from include/mod/msm_defs.h)
MSM_TIMEOUT = 5  # 아답터 수신대기 시간(초)
MSM_POLL_INTERVAL_MS = 10  # 브로커 폴링 간격 (밀리초)

# Default exchange
DEFAULT_EXCHANGE = "amq.topic"


class AthenaException(Exception):
    """Athena 클라이언트 예외"""
    pass


class AthenaMessage:
    """수신된 메시지"""
    def __init__(self, delivery_tag: int, queue_name: str, exchange: str,
                 routing_key: str, message_id: int, payload: bytes):
        self.delivery_tag = delivery_tag
        self.queue_name = queue_name
        self.exchange = exchange
        self.routing_key = routing_key
        self.message_id = message_id
        self.payload = payload
        self._body = None

    def get_payload_str(self, encoding='utf-8') -> str:
        """페이로드를 문자열로 반환"""
        return self.payload.decode(encoding)

    @property
    def body(self) -> bytes:
        """페이로드"""
        return self.payload

    def __repr__(self):
        return (f"AthenaMessage(tag={self.delivery_tag}, queue={self.queue_name}, "
                f"exchange={self.exchange}, routing_key={self.routing_key}, id={self.message_id})")


class AthenaClient:
    """Athena Broker 클라이언트 (async 지원)"""

    def __init__(self, broker_url: str = "tcp://localhost:2736",
                 client_id: Optional[str] = None, timeout_ms: Optional[int] = None):
        """
        Args:
            broker_url: Broker URL (예: "tcp://localhost:2736")
            client_id: 클라이언트 ID (None이면 자동 생성)
            timeout_ms: 기본 타임아웃 (밀리초, None이면 MSM_TIMEOUT 사용)
        """
        self.broker_url = broker_url
        self.client_id = client_id or self._generate_client_id()
        self.timeout_ms = timeout_ms or (MSM_TIMEOUT * 1000)  # MSM_TIMEOUT 초를 밀리초로 변환
        self.socket: Optional[Req0] = None
        self.push_socket: Optional[Push0] = None  # PUSH 소켓 (publish 전용, 비동기)
        self.push_connected = False  # PUSH 소켓 연결 상태
        self.connected = False
        self._lock = asyncio.Lock()
        self._push_lock = asyncio.Lock()  # PUSH 소켓 전용 lock

    @staticmethod
    def _generate_client_id() -> str:
        """고유한 클라이언트 ID 생성"""
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"python_client_{timestamp}_{unique_id}"

    @staticmethod
    def _bytes_to_hex(data: bytes) -> str:
        """바이트 배열을 16진수 문자열로 변환 (디버깅용)"""
        return ' '.join(f'{b:02x}' for b in data)

    def _make_push_url(self, url: str) -> str:
        """
        Control URL에서 PUSH URL 생성 (port + 2)
        예: tcp://localhost:2736 -> tcp://localhost:2738
        """
        import re
        match = re.match(r'^(tcp://[^:]+):(\d+)$', url)
        if match:
            host_part = match.group(1)
            port = int(match.group(2))
            return f"{host_part}:{port + 2}"
        return url  # 파싱 실패 시 원본 반환

    async def connect(self, timeout_ms: Optional[int] = None):
        """Broker에 연결"""
        timeout = timeout_ms or self.timeout_ms
        self.socket = None
        self.push_socket = None

        try:
            # NNG REQ 소켓 생성 (Control 채널)
            self.socket = Req0(dial=self.broker_url, send_timeout=timeout, recv_timeout=timeout)

            # CONNECT 메시지 전송
            connect_msg = self._build_connect_message()
            await asyncio.to_thread(self.socket.send, connect_msg)

            # CONNACK 응답 수신
            # CONNACK은 고정 길이(2 bytes)이므로 이를 검증해야 함
            response = await asyncio.to_thread(self.socket.recv)

            if len(response) < 2 or response[0] != MSG_OP_CONNACK:
                raise AthenaException("Invalid CONNACK response")

            if response[1] != MSM_RESP_SUCCESS:
                raise AthenaException(f"Connection failed: response_code=0x{response[1]:02x}")

            # PUSH 소켓 생성 (Data 채널 - Publish 전용)
            # port + 2로 연결 (예: 2736 -> 2738)
            push_url = self._make_push_url(self.broker_url)
            try:
                self.push_socket = Push0(send_timeout=1000)  # PUSH는 짧은 timeout
                self.push_socket.dial(push_url, block=False)  # Non-blocking 연결
                self.push_connected = True
            except Exception:
                # PUSH 소켓 연결 실패 시 REQ/REP 폴백 모드로 동작
                if self.push_socket:
                    try:
                        self.push_socket.close()
                    except:
                        pass
                self.push_socket = None
                self.push_connected = False

            self.connected = True

        except Exception as e:
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            if self.push_socket:
                try:
                    self.push_socket.close()
                except:
                    pass
                self.push_socket = None

            # 에러 메시지 상세화
            error_msg = str(e)
            raise AthenaException(
                f"Failed to connect to Athena Broker at {self.broker_url}.\n"
                f"Error type: {type(e).__name__}\n"
                f"Error message: {error_msg}\n"
                f"\nPlease check:\n"
                f"  1. Athena Broker server is running and accessible\n"
                f"  2. Configuration file: $ATHENA_HOME/etc/athena-agent.yaml\n"
                f"  3. Broker URL: {self.broker_url}"
            )

    def _build_connect_message(self) -> bytes:
        """
        CONNECT 메시지 생성
        
        서버는 sizeof(msm_connect_msg_t) = 160 bytes를 기대합니다.
        총 크기: 161 bytes (opcode 1 + 구조체 160)
        """
        client_id_bytes = self.client_id.encode('utf-8')
        client_id_len = min(len(client_id_bytes), 127)  # 최대 128 bytes (null 포함)

        msg = struct.pack('>B', MSG_OP_CONNECT)              # opcode (1 byte)
        msg += struct.pack('>B', MSM_PROTOCOL_VERSION)       # protocol_version (1 byte, offset 0)
        msg += client_id_bytes[:client_id_len]                # client_id (128 bytes, offset 1)
        msg += b'\x00' * (128 - client_id_len)                # null padding
        msg += b'\x00' * 3                                    # padding (3 bytes, offset 129-131)
        msg += struct.pack('>I', 60)                         # keepalive (4 bytes, offset 132, 60s)
        msg += struct.pack('>H', 0)                          # flags (2 bytes, offset 136)
        msg += b'\x00' * 6                                    # padding (6 bytes, offset 138-143)
        msg += struct.pack('>Q', 0)                          # username pointer (8 bytes, offset 144)
        msg += struct.pack('>Q', 0)                          # password pointer (8 bytes, offset 152)

        return msg

    async def publish(self, topic: str, payload: bytes, exchange: Optional[str] = None):
        """
        메시지 발행

        PUSH 소켓이 사용 가능하면 비동기 fire & forget 방식으로 전송하고,
        그렇지 않으면 기존 REQ/REP 방식으로 폴백합니다.

        Args:
            topic: 토픽/라우팅 키
            payload: 메시지 내용 (bytes)
            exchange: Exchange 이름 (None이면 기본값 사용)
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        effective_exchange = exchange or DEFAULT_EXCHANGE
        publish_msg = self._build_publish_message(effective_exchange, topic, payload)

        if self.push_connected and self.push_socket:
            # PUSH 소켓 사용 (비동기, 응답 대기 없음 - fire & forget)
            async with self._push_lock:
                try:
                    await asyncio.to_thread(self.push_socket.send, publish_msg)
                    return  # 성공 시 바로 리턴
                except Exception:
                    # PUSH 실패 시 연결 상태 해제하고 REQ/REP 폴백
                    self.push_connected = False

        # REQ/REP 폴백 (동기, PUBACK 응답 대기)
        await self._publish_via_req(publish_msg)

    async def _publish_via_req(self, publish_msg: bytes):
        """REQ/REP를 통한 publish (fallback)"""
        async with self._lock:
            try:
                await asyncio.to_thread(self.socket.send, publish_msg)

                # PUBACK 수신 (타임아웃 설정)
                old_timeout = self.socket.recv_timeout
                try:
                    self.socket.recv_timeout = 5000  # 5초 타임아웃
                    response = await asyncio.to_thread(self.socket.recv)

                    if len(response) < 1:
                        raise AthenaException("Empty PUBACK response")

                    if response[0] != MSG_OP_PUBACK:
                        error_code = response[1] if len(response) >= 2 else 0xFF
                        raise AthenaException(f"Invalid PUBACK response: opcode=0x{response[0]:02x}, error=0x{error_code:02x}")
                except Timeout:
                    raise AthenaException("PUBACK timeout - broker did not respond")
                finally:
                    self.socket.recv_timeout = old_timeout

            except AthenaException:
                raise
            except Exception as e:
                raise AthenaException(f"Failed to publish via REQ/REP: {e}")

    async def publish_str(self, topic: str, message: str, encoding='utf-8', exchange: Optional[str] = None):
        """문자열 메시지 발행 (편의 메서드)"""
        await self.publish(topic, message.encode(encoding), exchange)

    def _build_publish_message(self, exchange: str, topic: str, payload: bytes) -> bytes:
        """PUBLISH 메시지 생성"""
        exchange_bytes = exchange.encode('utf-8')
        topic_bytes = topic.encode('utf-8')

        msg = struct.pack('>B', MSG_OP_PUBLISH)              # opcode
        msg += exchange_bytes                                # exchange
        msg += b'\x00'                                       # null terminator
        msg += topic_bytes                                   # topic
        msg += b'\x00'                                       # null terminator
        msg += payload                                       # payload

        return msg

    async def queue_declare(self, queue_name: Optional[str] = None, max_size: int = 10000,
                           ttl: int = 0, persistent: bool = False, exclusive: bool = False,
                           auto_delete: bool = False, prefix: str = "worker") -> Tuple[str, int, int]:
        """
        큐 선언

        Args:
            queue_name: 큐 이름 (None이면 임시 큐 생성)
            max_size: 최대 메시지 개수
            ttl: 메시지 TTL (초, 0 = 무제한)
            persistent: 영속성 여부 (bit 0)
            exclusive: 독점 큐 여부 (bit 1)
            auto_delete: 자동 삭제 여부 (bit 2)
            prefix: 큐 접두사 (임시 큐 생성 시 사용, 기본값: "worker")

        Returns:
            (queue_name, message_count, consumer_count) 튜플
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        async with self._lock:
            try:
                # flags 계산
                flags = 0
                if persistent: flags |= 0x01
                if exclusive: flags |= 0x02
                if auto_delete: flags |= 0x04

                # queue_name이 None이면 빈 문자열로 처리 (서버가 이름 생성)
                target_queue_name = queue_name or ""

                declare_msg = self._build_queue_declare_message(
                    target_queue_name, max_size, ttl, flags, prefix
                )
                await asyncio.to_thread(self.socket.send, declare_msg)

                # QUEUE_DECLARE_OK 수신
                # 구조: [opcode:1][queue_name:256][message_count:4][consumer_count:4]
                response = await asyncio.to_thread(self.socket.recv)

                if len(response) < 1 or response[0] != MSG_OP_QUEUE_DECLARE_OK:
                    raise AthenaException("Invalid QUEUE_DECLARE_OK response")
                
                if len(response) < 265:
                     raise AthenaException(f"QUEUE_DECLARE_OK response too short: {len(response)} bytes")

                # 응답 파싱
                offset = 1
                
                # queue_name (256 bytes)
                qname_bytes = response[offset:offset+256]
                null_index = qname_bytes.find(b'\x00')
                if null_index >= 0:
                    declared_queue_name = qname_bytes[:null_index].decode('utf-8')
                else:
                    declared_queue_name = qname_bytes.decode('utf-8')
                offset += 256
                
                # message_count (4 bytes)
                message_count = struct.unpack_from('>I', response, offset)[0]
                offset += 4
                
                # consumer_count (4 bytes)
                consumer_count = struct.unpack_from('>I', response, offset)[0]
                
                return declared_queue_name, message_count, consumer_count
            
            except Exception as e:
                raise AthenaException(f"Failed to declare queue: {e}")

    async def queue_bind(self, queue_name: str, exchange: str, routing_key: str):
        """
        큐 바인딩

        Args:
            queue_name: 큐 이름
            exchange: Exchange 이름
            routing_key: 라우팅 키
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        async with self._lock:
            try:
                bind_msg = self._build_queue_bind_message(queue_name, exchange, routing_key)
                await asyncio.to_thread(self.socket.send, bind_msg)

                # QUEUE_BIND_OK 수신 (0x13)
                # 구조: [opcode:1][result_code:1]
                response = await asyncio.to_thread(self.socket.recv)

                if len(response) < 2 or response[0] != MSG_OP_QUEUE_BIND_OK:
                    raise AthenaException(f"Invalid QUEUE_BIND_OK response: {self._bytes_to_hex(response)}")
                
                result_code = response[1]
                if result_code != MSM_RESP_SUCCESS:
                    raise AthenaException(f"Queue bind failed: result_code=0x{result_code:02x}")

            except Exception as e:
                raise AthenaException(f"Failed to bind queue: {e}")

    def _build_queue_bind_message(self, queue_name: str, exchange: str, routing_key: str) -> bytes:
        """
        QUEUE_BIND 메시지 생성
        구조 (protocol.h):
        typedef struct {
            char queue_name[256];
            char binding_key[256];  /* Topic pattern */
            char exchange[256];     /* Exchange name */
        } queue_bind_msg_t;
        
        총 크기: 768 bytes + Opcode(1) = 769 bytes
        """
        queue_bytes = queue_name.encode('utf-8')
        exchange_bytes = exchange.encode('utf-8')
        routing_key_bytes = routing_key.encode('utf-8')

        msg = struct.pack('>B', MSG_OP_QUEUE_BIND)           # opcode
        
        # 1. queue_name (256)
        q_len = min(len(queue_bytes), 255)
        msg += queue_bytes[:q_len]
        msg += b'\x00' * (256 - q_len)
        
        # 2. binding_key (routing_key) (256)
        r_len = min(len(routing_key_bytes), 255)
        msg += routing_key_bytes[:r_len]
        msg += b'\x00' * (256 - r_len)

        # 3. exchange (256)
        e_len = min(len(exchange_bytes), 255)
        msg += exchange_bytes[:e_len]
        msg += b'\x00' * (256 - e_len)
        
        return msg

    def _build_queue_declare_message(self, queue_name: str, max_size: int,
                                    ttl: int, flags: int, prefix: str) -> bytes:
        """
        QUEUE_DECLARE 메시지 생성
        
        구조체 정의 (include/mod/msm_protocol.h):
        typedef struct {
            char queue_name[256];
            uint8_t flags;
            // [패딩 3 bytes]
            uint32_t max_size;
            uint32_t ttl;
            char queue_prefix[64];
        } msm_queue_declare_msg_t;
        
        총 크기: 332 bytes + Opcode(1) = 333 bytes
        """
        queue_bytes = queue_name.encode('utf-8')
        queue_len = min(len(queue_bytes), 255)  # 최대 256 bytes (null 포함)
        
        prefix_bytes = prefix.encode('utf-8')
        prefix_len = min(len(prefix_bytes), 63) # 최대 64 bytes (null 포함)

        msg = struct.pack('>B', MSG_OP_QUEUE_DECLARE)        # opcode (1)
        msg += queue_bytes[:queue_len]                       # queue_name (256 bytes)
        msg += b'\x00' * (256 - queue_len)                    # null padding
        msg += struct.pack('>B', flags)                      # flags (1 byte)
        msg += b'\x00' * 3                                    # padding (3 bytes)
        msg += struct.pack('>I', max_size)                    # max_size (4 bytes, Big-Endian)
        msg += struct.pack('>I', ttl)                         # ttl (4 bytes, Big-Endian)
        msg += prefix_bytes[:prefix_len]                     # queue_prefix (64 bytes)
        msg += b'\x00' * (64 - prefix_len)                    # null padding

        return msg

    async def subscribe(self, topic_pattern: str, qos: int = 0) -> int:
        """
        토픽 구독

        Args:
            topic_pattern: 토픽 패턴 (와일드카드 지원: *, #)
            qos: QoS 레벨 (0, 1, 또는 2)

        Returns:
            구독 ID
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        async with self._lock:
            try:
                subscribe_msg = self._build_subscribe_message(topic_pattern, qos)
                await asyncio.to_thread(self.socket.send, subscribe_msg)

                # SUBACK 응답 수신
                response = await asyncio.to_thread(self.socket.recv)

                if len(response) < 10 or response[0] != MSG_OP_SUBACK:
                    raise AthenaException("Invalid SUBACK response")

                if response[1] != MSM_RESP_SUCCESS:
                    raise AthenaException(f"Subscribe failed: {response[1]}")

                # subscription_id 추출 (8 bytes, Big-Endian)
                subscription_id = struct.unpack_from('>Q', response, 2)[0]
                return subscription_id

            except Exception as e:
                raise AthenaException(f"Failed to subscribe: {e}")

    def _build_subscribe_message(self, topic_pattern: str, qos: int) -> bytes:
        """
        SUBSCRIBE 메시지 생성
        
        중요: 구조체 크기는 264 bytes입니다.
        실제 전송 크기: opcode(1) + 구조체(264) = 265 bytes
        """
        pattern_bytes = topic_pattern.encode('utf-8')
        pattern_len = min(len(pattern_bytes), 255)  # 최대 256 bytes (null 포함)
        
        msg = struct.pack('>B', MSG_OP_SUBSCRIBE)          # opcode
        msg += struct.pack('>I', 0)                        # subscription_id (4 bytes, offset 0)
        msg += pattern_bytes[:pattern_len]                 # topic_pattern (256 bytes, offset 4)
        msg += b'\x00' * (256 - pattern_len)               # null padding
        msg += struct.pack('>B', qos)                      # qos (1 byte, offset 260)
        msg += struct.pack('>H', 0)                        # flags (2 bytes, offset 262)
        
        return msg

    async def consume(self, queue_name: str, timeout_ms: Optional[int] = None) -> Optional[AthenaMessage]:
        """
        큐에서 메시지 소비 (블로킹)
        서버 코드(msm_adapter.c)와 동일하게 MSM_TIMEOUT 사용

        Args:
            queue_name: 큐 이름
            timeout_ms: 타임아웃 (밀리초, None이면 MSM_TIMEOUT 사용)

        Returns:
            수신된 메시지 (타임아웃 시 None)
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        # 서버 코드와 동일: MSM_TIMEOUT * 1000 (5초)
        timeout = timeout_ms or (MSM_TIMEOUT * 1000)
        
        old_timeout = self.socket.recv_timeout
        try:
            # 타임아웃 임시 변경 (서버 처리 시간 고려하여 약간 여유 있게)
            self.socket.recv_timeout = timeout + 1000

            async with self._lock:
                consume_msg = self._build_consume_message(queue_name, timeout)
                await asyncio.to_thread(self.socket.send, consume_msg)

                # DELIVER 메시지 수신
                try:
                    response = await asyncio.to_thread(self.socket.recv)
                except Timeout:
                    return None

                if len(response) < 1:
                    return None

                if response[0] != MSG_OP_DELIVER:
                    # 에러 응답 처리 (0xFF)
                    if response[0] == 0xFF and len(response) >= 2:
                        error_code = response[1]
                        if error_code == MSM_RESP_TIMEOUT:
                            # 타임아웃은 정상적인 "메시지 없음" 상태
                            return None
                    
                    return None

                return self._parse_deliver_message(response)

        except Timeout:
            return None
        except Exception as e:
            raise AthenaException(f"Failed to consume: {e}")
        finally:
            self.socket.recv_timeout = old_timeout

    def _build_consume_message(self, queue_name: str, timeout_ms: int) -> bytes:
        """
        CONSUME 메시지 생성
        
        중요: 구조체 크기는 264 bytes입니다 (패딩 포함).
        실제 전송 크기: opcode(1) + 구조체(264) = 265 bytes
        """
        queue_bytes = queue_name.encode('utf-8')
        queue_len = min(len(queue_bytes), 255)  # 최대 256 bytes (null 포함)

        msg = struct.pack('>B', MSG_OP_CONSUME)              # opcode
        msg += queue_bytes[:queue_len]                       # queue_name (256 bytes, offset 0)
        msg += b'\x00' * (256 - queue_len)                    # null padding
        msg += struct.pack('>H', 1)                          # prefetch_count (2 bytes, offset 256)
        msg += struct.pack('>B', 0)                           # flags (1 byte, offset 258)
        msg += b'\x00'                                        # padding (1 byte, offset 259)
        msg += struct.pack('>I', timeout_ms)                 # timeout_ms (4 bytes, offset 260)

        return msg

    def _parse_deliver_message(self, data: bytes) -> AthenaMessage:
        """
        DELIVER 메시지 파싱
        고정 헤더 크기: 800 bytes
        """
        if len(data) < 800:
            raise AthenaException(f"DELIVER message too small: {len(data)} bytes")

        offset = 0

        # opcode (1 byte)
        opcode = data[offset]
        if opcode != MSG_OP_DELIVER:
            raise AthenaException(f"Invalid DELIVER opcode: 0x{opcode:02x}")
        offset += 1

        # delivery_tag (8 bytes, Big-Endian)
        delivery_tag = struct.unpack_from('>Q', data, offset)[0]
        offset += 8

        # queue_name (256 bytes, null-terminated)
        queue_name_bytes = data[offset:offset+256]
        null_index = queue_name_bytes.find(b'\x00')
        if null_index >= 0:
            queue_name = queue_name_bytes[:null_index].decode('utf-8')
        else:
            queue_name = queue_name_bytes.rstrip(b'\x00').decode('utf-8')
        offset += 256

        # exchange (256 bytes, null-terminated)
        exchange_bytes = data[offset:offset+256]
        null_index = exchange_bytes.find(b'\x00')
        if null_index >= 0:
            exchange = exchange_bytes[:null_index].decode('utf-8')
        else:
            exchange = exchange_bytes.rstrip(b'\x00').decode('utf-8')
        offset += 256

        # routing_key (256 bytes, null-terminated)
        routing_key_bytes = data[offset:offset+256]
        null_index = routing_key_bytes.find(b'\x00')
        if null_index >= 0:
            routing_key = routing_key_bytes[:null_index].decode('utf-8')
        else:
            routing_key = routing_key_bytes.rstrip(b'\x00').decode('utf-8')
        offset += 256

        # message_id (8 bytes) - 서버 코드에서 memcpy 사용, 네이티브 바이트 순서
        # 프로토콜 문서는 Big-Endian을 명시하지만, 서버 구현은 memcpy 사용
        # 일단 Big-Endian으로 시도하고, 값이 비정상적이면 네이티브로 재시도
        message_id = struct.unpack_from('>Q', data, offset)[0]
        offset += 8

        # payload_len (4 bytes) - 서버 코드에서 memcpy 사용
        # 서버가 네이티브 바이트 순서로 전송하므로, 시스템 바이트 순서 확인 필요
        import sys
        payload_len_bytes = data[offset:offset+4]
        
        # 먼저 Big-Endian으로 시도 (프로토콜 문서 명시)
        payload_len_be = struct.unpack_from('>I', data, offset)[0]
        
        # 값이 비정상적으로 크면 (16MB 이상) 네이티브 바이트 순서로 재시도
        if payload_len_be > 16 * 1024 * 1024:
            # Little-Endian으로 재시도
            payload_len_le = struct.unpack_from('<I', data, offset)[0]
            if payload_len_le <= 16 * 1024 * 1024:
                # Little-Endian이 합리적이면 사용
                payload_len = payload_len_le
            else:
                # 둘 다 비정상적이면 에러
                raise AthenaException(
                    f"Invalid payload_len: BE={payload_len_be}, LE={payload_len_le} "
                    f"(hex: {self._bytes_to_hex(payload_len_bytes)}). "
                    f"Message may be corrupted."
                )
        else:
            payload_len = payload_len_be
        
        offset += 4

        # flags (2 bytes) - 서버 코드에서 memcpy 사용
        offset += 2

        # timestamp (8 bytes) - 서버 코드에서 memcpy 사용
        offset += 8

        # redelivered (1 byte)
        offset += 1

        # payload
        if len(data) < 800 + payload_len:
            raise AthenaException(f"DELIVER message payload incomplete: "
                                 f"expected {800 + payload_len} bytes, got {len(data)}")

        payload = data[offset:offset+payload_len]

        return AthenaMessage(delivery_tag, queue_name, exchange, routing_key,
                            message_id, payload)

    async def ack(self, delivery_tag: int):
        """
        메시지 확인 응답 (ACK)

        Args:
            delivery_tag: 전달 태그
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        try:
            msg = struct.pack('>B', MSG_OP_ACK)          # opcode
            msg += struct.pack('>Q', delivery_tag)       # delivery_tag (8 bytes, Big-Endian)
            msg += struct.pack('>B', MSM_RESP_SUCCESS)   # return_code (1 byte)
            msg += b'\x00' * 128                          # reason (128 bytes)
            msg += b'\x00' * 7                            # padding (7 bytes) -> 144 bytes struct

            async with self._lock:
                await asyncio.to_thread(self.socket.send, msg)
            # ACK는 응답을 기다리지 않음

        except Exception as e:
            raise AthenaException(f"Failed to send ACK: {e}")

    async def nack(self, delivery_tag: int, requeue: bool = True, multiple: bool = False):
        """
        메시지 거부 (NACK)

        Args:
            delivery_tag: 전달 태그
            requeue: 재큐잉 여부
            multiple: 다중 NACK 여부
        """
        if not self.connected:
            raise AthenaException("Not connected to broker")

        try:
            msg = struct.pack('>B', MSG_OP_NACK)         # opcode
            msg += struct.pack('>Q', delivery_tag)       # delivery_tag (8 bytes, Big-Endian)
            msg += struct.pack('>B', 1 if requeue else 0) # requeue (1 byte)
            msg += struct.pack('>B', 1 if multiple else 0) # multiple (1 byte)
            msg += b'\x00' * 6                            # padding (6 bytes)

            async with self._lock:
                await asyncio.to_thread(self.socket.send, msg)
                
                # NACK에 대한 응답(ACK) 대기 (서버 소스: MSG_OP_ACK 반환함)
                # Client: MSG_OP_NACK -> Server: MSG_OP_ACK
                response = await asyncio.to_thread(self.socket.recv)

        except Exception as e:
            raise AthenaException(f"Failed to send NACK: {e}")

    async def close(self):
        """연결 종료"""
        if self.push_socket:
            try:
                await asyncio.to_thread(self.push_socket.close)
            except:
                pass
            self.push_socket = None
            self.push_connected = False
        if self.socket:
            try:
                await asyncio.to_thread(self.socket.close)
            except:
                pass
            self.socket = None
        self.connected = False

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.connected

    async def __aenter__(self):
        """async with 문 지원"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """async with 문 종료 시 자동 정리"""
        await self.close()
