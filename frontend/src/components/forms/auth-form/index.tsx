import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { toast } from 'sonner';
import { handleApiError } from '@/services/api';
import { useAuthStore } from '@/store/auth-store';
import logo from '@/assets/hr-avatar-logo.svg';
import { useAuthorization, useRegistration } from '@/services/mutations/auth';
import {
  loginSchema,
  registerSchema,
  type LoginFormData,
  type RegisterFormData,
} from './auth-form.validation';
import { cn } from '@/lib/utils';
import styles from './auth-form.module.scss';
import { AxiosError } from 'axios';

const AuthForm: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const { logout, isLoggedIn } = useAuthStore();

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const authorizationMutation = useAuthorization();
  const registrationMutation = useRegistration();

  const onLoginSubmit = (data: LoginFormData) => {
    authorizationMutation.mutate(
      {
        grant_type: 'password',
        username: data.email,
        password: data.password,
        scope: '',
        client_id: 'string',
        client_secret: '******',
      },
      {
        onSuccess: () => {
          toast.success('Успех', { description: 'Вы успешно вошли в систему' });
          navigate('/');
        },
        onError: (error: Error | AxiosError) => {
          if (error instanceof AxiosError) {
            handleApiError(error, 'Ошибка входа');
            toast.error('Ошибка', {
              description: 'Не удалось войти в систему',
            });
          } else {
            toast.error('Ошибка', { description: error.message });
          }
        },
      }
    );
  };

  const onRegisterSubmit = (data: RegisterFormData) => {
    registrationMutation.mutate(
      {
        email: data.email,
        full_name: `${data.firstName} ${data.lastName}`,
        password: data.password,
      },
      {
        onSuccess: () => {
          toast.success('Успех', {
            description: 'Регистрация прошла успешно. Теперь вы можете войти.',
          });
          setActiveTab('login');
          registerForm.reset();
        },
        onError: (error: Error | AxiosError) => {
          handleApiError(error, 'Ошибка регистрации');
          toast.error('Ошибка', {
            description: 'Не удалось зарегистрироваться',
          });
        },
      }
    );
  };

  const handleLogout = () => {
    logout();
    toast.success('Успех', { description: 'Вы вышли из системы' });
    navigate('/auth');
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <Tabs
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as 'login' | 'register')}
        className="mb-4"
      >
        <TabsList className="grid w-full grid-cols-2 bg-gray-100 rounded-lg">
          <TabsTrigger
            value="login"
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm"
          >
            Вход
          </TabsTrigger>
          <TabsTrigger
            value="register"
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm"
          >
            Регистрация
          </TabsTrigger>
        </TabsList>
      </Tabs>
      <Card>
        <CardHeader className="flex items-center justify-center">
          <img src={logo} alt="Logo" className="h-16" />
        </CardHeader>
        <CardContent>
          {isLoggedIn && (
            <Button
              onClick={handleLogout}
              className="mb-4 w-full bg-custom-blue hover:bg-custom-blue/90 text-white"
              variant="default"
            >
              Выйти
            </Button>
          )}
          {!isLoggedIn && (
            <Tabs value={activeTab}>
              <TabsContent value="login">
                <Form {...loginForm}>
                  <form
                    onSubmit={loginForm.handleSubmit(onLoginSubmit)}
                    className="space-y-4"
                  >
                    <FormField
                      control={loginForm.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input placeholder="Введите email" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={loginForm.control}
                      name="password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Пароль</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Введите пароль"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="submit"
                      className={cn(
                        'w-full bg-[#00aaff] hover:bg-[#00aaff]/90 text-white',
                        styles.button
                      )}
                      disabled={authorizationMutation.isPending}
                    >
                      {authorizationMutation.isPending ? 'Вход...' : 'Войти'}
                    </Button>
                  </form>
                </Form>
              </TabsContent>
              <TabsContent value="register">
                <Form {...registerForm}>
                  <form
                    onSubmit={registerForm.handleSubmit(onRegisterSubmit)}
                    className="space-y-4"
                  >
                    <div className="flex space-x-4">
                      <FormField
                        control={registerForm.control}
                        name="firstName"
                        render={({ field }) => (
                          <FormItem className="flex-1">
                            <FormLabel>Имя</FormLabel>
                            <FormControl>
                              <Input placeholder="Введите имя" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={registerForm.control}
                        name="lastName"
                        render={({ field }) => (
                          <FormItem className="flex-1">
                            <FormLabel>Фамилия</FormLabel>
                            <FormControl>
                              <Input placeholder="Введите фамилию" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <FormField
                      control={registerForm.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input placeholder="Введите email" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={registerForm.control}
                      name="password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Пароль</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Введите пароль"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={registerForm.control}
                      name="confirmPassword"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Подтверждение пароля</FormLabel>
                          <FormControl>
                            <Input
                              type="password"
                              placeholder="Подтвердите пароль"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button
                      type="submit"
                      className={cn(
                        'w-full bg-[#00aaff] hover:bg-[#00aaff]/90 text-white',
                        styles.button
                      )}
                      disabled={registrationMutation.isPending}
                    >
                      {registrationMutation.isPending
                        ? 'Регистрация...'
                        : 'Зарегистрироваться'}
                    </Button>
                  </form>
                </Form>
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthForm;
