import { Button, Input } from '@/components';
import { useAuth } from '@/hooks';
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';

interface FormInputs {
  email: string;
  password: string;
}

const schema = yup.object().shape({
  email: yup.string().required(),
  password: yup.string().required(),
});

export default function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormInputs>({ resolver: yupResolver(schema) });

  const { login } = useAuth();

  return (
    <>
      <h1 className="text-3xl text-center">Login</h1>
      <form className="flex flex-col gap-6" onSubmit={handleSubmit(login)}>
        <Input
          {...register('email')}
          error={!!errors.email}
          helperText={errors.email ? errors.email.message : ''}
        />
        <Input
          {...register('password')}
          error={!!errors.password}
          helperText={errors.password ? errors.password.message : ''}
        />
        <Button text="Login" colorScheme="Orange" />
      </form>
    </>
  );
}
