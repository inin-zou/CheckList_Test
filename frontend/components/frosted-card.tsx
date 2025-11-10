import type React from "react"
import { cn } from "@/lib/utils"

interface FrostedCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function FrostedCard({ children, className, ...props }: FrostedCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl backdrop-blur-xl bg-white/70 dark:bg-gray-900/70",
        "border border-white/20 dark:border-gray-700/50",
        "shadow-lg shadow-blue-500/10 dark:shadow-cyan-500/10",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}
