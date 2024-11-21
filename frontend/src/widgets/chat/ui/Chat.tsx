'use client';

import React, { useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import { useChat } from 'ai/react';
import { useModelSettingsContext } from '@/shared/context/model-settings-provider';
import { useImageContext } from '@/shared/context/image-base64-provider';
import { MessagesOutput } from './MessagesOutput';
import { Input } from './Input';

const saveMessageToCookies = (message) => {
    const chatHistory = JSON.parse(Cookies.get('chatHistory') || '[]');
    chatHistory.push(message);
    Cookies.set('chatHistory', JSON.stringify(chatHistory));
};

const Chat = () => {
    const { modelSettings, messageSettings } = useModelSettingsContext();
    const { imageData } = useImageContext();
    const { base64, fileType } = imageData || {};
    const [chatHistory, setChatHistory] = useState([]);

    useEffect(() => {
        const storedChatHistory = JSON.parse(Cookies.get('chatHistory') || '[]');
        setChatHistory(storedChatHistory);
    }, []);

    const chatHook = useChat({
        api: '/api/chat',
        streamProtocol: 'text',
        body: {
            model: modelSettings.model,
            temperature: modelSettings.temperature,
            max_tokens: modelSettings.max_tokens,
            top_p: modelSettings.top_p,
            top_k: modelSettings.top_k,
            system_message: messageSettings.content,
            image: base64,
            image_type: fileType,
        },
        onError: (error) => console.error(error),
        onResponse: (response) => {
            console.log(response);
            saveMessageToCookies(response);
        },
        onFinish: () => console.log('finished'),
    });

    return (
        <div className="relative flex flex-col h-[90svh] min-h-[50svh] rounded-xl bg-muted/50 p-4 lg:col-span-2">
            <MessagesOutput messages={[...chatHistory, ...chatHook.messages]} />
            <Input chatHook={chatHook} />
        </div>
    );
};

export { Chat };