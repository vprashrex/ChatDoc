import { useAuth } from "../context/AuthContext";
import { LoadingPage } from "../hooks/LoadingPage";
import { useState, useEffect } from "react";

export function PrivateRoute({ Component, FallbackComponent }) {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const waitForAuth = new Promise((resolve) => {
      const checkAuth = setInterval(() => {
        if (currentUser !== undefined) {
          clearInterval(checkAuth);
          resolve();
        }
      }, 100); 
    });
    waitForAuth.then(() => {
      setLoading(false);
    });
  }, [currentUser]);

  if (loading) {
    return <LoadingPage/>;
  }
  return currentUser ? Component : FallbackComponent;
}