import {
  Route,
  Routes,
} from "react-router";

import Dashboard from "./pages/Dashboard";
import ModelDetail from "./pages/ModelDetail";
import RegisterModel from "./pages/RegisterModel";

import "./App.css";


function App() {
  return (
    <main className="app">
      <Routes>
        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/models/new"
          element={<RegisterModel />}
        />

        <Route
          path="/models/:modelId"
          element={<ModelDetail />}
        />
      </Routes>
    </main>
  );
}

export default App;