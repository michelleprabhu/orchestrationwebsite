import { Poppins } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
})

export const metadata = {
  title: "AI Chat Platform",
  description: "Your personal AI assistant",
    generator: 'v0.dev'
}

export const viewport = {
  themeColor: "#000000",
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${poppins.variable} font-poppins`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false} disableTransitionOnChange>
          <div className="min-h-screen bg-gradient-to-br from-black to-black via-orange-950">{children}</div>
        </ThemeProvider>
      </body>
    </html>
  )
}



import './globals.css'