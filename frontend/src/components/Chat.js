import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, Send } from 'lucide-react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import {  toast } from 'react-toastify';
import { useAuth } from "../context/AuthContext";


export const ChatUI = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);
  const [userId, setUserId] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const fileInputRef = useRef(null);
  const {currentUser} = useAuth();
  useEffect(() => {
    setUserId(currentUser.user_id);
    fetchChatHistory(currentUser.user_id);
    fetchUserFiles(currentUser.user_id);
  }, []);


  const fetchChatHistory = async (userId) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_KEY}/chat/get_chat_history/${userId}`);
      const chatHistory = response.data.map((msg) => ({
        id: uuidv4(),
        content: msg.content,
        sender: msg.sender,
      }));
      setMessages(chatHistory);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const fetchUserFiles = async (userId) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_KEY}/embedding/get/user_files`, {
        headers: { user_id: userId },
      });
      const files = response.data.files.map((file) => ({
        id: uuidv4(),
        name: file,
        userId,
      }));
      setDocuments(files);
    } catch (error) {
      console.log("no file")
    }
  };

  

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = {
        id: uuidv4(),
        content: input,
        sender: 'user'
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsSending(true);
      setIsTyping(true);

      try {
        const response = await axios.post(`${process.env.REACT_APP_API_KEY}/chat/send_message`, {
          userId,
          content: input,
          sender: "user"
        });
        const aiMessage = {
          ...response.data,
          id: uuidv4(),
          sender: 'ai'
        };
        setMessages((prev) => [...prev, aiMessage]);
      } catch (error) {
        console.error('Message sending failed:', error);
        toast.error('Message sending failed');
      } finally {
        setIsSending(false);
        setIsTyping(false);
      }

      setInput('');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setIsUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      console.log(formData.get("file"));
      console.log(userId);

      toast.promise(
        axios.post(`${process.env.REACT_APP_API_KEY}/embedding/add/document`, formData, {
          headers: {
            'Content-Type': false, 
            user_id:userId
          }
        }),
        {
          pending: 'Uploading file...',
          success: 'File uploaded successfully!',
          error: 'File upload failed'
        }
      )
      .then((response) => {
        const newDoc = {
          id: uuidv4(),
          name: file.name,
          userId
        };
        setDocuments((prev) => [...prev, newDoc]);
      })
      .catch((error) => {
        console.error('Upload failed:', error?.response?.data || error.message);
      })
      .finally(() => {
        setIsUploading(false);
      });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      
      <div className="w-64 bg-white p-4 border-r">
        <h2 className="text-lg font-semibold mb-4">Uploaded Documents</h2>
        <div className="space-y-2">
          {documents.map((doc) => (
            <div key={doc.id} className="p-2 bg-gray-50 rounded-lg text-sm">
              <p className="font-medium truncate">{doc.name}</p>
            </div>
          ))}
          {documents.length === 0 && (
            <p className="text-sm text-gray-500">No documents uploaded yet</p>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] p-3 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white border border-gray-200'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start mb-4">
              <div className="max-w-[70%] p-3 rounded-lg bg-white border border-gray-200 text-gray-500">
                <span className="typing-dots">Typing...</span>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t bg-white">
          <div className="flex items-center gap-2">
            <button 
              onClick={() => fileInputRef.current.click()} 
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              disabled={isUploading}
            >
              {isUploading ? (
                <div className="loader w-5 h-5 border-2 border-gray-300 border-t-2 border-t-blue-500 rounded-full animate-spin"></div>
              ) : (
                <Paperclip className="w-5 h-5 text-gray-500" />
              )}
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
            />
            <div className="flex-1 flex items-center border rounded-lg bg-white">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 outline-none"
                disabled={isSending}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isSending}
                className="p-2 text-blue-500 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSending ? (
                  <div className="loader w-5 h-5 border-2 border-gray-300 border-t-2 border-t-blue-500 rounded-full animate-spin"></div>
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
