import { ButtonHTMLAttributes, useMemo } from 'react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  text: string;
  colorScheme?: 'Orange';
}

export function Button({ text, colorScheme, ...buttonProps }: Props) {
  const buttonColorProps = useMemo(() => {
    let styleProps = '';
    switch (colorScheme) {
      case 'Orange':
        styleProps = 'bg-orange-200 hover:bg-orange-200/[0.75] text-white';
        break;
      default:
        styleProps =
          'border border-blue-dark-300/[0.5] hover:bg-blue-dark-300/[0.5] bg-blue-dark-300/[.25]';
    }
    return styleProps;
  }, [colorScheme]);

  return (
    <button
      {...buttonProps}
      className={`px-6 py-2.5 text-sm duration-200 rounded-md ${buttonColorProps}`}
    >
      {text}
    </button>
  );
}
