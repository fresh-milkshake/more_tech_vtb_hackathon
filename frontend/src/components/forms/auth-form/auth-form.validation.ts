import { z } from 'zod';

export const loginSchema = z.object({
  email: z
    .string()
    .email('Введите корректный email')
    .min(1, 'Email обязателен'),
  password: z.string().min(6, 'Пароль должен быть не менее 6 символов'),
});

export const registerSchema = z
  .object({
    firstName: z.string().min(1, 'Имя обязательно'),
    lastName: z.string().min(1, 'Фамилия обязательна'),
    email: z
      .string()
      .email('Введите корректный email')
      .min(1, 'Email обязателен'),
    password: z.string().min(6, 'Пароль должен быть не менее 6 символов'),
    confirmPassword: z.string().min(6, 'Подтверждение пароля обязательно'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Пароли должны совпадать',
    path: ['confirmPassword'],
  });

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
