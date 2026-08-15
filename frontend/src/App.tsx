import {
  Route,
  Routes,
} from "react-router";

import ProtectedRoute
  from "./auth/ProtectedRoute";

import Dashboard
  from "./pages/Dashboard";

import Login
  from "./pages/Login";

import ModelDetail
  from "./pages/ModelDetail";

import RegisterModel
  from "./pages/RegisterModel";

import "./App.css";


function App() {
  return (
    <main className="app">
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          element={
            <ProtectedRoute />
          }
        >
          <Route
            path="/"
            element={
              <Dashboard />
            }
          />

          <Route
            path="/models/new"
            element={
              <RegisterModel />
            }
          />

          <Route
            path="/models/:modelId"
            element={
              <ModelDetail />
            }
          />
        </Route>
      </Routes>
    </main>
  );
}


export default App;