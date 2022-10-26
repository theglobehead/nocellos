import { useCallback } from 'react';
import { toast, ToastOptions } from 'react-toastify';

const TOAST_OPTIONS: ToastOptions = {
  position: 'bottom-right',
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  progress: undefined,
};

export function useToastEmitter(): {
  emitInfo: (msg: string) => void;
} {
  const emitInfo = useCallback(
    (msg: string) => toast.info(msg, TOAST_OPTIONS),
    []
  );

  return { emitInfo };
}
