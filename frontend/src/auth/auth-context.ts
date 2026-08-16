import {
  createContext,
} from "react";

import type {
  UserRecord,
} from "../types";


export interface AuthContextValue {
  user: UserRecord | null;
  loading: boolean;

  login: (
    email: string,
    password: string,
  ) => Promise<void>;

  logout: () => void;
}


export const AuthContext =
  createContext<
    AuthContextValue | undefined
  >(undefined);