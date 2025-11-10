'use client'

import React, { useEffect, useRef } from 'react'

interface IridescenceProps {
  color?: [number, number, number]
  mouseReact?: boolean
  amplitude?: number
  speed?: number
}

const Iridescence: React.FC<IridescenceProps> = ({
  color = [1, 1, 1],
  mouseReact = false,
  amplitude = 0.1,
  speed = 1.0,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mousePos = useRef({ x: 0.5, y: 0.5 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const setCanvasSize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    setCanvasSize()
    window.addEventListener('resize', setCanvasSize)

    const handleMouseMove = (e: MouseEvent) => {
      if (mouseReact) {
        mousePos.current = {
          x: e.clientX / window.innerWidth,
          y: e.clientY / window.innerHeight,
        }
      }
    }
    window.addEventListener('mousemove', handleMouseMove)

    let time = 0
    const animate = () => {
      time += 0.01 * speed

      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
      
      const hue1 = (time * 50) % 360
      const hue2 = (time * 50 + 60) % 360
      const hue3 = (time * 50 + 120) % 360
      const hue4 = (time * 50 + 180) % 360

      gradient.addColorStop(0, `hsla(${hue1}, 70%, 60%, 0.3)`)
      gradient.addColorStop(0.33, `hsla(${hue2}, 70%, 60%, 0.3)`)
      gradient.addColorStop(0.66, `hsla(${hue3}, 70%, 60%, 0.3)`)
      gradient.addColorStop(1, `hsla(${hue4}, 70%, 60%, 0.3)`)

      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Add noise effect
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const data = imageData.data
      
      for (let i = 0; i < data.length; i += 4) {
        const noise = (Math.random() - 0.5) * amplitude * 50
        data[i] = Math.min(255, Math.max(0, data[i] + noise))
        data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + noise))
        data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + noise))
      }
      
      ctx.putImageData(imageData, 0, 0)

      requestAnimationFrame(animate)
    }
    animate()

    return () => {
      window.removeEventListener('resize', setCanvasSize)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [color, mouseReact, amplitude, speed])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full -z-10"
      style={{ pointerEvents: 'none' }}
    />
  )
}

export default Iridescence