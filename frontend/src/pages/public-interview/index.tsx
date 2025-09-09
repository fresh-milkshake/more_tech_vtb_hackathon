import { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Mic, Send } from 'lucide-react';

// Типы для Web Speech API
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;

  start: () => void;
  stop: () => void;

  onresult: (event: SpeechRecognitionEvent) => void;
  onend: () => void;
}

const questions = [
  'Привет! Расскажите немного о себе.',
  'Почему вам интересна эта вакансия?',
  'Какими достижениями вы особенно гордитесь?',
  'Как вы решаете сложные задачи?',
  'Есть ли у вас вопросы к компании?',
];

export function PublicInterviewPage() {
  const [step, setStep] = useState(0);
  const [messages, setMessages] = useState<
    { role: 'bot' | 'user'; text: string }[]
  >([{ role: 'bot', text: 'Добро пожаловать на тестовое интервью! 🚀' }]);
  const [input, setInput] = useState('');
  const [listening, setListening] = useState(false);
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    const SpeechRecognitionConstructor =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionConstructor) {
      console.warn('Speech Recognition not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognitionConstructor();
    recognition.lang = 'ru-RU';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev + ' ' + transcript);
      setListening(false);
    };

    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', text: input }]);
    setInput('');
    setTyping(true);

    setTimeout(() => {
      if (step < questions.length) {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', text: questions[step] },
        ]);
        setStep(step + 1);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: 'bot', text: 'Спасибо за участие! ✅ Интервью завершено.' },
        ]);
      }
      setTyping(false);
    }, 800);
  };

  const handleMic = () => {
    if (!recognitionRef.current) return;
    if (!listening) {
      recognitionRef.current.start();
      setListening(true);
    } else {
      recognitionRef.current.stop();
      setListening(false);
    }
  };

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, typing]);

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-white border-r p-4 flex flex-col">
        <h2 className="text-lg font-semibold mb-4">Прогресс интервью</h2>
        <div className="flex-1 space-y-2">
          {questions.map((q, idx) => (
            <div
              key={idx}
              className={`p-2 rounded ${
                idx === step
                  ? 'bg-blue-500 text-white font-semibold'
                  : idx < step
                  ? 'bg-gray-200'
                  : 'bg-gray-100'
              }`}
            >
              {q}
            </div>
          ))}
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        <Card className="flex-1 flex flex-col shadow-none rounded-none">
          <CardContent
            ref={scrollRef}
            className="flex-1 overflow-y-auto space-y-4 p-6 bg-gray-100"
          >
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 ${
                  m.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {m.role === 'bot' && (
                  <>
                    <Avatar className="w-10 h-10">
                      <AvatarImage src="/bot-avatar.png" alt="Bot" />
                      <AvatarFallback>🤖</AvatarFallback>
                    </Avatar>
                    <div className="bg-gray-200 p-3 rounded-lg max-w-[70%] break-words">
                      {m.text}
                    </div>
                  </>
                )}
                {m.role === 'user' && (
                  <>
                    <div className="bg-blue-500 text-white p-3 rounded-lg max-w-[70%] break-words">
                      {m.text}
                    </div>
                    <Avatar className="w-10 h-10">
                      <AvatarFallback>🙋‍♂️</AvatarFallback>
                    </Avatar>
                  </>
                )}
              </div>
            ))}

            {/* Индикатор печатает */}
            {typing && (
              <div className="flex items-center gap-3">
                <Avatar className="w-10 h-10">
                  <AvatarFallback>🤖</AvatarFallback>
                </Avatar>
                <div className="bg-gray-200 p-2 rounded-lg max-w-[30%]">
                  <span className="animate-pulse">Бот печатает...</span>
                </div>
              </div>
            )}
          </CardContent>

          {/* Поле ввода */}
          <div className="flex gap-2 p-4 border-t bg-white">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Введите ваш ответ..."
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <Button
              onClick={handleMic}
              variant={listening ? 'destructive' : 'default'}
            >
              <Mic className="w-5 h-5" />
            </Button>
            <Button onClick={handleSend}>
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </Card>
      </main>
    </div>
  );
}
