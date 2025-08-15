'use client'

import { motion, useAnimation } from 'framer-motion'
import { useEffect, useState } from 'react'

export default function AnimatedHero() {
  const controls = useAnimation()
  const [isLoaded, setIsLoaded] = useState(false)
  
  useEffect(() => {
    setIsLoaded(true)
    controls.start('visible')
  }, [controls])
  
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  }
  
  const titleVariants = {
    hidden: { 
      opacity: 0, 
      y: 50,
      scale: 0.8
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: "spring" as const,
        stiffness: 100,
        damping: 15,
        duration: 0.8
      }
    }
  }
  
  const glowVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: [0, 0.5, 0.3],
      transition: {
        duration: 2,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    }
  }
  
  return (
    <motion.div
      initial="hidden"
      animate={controls}
      variants={containerVariants}
      className="relative text-center space-y-6 mb-16"
    >
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 0.1, scale: 1 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
        >
          <div className="w-[800px] h-[800px] bg-cyber-primary rounded-full blur-3xl" />
        </motion.div>
      </div>
      
      {/* Main title with glow effect */}
      <div className="relative">
        <motion.div
          variants={glowVariants}
          className="absolute inset-0 blur-2xl"
        >
          <h1 className="text-cyber-title text-cyber-primary opacity-50">
            SOL<span className="text-cyber-secondary">DEGEN</span>
          </h1>
        </motion.div>
        
        <motion.h1
          variants={titleVariants}
          className="text-cyber-title relative z-10"
        >
          <motion.span
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            SOL
          </motion.span>
          <motion.span
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.5 }}
            className="text-cyber-primary"
          >
            DEGEN
          </motion.span>
        </motion.h1>
      </div>
      
      {/* Animated subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.8 }}
        className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed"
      >
        Multi-agent AI system hunting{' '}
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3, duration: 0.5 }}
          className="text-cyber-primary font-semibold"
        >
          extreme yields
        </motion.span>{' '}
        across Solana DeFi protocols
      </motion.p>
      
      {/* Animated stats bar */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.8 }}
        className="flex justify-center items-center gap-8 text-sm"
      >
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="flex items-center gap-2"
        >
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [1, 0.7, 1]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatType: "loop" as const
            }}
            className="status-dot status-online"
          />
          <span className="text-terminal">4 AGENTS ACTIVE</span>
        </motion.div>
        
        <div className="text-text-tertiary">|</div>
        
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.7 }}
          className="text-cyber-tertiary"
        >
          SCANNING 47 PROTOCOLS
        </motion.div>
        
        <div className="text-text-tertiary">|</div>
        
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ 
            delay: 2,
            type: "spring" as const,
            stiffness: 200,
            damping: 15
          }}
          className="text-performance-extreme font-bold"
        >
          HIGHEST: 2,847% APY
        </motion.div>
      </motion.div>
      
      {/* Animated particles */}
      {isLoaded && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ 
                opacity: 0,
                x: Math.random() * window.innerWidth,
                y: window.innerHeight + 50
              }}
              animate={{
                opacity: [0, 0.5, 0],
                y: -50,
                x: `+=${Math.random() * 200 - 100}`
              }}
              transition={{
                duration: Math.random() * 5 + 5,
                delay: Math.random() * 3,
                repeat: Infinity,
                repeatType: "loop" as const
              }}
              className="absolute"
            >
              <div className="w-1 h-1 bg-cyber-primary rounded-full" />
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  )
}