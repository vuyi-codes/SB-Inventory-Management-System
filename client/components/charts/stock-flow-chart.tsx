"use client"

import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, Cell, LabelList, XAxis } from "recharts"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

export const description = "A bar chart showing net stock movements"

// Adapted for your inventory system (Stock In vs Stock Out / Adjustments)
const chartData = [
  { month: "May", netFlow: 145 },
  { month: "Jun", netFlow: 210 },
  { month: "Jul", netFlow: -85 },
  { month: "Aug", netFlow: 190 },
  { month: "Sep", netFlow: -120 },
  { month: "Oct", netFlow: 230 },
]

const chartConfig = {
  netFlow: {
    label: "Net Stock Flow",
  },
} satisfies ChartConfig

export function StockFlowChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Net Inventory Flow</CardTitle>
        <CardDescription>May - October Stock Adjustments</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart accessibilityLayer data={chartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel hideIndicator />}
            />
            <Bar dataKey="netFlow">
              {chartData.map((item) => (
                <Cell
                  key={item.month}
                  fill={item.netFlow > 0 ? "var(--chart-1)" : "var(--chart-2)"}
                />
              ))}
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 leading-none font-medium">
          Net stock increased by 14.2% this quarter <TrendingUp className="h-4 w-4" />
        </div>
        <div className="leading-none text-muted-foreground">
          Comparing total stock-ins versus stock-outs
        </div>
      </CardFooter>
    </Card>
  )
}