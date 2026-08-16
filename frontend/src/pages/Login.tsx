import {
  useState,
  type FormEvent,
} from "react";

import {
  Navigate,
  useNavigate,
} from "react-router";

import {
  useAuth,
} from "../auth/useAuth";


function Login() {
  const {
    user,
    login,
  } = useAuth();

  const navigate =
    useNavigate();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  if (user) {
    return (
      <Navigate
        to="/"
        replace
      />
    );
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError(null);

      await login(
        email,
        password,
      );

      navigate(
        "/",
        {
          replace: true,
        },
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to sign in.",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <div className="login-page">
      <section className="login-card">
        <p className="eyebrow">
          MODEL GOVERNANCE PLATFORM
        </p>

        <h1>ModelControl</h1>

        <p className="subtitle">
          Sign in to access the model
          governance inventory.
        </p>

        <form
          className="login-form"
          onSubmit={handleSubmit}
        >
          <label>
            Email

            <input
              required
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value,
                )
              }
              placeholder="you@example.com"
            />
          </label>

          <label>
            Password

            <input
              required
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
            />
          </label>

          {error && (
            <p className="login-error">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
          >
            {submitting
              ? "Signing in..."
              : "Sign In"}
          </button>
        </form>
      </section>
    </div>
  );
}


export default Login;