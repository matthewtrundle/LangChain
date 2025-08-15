'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'
import confetti from 'canvas-confetti'

interface SuccessCelebrationProps {
  show: boolean
  profit: number
  onComplete?: () => void
}

export default function SuccessCelebration({ show, profit, onComplete }: SuccessCelebrationProps) {
  const [isVisible, setIsVisible] = useState(false)
  
  useEffect(() => {
    if (show) {
      setIsVisible(true)
      
      // Trigger confetti
      const duration = 3 * 1000
      const animationEnd = Date.now() + duration
      const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 }
      
      const randomInRange = (min: number, max: number) => {
        return Math.random() * (max - min) + min
      }
      
      const interval: any = setInterval(function() {
        const timeLeft = animationEnd - Date.now()
        
        if (timeLeft <= 0) {
          clearInterval(interval)
          setTimeout(() => {
            setIsVisible(false)
            onComplete?.()
          }, 1000)
          return
        }
        
        const particleCount = 50 * (timeLeft / duration)
        
        // Confetti from different angles
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
          colors: ['#00ff00', '#10b981', '#22c55e', '#86efac']
        })
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
          colors: ['#00ff00', '#10b981', '#22c55e', '#86efac']
        })
      }, 250)
      
      // Play success sound
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiS2Oy9diMFl2+z1qugUBQKOI7ZysCPW/CQql+2R8uw/4+jj5+e09Hj5PDf0r+1tq+sjoQdI06389K7s7uxNJLT/0LJX6iqpJqOHClJpe3pu62vrbIljdH/Vrl2kcSxa1cfJUed5dvJpJ6lqTCM0v9QsXePua1eVhhCm+DYyJ+cq7M7j9H+jUW0NdGicVMiFZ7euZqYsa89kMr3fEWvPMmleFAaEY/a1YyZmYGhJXTK2JZUvBzamm9XLhjA/8aXirGJmCJvytOZVrgb2KJwVi4hv/nFlomzh6cnbMXUmma1GtamdFQvH7v1wJeIs4emKHfH0ppotxjUo3NeLxa38sKahLCJpydvwtGbaLUX0al7Ui4vhhy8AkWwgP+PWbubq2eiqPuNmJeFihqNwndNHG/5wpyesnBGLx/+sLKxG5kyrJGQi/0aeYaz/u9+koLO7aDWyMDKq3lrJdyyjJp/lsQAABEREREREQ==')
      audio.play().catch(() => {})
    }
  }, [show, onComplete])
  
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
        >
          {/* Background overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.8 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          />
          
          {/* Success message */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 180 }}
            transition={{
              type: "spring" as const,
              stiffness: 200,
              damping: 20
            }}
            className="relative z-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-8 shadow-2xl"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-center space-y-4"
            >
              {/* Trophy icon */}
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  rotate: [0, 10, -10, 0]
                }}
                transition={{
                  duration: 0.5,
                  repeat: 3,
                  repeatType: "reverse" as const
                }}
                className="text-6xl"
              >
                🏆
              </motion.div>
              
              <h2 className="text-3xl font-bold text-white">
                Profitable Position!
              </h2>
              
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5, type: "spring" as const }}
                className="text-5xl font-bold text-white"
              >
                +${profit.toLocaleString()}
              </motion.div>
              
              <p className="text-green-100">
                Your yield hunting strategy is working!
              </p>
            </motion.div>
            
            {/* Animated rings */}
            <motion.div
              animate={{
                scale: [1, 1.5, 2],
                opacity: [0.5, 0.3, 0]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "loop" as const
              }}
              className="absolute inset-0 rounded-2xl border-4 border-white/30"
            />
            
            <motion.div
              animate={{
                scale: [1, 1.5, 2],
                opacity: [0.5, 0.3, 0]
              }}
              transition={{
                duration: 2,
                delay: 0.5,
                repeat: Infinity,
                repeatType: "loop" as const
              }}
              className="absolute inset-0 rounded-2xl border-4 border-white/20"
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Export a function to trigger celebration
export function triggerSuccessCelebration(profit: number) {
  const event = new CustomEvent('success-celebration', { detail: { profit } })
  window.dispatchEvent(event)
}