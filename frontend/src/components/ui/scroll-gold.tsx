import * as React from "react"
import { cn } from "@/lib/utils"

interface ScrollGoldProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

const ScrollGold = React.forwardRef<HTMLDivElement, ScrollGoldProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-600 text-white p-6 rounded-lg shadow-lg",
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
ScrollGold.displayName = "ScrollGold"

export { ScrollGold } 