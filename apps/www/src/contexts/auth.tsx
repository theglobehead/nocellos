import { HOST } from '@/consts/env';
import { useAxios } from '@/hooks';
import { useMutation, useQuery } from '@tanstack/react-query';
import axiosClient, { AxiosResponse } from 'axios';
import qs from 'qs';
import React, { createContext, useCallback, useState } from 'react';

interface LoginProps {
  email: string;
  password: string;
}

interface RegisterProps extends LoginProps {
  name: string;
}

interface User {
  user_name: string;
  user_email: string;
  user_uuid: string;
  token_uuid: string;
}

type UserMeta = Omit<User, 'user_name' | 'user_email'>;

interface IAuthContext {
  login(credentials: LoginProps): void;
  logout(): void;
  register(credentials: RegisterProps): void;
  user?: User;
}

export const AuthContext = createContext<IAuthContext>(undefined);

export default function AuthProvider({
  children,
}: React.PropsWithChildren<unknown>) {
  const axios = useAxios();

  const [authState, setAuthState] = useState<UserMeta>({
    token_uuid: '2ffae871-b99e-466a-b479-fcf57526a141',
    user_uuid: '5e67adbd-8941-421a-adb7-a8e9a78b8b24',
  });
  const loginMutation = useMutation(
    ['user'],
    async (req: { email: string; password: string }) => {
      const body = qs.stringify(req);

      const { data } = await axios.post<
        { email: string; password: string },
        AxiosResponse<User>
      >(`${HOST}/login`, body);

      const { token_uuid, user_uuid } = data;
      if (data && token_uuid && user_uuid) {
        localStorage.setItem('token_uuid', data.token_uuid);
        localStorage.setItem('user_uuid', data.user_uuid);
        setAuthState({ token_uuid, user_uuid });
      }
    }
  );

  const logoutMutation = useMutation(['user'], async () => {
    await axios.post(`${HOST}/logout`);
  });

  const registerMutation = useMutation(
    ['user'],
    async (req: { name: string; email: string; password: string }) => {
      const body = qs.stringify(req);
      await axios.post<
        {
          name: string;
          email: string;
          password: string;
        },
        AxiosResponse<unknown>
      >(`${HOST}/register`, body);
    }
  );

  const login = useCallback(
    (credentials: LoginProps) => {
      loginMutation.mutate(credentials);
    },
    [loginMutation]
  );

  const register = useCallback(
    (credentials: RegisterProps) => {
      registerMutation.mutate(credentials);
    },
    [registerMutation]
  );

  const logout = useCallback(() => {
    logoutMutation.mutate();
  }, [logoutMutation]);

  const { data: user } = useQuery(['user'], async () => {
    const body = qs.stringify({
      user_uuid: authState.user_uuid,
    });
    const { data } = await axiosClient.post<
      null,
      AxiosResponse<{ user: User }>
    >(`${HOST}/get_user_info`, body);
    // console.log({ ...data, ...authState }, 'user');
    return data.user;
  });

  return (
    <AuthContext.Provider value={{ login, register, logout, user }}>
      {children}
    </AuthContext.Provider>
  );
}
