import { Label } from '@/pages';
import { Square3Stack3DIcon } from '@heroicons/react/24/outline';
import { useMemo } from 'react';

interface Props {
  name: string;
  cardCount: number;
  cardsFinished: number;
  labels: Label[];
  onClick?: () => void;
}

export function DeckPreview({
  cardCount,
  labels,
  name,
  cardsFinished,
  onClick,
}: Props) {
  const cardProgressPercent = useMemo(
    () => (cardCount / cardsFinished) * 100,
    [cardCount, cardsFinished]
  );
  return (
    <div
      onClick={onClick}
      className="w-64 hover:bg-blue-dark-400 duration-200 hover:scale-105 cursor-pointer bg-blue-dark-400/[0.5] p-5 rounded-lg flex flex-col items-center h-64 justify-between"
    >
      <div className="flex items-center justify-between w-full">
        <div className="flex items-center">
          <Square3Stack3DIcon className="w-6 text-blue-light-100" />
          <h6 className="ml-2 text-sm text-blue-light-100">{cardCount}</h6>
        </div>
        {labels.map((l, i) => (
          <div
            key={i}
            className="rounded-full bg-green-light-100/[.10] py-0.5 px-3 text-xs uppercase text-green-light-100"
          >
            {l.label_name}
          </div>
        ))}
      </div>
      <p className="text-center">{name}</p>

      <div className="w-full">
        <div className="flex items-center justify-between mb-2 text-sm">
          <h6>Progress</h6>
          <h6 className="text-blue-dark-300">{cardProgressPercent}%</h6>
        </div>
        <div className="relative">
          <div
            className={`absolute w-[${cardProgressPercent}%] bg-orange-200 rounded-full h-1 left-0 top-0­`}
          />
          <div className="w-full h-1 rounded-full bg-blue-dark-300" />
        </div>
      </div>
    </div>
  );
}
