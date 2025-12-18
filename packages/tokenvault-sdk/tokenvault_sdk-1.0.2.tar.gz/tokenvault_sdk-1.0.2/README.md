# TokenVault SDK

[![PyPI version](https://badge.fury.io/py/tokenvault-sdk.svg)](https://badge.fury.io/py/tokenvault-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/tokenvault-sdk.svg)](https://pypi.org/project/tokenvault-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python SDK for AI agents to track LLM usage and manage billing with TokenVault.

## Features

- Credit balance checking with Redis caching
- Usage tracking and forwarding to TokenVault
- Async/await support with automatic retries
- Fail-open mode for resilience
- Groq API integration

## Installation

```bash
pip install tokenvault-sdk
```

## Requirements

- Python 3.11+
- Redis server
- TokenVault API access

## Quick Start

Set environment variables:

```bash
export TOKENVAULT_REDIS_URL="redis://localhost:6379"
export TOKENVAULT_API_URL="https://api.tokenvault.io"
export TOKENVAULT_FREE_TRIAL_MONEY="100.0"  # Optional: free trial amount in dollars
```

## Quick Start (New: One-Line Setup!)

The easiest way to get started:

```python
import asyncio
from tokenvault_sdk import quickstart

async def main():
    # ONE LINE. ZERO PARAMETERS. PERFECT!
    tracker, agent_id = await quickstart(
        organization_id="my-company-2025",
        agent_name="customer-support-pro"
    )

    # Free trial amount configured via TOKENVAULT_FREE_TRIAL_MONEY env var
    # Default: $50. Set to $100: export TOKENVAULT_FREE_TRIAL_MONEY=100.0

    # Now use it (organization auto-created, user auto-created, agent auto-created)
    async with tracker.track_usage(
        organization_id="my-company-2025",
        profile_id=agent_id,
        model="llama-3.3-70b-versatile",
        prompt_tokens=300,
        completion_tokens=600,
    ):
        # Your agent does its thing
        response = await groq_client.chat.completions.create(...)
        print(response.choices[0].message.content)

asyncio.run(main())
```

## Hierarchy and Setup

TokenVault uses a three-level hierarchy for multi-user, multi-agent teams:

```
Organization (workspace/business)
└── Users (real people)
    └── Profiles (agents belonging to a user)
```

## Clean API: Only Two Endpoints

TokenVault has **exactly two endpoints** for the complete billing flow:

### 1. Add Money → `/v1/recharge`
```python
POST /v1/recharge
{
  "organization_id": "org_123",
  "money_amount": 100.0,
  "metadata": { "source": "stripe" }
}
```

### 2. Spend Credits → `/v1/consumption/process`
```python
POST /v1/consumption/process
{
  "organization_id": "org_123",
  "profile_id": "agent_123",
  "model": "llama-3.3-70b-versatile",
  "prompt_tokens": 150,
  "completion_tokens": 400
}
```

**That's it.** No other ways to add or spend funds. One clean flow.

### Add Funds (Free Trial or Real Payment)

```python
# Free trial ($50 grant)
await client.post("https://api.tokenvault.io/v1/recharge", json={
    "organization_id": "acme",
    "money_amount": 50.0,
    "metadata": {"reason": "free_trial"}
})

# Real payment (Stripe/Paddle webhook)
await client.post("https://api.tokenvault.io/v1/recharge", json={
    "organization_id": "acme",
    "money_amount": 100.0,
    "metadata": {"source": "stripe"}
})
```

**Both use the same endpoint. Both convert money → credits. Perfect.**

### Bootstrap Your Organization

Before using the SDK, set up your hierarchy:

```python
import httpx
import os

API_URL = os.getenv("TOKENVAULT_API_URL", "http://localhost:9000")

# Your identifiers
ORG_ID = "org_mycompany_001"
USER_ID = "user_john_doe"
PROFILE_ID = f"agent_grok_{uuid.uuid4().hex[:8]}"

async def bootstrap_hierarchy():
    async with httpx.AsyncClient() as client:
        # 1. Create organization
        await client.post(f"{API_URL}/v1/wallet/organizations", json={
            "id": ORG_ID, "name": "My AI Team"
        })

        # 2. Create user
        await client.post(f"{API_URL}/v1/wallet/users", json={
            "id": USER_ID, "organization_id": ORG_ID, "name": "John Doe"
        })

        # 3. Create agent profile under user
        await client.post(f"{API_URL}/v1/wallet/profiles", json={
            "id": PROFILE_ID, "organization_id": ORG_ID,
            "user_id": USER_ID, "metadata": {"agent_type": "grok"}
        })

        # 4. Add credits
        await client.post(f"{API_URL}/v1/recharge", json={
            "organization_id": ORG_ID, "money_amount": 20.0
        })

# Run at startup
await bootstrap_hierarchy()
```

### Usage with Correct Hierarchy

```python
import asyncio
from tokenvault_sdk import SDKConfig, UsageTracker
from groq import AsyncGroq

async def main():
    config = SDKConfig.from_env()
    tracker = UsageTracker(
        redis_url=config.redis_url,
        tokenvault_api_url=config.tokenvault_api_url,
    )

    groq_client = AsyncGroq(api_key="your-api-key")

    try:
        # Check organization credit balance
        credit_balance = await tracker.check_credit_balance(organization_id=ORG_ID)
        print(f"Credit balance: {credit_balance:.2f} credits")

        # Make LLM call
        response = await groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}]
        )

        # Track usage with organization + profile (agent)
        # user_id is optional for attribution
        asyncio.create_task(
            tracker.track_usage(
                groq_response=response.model_dump(),
                organization_id=ORG_ID,
                profile_id=PROFILE_ID,
                user_id=USER_ID,  # Optional: who ran this agent
            )
        )

        print(response.choices[0].message.content)
    finally:
        await tracker.close()

asyncio.run(main())
```

## Configuration

Environment variables:

| Variable | Required | Default |
|----------|----------|---------|
| `TOKENVAULT_REDIS_URL` | Yes | - |
| `TOKENVAULT_API_URL` | Yes | - |
| `TOKENVAULT_FREE_TRIAL_MONEY` | No | `50.0` |
| `TOKENVAULT_STREAM_NAME` | No | `usage_records` |
| `TOKENVAULT_BALANCE_THRESHOLD` | No | `0.0` |
| `TOKENVAULT_CACHE_TTL` | No | `60` |
| `TOKENVAULT_FAIL_OPEN` | No | `true` |
| `TOKENVAULT_MAX_RETRIES` | No | `3` |
| `TOKENVAULT_RETRY_BACKOFF_MS` | No | `100` |

Or configure programmatically:

```python
from tokenvault_sdk import SDKConfig, UsageTracker

config = SDKConfig(
    redis_url="redis://localhost:6379",
    tokenvault_api_url="https://api.tokenvault.io",
    balance_threshold=0.0,
    cache_ttl=60,
    fail_open=True,
)

tracker = UsageTracker(
    redis_url=config.redis_url,
    wallet_api_url=config.wallet_api_url,
    balance_threshold=config.balance_threshold,
    cache_ttl=config.cache_ttl,
    fail_open=config.fail_open,
)
```

## API Reference

### UsageTracker

**Methods:**

`check_credit_balance(organization_id: str, force_refresh: bool = False) -> float`
- Check organization credit balance with optional cache bypass
- Returns credit balance as float
- Raises `InsufficientBalanceError` if below threshold

`track_usage(groq_response: Dict, organization_id: str, profile_id: str, user_id: str = "", metadata: Optional[Dict] = None)`
- Track LLM usage and publish to Redis Stream
- Designed for fire-and-forget usage with `asyncio.create_task()`

`close()`
- Close all connections gracefully

### Exceptions

- `SDKConfigurationError`: Invalid configuration
- `InsufficientBalanceError`: Balance below threshold
- `TrackingError`: Usage tracking failed (fail-closed mode)

## Error Handling

```python
from tokenvault_sdk import (
    UsageTracker,
    InsufficientBalanceError,
    SDKConfigurationError,
)

try:
    config = SDKConfig.from_env()
except SDKConfigurationError as e:
    print(f"Configuration error: {e}")
    exit(1)

tracker = UsageTracker(
    redis_url=config.redis_url,
    tokenvault_api_url=config.tokenvault_api_url,
)

try:
    credit_balance = await tracker.check_credit_balance("org_123")
except InsufficientBalanceError as e:
    print(f"Insufficient credit balance: {e}")
```

## Modes

**Fail-Open (default):** Allows requests when services are unavailable
```python
tracker = UsageTracker(..., fail_open=True)
```

**Fail-Closed:** Rejects requests when services are unavailable
```python
tracker = UsageTracker(..., fail_open=False)
```

## Angular Frontend Integration

TokenVault provides real-time credit streaming via Server-Sent Events (SSE) endpoints. Integrate live balance updates into your Angular frontend.

### Available Streaming Endpoints

- **Organization Balance**: `GET /v1/balance/organizations/{org_id}/stream`
- **Profile Balance**: `GET /v1/balance/profiles/{profile_id}/stream`

These endpoints stream balance updates in real-time using Redis pub/sub, sending updates whenever credits are added or deducted.

### 1. Create a Credit Service

```typescript
// src/app/services/credit.service.ts
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

export interface BalanceUpdate {
  organization_id: string;
  credits: number;
  money_equivalent: number;
  last_updated: number;
}

@Injectable({
  providedIn: 'root'
})
export class CreditService {
  private balanceSubject = new Subject<BalanceUpdate>();
  private eventSource: EventSource | null = null;

  constructor() {}

  connectToBalanceStream(organizationId: string): Observable<BalanceUpdate> {
    this.disconnect();

    const apiUrl = 'http://localhost:9000'; // Your TokenVault API URL
    const url = `${apiUrl}/v1/balance/organizations/${organizationId}/stream`;

    this.eventSource = new EventSource(url);

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.error) {
          console.error('SSE Error:', data.error);
          return;
        }
        this.balanceSubject.next(data);
      } catch (error) {
        console.error('Failed to parse SSE data:', error);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      // Auto-reconnect after 5 seconds
      setTimeout(() => {
        if (!this.eventSource || this.eventSource.readyState === EventSource.CLOSED) {
          this.connectToBalanceStream(organizationId);
        }
      }, 5000);
    };

    return this.balanceSubject.asObservable();
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
```

### 2. Create a Balance Display Component

```typescript
// src/app/components/balance-display.component.ts
import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { Subscription } from 'rxjs';
import { CreditService, BalanceUpdate } from '../services/credit.service';

@Component({
  selector: 'app-balance-display',
  template: `
    <div class="balance-card">
      <h3>Credit Balance</h3>
      <div class="balance-amount">
        <span class="credits">{{ currentBalance?.credits || 0 }}</span>
        <span class="currency">credits</span>
      </div>
      <div class="money-equivalent">
        ≈ ${{ currentBalance?.money_equivalent || 0 }}
      </div>
      <div class="last-updated" *ngIf="currentBalance">
        Updated: {{ currentBalance.last_updated | date:'short' }}
      </div>
      <div class="connection-status" [class.connected]="isConnected">
        {{ isConnected ? '🟢 Live' : '🔴 Disconnected' }}
      </div>
    </div>
  `,
  styles: [`
    .balance-card {
      padding: 1rem;
      border: 1px solid #ddd;
      border-radius: 8px;
      margin: 1rem 0;
    }
    .balance-amount {
      font-size: 2rem;
      font-weight: bold;
      margin: 0.5rem 0;
    }
    .credits {
      color: #007bff;
    }
    .money-equivalent {
      color: #666;
      font-size: 0.9rem;
    }
    .connection-status {
      font-size: 0.8rem;
      margin-top: 0.5rem;
    }
    .connected {
      color: #28a745;
    }
  `]
})
export class BalanceDisplayComponent implements OnInit, OnDestroy {
  @Input() organizationId!: string;

  currentBalance: BalanceUpdate | null = null;
  isConnected = false;
  private subscription: Subscription = new Subscription();

  constructor(private creditService: CreditService) {}

  ngOnInit(): void {
    this.subscription = this.creditService
      .connectToBalanceStream(this.organizationId)
      .subscribe({
        next: (balance) => {
          this.currentBalance = balance;
          this.isConnected = true;
          console.log('Balance updated:', balance);
        },
        error: (error) => {
          console.error('Balance stream error:', error);
          this.isConnected = false;
        }
      });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
    this.creditService.disconnect();
  }
}
```

### 3. Use in Your Application

```typescript
// src/app/app.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-container">
      <header>
        <h1>TokenVault Dashboard</h1>
        <app-balance-display [organizationId]="currentOrgId"></app-balance-display>
      </header>

      <main>
        <!-- Your agent usage, recharge forms, etc. -->
        <div class="controls">
          <button (click)="rechargeCredits()">Recharge Credits</button>
          <button (click)="runAgent()">Run Agent</button>
        </div>
      </main>
    </div>
  `
})
export class AppComponent {
  currentOrgId = 'org_client_001'; // Get this from your auth/user context

  rechargeCredits(): void {
    // Call TokenVault API to recharge credits
    // The balance will update automatically via SSE
  }

  runAgent(): void {
    // Make agent calls that consume credits
    // The balance will update automatically via SSE
  }
}
```

### 4. Environment Configuration

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  tokenvaultApiUrl: 'http://localhost:9000'
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  tokenvaultApiUrl: 'https://your-api-domain.com'
};
```

### 5. Angular Module Setup

```typescript
// src/app/app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { BalanceDisplayComponent } from './components/balance-display.component';

@NgModule({
  declarations: [
    AppComponent,
    BalanceDisplayComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

### Key Features

- **Real-time Updates**: Balance changes stream immediately when credits are added/deducted
- **Initial Balance**: Stream sends current balance immediately on connection
- **Auto-reconnection**: Automatically reconnects on connection failures
- **Connection Status**: Visual indicator of stream connection status
- **Reactive UI**: Uses RxJS observables for seamless UI updates

### API Integration Examples

#### Check Balance
```typescript
// Get current balance (non-streaming)
getBalance(orgId: string): Observable<BalanceUpdate> {
  return this.http.get<BalanceUpdate>(
    `${this.apiUrl}/v1/wallet/organizations/${orgId}/balance`
  );
}
```

#### Recharge Credits
```typescript
// Add credits (triggers SSE update)
rechargeCredits(orgId: string, amount: number): Observable<any> {
  return this.http.post(`${this.apiUrl}/v1/wallet/recharge`, {
    organization_id: orgId,
    money_amount: amount,
    metadata: { source: 'frontend' }
  });
}
```

#### Process Consumption
```typescript
// Process usage (triggers SSE update)
processConsumption(consumptionData: any): Observable<any> {
  return this.http.post(`${this.apiUrl}/v1/consumption/process`, consumptionData);
}
```

## License

MIT License - see LICENSE file for details
