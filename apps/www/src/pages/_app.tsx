import { Navbar } from '@/components';
import AuthProvider from '@/contexts/auth';
import AxiosProvider from '@/contexts/axios';
import '@/styles/globals.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppProps } from 'next/app';
import Head from 'next/head';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const queryClient = new QueryClient();

function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Nocellos</title>
      </Head>
      <AxiosProvider>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <ToastContainer
              position="bottom-right"
              autoClose={5000}
              hideProgressBar={false}
              newestOnTop={false}
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
            />
            <Navbar />
            <Component {...pageProps} />
          </AuthProvider>
        </QueryClientProvider>
      </AxiosProvider>
    </>
  );
}

export default App;
