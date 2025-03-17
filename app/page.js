import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"
import { redirect } from "next/navigation"

export default function Home() {
  // Redirect directly to login page
  redirect("/login")

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center text-center">
        <Image src="/moolai-logo.png" alt="MoolAI Logo" width={200} height={80} className="mx-auto mb-8" />
        <h1 className="text-4xl sm:text-6xl font-bold text-white mb-6">
          Welcome to <span className="text-primary">MoolAI</span>
        </h1>
        <p className="text-lg text-gray-300 mb-8">Your personal AI assistant powered by cutting-edge language models</p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg" className="text-lg">
            <Link href="/signup">Get Started</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="text-lg">
            <Link href="/login">Login</Link>
          </Button>
        </div>
      </div>
    </main>
  )
}

