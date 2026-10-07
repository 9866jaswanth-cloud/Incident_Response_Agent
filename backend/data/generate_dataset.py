"""Generates 35 realistic enterprise synthetic incidents with recurring patterns."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_TIME = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)

incidents = [
    # =========================================================================
    # PRIMARY DEMO INCIDENT #1 (Act 1: First Encounter)
    # =========================================================================
    {
        "id": "INC-001",
        "title": "Payment API Latency Spike and Database Connection Pool Exhaustion",
        "service": "Payment API",
        "severity": "P1-Critical",
        "status": "Investigating",
        "error_message": "org.postgresql.util.PSQLException: Connection to 10.0.4.12:5432 refused. Connection pool 'PaymentHikariPool' exhausted. Active: 10/10, Pending: 142.",
        "symptoms": [
            "Payment API p99 latency spiked from 195ms to 8.4 seconds",
            "HTTP 504 Gateway Timeout on /v1/charges and /v1/checkout endpoints",
            "Database connection acquisition timeouts (timeout exceeded 5000ms)",
            "HikariCP connection pool completely exhausted (10/10 active connections locked)"
        ],
        "logs": (
            "2026-09-20T10:14:22.104Z [ERROR] [payment-api-7b9c6f8f-xk49p] com.zaxxer.hikari.pool.HikariPool - "
            "PaymentHikariPool - Connection is not available, request timed out after 5002ms (active=10, idle=0, waiting=142)\n"
            "2026-09-20T10:14:23.011Z [ERROR] [payment-api-7b9c6f8f-xk49p] c.c.p.controller.ChargeController - "
            "Failed processing payment charge transaction_id=txn_8941029: Database connection pool timeout\n"
            "org.springframework.dao.CannotGetJdbcConnectionException: Failed to obtain JDBC Connection; nested exception is org.postgresql.util.PSQLException\n"
            "\tat org.springframework.jdbc.datasource.DataSourceUtils.getConnection(DataSourceUtils.java:83)\n"
            "\tat c.c.p.repository.TransactionRepository.saveAndFlush(TransactionRepository.java:42)\n"
            "2026-09-20T10:14:24.450Z [WARN] [payment-api-7b9c6f8f-xk49p] org.apache.coyote.http11.Http11Processor - "
            "HTTP request processing thread pool saturated (200/200 active threads)"
        ),
        "metrics": {
            "p99_latency_ms": 8420,
            "p50_latency_ms": 1200,
            "error_rate_pct": 34.8,
            "active_connections": 10,
            "max_pool_size": 10,
            "pending_connection_requests": 142,
            "throughput_rps": 485,
            "db_cpu_pct": 38.2
        },
        "recent_changes": "Commit #c4b8109 deployed 45 minutes ago: 'Refactor payment validation filter and update database connection timeouts'.",
        "stack_trace": (
            "org.springframework.dao.CannotGetJdbcConnectionException: Failed to obtain JDBC Connection\n"
            "  at org.springframework.jdbc.datasource.DataSourceUtils.getConnection(DataSourceUtils.java:83)\n"
            "  at com.corp.payment.repository.TransactionRepository.saveAndFlush(TransactionRepository.java:42)\n"
            "  at com.corp.payment.service.PaymentService.executeCharge(PaymentService.java:114)\n"
            "Caused by: org.postgresql.util.PSQLException: HikariPool-1 - Connection is not available, request timed out after 5000ms."
        ),
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Database connection pool misconfiguration. Under 500 RPS traffic, maximum pool size was constrained to 10 connections, causing starvation when unindexed ledger queries held connections.",
        "confirmed_resolution": "Increased database connection pool max_size from 10 to 50 in Helm values and set connection-timeout to 3000ms. Added composite index on ledger_entries(account_id, created_at).",
        "investigation_steps": [
            "1. Verified PostgreSQL RDS CPU was low (38%), ruling out DB server crash.",
            "2. Inspected HikariCP pool metrics in Grafana; saw all 10 connections continuously occupied.",
            "3. Ran pg_stat_activity and discovered connections blocked waiting on ledger transaction updates.",
            "4. Reviewed Helm deployment diff for commit #c4b8109 and noted pool max-size was accidentally capped at 10."
        ],
        "post_mortem_lesson": "Always validate connection pool capacity against peak concurrency requirements during load spikes.",
        "retained_to_hindsight": False,
        "created_at": (BASE_TIME - timedelta(days=5)).isoformat()
    },

    # =========================================================================
    # PRIMARY DEMO INCIDENT #2 (Act 2: Recurrence of Connection Pool Starvation)
    # =========================================================================
    {
        "id": "INC-002",
        "title": "Payment API Elevated Latency and Hikari Pool Starvation",
        "service": "Payment API",
        "severity": "P1-Critical",
        "status": "Investigating",
        "error_message": "com.zaxxer.hikari.pool.HikariPool$PoolInitializationException: Connection is not available, request timed out after 5004ms. Active connections at limit (10).",
        "symptoms": [
            "Payment API response times degraded rapidly from 210ms to 8.2 seconds",
            "Database connection timeout errors on checkout requests",
            "Connection pool exhaustion under increased flash-sale traffic (520 RPS)",
            "Downstream microservices reporting 504 Gateway Timeouts from Payment API"
        ],
        "logs": (
            "2026-09-25T14:02:11.890Z [ERROR] [payment-api-5c4d3e2f-bb82q] com.zaxxer.hikari.pool.HikariPool - "
            "PaymentHikariPool - Connection is not available, request timed out after 5004ms (active=10, idle=0, waiting=118)\n"
            "2026-09-25T14:02:12.302Z [ERROR] [payment-api-5c4d3e2f-bb82q] c.c.p.service.CheckoutService - "
            "Checkout failed for customer=cust_99214: Connection timeout acquiring database lock on account table\n"
            "2026-09-25T14:02:13.118Z [WARN] [payment-api-5c4d3e2f-bb82q] c.c.p.monitoring.HealthIndicator - "
            "Database health check failing: DB query ping timed out after 3000ms"
        ),
        "metrics": {
            "p99_latency_ms": 8190,
            "p50_latency_ms": 1150,
            "error_rate_pct": 31.4,
            "active_connections": 10,
            "max_pool_size": 10,
            "pending_connection_requests": 118,
            "throughput_rps": 520,
            "db_cpu_pct": 34.1
        },
        "recent_changes": "Release v2.14.0 deployed 20 minutes ago for Flash Sale promotional banner rollout.",
        "stack_trace": (
            "com.zaxxer.hikari.pool.HikariPool$PoolInitializationException: Connection is not available\n"
            "  at com.zaxxer.hikari.pool.HikariPool.throwPoolInitializationException(HikariPool.java:596)\n"
            "  at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:180)\n"
            "  at com.corp.payment.service.CheckoutService.processCheckout(CheckoutService.java:88)"
        ),
        "environment": "production-us-east-1",
        "confirmed_root_cause": None,
        "confirmed_resolution": None,
        "investigation_steps": [],
        "post_mortem_lesson": None,
        "retained_to_hindsight": False,
        "created_at": (BASE_TIME - timedelta(hours=3)).isoformat()
    },

    # =========================================================================
    # PRIMARY DEMO INCIDENT #3 (Act 3: Cross-Service Experience Precedent)
    # =========================================================================
    {
        "id": "INC-003",
        "title": "Order Service Database Connection Timeout and Checkout Block",
        "service": "Order Service",
        "severity": "P2-High",
        "status": "Investigating",
        "error_message": "org.postgresql.util.PSQLException: Connection acquisition timeout after 4500ms. Connection pool 'OrderHikariPool' reached limit (15/15).",
        "symptoms": [
            "Order creation latency increased from 150ms to 4.2 seconds",
            "Database connection timeout errors on order commit",
            "Active database connection pool saturated at 15/15 connections",
            "Order placement queue filling up due to slow writes to shared database cluster"
        ],
        "logs": (
            "2026-09-26T09:12:00.120Z [ERROR] [order-service-89f4b-72pxa] com.zaxxer.hikari.pool.HikariPool - "
            "OrderHikariPool - Connection is not available, request timed out after 4501ms (active=15, idle=0, waiting=86)\n"
            "2026-09-26T09:12:01.405Z [ERROR] [order-service-89f4b-72pxa] c.c.o.service.OrderCreationService - "
            "Failed creating order order_id=ord_78102: Connection timeout from pool\n"
            "2026-09-26T09:12:02.890Z [WARN] [order-service-89f4b-72pxa] c.c.o.repository.OrderRepository - "
            "Transaction commit latency exceeds SLA threshold (>3000ms)"
        ),
        "metrics": {
            "p99_latency_ms": 4210,
            "p50_latency_ms": 820,
            "error_rate_pct": 18.2,
            "active_connections": 15,
            "max_pool_size": 15,
            "pending_connection_requests": 86,
            "throughput_rps": 380,
            "db_cpu_pct": 42.0
        },
        "recent_changes": "Order Service scaled to 6 replicas ahead of regional marketing push.",
        "stack_trace": (
            "org.postgresql.util.PSQLException: HikariPool-Order - Connection not available\n"
            "  at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:180)\n"
            "  at com.corp.order.service.OrderCreationService.createOrder(OrderCreationService.java:94)"
        ),
        "environment": "production-us-east-1",
        "confirmed_root_cause": None,
        "confirmed_resolution": None,
        "investigation_steps": [],
        "post_mortem_lesson": None,
        "retained_to_hindsight": False,
        "created_at": (BASE_TIME - timedelta(hours=1)).isoformat()
    },

    # =========================================================================
    # RECURRING PATTERN 2: Redis Out-of-Memory & Eviction Storms
    # =========================================================================
    {
        "id": "INC-004",
        "title": "Redis Cluster Maxmemory Reached and Auth Session Eviction Storm",
        "service": "Redis/Cache Service",
        "severity": "P1-Critical",
        "status": "Resolved",
        "error_message": "redis.exceptions.ResponseError: OOM command not allowed when used memory > 'maxmemory' (limit: 16GB, used: 15.98GB).",
        "symptoms": [
            "Sudden spike in user session logouts and 401 Unauthorized responses",
            "Redis cluster response latency increased from 1.2ms to 450ms",
            "Keys eviction rate skyrocketed to 8,500 evictions/second",
            "Database auth table flooded with 12x read queries due to cache miss storm"
        ],
        "logs": (
            "2026-09-18T16:20:10.115Z [ERROR] [redis-node-01] oom-killer - "
            "Memory usage reached 99.8% of configured maxmemory 16gb. Current policy: allkeys-lru\n"
            "2026-09-18T16:20:11.450Z [ERROR] [auth-service-67b-12xk] c.c.a.session.SessionStore - "
            "RedisCommandExecutionException: OOM command not allowed when used memory > 'maxmemory'\n"
            "2026-09-18T16:20:12.890Z [WARN] [auth-service-67b-12xk] c.c.a.session.SessionFallback - "
            "Falling back to PostgreSQL database for active session verification"
        ),
        "metrics": {
            "used_memory_bytes": 17158864896,
            "maxmemory_bytes": 17179869184,
            "evicted_keys_per_sec": 8500,
            "cache_hit_rate_pct": 41.2,
            "db_auth_qps": 4800
        },
        "recent_changes": "Feature flag 'enable_extended_user_telemetry_cache' toggled to ON 2 hours prior.",
        "stack_trace": "redis.exceptions.ResponseError: OOM command not allowed when used memory > 'maxmemory'",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Telemetry caching feature stored raw user clickstream payloads in Redis without setting an expiration TTL, filling the 16GB memory ceiling and triggering an allkeys-lru eviction storm that purged valid user auth sessions.",
        "confirmed_resolution": "Disabled 'enable_extended_user_telemetry_cache' feature flag, executed script to prune untagged telemetry keys with zero TTL, and enforced default 3600s TTL on all cached session objects.",
        "investigation_steps": [
            "1. Inspected redis-cli INFO memory and verified used_memory was at 15.98GB.",
            "2. Ran redis-cli --bigkeys and identified millions of 'telemetry:click:*' keys.",
            "3. Checked TTL on sample telemetry keys and found TTL=-1 (persistent indefinite retention)."
        ],
        "post_mortem_lesson": "All cache writes must enforce strict TTL policies. Telemetry data belongs in streaming queues, not in shared session cache.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=9)).isoformat()
    },
    {
        "id": "INC-018",
        "title": "Order Service Redis Cache OOM and Cart Retrieval Failure",
        "service": "Order Service",
        "severity": "P2-High",
        "status": "Resolved",
        "error_message": "redis.clients.jedis.exceptions.JedisDataException: OOM command not allowed when used memory > 'maxmemory'.",
        "symptoms": [
            "Shopping cart retrieval errors on /api/cart",
            "Redis cache memory exhausted under heavy traffic",
            "Database fallback causing elevated PostgreSQL connection count"
        ],
        "logs": (
            "2026-09-22T08:14:00.100Z [ERROR] [order-service-78f-22a] c.c.o.cart.CartCache - "
            "Failed saving temporary cart state to Redis: OOM command not allowed\n"
            "2026-09-22T08:14:01.320Z [WARN] [order-service-78f-22a] c.c.o.cart.CartFallback - "
            "Persisting cart state directly to PostgreSQL fallback store"
        ),
        "metrics": {
            "used_memory_bytes": 17169869000,
            "maxmemory_bytes": 17179869184,
            "cart_error_rate_pct": 22.4,
            "p99_latency_ms": 3100
        },
        "recent_changes": "Promotion campaign for VIP shoppers launched at 08:00 UTC.",
        "stack_trace": "redis.clients.jedis.exceptions.JedisDataException: OOM command not allowed",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Abandoned cart keys were being written without TTL expiry during high-traffic promo launch, filling Redis memory.",
        "confirmed_resolution": "Applied standard TTL policy of 86400s (24h) to cart keys and scaled Redis cluster maxmemory from 16GB to 32GB.",
        "investigation_steps": [
            "1. Verified Redis memory saturation at 99.9%.",
            "2. Identified unexpired cart:* keys accumulating without TTL.",
            "3. Flushed expired cart tokens and adjusted client TTL configuration."
        ],
        "post_mortem_lesson": "Enforce automated TTL checks on all cache write interfaces.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=4)).isoformat()
    },

    # =========================================================================
    # RECURRING PATTERN 3: Kafka Message Queue Backlog & Consumer Starvation
    # =========================================================================
    {
        "id": "INC-005",
        "title": "Payment Notification Kafka Consumer Group Rebalance Storm",
        "service": "Message Queue",
        "severity": "P1-Critical",
        "status": "Resolved",
        "error_message": "org.apache.kafka.clients.consumer.CommitFailedException: Commit cannot be completed since the group has already rebalanced and assigned the partitions to another member.",
        "symptoms": [
            "Notification lag climbed from 150 messages to over 240,000 unconsumed events",
            "Customer transaction SMS and emails delayed by up to 45 minutes",
            "Consumer group repeatedly dropping and rejoining consumer cluster",
            "High CPU churn on Kafka brokers handling continuous partition reassignments"
        ],
        "logs": (
            "2026-09-17T11:05:40.220Z [WARN] [notif-worker-4b8c-55xk] o.a.k.c.c.i.ConsumerCoordinator - "
            "Consumer poll timeout: processing batch took 312,000ms exceeding max.poll.interval.ms (300,000ms)\n"
            "2026-09-17T11:05:41.100Z [ERROR] [notif-worker-4b8c-55xk] o.a.k.c.c.i.ConsumerCoordinator - "
            "CommitFailedException: Offset commit failed with CommitFailedException\n"
            "2026-09-17T11:05:42.500Z [INFO] [notif-worker-4b8c-55xk] o.a.k.c.c.i.AbstractCoordinator - "
            "Initiating rebalance for group 'payment-notification-consumers'"
        ),
        "metrics": {
            "consumer_lag_messages": 241080,
            "max_poll_interval_ms": 300000,
            "actual_batch_processing_time_ms": 312000,
            "rebalance_count_last_hour": 38,
            "notification_delay_sec": 2700
        },
        "recent_changes": "Worker batch size increased from 50 to 500 records in config commit #e1903fa.",
        "stack_trace": "org.apache.kafka.clients.consumer.CommitFailedException: Commit cannot be completed since the group has already rebalanced.",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Increasing max.poll.records to 500 caused downstream email API rendering to exceed the 300-second max.poll.interval.ms threshold, prompting Kafka to assume consumer failure and trigger infinite rebalance storms.",
        "confirmed_resolution": "Reverted max.poll.records to 100, increased max.poll.interval.ms to 600,000ms (10 minutes), and added concurrency to email dispatcher thread pool.",
        "investigation_steps": [
            "1. Observed repeated ConsumerCoordinator rebalance events in logs every 5 minutes.",
            "2. Traced processing time per batch of 500 emails to ~310 seconds.",
            "3. Correlated commit failure with Kafka heartbeat expiration timer."
        ],
        "post_mortem_lesson": "Batch processing timeout (max.poll.interval.ms) must be at least 3x the p99 batch execution time.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=10)).isoformat()
    },
    {
        "id": "INC-021",
        "title": "Notification Service Dead Letter Queue Saturation on Malformed Webhook",
        "service": "Notification Service",
        "severity": "P2-High",
        "status": "Resolved",
        "error_message": "com.fasterxml.jackson.core.JsonParseException: Unexpected character ('<' (code 60)): expected a valid value.",
        "symptoms": [
            "Notification dead letter queue (DLQ) messages surged to 55,000 messages",
            "Worker error logs showing continuous JSON parse exceptions",
            "Downstream partner webhooks dropping deliveries"
        ],
        "logs": (
            "2026-09-21T18:22:04.102Z [ERROR] [notif-worker-99x-11b] c.c.n.consumer.WebhookConsumer - "
            "Unrecoverable JSON deserialization failure on payload from vendor_partner_12\n"
            "2026-09-21T18:22:05.311Z [WARN] [notif-worker-99x-11b] c.c.n.dlq.DeadLetterProducer - "
            "Routing message to payment-events-dlq after 3 retries"
        ),
        "metrics": {
            "dlq_message_count": 55410,
            "failed_delivery_pct": 14.5,
            "consumer_throughput_eps": 120
        },
        "recent_changes": "Partner vendor updated webhook signature format without notice.",
        "stack_trace": "com.fasterxml.jackson.core.JsonParseException: Unexpected character ('<' (code 60))",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Partner vendor sent raw HTML error pages instead of JSON on rate limit, causing JSON deserializer crash.",
        "confirmed_resolution": "Added content-type pre-validation filter before parsing, dropping HTML payloads directly to quarantine bucket without blocking consumer queue.",
        "investigation_steps": [
            "1. Inspected first 10 messages in DLQ; discovered Cloudflare HTML 502 error pages.",
            "2. Identified missing content-type validation header check.",
            "3. Deployed hotfix to gracefully handle non-JSON partner responses."
        ],
        "post_mortem_lesson": "Never parse remote payloads without validating expected content-type header.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=6)).isoformat()
    },

    # =========================================================================
    # RECURRING PATTERN 4: Authentication Service Key Rotation & Config Errors
    # =========================================================================
    {
        "id": "INC-006",
        "title": "Authentication Service JWT Verification Failure Following Key Rotation",
        "service": "Authentication Service",
        "severity": "P1-Critical",
        "status": "Resolved",
        "error_message": "com.auth0.jwt.exceptions.SignatureVerificationException: The Token's Signature resulted invalid when verified using the Algorithm: HmacSHA256.",
        "symptoms": [
            "All customer API requests failing with HTTP 401 Unauthorized across all microservices",
            "API Gateway rejected 100% of validated authorization headers",
            "Authentication service logs flooded with signature verification mismatch errors"
        ],
        "logs": (
            "2026-09-19T02:00:15.890Z [ERROR] [auth-service-44f-99xa] c.c.a.jwt.JwtValidator - "
            "SignatureVerificationException: Public key key_id='auth-key-2026-09' failed verification for incoming bearer token\n"
            "2026-09-19T02:00:16.412Z [ERROR] [gateway-proxy-88b-11k] c.c.g.filter.AuthFilter - "
            "Token validation rejected by auth service: 401 Unauthorized"
        ),
        "metrics": {
            "http_401_error_rate_pct": 98.4,
            "total_rejected_requests": 84000,
            "auth_validation_latency_ms": 14
        },
        "recent_changes": "Scheduled monthly automated cryptographic key rotation executed at 02:00 UTC.",
        "stack_trace": "com.auth0.jwt.exceptions.SignatureVerificationException: Signature invalid",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Key rotation script replaced the active signing secret in AWS Secrets Manager without keeping the previous public key in the JWKS verification set, invalidating all existing in-flight tokens before client refresh.",
        "confirmed_resolution": "Restored previous public key to the JWKS key set to allow 24-hour dual-key coexistence window, and cleared the API gateway cached verification keys.",
        "investigation_steps": [
            "1. Correlated start time of 401 errors exactly with 02:00 UTC cron rotation job.",
            "2. Checked JWKS endpoint output; saw only the new key ID was advertised.",
            "3. Confirmed client tokens had key_id of previous rotation."
        ],
        "post_mortem_lesson": "Key rotation pipelines must maintain N-1 key verification capability for at least the maximum token TTL.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=8)).isoformat()
    },
    {
        "id": "INC-024",
        "title": "Payment API Mutual TLS Handshake Failure After Certificate Renewal",
        "service": "Payment API",
        "severity": "P1-Critical",
        "status": "Resolved",
        "error_message": "javax.net.ssl.SSLHandshakeException: Received fatal alert: certificate_unknown.",
        "symptoms": [
            "Payment processor bank gateway reporting SSL handshake failures",
            "100% credit card settlement batch jobs failing with TLS errors"
        ],
        "logs": (
            "2026-09-23T04:12:00.120Z [ERROR] [payment-api-44x-11k] c.c.p.gateway.BankClient - "
            "SSLHandshakeException: PKIX path building failed: unable to find valid certification path to requested target\n"
            "2026-09-23T04:12:01.300Z [ERROR] [payment-api-44x-11k] c.c.p.settlement.SettlementWorker - "
            "Batch settlement transaction failed: bank connection closed abruptly"
        ),
        "metrics": {
            "tls_handshake_error_rate_pct": 100.0,
            "failed_settlement_volume_usd": 420000
        },
        "recent_changes": "mTLS client certificate updated in Kubernetes secret 'payment-tls-cert'.",
        "stack_trace": "javax.net.ssl.SSLHandshakeException: Received fatal alert: certificate_unknown",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Intermediate certificate authority (CA) bundle was omitted from the Kubernetes secret during certificate renewal, causing bank server to reject verification chain.",
        "confirmed_resolution": "Appended intermediate CA certificates to tls.crt in secret and performed rolling restart of payment pods.",
        "investigation_steps": [
            "1. Verified certificate expiry date was valid.",
            "2. Ran openssl s_client -connect bank.gateway:443 to inspect cert chain.",
            "3. Discovered missing intermediate certificate in client handshake."
        ],
        "post_mortem_lesson": "Always bundle full certificate chain (leaf + intermediate) in TLS secrets.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=3)).isoformat()
    },

    # =========================================================================
    # RECURRING PATTERN 5: API Gateway Timeout & Cascading Failures
    # =========================================================================
    {
        "id": "INC-007",
        "title": "API Gateway Cascading 504 Timeout on Upstream Search Degradation",
        "service": "API Gateway",
        "severity": "P1-Critical",
        "status": "Resolved",
        "error_message": "Envoy upstream request timeout (duration: 15000ms reached on cluster 'catalog_search_service').",
        "symptoms": [
            "API Gateway CPU utilization spiked to 92% across all 12 edge nodes",
            "Gateway thread pool saturation causing innocent health checks to fail",
            "All frontend traffic returning HTTP 504 Gateway Timeout"
        ],
        "logs": (
            "2026-09-16T14:40:12.890Z [WARN] [envoy-proxy-edge-01] upstream - "
            "upstream response timeout on request to cluster catalog_search_service\n"
            "2026-09-16T14:40:13.200Z [ERROR] [envoy-proxy-edge-01] router - "
            "circuit breaker open for cluster catalog_search_service: max pending requests (1024) exceeded\n"
            "2026-09-16T14:40:14.500Z [CRITICAL] [envoy-proxy-edge-01] main - "
            "Gateway memory footprint near 90% due to accumulated pending connection buffers"
        ),
        "metrics": {
            "gateway_cpu_pct": 92.4,
            "p99_latency_ms": 15000,
            "http_504_rate_pct": 48.2,
            "active_pending_requests": 1024,
            "healthy_upstream_endpoints": 8
        },
        "recent_changes": "Gateway route timeout for /api/search was increased from 2000ms to 15000ms in config PR #819.",
        "stack_trace": "Envoy: upstream request timeout after 15000ms",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Increasing the search route timeout to 15s allowed slow catalog queries to hold gateway worker threads open indefinitely during traffic surge, exhausting gateway connection buffers and triggering cascading 504s.",
        "confirmed_resolution": "Restored search route timeout to 2500ms, enabled aggressive circuit breaker tripping at 200 pending connections, and configured fallback degraded response for catalog queries.",
        "investigation_steps": [
            "1. Verified Catalog Search Service was running slow Elastic queries.",
            "2. Identified API Gateway thread starvation due to long 15s timeout window.",
            "3. Reverted timeout change in Gateway virtual host route configuration."
        ],
        "post_mortem_lesson": "Never set gateway timeouts higher than 3000ms for user-facing interactive endpoints without circuit breakers.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=11)).isoformat()
    },
    {
        "id": "INC-028",
        "title": "Order Service Gateway Timeout on Unindexed Order Search",
        "service": "Order Service",
        "severity": "P2-High",
        "status": "Resolved",
        "error_message": "HTTP 504 Gateway Timeout: Upstream order-service failed to respond within 5000ms.",
        "symptoms": [
            "Customers unable to view past orders on user account dashboard",
            "Gateway reporting 504 timeouts on /api/orders/history"
        ],
        "logs": (
            "2026-09-24T19:05:00.110Z [WARN] [gateway-proxy-77a] router - "
            "Timeout waiting for upstream order-service on GET /api/orders/history?customer_id=12890\n"
            "2026-09-24T19:05:02.400Z [ERROR] [order-service-88b] c.c.o.repository - "
            "Slow query execution (4920ms): SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC"
        ),
        "metrics": {
            "p99_latency_ms": 5200,
            "http_504_count": 1840,
            "db_sequential_scan_rate": 84
        },
        "recent_changes": "Database migration script 044_add_order_metadata.sql ran earlier in the day.",
        "stack_trace": "HTTP 504 Gateway Timeout",
        "environment": "production-us-east-1",
        "confirmed_root_cause": "Migration script dropped composite index idx_orders_customer_created, turning index scan into full sequential table scan across 12M rows.",
        "confirmed_resolution": "Recreated index CONCURRENTLY idx_orders_customer_created ON orders (customer_id, created_at DESC).",
        "investigation_steps": [
            "1. Ran EXPLAIN ANALYZE on slow query and observed Seq Scan on orders.",
            "2. Checked pg_indexes and discovered index was missing.",
            "3. Created index concurrently without locking production writes."
        ],
        "post_mortem_lesson": "Database migration reviews must explicitly check for accidental index drops.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=2)).isoformat()
    }
]

# Generate additional realistic incidents to reach 35 incidents across all 8 enterprise services
SERVICES = [
    "Payment API", "Authentication Service", "Order Service", "Notification Service",
    "Database Service", "Redis/Cache Service", "Message Queue", "API Gateway"
]

ADDITIONAL_SCENARIOS = [
    # Database Service
    ("INC-008", "Database Service", "P1-Critical", "PostgreSQL Primary Node Replication Lag Spike",
     "FATAL: terminating connection due to conflict with recovery.",
     ["Replication delay reached 420 seconds on read replicas", "Read-after-write inconsistencies for user profile data", "Replication slot WAL file accumulation filling disk to 88%"],
     "WAL disk accumulation due to idle replication slot from retired staging cluster.",
     "Dropped orphaned replication slot and increased max_wal_size to 32GB."),

    ("INC-009", "Database Service", "P2-High", "Database Deadlock on Inventory Allocation Rows",
     "org.postgresql.util.PSQLException: ERROR: deadlock detected. Process 19482 waits for ShareLock on transaction.",
     ["Order checkout failures with 500 Internal Server Error", "Database active locks spiking to 4,200", "Concurrent batch inventory reservation colliding with cart updates"],
     "Inventory reservation and cart checkout acquired row locks in opposite alphabetical order of SKU IDs.",
     "Standardized lock acquisition order by sorting SKU IDs before acquiring row locks in transaction."),

    # Notification Service
    ("INC-010", "Notification Service", "P2-High", "SES API Rate Limit Throttling on Bulk Announcement",
     "com.amazonaws.services.simpleemail.model.AmazonSimpleEmailServiceException: Maximum sending rate exceeded (limit: 200/sec).",
     ["Password reset and 2FA emails delayed by up to 25 minutes", "SES client reporting 429 throttling errors", "Outbound notification queue depth reached 80,000"],
     "Marketing newsletter broadcast consumed 100% of shared SES account sending quota.",
     "Separated transactional emails and marketing broadcasts into distinct AWS SES accounts and configured token bucket rate limiter."),

    # API Gateway
    ("INC-011", "API Gateway", "P1-Critical", "DNS Resolution Failure on Core Microservice Routing",
     "Envoy: upstream cluster 'auth-service' DNS lookup failed: NXDOMAIN.",
     ["Core K8s CoreDNS pods CPU at 100%", "API Gateway unable to resolve internal cluster IPs", "Service mesh routing failing for 60% of ingress requests"],
     "CoreDNS configuration had ndots:5 causing 5 iterative query loops for every internal cluster request during traffic spike.",
     "Updated dnsConfig ndots:2 in pod specs and deployed CoreDNS horizontal pod autoscaler."),

    # Redis/Cache
    ("INC-012", "Redis/Cache Service", "P2-High", "Cache Stampede on Product Homepage Metadata",
     "RedisTimeoutException: Redis response timeout after 2000ms under 14,000 QPS.",
     ["Homepage load time degraded from 180ms to 3.8s", "Single key 'catalog:homepage:featured' requested by 12,000 concurrent clients", "Backend database overloaded by 80x read spike"],
     "Key expired simultaneously across all web pods without probabilistic early expiration (XFetch / stale-while-revalidate).",
     "Implemented mutual exclusion lock (single-flight) on cache misses and added 15% random TTL jitter."),

    # Payment API
    ("INC-013", "Payment API", "P2-High", "Stripe Webhook Idempotency Key Duplicate Rejection",
     "com.corp.payment.exception.IdempotencyConflictException: Key already locked by in-flight charge.",
     ["Chargeback notifications failing with HTTP 409 Conflict", "Double charge protection falsely triggering on network retries"],
     "Client retry header generation used system millisecond timestamp instead of unique transaction UUID.",
     "Updated client SDK to generate deterministic UUIDv5 idempotency keys based on transaction ID and retry attempt."),

    # Order Service
    ("INC-014", "Order Service", "P1-Critical", "Order Fulfillment Queue Worker Out of Memory Crash",
     "java.lang.OutOfMemoryError: Java heap space (allocated: 4096MB).",
     ["Order fulfillment container pods in CrashLoopBackOff", "Fulfillment throughput dropped to 0 orders/sec", "Heap dumps showing millions of uncompressed PDF invoice byte arrays"],
     "Invoice generation retained raw PDF byte arrays in memory during bulk order export without streaming to S3.",
     "Streamed invoice documents directly to S3 via ChunkedOutputStream and increased worker heap limit to 6GB."),

    # Notification Service
    ("INC-015", "Notification Service", "P2-High", "Notification Service DB Pool Starvation After SMS Blast",
     "org.postgresql.util.PSQLException: Connection pool 'NotifHikariPool' exhausted (active: 10/10).",
     ["Notification status updates failing with DB timeout", "Connection pool exhausted during flash sale notification burst"],
     "HikariCP pool limit was left at default (10) while worker threads were scaled to 40.",
     "Scaled HikariCP pool max_size to 40 to match worker thread capacity."),

    # Message Queue
    ("INC-016", "Message Queue", "P1-Critical", "RabbitMQ Disk Alarm Triggered and Cluster Blocked",
     "RabbitMQ: disk free space alarm triggered (free space: 480MB, limit: 1024MB). All producers blocked.",
     ["All publisher applications received 503 Channel Blocked", "Event ingestion halted across payment, order, and telemetry microservices"],
     "Unacknowledged messages on non-expiring audit queue accumulated 45GB of disk logs.",
     "Purged stale unacknowledged messages, increased disk volume size to 200GB, and configured maximum message TTL of 7 days."),

    # Authentication Service
    ("INC-017", "Authentication Service", "P2-High", "LDAP Corporate Directory Sync Timeout",
     "javax.naming.CommunicationException: ldap.corp.internal:636 connection timed out.",
     ["Internal admin portal login disabled for all on-call engineers", "SSO token exchange failing with 504 Gateway Timeout"],
     "Firewall rule change on corporate VPN dropped egress traffic to LDAP port 636.",
     "Restored egress rule in Palo Alto firewall configuration and added health check alert for LDAP endpoint."),

    # Additional diverse incidents to round out 35
    ("INC-019", "Payment API", "P2-High", "Currency Conversion API Rate Limit Reached",
     "CurrencyConversionException: 429 Too Many Requests from Fixer.io.",
     ["International payment transactions failing at checkout", "Exchange rate conversion returning stale or zero rates"],
     "Microservice queried remote exchange rate API on every charge instead of caching rates locally.",
     "Cached exchange rates in Redis with 1-hour TTL and fallback to daily European Central Bank rates."),

    ("INC-020", "Authentication Service", "P3-Medium", "Password Hashing Bcrypt Work Factor CPU Bottleneck",
     "Bcrypt execution duration 1,840ms per verification. Auth pod CPU at 100%.",
     ["User login latency elevated to 2.2 seconds", "Container CPU throttling reported in Kubernetes"],
     "Bcrypt cost factor was inadvertently raised from 12 to 16 in user authentication configuration.",
     "Reverted bcrypt cost factor to 12 and enabled asynchronous work pool for password verification."),

    ("INC-022", "API Gateway", "P1-Critical", "TLS Certificate Expiry on Public Ingress Domain",
     "SSL_ERROR_EXPIRED_CERT_ALERT: api.enterprise.corp certificate expired 10 minutes ago.",
     ["100% of mobile and web clients blocked by browser SSL warnings", "Inbound traffic dropped to zero"],
     "Cert-manager Let's Encrypt renewal failed due to DNS-01 webhook timeout in Route53.",
     "Manually renewed certificate via Cloudflare origin SSL and corrected cert-manager IAM permissions."),

    ("INC-023", "Database Service", "P2-High", "Disk Space Exhaustion on Database Archive Volume",
     "PANIC: could not write to file 'pg_wal/0000000100000012': No space left on device.",
     ["PostgreSQL master shut down to prevent data corruption", "Read-write database availability lost for 18 minutes"],
     "pg_dump logical backup cron job failed to clean up previous uncompressed .sql dump files.",
     "Expanded EBS volume size from 500GB to 1TB and added S3 direct streaming to backup script."),

    ("INC-025", "Order Service", "P3-Medium", "Order State Machine Invalid Transition Exception",
     "IllegalStateTransitionException: Cannot transition order ord_88190 from CANCELLED to SHIPPED.",
     ["Warehouse fulfillment worker logging 500 errors", "Orphaned warehouse packages with mismatched order statuses"],
     "Concurrent race condition between customer self-service cancellation and warehouse barcode scanning.",
     "Added optimistic locking with version column to Order aggregate root entity."),

    ("INC-026", "Redis/Cache Service", "P2-High", "Redis Client Connection Leak in Billing Worker",
     "redis.clients.jedis.exceptions.JedisConnectionException: Could not get a resource from the pool.",
     ["Billing generation batch job halted halfway through monthly run", "Redis server active client connections reached 10,000 maximum"],
     "Billing worker failed to close Jedis connection inside finally block when transaction calculation raised an exception.",
     "Wrapped Jedis connection handling in try-with-resources statement across all billing repository methods."),

    ("INC-027", "Notification Service", "P3-Medium", "Apple Push Notification APNs Auth Key Expired",
     "ApnsDeliveryException: 403 Forbidden: ExpiredProviderToken.",
     ["iOS push notifications failing for mobile app users", "APNs feedback service reporting invalid provider token"],
     "Apple Developer APNs p8 authentication token exceeded 1-hour session renewal interval.",
     "Implemented automatic token renewal every 50 minutes in APNs client connection factory."),

    ("INC-029", "Message Queue", "P2-High", "Kafka Partition Hotspotting on Low-Cardinality Key",
     "Partition 4 consumer lag: 180,000 msgs. Partitions 0-3 lag: 12 msgs.",
     ["Order processing skewed with 20% of orders delayed by 15 minutes", "Single consumer worker CPU pinned at 100%"],
     "Kafka message producer partitioned orders by country code ('US') causing 90% of traffic to hit partition 4.",
     "Changed partition key to composite hash of country_code + customer_id for even distribution."),

    ("INC-030", "Authentication Service", "P2-High", "Multi-Factor Authentication SMS Provider Outage",
     "TwilioRestException: 503 Service Unavailable: SMS carrier route degraded.",
     ["Users unable to receive SMS MFA verification codes during login", "Login failure rate reached 42% for 2FA users"],
     "Primary SMS gateway experienced major North American carrier routing outage.",
     "Enabled automated secondary SMS carrier fallback (AWS SNS) and allowed TOTP authenticator app verification."),

    ("INC-031", "Database Service", "P1-Critical", "Connection Pool Starvation on Analytics Query Leak",
     "FATAL: remaining connection slots are reserved for non-replication superuser connections (max_connections: 500).",
     ["All application microservices unable to establish new database connections", "Core PostgreSQL instance connection table filled with pg_read_all_stats queries"],
     "BI data science tool ran unthrottled ad-hoc analytical queries directly against primary OLTP database instead of read replica.",
     "Killed all active BI connections, revoked read permissions on OLTP master for BI user role, and routed analytical reporting to read replica."),

    ("INC-032", "API Gateway", "P2-High", "Rate Limiter Redis Backend Network Partition",
     "RateLimitFilterException: Failed connecting to rate-limit Redis cluster at 10.0.12.8:6379.",
     ["API Gateway default-failing requests with 500 Internal Server Error", "False-positive 429 throttling on authenticated API partners"],
     "VPC security group modification revoked ingress on port 6379 between Gateway subnet and Redis subnet.",
     "Reverted VPC security group rule and configured rate limiter to fail-open during transient Redis outages."),

    ("INC-033", "Order Service", "P2-High", "Order Total Decimal Precision Rounding Discrepancy",
     "CurrencyPrecisionMismatchException: Total amount 104.994 does not match expected currency scale (2).",
     ["Shopping cart checkout rejected by payment gateway with invalid amount error", "Failed transactions accumulating in order intake log"],
     "Tax calculation library used float64 instead of fixed-point BigDecimal, causing floating-point rounding errors.",
     "Refactored tax engine to use Java BigDecimal with RoundingMode.HALF_EVEN."),

    ("INC-034", "Payment API", "P1-Critical", "Fraud Detection Service gRPC Circuit Breaker Open",
     "StatusRuntimeException: UNAVAILABLE: io.grpc.StatusRuntimeException: Channel shutdown.",
     ["Credit card authorization flow blocked on fraud evaluation step", "Checkout completion rate plummeted to 12%"],
     "Fraud service machine learning inference pod crashed due to GPU driver CUDA memory allocation fault.",
     "Configured payment gateway to bypass fraud check for trusted recurring customers with risk score < 10 when fraud service circuit breaker trips."),

    ("INC-035", "Notification Service", "P3-Medium", "Email Template Syntax Error on Localization Render",
     "FreemarkerException: FreeMarker template error: Template not found for locale 'es_MX'.",
     ["Mexican customers receiving blank confirmation emails", "Template worker error rate spiked to 100% on es_MX requests"],
     "New order confirmation template was only translated for 'es_ES' and lacked fallback to base Spanish locale.",
     "Added locale fallback chain in template engine: es_MX -> es -> en_US.")
]

for idx, (inc_id, service, sev, title, err, symptoms, root_cause, resolution) in enumerate(ADDITIONAL_SCENARIOS, start=8):
    incidents.append({
        "id": inc_id,
        "title": title,
        "service": service,
        "severity": sev,
        "status": "Resolved",
        "error_message": err,
        "symptoms": symptoms,
        "logs": f"2026-09-1{idx%9}T10:00:00.000Z [ERROR] [{service.lower().replace(' ', '-')}-node] - {err}",
        "metrics": {"error_rate_pct": 18.5, "p99_latency_ms": 1450, "affected_users": 1200},
        "recent_changes": f"Routine deployment or dependency update for {service}.",
        "stack_trace": err,
        "environment": "production-us-east-1",
        "confirmed_root_cause": root_cause,
        "confirmed_resolution": resolution,
        "investigation_steps": [f"1. Investigated telemetry for {service}.", f"2. Isolated issue: {root_cause[:60]}..."],
        "post_mortem_lesson": f"Documented best practice for {service} reliability.",
        "retained_to_hindsight": True,
        "created_at": (BASE_TIME - timedelta(days=idx)).isoformat()
    })

dataset = {
    "_metadata": {
        "dataset_type": "SYNTHETIC_ENTERPRISE_DEMO_DATASET",
        "version": "1.0",
        "total_incidents": len(incidents),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": "Realistic enterprise incident dataset featuring recurring patterns across 8 microservices for Hindsight persistent memory demonstration."
    },
    "incidents": incidents
}

output_path = Path("C:/Users/ADMIN/.gemini/antigravity/scratch/incident-response-agent/backend/data/synthetic_incidents.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print(f"Successfully generated {len(incidents)} incidents in {output_path}")
