import {
  Navigate,
  Outlet,
} from "react-router";

import {
  useAuth,
} from "./useAuth";

function ProtectedRoute() {
  const {
    user,
    loading,
  } = useAuth();

  if (loading) {
    return (
      <p className="content-message">
        Loading session...
      </p>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return <Outlet />;
}


export default ProtectedRoute;