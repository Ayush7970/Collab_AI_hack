import React, { useState, useEffect, useRef } from 'react';
import { FileText } from 'lucide-react';

// --- STYLES ---
const chatStyles = {
    container: { width: '100%', height: '100%', display: 'flex', flexDirection: 'column', background: '#f0f2f5' },
    header: { padding: '10px 20px', background: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 1, borderBottom: '1px solid #ddd' },
    headerTitle: { margin: 0, fontSize: '1.2rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px' },
    backButton: { background: '#e4e6eb', border: 'none', borderRadius: '20px', padding: '8px 16px', cursor: 'pointer', fontWeight: '600' },
    chatLog: { flexGrow: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column' },
    messageBubble: { maxWidth: '70%', padding: '10px 15px', borderRadius: '18px', marginBottom: '10px', lineHeight: '1.4', boxShadow: '0 1px 1px rgba(0,0,0,0.1)' },
    messageMeta: { fontSize: '0.75rem', color: '#65676b', marginTop: '5px' },
    agent1: { alignSelf: 'flex-start', background: '#e4e6eb', color: '#050505' },
    agent2: { alignSelf: 'flex-end', background: 'linear-gradient(135deg, #6a11cb, #2575fc)', color: '#fff' }
};

// --- Typewriter Hook ---
const useTypewriter = (text, speed = 5, onFinished) => {
    const [displayedText, setDisplayedText] = useState('');
    const onFinishedRef = useRef(onFinished);
    onFinishedRef.current = onFinished;

    useEffect(() => {
        if (!text) return;
        setDisplayedText('');
        let i = 0;
        const intervalId = setInterval(() => {
            setDisplayedText(text.slice(0, i + 1));
            i++;
            if (i > text.length) {
                clearInterval(intervalId);
                if (onFinishedRef.current) onFinishedRef.current();
            }
        }, speed);

        return () => clearInterval(intervalId);
    }, [text, speed]);

    return displayedText;
};

// --- Message Bubble Component ---
const MessageBubble = ({ msg, isTyping, onFinishedTyping }) => {
    const isAgent1 = msg.sender === 'video_director';
    const animatedText = useTypewriter(isTyping ? msg.message : '', 25, onFinishedTyping);

    return (
        <div style={{ ...chatStyles.messageBubble, ...(isAgent1 ? chatStyles.agent1 : chatStyles.agent2) }}>
            <div>{isTyping ? animatedText : msg.message}</div>
            <div style={{ ...chatStyles.messageMeta, color: isAgent1 ? '#65676b' : 'rgba(255,255,255,0.8)', textAlign: isAgent1 ? 'left' : 'right' }}>
                <strong>{msg.sender}</strong> - {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
        </div>
    );
};

// --- AgentChat Main Component ---
const AgentChat = ({ onBack }) => {
    const [allMessages, setAllMessages] = useState([]);
    const [displayedMessageCount, setDisplayedMessageCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const chatLogRef = useRef(null);

    useEffect(() => {
        fetch('/chat_log.txt')
            .then(response => response.text())
            .then(text => {
                const messages = text.split('\n')
                    .filter(line => line.trim())
                    .map((line, index) => {
                        const [sender, ...messageParts] = line.split(':');
                        return {
                            sender: sender.trim(),
                            message: messageParts.join(':').trim(),
                            timestamp: Date.now() + index * 1000  // fake increasing timestamps
                        };
                    });

                setAllMessages(messages);
                setTimeout(() => setDisplayedMessageCount(1), 100);
                setIsLoading(false);
            })
            .catch(error => {
                console.error("❌ Failed to fetch chat log:", error);
                setIsLoading(false);
            });
    }, []);

    useEffect(() => {
        if (chatLogRef.current) {
            chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
        }
    }, [displayedMessageCount]);

    const handleTypingFinished = () => {
        if (displayedMessageCount < allMessages.length) {
            setTimeout(() => {
                setDisplayedMessageCount(prev => prev + 1);
            }, 800);
        }
    };

    return (
        <div style={chatStyles.container}>
            <header style={chatStyles.header}>
                <h2 style={chatStyles.headerTitle}>
                    <FileText size={24} color="#6a11cb" />
                    Agent Matchmaking Log
                </h2>
                <button style={chatStyles.backButton} onClick={onBack}>← Back to Matches</button>
            </header>
            <div style={chatStyles.chatLog} ref={chatLogRef}>
                {isLoading ? (
                    <p style={{ alignSelf: 'center', color: '#65676b' }}>Loading chat...</p>
                ) : (
                    allMessages.slice(0, displayedMessageCount).map((msg, index) => (
                        <MessageBubble
                            key={index}
                            msg={msg}
                            isTyping={index === displayedMessageCount - 1}
                            onFinishedTyping={handleTypingFinished}
                        />
                    ))
                )}
            </div>
        </div>
    );
};

export default AgentChat;
