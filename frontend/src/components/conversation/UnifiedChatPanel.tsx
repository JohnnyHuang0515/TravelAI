"use client";

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  unifiedChat, 
  sendUnifiedMessage, 
  getUnifiedConversationState,
  resetUnifiedConversation,
  getUnifiedSuggestions,
  getUnifiedSessionStats,
  type UnifiedConversationResponse,
  type ConversationStateResponse
} from '@/lib/api/planning';

interface UnifiedChatPanelProps {
  sessionId: string;
  onItineraryGenerated?: (itinerary: any) => void;
  onError?: (error: string) => void;
  className?: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: string;
  intent?: string;
  confidence?: number;
  suggestions?: string[];
}

interface ProcessingStep {
  id: string;
  text: string;
  completed: boolean;
  active: boolean;
}

const quickSuggestions = [
  "我想去台北旅遊",
  "推薦一些美食景點",
  "我想規劃3天行程",
  "我的預算是中等",
  "我喜歡文化景點",
  "幫我安排住宿"
];

export function UnifiedChatPanel({ 
  sessionId, 
  onItineraryGenerated, 
  onError,
  className = ""
}: UnifiedChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationState, setConversationState] = useState<ConversationStateResponse | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [sessionStats, setSessionStats] = useState<any>(null);
  
  // 處理步驟狀態
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState<number>(0);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 滾動到底部
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 初始化處理步驟
  const initializeProcessingSteps = (message: string) => {
    let steps: ProcessingStep[] = [];
    
    // 基本步驟
    steps.push({ id: 'analyze', text: '正在分析您的需求...', completed: false, active: false });
    steps.push({ id: 'extract', text: '正在提取旅遊信息...', completed: false, active: false });
    
    // 根據訊息內容動態添加步驟
    if (message.includes('推薦') || message.includes('景點') || message.includes('地方')) {
      steps.push({ id: 'search', text: '正在搜尋相關景點...', completed: false, active: false });
      steps.push({ id: 'recommend', text: '正在生成推薦理由...', completed: false, active: false });
    }
    
    if (message.includes('住宿') || message.includes('酒店') || message.includes('飯店')) {
      steps.push({ id: 'accommodation', text: '正在搜尋住宿選項...', completed: false, active: false });
    }
    
    if (message.includes('行程') || message.includes('規劃') || message.includes('安排')) {
      steps.push({ id: 'plan', text: '正在規劃行程路線...', completed: false, active: false });
    }
    
    // 如果沒有特定關鍵字，使用默認步驟
    if (steps.length <= 2) {
      steps.push(
        { id: 'search', text: '正在搜尋相關景點...', completed: false, active: false },
        { id: 'recommend', text: '正在生成推薦理由...', completed: false, active: false }
      );
    }
    
    // 計算預估時間（每個步驟 1.2秒）
    const estimatedTimeMs = steps.length * 1200;
    
    setProcessingSteps(steps);
    setCurrentStepIndex(0);
    setEstimatedTime(estimatedTimeMs);
  };

  // 模擬處理步驟進度
  useEffect(() => {
    if (!isLoading || processingSteps.length === 0) return;

    const stepInterval = setInterval(() => {
      setProcessingSteps(prev => {
        const newSteps = [...prev];
        
        // 完成當前步驟
        if (currentStepIndex < newSteps.length) {
          newSteps[currentStepIndex] = {
            ...newSteps[currentStepIndex],
            completed: true,
            active: false
          };
        }
        
        // 激活下一個步驟
        if (currentStepIndex + 1 < newSteps.length) {
          newSteps[currentStepIndex + 1] = {
            ...newSteps[currentStepIndex + 1],
            active: true
          };
        }
        
        return newSteps;
      });
      
      setCurrentStepIndex(prev => prev + 1);
    }, 1200);

    return () => clearInterval(stepInterval);
  }, [isLoading, processingSteps.length, currentStepIndex]);

  // 初始化對話狀態
  useEffect(() => {
    if (sessionId) {
      loadConversationState();
      loadSuggestions();
    }
  }, [sessionId]);

  // 載入對話狀態
  const loadConversationState = async () => {
    try {
      const state = await getUnifiedConversationState(sessionId);
      setConversationState(state);
      
      // 載入歷史對話
      if (state.conversation_history && state.conversation_history.length > 0) {
        const historyMessages: ChatMessage[] = state.conversation_history.map((msg, index) => ({
          id: `history-${index}`,
          type: msg.role === 'user' ? 'user' : 'ai',
          content: msg.content,
          timestamp: msg.timestamp
        }));
        setMessages(historyMessages);
      }
    } catch (error) {
      console.error('Failed to load conversation state:', error);
      onError?.('無法載入對話狀態');
    }
  };

  // 載入建議
  const loadSuggestions = async () => {
    try {
      const suggestionData = await getUnifiedSuggestions(sessionId);
      setSuggestions(suggestionData.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  // 載入會話統計
  const loadSessionStats = async () => {
    try {
      const stats = await getUnifiedSessionStats(sessionId);
      setSessionStats(stats);
    } catch (error) {
      console.error('Failed to load session stats:', error);
    }
  };

  // 發送訊息
  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    // 初始化處理步驟
    initializeProcessingSteps(message);

    try {
      // 開始處理步驟動畫
      setProcessingSteps(prev => prev.map((step, index) => ({
        ...step,
        active: index === 0,
        completed: false
      })));
      setCurrentStepIndex(0);

      const response = await sendUnifiedMessage(sessionId, message);
      
      // 完成所有步驟
      setProcessingSteps(prev => prev.map(step => ({
        ...step,
        completed: true,
        active: false
      })));
      
      const aiMessage: ChatMessage = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: response.message,
        timestamp: response.timestamp,
        intent: response.intent,
        confidence: response.confidence_score,
        suggestions: response.suggestions
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // 更新建議
      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }

      // 如果行程生成完成
      if (response.is_complete && response.itinerary) {
        onItineraryGenerated?.(response.itinerary);
      }

      // 重新載入狀態和統計
      await Promise.all([
        loadConversationState(),
        loadSessionStats()
      ]);

    } catch (error: any) {
      console.error('Failed to send message:', error);
      
      // 停止處理步驟
      setProcessingSteps([]);
      
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'system',
        content: `抱歉，處理您的訊息時遇到問題：${error.message || '未知錯誤'}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
      onError?.(error.message || '發送訊息失敗');
    } finally {
      setIsLoading(false);
      setProcessingSteps([]);
      setCurrentStepIndex(0);
      setEstimatedTime(0);
    }
  };

  // 處理表單提交
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputMessage);
  };

  // 處理建議點擊
  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  // 重置對話
  const handleResetConversation = async () => {
    if (window.confirm('確定要重置對話嗎？這將清除所有對話歷史。')) {
      try {
        await resetUnifiedConversation(sessionId);
        setMessages([]);
        setConversationState(null);
        setSuggestions([]);
        setSessionStats(null);
      } catch (error: any) {
        console.error('Failed to reset conversation:', error);
        onError?.('重置對話失敗');
      }
    }
  };

  // 格式化時間
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('zh-TW', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-slate-800 rounded-lg shadow-lg ${className}`}>
      {/* 標題欄 */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            AI 旅遊助手
          </h3>
          {sessionStats && (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              完成度: {Math.round(sessionStats.completion_rate * 100)}% | 
              對話輪次: {sessionStats.turn_count} | 
              置信度: {Math.round(sessionStats.confidence_score * 100)}%
            </p>
          )}
        </div>
        <button
          onClick={handleResetConversation}
          className="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
        >
          重置對話
        </button>
      </div>

      {/* 對話區域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h4 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
              開始您的旅遊規劃對話
            </h4>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
              告訴我您的旅遊需求，我會為您量身打造完美行程
            </p>
            
            {/* 快速建議 */}
            <div className="grid grid-cols-2 gap-2 max-w-md mx-auto">
              {quickSuggestions.slice(0, 4).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs p-2 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-primary-500 text-white' 
                  : message.type === 'system'
                  ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white'
              }`}>
                <p className="text-sm">{message.content}</p>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs opacity-70">
                    {formatTime(message.timestamp)}
                  </span>
                  {message.confidence && (
                    <span className="text-xs opacity-70">
                      置信度: {Math.round(message.confidence * 100)}%
                    </span>
                  )}
                </div>
                
                {/* AI建議 */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.suggestions.slice(0, 3).map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="block w-full text-left text-xs p-2 bg-white/20 hover:bg-white/30 rounded transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isLoading && processingSteps.length > 0 && (
          <div className="flex justify-start">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 px-4 py-3 rounded-lg max-w-md">
              <div className="space-y-3">
                {/* 處理步驟列表 */}
                <div className="space-y-2">
                  {processingSteps.map((step, index) => (
                    <div key={step.id} className="flex items-center space-x-3">
                      {/* 步驟圖標 */}
                      <div className="flex-shrink-0">
                        {step.completed ? (
                          <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                        ) : step.active ? (
                          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                          </div>
                        ) : (
                          <div className="w-5 h-5 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
                        )}
                      </div>
                      
                      {/* 步驟文字 */}
                      <div className="flex-1">
                        <span className={`text-sm ${
                          step.completed 
                            ? 'text-green-600 dark:text-green-400' 
                            : step.active 
                            ? 'text-blue-600 dark:text-blue-400 font-medium' 
                            : 'text-slate-500 dark:text-slate-400'
                        }`}>
                          {step.text}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* 進度條 */}
                <div className="pt-2">
                  <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
                    <span>處理進度</span>
                    <span>{Math.round((currentStepIndex / processingSteps.length) * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-indigo-500 h-1.5 rounded-full transition-all duration-500 ease-out"
                      style={{ 
                        width: `${(currentStepIndex / processingSteps.length) * 100}%` 
                      }}
                    ></div>
                  </div>
                </div>
                
                {/* 預估時間 */}
                {estimatedTime > 0 && (
                  <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center space-x-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>預估還需 {Math.ceil((estimatedTime - (currentStepIndex * 1000)) / 1000)} 秒</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 建議區域 */}
      {suggestions.length > 0 && (
        <div className="p-4 border-t border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">建議操作：</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-xs px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-full hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 輸入區域 */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="輸入您的訊息..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? '發送中...' : '發送'}
          </button>
        </form>
      </div>
    </div>
  );
}
