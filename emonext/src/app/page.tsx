"use client";
import { useState, useEffect } from "react";
import axios from "axios";

export default function Home() {
  const [clientId, setClientId] = useState("");
  const [assignedSubscriber, setAssignedSubscriber] = useState(null);
  const [emojiCounts, setEmojiCounts] = useState<Record<string, number>>({});
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamInterval, setStreamInterval] = useState<NodeJS.Timeout | null>(null);

  const emojis = ["😀", "😂", "🥳", "😎", "🔥", "🚀", "🎉", "💖", "🌟", "💡", "🍕", "🎵"];

  const getRandomEmoji = () => emojis[Math.floor(Math.random() * emojis.length)];

  const registerClient = async () => {
    try {
      const response = await axios.post("http://localhost:5000/register_client", {
        client_id: clientId,
      });
      setAssignedSubscriber(response.data.assigned_subscriber);
    } catch (error) {
      console.error("Registration failed", error);
    }
  };

  const sendEmoji = async () => {
    if (!assignedSubscriber) {
      alert("Register first!");
      return;
    }
    try {
      await axios.post("http://localhost:5000/emoji", {
        emoji_type: getRandomEmoji(),
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.error("Failed to send emoji", error);
    }
  };

  const startStreaming = () => {
    if (!assignedSubscriber) {
      alert("Register first!");
      return;
    }
    setIsStreaming(true);
    const interval = setInterval(sendEmoji, 1000);
    setStreamInterval(interval);
  };

  const stopStreaming = () => {
    setIsStreaming(false);
    if (streamInterval) {
      clearInterval(streamInterval);
      setStreamInterval(null);
    }
  };

  useEffect(() => {
    if (assignedSubscriber) {
      const { port } = assignedSubscriber;
      const ws = new WebSocket(`ws://localhost:${port}`);

      ws.onopen = () => console.log(`Connected to subscriber on port ${port}`);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log(data);
          setEmojiCounts((prev) => ({ ...prev, ...data }));
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onerror = (error) => console.error("WebSocket error:", error);
      ws.onclose = () => console.log("WebSocket connection closed");

      setSocket(ws);
    }
  }, [assignedSubscriber]);

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-100 p-10">
      <h1 className="text-3xl font-bold text-blue-600">🎭 Kafka Emoji Stream</h1>

      {/* Input Field and Register Button */}
      <div className="mt-6 flex items-center gap-3">
        <input
          type="text"
          placeholder="Enter Client ID"
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
          className="border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={registerClient}
          className="bg-blue-500 hover:bg-blue-600 text-white px-5 py-3 rounded-lg transition-all"
        >
          Register
        </button>
      </div>

      {assignedSubscriber && (
        <div className="mt-5 text-green-600 text-lg font-medium">
          ✅ Assigned to: <span className="font-bold">{JSON.stringify(assignedSubscriber)}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-8 flex gap-4">
        <button
          onClick={sendEmoji}
          className="bg-green-500 hover:bg-green-600 text-white px-5 py-3 rounded-lg transition-all"
        >
          🎭 Send Random Emoji
        </button>
        {isStreaming ? (
          <button
            onClick={stopStreaming}
            className="bg-red-500 hover:bg-red-600 text-white px-5 py-3 rounded-lg transition-all"
          >
            ⏹ Stop Streaming
          </button>
        ) : (
          <button
            onClick={startStreaming}
            className="bg-yellow-500 hover:bg-yellow-600 text-white px-5 py-3 rounded-lg transition-all"
          >
            ▶ Start Streaming
          </button>
        )}
      </div>

      {/* Live Emoji Counts Section */}
      <h2 className="mt-10 text-2xl font-semibold text-gray-700">📊 Live Emoji Counts</h2>
      <div className="mt-6 bg-white shadow-lg rounded-lg p-6 w-full max-w-lg">
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(emojiCounts).length > 0 ? (
            Object.entries(emojiCounts).map(([emoji, count]) => (
              <div
                key={emoji}
                className="flex flex-col items-center p-4 bg-gray-200 rounded-lg shadow-md"
              >
                <span className="text-4xl">{emoji}</span>
                <span className="text-lg font-bold">{count}</span>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center col-span-3">No data yet...</p>
          )}
        </div>
      </div>
    </div>
  );
}
