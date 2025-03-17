"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts"

export function DashboardContent() {
  // Cost Optimization Impact Data
  const costOptimizationData = [
    { month: "Jan", potential: 500, actual: 300 },
    { month: "Feb", potential: 600, actual: 400 },
    { month: "Mar", potential: 400, actual: 200 },
    { month: "Apr", potential: 450, actual: 250 },
    { month: "May", potential: 400, actual: 200 },
  ]

  // Monthly Cost Breakdown Data
  const monthlyBreakdownData = Array.from({ length: 15 }, (_, i) => ({
    day: i + 1,
    openai: Math.sin((i / 15) * Math.PI * 2) * 10 + 15,
    moolai: Math.cos((i / 15) * Math.PI * 2) * 8 + 12,
  }))

  // Monthly API Calls Data
  const apiCallsData = Array.from({ length: 15 }, (_, i) => ({
    day: i + 1,
    openai: Math.sin((i / 15) * Math.PI * 2) * 8 + 12,
    moolai: Math.cos((i / 15) * Math.PI * 2) * 8 + 12,
  }))

  // Distribution Data
  const callDistributionData = [
    { name: "OpenAI", value: 50 },
    { name: "MoolAI", value: 50 },
  ]

  const costDistributionData = [
    { name: "OpenAI", value: 90 },
    { name: "MoolAI", value: 10 },
  ]

  const COLORS = {
    openai: "#22D3EE",
    moolai: "#FF4500",
  }

  return (
    <div className="flex-1 p-8 bg-[#121212]">
      <div className="max-w-[1400px] mx-auto space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            Hello, Michelle
            <span role="img" aria-label="wave">
              👋
            </span>
          </h1>
          <p className="text-gray-400 mt-1">Track your model usage and compare costs right here.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-4">
          {/* Total Savings */}
          <Card className="bg-[#1A1A1A] border-gray-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Total Savings with MoolAI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">$5,184</div>
              <p className="text-xs text-green-500">+16% from last month</p>
            </CardContent>
          </Card>

          {/* Total API Calls */}
          <Card className="bg-[#1A1A1A] border-gray-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Total API Calls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white mb-2">1,000</div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                    <span className="text-sm text-gray-400">OpenAI</span>
                  </div>
                  <p className="text-white ml-4">500</p>
                  <p className="text-xs text-gray-500 ml-4">400k tokens Used</p>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                    <span className="text-sm text-gray-400">MoolAI</span>
                  </div>
                  <p className="text-white ml-4">500</p>
                  <p className="text-xs text-gray-500 ml-4">400k tokens Used</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Total Cost */}
          <Card className="bg-[#1A1A1A] border-gray-800 col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-400">Total Cost</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                    <span className="text-sm text-gray-400">OpenAI</span>
                  </div>
                  <p className="text-white ml-4">$5760</p>
                  <p className="text-xs text-gray-500 ml-4">Avg $0.02 per query</p>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                    <span className="text-sm text-gray-400">MoolAI</span>
                  </div>
                  <p className="text-white ml-4">$576</p>
                  <p className="text-xs text-gray-500 ml-4">Avg $0.002 per query</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 grid-cols-2">
          {/* Cost Optimization Impact */}
          <Card className="bg-[#1A1A1A] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg font-medium text-white">Cost Optimization Impact</CardTitle>
                <div className="mt-1">
                  <span className="text-2xl font-bold text-white">$5,184</span>
                  <span className="text-sm ml-2 text-gray-400">saved</span>
                </div>
                <p className="text-xs text-gray-500">800k tokens used</p>
              </div>
              <Select defaultValue="2025">
                <SelectTrigger className="w-[100px]">
                  <SelectValue placeholder="2025" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2025">2025</SelectItem>
                  <SelectItem value="2024">2024</SelectItem>
                </SelectContent>
              </Select>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={costOptimizationData} barGap={0}>
                    <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#666" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: "#666" }} />
                    <Bar dataKey="potential" fill="#22D3EE" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="actual" fill="#FF4500" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-between mt-4">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                  <span className="text-sm text-gray-400">Potential Cost: $11,520</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                  <span className="text-sm text-gray-400">Actual Cost: $6,336</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Monthly Cost Breakdown */}
          <Card className="bg-[#1A1A1A] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg font-medium text-white">Monthly Cost Breakdown</CardTitle>
                <div className="mt-1">
                  <span className="text-2xl font-bold text-white">$3,960</span>
                  <span className="text-sm ml-2 text-gray-400">spent</span>
                </div>
                <p className="text-xs text-gray-500">250,000 tokens</p>
              </div>
              <Select defaultValue="jan-2025">
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Jan 2025" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="jan-2025">Jan 2025</SelectItem>
                  <SelectItem value="feb-2025">Feb 2025</SelectItem>
                </SelectContent>
              </Select>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={monthlyBreakdownData}>
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#666" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: "#666" }} />
                    <Area type="monotone" dataKey="openai" stroke="#22D3EE" fill="#22D3EE" fillOpacity={0.2} />
                    <Area type="monotone" dataKey="moolai" stroke="#FF4500" fill="#FF4500" fillOpacity={0.2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-between mt-4">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                  <span className="text-sm text-gray-400">OpenAI Cost: $3,600</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                  <span className="text-sm text-gray-400">MoolAI Cost: $360</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Monthly API Calls */}
          <Card className="bg-[#1A1A1A] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg font-medium text-white">Monthly API Calls Comparison</CardTitle>
                <div className="mt-1">
                  <span className="text-2xl font-bold text-white">500</span>
                  <span className="text-sm ml-2 text-gray-400">calls</span>
                </div>
                <p className="text-xs text-gray-500">2,242 tokens</p>
              </div>
              <Select defaultValue="jan-2025">
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Jan 2025" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="jan-2025">Jan 2025</SelectItem>
                  <SelectItem value="feb-2025">Feb 2025</SelectItem>
                </SelectContent>
              </Select>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={apiCallsData}>
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#666" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: "#666" }} />
                    <Line type="monotone" dataKey="openai" stroke="#22D3EE" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="moolai" stroke="#FF4500" dot={false} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-between mt-4">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                  <span className="text-sm text-gray-400">OpenAI: 245</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                  <span className="text-sm text-gray-400">MoolAI: 255</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Distribution */}
          <Card className="bg-[#1A1A1A] border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-medium text-white">API Call vs Cost Distribution</CardTitle>
              <Select defaultValue="2025">
                <SelectTrigger className="w-[100px]">
                  <SelectValue placeholder="2025" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2025">2025</SelectItem>
                  <SelectItem value="2024">2024</SelectItem>
                </SelectContent>
              </Select>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-center text-sm text-gray-400 mb-4">Call</p>
                  <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={callDistributionData}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          startAngle={90}
                          endAngle={-270}
                        >
                          {callDistributionData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index === 0 ? COLORS.openai : COLORS.moolai} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-center gap-8 mt-4">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                      <span className="text-sm text-gray-400">50%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                      <span className="text-sm text-gray-400">50%</span>
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-center text-sm text-gray-400 mb-4">Cost</p>
                  <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={costDistributionData}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          startAngle={90}
                          endAngle={-270}
                        >
                          {costDistributionData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index === 0 ? COLORS.openai : COLORS.moolai} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-center gap-8 mt-4">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-[#22D3EE] rounded-full" />
                      <span className="text-sm text-gray-400">90%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 bg-[#FF4500] rounded-full" />
                      <span className="text-sm text-gray-400">10%</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
