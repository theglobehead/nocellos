import axios, { Axios } from 'axios';
import { createContext, useMemo } from 'react';

export const AxiosContext = createContext<Axios>(undefined);

export default function AxiosProvider({
  children,
}: React.PropsWithChildren<unknown>) {
  const axiosClient = useMemo(() => {
    axios.interceptors.request.use(
      (config) => {
        // Read token for anywhere, in this case directly from localStorage
        const token = localStorage.getItem('token_uuid');
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      },
      (err) => Promise.reject(err)
    );

    return axios;
  }, []);

  return (
    <AxiosContext.Provider value={axiosClient}>
      {children}
    </AxiosContext.Provider>
  );
}
