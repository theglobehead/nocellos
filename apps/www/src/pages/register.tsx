import { Button, Input } from '@/components';
import { useAuth } from '@/hooks';
import {
  EnvelopeIcon,
  KeyIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';

interface FormInputs {
  name: string;
  email: string;
  password: string;
  terms: boolean;
}

const schema = yup.object().shape({
  name: yup.string().required().max(20),
  email: yup.string().email().required(),
  password: yup.string().required().min(4).max(20),
  terms: yup.bool().oneOf([true], 'You must agree to Terms & Conditions'),
});

export default function Register() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormInputs>({ resolver: yupResolver(schema) });

  const { register: _register } = useAuth();

  return (
    <div className="absolute max-w-md -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2">
      <h1 className="mb-4 text-3xl text-center">Register</h1>
      <p className="text-center text-blue-dark-200">
        Welcome to Nocellos! Don&apos;t have an account? Create one here.
      </p>
      <form
        className="flex flex-col gap-6 mt-8"
        onSubmit={handleSubmit(_register)}
      >
        <Input
          {...register('name')}
          placeholder="Name"
          error={!!errors.name}
          helperText={errors.name ? errors.name?.message : ''}
          icon={<UserCircleIcon />}
        />
        <Input
          {...register('email')}
          placeholder="E-mail"
          error={!!errors.email}
          helperText={errors.email ? errors.email?.message : ''}
          icon={<EnvelopeIcon />}
        />
        <Input
          {...register('password')}
          placeholder="Password"
          error={!!errors.password}
          helperText={errors.password ? errors.password?.message : ''}
          icon={<KeyIcon />}
        />
        <div>
          <input type="checkbox" {...register('terms')} id="terms" />
          <label htmlFor="terms" className="ml-3 text-sm">
            I agree to Terms & Conditions
          </label>
          {errors.terms && (
            <p className="mt-1 text-xs capitalize text-red-light-100">
              {errors.terms.message}
            </p>
          )}
        </div>

        <Button text="Register" colorScheme="Orange" type="submit" />
      </form>
    </div>
  );
}
