import Link from "next/link"
import { 
  Package, 
  AlertTriangle, 
  ShoppingCart, 
  TrendingUp, 
  ArrowUpRight, 
  Plus, 
  ArrowLeftRight, 
  FileText,
  Users
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { StockFlowChart } from "@/components/charts/stock-flow-chart"

export default function ManagerDashboardPage() {
  // Mock data representing database metrics (replace with actual DB queries or API calls)
  const stats = [
    { title: "Total Products", value: "1,248", change: "+4.2% this month", icon: Package, href: "/manager/inventory" },
    { title: "Low Stock Alerts", value: "12", change: "Requires attention", icon: AlertTriangle, href: "/manager/inventory", alert: true },
    { title: "Active Orders", value: "34", change: "+8 pending fulfillment", icon: ShoppingCart, href: "/manager/orders" },
    { title: "Total Stock Value", value: "R 482,500", change: "+12.1% vs last month", icon: TrendingUp, href: "/manager/reports" },
  ]

  const lowStockItems = [
    { id: 1, sku: "STA-001", name: "A4 Hardcover Notebook 192p", category: "Stationery", current: 8, min: 10 },
    { id: 2, sku: "BEV-042", name: "Energy Drink 500ml", category: "Beverages", current: 4, min: 15 },
    { id: 3, sku: "SNK-112", name: "Organic Protein Bar 60g", category: "Snacks", current: 6, min: 20 },
  ]

  const recentMovements = [
    { id: 1, sku: "BEV-001", product: "Sparkling Mineral Water 500ml", type: "IN", qty: "+120", user: "manager_admin", time: "10 mins ago" },
    { id: 2, sku: "SNK-001", product: "Artisanal Potato Chips 125g", type: "OUT", qty: "-15", user: "clerk_sarah", time: "35 mins ago" },
    { id: 3, sku: "STA-001", product: "A4 Hardcover Notebook 192p", type: "IN", qty: "+50", user: "manager_admin", time: "2 hours ago" },
  ]

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Top Header & Quick Actions */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Manager Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of inventory health, stock movements, and team operations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button asChild variant="outline">
            <Link href="/manager/inventory">
              <Plus className="mr-2 h-4 w-4" /> Add Product
            </Link>
          </Button>
          <Button asChild>
            <Link href="/manager/reports">
              <FileText className="mr-2 h-4 w-4" /> Generate Report
            </Link>
          </Button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index} className={stat.alert ? "border-destructive/50 bg-destructive/5" : ""}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.alert ? "text-destructive" : "text-muted-foreground"}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className={`text-xs ${stat.alert ? "text-destructive font-semibold" : "text-muted-foreground"} mt-1 flex items-center`}>
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="lg:col-span-3">
        <StockFlowChart />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        
        {/* Low Stock Alerts Table (Col span 4) */}
        <Card className="lg:col-span-4">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Low Stock Alerts</CardTitle>
              <CardDescription>Items that have fallen below safety minimum levels.</CardDescription>
            </div>
            <Button asChild size="sm" variant="ghost">
              <Link href="/manager/inventory">View all <ArrowUpRight className="ml-1 h-4 w-4" /></Link>
            </Button>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Product Name</TableHead>
                  <TableHead className="text-right">Current</TableHead>
                  <TableHead className="text-right">Min Level</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {lowStockItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-mono text-xs">{item.sku}</TableCell>
                    <TableCell className="font-medium">{item.name}</TableCell>
                    <TableCell className="text-right font-bold text-destructive">{item.current}</TableCell>
                    <TableCell className="text-right text-muted-foreground">{item.min}</TableCell>
                    <TableCell className="text-center">
                      <Badge variant="destructive">Critical</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Recent Stock Movements / Audit Log (Col span 3) */}
        <Card className="lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest stock adjustments & logs.</CardDescription>
            </div>
            <Button asChild size="sm" variant="ghost">
              <Link href="/manager/reports">Audit Log <ArrowUpRight className="ml-1 h-4 w-4" /></Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentMovements.map((mov) => (
                <div key={mov.id} className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0">
                  <div className="space-y-1">
                    <p className="text-sm font-medium leading-none">{mov.product}</p>
                    <p className="text-xs text-muted-foreground">Logged by <span className="font-mono">{mov.user}</span> • {mov.time}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={mov.type === "IN" ? "default" : "secondary"}>
                      {mov.qty}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}