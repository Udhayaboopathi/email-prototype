"use client";

import * as React from "react";

type Toast = {
  id: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
  variant?: "default" | "success" | "destructive" | "warning";
};

type ToastAction =
  | {
      type: "ADD_TOAST";
      toast: Toast;
    }
  | {
      type: "DISMISS_TOAST";
      toastId?: string;
    };

interface ToastState {
  toasts: Toast[];
}

const initialState: ToastState = {
  toasts: [],
};

const toastReducer = (
  state: ToastState,
  action: ToastAction,
): ToastState => {
  switch (action.type) {
    case "ADD_TOAST":
      return {
        ...state,
        toasts: [action.toast, ...state.toasts],
      };
    case "DISMISS_TOAST":
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      };
    default:
      return state;
  }
};

type ToastContextType = {
  state: ToastState;
  dispatch: React.Dispatch<ToastAction>;
};

const ToastContext = React.createContext<ToastContextType | undefined>(
  undefined,
);

export const ToastProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [state, dispatch] = React.useReducer(toastReducer, initialState);

  return (
    <ToastContext.Provider value={{ state, dispatch }}>
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = React.useContext(ToastContext);

  // Graceful fallback when used outside ToastProvider (e.g., in sonner-based setups)
  if (context === undefined) {
    return {
      toasts: [] as Toast[],
      toast: (props: Omit<Toast, "id">) => {
        console.warn("useToast called outside ToastProvider", props);
      },
      dismiss: (_toastId?: string) => {},
    };
  }

  return {
    toasts: context.state.toasts,
    toast: (props: Omit<Toast, "id">) => {
      const id = Math.random().toString(36).substr(2, 9);
      context.dispatch({
        type: "ADD_TOAST",
        toast: {
          ...props,
          id,
        },
      });
    },
    dismiss: (toastId?: string) => {
      context.dispatch({ type: "DISMISS_TOAST", toastId });
    },
  };
};
