import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Plots from "./pages/Plots";
import PlotDetail from "./pages/PlotDetail";
import Alerts from "./pages/Alerts";
import { isAuthenticated } from "./services/auth";
import React from "react";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/" />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/plots"
          element={
            <PrivateRoute>
              <Plots />
            </PrivateRoute>
          }
        />
        <Route
          path="/plots/:id"
          element={
            <PrivateRoute>
              <PlotDetail />
            </PrivateRoute>
          }
        />
        <Route
          path="/anomalies"
          element={
            <PrivateRoute>
              <Alerts />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
