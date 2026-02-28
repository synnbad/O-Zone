import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, MessageCircle, Send, Bot, User } from "lucide-react";
import { useUser } from "../context/UserContext";
import { useChat } from "../hooks/useChat";

export function Chat() {
  const navigate = useNavigate();
  const { profile } = useUser();
  const { messages, sendMessage, loading } = useChat();
  const [inputText, setInputText] = useState("");

  const quickQuestions = [
    "Is it safe to exercise outside?",
    "What's the air quality forecast?",
    "Tips to improve indoor air quality",
    "Best time for outdoor activities",
  ];

  const handleSend = async () => {
    if (!inputText.trim() || loading) return;
    
    await sendMessage(inputText);
    setInputText("");
  };

  const handleQuickQuestion = async (question: string) => {
    await sendMessage(question);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-pink-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl">AI Assistant</h1>
            <p className="text-sm opacity-90">Personalized recommendations</p>
          </div>
          <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              message.role === "assistant" ? "bg-pink-500" : "bg-blue-500"
            }`}>
              {message.role === "assistant" ? (
                <Bot className="w-5 h-5 text-white" />
              ) : (
                <User className="w-5 h-5 text-white" />
              )}
            </div>
            <div
              className={`max-w-[75%] rounded-2xl p-3 ${
                message.role === "assistant"
                  ? "bg-white shadow"
                  : "bg-blue-500 text-white"
              }`}
            >
              <p className="text-sm whitespace-pre-line">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.role === "assistant" ? "text-gray-400" : "text-blue-100"
              }`}>
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Questions */}
      <div className="p-4 bg-white border-t">
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-2">Quick questions:</p>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {quickQuestions.map((q) => (
              <button
                key={q}
                onClick={() => handleQuickQuestion(q)}
                className="px-3 py-2 bg-gray-100 rounded-full text-xs whitespace-nowrap hover:bg-gray-200"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about air quality..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-pink-500"
          />
          <button
            onClick={handleSend}
            className="w-12 h-12 bg-pink-500 text-white rounded-full flex items-center justify-center hover:bg-pink-600"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
