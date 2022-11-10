export const HOST =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_HOST_DEV
    : process.env.NEXT_PUBLIC_HOST_PROD;
