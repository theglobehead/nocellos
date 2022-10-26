import { HOST } from '@/consts/env';
import { useQuery } from '@tanstack/react-query';
import { AxiosResponse } from 'axios';
import { useAxios } from './use-axios';

export interface Label {
  label_name: string;
}
interface Deck {
  card_count: number;
  deck_uuid: string;
  deck_name: string;
  is_public: boolean;
  labels: Label[];
}

export function useDecks() {
  const axios = useAxios();

  return useQuery(['decks'], async () => {
    const { data } = await axios.post<
      unknown,
      AxiosResponse<{ decks: Deck[] }>
    >(`${HOST}/get_user_decks`, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data['decks'];
  });
}
