import { ScanResult, AgentResponse, CoordinatorResponse } from './types'

const API_BASE_URL = 'http://localhost:8000'

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
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

export const apiClient = new ApiClient()