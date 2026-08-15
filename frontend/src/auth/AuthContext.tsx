import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  clearAccessToken,
  fetchCurrentUser,
  getAccessToken,
  loginUser,
  setAccessToken,
} from "../api";

import type {
  UserRecord,
} from "../types";


interface AuthContextValue {
  user: UserRecord | null;
  loading: boolean;

  login: (
    email: string,
    password: string,
  ) => Promise<void>;

  logout: () => void;
}


const AuthContext =
  createContext<
    AuthContextValue | undefined
  >(undefined);


interface AuthProviderProps {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<UserRecord | null>(null);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {
    async function restoreSession() {
      const token =
        getAccessToken();

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser =
          await fetchCurrentUser();

        setUser(currentUser);
      } catch {
        clearAccessToken();
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);


  async function login(
    email: string,
    password: string,
  ) {
    const tokenResponse =
      await loginUser(
        email,
        password,
      );

    setAccessToken(
      tokenResponse.access_token,
    );

    try {
      const currentUser =
        await fetchCurrentUser();

      setUser(currentUser);
    } catch (error) {
      clearAccessToken();

      throw error;
    }
  }


  function logout() {
    clearAccessToken();
    setUser(null);
  }


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    );
  }

  return context;
}