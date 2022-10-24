interface Props {
  text: string;
}

export function Button({ text }: Props) {
  return (
    <button className="px-6 py-2 text-sm rounded-md border border-blue-dark-300/[0.5] duration-200 hover:bg-blue-dark-300/[0.5] bg-blue-dark-300/[.25]">
      {text}
    </button>
  );
}
