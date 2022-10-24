import NextLink from 'next/link';
import { useRouter } from 'next/router';

interface Props {
  href: string;
  text: string;
}

export function Link({ href, text }: Props) {
  const router = useRouter();
  return (
    <NextLink href={href}>
      <a
        className={`hover:text-blue-light-100 duration-200 ${
          router.pathname === href
            ? 'text-blue-light-100'
            : 'text-blue-dark-300'
        }`}
      >
        {text}
      </a>
    </NextLink>
  );
}
