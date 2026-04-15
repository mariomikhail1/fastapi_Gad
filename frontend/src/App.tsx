import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ReactElement } from "react";

import { AuthProvider, useAuth } from "./AuthContext";
import Login from "./components/Login";
import ProductList from "./components/ProductList";

const ProtectedRoute = ({ children }: { children: ReactElement }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/products"
            element={
              <ProtectedRoute>
                <ProductList />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/products" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

