import { Head, Html, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html>
      <Head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body className="h-screen max-w-6xl m-auto text-blue-light-100 bg-blue-dark-500 font-poppins">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
