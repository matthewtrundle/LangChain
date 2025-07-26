# Refactoring Plan for Production Readiness

## Overview
This document outlines the refactoring needed to move from MVP to production-ready code.

## Critical Issues (Fix Before Deploy)

### 1. Remove Hardcoded Backend URL
**File**: `/frontend/lib/api.ts`
**Issue**: Line 11 hardcodes Railway URL
**Fix**: 
```typescript
// Remove: return 'https://langchain-production-881c.up.railway.app'
// Use environment variable only
```

### 2. Fix CORS Configuration
**File**: `/backend/main.py`
**Issue**: Line 29 allows all origins with "*"
**Fix**:
```python
allow_origins = [
    "https://your-frontend-domain.com",
    "http://localhost:3000"  # Dev only
]
```

### 3. Remove Console Logs
**Files**: Multiple
**Fix**: Global search and remove all console.log and print statements

### 4. Add API Key Validation
**File**: `/backend/config.py`
**Fix**: Add startup validation
```python
def validate_config():
    if not Config.HELIUS_API_KEY:
        raise ValueError("HELIUS_API_KEY is required")
    if not Config.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is required")
```

## High Priority Refactoring

### 1. Replace Mock Data with Real Data

#### Analyze Endpoint
**File**: `/backend/main.py` (lines 140-154)
**Current**: Returns mock pool data
**Fix**: Query real blockchain data using Helius

#### Pool Scanner
**File**: `/backend/tools/pool_scanner.py`
**Current**: Returns mock pools
**Fix**: Use real Helius RPC calls

### 2. Implement Proper Error Handling

#### Backend
- Replace bare `except:` with specific exceptions
- Add user-friendly error messages
- Implement error logging

#### Frontend
- Add error boundaries
- Show user-friendly error messages
- Implement retry logic

### 3. Configuration Management

#### Move Hardcoded Values
Create environment variables for:
- APY thresholds (100%, 1000%)
- Pool age limits (24h, 72h)
- Max pools per scan (10)
- Position limits ($1000, $5000)
- API URLs and endpoints

### 4. Type Safety
- Remove all `as any` type assertions
- Create proper TypeScript interfaces
- Add runtime type validation

## Medium Priority

### 1. Performance Optimization
- Implement connection pooling
- Add response caching
- Use pagination for large datasets
- Implement request debouncing

### 2. Logging System
- Replace print/console.log with proper logging
- Add log levels (DEBUG, INFO, WARNING, ERROR)
- Implement log rotation
- Add request/response logging

### 3. Testing
- Add unit tests for critical functions
- Add integration tests for API endpoints
- Add frontend component tests
- Set up CI/CD pipeline

### 4. Security Enhancements
- Add rate limiting
- Implement API authentication
- Add input sanitization
- Implement CSRF protection

## Implementation Timeline

### Week 1: Critical Issues
- [ ] Remove hardcoded URLs
- [ ] Fix CORS configuration
- [ ] Remove debug logs
- [ ] Add config validation

### Week 2: Core Functionality
- [ ] Replace mock data with real APIs
- [ ] Implement error handling
- [ ] Add configuration management
- [ ] Fix type safety issues

### Week 3: Performance & Security
- [ ] Add caching layer
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Performance optimization

### Week 4: Testing & Documentation
- [ ] Write unit tests
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Set up monitoring

## Code Examples

### Configuration Class
```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    # API Keys
    helius_api_key: str
    openrouter_api_key: str
    
    # API URLs
    defi_llama_url: str = "https://api.llama.fi"
    jupiter_api_url: str = "https://price.jup.ag/v4"
    
    # Thresholds
    min_apy_threshold: float = 100.0
    high_apy_threshold: float = 1000.0
    max_pool_age_hours: int = 72
    
    # Limits
    max_pools_per_scan: int = 10
    max_position_size: float = 1000.0
    max_total_exposure: float = 5000.0
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            helius_api_key=os.environ["HELIUS_API_KEY"],
            openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
            min_apy_threshold=float(os.getenv("MIN_APY_THRESHOLD", "100")),
            # ... etc
        )
```

### Error Handler
```python
# utils/error_handler.py
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def handle_api_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError as e:
            logger.error(f"App error: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.exception("Unexpected error")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper
```

### Type-Safe API Client
```typescript
// lib/api.ts
interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  retries?: number;
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class TypedApiClient {
  constructor(private config: ApiConfig) {}
  
  async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.config.baseUrl}${path}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      const data = await response.json();
      
      return {
        data: response.ok ? data : undefined,
        error: response.ok ? undefined : data.detail || 'Request failed',
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }
}
```

## Testing Strategy

### Unit Tests
```python
# tests/test_degen_scorer.py
def test_liquidity_scoring():
    scorer = DegenScorerTool()
    assert scorer._score_liquidity({"tvl": 1000000}) == 10.0
    assert scorer._score_liquidity({"tvl": 10000}) == 5.0
    assert scorer._score_liquidity({"tvl": 100}) == 1.0
```

### Integration Tests
```python
# tests/test_api.py
async def test_scan_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/scan", json={"min_apy": 500})
        assert response.status_code == 200
        assert "pools" in response.json()
```

## Monitoring & Observability

### Metrics to Track
- API response times
- Error rates by endpoint
- Pool scanner success rate
- Position P&L over time
- Agent execution times

### Logging Strategy
```python
import structlog

logger = structlog.get_logger()

logger.info("pool_scanned", 
    pool_address=pool_address,
    apy=apy,
    tvl=tvl,
    risk_score=risk_score
)
```

## Deployment Checklist

- [ ] All environment variables documented
- [ ] Secrets stored in secure vault
- [ ] CORS configured for production domains
- [ ] Rate limiting enabled
- [ ] Error tracking configured (Sentry)
- [ ] Monitoring dashboards created
- [ ] Database backups configured
- [ ] SSL certificates installed
- [ ] CDN configured for static assets
- [ ] Load testing completed