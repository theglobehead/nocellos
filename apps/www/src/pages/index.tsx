import { DeckPreview } from '@/components';
import { HOST } from '@/consts/env';
import { useQuery } from '@tanstack/react-query';
import axios, { AxiosResponse } from 'axios';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import { useMemo } from 'react';

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

export function Index() {
  const router = useRouter();

  const { data: decks } = useQuery(['decks'], async () => {
    const body = new FormData();
    body.append('user_uuid', '5e67adbd-8941-421a-adb7-a8e9a78b8b24');
    body.append('requester_user_uuid', '5e67adbd-8941-421a-adb7-a8e9a78b8b24');
    const { data } = await axios.post<
      unknown,
      AxiosResponse<{ decks: Deck[] }>
    >(`${HOST}/get_user_decks`, body, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data['decks'];
  });

  const deckOpenUUID = useMemo(() => {
    if (!decks) return;
    return decks.find(
      (deck) => deck.deck_uuid === (router.query['deck'] as string)
    );
  }, [decks, router.query]);

  return (
    <>
      {deckOpenUUID ? (
        <motion.div
          className="absolute p-10 -translate-x-1/2 -translate-y-1/2 rounded-lg isolate bg-blue-dark-400 p top-1/2 left-1/2"
          initial={{ scale: 0.2, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        >
          <p>This is a card</p>
        </motion.div>
      ) : (
        <>
          <h1 className="mb-10 text-3xl">Daily tasks</h1>

          <div className="flex flex-wrap gap-10">
            {decks ? (
              decks.map((deck, i) => (
                <DeckPreview
                  name={deck.deck_name}
                  cardCount={deck.card_count}
                  labels={deck.labels}
                  cardsFinished={3}
                  onClick={() =>
                    router.push({
                      pathname: '/',
                      query: { deck: deck.deck_uuid },
                    })
                  }
                  key={i}
                />
              ))
            ) : (
              <p>Loading...</p>
            )}
          </div>
        </>
      )}
    </>
  );
}

export default Index;
