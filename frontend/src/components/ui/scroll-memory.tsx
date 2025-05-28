import * as React from "react"
import { cn } from "@/lib/utils"

interface ScrollMemoryProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  title?: string
  description?: string
}

const ScrollMemory = React.forwardRef<HTMLDivElement, ScrollMemoryProps>(
  ({ className, children, title, description, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600 text-white p-6 rounded-lg shadow-lg",
          className
        )}
        {...props}
      >
        {title && <h2 className="text-2xl font-bold mb-2">{title}</h2>}
        {description && <p className="text-sm opacity-90 mb-4">{description}</p>}
        {children}
      </div>
    )
  }
)
ScrollMemory.displayName = "ScrollMemory"

export { ScrollMemory } 