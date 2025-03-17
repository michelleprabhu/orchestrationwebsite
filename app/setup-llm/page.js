import { SetupProfileForm } from "@/components/setup-profile-form"
import Image from "next/image"

export default function SetupProfilePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Image src="/moolai-logo.png" alt="MoolAI Logo" width={180} height={70} className="mx-auto mb-6" />
          <h1 className="text-4xl font-bold text-white">Set Up Your Profile</h1>
          <p className="mt-2 text-gray-400">Configure your profile to get started</p>
        </div>
        <SetupProfileForm />
      </div>
    </div>
  )
}

