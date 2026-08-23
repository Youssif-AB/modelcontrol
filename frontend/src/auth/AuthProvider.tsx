import {
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  clearAccessToken,
  fetchCurrentUser,
  getAccessToken,
  loginUser,
  SESSION_EXPIRED_EVENT,
  setAccessToken,
} from "../api";

import type {
  UserRecord,
} from "../types";

import {
  AuthContext,
} from "./auth-context";


interface AuthProviderProps {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<UserRecord | null>(null);

  const [loading, setLoading] =
    useState(
      () => getAccessToken() !== null,
    );


  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      return;
    }

    let cancelled = false;

    fetchCurrentUser()
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser);
        }
      })
      .catch(() => {
        clearAccessToken();

        if (!cancelled) {
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);


  useEffect(() => {
    function handleSessionExpired() {
      setUser(null);
      setLoading(false);
    }

    window.addEventListener(
      SESSION_EXPIRED_EVENT,
      handleSessionExpired,
    );

    return () => {
      window.removeEventListener(
        SESSION_EXPIRED_EVENT,
        handleSessionExpired,
      );
    };
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
