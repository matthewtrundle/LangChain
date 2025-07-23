/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Cyber terminal theme - high energy colors
        'cyber': {
          primary: '#00ff88',      // Electric green (success/profit)
          secondary: '#ff0080',    // Hot pink (danger/extreme)
          tertiary: '#00d4ff',     // Cyan blue (info/analysis)
          warning: '#ffaa00',      // Bright orange (warning)
          purple: '#8b5cf6',       // Keep existing purple
        },
        
        // Terminal background system - deeper, richer
        'terminal': {
          bg: '#000008',           // Almost black with blue tint
          surface: '#0a0a12',      // Dark blue-black
          card: '#141420',         // Lighter surface
          border: '#1a1a2e',       // Subtle borders
          accent: '#242438',       // Hover states
        },
        
        // Text hierarchy - better contrast
        'text': {
          primary: '#ffffff',      // Pure white
          secondary: '#e0e0ff',    // Light blue-white
          tertiary: '#b0b0d0',     // Muted blue-gray
          accent: '#00ff88',       // Green accent text
        },
        
        // APY/Performance colors - more dramatic
        'performance': {
          extreme: '#ff0080',      // Hot pink for 2000%+
          high: '#ff4500',         // Orange red for 1000%+
          good: '#ffaa00',         // Gold for 500%+
          normal: '#00ff88',       // Green for standard
        },

        // Legacy colors for compatibility
        'degen': {
          primary: '#00ff88',
          secondary: '#00d4ff',
          success: '#00ff88',
          warning: '#ffaa00',
          danger: '#ff0080',
          bg: '#000008',
          surface: '#141420',
          border: '#1a1a2e',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Fira Code', 'ui-monospace', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-subtle': 'bounce 1s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'grid-move': 'grid-move 20s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite alternate',
        'number-count': 'number-count 1s ease-out',
        'cyber-pulse': 'cyber-pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up-fade': 'slide-up-fade 0.5s ease-out',
        'glow-rotate': 'glow-rotate 3s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'grid-move': {
          '0%': { transform: 'translate(0, 0)' },
          '100%': { transform: 'translate(50px, 50px)' },
        },
        'pulse-glow': {
          '0%': { 
            textShadow: '0 0 20px rgba(0, 255, 136, 0.5)',
            transform: 'scale(1)',
          },
          '100%': { 
            textShadow: '0 0 30px rgba(0, 255, 136, 0.8)',
            transform: 'scale(1.02)',
          },
        },
        'cyber-pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        'slide-up-fade': {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'glow-rotate': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      boxShadow: {
        'glow': '0 0 20px rgba(0, 255, 136, 0.3)',
        'glow-green': '0 0 20px rgba(0, 255, 136, 0.3)',
        'glow-red': '0 0 20px rgba(255, 0, 128, 0.3)',
        'glow-blue': '0 0 20px rgba(0, 212, 255, 0.3)',
        'glow-orange': '0 0 20px rgba(255, 170, 0, 0.3)',
        'cyber-glow': '0 0 40px rgba(0, 255, 136, 0.2), 0 0 80px rgba(0, 255, 136, 0.1)',
        'card-hover': '0 20px 40px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 255, 136, 0.1)',
      },
      fontSize: {
        '7xl': '5rem',
        '8xl': '6rem',
        '9xl': '7rem',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [],
}