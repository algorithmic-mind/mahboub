// ai.js - هوش مصنوعی محبوب

class AIChat {
    constructor() {
        this.messages = [];
        this.recognition = null;
        this.isRecording = false;
        this.init();
    }

    init() {
        this.initElements();
        this.initEventListeners();
        this.initSpeechRecognition();
        this.adjustTextareaHeight();
    }

    initElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.emojiBtn = document.getElementById('emojiBtn');
        this.emojiPicker = document.getElementById('emojiPicker');
        this.emojiClose = document.getElementById('emojiClose');
        this.voiceRecording = document.getElementById('voiceRecording');
        this.recordingStop = document.getElementById('recordingStop');
        this.suggestedQuestions = document.getElementById('suggestedQuestions');
    }

    initEventListeners() {
        // Send message
        this.sendBtn?.addEventListener('click', () => this.sendMessage());
        
        // Enter to send
        this.messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Enable/disable send button
        this.messageInput?.addEventListener('input', (e) => {
            this.sendBtn.disabled = !e.target.value.trim();
            this.adjustTextareaHeight();
        });

        // Emoji picker
        this.emojiBtn?.addEventListener('click', () => this.toggleEmojiPicker());
        this.emojiClose?.addEventListener('click', () => this.closeEmojiPicker());

        // Emoji selection
        document.querySelectorAll('.emoji-item').forEach(emoji => {
            emoji.addEventListener('click', (e) => {
                this.insertEmoji(e.target.textContent);
            });
        });

        // Voice recording
        this.voiceBtn?.addEventListener('click', () => this.toggleVoiceRecording());
        this.recordingStop?.addEventListener('click', () => this.stopVoiceRecording());

        // Suggested questions
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const text = e.currentTarget.textContent.trim();
                this.messageInput.value = text;
                this.sendBtn.disabled = false;
                this.suggestedQuestions.style.display = 'none';
            });
        });
    }

    initSpeechRecognition() {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported');
            this.voiceBtn.style.display = 'none';
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'fa-IR'; // Persian
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            this.sendBtn.disabled = false;
            this.stopVoiceRecording();
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopVoiceRecording();
            
            if (event.error === 'no-speech') {
                this.showNotification('صدایی دریافت نشد. دوباره تلاش کنید.');
            } else if (event.error === 'not-allowed') {
                this.showNotification('دسترسی به میکروفون رد شد.');
            } else {
                this.showNotification('خطا در تشخیص صدا');
            }
        };

        this.recognition.onend = () => {
            this.isRecording = false;
            this.voiceRecording.classList.remove('active');
            this.voiceBtn.classList.remove('recording');
        };
    }

    adjustTextareaHeight() {
        if (!this.messageInput) return;
        
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    toggleEmojiPicker() {
        this.emojiPicker?.classList.toggle('active');
    }

    closeEmojiPicker() {
        this.emojiPicker?.classList.remove('active');
    }

    insertEmoji(emoji) {
        const cursorPos = this.messageInput.selectionStart;
        const textBefore = this.messageInput.value.substring(0, cursorPos);
        const textAfter = this.messageInput.value.substring(cursorPos);
        
        this.messageInput.value = textBefore + emoji + textAfter;
        this.messageInput.focus();
        
        // Set cursor position after emoji
        this.messageInput.selectionStart = cursorPos + emoji.length;
        this.messageInput.selectionEnd = cursorPos + emoji.length;
        
        this.sendBtn.disabled = false;
        this.closeEmojiPicker();
    }

    toggleVoiceRecording() {
        if (this.isRecording) {
            this.stopVoiceRecording();
        } else {
            this.startVoiceRecording();
        }
    }

    startVoiceRecording() {
        if (!this.recognition) {
            this.showNotification('تشخیص صدا در مرورگر شما پشتیبانی نمی‌شود');
            return;
        }

        try {
            this.recognition.start();
            this.isRecording = true;
            this.voiceRecording.classList.add('active');
            this.voiceBtn.classList.add('recording');
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showNotification('خطا در شروع ضبط صدا');
        }
    }

    stopVoiceRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
        this.isRecording = false;
        this.voiceRecording.classList.remove('active');
        this.voiceBtn.classList.remove('recording');
    }

    async sendMessage() {
        const text = this.messageInput?.value.trim();
        if (!text) return;

        // Hide suggestions
        this.suggestedQuestions.style.display = 'none';

        // Add user message
        this.addMessage(text, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.sendBtn.disabled = true;
        this.adjustTextareaHeight();

        // Scroll to bottom
        this.scrollToBottom();

        // Show typing indicator
        this.showTypingIndicator();

        // Simulate AI response (در حالت واقعی باید به API متصل شود)
        setTimeout(() => {
            this.hideTypingIndicator();
            this.addAIResponse(text);
            this.scrollToBottom();
        }, 1500 + Math.random() * 1000);
    }

    addMessage(text, type = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        const p = document.createElement('p');
        p.textContent = text;
        bubble.appendChild(p);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        
        this.chatMessages?.appendChild(messageDiv);
        this.messages.push({ text, type });
    }

    addAIResponse(userMessage) {
        // پاسخ‌های نمونه (در حالت واقعی از API دریافت می‌شود)
        const responses = {
            'تفسیر': 'برای تفسیر آیه مورد نظر، لطفاً آیه را بنویسید تا تفسیر کاملی از منابع معتبر برای شما ارائه دهم.',
            'احادیث': 'در زمینه احادیث، می‌توانم به شما کمک کنم. لطفاً موضوع خاصی را مشخص کنید تا احادیث مرتبط را جستجو کنم.',
            'نماز': 'نماز ستون دین است. کدام بخش از احکام نماز را می‌خواهید بدانید؟ (واجبات، مستحبات، مبطلات، شرایط)',
            'default': 'سوال جالبی است! اجازه دهید در منابع محبوب جستجو کنم و پاسخ دقیقی به شما بدهم. 📚'
        };

        let response = responses.default;
        
        // Simple keyword matching
        if (userMessage.includes('تفسیر') || userMessage.includes('آیه')) {
            response = responses['تفسیر'];
        } else if (userMessage.includes('حدیث') || userMessage.includes('روایت')) {
            response = responses['احادیث'];
        } else if (userMessage.includes('نماز')) {
            response = responses['نماز'];
        }

        this.addMessage(response, 'ai');
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message ai-message';
        indicator.id = 'typingIndicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = `
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;
        
        indicator.appendChild(avatar);
        indicator.appendChild(bubble);
        
        this.chatMessages?.appendChild(indicator);
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator?.remove();
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages?.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--card-bg);
            color: var(--text-primary);
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: var(--shadow-xl);
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            border: 1px solid var(--gray-200);
            animation: slideDown 0.3s ease;
            max-width: 90%;
            text-align: center;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }

    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translate(-50%, 0);
        }
        to {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    window.aiChat = new AIChat();
});