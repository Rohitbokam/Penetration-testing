# Real-Time Penetration Testing Platform - System Architecture

## 1. High-Level System Architecture Blueprint

The platform follows a microservices-based, event-driven architecture designed for scalability, security, and real-time responsiveness.

```mermaid
graph TD
    User[User/Browser] -->|HTTPS/WSS| LB[Load Balancer]
    LB -->|API Req| Gateway[API Gateway / Backend]
    LB -->|WebSocket| WS[Real-time Service]

    subgraph "Core Services"
        Gateway --> Auth[Auth Service]
        Gateway --> ScanMgr[Scan Manager]
        Gateway --> ReportMgr[Report Engine]
        WS --> RedisPubSub[Redis Pub/Sub]
    end

    subgraph "Data Layer"
        ScanMgr --> PG[(PostgreSQL - Users/Meta)]
        ScanMgr --> Mongo[(MongoDB - Logs/Results)]
        WS --> Redis[(Redis - Cache/Realtime)]
    end

    subgraph "Execution Plane (Isolated)"
        ScanMgr -->|Task Queue| RabbitMQ[RabbitMQ/Redis]
        RabbitMQ --> Workers[Scan Workers (Celery)]
        Workers -->|Execute| Tools[Nmap, ZAP, Nuclei, etc.]
        Workers -->|Stream Logs| RedisPubSub
        Workers -->|Save Results| Mongo
    end

    subgraph "AI Layer"
        Workers -->|Raw Data| AIEngine[AI Correlation Engine]
        AIEngine -->|Insights| Mongo
    end
```

## 2. Database Schema Design

### PostgreSQL (Relational Data)
Used for structured data, user management, and billing.

*   **Users Table**
    *   `id` (UUID, PK)
    *   `email` (VARCHAR, Unique)
    *   `password_hash` (VARCHAR)
    *   `role` (ENUM: admin, tester, viewer)
    *   `mfa_secret` (VARCHAR)
    *   `organization_id` (FK)

*   **Organizations Table**
    *   `id` (UUID, PK)
    *   `name` (VARCHAR)
    *   `subscription_tier` (ENUM)

*   **Targets Table**
    *   `id` (UUID, PK)
    *   `organization_id` (FK)
    *   `target_value` (VARCHAR - IP/Domain)
    *   `verification_status` (BOOLEAN)
    *   `proof_of_ownership` (VARCHAR - file path)

*   **Scans Table**
    *   `id` (UUID, PK)
    *   `target_id` (FK)
    *   `initiated_by` (FK)
    *   `status` (ENUM: queued, running, paused, completed, failed)
    *   `start_time` (TIMESTAMP)
    *   `end_time` (TIMESTAMP)
    *   `config` (JSONB)

*   **Reports Table**
    *   `id` (UUID, PK)
    *   `scan_id` (FK)
    *   `generated_at` (TIMESTAMP)
    *   `file_path` (VARCHAR - S3 Key)
    *   `access_token` (VARCHAR)

### MongoDB (Unstructured/Log Data)
Used for high-volume scan outputs and tool results.

*   **ScanLogs Collection**
    *   `scan_id` (Index)
    *   `timestamp`
    *   `tool` (e.g., nmap, zap)
    *   `level` (INFO, WARN, ERROR)
    *   `message`

*   **Vulnerabilities Collection**
    *   `scan_id` (Index)
    *   `tool_source`
    *   `name`
    *   `severity` (Critical, High, Medium, Low)
    *   `cvss_score`
    *   `description`
    *   `evidence` (Raw output snippet)
    *   `remediation`

### Redis (Real-time & Caching)
*   **Pub/Sub Channels**: `scan:updates:{scan_id}`
*   **Cache**: `user:session:{token}`, `scan:status:{scan_id}`

## 3. API Endpoints List

### Authentication & Users
*   `POST /api/v1/auth/login`: Get JWT token.
*   `POST /api/v1/auth/register`: Create account.
*   `POST /api/v1/auth/mfa/verify`: Verify 2FA.

### Target Management
*   `POST /api/v1/targets`: Add new target.
*   `POST /api/v1/targets/{id}/verify`: Upload authorization proof.
*   `GET /api/v1/targets`: List authorized targets.

### Scan Management
*   `POST /api/v1/scans`: Start a new scan (Requires target ID + config).
*   `GET /api/v1/scans/{id}`: Get scan status.
*   `POST /api/v1/scans/{id}/action`: Body `{"action": "pause" | "resume" | "stop"}`.
*   `GET /api/v1/scans/{id}/results`: Get JSON results.

### Reporting
*   `POST /api/v1/reports/generate`: Trigger PDF generation for a scan.
*   `GET /api/v1/reports/{id}/download`: Get signed URL for PDF.

### WebSocket (Real-time)
*   `WS /ws/v1/scans/{scan_id}`: Stream logs and progress updates.

## 4. PDF Pipeline Architecture

1.  **Trigger**: User requests report via API.
2.  **Queue**: Request pushed to `reports_queue` (RabbitMQ).
3.  **Generation Worker**:
    *   Fetches structured findings from PostgreSQL & MongoDB.
    *   Fetches branding assets (Logos) from Object Storage.
    *   Uses **ReportLab** (Python) or **Puppeteer** (Node) to render PDF.
    *   Sections included: Cover, Exec Summary, Findings, Compliance, Appendix.
4.  **Storage**: PDF uploaded to secure Object Storage (S3/MinIO) with Server-Side Encryption (SSE-S3).
5.  **Notification**: User notified via WebSocket/Email that report is ready.

## 5. Security Controls

*   **Authentication**: OAuth2 with JWT, mandatory MFA.
*   **Authorization**: RBAC (Role-Based Access Control) via middleware.
*   **Input Validation**: Strict schema validation (Pydantic/Joi) to prevent injection.
*   **Sandboxing**: All scanning tools run in ephemeral, network-restricted Docker containers.
*   **Rate Limiting**: Per-user and per-target throttling (Redis-based token bucket).
*   **Audit Logging**: All actions (scan start, report download) logged to immutable audit table.
*   **Encryption**: TLS 1.3 for transit, AES-256 for database columns (secrets) and S3 objects.

## 6. Infrastructure & Deployment (K8s)

*   **Ingress**: Nginx Ingress Controller with Let's Encrypt.
*   **Services**:
    *   `frontend`: React App (Nginx container).
    *   `backend`: FastAPI (gunicorn/uvicorn).
    *   `worker-scan`: Celery workers (Scaled based on CPU/Queue depth).
    *   `worker-report`: PDF generation workers.
*   **State**:
    *   PostgreSQL (StatefulSet or Managed RDS).
    *   MongoDB (StatefulSet or Managed Atlas).
    *   Redis (Cluster).
    *   RabbitMQ.

## 7. AI Intelligence Layer

*   **Deduplication**: AI model compares findings from different tools (e.g., Nikto vs ZAP) to merge duplicates.
*   **False Positive Reduction**: Confidence scoring based on historical data.
*   **Remediation Suggester**: Maps findings to specific code-fix suggestions using LLM integration (Optional/Local).
