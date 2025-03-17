import { SignUpForm } from "@/components/signup-form"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center space-y-6">
          <div className="h-24" /> {/* Spacing above logo */}
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-03-05%20at%209.42.58%20PM-GHuHTxWXGTn1xOnyk9xK6vJE0x3QEB.png"
            alt="MoolAI Logo"
            width={180}
            height={70}
            className="mx-auto"
          />
          <div>
            <h1 className="text-4xl font-bold text-white">Create Account</h1>
            <p className="mt-2 text-gray-400">Enter the details below to sign up</p>
          </div>
        </div>
        <SignUpForm />
        <div className="text-center text-sm">
          <p className="text-gray-400">
            Already have an account?{" "}
            <Button variant="link" asChild className="p-0">
              <Link href="/login" className="text-primary">
                Login
              </Link>
            </Button>
          </p>
        </div>
      </div>
    </div>
  )
}

