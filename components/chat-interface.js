"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, Mic, Send, Search } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export function ChatInterface() {
  const [input, setInput] = useState("");
  const [chats, setChats] = useState([
    { id: 1, userMessage: "Hello, how are you?", botResponse: "I'm doing well, thank you!" },
    { id: 2, userMessage: "What's the weather like today?", botResponse: "It's sunny with a high of 75 degrees." },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setChats([...chats, { userMessage, botResponse: "Loading..." }]);
    setInput("");
    setIsLoading(true);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await fetch("http://localhost:8000/process_prompt", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt: input }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }

        const data = await response.json();

        setChats((prevChats) => {
          const updatedChats = [...prevChats];
          updatedChats[updatedChats.length - 1].botResponse = data.response;
          return updatedChats;
        });
      } catch (fetchError) {
        console.error("API call failed:", fetchError);

        let errorMessage = "Sorry, I couldn't connect to the AI service.";

        if (fetchError.name === "AbortError") {
          errorMessage = "The request timed out. Please check if the backend server is running.";
        } else if (fetchError.message.includes("Failed to fetch")) {
          errorMessage = "Couldn't connect to the backend server. Please make sure it's running at http://localhost:8000";
        }

        setChats((prevChats) => {
          const updatedChats = [...prevChats];
          updatedChats[updatedChats.length - 1].botResponse = errorMessage;
          return updatedChats;
        });
      }
    } catch (error) {
      console.error("Error in message handling:", error);
      setChats((prevChats) => {
        const updatedChats = [...prevChats];
        updatedChats[updatedChats.length - 1].botResponse =
          "Sorry, I encountered an unexpected error. Please try again.";
        return updatedChats;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex w-full h-screen bg-[#121212]">
      {/* Sidebar */}
      <div className="w-64 flex flex-col h-full bg-[#1A1A1A] border-r border-gray-800">
        <div className="p-4">
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Screenshot%202025-03-05%20at%209.42.58%20PM-GHuHTxWXGTn1xOnyk9xK6vJE0x3QEB.png"
            alt="MoolAI Logo"
            width={120}
            height={40}
          />
        </div>

        <div className="p-4 space-y-2">
          <Button variant="ghost" className="w-full flex items-center justify-start gap-2 text-white hover:bg-gray-800">
            <Plus size={16} /> New Chat
          </Button>

          <Link href="/dashboard">
            <Button variant="ghost" className="w-full flex items-center justify-start gap-2 text-white hover:bg-gray-800">
              Dashboard
            </Button>
          </Link>
        </div>

        <div className="px-4 py-2">
          <p className="px-2 py-1.5 text-sm text-gray-400">Previous Chats</p>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
            <Input placeholder="Search chats..." className="pl-8 bg-[#2A2A2A] border-none" />
          </div>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {chats.map((chat, index) => (
              <Button key={index} variant="ghost" className="w-full justify-start text-left px-2 py-2 h-auto text-gray-300 hover:bg-gray-800">
                Chat {index + 1}
              </Button>
            ))}
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-gray-800">
          <Button variant="ghost" className="w-full justify-start gap-2">
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
              <span className="text-primary-foreground">M</span>
            </div>
            <div className="text-left">
              <p className="text-sm font-medium text-white">Michelle</p>
              <p className="text-xs text-gray-400">michelle@example.com</p>
            </div>
          </Button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative bg-[#121212]">
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-3xl mx-auto space-y-8">
            {chats.map((chat, index) => (
              <div key={index} className="space-y-4">
                {/* User Message - Right-aligned */}
                <div className="flex justify-end">
                  <div className="bg-white text-black rounded-lg p-4 max-w-[60%] shadow-md">
                    <p className="text-base font-medium">{chat.userMessage}</p>
                  </div>
                </div>

                {/* Bot Response - Left-aligned */}
                <div className="flex justify-start">
                  <div className="bg-[#FF4500] text-white rounded-lg p-4 max-w-[60%] shadow-md">
                    {chat.botResponse === "Loading..." ? (
                      <div className="flex space-x-2">
                        <div className="h-3 w-3 bg-white rounded-full animate-bounce"></div>
                        <div className="h-3 w-3 bg-white rounded-full animate-bounce delay-100"></div>
                        <div className="h-3 w-3 bg-white rounded-full animate-bounce delay-200"></div>
                      </div>
                    ) : (
                      <p className="text-base font-medium">{chat.botResponse}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="absolute bottom-8 left-0 right-0">
          <div className="max-w-3xl mx-auto px-4">
            <div className="relative">
              <Input
                placeholder="How can I help you today?"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                disabled={isLoading}
                className="pl-12 pr-32 py-6 bg-[#2A2A2A] border-none text-white placeholder-gray-400"
              />

              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                <Button variant="ghost" size="icon" className="text-gray-400 hover:text-white">
                  <Mic className="h-5 w-5" />
                </Button>

                <Button onClick={handleSend} disabled={!input.trim() || isLoading} size="icon" className="bg-primary text-primary-foreground hover:bg-primary/90">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
