import { LoginForm } from "@/components/login-form"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Image src="/moolai-logo.png" alt="MoolAI Logo" width={180} height={70} className="mx-auto mb-6" />
          <h1 className="text-4xl font-bold text-white">Let's Get Started</h1>
          <p className="mt-2 text-gray-400">Enter details to login</p>
        </div>
        <LoginForm />
        <div className="text-center text-sm">
          <p className="text-gray-400">
            Don&apos;t have an account?{" "}
            <Button variant="link" asChild className="p-0">
              <Link href="/signup" className="text-primary">
                Sign Up
              </Link>
            </Button>
          </p>
        </div>
      </div>
    </div>
  )
}

