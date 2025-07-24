// Debug file to check environment variables
export const debugInfo = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  nodeEnv: process.env.NODE_ENV,
  allEnvKeys: Object.keys(process.env).filter(key => key.startsWith('NEXT_PUBLIC_')),
}

console.log('🔍 Debug Info:', debugInfo)
console.log('🔍 API URL from env:', process.env.NEXT_PUBLIC_API_URL)
console.log('🔍 All NEXT_PUBLIC vars:', Object.keys(process.env).filter(key => key.startsWith('NEXT_PUBLIC_')).map(key => `${key}=${process.env[key]}`))