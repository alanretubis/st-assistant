<template>
  <div class="app-container" :class="{ dark: isDarkMode }">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h3>Travel Assistant</h3>
        <div class="sidebar-controls">
          <button
            class="theme-toggle"
            @click="toggleTheme"
            :aria-pressed="isDarkMode"
          >
            <i v-if="!isDarkMode" class="fa-solid fa-moon"></i>
            <i v-else class="fa-solid fa-sun"></i>
          </button>
          <button
            class="collapse-toggle"
            :class="{ collapsed: sidebarCollapsed }"
            @click="sidebarCollapsed = !sidebarCollapsed"
            aria-label="Toggle sidebar"
            title="Toggle sidebar"
          >
            <i
              :class="
                sidebarCollapsed ? 'fa-solid fa-xmark' : 'fa-solid fa-bars'
              "
            ></i>
          </button>
        </div>
      </div>

      <!-- <ul v-if="!sidebarCollapsed">
        <li
          v-for="(chat, index) in chatList"
          :key="index"
          @click="loadChat(index)"
          :class="{ active: currentChatIndex === index }"
        >
          {{ chat.title }}
        </li>
      </ul> -->

      <!-- <button
        v-if="!sidebarCollapsed"
        @click="startNewChat"
        class="new-chat-btn"
      >
        + New Chat
      </button> -->
    </aside>

    <!-- Main Chat Area -->
    <main class="chat-container">
      <div
        class="chat-display"
        ref="chatDisplay"
        v-if="currentMessages.length > 0"
      >
        <div
          v-for="(msg, i) in currentMessages"
          :key="i"
          :class="['message', msg.role === 'You' ? 'user' : 'assistant']"
        >
          <strong>{{ msg.role }}:</strong>
          <div v-if="msg.role === 'Assistant'" v-html="msg.text"></div>
          <div v-else>{{ msg.text }}</div>
        </div>

        <div v-if="loading" class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <div v-else class="welcome" style="margin-bottom: auto; width: 100%">
        <h2>Welcome 👋</h2>
        <p>Ask me anything about travel planning!</p>
      </div>

      <!-- Input Bar -->
      <div class="input-area">
        <input
          v-model="question"
          @keyup.enter="send"
          placeholder="Ask your travel question..."
          :disabled="loading"
          ref="inputField"
        />
        <button @click="send" :disabled="loading">
          <span
            v-if="loading"
            style="
              display: flex;
              align-items: center;
              justify-content: center;
              width: 100%;
              height: 100%;
            "
          >
            <i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i>
          </span>
          <span
            v-else
            style="
              display: flex;
              align-items: center;
              justify-content: center;
              width: 100%;
              height: 100%;
            "
          >
            <i class="fa-solid fa-play"></i>
          </span>
        </button>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from "vue";
import axios from "axios";

interface Message {
  role: string;
  text: string;
}

interface Chat {
  title: string;
  messages: Message[];
}

export default defineComponent({
  setup() {
    const chatList = ref<Chat[]>([{ title: "Chat 1", messages: [] }]);
    const currentChatIndex = ref(0);
    const question = ref("");
    const loading = ref(false);
    const isDarkMode = ref(false);
    const sidebarCollapsed = ref(false);
    const chatDisplay = ref<HTMLElement | null>(null);
    const inputField = ref<HTMLInputElement | null>(null);

    const currentMessages = computed(
      () => chatList.value[currentChatIndex.value]?.messages || []
    );

    const scrollToBottom = () => {
      if (chatDisplay.value)
        chatDisplay.value.scrollTop = chatDisplay.value.scrollHeight;
    };

    watch(currentMessages, () => setTimeout(scrollToBottom, 50));

    const formatAssistantText = (text: string) => {
      let html = text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");
      return html;
    };

    const send = async () => {
      const q = question.value.trim();
      if (!q) return;

      // Ensure there is a chat at the current index; create one if missing
      let currentChat = chatList.value[currentChatIndex.value];
      if (!currentChat) {
        const newChat: Chat = {
          title: `Chat ${chatList.value.length + 1}`,
          messages: [{ role: "You", text: q }],
        };
        chatList.value.push(newChat);
        currentChatIndex.value = chatList.value.length - 1;
        currentChat = chatList.value[currentChatIndex.value];
      } else {
        currentChat.messages.push({
          role: "You",
          text: q,
        });
      }

      question.value = "";
      loading.value = true;

      try {
        const apiBase =
          (import.meta.env.VITE_API_BASE as string) || "http://0.0.0.0:8000";
        const url = apiBase.replace(/\/+$/, "") + "/chat";
        const res = await axios.post(url, {
          question: q,
        });
        // read the current chat fresh from the reactive array (non-undefined)
        const currentChat = chatList.value[currentChatIndex.value];

        if (currentChat) {
          currentChat.messages.push({
            role: "Assistant",
            text: formatAssistantText(res.data.answer),
          });
        }
      } catch {
        const currentChat = chatList.value[currentChatIndex.value];
        if (currentChat) {
          currentChat.messages.push({
            role: "Assistant",
            text: "⚠️ Error: Unable to get a response.",
          });
        }
      } finally {
        loading.value = false;
        scrollToBottom();
        inputField.value?.focus();
      }
    };

    const startNewChat = () => {
      chatList.value.push({
        title: `Chat ${chatList.value.length + 1}`,
        messages: [],
      });
      currentChatIndex.value = chatList.value.length - 1;
    };

    const loadChat = (index: number) => (currentChatIndex.value = index);
    const toggleTheme = () => (isDarkMode.value = !isDarkMode.value);

    const loadHistory = async () => {
      try {
        const apiBase =
          (import.meta.env.VITE_API_BASE as string) || "http://0.0.0.0:8000";
        const url = apiBase.replace(/\/+$/, "") + "/history";
        const res = await axios.get(url);
        const chats = res.data?.chats || [];
        if (Array.isArray(chats) && chats.length > 0) {
          // replace local chatList with history (preserve ordering: most recent first -> put oldest first)
          // If you prefer newest-first keep as-is.
          chatList.value = chats
            .slice()
            .reverse() // show oldest first in the list (optional)
            .map((c: any, idx: number) => ({
              title: c.title || `Chat ${idx + 1}`,
              messages: c.messages || [],
            }));
          currentChatIndex.value = 0;
        }
      } catch (e) {
        console.warn("Failed to load history:", e);
      }
    };

    onMounted(() => {
      inputField.value?.focus();
      void loadHistory();
    });

    return {
      chatList,
      currentChatIndex,
      currentMessages,
      question,
      loading,
      chatDisplay,
      inputField,
      send,
      startNewChat,
      loadChat,
      isDarkMode,
      toggleTheme,
      sidebarCollapsed,
    };
  },
});
</script>

<style scoped>
/* Global container */
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  max-width: 100vw;
  overflow-x: hidden;
  /* changed: prevent page from scrolling */
  overflow-y: hidden;
  background: #f9fafb;
  color: #1e293b;
  font-family: "Inter", sans-serif;
  transition: all 0.3s;
}

.app-container.dark {
  background: #0f172a;
  color: #f1f5f9;
}

/* Sidebar */
.sidebar {
  max-height: 100vh;
  width: 260px;
  background: #1e293b;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  padding: 15px;
  transition: all 0.3s ease;
  position: relative; /* changed: allow absolutely positioned controls inside */
}

.sidebar.collapsed {
  width: 80px;
}

/* ensure header reserves space for absolute controls */
.sidebar-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-right: 56px; /* changed: leave room for the controls */
}

/* move controls inside sidebar (always visible) */
.sidebar-controls {
  position: absolute; /* changed: keep inside sidebar regardless of collapse */
  top: 12px;
  right: 12px;
  display: flex;
  gap: 5px;
  z-index: 5;
}

/* hide the title when collapsed to save space */
.sidebar.collapsed .sidebar-header h3 {
  display: none;
}

.theme-toggle,
.collapse-toggle {
  background: transparent;
  border: none;
  color: #f8fafc;
  font-size: 18px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
}

/* remove old bar-based hamburger rules and use icon sizing instead */
.collapse-toggle i,
.theme-toggle i {
  font-size: 18px;
}

/* optional small tweak so the collapse icon sits nicely when collapsed */
.sidebar.collapsed .sidebar-controls .collapse-toggle {
  /* keep the control visible and not overflowing */
  padding: 6px;
}

/* Ensure color adapts to dark/light theme */
.app-container.dark .collapse-toggle,
.app-container.dark .theme-toggle {
  color: #f8fafc;
}

.theme-toggle,
.collapse-toggle {
  color: inherit;
}

.sidebar ul {
  flex: 1;
  margin-top: 15px;
  overflow-y: auto;
}

.sidebar li {
  padding: 10px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.2s;
}

.sidebar li.active {
  background: #22c55e;
}

.sidebar li:hover {
  background: rgba(255, 255, 255, 0.1);
}

.new-chat-btn {
  background: #22c55e;
  border: none;
  color: white;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.new-chat-btn:hover {
  background: #16a34a;
  transform: scale(1.05);
}

/* Chat area */
.chat-container {
  flex: 1;
  max-height: 100%;
  /* changed: make this a column flex container and allow children to control scrolling */
  display: flex;
  flex-direction: column;
  min-height: 0; /* crucial to allow .chat-display to overflow correctly */
  justify-content: flex-end;
  padding: 20px;
  /* removed overflow-y: scroll so only .chat-display scrolls */
}

.chat-display {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 70%;
  padding: 12px 18px;
  border-radius: 18px;
  line-height: 1.5;
  animation: fadeIn 0.3s ease;
}

.message.user {
  background: #22c55e;
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 5px;
}

.message.assistant {
  background: #e2e8f0;
  align-self: flex-start;
  border-bottom-left-radius: 5px;
}

.app-container.dark .message.assistant {
  background: #1e293b;
  color: #f8fafc;
}

.input-area {
  display: flex;
  gap: 10px;
  background: white;
  border-radius: 30px;
  padding: 10px 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-container.dark .input-area {
  background: #1e293b;
}

.input-area input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  color: inherit;
}

.input-area button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #22c55e;
  border: none;
  border-radius: 50%;
  width: 45px;
  height: 45px;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: 0.2s;
}

.input-area button:hover {
  background: #16a34a;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 5px;
  align-self: flex-start;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #94a3b8;
  border-radius: 50%;
  animation: bounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  .spinner {
    display: inline-block;
    box-sizing: border-box;
    width: 20px;
    height: 20px;
    border: 3px solid #fff;
    border-top: 3px solid #22c55e;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    vertical-align: middle;
  }
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Responsive */
@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    height: 100%;
    z-index: 10;
    left: 0;
    top: 0;
    transform: translateX(-100%);
  }

  .sidebar.collapsed {
    transform: translateX(0);
  }

  .chat-container {
    padding: 10px;
  }
}
</style>
