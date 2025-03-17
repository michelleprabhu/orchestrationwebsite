"use client"

import * as React from "react"
import {
  Area,
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { cn } from "@/lib/utils"

const ChartContainer = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("w-full h-full", className)} {...props} />
))
ChartContainer.displayName = "ChartContainer"

const Chart = React.forwardRef(({ className, variant = "default", ...props }, ref) => {
  if (variant === "pie") {
    return (
      <div ref={ref} className={cn("w-full h-full", className)}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart {...props} />
        </ResponsiveContainer>
      </div>
    )
  }

  return (
    <div ref={ref} className={cn("w-full h-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart {...props} />
      </ResponsiveContainer>
    </div>
  )
})
Chart.displayName = "Chart"

const ChartPie = React.forwardRef((props, _) => <Pie {...props} fill="#FF4500" stroke="none" />)
ChartPie.displayName = "ChartPie"

const ChartArea = React.forwardRef((props, _) => <Area {...props} type="monotone" strokeWidth={2} />)
ChartArea.displayName = "ChartArea"

const ChartBar = React.forwardRef((props, _) => <Bar {...props} radius={[4, 4, 0, 0]} />)
ChartBar.displayName = "ChartBar"

const ChartLine = React.forwardRef((props, _) => <Line {...props} type="monotone" strokeWidth={2} dot={false} />)
ChartLine.displayName = "ChartLine"

const ChartXAxis = React.forwardRef((props, _) => <XAxis {...props} stroke="#666" fontSize={12} />)
ChartXAxis.displayName = "ChartXAxis"

const ChartYAxis = React.forwardRef((props, _) => <YAxis {...props} stroke="#666" fontSize={12} />)
ChartYAxis.displayName = "ChartYAxis"

const ChartTooltip = React.forwardRef((props, _) => <Tooltip {...props} />)
ChartTooltip.displayName = "ChartTooltip"

const ChartLegend = React.forwardRef((props, _) => <Legend {...props} />)
ChartLegend.displayName = "ChartLegend"

const ChartGrid = React.forwardRef((props, _) => <CartesianGrid {...props} />)
ChartGrid.displayName = "ChartGrid"

export {
  Chart,
  ChartContainer,
  ChartArea,
  ChartBar,
  ChartLine,
  ChartPie,
  ChartXAxis,
  ChartYAxis,
  ChartTooltip,
  ChartLegend,
  ChartGrid,
  Cell,
}

