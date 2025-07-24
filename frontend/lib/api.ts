import { ScanResult, AgentResponse, CoordinatorResponse } from './types'

// Get API URL from environment variable or use default
const getApiUrl = () => {
  // In production, use the environment variable
  if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  
  // Fallback to the Railway backend URL if env var not available
  return 'https://langchain-production-881c.up.railway.app'
}

const API_BASE_URL = getApiUrl()

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    // Ensure URL doesn't have trailing slash
    this.baseUrl = baseUrl.replace(/\/$/, '')
    console.log('API Client initialized with URL:', this.baseUrl)
  }

  async hunt(query: string): Promise<CoordinatorResponse> {
    const response = await fetch(`${this.baseUrl}/hunt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    })

    if (!response.ok) {
      throw new Error(`Hunt failed: ${response.statusText}`)
    }

    return response.json()
  }

  async scan(minApy: number = 500, maxAgeHours: number = 48): Promise<ScanResult> {
    const response = await fetch(`${this.baseUrl}/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        min_apy: minApy,
        max_age_hours: maxAgeHours,
      }),
    })

    if (!response.ok) {
      throw new Error(`Scan failed: ${response.statusText}`)
    }

    return response.json()
  }

  async analyze(poolAddress: string): Promise<AgentResponse> {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pool_address: poolAddress }),
    })

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getSystemStatus(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/system/status`)

    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`)
    }

    return response.json()
  }

  async checkHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`)

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }

    return response.json()
  }
}

// Create client with API URL
export const apiClient = new ApiClient()