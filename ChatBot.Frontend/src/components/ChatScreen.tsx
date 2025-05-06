import React, { useState, useRef, useEffect } from 'react';
import './ChatScreen.css';
import { apiService, SendMessageRequest, MessageStreamEvent } from '../services/api';
import { useUser } from './UserContext';
import { useChats } from './ChatsContext';
import { useMessages } from './MessagesContext';
import { useTelegram } from '../hooks/useTelegram';

const features = [
  { label: 'Улучшить промпт', icon: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <rect x="10.2" y="10.5" width="1.2" height="6" rx="0.6" transform="rotate(-35 10.2 10.5)" fill="#bfcfff"/>
      <rect x="8.5" y="6.5" width="5" height="2" rx="1" fill="#fff" stroke="#bfcfff" strokeWidth="1"/>
      <rect x="12.5" y="6.5" width="1.2" height="2" rx="0.6" fill="#bfcfff"/>
      <g>
        <path d="M15.5 5.5L15.8 6.1L16.5 6.3L15.8 6.5L15.5 7.1L15.2 6.5L14.5 6.3L15.2 6.1L15.5 5.5Z" stroke="#bfcfff" strokeWidth="0.5" fill="none"/>
        <path d="M13.2 4.2L13.4 4.6L13.9 4.7L13.4 4.9L13.2 5.3L13 4.9L12.5 4.7L13 4.6L13.2 4.2Z" stroke="#bfcfff" strokeWidth="0.4" fill="none"/>
        <path d="M16.5 8.2L16.7 8.5L17.1 8.6L16.7 8.7L16.5 9L16.3 8.7L15.9 8.6L16.3 8.5L16.5 8.2Z" stroke="#bfcfff" strokeWidth="0.3" fill="none"/>
      </g>
    </svg>
  ) },
  { label: 'Стиль', icon: (
    <div style={{position: 'relative', width: 20, height: 20}}>
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{position: 'absolute', left: 0, top: 0}}><circle cx="10" cy="10" r="8" fill="#bfcfff" opacity="0.2"/><path d="M7 10C7 11.5 8.5 13 10 13C11.5 13 13 11.5 13 10C13 8.5 11.5 7 10 7C8.5 7 7 8.5 7 10Z" fill="#bfcfff"/></svg>
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{position: 'absolute', left: 4, top: 4}}><circle cx="10" cy="10" r="8" fill="#bfcfff" opacity="0.2"/><path d="M7 10C7 11.5 8.5 13 10 13C11.5 13 13 11.5 13 10C13 8.5 11.5 7 10 7C8.5 7 7 8.5 7 10Z" fill="#bfcfff"/></svg>
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{position: 'absolute', left: 8, top: 8}}><circle cx="10" cy="10" r="8" fill="#bfcfff"/><path d="M7 10C7 11.5 8.5 13 10 13C11.5 13 13 11.5 13 10C13 8.5 11.5 7 10 7C8.5 7 7 8.5 7 10Z" fill="#181a20"/></svg>
    </div>
  ) },
  { label: 'Отчёт', icon: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="4" y="4" width="12" height="16" rx="1.5" stroke="#bfcfff" strokeWidth="1.5"/><path d="M7 8h6M7 11h6M7 14h3" stroke="#bfcfff" strokeWidth="1.5" strokeLinecap="round"/></svg>
  ) },
];

const attachments = [
  { label: 'Файлы', icon: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M7 10.5L13 4.5C14.1046 3.39543 15.8954 3.39543 17 4.5C18.1046 5.60457 18.1046 7.39543 17 8.5L9 16.5C7.34315 18.1569 4.65685 18.1569 3 16.5C1.34315 14.8431 1.34315 12.1569 3 10.5L11 2.5" stroke="#bfcfff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
  ) },
  { label: 'Фотография', icon: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3" y="5.5" width="14" height="9" rx="2" stroke="#bfcfff" strokeWidth="1.5"/><circle cx="7" cy="10" r="1.3" stroke="#bfcfff" strokeWidth="1.2"/><path d="M10 14L13.5 10.5L17 14" stroke="#bfcfff" strokeWidth="1.2" strokeLinecap="round"/><circle cx="15.2" cy="8.2" r="0.7" fill="#bfcfff"/></svg>
  ) },
  { label: 'Камера', icon: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="4" y="7" width="12" height="7" rx="2" stroke="#bfcfff" strokeWidth="1.7"/><circle cx="10" cy="10.5" r="2.3" stroke="#bfcfff" strokeWidth="1.5"/><rect x="8.2" y="4.2" width="3.6" height="2.2" rx="1.1" stroke="#bfcfff" strokeWidth="1.2" fill="none"/></svg>
  ) },
];

const PlusIcon = () => (
  <svg width="22" height="22" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="9" fill="none"/>
    <path d="M10 5V15M5 10H15" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/>
  </svg>
);

const Sidebar: React.FC<{
  open: boolean;
  onClose: () => void;
  projects: string[];
  chats: string[];
  onAddProject: () => void;
  onSelectChat: (idx: number) => void;
  selectedChat: number | null;
}> = ({ open, onClose, projects, chats, onAddProject, onSelectChat, selectedChat }) => {
  const [search, setSearch] = useState('');
  return (
    <div className={`sidebar-drawer${open ? ' sidebar-drawer--open' : ''}`}> 
      <div className="sidebar-search-row">
        <input
          type="text"
          className="sidebar-search-input"
          placeholder="Поиск..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button className="sidebar-close" onClick={onClose} title="Закрыть">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M6 6l8 8M14 6l-8 8" stroke="#bfcfff" strokeWidth="2.2" strokeLinecap="round"/>
          </svg>
        </button>
      </div>
      <div className="sidebar-header" style={{marginTop: 0}}>
        <span style={{fontWeight: 700, fontSize: 18}}>Проекты</span>
        <button className="sidebar-add-btn" onClick={onAddProject}><PlusIcon /></button>
      </div>
      <div className="sidebar-section">
        {projects.map((p) => (
          <div key={p} className="sidebar-project">{p}</div>
        ))}
      </div>
      <div className="sidebar-section" style={{marginTop: 24}}>
        <div style={{fontWeight: 700, fontSize: 16, margin: '8px 0'}}>Чаты</div>
        {chats.map((c, i) => (
          <div
            key={c}
            className={`sidebar-chat${selectedChat === i ? ' sidebar-chat--active' : ''}`}
            onClick={() => onSelectChat(i)}
          >
            {c}
          </div>
        ))}
      </div>
    </div>
  );
};

const ProjectModal: React.FC<{ open: boolean; onClose: () => void; onCreate: (name: string) => void; }> = ({ open, onClose, onCreate }) => {
  const [name, setName] = useState('');
  if (!open) return null;
  return (
    <div className="modal-backdrop">
      <div className="modal-window">
        <div style={{fontWeight: 700, fontSize: 18, marginBottom: 16}}>Создать проект</div>
        <input
          className="modal-input"
          placeholder="Название проекта"
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <div className="modal-actions">
          <button onClick={onClose} className="modal-btn modal-btn--cancel">Отмена</button>
          <button onClick={() => { if (name.trim()) { onCreate(name.trim()); setName(''); }}} className="modal-btn modal-btn--create" disabled={!name.trim()}>Создать</button>
        </div>
      </div>
    </div>
  );
};

// Хук для определения мобильного Telegram Mini App
function useIsMobileWebApp() {
  const [isMobileApp, setIsMobileApp] = React.useState(false);
  React.useEffect(() => {
    const isMobile = /Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i.test(navigator.userAgent);
    const isTelegramWebApp = typeof window !== 'undefined' && (window as any).Telegram?.WebApp;
    setIsMobileApp(isMobile && !!isTelegramWebApp);
  }, []);
  return isMobileApp;
}

export const ChatScreen: React.FC = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);
  const [showClipPanel, setShowClipPanel] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [projectModalOpen, setProjectModalOpen] = useState(false);
  const [projects, setProjects] = useState<string[]>(['Мой проект']);
  const [selectedChat, setSelectedChat] = useState<number | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const featuresPanelRef = useRef<HTMLDivElement>(null);
  const clipPanelRef = useRef<HTMLDivElement | null>(null);
  const [modelMenuOpen, setModelMenuOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState({
    name: 'ChatLUX',
    desc: 'Our standard model for most tasks',
  });
  const modelMenuRef = useRef<HTMLDivElement>(null);
  const models = [
    { name: 'ChatLUX', desc: 'Our standard model for most tasks' },
    { name: 'GPT-4o', desc: 'OpenAI latest model' },
    { name: 'Gemma3', desc: 'Gemini latest model' },
  ];
  const isMobileApp = useIsMobileWebApp();
  const [wavesEnabled, setWavesEnabled] = useState(true);
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const { user, login } = useUser();
  const { chats: chatsContext, loadChats, selectChat, activeChatId } = useChats();
  const { messages, loadMessages, sendMessage } = useMessages();
  const { tg } = useTelegram();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  useEffect(() => {
    if (!showFeatures && !showClipPanel) return;
    const handleClick = (e: MouseEvent) => {
      if (showFeatures && featuresPanelRef.current && !featuresPanelRef.current.contains(e.target as Node)) {
        setShowFeatures(false);
      }
      if (showClipPanel && clipPanelRef.current && !clipPanelRef.current.contains(e.target as Node)) {
        setShowClipPanel(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showFeatures, showClipPanel]);

  useEffect(() => {
    if (!modelMenuOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (modelMenuRef.current && !modelMenuRef.current.contains(e.target as Node)) {
        setModelMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [modelMenuOpen]);

  useEffect(() => {
    // Получаем init_data из Telegram WebApp и логинимся
    const initData = tg?.initData;
    if (initData) {
      login(initData).then(() => {
        loadChats();
      });
    }
  }, [tg]);

  useEffect(() => {
    // Загружаем сообщения при выборе чата
    if (activeChatId) {
      loadMessages();
    }
  }, [activeChatId]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setInput('');
    setLoading(true);
    try {
      await sendMessage(input);
    } finally {
      setLoading(false);
    }
  };

  const sendActive = !!input.trim();
  const arrowColor = sendActive ? '#181a20' : '#bfcfff';

  return (
    <div className={`chat-root ${isMobileApp ? 'mobile-app' : 'desktop-app'}`}>
      {wavesEnabled && <div className="background-gradient" aria-hidden="true"></div>}
      {wavesEnabled && (
        <div className="background-waves" aria-hidden="true">
          <svg width="100%" height="100%" viewBox="0 0 1440 900" preserveAspectRatio="none" style={{position: 'absolute', top: 0, left: 0, width: '120vw', height: '120vh', transform: 'translate(-10vw, -8vh) rotate(-18deg)'}}>
            <defs>
              <linearGradient id="waveGradient1" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#232bff" stopOpacity="0.18"/>
                <stop offset="100%" stopColor="#646cff" stopOpacity="0.10"/>
              </linearGradient>
              <linearGradient id="waveGradient2" x1="0" y1="1" x2="1" y2="0">
                <stop offset="0%" stopColor="#bfcfff" stopOpacity="0.08"/>
                <stop offset="100%" stopColor="#232bff" stopOpacity="0.06"/>
              </linearGradient>
            </defs>
            <path className="wave1" d="M0,700 Q360,600 720,700 T1440,700 V900 H0Z" fill="url(#waveGradient1)"/>
            <path className="wave2" d="M0,800 Q480,750 960,800 T1440,800 V900 H0Z" fill="url(#waveGradient2)"/>
          </svg>
        </div>
      )}
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        projects={projects}
        chats={chatsContext.map(c => c.title)}
        onAddProject={() => setProjectModalOpen(true)}
        onSelectChat={idx => { selectChat(chatsContext[idx]?.id); setInput(''); }}
        selectedChat={chatsContext.findIndex(c => c.id === activeChatId)}
      />
      <ProjectModal
        open={projectModalOpen}
        onClose={() => setProjectModalOpen(false)}
        onCreate={name => { setProjects(prev => [...prev, name]); setProjectModalOpen(false); }}
      />
      {/* Верхняя панель */}
      <div className="chat-topbar">
        <button className="chat-topbar__icon" title="Меню" onClick={() => setSidebarOpen(v => !v)}>
          <span role="img" aria-label="menu">☰</span>
        </button>
        <div style={{flex: 1, display: 'flex', justifyContent: 'center', position: 'relative'}}>
          <button
            className="chat-topbar__title"
            style={{background: 'none', border: 'none', color: '#e6eaff', fontWeight: 600, fontSize: '1.2em', cursor: 'pointer', padding: 0, display: 'flex', alignItems: 'center', gap: 8}}
            onClick={() => setModelMenuOpen(v => !v)}
          >
            {selectedModel.name}
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" style={{marginLeft: 4, opacity: 0.7}}>
              <path d="M6 8l4 4 4-4" stroke="#bfcfff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          {modelMenuOpen && (
            <div
              className="model-menu"
              ref={modelMenuRef}
              style={{
                position: 'absolute',
                top: 'calc(100% + 8px)',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(30,32,38,0.98)',
                borderRadius: 18,
                boxShadow: '0 6px 32px 0 #000a',
                padding: '8px 0',
                minWidth: 260,
                zIndex: 1002,
                display: 'flex',
                flexDirection: 'column',
                gap: 0,
              }}
            >
              {models.map((m) => (
                <button
                  key={m.name}
                  className="model-menu__item"
                  style={{
                    background: selectedModel.name === m.name ? '#23242a' : 'none',
                    color: '#e6eaff',
                    textAlign: 'left',
                    padding: '14px 22px 10px 22px',
                    fontSize: 17,
                    fontWeight: 600,
                    cursor: 'pointer',
                    borderRadius: 12,
                    marginBottom: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                  onClick={() => { setSelectedModel(m); setModelMenuOpen(false); }}
                >
                  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 2}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                      <span>{m.name}</span>
                      {m.name === 'Gemma3' && (
                        <span style={{color: '#ffe066', fontSize: 16, fontWeight: 500, marginLeft: 4}}>⚠️</span>
                      )}
                      {m.name === 'ChatLUX' && (
                        <span style={{color: '#bfcfff', fontSize: 13, fontWeight: 500, marginLeft: 6, background: '#23242a', borderRadius: 8, padding: '2px 8px'}}>RESEARCH PREVIEW</span>
                      )}
                    </div>
                    <div style={{fontSize: 14, color: '#bfcfff', fontWeight: 400, marginTop: 2}}>{m.desc}</div>
                  </div>
                  {selectedModel.name === m.name && (
                    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" style={{marginLeft: 12}}>
                      <path d="M6 10.5l3 3 5-5.5" stroke="#bfcfff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
        <div style={{position: 'relative'}}>
          <button className="chat-topbar__icon" title="Профиль/настройки" onClick={() => setShowSettingsMenu(v => !v)}>
            <span role="img" aria-label="profile">⋮</span>
          </button>
          {showSettingsMenu && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 8px)',
              right: 0,
              background: 'rgba(30,32,38,0.98)',
              borderRadius: 14,
              boxShadow: '0 6px 24px 0 #000a',
              padding: '8px 0',
              minWidth: 180,
              zIndex: 2005,
              display: 'flex',
              flexDirection: 'column',
              gap: 0,
            }}>
              <button
                style={{
                  background: 'none',
                  color: '#e6eaff',
                  textAlign: 'left',
                  padding: '12px 22px',
                  fontSize: 16,
                  fontWeight: 500,
                  cursor: 'pointer',
                  border: 'none',
                  borderRadius: 10,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
                onClick={() => setWavesEnabled(v => !v)}
              >
                <span style={{flex: 1}}>Включить анимацию</span>
                <input type="checkbox" checked={wavesEnabled} readOnly style={{accentColor: '#646cff', width: 18, height: 18}} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Центральная часть */}
      <div className="chat-center">
        <h2 className="chat-center__title">Чем я могу помочь?</h2>
        <div className="chat-quick-actions">
          <button className="chat-quick-action">
            <span className="chat-quick-action__icon">🖼️</span>Создать изображение
          </button>
          <button className="chat-quick-action">
            <span className="chat-quick-action__icon">💡</span>Придумай
          </button>
          <button className="chat-quick-action" disabled>
            Больше
          </button>
        </div>
      </div>

      {/* Нижняя панель */}
      <div className="chat-bottom-bar">
        <div className="chat-bottom-bar__input-wrap">
          <textarea
            ref={textareaRef}
            className="chat-bottom-bar__textarea"
            placeholder="Спросите что-нибудь"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
            disabled={loading}
            rows={1}
            maxLength={1000}
            style={{resize: 'none'}}
          />
          <button
            className={`chat-bottom-bar__send${sendActive ? ' chat-bottom-bar__send--active' : ''}`}
            onClick={handleSend}
            disabled={loading || !sendActive}
            aria-label="Отправить"
            style={{padding: 0}}
          >
            <svg className="send-arrow" viewBox="0 0 20 20" width={22} height={22} style={{display:'block'}}>
              <path d="M10 16V4M10 4L5 9M10 4l5 5" stroke={arrowColor} strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div className="chat-bottom-bar__actions-popover">
            <button className="quick-action-btn" title="Добавить" onClick={() => setShowClipPanel(v => !v)}>
              <span className="quick-action-btn__icon"><PlusIcon /></span>
            </button>
            {showClipPanel && (
              <div className="features-panel" ref={clipPanelRef} style={{left: 0, bottom: 44}}>
                {attachments.map(a => (
                  <button key={a.label} className="feature-btn">
                    <span style={{marginRight: 10, display: 'inline-flex', alignItems: 'center'}}>{a.icon}</span>
                    {a.label}
                  </button>
                ))}
              </div>
            )}
            <button className="quick-action-btn" title="Инструменты" onClick={() => setShowFeatures(v => !v)}>
              <span className="quick-action-btn__icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="4" y="10" width="12" height="5" rx="1.5" stroke="#bfcfff" strokeWidth="1.7" fill="none"/>
                  <rect x="8.5" y="13" width="3" height="1.1" rx="0.55" fill="#bfcfff"/>
                  <rect x="12.7" y="6.2" width="1" height="5" rx="0.5" fill="#ffe066" stroke="#bfcfff" strokeWidth="0.5"/>
                  <rect x="12.5" y="5.2" width="1.4" height="1.2" rx="0.5" fill="#ffa600" stroke="#bfcfff" strokeWidth="0.3"/>
                  <rect x="13.05" y="4.3" width="0.3" height="1.1" rx="0.15" fill="#bfcfff"/>
                </svg>
              </span>
            </button>
            {showFeatures && (
              <div className="features-panel" ref={featuresPanelRef}>
                {features.map(f => (
                  <button key={f.label} className="feature-btn">
                    <span style={{marginRight: 10, display: 'inline-flex', alignItems: 'center'}}>{f.icon}</span>
                    {f.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 