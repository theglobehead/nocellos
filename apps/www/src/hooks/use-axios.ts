import { AxiosContext } from '@/contexts/axios';
import { useContext } from 'react';

export function useAxios() {
  return useContext(AxiosContext);
}
